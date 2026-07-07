#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Mapping, Sequence
from typing import Protocol

from ._graph import Graph
from ._options import ConsolidationFunction, TimeRange
from ._perfdata import (
    FetchedData,
    MetricName,
    PerformanceData,
    Service,
    TimeSeries,
)
from ._quantities import EvaluationContext, Metric, RRDMetric


class RRDFetchMetricNames(Protocol):
    def __call__(self, services: Sequence[Service]) -> Mapping[Service, frozenset[MetricName]]: ...


class RRDDataSource(Protocol):
    def fetch(
        self,
        metrics: Sequence[Metric],
        *,
        consolidation_function: ConsolidationFunction,
        time_range: TimeRange,
    ) -> Mapping[Metric, Sequence[FetchedData]]: ...


def fetch_evaluation_context(
    *,
    consolidation_function: ConsolidationFunction,
    time_range: TimeRange,
    graphs: Sequence[Graph],
    rrd: RRDDataSource,
) -> EvaluationContext:
    metrics = list(dict.fromkeys(metric for graph in graphs for metric in graph.metrics()))
    fetched = rrd.fetch(
        metrics, consolidation_function=consolidation_function, time_range=time_range
    )
    performance_data: dict[RRDMetric, PerformanceData] = {}
    time_series: dict[RRDMetric, TimeSeries] = {}
    for metric, fetched_data in fetched.items():
        if not isinstance(metric, RRDMetric):
            continue
        for data in fetched_data:
            if data.performance_data is not None:
                performance_data[metric] = data.performance_data
            if data.time_series is not None:
                time_series[metric] = data.time_series
    return EvaluationContext(
        performance_data=performance_data,
        time_series=time_series,
        time_range=time_range,
        fetched=fetched,
    )
