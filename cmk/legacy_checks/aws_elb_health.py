#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# mypy: disable-error-code="no-untyped-def"


from dataclasses import dataclass

from cmk.agent_based.legacy.v0_unstable import LegacyCheckDefinition
from cmk.agent_based.v2 import StringTable
from cmk.plugins.aws.lib import parse_aws

check_info = {}

AWSELBHealthMap = {
    "InService": "in service",
    "OutOfService": "out of service",
    "Unknown": "unknown",
}


@dataclass(frozen=True)
class ElbHealth:
    state: str
    instance_id: str
    reason_code: str | None = None
    description: str | None = None


def parse_aws_elb_health(string_table: StringTable) -> ElbHealth | None:
    try:
        row = parse_aws(string_table)[-1]
    except IndexError:
        return None
    return ElbHealth(
        state=row["State"],
        instance_id=row["InstanceId"],
        reason_code=row.get("ReasonCode"),
        description=row.get("Description"),
    )


def discover_aws_elb_health(section: ElbHealth | None):
    if section is not None:
        yield None, {}


def check_aws_elb_health(item, params, parsed: ElbHealth):
    state_readable = AWSELBHealthMap[parsed.state]
    if state_readable == "in service":
        state = 0
    elif state_readable == "out of service":
        state = 1
    else:
        state = 3
    yield state, "Status: %s" % state_readable
    yield 0, "Instance: %s" % parsed.instance_id

    reason_code = parsed.reason_code
    if reason_code not in [None, "", "N/A"]:
        yield 0, "Reason: %s" % reason_code

    description = parsed.description
    if description not in [None, "", "N/A"]:
        yield 0, "Description: %s" % description


check_info["aws_elb_health"] = LegacyCheckDefinition(
    name="aws_elb_health",
    parse_function=parse_aws_elb_health,
    service_name="AWS/ELB Health ",
    discovery_function=discover_aws_elb_health,
    check_function=check_aws_elb_health,
)
