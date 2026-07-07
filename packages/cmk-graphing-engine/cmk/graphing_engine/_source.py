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
    Service,
    TimeSeries,
)
from ._quantities import EvaluationContext, RRDMetric
from ._translate import translate_metric_names


class RRDFetchRawMetricNames(Protocol):
    def __call__(self, services: Sequence[Service]) -> Mapping[Service, RawMetricNames]: ...


class RRDDataSource(Protocol):
    def fetch_performance_data(
        self, rrd_metrics: Sequence[RRDMetric]
    ) -> Mapping[RRDMetric, PerformanceData]: ...

    def fetch_time_series(
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


def fetch_evaluation_context(
    *,
    consolidation_function: ConsolidationFunction,
    time_range: TimeRange,
    graphs: Sequence[Graph],
    rrd: RRDDataSource,
) -> EvaluationContext:
    rrd_metrics = list(dict.fromkeys(metric for graph in graphs for metric in graph.metrics()))
    return EvaluationContext(
        performance_data=rrd.fetch_performance_data(rrd_metrics),
        time_series=rrd.fetch_time_series(
            rrd_metrics,
            consolidation_function=consolidation_function,
            time_range=time_range,
        ),
        time_range=time_range,
    )
