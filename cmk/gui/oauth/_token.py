#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import http.client as http_client
import secrets
from collections.abc import Callable
from typing import override

from cmk.gui.http import request, response
from cmk.gui.oauth._models import OAuthTokenResponse
from cmk.gui.pages import Page, PageContext, PageResult


class OAuthTokenPage(Page):
    """RFC 6749 section 3.2 token endpoint for this site.

    Accessed unauthenticated, referenced via the "token_endpoint" field of the
    RFC 8414 authorization server metadata document. Returns 404 while no
    OAuth-consuming feature is enabled for the site (the enabled predicate is
    injected at registration).

    This is a stub: it does not validate the grant (authorization code,
    client credentials, ...) or the client at all, it only hands out a
    random access token.
    """

    def __init__(self, enabled: Callable[[], bool]) -> None:
        self._enabled = enabled

    @override
    def page(self, ctx: PageContext) -> PageResult:
        if not self._enabled():
            response.status_code = http_client.NOT_FOUND
            return None

        if request.request_method != "POST":
            response.status_code = http_client.METHOD_NOT_ALLOWED
            return None

        response.set_content_type("application/json")
        response.set_data(
            OAuthTokenResponse(access_token=secrets.token_urlsafe(32)).model_dump_json()
        )
        return None
