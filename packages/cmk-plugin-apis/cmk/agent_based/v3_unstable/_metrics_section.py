#!/usr/bin/env python3
# Copyright (C) 2025 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Literal, overload, TypeVar

from cmk.agent_based.v2 import (
    AgentParseFunction,
    AgentSection,
    HostLabelGenerator,
    RuleSetType,
    StringTable,
)

_Section = TypeVar("_Section")
_HostLabelFunctionNoParams = Callable[[_Section], HostLabelGenerator]
_HostLabelFunctionMergedParams = Callable[[Mapping[str, object], _Section], HostLabelGenerator]
_HostLabelFunctionAllParams = Callable[
    [Sequence[Mapping[str, object]], _Section], HostLabelGenerator
]


# NOTE: The dataclasses below duplicate quite a few things from
# cmk.metric_backend.query.models.attribute_filter. Is there a
# reason for not simply using the metric backend data types?


@dataclass(kw_only=True, frozen=True)
class ScopeFilter:
    key: str
    value: str


@dataclass(kw_only=True, frozen=True)
class ResourceFilter:
    key: str
    value: str


@dataclass(kw_only=True, frozen=True)
class DatapointFilter:
    key: str
    value: str


AttributeFilter = ScopeFilter | DatapointFilter | ResourceFilter


@dataclass(kw_only=True, frozen=True)
class GaugeAggregation:
    """
    Gauge data point types will always return the latest value of the last minute.
    """

    lookback_minutes: int = 1


@dataclass(kw_only=True, frozen=True)
class SumAggregation:
    """
    Sum data point types will always return the delta value between the first and the last value
    in the aggregation timespan, even when the data point is cumulative.
    Therefor the aggregation minutes should be set to a multiple (5x) of datapoint emission period.
    E.g. when a datapoint is emitted every minute, aggregation minutes should be at least 5 minutes.
    The timespan is the time from the execution of the check minus the aggregation_minutes.
    """

    aggregation_minutes: int = 1


@dataclass(kw_only=True, frozen=True)
class HistogramAggregation:
    """
    Histogram data point types will always return the delta for count and rate between the first and
    last data point in the aggregation timespan, even when the data point is cumulative.
    Therefor the aggregation minutes should be set to a multiple (5x) of datapoint emission period.
    E.g. when a datapoint is emitted every minute, aggregation minutes should be at least 5 minutes.
    The timespan is the time from the execution of the check minus the aggregation_minutes.

    A list of quantiles can be provided to calculate the distribution of values in the buckets.
    The values must be provided between 0 and 1, and will be returned in the same order as provided.
    """

    aggregation_minutes: int = 1
    quantiles: Sequence[float] = field(default_factory=list)


@dataclass(kw_only=True, frozen=True)
class InstantAggregation:
    """
    Returns the value for the smallest possible time range for all data points.
    Currently, that is 1 minute.
    """

    lookback_minutes: int = 1


Aggregation = GaugeAggregation | SumAggregation | HistogramAggregation | InstantAggregation


@dataclass(kw_only=True, frozen=True)
class MetricSelector:
    """
    Configuration object for selecting metric sections.

    [metric_name AND [attribute_filter AND attribute_filter]]

    Args:
        name:               A arbitrary string that identifies the selector and will be returned with the selected data point
        metric_name:        A metric name to be filtered for
        attribute_filters:  Only data points that match all provided filters will match
        aggregation:        Aggregation object, that determines how values are aggregated over a
                            defined time range.
                            For "instant" values choose 1 minute as the time range.
                            Not setting the aggregation will return the "instant" value, independent of datatype.
    """

    name: str = ""
    metric_name: str | None
    attribute_filters: Sequence[AttributeFilter] = ()
    aggregation: Aggregation = InstantAggregation()


