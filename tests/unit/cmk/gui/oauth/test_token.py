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


@pytest.mark.usefixtures("request_context")
class TestOAuthTokenPage:
    def test_returns_access_token_when_enabled(self, flask_app: Flask) -> None:
        with flask_app.test_request_context(method="POST"):
            flask_app.preprocess_request()
            OAuthTokenPage(lambda: True).handle_page(PageContext(config=Config(), request=request))

            assert response.status_code == 200
            assert isinstance(response.json, dict)
            assert response.json["token_type"] == "Bearer"
            access_token = response.json["access_token"]
            assert isinstance(access_token, str)
            assert access_token

    def test_returns_different_access_token_on_each_call(self, flask_app: Flask) -> None:
        with flask_app.test_request_context(method="POST"):
            flask_app.preprocess_request()
            OAuthTokenPage(lambda: True).handle_page(PageContext(config=Config(), request=request))
            assert isinstance(response.json, dict)
            first_access_token = response.json["access_token"]

            OAuthTokenPage(lambda: True).handle_page(PageContext(config=Config(), request=request))
            assert isinstance(response.json, dict)
            second_access_token = response.json["access_token"]

        assert first_access_token != second_access_token

    def test_returns_404_when_disabled(self, flask_app: Flask) -> None:
        with flask_app.test_request_context(method="POST"):
            flask_app.preprocess_request()
            OAuthTokenPage(lambda: False).handle_page(PageContext(config=Config(), request=request))

            assert response.status_code == 404

    def test_returns_405_when_method_is_not_post(self, flask_app: Flask) -> None:
        with flask_app.test_request_context(method="GET"):
            flask_app.preprocess_request()
            OAuthTokenPage(lambda: True).handle_page(PageContext(config=Config(), request=request))

            assert response.status_code == 405
