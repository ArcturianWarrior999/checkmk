#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
"""Tests for the ``user_sync`` → ``authentication_connections`` /
``user_attribute_sync_connections`` migration."""

from livestatus import AuthenticationConnectionEntry

from cmk.update_config.plugins.actions.migrate_user_sync_to_auth_connections import (
    _derive_new_values,
)

_FROZEN: list[AuthenticationConnectionEntry] = [("ldap", "ldap_a"), ("ldap", "ldap_b")]


def test_legacy_all_on_central_migrates_to_all_shorthand() -> None:
    """Legacy ``"all"`` implied "every LDAP connection, including ones added
    later". On the central site the new ``"all"`` shorthand preserves that
    (SAML already authenticated there before the upgrade), so both new fields
    become ``"all"`` and the site keeps creating users after upgrade."""
    auth, attr = _derive_new_values("all", is_central_site=True, frozen_ldap_entries=_FROZEN)
    assert auth == "all"
    assert attr == "all"


def test_legacy_all_on_remote_freezes_ldap_authentication() -> None:
    """On a remote site the new ``"all"`` shorthand would also enroll every
    SAML connection, which never authenticated on remotes before the upgrade.
    Authentication is frozen to the LDAP entries existing at upgrade time;
    the attribute sync keeps ``"all"`` — its value space is LDAP-only, so the
    legacy auto-join semantics carry over unchanged."""
    auth, attr = _derive_new_values("all", is_central_site=False, frozen_ldap_entries=_FROZEN)
    assert auth == _FROZEN
    assert attr == "all"


def test_legacy_master_on_central_migrates_to_all_shorthand() -> None:
    auth, attr = _derive_new_values("master", is_central_site=True, frozen_ldap_entries=_FROZEN)
    assert auth == "all"
    assert attr == "all"


def test_legacy_master_on_remote_freezes_auth_and_leaves_attr_sync_unset() -> None:
    """``"master"`` on a remote = the central syncs, the remote does not; the
    attribute sync key is left unset (inherit from central). Authentication
    is frozen to the LDAP entries existing at upgrade time — an absent key
    would inherit the central's ``"all"`` and thereby enroll SAML
    connections."""
    auth, attr = _derive_new_values("master", is_central_site=False, frozen_ldap_entries=_FROZEN)
    assert auth == _FROZEN
    assert attr is None


def test_legacy_list_migrates_to_plain_lists() -> None:
    """The explicit ``("list", [conn_ids])`` legacy form becomes a plain
    list of LDAP entries for auth and a plain list of connection IDs for
    attribute sync — no tuple wrappers, and the frozen entries are not
    consulted."""
    auth, attr = _derive_new_values(
        ("list", ["ldap_a", "ldap_b"]), is_central_site=False, frozen_ldap_entries=[]
    )
    assert auth == [("ldap", "ldap_a"), ("ldap", "ldap_b")]
    assert attr == ["ldap_a", "ldap_b"]


def test_no_ldap_connections_freezes_to_empty_list_on_remote() -> None:
    """With no LDAP connections at upgrade time a remote gets an explicit
    empty list — key absence would inherit the central's ``"all"`` and
    enroll SAML connections."""
    auth, attr = _derive_new_values("all", is_central_site=False, frozen_ldap_entries=[])
    assert auth == []
    assert attr == "all"


def test_unknown_user_sync_value_leaves_both_unset() -> None:
    auth, attr = _derive_new_values(None, is_central_site=False, frozen_ldap_entries=_FROZEN)
    assert auth is None
    assert attr is None
