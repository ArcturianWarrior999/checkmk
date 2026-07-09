#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Mapping
from typing import Any

from cmk.agent_based.legacy.conversion import (
    # Temporary compatibility layer until we migrate the corresponding ruleset.
    check_levels_legacy_compatible as check_levels,
)
from cmk.agent_based.v2 import CheckPlugin, CheckResult, DiscoveryResult, Result, Service, State

Section = dict[str, dict[str, int]]


def discover_cisco_vpn_sessions(section: Section) -> DiscoveryResult:
    yield from (Service(item=item) for item in section)


def check_cisco_vpn_sessions(item: str, params: Mapping[str, Any], section: Section) -> CheckResult:
    if not (data := section.get(item)):
        return
    yield from check_levels(
        data["active_sessions"],
        "active_sessions",
        params.get("active_sessions"),
        infoname="Active sessions",
        human_readable_func=int,
    )

    if item != "Summary":
        yield from check_levels(
            data["peak_sessions"],
            "active_sessions_peak",
            None,
            infoname="Peak count",
            human_readable_func=int,
        )

    if "maximum_sessions" in data:
        yield Result(state=State.OK, summary=f"Overall system maximum: {data['maximum_sessions']}")

    yield Result(state=State.OK, summary=f"Cumulative count: {data['cumulative_sessions']}")


check_plugin_cisco_vpn_sessions = CheckPlugin(
    name="cisco_vpn_sessions",
    service_name="VPN Sessions %s",
    discovery_function=discover_cisco_vpn_sessions,
    check_function=check_cisco_vpn_sessions,
    check_ruleset_name="cisco_vpn_sessions",
    check_default_parameters={},
)
