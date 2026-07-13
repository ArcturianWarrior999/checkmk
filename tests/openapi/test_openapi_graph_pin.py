#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.ccc.user import UserId
from cmk.gui.graphing._graph_pin_store import GRAPH_PIN_USER_FILE
from cmk.gui.logged_in import load_user_file
from tests.testlib.rest_api_client import ClientRegistry


def _stored_pin(user_id: UserId) -> object:
    return load_user_file(GRAPH_PIN_USER_FILE, user_id, None, lock=False)


def test_set_graph_pin_persists_the_timestamp(
    clients: ClientRegistry, with_automation_user: tuple[UserId, str]
) -> None:
    clients.Graph.set_pin(1700000000)

    assert _stored_pin(with_automation_user[0]) == 1700000000


def test_set_graph_pin_removes_the_pin_when_null(
    clients: ClientRegistry, with_automation_user: tuple[UserId, str]
) -> None:
    clients.Graph.set_pin(1700000000)

    clients.Graph.set_pin(None)

    assert _stored_pin(with_automation_user[0]) is None
