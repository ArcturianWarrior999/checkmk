#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import http.client as http_client
import secrets
import urllib.parse
from collections.abc import Callable
from typing import override

from cmk.gui.breadcrumb import Breadcrumb
from cmk.gui.header import make_header
from cmk.gui.htmllib.html import html
from cmk.gui.http import request, response
from cmk.gui.i18n import _
from cmk.gui.logged_in import user
from cmk.gui.pages import Page, PageContext, PageResult
from cmk.gui.utils.security_log_events import OAuthAuthorizationFailureEvent
from cmk.gui.utils.transaction_manager import transactions
from cmk.utils.security_event import log_security_event


class OAuthAuthorizePage(Page):
    """RFC 6749 section 3.1 authorization endpoint for this site.

    Referenced via the "authorization_endpoint" field of the RFC 8414
    authorization server metadata document. Requires an active Checkmk login
    session (enforced by the page registry via the missing "noauth:" prefix,
    see cmk.gui.oauth.register()) and shows a consent screen before issuing a
    code. Returns 404 while no OAuth-consuming feature is enabled for the
    site (the enabled predicate is injected at registration).

    This is a stub: it does not validate the client_id, it hands out a
    random authorization code as soon as the user confirms the consent
    screen. Rejected requests are logged as security events (see
    OAuthAuthorizationFailureEvent).
    """

    def __init__(self, enabled: Callable[[], bool]) -> None:
        self._enabled = enabled

    @override
    def page(self, ctx: PageContext) -> PageResult:
        if not self._enabled():
            response.status_code = http_client.NOT_FOUND
            return None

        redirect_uri = request.var("redirect_uri")
        if redirect_uri is None or urllib.parse.urlsplit(redirect_uri).scheme not in (
            "http",
            "https",
        ):
            # Rejects javascript:/data: etc. here, once, rather than at each
            # place redirect_uri ends up in a href/content attribute below --
            # HTML-escaping alone doesn't neutralize a dangerous URL scheme.
            self._log_authorization_failure("invalid or missing redirect_uri")
            response.status_code = http_client.BAD_REQUEST
            return None

        # received authorization form OK
        if request.request_method == "POST" and transactions.check_transaction():
            params = (
                {"error": "access_denied"}
                if request.var("_deny") is not None
                else {"code": secrets.token_urlsafe(32)}
            )
            if (state := request.var("state")) is not None:
                params["state"] = state
            self._show_redirect_page(ctx, redirect_uri, params)
            return None

        # show concent page
        self._show_consent_page(ctx, redirect_uri)
        return None

    def _open_login_frame(self, ctx: PageContext, title: str) -> None:
        # Reuses the login/two-factor page chrome: this page is shown before
        # the user reaches the normal, navigable GUI, just like those.
        html.render_headfoot = False
        html.add_body_css_class("login")
        html.add_body_css_class("two_factor")
        make_header(
            html,
            title=title,
            breadcrumb=Breadcrumb(),
            show_main_navigation=False,
            debug=ctx.config.debug,
            lang=user.language,
            inject_js_profiling_code=ctx.config.inject_js_profiling_code,
            load_frontend_vue=ctx.config.load_frontend_vue,
            custom_style_sheet=ctx.config.custom_style_sheet,
            screenshotmode=ctx.config.screenshotmode,
            inline_help_as_text=user.inline_help_as_text,
            hide_suggestions=not user.get_tree_state("suggestions", "all", True),
            user_role_ids=user.role_ids,
        )
        html.open_div(id_="login")
        html.open_div(id_="login_window")

    def _close_login_frame(self) -> None:
        html.close_div()
        html.close_div()
        html.footer()

    def _log_authorization_failure(self, reason: str) -> None:
        log_security_event(
            OAuthAuthorizationFailureEvent(
                reason=reason,
                client_id=request.var("client_id"),
                remote_ip=request.remote_ip,
            )
        )

    def _show_redirect_page(
        self, ctx: PageContext, redirect_uri: str, params: dict[str, str]
    ) -> None:
        parts = urllib.parse.urlsplit(redirect_uri)
        qs_map = dict(urllib.parse.parse_qsl(parts.query, keep_blank_values=True))
        qs_map.update(params)
        query = urllib.parse.urlencode(list(qs_map.items()))
        target_url = urllib.parse.urlunsplit(parts._replace(query=query))

        self._open_login_frame(ctx, _("Redirecting..."))
        # Not an HTTP redirect: redirect_uri is necessarily cross-origin (the
        # OAuth client's own callback), and Chrome -- unlike Firefox --
        # enforces the site's form-action CSP against redirects resulting
        # from a form submission. A 200 page that navigates via meta-refresh
        # isn't part of that chain, so no CSP directive here restricts it.
        # (A body-placed refresh meta tag is valid HTML5, unlike most other
        # meta variants -- make_header() has already closed <head> for us.)
        html.meta(httpequiv="refresh", content=f"0; url={target_url}")
        html.p(_("Redirecting..."))
        html.a(_("Click here if you are not redirected automatically."), href=target_url)
        self._close_login_frame()

    def _show_consent_page(self, ctx: PageContext, redirect_uri: str) -> None:
        client_id = request.var("client_id")

        self._open_login_frame(ctx, _("Authorize access"))
        html.h1(_("Authorize access"))
        if client_id is None:
            html.p(_("An application is requesting access to this Checkmk site."))
        else:
            html.p(
                _('The application "%(client_id)s" is requesting access to this Checkmk site.')
                % {"client_id": client_id}
            )
        html.p(_("Redirect target: %(redirect_uri)s") % {"redirect_uri": redirect_uri})
        # Explicit action: this page is also reachable via the external OAuth
        # issuer alias (/oauth-<site>/authorize, see system_apache.py), where
        # the default relative "oauth_authorize.py" action would resolve
        # against the wrong base path and never reach the backend.
        with html.form_context("oauth_authorize", method="POST", action=request.path):
            html.button("_authorize", _("Authorize"), cssclass="hot")
            html.button("_deny", _("Deny"))
            html.hidden_fields()
        self._close_login_frame()
