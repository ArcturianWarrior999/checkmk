#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from collections.abc import Mapping
from typing import Any

from cmk.agent_based.v1 import check_levels as check_levels_v1
from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
    render,
    Result,
    Service,
    State,
    StringTable,
)
from cmk.plugins.aws.lib import parse_aws

Section = Mapping[str, Mapping[str, Any]]


def parse_aws_glacier(string_table: StringTable) -> Section:
    return {vault["VaultName"]: vault for vault in parse_aws(string_table)}


def discover_aws_glacier(section: Section) -> DiscoveryResult:
    for vault_name in section:
        yield Service(item=vault_name)


def check_aws_glacier_archives(
    item: str, params: Mapping[str, Any], section: Section
) -> CheckResult:
    if not (data := section.get(item)):
        return

    vault_size = data.get("SizeInBytes", 0)
    yield from check_levels_v1(
        vault_size,
        metric_name="aws_glacier_vault_size",
        levels_upper=params.get("vault_size_levels", (None, None)),
        render_func=render.disksize,
        label="Vault size",
    )

    num_archives = data.get("NumberOfArchives", 0)
    yield Result(state=State.OK, summary=f"Number of archives: {int(num_archives)}")
    yield Metric("aws_glacier_num_archives", num_archives)

    tag_infos = [f"{key}: {value}" for key, value in data.get("Tagging", {}).items()]
    if tag_infos:
        yield Result(state=State.OK, summary=f"[Tags]: {', '.join(tag_infos)}")


agent_section_aws_glacier = AgentSection(
    name="aws_glacier",
    parse_function=parse_aws_glacier,
)


check_plugin_aws_glacier = CheckPlugin(
    name="aws_glacier",
    service_name="AWS/Glacier Vault: %s",
    discovery_function=discover_aws_glacier,
    check_function=check_aws_glacier_archives,
    check_ruleset_name="aws_glacier_vault_archives",
    check_default_parameters={},
)


def discover_aws_glacier_summary(section: Section) -> DiscoveryResult:
    if section:
        yield Service()


def check_aws_glacier_summary(params: Mapping[str, Any], section: Section) -> CheckResult:
    sum_size = 0
    largest_vault = None
    largest_vault_size = 0
    for vault_name in sorted(section):
        vault_size = section[vault_name].get("SizeInBytes", 0)
        sum_size += vault_size
        if vault_size >= largest_vault_size:
            largest_vault = vault_name
            largest_vault_size = vault_size
    yield from check_levels_v1(
        sum_size,
        metric_name="aws_glacier_total_vault_size",
        levels_upper=params.get("vault_size_levels", (None, None)),
        render_func=render.disksize,
        label="Total size",
    )

    if largest_vault:
        yield Result(
            state=State.OK,
            summary=f"Largest vault: {largest_vault} ({render.disksize(largest_vault_size)})",
        )
        yield Metric("aws_glacier_largest_vault_size", largest_vault_size)


check_plugin_aws_glacier_summary = CheckPlugin(
    name="aws_glacier_summary",
    service_name="AWS/Glacier Summary",
    sections=["aws_glacier"],
    discovery_function=discover_aws_glacier_summary,
    check_function=check_aws_glacier_summary,
    check_ruleset_name="aws_glacier_vaults",
    check_default_parameters={},
)
