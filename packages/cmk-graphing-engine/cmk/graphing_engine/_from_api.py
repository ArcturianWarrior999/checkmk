#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import assert_never, Protocol

from cmk.graphing.v1 import graphs as graphs_v1
from cmk.graphing.v1 import metrics as metrics_v1
from cmk.graphing.v2_unstable import graphs as graphs_v2_unstable
from cmk.graphing.v2_unstable import metrics as metrics_v2_unstable

from ._display import (
    FALLBACK_ATTRIBUTES,
    metric_display_attributes,
    parse_color,
    parse_unit,
)
from ._graph import Bound, Curve, Graph, Line, MinimalRange, Rule, Stack
from ._perfdata import MetricName, Service
from ._quantities import (
    Constant,
    Difference,
    Fraction,
    Product,
    Quantity,
    RRDMetric,
    ScalarOf,
    ScalarType,
    Sum,
)
from ._units import CurveAttributes

type _ApiQuantity = (
    str
    | metrics_v1.Constant
    | metrics_v1.WarningOf
    | metrics_v1.CriticalOf
    | metrics_v2_unstable.LowerWarningOf
    | metrics_v2_unstable.LowerCriticalOf
    | metrics_v1.MinimumOf
    | metrics_v1.MaximumOf
    | metrics_v1.Sum
    | metrics_v1.Product
    | metrics_v1.Difference
    | metrics_v1.Fraction
)


class QuantityBuilder(Protocol):
    def __call__(self, metrics: Sequence[RRDMetric]) -> Quantity: ...


class _SingleQuantityBuilder:
    def __call__(self, metrics: Sequence[RRDMetric]) -> Quantity:
        (metric,) = metrics
        return metric


_SINGLE_QUANTITY_BUILDER = _SingleQuantityBuilder()


@dataclass(frozen=True)
class _ParseContext:
    services: Sequence[Service]
    quantity_builder: QuantityBuilder
    localizer: Callable[[str], str]
    registered_metrics: Mapping[str, metrics_v1.Metric]

    def drawn(self, metric_name: str) -> Quantity:
        return self.quantity_builder(
            [
                RRDMetric(
                    host_name=service.host_name,
                    service_name=service.service_name,
                    metric_name=MetricName(metric_name),
                )
                for service in self.services
            ]
        )

    def scalar(self, metric_name: str) -> RRDMetric:
        service = self.services[0]
        return RRDMetric(
            host_name=service.host_name,
            service_name=service.service_name,
            metric_name=MetricName(metric_name),
        )


def _curve_display(quantity: _ApiQuantity, context: _ParseContext) -> CurveAttributes:
    match quantity:
        case str():
            return metric_display_attributes(
                quantity, context.localizer, context.registered_metrics
            )
        case metrics_v1.Constant():
            return CurveAttributes(
                title=quantity.title.localize(context.localizer),
                unit=parse_unit(quantity.unit),
                color=parse_color(quantity.color),
            )
        case (
            metrics_v2_unstable.LowerWarningOf()
            | metrics_v2_unstable.LowerCriticalOf()
            | metrics_v1.WarningOf()
            | metrics_v1.CriticalOf()
        ):
            return _curve_display(quantity.metric_name, context)
        case metrics_v1.MinimumOf() | metrics_v1.MaximumOf():
            attributes = _curve_display(quantity.metric_name, context)
            return CurveAttributes(
                title=attributes.title, unit=attributes.unit, color=parse_color(quantity.color)
            )
        case metrics_v1.Sum():
            return CurveAttributes(
                title=quantity.title.localize(context.localizer),
                unit=_curve_display(quantity.summands[0], context).unit,
                color=parse_color(quantity.color),
            )
        case metrics_v1.Product():
            return CurveAttributes(
                title=quantity.title.localize(context.localizer),
                unit=parse_unit(quantity.unit),
                color=parse_color(quantity.color),
            )
        case metrics_v1.Difference():
            return CurveAttributes(
                title=quantity.title.localize(context.localizer),
                unit=_curve_display(quantity.minuend, context).unit,
                color=parse_color(quantity.color),
            )
        case metrics_v1.Fraction():
            return CurveAttributes(
                title=quantity.title.localize(context.localizer),
                unit=parse_unit(quantity.unit),
                color=parse_color(quantity.color),
            )
        case _:
            assert_never(quantity)


