#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import TypedDict

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    SNMPSection,
    SNMPTree,
    State,
    StringTable,
)
from cmk.plugins.genua.lib import DETECT_GENUA
from cmk.plugins.lib.fan import check_fan


class FanParams(TypedDict, total=False):
    lower: tuple[float, float]
    upper: tuple[float, float]
    output_metrics: bool


@dataclass(frozen=True)
class Fan:
    rpm: int
    state: str


Section = Mapping[str, Fan]


def parse_genua_fan(string_table: Sequence[StringTable]) -> Section:
    # only the first non-empty tree is relevant; the others are due to the
    # alternative enterprise id in the SNMP fetch.
    for tree in string_table:
        if tree:
            return {name: Fan(rpm=int(reading), state=state) for name, reading, state in tree}
    return {}


def discover_genua_fan(section: Section) -> DiscoveryResult:
    yield from (Service(item=name) for name in section)


def check_genua_fan(item: str, params: FanParams, section: Section) -> CheckResult:
    map_states = {
        "1": (State.OK, "OK"),
        "2": (State.WARN, "warning"),
        "3": (State.CRIT, "critical"),
        "4": (State.CRIT, "unknown"),
        "5": (State.CRIT, "unknown"),
        "6": (State.CRIT, "unknown"),
    }

    if (fan := section.get(item)) is None:
        return

    state, state_readable = map_states[fan.state]
    yield Result(state=state, summary=f"Status: {state_readable}")
    yield from check_fan(fan.rpm, params)


snmp_section_genua_fan = SNMPSection(
    name="genua_fan",
    detect=DETECT_GENUA,
    fetch=[
        SNMPTree(
            base=".1.3.6.1.4.1.3717.2.1.1.1.1",
            oids=["2", "3", "4"],
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.3137.2.1.1.1.1",
            oids=["2", "3", "4"],
        ),
    ],
    parse_function=parse_genua_fan,
)


check_plugin_genua_fan = CheckPlugin(
    name="genua_fan",
    service_name="FAN %s",
    discovery_function=discover_genua_fan,
    check_function=check_genua_fan,
    check_ruleset_name="hw_fans",
    check_default_parameters=FanParams(
        lower=(2000, 1000),
        upper=(8000, 8400),
    ),
)
