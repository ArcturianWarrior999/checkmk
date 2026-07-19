#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import re
from collections.abc import Iterator
from html import unescape
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

import pytest
from flask import Flask
from pytest_mock import MockerFixture

from cmk.gui.config import Config
from cmk.gui.http import request, response
from cmk.gui.oauth._authorize import OAuthAuthorizePage
from cmk.gui.pages import PageContext
from cmk.gui.utils.transaction_manager import TransactionManager


def _extract_redirect_target(body: str) -> str:
    match = re.search(r'<a[^>]+href="([^"]+)"', body)
    assert match is not None, "no fallback link in the redirect page"
    return unescape(match.group(1))


@pytest.fixture(name="mock_vue_manifest")
def fixture_mock_vue_manifest() -> Iterator[None]:
    # make_header() -> body_start() -> _head() loads the built frontend's
    # Vue manifest unconditionally, even in "static_files" mode. There's no
    # real frontend build in this test sandbox, so stub it out.
    fake_manifest = SimpleNamespace(
        main="cmk-frontend-vue/main.js",
        main_stylesheets=[],
        nav_sidebar="cmk-frontend-vue/nav_sidebar.js",
        nav_sidebar_stylesheets=[],
        stage1="cmk-frontend-vue/stage1.js",
    )
    with patch("cmk.gui.htmllib.html._load_vue_manifest", return_value=fake_manifest):
        yield


