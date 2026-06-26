#!/usr/bin/env python3
# Copyright (C) 2022 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from flask import make_response, Response


def render_string_template(template_string: str, **kwargs: str) -> Response:
    """Renders a text formatted with Python's `string.format`"""
    return make_response(template_string.format(**kwargs))
