#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
"""Migrate the removed ``user_sync`` site field to ``authentication_connections``
and ``user_attribute_sync_connections``.

Two constraints shape the mapping:

* Key absence now means "inherit from the central site" (typically ``"all"``),
  so legacy values that meant "no sync on this site" (``None``, ``"master"``
  on a remote) must become an explicit ``"disabled"`` — leaving the key out
  would silently turn the sync on.

* The new ``"all"`` shorthand for ``authentication_connections`` also enrolls
  SAML connections, which before the upgrade authenticated only on the central
  site. Remote sites therefore never get ``"all"`` (nor an absent key); they
  get the explicit list of LDAP connections existing at upgrade time. That
  freezes the list — LDAP connections added later no longer join remotes
  automatically — but that fails loud (the admin notices when enabling one),
  whereas enrolling SAML on remotes would fail silent.
  ``user_attribute_sync_connections`` is LDAP-only and unaffected, so it may
  keep ``"all"`` on remotes.

Only fields not yet set are filled in, so manually migrated sites keep their
configuration.
"""

from logging import Logger
from typing import Literal, override

from cmk.ccc.site import omd_site
from cmk.gui.config import active_config
from cmk.gui.userdb._connections import (
    is_ldap,
    ldap_authentication_entries_for_site,
    load_connection_config,
)
from cmk.gui.watolib.hosts_and_folders import make_folder_tree
from cmk.gui.watolib.sites import site_management_registry
from cmk.livestatus_client import AuthenticationConnectionEntry
from cmk.update_config.lib import ExpiryVersion
from cmk.update_config.registry import update_action_registry, UpdateAction
from cmk.utils.log import VERBOSE

AuthConnectionsValue = Literal["all"] | list[AuthenticationConnectionEntry]
AttrSyncConnectionsValue = Literal["all", "disabled"] | list[str]

# Distinguishes "key not on disk" from an explicit ``user_sync = None``
# (the legacy "Disable automatic user synchronization" choice).
_MISSING = object()


class MigrateUserSyncToAuthConnections(UpdateAction):
    @override
    def __call__(self, logger: Logger) -> None:
        site_mgmt = site_management_registry["site_management"]
        configured_sites = site_mgmt.load_sites()
        central_site_id = omd_site()

        # All configured LDAP connections, read from disk (independent of
        # whether `active_config.user_connections` is populated during
        # update-config). Remote sites freeze into an explicit list over
        # these — including currently disabled connections: a disabled
        # connection is inert at login time and joins again when re-enabled,
        # as it would have under the legacy bare-string forms.
        ldap_connections = {c["id"]: c for c in load_connection_config() if is_ldap(c)}

        migrated = False
        for site_id, site_spec in configured_sites.items():
            # `user_sync` was a required field on legacy `SiteConfiguration`
            # and the legacy valuespec always wrote it, so it is usually
            # present when we run. We `pop` here so the on-disk spec ends up
            # without the obsolete key regardless of whether the new fields
            # had already been set manually. The `_MISSING` sentinel keeps a
            # hand-edited spec without the key distinguishable from an
            # explicit `user_sync = None` ("sync disabled").
            user_sync = site_spec.pop("user_sync", _MISSING)  # type: ignore[typeddict-item]
            auth_value, attr_sync_value = _derive_new_values(
                user_sync,
                is_central_site=(site_id == central_site_id),
                frozen_ldap_entries=ldap_authentication_entries_for_site(
                    ldap_connections, site_spec
                ),
            )
            did_set = user_sync is not _MISSING
            if "authentication_connections" not in site_spec and auth_value is not None:
                site_spec["authentication_connections"] = auth_value
                did_set = True
            if "user_attribute_sync_connections" not in site_spec and attr_sync_value is not None:
                site_spec["user_attribute_sync_connections"] = attr_sync_value
                did_set = True

            if did_set:
                migrated = True
                logger.log(
                    VERBOSE,
                    "Migrated user_sync=%(user_sync)r on site %(site_id)r to "
                    "authentication_connections=%(authentication_connections)r, "
                    "user_attribute_sync_connections=%(user_attribute_sync_connections)r",
                    {
                        "user_sync": user_sync,
                        "site_id": str(site_id),
                        "authentication_connections": site_spec.get("authentication_connections"),
                        "user_attribute_sync_connections": site_spec.get(
                            "user_attribute_sync_connections"
                        ),
                    },
                )

        if migrated:
            site_mgmt.save_sites(
                make_folder_tree(active_config),
                configured_sites,
                activate=False,
                pprint_value=active_config.wato_pprint_config,
                liveproxyd_enabled=active_config.liveproxyd_enabled,
                use_git=active_config.wato_use_git,
                acting_user_id=None,
            )


def _derive_new_values(
    user_sync: object,
    *,
    is_central_site: bool,
    frozen_ldap_entries: list[AuthenticationConnectionEntry],
) -> tuple[AuthConnectionsValue | None, AttrSyncConnectionsValue | None]:
    """Map a ``user_sync`` value to the new fields.

    ``None`` for a field means "leave the key absent on disk" so the runtime
    inherits the central site's value — callers must skip the assignment.
    See the module docstring for why remotes get ``frozen_ldap_entries``
    instead of ``"all"`` and why "no sync" maps to an explicit ``"disabled"``.
    """
    if user_sync == "all":
        return ("all", "all") if is_central_site else (frozen_ldap_entries, "all")
    if user_sync == "master":
        return ("all", "all") if is_central_site else (frozen_ldap_entries, "disabled")
    if isinstance(user_sync, tuple) and user_sync[0] == "list":
        conn_ids: list[str] = list(user_sync[1])
        auth_entries: list[AuthenticationConnectionEntry] = [
            ("ldap", conn_id) for conn_id in conn_ids
        ]
        return auth_entries, conn_ids
    if user_sync is None:
        return (None, "disabled") if is_central_site else (frozen_ldap_entries, "disabled")
    return None, None


update_action_registry.register(
    MigrateUserSyncToAuthConnections(
        name="migrate_user_sync_to_auth_connections",
        title="Migrate site user_sync to authentication_connections",
        # Run after `clean_up_site_attributes` (sort_index=30), which
        # `setdefault`s `user_sync = "all"` for legacy sites that lacked it.
        sort_index=35,
        expiry_version=ExpiryVersion.CMK_310,
    )
)
