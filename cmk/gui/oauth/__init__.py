#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Callable

from cmk.gui.oauth._authorization_server import OAuthAuthorizationServerMetadataPage
from cmk.gui.oauth._authorize import OAuthAuthorizePage
from cmk.gui.oauth._client_registration import OAuthClientRegistrationPage
from cmk.gui.oauth._token import OAuthTokenPage
from cmk.gui.pages import PageEndpoint, PageRegistry

__all__ = ["register"]


def register(page_registry: PageRegistry, *, enabled: Callable[[], bool]) -> None:
    """Register the OAuth authorization server pages of this site.

    enabled decides whether any OAuth-consuming feature (currently only the
    MCP server) is active for the site; while it returns False, every page
    answers 404.
    """
    page_registry.register(
        PageEndpoint(
            "noauth:oauth_authorization_server", OAuthAuthorizationServerMetadataPage(enabled)
        )
    )
    page_registry.register(PageEndpoint("oauth_authorize", OAuthAuthorizePage(enabled)))
    page_registry.register(
        PageEndpoint("noauth:oauth_client_registration", OAuthClientRegistrationPage(enabled))
    )
    page_registry.register(PageEndpoint("noauth:oauth_token", OAuthTokenPage(enabled)))
