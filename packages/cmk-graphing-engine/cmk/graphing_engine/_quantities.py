#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from __future__ import annotations

import enum
import math
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import assert_never, Protocol

from cmk.graphing.v1 import metrics as metrics_v1

from ._display import metric_display_attributes
from ._options import ConsolidationFunction, TimeRange
from ._perfdata import FetchedData, HostName, MetricName, PerformanceData, ServiceName, TimeSeries
from ._units import CurveAttributes


# The leaves a graph fetches data for: the keys of EvaluationContext.fetched and the elements
# Quantity.metrics() yields. A metric is identified by its metric_name - that is what sets it apart
# from a plain Quantity (an expression node) - and tagged by kind() like any serialized quantity.
class Metric(Protocol):
    def kind(self) -> str: ...

    @property
    def metric_name(self) -> MetricName: ...


@dataclass(frozen=True, kw_only=True)
class EvaluationContext:
    time_range: TimeRange
    fetched: Mapping[Metric, Sequence[FetchedData]] = field(default_factory=dict)

    def fetched_of(self, metric: Metric) -> Sequence[FetchedData]:
        return self.fetched.get(metric, ())

    def data_of(self, metric: Metric) -> PerformanceData | None:
        performance_data: PerformanceData | None = None
        for data in self.fetched_of(metric):
            if data.performance_data is not None:
                performance_data = data.performance_data
        return performance_data

    def time_series_of(self, metric: Metric) -> TimeSeries | None:
        time_series: TimeSeries | None = None
        for data in self.fetched_of(metric):
            if data.time_series is not None:
                time_series = data.time_series
        return time_series


@dataclass(frozen=True, kw_only=True)
class EvaluatedQuantity:
    value: float | None
    time_series: TimeSeries
    label: str = ""


class Quantity(Protocol):
    def kind(self) -> str: ...

    def ident(self) -> str: ...

    def metrics(self) -> Iterable[Metric]: ...

    # A quantity evaluates to a sequence of curves: empty when absent, one for an ordinary quantity,
    # and several when a fan-out leaf (e.g. a query matching many services) expands into one curve
    # per matched series.
    def evaluate(self, context: EvaluationContext) -> Sequence[EvaluatedQuantity]: ...

    def attributes(
        self,
        localizer: Callable[[str], str],
        registered_metrics: Mapping[str, metrics_v1.Metric],
        /,
    ) -> CurveAttributes | None: ...


type _Operator = Callable[[Sequence[float | None]], float | None]


def _op_sum(point: Sequence[float | None]) -> float | None:
    return sum(value for value in point if value is not None)


def _op_product(point: Sequence[float | None]) -> float | None:
    present = [value for value in point if value is not None]
    if len(present) != len(point):
        return None
    return math.prod(present)


def _op_difference(point: Sequence[float | None]) -> float | None:
    minuend, subtrahend = point
    if minuend is None or subtrahend is None:
        return None
    return minuend - subtrahend


def _op_fraction(point: Sequence[float | None]) -> float | None:
    dividend, divisor = point
    if dividend is None or divisor is None or divisor == 0:
        return None
    return dividend / divisor


def _apply(operator: _Operator, point: Sequence[float | None]) -> float | None:
    if all(value is None for value in point):
        return None
    return operator(point)


