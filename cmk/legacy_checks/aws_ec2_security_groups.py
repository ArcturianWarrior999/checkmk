#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# mypy: disable-error-code="no-untyped-def"


from collections.abc import Sequence
from dataclasses import dataclass

from cmk.agent_based.legacy.v0_unstable import LegacyCheckDefinition
from cmk.agent_based.v2 import StringTable
from cmk.plugins.aws.lib import parse_aws

check_info = {}


@dataclass(frozen=True)
class Ec2SecurityGroup:
    group_id: str
    group_name: str
    description: str | None = None


def parse_aws_ec2_security_groups(string_table: StringTable) -> Sequence[Ec2SecurityGroup]:
    return [
        Ec2SecurityGroup(
            group_id=group["GroupId"],
            group_name=group["GroupName"],
            description=group.get("Description"),
        )
        for group in parse_aws(string_table)
    ]


def discover_aws_ec2_security_groups(parsed: Sequence[Ec2SecurityGroup]):
    if parsed:
        yield None, {"groups": [group.group_id for group in parsed]}


def check_aws_ec2_security_groups(item, params, parsed: Sequence[Ec2SecurityGroup]):
    for group in parsed:
        state = 0
        descr = group.description
        if descr:
            prefix = "[%s] " % descr
        else:
            prefix = ""
        infotext = f"{prefix}{group.group_name}: {group.group_id}"
        if group.group_id not in params["groups"]:
            infotext += " (has changed)"
            state = 2
        yield state, infotext


check_info["aws_ec2_security_groups"] = LegacyCheckDefinition(
    name="aws_ec2_security_groups",
    parse_function=parse_aws_ec2_security_groups,
    service_name="AWS/EC2 Security Groups",
    discovery_function=discover_aws_ec2_security_groups,
    check_function=check_aws_ec2_security_groups,
    check_default_parameters={},
)
