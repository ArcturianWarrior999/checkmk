#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


import abc
import http.client as http_client
import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import cast, override, Protocol

from flask import current_app

import cmk.ccc.plugin_registry
from cmk.ccc.exceptions import MKException, MKGeneralException
from cmk.gui import http, i18n
from cmk.gui.config import active_config, Config
from cmk.gui.crash_handler import handle_exception_as_gui_crash_report
from cmk.gui.ctx_stack import g, set_global_var
from cmk.gui.display_options import DisplayOptions
from cmk.gui.exceptions import MKMissingDataError
from cmk.gui.htmllib.html import html, HTMLGenerator
from cmk.gui.http import Request, request, response
from cmk.gui.log import logger
from cmk.gui.theme import make_theme
from cmk.gui.utils.json import CustomObjectJSONEncoder
from cmk.gui.utils.mobile import is_mobile
from cmk.gui.utils.output_funnel import OutputFunnel
from cmk.gui.utils.timeout_manager import TimeoutManager
from cmk.gui.utils.user_errors import UserErrors

PageResult = object


@dataclass(frozen=True, kw_only=True)
class PageContext:
    """Context passed to page handlers, please use these instead of importing globals."""

    config: Config
    request: Request


class PageHandler(Protocol):
    def __call__(self, ctx: PageContext) -> None: ...


# At the moment pages are simply callables that somehow render content for the HTTP response
# and send it to the client.
#
# At least for HTML pages we should standardize the pages a bit more since there are things all pages do
# - Create a title, render the header
# - Have a breadcrumb
# - Optional: Handle actions
# - Render the page
#
# TODO: Check out the WatoMode class and find out how to do this. Looks like handle_page() could
# implement parts of the cmk.gui.wato.page_handler.page_handler() logic.
class Page(abc.ABC):
    """The base page class for our page registry.

    It is important that you DO NOT handle global variables like request and session from within the
    __init__ function.

    This causes a temporal dependency as the pages are now initialized at registration. You do,
    however, now have the ability to inject dependencies from external registries at registration.
    That is up to the discretion of the page and is totally optional as the __init__ method is not
    part of the base class.
    """

    def handle_page(self, ctx: PageContext) -> None:
        self.page(ctx)

    @abc.abstractmethod
    def page(self, ctx: PageContext) -> PageResult:
        """Override this to implement the page functionality"""
        raise NotImplementedError


# TODO: Clean up implicit _from_vars() procotocol
class AjaxPage(Page, abc.ABC):
    """Generic page handler that wraps page() calls into AJAX respones"""

    def _handle_exc(self, ctx: PageContext, method: Callable[[PageContext], PageResult]) -> None:
        try:
            method(ctx)
        # I added MKGeneralException during a refactoring, but I did not check if it is needed.
        except (MKException, MKGeneralException) as e:
            response.status_code = http_client.BAD_REQUEST
            html.write_text_permissive(str(e))
        except Exception as e:
            response.status_code = http_client.INTERNAL_SERVER_ERROR
            if ctx.config.debug:
                raise
            logger.exception("error calling AJAX page handler")
            handle_exception_as_gui_crash_report(
                plain_error=True,
                show_crash_link=getattr(g, "may_see_crash_reports", False),
                debug=ctx.config.debug,
                inject_js_profiling_code=ctx.config.inject_js_profiling_code,
                load_frontend_vue=ctx.config.load_frontend_vue,
                custom_style_sheet=ctx.config.custom_style_sheet,
                screenshotmode=ctx.config.screenshotmode,
            )
            html.write_text_permissive(str(e))

    @override
    def handle_page(self, ctx: PageContext) -> None:
        """The page handler, called by the page registry"""
        try:
            action_response = self.page(ctx)
            resp = {"result_code": 0, "result": action_response, "severity": "success"}
        except MKMissingDataError as e:
            resp = {"result_code": 1, "result": str(e), "severity": "success"}
        # I added MKGeneralException during a refactoring, but I did not check if it is needed.
        except (MKException, MKGeneralException) as e:
            resp = {"result_code": 1, "result": str(e), "severity": "error"}

        except Exception as e:
            if ctx.config.debug:
                raise
            logger.exception("error calling AJAX page handler")
            handle_exception_as_gui_crash_report(
                plain_error=True,
                show_crash_link=getattr(g, "may_see_crash_reports", False),
                debug=ctx.config.debug,
                inject_js_profiling_code=ctx.config.inject_js_profiling_code,
                load_frontend_vue=ctx.config.load_frontend_vue,
                custom_style_sheet=ctx.config.custom_style_sheet,
                screenshotmode=ctx.config.screenshotmode,
            )
            resp = {"result_code": 1, "result": str(e), "severity": "error"}

        response.set_content_type("application/json")
        try:
            response.set_data(json.dumps(resp, cls=CustomObjectJSONEncoder))
        except Exception:
            if ctx.config.debug:
                raise
            logger.exception("error serializing AJAX response")
            response.set_data(
                json.dumps(
                    {
                        "result_code": 1,
                        "result": "Internal error: failed to serialize response",
                        "severity": "error",
                    }
                )
            )


