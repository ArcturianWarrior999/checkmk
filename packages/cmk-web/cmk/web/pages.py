#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
import abc
from collections.abc import Callable
from dataclasses import dataclass

from cmk.web.context import ActionUrlBuilder, RequestProtocol, UserProtocol
from cmk.web.page_container import PageContainer


@dataclass(frozen=True, kw_only=True)
class PageContext:
    """Dependencies passed to a feature page handler.

    Use these instead of importing ``cmk.gui`` globals so the page stays free of
    a ``cmk.gui`` dependency.
    """

    request: RequestProtocol
    user: UserProtocol
    i18n: Callable[[str], str]
    make_action_url: ActionUrlBuilder


class Page(abc.ABC):
    @abc.abstractmethod
    def page(self, ctx: PageContext) -> PageContainer:
        raise NotImplementedError
