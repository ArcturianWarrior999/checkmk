#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import uuid
from collections.abc import Mapping
from typing import Any, Literal, NamedTuple

from cmk.gui.watolib.rulesets import Rule, RuleOptions, Ruleset
from cmk.plugins.oracle.bakery.mk_oracle_unified import (
    GuiAuthConf,
    GuiConfig,
    GuiConnectionConf,
    GuiInstanceConf,
    GuiMainConf,
    OracleAuthType,
)

MIGRATION_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "checkmk.com/oracle-migration")

RawSecret = tuple[
    Literal["cmk_postprocessed"],
    Literal["explicit_password", "stored_password"],
    tuple[str, str],
]


class MigratedRule(NamedTuple):
    rule: GuiConfig[RawSecret]
    warnings: list[str]


class MigrationResult(NamedTuple):
    legacy_rule: Rule
    new_rule: Rule
    warnings: list[str]


def convert(legacy: Mapping[str, Any]) -> MigratedRule:
    warnings: list[str] = []
    instances: list[GuiInstanceConf[RawSecret]] = []

    deploy: tuple[Literal["deploy", "do_not_deploy"], None] = (
        ("deploy", None) if legacy.get("activated") else ("do_not_deploy", None)
    )

    cache_age = legacy.get("async_interval") or None

    auth = GuiAuthConf[RawSecret](auth_type=(OracleAuthType.WALLET, None))
    warnings.append("No auth defined in legacy rule. Defaulting to Oracle wallet.")

    main = GuiMainConf[RawSecret](auth=auth, connection=GuiConnectionConf(), cache_age=cache_age)

    return MigratedRule(
        rule=GuiConfig[RawSecret](deploy=deploy, instances=instances, main=main),
        warnings=warnings,
    )


def dump(config: GuiConfig[RawSecret]) -> dict[str, Any]:
    return config.model_dump(exclude_unset=True, exclude_none=True, mode="python")


def migrate_ruleset(
    legacy_ruleset: Ruleset, unified_ruleset: Ruleset, *, disabled: bool
) -> tuple[list[MigrationResult], int]:
    existing_ids = {rule.id for _, _, rule in unified_ruleset.get_rules()}

    results: list[MigrationResult] = []
    skipped = 0
    for folder, _index, rule in legacy_ruleset.get_rules():
        new_id = str(uuid.uuid5(MIGRATION_NAMESPACE, rule.id))
        if new_id in existing_ids:
            skipped += 1
            continue

        migrated = convert(rule.value)

        new_rule = Rule(
            id_=new_id,
            folder=folder,
            ruleset=unified_ruleset,
            conditions=rule.conditions.clone(),
            options=RuleOptions(
                disabled=disabled,
                description=f"(Migrated) {rule.description()}"
                if rule.description()
                else "(Migrated)",
                comment=rule.rule_options.comment,
                docu_url="",
                predefined_condition_id=rule.rule_options.predefined_condition_id,
            ),
            value=dump(migrated.rule),
        )
        results.append(
            MigrationResult(
                legacy_rule=rule,
                new_rule=new_rule,
                warnings=migrated.warnings,
            )
        )

    return results, skipped
