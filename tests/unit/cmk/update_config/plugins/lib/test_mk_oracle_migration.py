#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.update_config.plugins.lib.mk_oracle_migration import convert, dump


def test_empty_body_is_not_deployed() -> None:
    assert dump(convert({}).rule)["deploy"] == ("do_not_deploy", None)


def test_empty_body_auth_is_wallet() -> None:
    assert dump(convert({}).rule)["main"]["auth"] == {"auth_type": ("wallet", None)}


def test_empty_body_has_no_instances() -> None:
    assert dump(convert({}).rule)["instances"] == []


def test_empty_body_has_warning() -> None:
    assert convert({}).warnings == ["No auth defined in legacy rule. Defaulting to Oracle wallet."]


def test_deploy_when_activated_true() -> None:
    assert dump(convert({"activated": True}).rule)["deploy"] == ("deploy", None)


def test_do_not_deploy_when_activated_false() -> None:
    assert dump(convert({"activated": False}).rule)["deploy"] == ("do_not_deploy", None)


def test_async_interval_cache_age() -> None:
    assert dump(convert({"async_interval": 600}).rule)["main"]["cache_age"] == 600


def test_sections_supported_keys_are_mapped() -> None:
    new_rule = convert({"sections": {"instance": "sync"}})

    assert new_rule.warnings == ["No auth defined in legacy rule. Defaulting to Oracle wallet."]
    assert dump(new_rule.rule)["main"]["sections"] == {"instance": "synchronous"}


def test_sections_unsupported_keys_are_skipped_with_warning() -> None:
    new_rule = convert({"sections": {"special_section": "sync"}})

    assert new_rule.warnings == [
        "Could not map section 'special_section'.",
        "No auth defined in legacy rule. Defaulting to Oracle wallet.",
    ]
    assert dump(new_rule.rule)["main"]["sections"] == {}


def test_sections_sync_becomes_synchronous() -> None:
    assert dump(convert({"sections": {"instance": "sync"}}).rule)["main"]["sections"] == {
        "instance": "synchronous"
    }


def test_sections_async_becomes_asynchronous() -> None:
    assert dump(convert({"sections": {"tablespaces": "async"}}).rule)["main"]["sections"] == {
        "tablespaces": "asynchronous"
    }


def test_sections_none_becomes_disabled() -> None:
    assert dump(convert({"sections": {"iostats": None}}).rule)["main"]["sections"] == {
        "iostats": "disabled"
    }


def test_sections_unsupported_value_becomes_disabled() -> None:
    assert dump(convert({"sections": {"iostats": "bad"}}).rule)["main"]["sections"] == {
        "iostats": "disabled"
    }


def test_sections_asm_sections_are_renamed() -> None:
    new_rule = convert(
        {
            "sections": {
                "asm:instance": "sync",
                "asm:asm_diskgroup": "async",
                "asm:processes": "sync",
            }
        }
    )
    assert dump(new_rule.rule)["main"]["sections"] == {
        "asm_instance": "synchronous",
        "asm_diskgroup": "asynchronous",
        "processes": "synchronous",
    }


def test_unmappable_fields_ignored() -> None:
    new_rule = convert(
        {
            "sqlnet_ora_group": "some_group",
            "validate_permissions": ("enable", {}),
            "xinetd_or_systemd": ("xinetd", None),
            "sqlnet_send_timeout": 30,
            "excluded_sections": [("s", ["x"])],
            "tnsalias_pre_postfix": ("all_sids", ("a", "b")),
            "remote_oracle_home": "/x",
        }
    )
    assert (
        "'sqlnet.ora permission group' has been skipped because it is not needed anymore by the unified plugin."
        in new_rule.warnings
    )
    assert (
        "'Oracle binaries permissions check' has been skipped because it is not needed by the unified plugin."
        in new_rule.warnings
    )
    assert (
        "'Host uses xinetd or systemd' has been skipped because it is not needed by the unified plugin."
        in new_rule.warnings
    )
    assert (
        "'Sqlnet Send timeout' has been skipped because it is not supported by the unified plugin. Use Connection Timeout instead if this is applicable."
        in new_rule.warnings
    )
    assert (
        "'Exclude some sections on certain instances' cannot be mapped. The new rule format only supports disabling sections globally."
        in new_rule.warnings
    )
    assert dump(new_rule.rule) == {
        "deploy": ("do_not_deploy", None),
        "main": {"auth": {"auth_type": ("wallet", None)}, "connection": {}},
        "instances": [],
    }


def test_discovery_not_mapped_when_nothing_defined() -> None:
    assert "discovery" not in dump(convert({"sids": None}).rule)["main"]


def test_discovery_include_mapped_when_sids_defined() -> None:
    assert dump(convert({"sids": ("only", ["a", "b"])}).rule)["main"]["discovery"] == {
        "enabled": True,
        "include": ["a", "b"],
    }


def test_discovery_exclude_mapped_when_skip_defined() -> None:
    assert dump(convert({"sids": ("skip", ["a"])}).rule)["main"]["discovery"] == {
        "enabled": True,
        "exclude": ["a"],
    }


def test_discovery_include_mapped_when_exclude_defined() -> None:
    assert dump(convert({"sids": ("exclude", ["a"])}).rule)["main"]["discovery"] == {
        "enabled": True,
        "exclude": ["a"],
    }
