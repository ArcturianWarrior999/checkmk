#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import uuid
from collections.abc import Mapping
from typing import Any, Final, Literal, NamedTuple

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


field_warning_messages: Final[dict[str, str]] = {
    "sqlnet_ora_group": "'sqlnet.ora permission group' has been skipped because it is not needed anymore by the unified plugin.",
    "validate_permissions": "'Oracle binaries permissions check' has been skipped because it is not needed by the unified plugin.",
    "xinetd_or_systemd": "'Host uses xinetd or systemd' has been skipped because it is not needed by the unified plugin.",
    "sqlnet_send_timeout": "'Sqlnet Send timeout' has been skipped because it is not supported by the unified plugin. Use Connection Timeout instead if this is applicable.",
    "excluded_sections": "'Exclude some sections on certain instances' cannot be mapped. The new rule format only supports disabling sections globally.",
    "remote_oracle_home": "'ORACLE_HOME to use for remote access' has been skipped because it is not needed by the unified plugin.",
    "tnsalias_pre_postfix": "'Add pre or postfix to TNSALIASes' has been skipped because it is not supported by the unified plugin.",
}

valid_sections: Final[frozenset[str]] = frozenset(
    {
        "instance",
        "asm_instance",
        "asm_diskgroup",
        "dataguard_stats",
        "locks",
        "logswitches",
        "longactivesessions",
        "performance",
        "processes",
        "recovery_area",
        "recovery_status",
        "sessions",
        "systemparameter",
        "undostat",
        "iostats",
        "jobs",
        "resumable",
        "rman",
        "tablespaces",
    }
)


def convert(legacy: Mapping[str, Any]) -> MigratedRule:
    warnings: list[str] = []
    instances: list[GuiInstanceConf[RawSecret]] = []

    deploy: tuple[Literal["deploy", "do_not_deploy"], None] = (
        ("deploy", None) if legacy.get("activated") else ("do_not_deploy", None)
    )

    cache_age = legacy.get("async_interval") or None

    sections = _convert_sections(legacy["sections"], warnings) if legacy.get("sections") else None

    auth = GuiAuthConf[RawSecret](auth_type=(OracleAuthType.WALLET, None))
    warnings.append("No auth defined in legacy rule. Defaulting to Oracle wallet.")

    main = GuiMainConf[RawSecret](
        auth=auth, connection=GuiConnectionConf(), cache_age=cache_age, sections=sections
    )

    warnings.extend(msg for key, msg in field_warning_messages.items() if key in legacy)

    return MigratedRule(
        rule=GuiConfig[RawSecret](deploy=deploy, instances=instances, main=main),
        warnings=warnings,
    )


def _convert_sections(
    sections: Mapping[str, Any], warnings: list[str]
) -> dict[str, Literal["synchronous", "asynchronous", "disabled"]]:
    """Rename ASM section keys, map sync/async settings, and warn on unsupported sections."""
    literal_mapping: dict[str, Literal["synchronous", "asynchronous"]] = {
        "sync": "synchronous",
        "async": "asynchronous",
    }
    sections_to_rename = {
        "asm:instance": "asm_instance",
        "asm:asm_diskgroup": "asm_diskgroup",
        "asm:processes": "processes",
    }

    new_sections: dict[str, Literal["synchronous", "asynchronous", "disabled"]] = {}
    for section, setting in sections.items():
        section = sections_to_rename.get(section, section)

        if section not in valid_sections:
            if section == "ts_quotas":
                message = (
                    "'TS quotas (not used)' has no corresponding check in either the legacy or "
                    "unified plugin, so no monitoring data would result from enabling "
                    "it — omitted."
                )
            else:
                message = f"Could not map section '{section}'."
            warnings.append(message)
            continue
        # None for the old plugin means disabled
        # but any other wrong values can also mean that too
        new_sections[section] = literal_mapping.get(setting, "disabled")

    return new_sections


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
