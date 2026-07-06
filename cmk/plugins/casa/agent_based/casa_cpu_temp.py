#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from collections.abc import Mapping, Sequence

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    get_value_store,
    OIDEnd,
    Result,
    Service,
    SNMPSection,
    SNMPTree,
    State,
    StringTable,
)
from cmk.plugins.casa.lib import DETECT_CASA
from cmk.plugins.lib.temperature import check_temperature, TempParamType

Section = Mapping[str, Mapping[str, str | None]]


def _beautify_module_text(text: str) -> str:
    text = text.replace("temperature sensor", "")
    if text.startswith("Module "):
        text = text.rsplit(None, 1)[0]  # Drop trailing " CPU"
    return text


def parse_casa_cpu_temp(string_table: Sequence[StringTable]) -> Section:
    entity_names = {int(k): v for k, v in string_table[0]}
    temp_value = {int(k): v for k, v in string_table[1]}
    temp_status = {int(k): v for k, v in string_table[2]}
    temp_unit = {int(k): v for k, v in string_table[3]}
    data: dict[str, Mapping[str, str | None]] = {}
    for entry in string_table[1]:
        entry_nr = int(entry[0])
        data[_beautify_module_text(entity_names[entry_nr])] = {
            "temp_value": temp_value.get(entry_nr),
            "temp_status": temp_status.get(entry_nr),
            "temp_unit": temp_unit.get(entry_nr),
        }
    return data


def discover_casa_cpu_temp(section: Section) -> DiscoveryResult:
    for key, value in section.items():
        if value.get("temp_value"):
            yield Service(item=key)


def check_casa_cpu_temp(item: str, params: TempParamType, section: Section) -> CheckResult:
    if (data := section.get(item)) is None:
        return
    if data["temp_status"] != "1":
        yield Result(state=State.CRIT, summary="Sensor failure!")
        return
    if (temp_value := data["temp_value"]) is None:
        return
    yield from check_temperature(
        float(temp_value) / 10,
        params,
        unique_name="case_cpu_temp_%s" % item,
        value_store=get_value_store(),
    )


snmp_section_casa_cpu_temp = SNMPSection(
    name="casa_cpu_temp",
    detect=DETECT_CASA,
    fetch=[
        SNMPTree(
            base=".1.3.6.1.2.1.47.1.1.1.1",
            oids=[OIDEnd(), "2"],
        ),
        SNMPTree(
            base=".1.3.6.1.2.1.99.1.1.1",
            oids=[OIDEnd(), "4"],
        ),
        SNMPTree(
            base=".1.3.6.1.2.1.99.1.1.1",
            oids=[OIDEnd(), "5"],
        ),
        SNMPTree(
            base=".1.3.6.1.2.1.99.1.1.1",
            oids=[OIDEnd(), "6"],
        ),
    ],
    parse_function=parse_casa_cpu_temp,
)
check_plugin_casa_cpu_temp = CheckPlugin(
    name="casa_cpu_temp",
    service_name="Temperature CPU %s",
    discovery_function=discover_casa_cpu_temp,
    check_function=check_casa_cpu_temp,
    check_ruleset_name="temperature",
    check_default_parameters={},
)
