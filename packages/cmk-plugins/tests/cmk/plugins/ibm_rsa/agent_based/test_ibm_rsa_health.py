#!/usr/bin/env python3
# Copyright (C) 2025 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Sequence

import pytest

from cmk.agent_based.v2 import Result, Service, State, StringTable
from cmk.plugins.ibm_rsa.agent_based.ibm_rsa_health import (
    check_ibm_rsa_health,
    discover_ibm_rsa_health,
    parse_ibm_rsa_health,
)


@pytest.mark.parametrize(
    "string_table, expected_discoveries",
    [
        ([["0"], ["1"], ["Critical"], ["SSL Server Certificate Error"]], [Service()]),
    ],
)
def test_discover_ibm_rsa_health(
    string_table: StringTable, expected_discoveries: Sequence[Service]
) -> None:
    """Test discovery function for ibm_rsa_health check."""
    parsed = parse_ibm_rsa_health(string_table)
    result = list(discover_ibm_rsa_health(parsed))
    assert result == expected_discoveries


@pytest.mark.parametrize(
    "string_table, expected_results",
    [
        (
            [["0"], ["1"], ["Critical"], ["SSL Server Certificate Error"]],
            [Result(state=State.CRIT, summary="SSL Server Certificate Error(Critical)")],
        ),
    ],
)
def test_check_ibm_rsa_health(
    string_table: StringTable, expected_results: Sequence[Result]
) -> None:
    """Test check function for ibm_rsa_health check."""
    parsed = parse_ibm_rsa_health(string_table)
    result = list(check_ibm_rsa_health(parsed))
    assert result == expected_results
