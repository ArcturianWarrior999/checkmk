#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Iterable, Mapping, Sequence
from typing import Protocol

from cmk.graphing.v1 import translations as translations_v1

from ._from_api import parse_translations_from_api
from ._graph import Graph
from ._options import ConsolidationFunction, TimeRange
from ._perfdata import (
    MetricName,
    PerformanceData,
    RawMetricNames,
    RawPerformanceData,
    Service,
    TimeSeries,
)
from ._quantities import EvaluationContext, RRDMetric
from ._resample import resample
from ._translate import (
    originals_for_metric_name,
    translate_metric_names,
    translate_performance_data,
)


class RRDFetchRawMetricNames(Protocol):
    def __call__(self, services: Sequence[Service]) -> Mapping[Service, RawMetricNames]: ...


class RRDDataSource(Protocol):
    def fetch_raw_performance_data(
        self, rrd_metrics: Sequence[RRDMetric]
    ) -> Mapping[Service, RawPerformanceData]: ...

    def fetch_raw_time_series(
        self,
        rrd_metrics: Sequence[RRDMetric],
        *,
        consolidation_function: ConsolidationFunction,
        time_range: TimeRange,
    ) -> Mapping[RRDMetric, TimeSeries]: ...


def fetch_metric_names(
    *,
    services: Iterable[Service],
    registered_translations: Iterable[translations_v1.Translation],
    fetch_raw_metric_names: RRDFetchRawMetricNames,
) -> Mapping[Service, frozenset[MetricName]]:
    parsed_translations = parse_translations_from_api(registered_translations)
    raw_metric_names = fetch_raw_metric_names(list(dict.fromkeys(services)))
    return {
        service: translate_metric_names(raw_metrics, parsed_translations)
        for service, raw_metrics in raw_metric_names.items()
    }


def _consolidation_function(
    metric: RRDMetric, consolidation_function: ConsolidationFunction
) -> ConsolidationFunction:
    return (
        consolidation_function
        if metric.consolidation_function is None
        else metric.consolidation_function
    )


def _scaled(time_series: TimeSeries, scale: float) -> TimeSeries:
    if scale == 1.0:
        return time_series
    return TimeSeries(
        time_range=time_series.time_range,
        values=[None if value is None else value * scale for value in time_series.values],
    )


def _merge(time_series: Sequence[TimeSeries], time_range: TimeRange) -> TimeSeries:
    return TimeSeries(
        time_range=time_range,
        values=[
            next((value for value in point if value is not None), None)
            for point in zip(*(member.values for member in time_series))
        ],
    )


def fetch_evaluation_context(
    *,
    consolidation_function: ConsolidationFunction,
    time_range: TimeRange,
    registered_graphs: Sequence[Graph],
    registered_translations: Iterable[translations_v1.Translation],
    rrd: RRDDataSource,
) -> EvaluationContext:
    parsed_translations = parse_translations_from_api(registered_translations)
    rrd_metrics = list(
        dict.fromkeys(metric for graph in registered_graphs for metric in graph.metrics())
    )
    raw_performance_data = rrd.fetch_raw_performance_data(rrd_metrics)
    translated = {
        service: translate_performance_data(raw, parsed_translations)
        for service, raw in raw_performance_data.items()
    }
    performance_data: dict[RRDMetric, PerformanceData] = {}
    for metric in rrd_metrics:
        service = Service(host_name=metric.host_name, service_name=metric.service_name)
        if (raw := raw_performance_data.get(service)) is None:
            continue
        if (data := translated[service].get(metric.metric_name)) is None:
            data = PerformanceData(
                value=None,
                originals=originals_for_metric_name(
                    metric.metric_name, parsed_translations, raw.check_command
                ),
            )
        performance_data[metric] = data

    originals_per_function: dict[
        ConsolidationFunction, dict[RRDMetric, list[tuple[RRDMetric, float]]]
    ] = {}
    for metric in rrd_metrics:
        if (data := performance_data.get(metric)) is None:
            continue
        function = _consolidation_function(metric, consolidation_function)
        originals_per_function.setdefault(function, {})[metric] = [
            (
                RRDMetric(
                    host_name=metric.host_name,
                    service_name=metric.service_name,
                    metric_name=original.metric_name,
                ),
                original.scale,
            )
            for original in data.originals
        ]

    time_series: dict[RRDMetric, TimeSeries] = {}
    for function, originals_per_metric in originals_per_function.items():
        raw_time_series = rrd.fetch_raw_time_series(
            list(
                dict.fromkeys(
                    rrd_metric
                    for originals in originals_per_metric.values()
                    for rrd_metric, _scale in originals
                )
            ),
            consolidation_function=function,
            time_range=time_range,
        )
        for metric, originals in originals_per_metric.items():
            scaled = [
                _scaled(resample(raw_time_series[rrd_metric], time_range, function), scale)
                for rrd_metric, scale in originals
                if rrd_metric in raw_time_series
            ]
            if scaled:
                time_series[metric] = _merge(scaled, time_range)
    return EvaluationContext(
        performance_data=performance_data,
        time_series=time_series,
        time_range=time_range,
    )
