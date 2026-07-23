#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


# Parse the snmp data from the IBM agent.
# must be cautius since a failed disk makes the snmp output
# shift and gives false info for "slot_id"


from cmk.agent_based.v2 import (
    all_of,
    any_of,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    equals,
    exists,
    Result,
    Service,
    SimpleSNMPSection,
    SNMPTree,
    State,
    StringTable,
)

Section = dict[str, tuple[int, str, str, str, str]]


def parse_ibm_xraid_pdisks(info: StringTable) -> Section:
    data: Section = {}
    for line in info:
        slot_id, disk_id, disk_type, disk_state, slot_desc = line
        if "slot" in slot_desc.lower():
            slot_id_int = int(slot_desc.split(", ")[-1][-1])
            enc_id = int(slot_desc.split(", ")[-2][-1])
            hba_id = int(slot_desc.split(", ")[-3][-1])
            disk_path = f"{hba_id}/{enc_id}/{slot_id_int}"
            data[disk_path] = (slot_id_int, disk_id, disk_type, disk_state, slot_desc)
    return data


def discover_ibm_xraid_pdisks(section: Section) -> DiscoveryResult:
    yield from (Service(item=disk_id) for disk_id in section)


def check_ibm_xraid_pdisks(item: str, section: Section) -> CheckResult:
    for disk_path, disk_entry in section.items():
        if disk_path == item:
            _slot_label, _disk_id, _disk_type, disk_state, slot_desc = disk_entry
            if disk_state == "3":
                yield Result(state=State.OK, summary=f"Disk is active [{slot_desc}]")
                return
            if disk_state == "4":
                yield Result(state=State.WARN, summary=f"Disk is rebuilding [{slot_desc}]")
                return
            if disk_state == "5":
                yield Result(state=State.CRIT, summary=f"Disk is dead [{slot_desc}]")
                return

    yield Result(state=State.CRIT, summary="disk is missing")


snmp_section_ibm_xraid_pdisks = SimpleSNMPSection(
    name="ibm_xraid_pdisks",
    detect=all_of(
        any_of(
            equals(".1.3.6.1.2.1.1.1.0", "software: windows"), equals(".1.3.6.1.2.1.1.1.0", "linux")
        ),
        exists(".1.3.6.1.4.1.795.14.1.100.1.0"),
    ),
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.795.14.1",
        oids=["503.1.1.4", "400.1.1.1", "400.1.1.5", "400.1.1.11", "400.1.1.12"],
    ),
    parse_function=parse_ibm_xraid_pdisks,
)


check_plugin_ibm_xraid_pdisks = CheckPlugin(
    name="ibm_xraid_pdisks",
    service_name="RAID PDisk %s",
    discovery_function=discover_ibm_xraid_pdisks,
    check_function=check_ibm_xraid_pdisks,
)
