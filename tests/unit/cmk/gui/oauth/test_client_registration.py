#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import pytest
from flask import Flask

from cmk.gui.config import Config
from cmk.gui.http import request, response
from cmk.gui.oauth._client_registration import OAuthClientRegistrationPage
from cmk.gui.pages import PageContext


@pytest.mark.usefixtures("request_context")
class TestOAuthClientRegistrationPage:
    def test_returns_client_id_when_enabled(self, flask_app: Flask) -> None:
        with flask_app.test_request_context(method="POST"):
            flask_app.preprocess_request()
            OAuthClientRegistrationPage(lambda: True).handle_page(
                PageContext(config=Config(), request=request)
            )

            assert response.status_code == 201
            assert isinstance(response.json, dict)
            client_id = response.json["client_id"]
            assert isinstance(client_id, str)
            assert client_id

    def test_returns_different_client_id_on_each_call(self, flask_app: Flask) -> None:
        with flask_app.test_request_context(method="POST"):
            flask_app.preprocess_request()
            OAuthClientRegistrationPage(lambda: True).handle_page(
                PageContext(config=Config(), request=request)
            )
            assert isinstance(response.json, dict)
            first_client_id = response.json["client_id"]

            OAuthClientRegistrationPage(lambda: True).handle_page(
                PageContext(config=Config(), request=request)
            )
            assert isinstance(response.json, dict)
            second_client_id = response.json["client_id"]

        assert first_client_id != second_client_id

    def test_returns_404_when_disabled(self, flask_app: Flask) -> None:
        with flask_app.test_request_context(method="POST"):
            flask_app.preprocess_request()
            OAuthClientRegistrationPage(lambda: False).handle_page(
                PageContext(config=Config(), request=request)
            )

            assert response.status_code == 404

    def test_returns_405_when_method_is_not_post(self, flask_app: Flask) -> None:
        with flask_app.test_request_context(method="GET"):
            flask_app.preprocess_request()
            OAuthClientRegistrationPage(lambda: True).handle_page(
                PageContext(config=Config(), request=request)
            )

            assert response.status_code == 405