def _parse_quantity(quantity: _ApiQuantity, context: _ParseContext) -> Quantity:
    match quantity:
        case str():
            return context.drawn(quantity)
        case metrics_v1.Constant():
            return Constant(quantity.value, display=_curve_display(quantity, context))
        case metrics_v2_unstable.LowerWarningOf():
            return ScalarOf(
                metric=context.scalar(quantity.metric_name),
                scalar_type=ScalarType.LOWER_WARNING,
            )
        case metrics_v2_unstable.LowerCriticalOf():
            return ScalarOf(
                metric=context.scalar(quantity.metric_name),
                scalar_type=ScalarType.LOWER_CRITICAL,
            )
        case metrics_v1.WarningOf():
            return ScalarOf(
                metric=context.scalar(quantity.metric_name), scalar_type=ScalarType.WARNING
            )
        case metrics_v1.CriticalOf():
            return ScalarOf(
                metric=context.scalar(quantity.metric_name), scalar_type=ScalarType.CRITICAL
            )
        case metrics_v1.MinimumOf():
            return ScalarOf(
                metric=context.scalar(quantity.metric_name),
                scalar_type=ScalarType.MINIMUM,
                color=parse_color(quantity.color),
            )
        case metrics_v1.MaximumOf():
            return ScalarOf(
                metric=context.scalar(quantity.metric_name),
                scalar_type=ScalarType.MAXIMUM,
                color=parse_color(quantity.color),
            )
        case metrics_v1.Sum():
            return Sum(
                summands=[_parse_quantity(s, context) for s in quantity.summands],
                display=_curve_display(quantity, context),
            )
        case metrics_v1.Product():
            return Product(
                factors=[_parse_quantity(f, context) for f in quantity.factors],
                display=_curve_display(quantity, context),
            )
        case metrics_v1.Difference():
            return Difference(
                minuend=_parse_quantity(quantity.minuend, context),
                subtrahend=_parse_quantity(quantity.subtrahend, context),
                display=_curve_display(quantity, context),
            )
        case metrics_v1.Fraction():
            return Fraction(
                dividend=_parse_quantity(quantity.dividend, context),
                divisor=_parse_quantity(quantity.divisor, context),
                display=_curve_display(quantity, context),
            )
        case _:
            assert_never(quantity)


def _metric_names_in_quantity(quantity: _ApiQuantity) -> Iterable[MetricName]:
    match quantity:
        case str():
            yield MetricName(quantity)
        case metrics_v1.Constant():
            return
        case (
            metrics_v2_unstable.LowerWarningOf()
            | metrics_v2_unstable.LowerCriticalOf()
            | metrics_v1.WarningOf()
            | metrics_v1.CriticalOf()
            | metrics_v1.MinimumOf()
            | metrics_v1.MaximumOf()
        ):
            yield MetricName(quantity.metric_name)
        case metrics_v1.Sum():
            for summand in quantity.summands:
                yield from _metric_names_in_quantity(summand)
        case metrics_v1.Product():
            for factor in quantity.factors:
                yield from _metric_names_in_quantity(factor)
        case metrics_v1.Difference():
            yield from _metric_names_in_quantity(quantity.minuend)
            yield from _metric_names_in_quantity(quantity.subtrahend)
        case metrics_v1.Fraction():
            yield from _metric_names_in_quantity(quantity.dividend)
            yield from _metric_names_in_quantity(quantity.divisor)
        case _:
            assert_never(quantity)


def _is_scalar(quantity: _ApiQuantity) -> bool:
    match quantity:
        case str():
            return False
        case (
            metrics_v1.Constant()
            | metrics_v2_unstable.LowerWarningOf()
            | metrics_v2_unstable.LowerCriticalOf()
            | metrics_v1.WarningOf()
            | metrics_v1.CriticalOf()
            | metrics_v1.MinimumOf()
            | metrics_v1.MaximumOf()
        ):
            return True
        case metrics_v1.Sum():
            return all(_is_scalar(s) for s in quantity.summands)
        case metrics_v1.Product():
            return all(_is_scalar(f) for f in quantity.factors)
        case metrics_v1.Difference():
            return _is_scalar(quantity.minuend) and _is_scalar(quantity.subtrahend)
        case metrics_v1.Fraction():
            return _is_scalar(quantity.dividend) and _is_scalar(quantity.divisor)
        case _:
            assert_never(quantity)


def drawn_metric_names_of_graph(
    graph: graphs_v1.Graph | graphs_v2_unstable.Graph,
) -> Sequence[MetricName]:
    return list(
        {
            name
            for quantity in (*graph.compound_lines, *graph.simple_lines)
            if not _is_scalar(quantity)
            for name in _metric_names_in_quantity(quantity)
        }
    )


