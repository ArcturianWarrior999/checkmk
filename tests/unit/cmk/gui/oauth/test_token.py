#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import pytest
from flask import Flask

from cmk.gui.config import Config
from cmk.gui.http import request, response
from cmk.gui.oauth._token import OAuthTokenPage
from cmk.gui.pages import PageContext

_FORM_CONTENT_TYPE = "application/x-www-form-urlencoded"
_VALID_FORM = {"grant_type": "authorization_code"}


@pytest.mark.usefixtures("request_context")
class TestOAuthTokenPage:
    def test_returns_access_token_when_enabled(self, flask_app: Flask) -> None:
        with flask_app.test_request_context(method="POST", data=_VALID_FORM):
            flask_app.preprocess_request()
            OAuthTokenPage(lambda: True).handle_page(PageContext(config=Config(), request=request))

            assert response.status_code == 200
            assert isinstance(response.json, dict)
            assert response.json["token_type"] == "Bearer"
            access_token = response.json["access_token"]
            assert isinstance(access_token, str)
            assert access_token

    def test_returns_different_access_token_on_each_call(self, flask_app: Flask) -> None:
        with flask_app.test_request_context(method="POST", data=_VALID_FORM):
            flask_app.preprocess_request()
            OAuthTokenPage(lambda: True).handle_page(PageContext(config=Config(), request=request))
            assert isinstance(response.json, dict)
            first_access_token = response.json["access_token"]

            OAuthTokenPage(lambda: True).handle_page(PageContext(config=Config(), request=request))
            assert isinstance(response.json, dict)
            second_access_token = response.json["access_token"]

        assert first_access_token != second_access_token

    def test_returns_404_when_disabled(self, flask_app: Flask) -> None:
        with flask_app.test_request_context(method="POST", data=_VALID_FORM):
            flask_app.preprocess_request()
            OAuthTokenPage(lambda: False).handle_page(PageContext(config=Config(), request=request))

            assert response.status_code == 404

    def test_returns_405_when_method_is_not_post(self, flask_app: Flask) -> None:
        with flask_app.test_request_context(method="GET"):
            flask_app.preprocess_request()
            OAuthTokenPage(lambda: True).handle_page(PageContext(config=Config(), request=request))

            assert response.status_code == 405

    def test_rejects_a_non_form_content_type(self, flask_app: Flask) -> None:
        with flask_app.test_request_context(
            method="POST",
            data='{"grant_type": "authorization_code"}',
            content_type="application/json",
        ):
            flask_app.preprocess_request()
            OAuthTokenPage(lambda: True).handle_page(PageContext(config=Config(), request=request))

            assert response.status_code == 400
            assert response.json == {"error": "invalid_request"}

    def test_accepts_a_form_content_type_with_charset_parameter(self, flask_app: Flask) -> None:
        with flask_app.test_request_context(
            method="POST",
            data="grant_type=authorization_code",
            content_type="application/x-www-form-urlencoded; charset=UTF-8",
        ):
            flask_app.preprocess_request()
            OAuthTokenPage(lambda: True).handle_page(PageContext(config=Config(), request=request))

            assert response.status_code == 200

    def test_ignores_a_grant_type_in_the_query_string(self, flask_app: Flask) -> None:
        with flask_app.test_request_context(
            "/oauth_token.py?grant_type=authorization_code",
            method="POST",
            content_type=_FORM_CONTENT_TYPE,
        ):
            flask_app.preprocess_request()
            OAuthTokenPage(lambda: True).handle_page(PageContext(config=Config(), request=request))

            assert response.status_code == 400
            assert response.json == {"error": "invalid_request"}

    def test_rejects_a_missing_grant_type(self, flask_app: Flask) -> None:
        with flask_app.test_request_context(method="POST", content_type=_FORM_CONTENT_TYPE):
            flask_app.preprocess_request()
            OAuthTokenPage(lambda: True).handle_page(PageContext(config=Config(), request=request))

            assert response.status_code == 400
            assert response.json == {"error": "invalid_request"}

    def test_treats_an_empty_grant_type_as_missing(self, flask_app: Flask) -> None:
        with flask_app.test_request_context(method="POST", data={"grant_type": ""}):
            flask_app.preprocess_request()
            OAuthTokenPage(lambda: True).handle_page(PageContext(config=Config(), request=request))

            assert response.status_code == 400
            assert response.json == {"error": "invalid_request"}

    @pytest.mark.parametrize("grant_type", ["refresh_token", "client_credentials", "no-such-grant"])
    def test_rejects_unsupported_grant_types(self, flask_app: Flask, grant_type: str) -> None:
        with flask_app.test_request_context(method="POST", data={"grant_type": grant_type}):
            flask_app.preprocess_request()
            OAuthTokenPage(lambda: True).handle_page(PageContext(config=Config(), request=request))

            assert response.status_code == 400
            assert response.json == {"error": "unsupported_grant_type"}

    def test_token_response_is_not_cacheable(self, flask_app: Flask) -> None:
        with flask_app.test_request_context(method="POST", data=_VALID_FORM):
            flask_app.preprocess_request()
            OAuthTokenPage(lambda: True).handle_page(PageContext(config=Config(), request=request))

            assert response.headers.get("Cache-Control") == "no-store"

    def test_error_response_is_not_cacheable(self, flask_app: Flask) -> None:
        with flask_app.test_request_context(method="POST", data={"grant_type": "refresh_token"}):
            flask_app.preprocess_request()
            OAuthTokenPage(lambda: True).handle_page(PageContext(config=Config(), request=request))

            assert response.headers.get("Cache-Control") == "no-store"
