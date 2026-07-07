#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import pytest

from cmk.plugins.checkmk.rulesets.super_server_solaris import migrate


@pytest.mark.parametrize("value", ["inetd", "no_service"])
def test_migrate_old_string_to_dict(value: str) -> None:
    assert migrate(value) == {"deployment": value}


@pytest.mark.parametrize("value", ["inetd", "no_service"])
def test_migrate_new_dict_passes_through(value: str) -> None:
    assert migrate({"deployment": value}) == {"deployment": value}


def test_migrate_unexpected_raises() -> None:
    with pytest.raises(ValueError, match="Unexpected value"):
        migrate(True)
