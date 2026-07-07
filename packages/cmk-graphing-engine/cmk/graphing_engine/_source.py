#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Mapping, Sequence
from typing import Protocol

from ._graph import Graph
from ._options import ConsolidationFunction, TimeRange
from ._perfdata import (
    MetricName,
    PerformanceData,
    Service,
    TimeSeries,
)
from ._quantities import EvaluationContext, RRDMetric


class RRDFetchMetricNames(Protocol):
    def __call__(self, services: Sequence[Service]) -> Mapping[Service, frozenset[MetricName]]: ...


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