@dataclass(frozen=True)
class PageEndpoint:
    ident: str
    handler: PageHandler | Page


class PageRegistry(cmk.ccc.plugin_registry.Registry[PageEndpoint]):
    @override
    def plugin_name(self, instance: PageEndpoint) -> str:
        return instance.ident


page_registry = PageRegistry()


def get_page_handler(name: str, dflt: PageHandler | None = None) -> PageHandler | None:
    """Returns either the page handler registered for the given name or None

    In case dflt is given it returns dflt instead of None when there is no
    page handler for the requested name."""
    if endpoint := page_registry.get(name):
        if isinstance(endpoint.handler, Page):
            return endpoint.handler.handle_page
        return endpoint.handler
    return dflt


_OUTPUT_FORMAT_MIME_TYPES = {
    "json": "application/json",
    "json_export": "application/json",
    "jsonp": "application/javascript",
    "csv": "text/csv",
    "csv_export": "text/csv",
    "python": "text/plain",
    "text": "text/plain",
    "html": "text/html",
    "xml": "text/xml",
    "pdf": "application/pdf",
    "x-tgz": "application/x-tgz",
}


def get_output_format(output_format: str) -> str:
    if output_format not in _OUTPUT_FORMAT_MIME_TYPES:
        return "html"
    return output_format


def get_mime_type_from_output_format(output_format: str) -> str:
    return _OUTPUT_FORMAT_MIME_TYPES[output_format]


def set_global_vars() -> None:
    # These variables will only be retained for the duration of the request.
    # *Flask* will clear them after the request finished.

    # Be aware that the order, in which these initialized is intentional.
    set_global_var("translation", None)

    output_format = get_output_format(request.args.get("output_format", default="html", type=str))
    response = cast(http.Response, current_app.make_response(""))
    response.mimetype = get_mime_type_from_output_format(output_format)

    # The oder within this block is irrelevant.
    theme = make_theme(validate_choices=current_app.debug and not current_app.testing)
    theme.from_config(active_config.ui_theme)
    set_global_var("theme", theme)

    output_funnel = OutputFunnel(response)
    set_global_var("output_funnel", output_funnel)

    set_global_var("display_options", DisplayOptions())
    set_global_var("response", response)
    set_global_var("timeout_manager", TimeoutManager())
    set_global_var("user_errors", UserErrors())
    set_global_var(
        "html",
        HTMLGenerator(
            request,
            output_funnel=output_funnel,
            output_format=output_format,
            mobile=is_mobile(request, response),
        ),
    )

    lang_code = request.args.get("lang", default=active_config.default_language, type=str)
    i18n.localize(lang_code)  # sets g.translation
