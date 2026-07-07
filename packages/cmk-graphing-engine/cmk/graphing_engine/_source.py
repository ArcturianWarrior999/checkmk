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
    Service,
)
from ._quantities import EvaluationContext, Metric


class RRDFetchMetricNames(Protocol):
    def __call__(self, services: Sequence[Service]) -> Mapping[Service, frozenset[MetricName]]: ...


class RRDFetchData(Protocol):
    def __call__(
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
    fetch_data: RRDFetchData,
) -> EvaluationContext:
    metrics = list(dict.fromkeys(metric for graph in graphs for metric in graph.metrics()))
    fetched = fetch_data(
        metrics, consolidation_function=consolidation_function, time_range=time_range
    )
    return EvaluationContext(time_range=time_range, fetched=fetched)
