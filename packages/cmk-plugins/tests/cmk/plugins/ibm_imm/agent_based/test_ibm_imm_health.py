#!/usr/bin/env python3
# Copyright (C) 2025 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Sequence

import pytest

from cmk.agent_based.v2 import Result, Service, State, StringTable
from cmk.plugins.ibm_imm.agent_based.ibm_imm_health import (
    check_ibm_imm_health,
    discover_ibm_imm_health,
    parse_ibm_imm_health,
)


@pytest.mark.parametrize(
    "string_table, expected_discoveries",
    [
        ([["223523"], ["2342"], ["234"], ["23352"]], [Service()]),
    ],
)
def test_discover_ibm_imm_health(
    string_table: StringTable, expected_discoveries: Sequence[Service]
) -> None:
    """Test discovery function for ibm_imm_health check."""
    parsed = parse_ibm_imm_health(string_table)
    result = list(discover_ibm_imm_health(parsed))
    assert result == expected_discoveries


@pytest.mark.parametrize(
    "string_table, expected_results",
    [
        (
            [["223523"], ["2342"], ["234"], ["23352"]],
            [Result(state=State.UNKNOWN, summary="23352(234)")],
        ),
    ],
)
def test_check_ibm_imm_health(
    string_table: StringTable, expected_results: Sequence[Result]
) -> None:
    """Test check function for ibm_imm_health check."""
    parsed = parse_ibm_imm_health(string_table)
    result = list(check_ibm_imm_health(parsed))
    assert result == expected_results
