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
    FetchedData,
    Graph,
    HostName,
    Line,
    Metric,
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


def _fetched(value: float | None, series: TimeSeries | None) -> Sequence[FetchedData]:
    return [FetchedData(performance_data=_perf(value), time_series=series)]


class _FakeRRDSource:
    # The source already delivers translated, per-Metric FetchedData; the engine only orchestrates.
    def __init__(self, fetched: Mapping[Metric, Sequence[FetchedData]] | None = None) -> None:
        self._fetched = fetched or {}

    def fetch(
        self,
        metrics: Sequence[Metric],
        *,
        consolidation_function: ConsolidationFunction,  # noqa: ARG002
        time_range: TimeRange,  # noqa: ARG002
    ) -> Mapping[Metric, Sequence[FetchedData]]:
        return {metric: self._fetched[metric] for metric in metrics if metric in self._fetched}


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
    rrd = _FakeRRDSource({cpu_user: _fetched(42.0, series)})

    [evaluated] = _update(graph, rrd=rrd)

    [line] = evaluated.lines
    assert line.curve.value == 42.0
    assert line.curve.time_series == series


def test_returns_one_evaluated_graph_per_graph_in_order() -> None:
    x, y = _rrd("x"), _rrd("y")
    graph_x = Graph(name="x", title="x", graph_type="test", lines=[_line(x)])
    graph_y = Graph(name="y", title="y", graph_type="test", lines=[_line(y)])
    rrd = _FakeRRDSource({x: _fetched(1.0, _ts(1.0)), y: _fetched(2.0, _ts(2.0))})

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
    rrd = _FakeRRDSource({in_: _fetched(1.0, _ts(1.0)), out: _fetched(2.0, _ts(2.0))})

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
        {
            load: _fetched(1.0, _ts(1.0)),
            cores: [FetchedData(performance_data=_perf(4.0, maximum=8.0), time_series=None)],
        }
    )

    [evaluated] = _update(graph, rrd=rrd)

    assert evaluated.title == "Load - 8 cores"
