#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import http.client as http_client
import re
import secrets
from collections.abc import Callable
from typing import Literal, override

from cmk.gui.http import request, response
from cmk.gui.oauth._models import OAuthTokenErrorResponse, OAuthTokenResponse
from cmk.gui.pages import Page, PageContext, PageResult

_FORM_CONTENT_TYPE = "application/x-www-form-urlencoded"

# The parameters this endpoint interprets. RFC 6749 section 3.2 forbids
# repeating request parameters, but it also requires unrecognized ones to be
# ignored, so the duplicate check deliberately covers only this set. Extend
# it before reading further parameters (redirect_uri, resource).
_KNOWN_PARAMS = ("grant_type", "code", "client_id", "code_verifier")

# RFC 7636 section 4.1: 43 to 128 characters from the unreserved set.
_CODE_VERIFIER_RE = re.compile(r"[A-Za-z0-9\-._~]{43,128}")

_TokenError = Literal["invalid_request", "unsupported_grant_type"]


def _error(error: _TokenError) -> None:
    """RFC 6749 section 5.2 error response: HTTP 400 with a JSON body."""
    response.status_code = http_client.BAD_REQUEST
    response.set_content_type("application/json")
    response.set_data(OAuthTokenErrorResponse(error=error).model_dump_json(exclude_none=True))


class OAuthTokenPage(Page):
    """RFC 6749 section 3.2 token endpoint for this site.

    Accessed unauthenticated, referenced via the "token_endpoint" field of the
    RFC 8414 authorization server metadata document. Returns 404 while no
    OAuth-consuming feature is enabled for the site (the enabled predicate is
    injected at registration).

    This is a stub: the request shape is validated (POST, form encoding,
    grant_type, required parameters, code_verifier syntax) and rejections
    follow the RFC 6749 section 5.2 error format, but the authorization code
    grant itself is not verified yet -- no code redemption, no PKCE, no
    client binding; any well-formed request gets a random access token.
    """

    def __init__(self, enabled: Callable[[], bool]) -> None:
        self._enabled = enabled

    @override
    def page(self, ctx: PageContext) -> PageResult:
        if not self._enabled():
            response.status_code = http_client.NOT_FOUND
            return None

        # RFC 6749 section 5.1/5.2: token endpoint responses carry tokens or
        # error details and MUST NOT be cached. Set up front to cover every
        # exit path below.
        response.headers["Cache-Control"] = "no-store"

        if request.request_method != "POST":
            response.status_code = http_client.METHOD_NOT_ALLOWED
            return None

        if request.mimetype != _FORM_CONTENT_TYPE:
            _error("invalid_request")
            return None

        # Token request parameters travel in the entity-body only (RFC 6749
        # section 4.1.3): request.form, never request.var, which would also
        # accept the query string and thereby leak the code and code_verifier
        # secrets into access logs. An empty value counts as absent
        # (section 3.2).
        form = request.form
        if any(len(form.getlist(name)) > 1 for name in _KNOWN_PARAMS):
            _error("invalid_request")
            return None

        grant_type = form.get("grant_type")
        if not grant_type:
            _error("invalid_request")
            return None
        if grant_type != "authorization_code":
            _error("unsupported_grant_type")
            return None

        # redirect_uri is deliberately not required here: OAuth 2.1
        # (section 10.2) removed it from the token request; it is only
        # enforced against the stored record if the client sends one.
        if not form.get("code") or not form.get("client_id"):
            _error("invalid_request")
            return None

        # Absent and malformed count the same: the syntax check runs before
        # any code would be consumed, so a bad request never burns a code.
        code_verifier = form.get("code_verifier")
        if code_verifier is None or _CODE_VERIFIER_RE.fullmatch(code_verifier) is None:
            _error("invalid_request")
            return None

        response.set_content_type("application/json")
        response.set_data(
            OAuthTokenResponse(access_token=secrets.token_urlsafe(32)).model_dump_json()
        )
        return None
