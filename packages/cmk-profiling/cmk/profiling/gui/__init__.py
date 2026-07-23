#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

"""GUI profiling: profile storage, flamegraph rendering, and WATO pages."""

from cmk.gui.pages import PageRegistry
from cmk.gui.watolib.mode import ModeRegistry

from ._store import ProfileStore
from .pages import register as _register_pages

__all__ = ["ProfileStore", "register"]


def register(
    page_registry: PageRegistry,
    mode_registry: ModeRegistry,
) -> None:
    _register_pages(page_registry, mode_registry)
