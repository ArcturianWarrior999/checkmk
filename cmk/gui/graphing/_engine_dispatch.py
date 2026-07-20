#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field

from cmk.ccc.plugin_registry import Registry
from cmk.graphing_engine import ConsolidationFunction, EvaluatedGraph, Graph, TimeRange

from ._engine_rrd import FetchDiagnostics
from ._engine_serialization import consolidation_function_of, ensure_type, Json, time_range_of


@dataclass(frozen=True, kw_only=True)
class GraphDataRequest:
    graph_type: str
    graphs: Mapping[str, object]
    options: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True)
class CommonGraphOptions:
    # The options common to every graph type's evaluation. A graph type only defines its own options
    # dataclass when it needs more than these (e.g. combined graphs add their combination mode).
    consolidation_function: ConsolidationFunction
    time_range: TimeRange

    @classmethod
    def from_request_options(cls, options: Mapping[str, object]) -> CommonGraphOptions:
        return cls(
            consolidation_function=consolidation_function_of(options),
            time_range=time_range_of(options),
        )


@dataclass(frozen=True, kw_only=True)
class EvaluatedGraphs:
    # The evaluated graphs plus the non-fatal fetch diagnostics (hit series caps, fetch errors) the
    # caller surfaces to the user - the engine evaluation itself stays diagnostics-free.
    graphs: Sequence[EvaluatedGraph]
    diagnostics: FetchDiagnostics


@dataclass(frozen=True)
class EngineGraphDispatcher:
    kind: str
    serialize: Callable[[Sequence[Graph]], Json]
    evaluate: Callable[[GraphDataRequest], EvaluatedGraphs]


class EngineGraphDispatcherRegistry(Registry[EngineGraphDispatcher]):
    def plugin_name(self, instance: EngineGraphDispatcher) -> str:
        return instance.kind


engine_graph_dispatcher_registry = EngineGraphDispatcherRegistry()


def serialize_graphs(graphs: Sequence[Graph]) -> Json:
    by_graph_type: dict[str, list[Graph]] = {}
    for graph in graphs:
        by_graph_type.setdefault(graph.graph_type, []).append(graph)
    serialized: list[object] = []
    for graph_type, batch in by_graph_type.items():
        dispatcher = engine_graph_dispatcher_registry[graph_type]
        serialized.extend(ensure_type(dispatcher.serialize(batch)["graphs"], list))
    return {"graphs": serialized}


def evaluate_graphs(request: GraphDataRequest) -> EvaluatedGraphs:
    return engine_graph_dispatcher_registry[request.graph_type].evaluate(request)
