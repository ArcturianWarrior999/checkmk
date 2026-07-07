#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Mapping, Sequence

from cmk.graphing_engine import (
    AutoPrecision,
    ConsolidationFunction,
    Curve,
    CurveAttributes,
    DecimalNotation,
    evaluate_graphs,
    EvaluatedGraph,
    Graph,
    HostName,
    Line,
    MetricName,
    PerformanceData,
    Quantity,
    RRDMetric,
    ServiceName,
    TimeRange,
    TimeSeries,
    Unit,
)

_UNIT = Unit(notation=DecimalNotation(""), precision=AutoPrecision(2))


def _time_range() -> TimeRange:
    return TimeRange(start=0, end=60, step=10)


def _rrd(name: str) -> RRDMetric:
    return RRDMetric(
        host_name=HostName("h"),
        service_name=ServiceName("svc"),
        metric_name=MetricName(name),
        consolidation_function=ConsolidationFunction.AVERAGE,
    )


def _curve(quantity: Quantity) -> Curve:
    return Curve(quantity=quantity, attributes=CurveAttributes(title="t", unit=_UNIT, color="#000"))


def _line(quantity: Quantity, *, inverse: bool = False) -> Line:
    return Line(curve=_curve(quantity), inverse=inverse)


def _ts(*values: float | None) -> TimeSeries:
    return TimeSeries(time_range=_time_range(), values=list(values))


def _perf(value: float | None, **thresholds: float | None) -> PerformanceData:
    return PerformanceData(value=value, **thresholds)


class _FakeRRDSource:
    # The source already delivers translated, per-RRDMetric performance data and time series; the
    # engine only orchestrates.
    def __init__(
        self,
        performance_data: Mapping[RRDMetric, PerformanceData] | None = None,
        time_series: Mapping[RRDMetric, TimeSeries] | None = None,
    ) -> None:
        self._performance_data = performance_data or {}
        self._time_series = time_series or {}
        self.time_series_calls: list[
            tuple[tuple[RRDMetric, ...], TimeRange, ConsolidationFunction]
        ] = []

    def fetch_performance_data(
        self, rrd_metrics: Sequence[RRDMetric]
    ) -> Mapping[RRDMetric, PerformanceData]:
        return {
            metric: self._performance_data[metric]
            for metric in rrd_metrics
            if metric in self._performance_data
        }

    def fetch_time_series(
        self,
        rrd_metrics: Sequence[RRDMetric],
        *,
        consolidation_function: ConsolidationFunction,
        time_range: TimeRange,
    ) -> Mapping[RRDMetric, TimeSeries]:
        self.time_series_calls.append((tuple(rrd_metrics), time_range, consolidation_function))
        return {
            metric: self._time_series[metric]
            for metric in rrd_metrics
            if metric in self._time_series
        }


def _update(
    *graphs: Graph,
    rrd: _FakeRRDSource,
    consolidation_function: ConsolidationFunction = ConsolidationFunction.AVERAGE,
) -> Sequence[EvaluatedGraph]:
    return evaluate_graphs(
        consolidation_function=consolidation_function,
        time_range=_time_range(),
        graphs=graphs,
        rrd=rrd,
    )


def test_empty_graphs_returns_empty_list() -> None:
    assert _update(rrd=_FakeRRDSource()) == []


def test_fetches_performance_data_and_time_series() -> None:
    cpu_user = _rrd("cpu_user")
    graph = Graph(name="cpu", title="CPU", graph_type="test", lines=[_line(cpu_user)])
    series = _ts(1.0, 2.0, 3.0)
    rrd = _FakeRRDSource({cpu_user: _perf(42.0)}, {cpu_user: series})

    [evaluated] = _update(graph, rrd=rrd)

    [line] = evaluated.lines
    assert line.curve.value == 42.0
    assert line.curve.time_series == series
    assert rrd.time_series_calls == [((cpu_user,), _time_range(), ConsolidationFunction.AVERAGE)]


def test_returns_one_evaluated_graph_per_graph_in_order() -> None:
    x, y = _rrd("x"), _rrd("y")
    graph_x = Graph(name="x", title="x", graph_type="test", lines=[_line(x)])
    graph_y = Graph(name="y", title="y", graph_type="test", lines=[_line(y)])
    rrd = _FakeRRDSource({x: _perf(1.0), y: _perf(2.0)}, {x: _ts(1.0), y: _ts(2.0)})

    results = _update(graph_x, graph_y, rrd=rrd)

    assert [[line.curve.value for line in graph.lines] for graph in results] == [[1.0], [2.0]]


def test_evaluates_lines_in_both_directions() -> None:
    in_, out = _rrd("if_in"), _rrd("if_out")
    graph = Graph(
        name="if",
        title="Interface",
        graph_type="test",
        lines=[_line(out), _line(in_, inverse=True)],
    )
    rrd = _FakeRRDSource({in_: _perf(1.0), out: _perf(2.0)}, {in_: _ts(1.0), out: _ts(2.0)})

    [evaluated] = _update(graph, rrd=rrd)

    assert [(line.curve.time_series, line.inverse) for line in evaluated.lines] == [
        (_ts(2.0), False),
        (_ts(1.0), True),
    ]


def test_resolves_a_title_expression_against_a_non_drawn_metric() -> None:
    # The title references "cores", which is not drawn; it still resolves against the service's
    # (source-delivered) performance data.
    load = _rrd("load")
    cores = RRDMetric(
        host_name=HostName("h"), service_name=ServiceName("svc"), metric_name=MetricName("cores")
    )
    graph = Graph(
        name="g",
        title='Load - _EXPRESSION:{"metric": "cores", "scalar": "max"} cores',
        graph_type="test",
        lines=[_line(load)],
    )
    rrd = _FakeRRDSource(
        {load: _perf(1.0), cores: _perf(4.0, maximum=8.0)},
        {load: _ts(1.0)},
    )

    [evaluated] = _update(graph, rrd=rrd)

    assert evaluated.title == "Load - 8 cores"
