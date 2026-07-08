#!/usr/bin/env python3
# Copyright (C) 2025 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Sequence

import pytest

from cmk.agent_based.v2 import Metric, Result, Service, State
from cmk.plugins.genua.agent_based.genua_pfstate import (
    check_genua_pfstate,
    discover_genua_pfstate,
    Params,
    parse_genua_pfstate,
)

_STRING_TABLE = [[["300000", "1268", "1"]], []]


@pytest.mark.parametrize(
    "string_table, expected_discoveries",
    [
        (_STRING_TABLE, [Service()]),
        ([[], []], []),
        ([[["300000", "1268"]], []], []),
    ],
)
def test_discover_genua_pfstate(
    string_table: Sequence[list[list[str]]],
    expected_discoveries: Sequence[Service],
) -> None:
    """Test discovery function for genua_pfstate check."""
    parsed = parse_genua_pfstate(string_table)
    assert list(discover_genua_pfstate(parsed)) == expected_discoveries


@pytest.mark.parametrize(
    "params, string_table, expected_results",
    [
        (
            {"used": None},
            _STRING_TABLE,
            [
                Result(state=State.OK, summary="PF State: OK"),
                Result(state=State.OK, summary="States used: 1268"),
                Metric("statesused", 1268.0, boundaries=(0.0, 300000.0)),
                Result(state=State.OK, summary="States max: 300000"),
            ],
        ),
        (
            {"used": (1000, 2000)},
            _STRING_TABLE,
            [
                Result(state=State.OK, summary="PF State: OK"),
                Result(
                    state=State.WARN,
                    summary="States used: 1268 (warn/crit at 1000/2000)",
                ),
                Metric(
                    "statesused",
                    1268.0,
                    levels=(1000.0, 2000.0),
                    boundaries=(0.0, 300000.0),
                ),
                Result(state=State.OK, summary="States max: 300000"),
            ],
        ),
        (
            {"used": None},
            [[["300000", "1268", "0"]], []],
            [
                Result(state=State.WARN, summary="PF State: notOK"),
                Result(state=State.OK, summary="States used: 1268"),
                Metric("statesused", 1268.0, boundaries=(0.0, 300000.0)),
                Result(state=State.OK, summary="States max: 300000"),
            ],
        ),
        (
            {"used": None},
            [[["300000", "1268"]], []],
            [Result(state=State.UNKNOWN, summary="Invalid Output from Agent")],
        ),
    ],
)
def test_check_genua_pfstate(
    params: Params,
    string_table: Sequence[list[list[str]]],
    expected_results: Sequence[Result | Metric],
) -> None:
    """Test check function for genua_pfstate check."""
    parsed = parse_genua_pfstate(string_table)
    assert list(check_genua_pfstate(params, parsed)) == expected_results
