#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import http.client as http_client
import secrets
from collections.abc import Callable
from typing import override

from cmk.gui.http import request, response
from cmk.gui.oauth._models import (
    OAuthClientRegistrationRequest,
    OAuthClientRegistrationResponse,
)
from cmk.gui.pages import Page, PageContext, PageResult


class OAuthClientRegistrationPage(Page):
    """RFC 7591 dynamic client registration endpoint for this site.

    Accessed unauthenticated, referenced via the "registration_endpoint" field
    of the RFC 8414 authorization server metadata document. Returns 404 while
    no OAuth-consuming feature is enabled for the site (the enabled predicate
    is injected at registration).

    This is a stub: it does not validate or persist the submitted client
    metadata, it only hands out a random client_id. redirect_uris is echoed
    back from the request body -- see OAuthClientRegistrationResponse's
    docstring for why that's required, not optional polish.
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

        body = OAuthClientRegistrationRequest.model_validate(request.get_json(silent=True) or {})

        response.status_code = http_client.CREATED
        response.set_content_type("application/json")
        response.set_data(
            OAuthClientRegistrationResponse(
                client_id=secrets.token_urlsafe(32), redirect_uris=body.redirect_uris
            ).model_dump_json()
        )
        return None
