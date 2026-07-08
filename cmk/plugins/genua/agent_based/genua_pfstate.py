#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TypedDict

from cmk.agent_based.v2 import (
    check_levels,
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

# Example Agent Output:
# GENUA-MIB:
# .1.3.6.1.4.1.3717.2.1.1.6.1 = INTEGER: 300000
# .1.3.6.1.4.1.3717.2.1.1.6.2 = INTEGER: 1268
# .1.3.6.1.4.1.3717.2.1.1.6.3 = INTEGER: 1


class Params(TypedDict):
    used: tuple[int, int] | None


@dataclass(frozen=True)
class PfState:
    maximum: int
    used: int
    status: str


Section = PfState


def parse_genua_pfstate(string_table: Sequence[StringTable]) -> Section | None:
    # remove empty elements due to alternative enterprise id in snmp_info
    non_empty = [tree for tree in string_table if tree]
    if non_empty and len(non_empty[0][0]) == 3:
        maximum, used, status = non_empty[0][0]
        return PfState(maximum=int(maximum), used=int(used), status=status)
    return None


def discover_genua_pfstate(section: Section | None) -> DiscoveryResult:
    if section is not None:
        yield Service()


def pfstate(st: str) -> str:
    names = {
        "0": "notOK",
        "1": "OK",
        "2": "unknown",
    }
    return names.get(st, st)


def check_genua_pfstate(params: Params, section: Section | None) -> CheckResult:
    if section is None:
        yield Result(state=State.UNKNOWN, summary="Invalid Output from Agent")
        return

    yield Result(
        state=State.OK if section.status == "1" else State.WARN,
        summary=f"PF State: {pfstate(section.status)}",
    )

    used = params["used"]
    yield from check_levels(
        section.used,
        levels_upper=("fixed", used) if used else None,
        metric_name="statesused",
        render_func=str,
        label="States used",
        boundaries=(0, section.maximum),
    )

    yield Result(state=State.OK, summary=f"States max: {section.maximum}")


snmp_section_genua_pfstate = SNMPSection(
    name="genua_pfstate",
    detect=DETECT_GENUA,
    fetch=[
        SNMPTree(
            base=".1.3.6.1.4.1.3717.2.1.1.6",
            oids=["1", "2", "3"],
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.3137.2.1.1.6",
            oids=["1", "2", "3"],
        ),
    ],
    parse_function=parse_genua_pfstate,
)


check_plugin_genua_pfstate = CheckPlugin(
    name="genua_pfstate",
    service_name="Paketfilter Status",
    discovery_function=discover_genua_pfstate,
    check_function=check_genua_pfstate,
    check_ruleset_name="pf_used_states",
    check_default_parameters=Params(used=None),
)