def _parse_bound(bound: int | float | _ApiQuantity, context: _ParseContext) -> Bound:
    if isinstance(bound, int | float):
        return bound
    return _parse_quantity(bound, context)


def _parse_minimal_range(
    minimal_range: graphs_v1.MinimalRange | graphs_v2_unstable.MinimalRange,
    context: _ParseContext,
) -> MinimalRange:
    return MinimalRange(
        lower=_parse_bound(minimal_range.lower, context),
        upper=_parse_bound(minimal_range.upper, context),
    )


def _parse_range(
    graph: graphs_v1.Graph | graphs_v2_unstable.Graph,
    context: _ParseContext,
) -> MinimalRange | None:
    return (
        None if graph.minimal_range is None else _parse_minimal_range(graph.minimal_range, context)
    )


def _bidirectional_range(
    graph: graphs_v1.Bidirectional | graphs_v2_unstable.Bidirectional,
    context: _ParseContext,
) -> MinimalRange | None:
    upper = _parse_range(graph.upper, context)
    lower = _parse_range(graph.lower, context)
    if upper is None:
        return lower
    if lower is None:
        return upper
    if (
        isinstance(upper.lower, int | float)
        and isinstance(upper.upper, int | float)
        and isinstance(lower.lower, int | float)
        and isinstance(lower.upper, int | float)
    ):
        return MinimalRange(
            lower=min(upper.lower, lower.lower),
            upper=max(upper.upper, lower.upper),
        )
    return upper


def build_curve(
    quantity: Quantity,
    localizer: Callable[[str], str],
    registered_metrics: Mapping[str, metrics_v1.Metric],
) -> Curve:
    return Curve(
        quantity=quantity,
        attributes=quantity.attributes(localizer, registered_metrics) or FALLBACK_ATTRIBUTES,
    )


def _parse_lines(
    graph: graphs_v1.Graph | graphs_v2_unstable.Graph,
    context: _ParseContext,
    *,
    inverse: bool,
) -> tuple[Sequence[Stack], Sequence[Line], Sequence[Rule]]:
    def _curve(q: _ApiQuantity) -> Curve:
        return build_curve(
            _parse_quantity(q, context), context.localizer, context.registered_metrics
        )

    stack_members = [_curve(q) for q in graph.compound_lines if not _is_scalar(q)]
    stacks = [Stack(members=stack_members, inverse=inverse)] if stack_members else []
    lines = [
        Line(curve=_curve(q), inverse=inverse) for q in graph.simple_lines if not _is_scalar(q)
    ]
    rules = [
        Rule(curve=_curve(q), inverse=inverse)
        for q in (*graph.compound_lines, *graph.simple_lines)
        if _is_scalar(q)
    ]
    return stacks, lines, rules


def parse_graph_from_api(
    graph: (
        graphs_v1.Graph
        | graphs_v1.Bidirectional
        | graphs_v2_unstable.Graph
        | graphs_v2_unstable.Bidirectional
    ),
    services: Sequence[Service],
    localizer: Callable[[str], str],
    registered_metrics: Mapping[str, metrics_v1.Metric],
    *,
    graph_type: str,
    quantity_builder: QuantityBuilder = _SINGLE_QUANTITY_BUILDER,
) -> Graph:
    context = _ParseContext(
        services=services,
        quantity_builder=quantity_builder,
        localizer=localizer,
        registered_metrics=registered_metrics,
    )
    match graph:
        case graphs_v1.Graph() | graphs_v2_unstable.Graph():
            stacks, lines, rules = _parse_lines(graph, context, inverse=False)
            return Graph(
                name=graph.name,
                title=graph.title.localize(localizer),
                graph_type=graph_type,
                vertical_range=_parse_range(graph, context),
                stacks=stacks,
                lines=lines,
                rules=rules,
            )
        case graphs_v1.Bidirectional() | graphs_v2_unstable.Bidirectional():
            upper_stacks, upper_lines, upper_rules = _parse_lines(
                graph.upper, context, inverse=False
            )
            lower_stacks, lower_lines, lower_rules = _parse_lines(
                graph.lower, context, inverse=True
            )
            return Graph(
                name=graph.name,
                title=graph.title.localize(localizer),
                graph_type=graph_type,
                vertical_range=_bidirectional_range(graph, context),
                stacks=[*upper_stacks, *lower_stacks],
                lines=[*upper_lines, *lower_lines],
                rules=[*upper_rules, *lower_rules],
            )
        case _:
            assert_never(graph)
