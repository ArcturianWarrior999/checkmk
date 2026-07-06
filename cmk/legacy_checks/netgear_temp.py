#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

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
from cmk.plugins.lib.temperature import check_temperature, TempParamType
from cmk.plugins.netgear.lib import DETECT_NETGEAR

# .1.3.6.1.4.1.4526.10.43.1.8.1.2.1.0 0 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorType.1.0
# .1.3.6.1.4.1.4526.10.43.1.8.1.2.1.1 0 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorType.1.1
# .1.3.6.1.4.1.4526.10.43.1.8.1.2.1.2 0 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorType.1.2
# .1.3.6.1.4.1.4526.10.43.1.8.1.2.2.0 0 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorType.2.0
# .1.3.6.1.4.1.4526.10.43.1.8.1.2.2.1 0 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorType.2.1
# .1.3.6.1.4.1.4526.10.43.1.8.1.2.2.2 0 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorType.2.2
# .1.3.6.1.4.1.4526.10.43.1.8.1.3.1.0 1 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorState.1.0
# .1.3.6.1.4.1.4526.10.43.1.8.1.3.1.1 1 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorState.1.1
# .1.3.6.1.4.1.4526.10.43.1.8.1.3.1.2 1 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorState.1.2
# .1.3.6.1.4.1.4526.10.43.1.8.1.3.2.0 1 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorState.2.0
# .1.3.6.1.4.1.4526.10.43.1.8.1.3.2.1 1 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorState.2.1
# .1.3.6.1.4.1.4526.10.43.1.8.1.3.2.2 1 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorState.2.2
# .1.3.6.1.4.1.4526.10.43.1.8.1.4.1.0 58 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorTemperature.1.0
# .1.3.6.1.4.1.4526.10.43.1.8.1.4.1.1 37 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorTemperature.1.1
# .1.3.6.1.4.1.4526.10.43.1.8.1.4.1.2 30 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorTemperature.1.2
# .1.3.6.1.4.1.4526.10.43.1.8.1.4.2.0 58 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorTemperature.2.0
# .1.3.6.1.4.1.4526.10.43.1.8.1.4.2.1 37 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorTemperature.2.1
# .1.3.6.1.4.1.4526.10.43.1.8.1.4.2.2 30 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorTemperature.2.2
# .1.3.6.1.4.1.4526.10.43.1.8.1.5.1.0 1 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorsEntry.5.1.0
# .1.3.6.1.4.1.4526.10.43.1.8.1.5.1.1 1 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorsEntry.5.1.1
# .1.3.6.1.4.1.4526.10.43.1.8.1.5.1.2 1 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorsEntry.5.1.2
# .1.3.6.1.4.1.4526.10.43.1.8.1.5.2.0 2 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorsEntry.5.2.0
# .1.3.6.1.4.1.4526.10.43.1.8.1.5.2.1 2 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorsEntry.5.2.1
# .1.3.6.1.4.1.4526.10.43.1.8.1.5.2.2 2 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorsEntry.5.2.2

# BUT (!!)
# .1.3.6.1.4.1.4526.10.43.1.8.1.2.1.0 0 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorType.1.0
# .1.3.6.1.4.1.4526.10.43.1.8.1.2.2.0 0 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorType.2.0
# .1.3.6.1.4.1.4526.10.43.1.8.1.3.1.0 1 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorState.1.0
# .1.3.6.1.4.1.4526.10.43.1.8.1.3.2.0 1 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorState.2.0
# .1.3.6.1.4.1.4526.10.43.1.8.1.4.1.0 1 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorTemperature.1.0
# .1.3.6.1.4.1.4526.10.43.1.8.1.4.2.0 1 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorTemperature.2.0
# .1.3.6.1.4.1.4526.10.43.1.8.1.5.1.0 35 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorsEntry.5.1.0
# .1.3.6.1.4.1.4526.10.43.1.8.1.5.2.0 37 --> FASTPATH-BOXSERVICES-PRIVATE-MIB::boxServicesTempSensorsEntry.5.2.0


@dataclass(frozen=True)
class TempSensor:
    type: str | None
    state: str
    reading: float


def parse_netgear_temp(string_table: Sequence[StringTable]) -> Mapping[str, TempSensor]:
    map_types = {
        "1": "fixed",
        "2": "removable",
    }

    versioninfo, sensorinfo = string_table
    parsed: dict[str, TempSensor] = {}
    for oid_end, sensor_ty, sstate, reading_str, reading_str_10 in sensorinfo:
        if versioninfo[0][0].startswith("10."):
            reading = float(reading_str_10)
        else:
            reading = float(reading_str)

        parsed.setdefault(
            f"Sensor {oid_end.replace('.', '/')}",
            TempSensor(
                type=map_types.get(sensor_ty),
                state=sstate,
                reading=reading,
            ),
        )
    return parsed


def discover_netgear_temp(section: Mapping[str, TempSensor]) -> DiscoveryResult:
    yield from (
        Service(item=sensorname)
        for sensorname, info in section.items()
        if info.state not in ("4", "5", "6")
    )


def check_netgear_temp(
    item: str, params: TempParamType, section: Mapping[str, TempSensor]
) -> CheckResult:
    map_states = {
        "1": (0, "normal"),
        "2": (1, "warning"),
        "3": (2, "critical"),
        "4": (1, "shutdown"),
        "5": (1, "not present"),
        "6": (1, "not operational"),
    }
    if data := section.get(item):
        if data.type:
            yield Result(state=State.OK, summary=f"Type: {data.type}")

        dev_status, dev_status_name = map_states[data.state]
        yield from check_temperature(
            data.reading,
            params,
            unique_name=f"netgear_temp.{item}",
            value_store=get_value_store(),
            dev_status=dev_status,
            dev_status_name=dev_status_name,
        )


snmp_section_netgear_temp = SNMPSection(
    name="netgear_temp",
    detect=DETECT_NETGEAR,
    fetch=[
        SNMPTree(
            base=".1.3.6.1.4.1.4526.10.1.1.1",
            oids=["13"],
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.4526.10.43.1.8.1",
            oids=[OIDEnd(), "2", "3", "4", "5"],
        ),
    ],
    parse_function=parse_netgear_temp,
)


check_plugin_netgear_temp = CheckPlugin(
    name="netgear_temp",
    service_name="Temperature %s",
    discovery_function=discover_netgear_temp,
    check_function=check_netgear_temp,
    check_ruleset_name="temperature",
    check_default_parameters={},
)
