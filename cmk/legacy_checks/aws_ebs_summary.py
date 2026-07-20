#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# mypy: disable-error-code="type-arg"


from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from cmk.agent_based.legacy.v0_unstable import (
    LegacyCheckDefinition,
    LegacyCheckResult,
    LegacyDiscoveryResult,
)
from cmk.agent_based.v2 import StringTable
from cmk.plugins.aws.lib import parse_aws

check_info = {}


@dataclass(frozen=True)
class EbsStatusDetail:
    name: str
    status: str


@dataclass(frozen=True)
class EbsVolumeStatus:
    status: str
    details: Sequence[EbsStatusDetail]


@dataclass(frozen=True)
class EbsSummaryVolume:
    volume_id: str
    volume_type: str
    state: str
    encrypted: bool | None = None
    create_time: str | None = None
    volume_status: EbsVolumeStatus | None = None


AWSEBSStorageTypes = {
    "standard": "Magnetic volumes",
    "gp2": "General Purpose SSD (gp2)",
    "gp3": "General Purpose SSD (gp3)",
    "io1": "Provisioned IOPS SSD (io1)",
    "io2": "Provisioned IOPS SSD (io2)",
    "st1": "Throughput Optimized HDD",
    "sc1": "Cold HDD",
}


def parse_aws_summary(string_table: StringTable) -> Mapping[str, EbsSummaryVolume]:
    parsed: dict[str, EbsSummaryVolume] = {}
    for row in parse_aws(string_table):
        if (vid := row["VolumeId"]) in parsed:
            continue
        volume_status = None
        if (raw_status := row.get("VolumeStatus")) is not None:
            volume_status = EbsVolumeStatus(
                status=raw_status["Status"],
                details=[
                    EbsStatusDetail(name=detail["Name"], status=detail["Status"])
                    for detail in raw_status.get("Details", [])
                ],
            )
        parsed[vid] = EbsSummaryVolume(
            volume_id=vid,
            volume_type=row["VolumeType"],
            state=row["State"],
            encrypted=row.get("Encrypted"),
            create_time=row.get("CreateTime"),
            volume_status=volume_status,
        )
    return parsed


#   .--summary-------------------------------------------------------------.
#   |                                                                      |
#   |           ___ _   _ _ __ ___  _ __ ___   __ _ _ __ _   _             |
#   |          / __| | | | '_ ` _ \| '_ ` _ \ / _` | '__| | | |            |
#   |          \__ \ |_| | | | | | | | | | | | (_| | |  | |_| |            |
#   |          |___/\__,_|_| |_| |_|_| |_| |_|\__,_|_|   \__, |            |
#   |                                                    |___/             |
#   '----------------------------------------------------------------------'


def discover_aws_ebs_summary(
    section: Mapping[str, EbsSummaryVolume],
) -> Iterable[tuple[None, dict]]:
    if section:
        yield None, {}


def check_aws_ebs_summary(
    item: None, params: Mapping[str, Any], parsed: Mapping[str, EbsSummaryVolume]
) -> LegacyCheckResult:
    stores_by_state: dict[str, list[str]] = {}
    stores_by_type: dict[str, list[str]] = {}
    long_output = []
    for volume_id, row in parsed.items():
        stores_by_state.setdefault(row.state, []).append(volume_id)
        stores_by_type.setdefault(row.volume_type, []).append(volume_id)
        long_output.append(
            f"Volume: {volume_id}, Status: {row.state}, Type: {row.volume_type}, Encrypted: {row.encrypted}, Creation time: {row.create_time}"
        )

    yield 0, "Stores: %s" % len(parsed)
    for state, stores in stores_by_state.items():
        yield 0, f"{state}: {len(stores)}"
    for type_, stores in stores_by_type.items():
        yield 0, "{}: {}".format(AWSEBSStorageTypes.get(type_, "unknown[%s]" % type_), len(stores))
    if long_output:
        yield 0, "\n%s" % "\n".join(long_output)


check_info["aws_ebs_summary"] = LegacyCheckDefinition(
    name="aws_ebs_summary",
    parse_function=parse_aws_summary,
    service_name="AWS/EBS Summary",
    discovery_function=discover_aws_ebs_summary,
    check_function=check_aws_ebs_summary,
)

# .
#   .--health--------------------------------------------------------------.
#   |                    _                _ _   _                          |
#   |                   | |__   ___  __ _| | |_| |__                       |
#   |                   | '_ \ / _ \/ _` | | __| '_ \                      |
#   |                   | | | |  __/ (_| | | |_| | | |                     |
#   |                   |_| |_|\___|\__,_|_|\__|_| |_|                     |
#   |                                                                      |
#   '----------------------------------------------------------------------'


def check_aws_ebs_summary_health(
    item: str, params: Mapping[str, Any], parsed: Mapping[str, EbsSummaryVolume]
) -> LegacyCheckResult:
    if (ebs_data := parsed.get(item)) is None:
        return
    if (volume_status := ebs_data.volume_status) is None:
        return
    ebs_status = volume_status.status
    yield 0 if ebs_status.lower() == "ok" else 2, "Status: %s" % ebs_status
    for detail in volume_status.details:
        yield 0, f"{detail.name}: {detail.status}"


def discover_aws_ebs_summary_health(
    section: Mapping[str, EbsSummaryVolume],
) -> LegacyDiscoveryResult:
    for volume_id, volume in section.items():
        if volume.volume_status is not None:
            yield volume_id, {}


check_info["aws_ebs_summary.health"] = LegacyCheckDefinition(
    name="aws_ebs_summary_health",
    service_name="AWS/EBS Health %s",
    sections=["aws_ebs_summary"],
    discovery_function=discover_aws_ebs_summary_health,
    check_function=check_aws_ebs_summary_health,
)