@pytest.mark.usefixtures("request_context", "mock_vue_manifest")
class TestOAuthAuthorizePage:
    def test_shows_consent_page_on_get(self, flask_app: Flask) -> None:
        with flask_app.test_request_context(
            query_string={"redirect_uri": "https://client.example/callback", "state": "xyz"}
        ):
            flask_app.preprocess_request()
            OAuthAuthorizePage(lambda: True).handle_page(
                PageContext(config=Config(), request=request)
            )

            assert response.status_code == 200
            body = response.get_data(as_text=True)
            assert "<form" in body
            assert 'name="_authorize"' in body
            assert 'name="_deny"' in body

    def test_consent_form_posts_back_to_the_request_path(self, flask_app: Flask) -> None:
        # Reached via the external OAuth issuer alias (/oauth-<site>/authorize,
        # see system_apache.py), not the backend's own /check_mk/oauth_authorize.py
        # path. The form must submit back to this same alias, not a relative
        # "oauth_authorize.py" that would resolve against the wrong base path.
        with flask_app.test_request_context(
            path="/oauth-heute/authorize",
            query_string={"redirect_uri": "https://client.example/callback"},
        ):
            flask_app.preprocess_request()
            OAuthAuthorizePage(lambda: True).handle_page(
                PageContext(config=Config(), request=request)
            )

            assert 'action="/oauth-heute/authorize"' in response.get_data(as_text=True)

    def test_redirects_with_code_once_confirmed(self, flask_app: Flask) -> None:
        with (
            patch.object(TransactionManager, "check_transaction", return_value=True),
            flask_app.test_request_context(
                method="POST",
                data={"redirect_uri": "https://client.example/callback", "state": "xyz"},
            ),
        ):
            flask_app.preprocess_request()
            OAuthAuthorizePage(lambda: True).handle_page(
                PageContext(config=Config(), request=request)
            )

            assert response.status_code == 200
            target_url = _extract_redirect_target(response.get_data(as_text=True))

        parts = urlsplit(target_url)
        assert f"{parts.scheme}://{parts.netloc}{parts.path}" == "https://client.example/callback"
        query = parse_qs(parts.query)
        assert query["state"] == ["xyz"]
        assert query["code"][0]

    def test_redirects_with_access_denied_when_denied(self, flask_app: Flask) -> None:
        with (
            patch.object(TransactionManager, "check_transaction", return_value=True),
            flask_app.test_request_context(
                method="POST",
                data={
                    "redirect_uri": "https://client.example/callback",
                    "state": "xyz",
                    "_deny": "Deny",
                },
            ),
        ):
            flask_app.preprocess_request()
            OAuthAuthorizePage(lambda: True).handle_page(
                PageContext(config=Config(), request=request)
            )

            assert response.status_code == 200
            target_url = _extract_redirect_target(response.get_data(as_text=True))

        parts = urlsplit(target_url)
        assert f"{parts.scheme}://{parts.netloc}{parts.path}" == "https://client.example/callback"
        query = parse_qs(parts.query)
        assert query["error"] == ["access_denied"]
        assert query["state"] == ["xyz"]
        assert "code" not in query

    def test_preserves_existing_query_params_on_redirect_uri(self, flask_app: Flask) -> None:
        with (
            patch.object(TransactionManager, "check_transaction", return_value=True),
            flask_app.test_request_context(
                method="POST",
                data={"redirect_uri": "https://client.example/callback?foo=bar"},
            ),
        ):
            flask_app.preprocess_request()
            OAuthAuthorizePage(lambda: True).handle_page(
                PageContext(config=Config(), request=request)
            )

            target_url = _extract_redirect_target(response.get_data(as_text=True))

        query = parse_qs(urlsplit(target_url).query)
        assert query["foo"] == ["bar"]
        assert query["code"][0]

    def test_redirect_page_is_not_an_http_redirect(self, flask_app: Flask) -> None:
        # Regression test: an HTTP 3xx here would carry the site's
        # form-action CSP over onto this cross-origin hop, and Chrome (unlike
        # Firefox) enforces that directive against redirects resulting from
        # a form submission -- blocking the navigation to redirect_uri since
        # it's necessarily a different origin (the OAuth client's callback).
        with (
            patch.object(TransactionManager, "check_transaction", return_value=True),
            flask_app.test_request_context(
                method="POST",
                data={"redirect_uri": "https://client.example/callback"},
            ),
        ):
            flask_app.preprocess_request()
            OAuthAuthorizePage(lambda: True).handle_page(
                PageContext(config=Config(), request=request)
            )

            assert response.status_code == 200
            body = response.get_data(as_text=True)
            assert 'http-equiv="refresh"' in body

    def test_shows_consent_page_again_when_not_confirmed(self, flask_app: Flask) -> None:
        with (
            patch.object(TransactionManager, "check_transaction", return_value=False),
            flask_app.test_request_context(
                method="POST",
                data={"redirect_uri": "https://client.example/callback"},
            ),
        ):
            flask_app.preprocess_request()
            OAuthAuthorizePage(lambda: True).handle_page(
                PageContext(config=Config(), request=request)
            )

            assert response.status_code == 200
            assert "<form" in response.get_data(as_text=True)

    def test_returns_400_when_redirect_uri_missing(self, flask_app: Flask) -> None:
        with flask_app.test_request_context():
            flask_app.preprocess_request()
            OAuthAuthorizePage(lambda: True).handle_page(
                PageContext(config=Config(), request=request)
            )

            assert response.status_code == 400

    def test_returns_400_when_redirect_uri_scheme_is_not_http_or_https(
        self, flask_app: Flask
    ) -> None:
        # Regression test: redirect_uri ends up in a href/content attribute
        # on the redirect page. HTML-escaping alone doesn't stop a
        # javascript: URI from executing if that link is followed.
        with flask_app.test_request_context(
            query_string={"redirect_uri": "javascript:alert(document.cookie)"}
        ):
            flask_app.preprocess_request()
            OAuthAuthorizePage(lambda: True).handle_page(
                PageContext(config=Config(), request=request)
            )

            assert response.status_code == 400

    def test_returns_404_when_disabled(self, flask_app: Flask) -> None:
        with flask_app.test_request_context(
            query_string={"redirect_uri": "https://client.example/callback"}
        ):
            flask_app.preprocess_request()
            OAuthAuthorizePage(lambda: False).handle_page(
                PageContext(config=Config(), request=request)
            )

            assert response.status_code == 404

    def test_logs_security_event_when_redirect_uri_is_invalid(
        self, flask_app: Flask, mocker: MockerFixture
    ) -> None:
        mock_log = mocker.patch("cmk.gui.oauth._authorize.log_security_event")
        with flask_app.test_request_context(query_string={"redirect_uri": "javascript:alert(1)"}):
            flask_app.preprocess_request()
            OAuthAuthorizePage(lambda: True).handle_page(
                PageContext(config=Config(), request=request)
            )

        mock_log.assert_called_once()
        assert mock_log.call_args.args[0].details["reason"] == "invalid or missing redirect_uri"
