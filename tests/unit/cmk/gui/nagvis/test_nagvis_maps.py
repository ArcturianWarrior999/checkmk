#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import pytest

from cmk.gui.nagvis._nagvis_maps import _is_nagvis_url


@pytest.mark.parametrize(
    "url, expected",
    [
        # Relative "Edit" footnote link
        ("../nagvis/", True),
        ("../nagvis/index.php?mod=Map&act=view&show=Germany", True),
        # Site-absolute map links as returned by the NagVis getMaps API (CMK-36587)
        ("/prod/nagvis/index.php?mod=Map&act=view&show=Germany", True),
        # Non-NagVis URLs must be rejected
        ("/prod/check_mk/index.py", False),
        ("https://example.com/", False),
        ("../check_mk/", False),
    ],
)
def test_is_nagvis_url(url: str, expected: bool) -> None:
    assert _is_nagvis_url(url, "/prod/") is expected
