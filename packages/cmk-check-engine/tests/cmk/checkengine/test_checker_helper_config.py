#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from pathlib import Path

import pytest

from cmk.checkengine.checker_helper_config import PackedConfigStore


class TestPackedConfigStore:
    @pytest.fixture()
    def store(self, tmp_path: Path) -> PackedConfigStore:
        return PackedConfigStore.from_serial(tmp_path)

    def test_read_not_existing_file(self, store: PackedConfigStore) -> None:
        with pytest.raises(FileNotFoundError):
            store.read()

    def test_write(self, store: PackedConfigStore, tmp_path: Path) -> None:
        precompiled_check_config = tmp_path / "precompiled_check_config.mk"
        assert not precompiled_check_config.exists()

        store.write({"abc": 1})

        assert precompiled_check_config.exists()
        assert store.read() == {"abc": 1}
