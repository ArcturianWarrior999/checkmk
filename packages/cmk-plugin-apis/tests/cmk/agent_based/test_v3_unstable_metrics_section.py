#!/usr/bin/env python3
# Copyright (C) 2025 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


import pytest

from cmk.agent_based.v2 import AgentSection, RuleSetType, StringTable
from cmk.agent_based.v3_unstable import (
    GaugeAggregation,
    MetricSelector,
    MetricsSection,
)

HOST_LABEL_PARAMS = {"level": "all"}


# --- Tests ---


def parse_func(_string_table: StringTable) -> dict[str, object]:
    return {"": ""}


def test_metric_backend_section_instantiation() -> None:
    """
    Test that the class can be instantiated correctly and all
    attributes, including those from the base class (via **kwargs), are set.
    """
    # 1. Define the filter configuration
    my_filter = MetricSelector(metric_name="cpu.load", aggregation=GaugeAggregation())
    my_filter2 = MetricSelector(metric_name="cpu.temperature", aggregation=GaugeAggregation())

    # 2. Create the section with *all* possible arguments
    section = MetricsSection(  # type: ignore[call-overload]
        # MetricsSection specific args
        name="test_section",
        selectors=[my_filter, my_filter2],
        # AgentSection args passed via **kwargs
        parse_function=parse_func,
        supersedes=["old_section"],
        parsed_section_name="my_parsed_name",
        host_label_default_parameters=HOST_LABEL_PARAMS,
        host_label_ruleset_name="my_ruleset",
        host_label_ruleset_type=RuleSetType.ALL,
    )

    # --- Assertions ---
    assert section.selectors[0] is my_filter
    assert section.selectors[0].metric_name == "cpu.load"
    assert section.selectors[1] is my_filter2
    assert section.selectors[1].metric_name == "cpu.temperature"
    assert section.parse_function is parse_func
    assert section.name == "test_section"
    assert section.supersedes == ["old_section"]
    assert section.parsed_section_name == "my_parsed_name"
    assert isinstance(section, AgentSection)
    assert section.host_label_default_parameters is HOST_LABEL_PARAMS
    assert section.host_label_ruleset_name == "my_ruleset"
    assert section.host_label_ruleset_type == RuleSetType.ALL


@pytest.mark.parametrize(
    "kwargs",
    [
        {"name": "cpu.load", "parse_function": dict},
        {
            "name": "cpu.temperature",
            "selectors": [MetricSelector(metric_name="cpu.load", aggregation=GaugeAggregation())],
        },
        {
            "parse_function": dict,
            "selectors": [MetricSelector(metric_name="cpu.load", aggregation=GaugeAggregation())],
        },
    ],
)
def test_missing_required_arguments(kwargs: dict[str, object]) -> None:
    """
    Test that instantiating without required arguments raises a TypeError.
    """
    # Test missing metric_filter
    with pytest.raises(TypeError):
        MetricsSection(**kwargs)  # type: ignore[call-overload]
