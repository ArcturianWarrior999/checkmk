#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from collections.abc import Mapping

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    SimpleSNMPSection,
    SNMPTree,
    State,
    StringTable,
)
from cmk.plugins.perle.lib import DETECT_PERLE


def parse_perle_modules(string_table: StringTable) -> StringTable:
    return string_table


def discover_perle_cm_modules(section: StringTable) -> DiscoveryResult:
    for _name, _led, index, *_rest in section:
        yield Service(item=index)


MAP_SPEED: Mapping[str, str] = {
    "0": "10 Mbs",
    "1": "100 Mbps",
    "2": "1000 Mbps",
}

MAP_POWER_LED: Mapping[str, tuple[State, str]] = {
    "0": (State.CRIT, "no power"),
    "1": (State.OK, "power to the module"),
    "2": (State.OK, "loopback enabled"),
}

MAP_FIBER_LPRF: Mapping[str, tuple[State, str]] = {
    "0": (State.OK, "ok"),
    "1": (State.CRIT, "offline"),
    "2": (State.CRIT, "link fault"),
    "3": (State.CRIT, "auto neg error"),
    # available for cm1110 modules
    "99": (State.CRIT, "not applicable"),
}
MAP_FIBER_LINK: Mapping[str, tuple[State, str]] = {
    "0": (State.WARN, "down"),
    "1": (State.OK, "up"),
}

MAP_FIBER_CONNECTOR: Mapping[str, str] = {
    "0": "sc",
    "1": "lc",
    "2": "st",
    "3": "sfp",
    "5": "fc",
    "6": "mtrj",
}
MAP_COPPER_LPRF: Mapping[str, tuple[State, str]] = {
    "0": (State.OK, "ok"),
    "1": (State.CRIT, "remote fault"),
}

MAP_COPPER_LINK: Mapping[str, tuple[State, str]] = {
    "0": (State.WARN, "down"),
    "1": (State.OK, "ok"),
}

MAP_COPPER_CONNECTOR: Mapping[str, str] = {
    "0": "rj45",
}


def check_perle_cm_modules(item: str, section: StringTable) -> CheckResult:
    for (
        _name,
        power_led,
        index,
        fiber_lprf,
        fiber_link,
        fiber_connector,
        fiber_speed,
        copper_lprf,
        copper_link,
        copper_connector,
        copper_speed,
    ) in section:
        if item != index:
            continue

        state, state_readable = MAP_POWER_LED[power_led]
        yield Result(state=state, summary=f"Power status: {state_readable}")

        yield Result(state=State.OK, summary=f"Fiber speed: {MAP_SPEED[fiber_speed]}")
        state, state_readable = MAP_FIBER_LPRF[fiber_lprf]
        yield Result(state=state, summary=f"LPRF: {state_readable}")
        state, state_readable = MAP_FIBER_LINK[fiber_link]
        yield Result(state=state, summary=f"Link: {state_readable}")
        yield Result(state=State.OK, summary=f"Connector: {MAP_FIBER_CONNECTOR[fiber_connector]}")

        yield Result(state=State.OK, summary=f"Copper speed: {MAP_SPEED[copper_speed]}")
        state, state_readable = MAP_COPPER_LPRF[copper_lprf]
        yield Result(state=state, summary=f"LPRF: {state_readable}")
        state, state_readable = MAP_COPPER_LINK[copper_link]
        yield Result(state=state, summary=f"Link: {state_readable}")
        yield Result(state=State.OK, summary=f"Connector: {MAP_COPPER_CONNECTOR[copper_connector]}")


snmp_section_perle_modules_cm1110 = SimpleSNMPSection(
    name="perle_modules_cm1110",
    parse_function=parse_perle_modules,
    detect=DETECT_PERLE,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.1966.21.1.1.1.1.4.3",
        oids=[
            "1.1.3",
            "3.1.3",
            "1.1.2",
            "1.1.21",
            "1.1.15",
            "1.1.16",
            "1.1.18",
            "1.1.32",
            "1.1.25",
            "1.1.26",
            "1.1.28",
        ],
    ),
)


check_plugin_perle_modules_cm1110 = CheckPlugin(
    name="perle_modules_cm1110",
    service_name="Chassis slot %s CM1110",
    discovery_function=discover_perle_cm_modules,
    check_function=check_perle_cm_modules,
)


snmp_section_perle_modules_cm1000 = SimpleSNMPSection(
    name="perle_modules_cm1000",
    parse_function=parse_perle_modules,
    detect=DETECT_PERLE,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.1966.21.1.1.1.1.4.1",
        oids=[
            "1.1.3",
            "3.1.3",
            "1.1.2",
            "1.1.18",
            "1.1.12",
            "1.1.13",
            "1.1.15",
            "1.1.28",
            "1.1.21",
            "1.1.22",
            "1.1.24",
        ],
    ),
)


check_plugin_perle_modules_cm1000 = CheckPlugin(
    name="perle_modules_cm1000",
    service_name="Chassis slot %s CM1000",
    discovery_function=discover_perle_cm_modules,
    check_function=check_perle_cm_modules,
)
