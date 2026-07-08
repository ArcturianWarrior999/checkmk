#!/usr/bin/env python3
# Copyright (C) 2025 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Sequence

import pytest

from cmk.agent_based.v2 import Result, Service, State
from cmk.plugins.genua.agent_based.genua_fan import (
    check_genua_fan,
    discover_genua_fan,
    FanParams,
    parse_genua_fan,
)

_STRING_TABLE = [
    [["fan1", "5000", "1"], ["fan2", "3000", "2"], ["fan3", "9000", "3"]],
    [],
]

_PARAMS = FanParams(lower=(2000, 1000), upper=(8000, 8400))


@pytest.mark.parametrize(
    "string_table, expected_discoveries",
    [
        (
            _STRING_TABLE,
            [Service(item="fan1"), Service(item="fan2"), Service(item="fan3")],
        ),
        ([[], []], []),
    ],
)
def test_discover_genua_fan(
    string_table: Sequence[list[list[str]]],
    expected_discoveries: Sequence[Service],
) -> None:
    """Test discovery function for genua_fan check."""
    parsed = parse_genua_fan(string_table)
    assert list(discover_genua_fan(parsed)) == expected_discoveries


@pytest.mark.parametrize(
    "item, params, string_table, expected_results",
    [
        (
            "fan1",
            _PARAMS,
            _STRING_TABLE,
            [
                Result(state=State.OK, summary="Status: OK"),
                Result(state=State.OK, summary="Speed: 5000 RPM"),
            ],
        ),
        (
            "fan2",
            _PARAMS,
            _STRING_TABLE,
            [
                Result(state=State.WARN, summary="Status: warning"),
                Result(state=State.OK, summary="Speed: 3000 RPM"),
            ],
        ),
        (
            "fan3",
            _PARAMS,
            _STRING_TABLE,
            [
                Result(state=State.CRIT, summary="Status: critical"),
                Result(
                    state=State.CRIT,
                    summary="Speed: 9000 RPM (warn/crit at 8000 RPM/8400 RPM)",
                ),
            ],
        ),
        (
            "missing",
            _PARAMS,
            _STRING_TABLE,
            [],
        ),
    ],
)
def test_check_genua_fan(
    item: str,
    params: FanParams,
    string_table: Sequence[list[list[str]]],
    expected_results: Sequence[Result],
) -> None:
    """Test check function for genua_fan check."""
    parsed = parse_genua_fan(string_table)
    assert list(check_genua_fan(item, params, parsed)) == expected_results
