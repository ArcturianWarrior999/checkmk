#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Service,
)
from cmk.plugins.aws.lib import check_aws_elb_summary_generic, GenericAWSSection, parse_aws


def discover_aws_elb_summary(section: GenericAWSSection) -> DiscoveryResult:
    if section:
        yield Service()


def check_aws_elb_summary(section: GenericAWSSection) -> CheckResult:
    yield from check_aws_elb_summary_generic(section)


agent_section_aws_elb_summary = AgentSection(
    name="aws_elb_summary",
    parse_function=parse_aws,
)


check_plugin_aws_elb_summary = CheckPlugin(
    name="aws_elb_summary",
    service_name="AWS/ELB Summary",
    discovery_function=discover_aws_elb_summary,
    check_function=check_aws_elb_summary,
)