@dataclass(kw_only=True)
class MetricBackendSection(AgentSection[Mapping[str, object]]):
    """
    A specialized AgentSection that pre-filters raw agent data
    fom the metric backend as a data source.

    Args:
        filters:            An list of filters to apply to the metric backend
                            to filter for data.

    Example:
        Get all data points for the cpu.aggregated metric. If the data points returned are
        of metric type Gauge, only the latest value will be returned
        >>> agent_section_metric_backend_example = MetricBackendSection(
        ...     name="example_check_plugin",
        ...     selectors=[MetricSelector(
        ...         name="filter_gauge",
        ...         metric_name="cpu.frequency",
        ...     )],
        ...     parse_function=lambda x: x
        ... )

        Get all aggregated data points for the http.server.requests.duration metric
        produced by a (made-up) http-collector exporter for the last minute
        >>> agent_section_metric_backend_example = MetricBackendSection(
        ...     name="example_check_plugin",
        ...     selectors=[MetricSelector(
        ...         name="filter_1",
        ...         metric_name="http.server.requests.duration",
        ...         attribute_filters=[
        ...             ScopeFilter(
        ...                 key="exporter",
        ...                 value="http-collector.github.com"
        ...             )
        ...         ],
        ...     )],
        ...     parse_function=lambda x: x
        ... )

        Get all aggregated data points for the http.server.requests.duration metric
        (which is a histogram metric), aggregated over the last 60 minutes with
        precalculated percentiles for the 50th (mean) and 99th percentile
        >>> agent_section_metric_backend_example = MetricBackendSection(
        ...     name="example_check_plugin",
        ...     selectors=[MetricSelector(
        ...         name="filter_60",
        ...         metric_name="http.server.requests.duration",
        ...         aggregation=HistogramAggregation(
        ...             aggregation_minutes=60,
        ...             quantiles=[0.50, 0.99]
        ...         )
        ...     )],
        ...     parse_function=lambda x: x
        ... )

        Get all aggregated data points for the http.server.requests.duration metric
        (which is a histogram metric), aggregated over the last 15 minutes with
        precalculated percentiles for the 50th (mean) and 99th percentile
        as well as all aggregated data points over the last 60 minutes with
        precalculated percentiles for the 75th and 99th percentile
        >>> agent_section_metric_backend_example = MetricBackendSection(
        ...     name="example_check_plugin",
        ...     selectors=[MetricSelector(
        ...         name="filter_15",
        ...         metric_name="http.server.requests.duration",
        ...         aggregation=HistogramAggregation(
        ...             aggregation_minutes=15,
        ...             quantiles=[0.50, 0.99]
        ...         )
        ...     ),
        ...     MetricSelector(
        ...         name="filter_60",
        ...         metric_name="http.server.requests.duration",
        ...         aggregation=HistogramAggregation(
        ...             aggregation_minutes=60,
        ...             quantiles=[0.75, 0.99]
        ...         )
        ...     )],
        ...     parse_function=lambda x: x
        ... )
    """

    selectors: Sequence[MetricSelector]

    @overload
    def __init__(
        self,
        *,
        name: str,
        selectors: Sequence[MetricSelector],
        parse_function: AgentParseFunction[_Section],
        host_label_function: _HostLabelFunctionNoParams[_Section] | None = None,
        host_label_default_parameters: None = None,
        host_label_ruleset_name: None = None,
        host_label_ruleset_type: RuleSetType = RuleSetType.MERGED,
        parsed_section_name: str | None = None,
        supersedes: list[str] | None = None,
    ): ...

    @overload
    def __init__(
        self,
        *,
        name: str,
        selectors: Sequence[MetricSelector],
        parse_function: AgentParseFunction[_Section],
        host_label_function: _HostLabelFunctionMergedParams[_Section],
        host_label_default_parameters: Mapping[str, object],
        host_label_ruleset_name: str,
        host_label_ruleset_type: Literal[RuleSetType.MERGED] = RuleSetType.MERGED,
        parsed_section_name: str | None = None,
        supersedes: list[str] | None = None,
    ): ...

    @overload
    def __init__(
        self,
        *,
        name: str,
        selectors: Sequence[MetricSelector],
        parse_function: Callable[[StringTable], _Section | None],
        host_label_function: _HostLabelFunctionAllParams[_Section],
        host_label_default_parameters: Mapping[str, object],
        host_label_ruleset_name: str,
        host_label_ruleset_type: Literal[RuleSetType.ALL],
        parsed_section_name: str | None = None,
        supersedes: list[str] | None = None,
    ): ...

    def __init__(
        self,
        *,
        selectors: Sequence[MetricSelector],
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.selectors = selectors
