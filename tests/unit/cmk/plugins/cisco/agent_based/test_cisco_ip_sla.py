#!/usr/bin/env python3
# Copyright (C) 2025 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Sequence

from cmk.agent_based.v2 import Metric, Result, Service, State, StringByteTable
from cmk.plugins.cisco.agent_based.cisco_ip_sla import (
    check_cisco_ip_sla,
    discover_cisco_ip_sla,
    parse_cisco_ip_sla,
)

_STRING_TABLE: Sequence[StringByteTable] = [
    [["6", [10, 96, 66, 4], [10, 96, 27, 69], "1"]],
    [["6", "", "", "9", "5000"]],
    [["6", "6", "", "2", "2", "2"]],
    [["6", "25", "1"]],
]


def test_discover_cisco_ip_sla() -> None:
    parsed = parse_cisco_ip_sla(_STRING_TABLE)
    result = list(discover_cisco_ip_sla(parsed))
    assert result == [Service(item="6")]


def test_check_cisco_ip_sla() -> None:
    params = {
        "completion_time_over_treshold_occured": "no",
        "connection_lost_occured": "no",
        "latest_rtt_completion_time": (250, 500),
        "latest_rtt_state": "ok",
        "state": "active",
        "timeout_occured": "no",
    }
    parsed = parse_cisco_ip_sla(_STRING_TABLE)
    result = list(check_cisco_ip_sla("6", params, parsed))
    assert result == [
        Result(state=State.OK, summary="Target address: 10.96.66.4"),
        Result(state=State.OK, summary="Source address: 10.96.27.69"),
        Result(state=State.OK, summary="RTT type: jitter"),
        Result(state=State.OK, summary="Threshold: 5000 ms"),
        Result(state=State.OK, summary="State: active"),
        Result(state=State.OK, summary="Connection lost occured: no"),
        Result(state=State.OK, summary="Timeout occured: no"),
        Result(state=State.OK, summary="Completion time over treshold occured: no"),
        Result(state=State.OK, summary="Latest RTT completion time: 25 ms"),
        Metric("rtt", 0.025, levels=(0.25, 0.5)),
        Result(state=State.OK, summary="Latest RTT state: ok"),
    ]
