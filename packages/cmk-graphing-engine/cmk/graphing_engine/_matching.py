#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Callable, Container, Mapping, Sequence
from dataclasses import dataclass

from cmk.graphing.v1 import graphs as graphs_v1
from cmk.graphing.v1 import metrics as metrics_v1
from cmk.graphing.v2_unstable import graphs as graphs_v2_unstable

from ._from_api import (
    _SINGLE_QUANTITY_BUILDER,
    build_curve,
    drawn_metric_names_of_graph,
    parse_graph_from_api,
    QuantityBuilder,
)
from ._graph import Graph, Line, Rule, Stack
from ._perfdata import MetricName, Service
from ._quantities import Quantity, RRDMetric, ScalarOf, ScalarType
from ._source import RRDFetchMetricNames

_PREDICT_PREFIX = "predict_"


def _matches(
    graph: graphs_v1.Graph | graphs_v2_unstable.Graph,
    names: Sequence[MetricName],
    available: Container[MetricName],
) -> bool:
    if any(MetricName(name) in available for name in graph.conflicting):
        return False
    optional = frozenset(MetricName(name) for name in graph.optional)
    return all(name in available for name in names if name not in optional)


@dataclass(frozen=True, kw_only=True)
class _GraphMatch:
    metric_names: Sequence[MetricName]
    matched: bool


def _walk(
    graph: (
        graphs_v1.Graph
        | graphs_v1.Bidirectional
        | graphs_v2_unstable.Graph
        | graphs_v2_unstable.Bidirectional
    ),
    available: Container[MetricName],
) -> _GraphMatch:
    match graph:
        case graphs_v1.Graph() | graphs_v2_unstable.Graph():
            names = drawn_metric_names_of_graph(graph)
            return _GraphMatch(metric_names=names, matched=_matches(graph, names, available))
        case graphs_v1.Bidirectional() | graphs_v2_unstable.Bidirectional():
            lower_names = drawn_metric_names_of_graph(graph.lower)
            upper_names = drawn_metric_names_of_graph(graph.upper)
            return _GraphMatch(
                metric_names=list({*lower_names, *upper_names}),
                matched=(
                    _matches(graph.lower, lower_names, available)
                    or _matches(graph.upper, upper_names, available)
                ),
            )


def _add_predictive_lines(
    graph: Graph,
    service: Service,
    available: Container[MetricName],
    localizer: Callable[[str], str],
    registered_metrics: Mapping[str, metrics_v1.Metric],
) -> tuple[Graph, set[MetricName]]:
    inverse_by_metric: dict[MetricName, bool] = {}
    for group in graph.stacks:
        for member in group.members:
            for metric in member.quantity.metrics():
                if isinstance(metric, RRDMetric):
                    inverse_by_metric.setdefault(metric.metric_name, group.inverse)
    for line in graph.lines:
        for metric in line.curve.quantity.metrics():
            if isinstance(metric, RRDMetric):
                inverse_by_metric.setdefault(metric.metric_name, line.inverse)

    added: list[Line] = []
    names: set[MetricName] = set()
    for base, inverse in inverse_by_metric.items():
        for predictive in (
            MetricName(f"predict_{base}"),
            MetricName(f"predict_lower_{base}"),
        ):
            if predictive in available and predictive not in names:
                added.append(
                    Line(
                        curve=build_curve(
                            RRDMetric(
                                host_name=service.host_name,
                                service_name=service.service_name,
                                metric_name=predictive,
                            ),
                            localizer,
                            registered_metrics,
                        ),
                        inverse=inverse,
                    )
                )
                names.add(predictive)
    if not added:
        return graph, names
    return (
        Graph(
            name=graph.name,
            title=graph.title,
            graph_type=graph.graph_type,
            vertical_range=graph.vertical_range,
            stacks=graph.stacks,
            lines=[*graph.lines, *added],
        ),
        names,
    )


type _GraphPlugin = (
    graphs_v1.Graph
    | graphs_v1.Bidirectional
    | graphs_v2_unstable.Graph
    | graphs_v2_unstable.Bidirectional
)


_FALLBACK_SCALAR_TYPES = (
    ScalarType.WARNING,
    ScalarType.CRITICAL,
    ScalarType.LOWER_WARNING,
    ScalarType.LOWER_CRITICAL,
)


def build_matched_graphs(
    *,
    services: Sequence[Service],
    localizer: Callable[[str], str],
    fetch_metric_names: RRDFetchMetricNames,
    graph_type: str,
    registered_graphs: Sequence[_GraphPlugin],
    registered_metrics: Mapping[str, metrics_v1.Metric],
    quantity_builder: QuantityBuilder = _SINGLE_QUANTITY_BUILDER,
) -> Sequence[Graph]:
    names_by_service = fetch_metric_names(services)
    available: frozenset[MetricName] = (
        frozenset[MetricName]().union(*names_by_service.values())
        if names_by_service
        else frozenset()
    )
    single_service = services[0] if len(services) == 1 else None
    matched_graphs: list[Graph] = []
    claimed: set[MetricName] = set()

    def _drawn(name: MetricName) -> Quantity:
        return quantity_builder(
            [
                RRDMetric(
                    host_name=service.host_name,
                    service_name=service.service_name,
                    metric_name=name,
                )
                for service in services
            ]
        )

    def _collect(base: Graph) -> None:
        # Rules and predictive lines are single-service concepts; a graph over multiple services
        # drops them.
        if single_service is None:
            matched_graphs.append(
                Graph(
                    name=base.name,
                    title=base.title,
                    graph_type=base.graph_type,
                    vertical_range=base.vertical_range,
                    stacks=base.stacks,
                    lines=base.lines,
                )
            )
            return
        graph, predictive_names = _add_predictive_lines(
            base, single_service, available, localizer, registered_metrics
        )
        claimed.update(predictive_names)
        matched_graphs.append(graph)

    def _fallback_rules(name: MetricName) -> Sequence[Rule]:
        if single_service is None:
            return []
        metric = RRDMetric(
            host_name=single_service.host_name,
            service_name=single_service.service_name,
            metric_name=name,
        )
        return [
            Rule(
                curve=build_curve(
                    ScalarOf(metric=metric, scalar_type=scalar_type), localizer, registered_metrics
                ),
                inverse=False,
            )
            for scalar_type in _FALLBACK_SCALAR_TYPES
        ]

    for plugin in registered_graphs:
        walks = [_walk(plugin, names) for names in names_by_service.values()]
        if not any(walk.matched for walk in walks):
            continue
        claimed.update(walks[0].metric_names)
        _collect(
            parse_graph_from_api(
                plugin,
                services,
                localizer,
                registered_metrics,
                graph_type=graph_type,
                quantity_builder=quantity_builder,
            )
        )

    for name in available:
        if name in claimed or name.startswith(_PREDICT_PREFIX):
            continue
        _collect(
            Graph(
                name=name,
                title=name,
                graph_type=graph_type,
                stacks=[
                    Stack(
                        members=[build_curve(_drawn(name), localizer, registered_metrics)],
                        inverse=False,
                    )
                ],
                rules=_fallback_rules(name),
            )
        )

    return matched_graphs
