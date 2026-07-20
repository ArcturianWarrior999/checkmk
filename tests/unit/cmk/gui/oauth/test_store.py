#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from datetime import datetime, UTC

import pytest
from pydantic import ValidationError

from cmk.ccc import store
from cmk.gui.oauth import _store
from cmk.gui.oauth._store import (
    ClientId,
    ClientRegistration,
    get_registered_client,
    register_client,
)


def test_register_client_then_get_registered_client_returns_it() -> None:
    registered = register_client(["https://client.example/callback"], "Example")

    assert get_registered_client(registered.client_id) == registered


def test_two_registered_clients_are_both_retrievable() -> None:
    first = register_client(["https://client.example/first"], "First Client")
    second = register_client(["https://client.example/second"], "Second Client")

    assert get_registered_client(first.client_id) == first
    assert get_registered_client(second.client_id) == second
    assert first != second


def test_get_registered_client_returns_none_for_unknown_client_id() -> None:
    assert get_registered_client("does-not-exist") is None


def test_get_registered_client_raises_when_store_is_corrupt() -> None:
    _store.REGISTERED_CLIENTS_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _store.REGISTERED_CLIENTS_STORE_PATH.write_text("not valid json")

    with pytest.raises(ValidationError):
        get_registered_client("whatever")


def test_register_client_releases_lock_when_store_is_corrupt() -> None:
    _store.REGISTERED_CLIENTS_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _store.REGISTERED_CLIENTS_STORE_PATH.write_text("not valid json")

    with pytest.raises(ValidationError):
        register_client(["https://client.example/callback"], "Example")

    assert not store.have_lock(_store.REGISTERED_CLIENTS_STORE_PATH)


def _seed_store_with(n: int) -> None:
    clients = {
        ClientId(f"client-{i}"): ClientRegistration(
            client_id=ClientId(f"client-{i}"),
            redirect_uris=["https://client.example/callback"],
            client_name=None,
            registered_at=datetime.fromtimestamp(0, tz=UTC),
        )
        for i in range(n)
    }
    _store.REGISTERED_CLIENTS_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _store.REGISTERED_CLIENTS_STORE_PATH.write_text(_store._serialize_store(clients))


def test_register_client_raises_when_store_is_at_capacity() -> None:
    _seed_store_with(1000)

    with pytest.raises(_store.ClientRegistrationLimitExceededError):
        register_client(["https://client.example/callback"], "Example")


def test_register_client_releases_lock_when_store_is_at_capacity() -> None:
    _seed_store_with(1000)

    with pytest.raises(_store.ClientRegistrationLimitExceededError):
        register_client(["https://client.example/callback"], "Example")

    assert not store.have_lock(_store.REGISTERED_CLIENTS_STORE_PATH)


def test_register_client_does_not_add_entry_when_store_is_at_capacity() -> None:
    _seed_store_with(1000)

    with pytest.raises(_store.ClientRegistrationLimitExceededError):
        register_client(["https://client.example/callback"], "Example")

    raw = _store.REGISTERED_CLIENTS_STORE_PATH.read_text()
    assert len(_store._parse_store(raw)) == 1000


def test_register_client_succeeds_when_store_is_one_below_capacity() -> None:
    _seed_store_with(999)

    registered = register_client(["https://client.example/callback"], "Example")

    assert get_registered_client(registered.client_id) == registered