def _num_points(time_range: TimeRange) -> int:
    if time_range.step <= 0:
        return 0
    return max(0, (time_range.end - time_range.start) // time_range.step)


def _constant_time_series(value: float | None, time_range: TimeRange) -> TimeSeries:
    return TimeSeries(time_range=time_range, values=[value] * _num_points(time_range))


def _apply_operator(
    operator: _Operator,
    operands: Sequence[EvaluatedQuantity | None],
    context: EvaluationContext,
) -> EvaluatedQuantity:
    values = [None if operand is None else operand.value for operand in operands]
    time_series = [
        _constant_time_series(None, context.time_range) if operand is None else operand.time_series
        for operand in operands
    ]
    return EvaluatedQuantity(
        value=None if any(value is None for value in values) else operator(values),
        time_series=TimeSeries(
            time_range=context.time_range,
            values=[_apply(operator, point) for point in zip(*(ts.values for ts in time_series))],
        ),
    )


def _collapse(results: Sequence[EvaluatedQuantity]) -> EvaluatedQuantity | None:
    # An operand of an operation must be single-valued: an absent operand is None; a fan-out operand
    # (a quantity that expands into several curves) cannot take part in an operation.
    match results:
        case []:
            return None
        case [single]:
            return single
        case _:
            raise ValueError("a fan-out quantity cannot be an operand of an operation")


@dataclass(frozen=True)
class Constant:
    value: int | float
    display: CurveAttributes | None = None

    def kind(self) -> str:
        return "constant"

    def ident(self) -> str:
        return f"{self.kind()}({self.value})"

    def metrics(self) -> Iterable[Metric]:
        return ()

    def evaluate(self, context: EvaluationContext) -> Sequence[EvaluatedQuantity]:
        return [
            EvaluatedQuantity(
                value=self.value, time_series=_constant_time_series(self.value, context.time_range)
            )
        ]

    def attributes(
        self,
        _localizer: Callable[[str], str],
        _registered_metrics: Mapping[str, metrics_v1.Metric],
    ) -> CurveAttributes | None:
        return self.display


@dataclass(frozen=True, kw_only=True)
class RRDMetric:
    host_name: HostName
    service_name: ServiceName
    metric_name: MetricName
    consolidation_function: ConsolidationFunction | None = None

    def kind(self) -> str:
        return "rrd_metric"

    def ident(self) -> str:
        return f"{self.kind()}({self.host_name}/{self.service_name}/{self.metric_name})"

    def metrics(self) -> Iterable[Metric]:
        yield self

    def evaluate(self, context: EvaluationContext) -> Sequence[EvaluatedQuantity]:
        data = context.data_of(self)
        existing = context.time_series_of(self)
        if not ((data is not None and data.value is not None) or existing is not None):
            return []
        return [
            EvaluatedQuantity(
                value=None if data is None else data.value,
                time_series=(
                    existing
                    if existing is not None
                    else _constant_time_series(None, context.time_range)
                ),
            )
        ]

    def attributes(
        self,
        localizer: Callable[[str], str],
        registered_metrics: Mapping[str, metrics_v1.Metric],
    ) -> CurveAttributes:
        return metric_display_attributes(self.metric_name, localizer, registered_metrics)


class ScalarType(enum.StrEnum):
    WARNING = "warning"
    CRITICAL = "critical"
    LOWER_WARNING = "lower_warning"
    LOWER_CRITICAL = "lower_critical"
    MINIMUM = "minimum"
    MAXIMUM = "maximum"


@dataclass(frozen=True)
class ScalarOf:
    metric: RRDMetric
    scalar_type: ScalarType
    color: str | None = None

    def kind(self) -> str:
        return "scalar_of"

    def ident(self) -> str:
        return f"{self.kind()}({self.scalar_type},{self.metric.ident()})"

    def metrics(self) -> Iterable[Metric]:
        yield self.metric

    def evaluate(self, context: EvaluationContext) -> Sequence[EvaluatedQuantity]:
        if (data := context.data_of(self.metric)) is None:
            return []
        match self.scalar_type:
            case ScalarType.WARNING:
                value = data.warning
            case ScalarType.CRITICAL:
                value = data.critical
            case ScalarType.LOWER_WARNING:
                value = data.lower_warning
            case ScalarType.LOWER_CRITICAL:
                value = data.lower_critical
            case ScalarType.MINIMUM:
                value = data.minimum
            case ScalarType.MAXIMUM:
                value = data.maximum
            case _:
                assert_never(self.scalar_type)
        return [
            EvaluatedQuantity(
                value=value, time_series=_constant_time_series(value, context.time_range)
            )
        ]

    def attributes(
        self,
        localizer: Callable[[str], str],
        registered_metrics: Mapping[str, metrics_v1.Metric],
    ) -> CurveAttributes:
        attributes = self.metric.attributes(localizer, registered_metrics)
        label: str
        type_color: str | None
        match self.scalar_type:
            case ScalarType.WARNING:
                label, type_color = "Warning", "#ffd000"
            case ScalarType.CRITICAL:
                label, type_color = "Critical", "#ff3232"
            case ScalarType.LOWER_WARNING:
                label, type_color = "Warning (lower)", "#ffd000"
            case ScalarType.LOWER_CRITICAL:
                label, type_color = "Critical (lower)", "#ff3232"
            case ScalarType.MINIMUM:
                label, type_color = "Minimum", None
            case ScalarType.MAXIMUM:
                label, type_color = "Maximum", None
            case _:
                assert_never(self.scalar_type)
        return CurveAttributes(
            title=localizer(label),
            unit=attributes.unit,
            color=self.color or type_color or attributes.color,
        )


@dataclass(frozen=True)
class Sum:
    summands: Sequence[Quantity]
    display: CurveAttributes | None = None

    def kind(self) -> str:
        return "sum"

    def ident(self) -> str:
        return f"{self.kind()}({','.join(summand.ident() for summand in self.summands)})"

    def metrics(self) -> Iterable[Metric]:
        for summand in self.summands:
            yield from summand.metrics()

    def evaluate(self, context: EvaluationContext) -> Sequence[EvaluatedQuantity]:
        operands = [_collapse(summand.evaluate(context)) for summand in self.summands]
        if not operands or operands[0] is None:
            return []
        return [_apply_operator(_op_sum, operands, context)]

    def attributes(
        self,
        _localizer: Callable[[str], str],
        _registered_metrics: Mapping[str, metrics_v1.Metric],
    ) -> CurveAttributes | None:
        return self.display


@dataclass(frozen=True)
class Product:
    factors: Sequence[Quantity]
    display: CurveAttributes | None = None

    def kind(self) -> str:
        return "product"

    def ident(self) -> str:
        return f"{self.kind()}({','.join(factor.ident() for factor in self.factors)})"

    def metrics(self) -> Iterable[Metric]:
        for factor in self.factors:
            yield from factor.metrics()

    def evaluate(self, context: EvaluationContext) -> Sequence[EvaluatedQuantity]:
        operands = [_collapse(factor.evaluate(context)) for factor in self.factors]
        return [_apply_operator(_op_product, operands, context)]

    def attributes(
        self,
        _localizer: Callable[[str], str],
        _registered_metrics: Mapping[str, metrics_v1.Metric],
    ) -> CurveAttributes | None:
        return self.display


@dataclass(frozen=True, kw_only=True)
class Difference:
    minuend: Quantity
    subtrahend: Quantity
    display: CurveAttributes | None = None

    def kind(self) -> str:
        return "difference"

    def ident(self) -> str:
        return f"{self.kind()}({self.minuend.ident()},{self.subtrahend.ident()})"

    def metrics(self) -> Iterable[Metric]:
        yield from self.minuend.metrics()
        yield from self.subtrahend.metrics()

    def evaluate(self, context: EvaluationContext) -> Sequence[EvaluatedQuantity]:
        minuend = _collapse(self.minuend.evaluate(context))
        if minuend is None:
            return []
        subtrahend = _collapse(self.subtrahend.evaluate(context))
        return [_apply_operator(_op_difference, [minuend, subtrahend], context)]

    def attributes(
        self,
        _localizer: Callable[[str], str],
        _registered_metrics: Mapping[str, metrics_v1.Metric],
    ) -> CurveAttributes | None:
        return self.display


@dataclass(frozen=True, kw_only=True)
class Fraction:
    dividend: Quantity
    divisor: Quantity
    display: CurveAttributes | None = None

    def kind(self) -> str:
        return "fraction"

    def ident(self) -> str:
        return f"{self.kind()}({self.dividend.ident()},{self.divisor.ident()})"

    def metrics(self) -> Iterable[Metric]:
        yield from self.dividend.metrics()
        yield from self.divisor.metrics()

    def evaluate(self, context: EvaluationContext) -> Sequence[EvaluatedQuantity]:
        dividend = _collapse(self.dividend.evaluate(context))
        divisor = _collapse(self.divisor.evaluate(context))
        return [_apply_operator(_op_fraction, [dividend, divisor], context)]

    def attributes(
        self,
        _localizer: Callable[[str], str],
        _registered_metrics: Mapping[str, metrics_v1.Metric],
    ) -> CurveAttributes | None:
        return self.display
