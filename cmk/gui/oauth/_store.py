#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import secrets
from datetime import datetime, UTC
from typing import NewType

from pydantic import BaseModel, TypeAdapter

import cmk.utils.paths
from cmk.ccc import store

REGISTERED_CLIENTS_STORE_PATH = cmk.utils.paths.var_dir / "oauth" / "registered_clients.json"
_MAX_REGISTERED_CLIENTS = 1000

ClientId = NewType("ClientId", str)


class ClientRegistrationLimitExceededError(Exception):
    pass


class ClientRegistration(BaseModel):
    """A dynamically registered OAuth client, as persisted to disk."""

    client_id: ClientId
    redirect_uris: list[str]
    client_name: str | None
    registered_at: datetime


_ClientsAdapter = TypeAdapter(dict[ClientId, ClientRegistration])


def _parse_store(raw: str) -> dict[ClientId, ClientRegistration]:
    if not raw:
        return {}
    return _ClientsAdapter.validate_json(raw)


def _serialize_store(clients: dict[ClientId, ClientRegistration]) -> str:
    return _ClientsAdapter.dump_json(clients).decode("utf-8")


def register_client(redirect_uris: list[str], client_name: str | None) -> ClientRegistration:
    raw = store.load_text_from_file(REGISTERED_CLIENTS_STORE_PATH, lock=True)
    try:
        clients = _parse_store(raw)
    except Exception:
        store.release_lock(REGISTERED_CLIENTS_STORE_PATH)
        raise

    if len(clients) >= _MAX_REGISTERED_CLIENTS:
        store.release_lock(REGISTERED_CLIENTS_STORE_PATH)
        raise ClientRegistrationLimitExceededError

    registration = ClientRegistration(
        client_id=ClientId(secrets.token_urlsafe(32)),
        redirect_uris=redirect_uris,
        client_name=client_name,
        registered_at=datetime.now(UTC),
    )
    clients[registration.client_id] = registration
    store.save_text_to_file(REGISTERED_CLIENTS_STORE_PATH, _serialize_store(clients))
    return registration


def get_registered_client(client_id: str) -> ClientRegistration | None:
    raw = store.load_text_from_file(REGISTERED_CLIENTS_STORE_PATH)
    return _parse_store(raw).get(ClientId(client_id))
