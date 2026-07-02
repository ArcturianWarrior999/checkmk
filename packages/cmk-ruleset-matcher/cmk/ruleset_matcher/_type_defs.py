#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

"""Local copies of a few foundational types/helpers.

Packages under ``packages/`` must not depend on ``cmk.utils``. The originals
still live in ``cmk.utils.servicename`` and ``cmk.utils.global_ident_type``;
these are plain (structural) aliases and a tiny helper, so keeping a local
copy here decouples the package without forcing a common foundational layer.
Since the types are structural (``str`` aliases /
identical ``TypedDict``) they interoperate freely with the ``cmk.utils`` ones.
"""

from typing import TypedDict

ServiceName = str
Item = str | None


class GlobalIdent(TypedDict):
    site_id: str
    program_id: str
    instance_id: str
