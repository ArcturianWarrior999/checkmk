#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
"""Pure-data description of a rendered feature page."""

from collections.abc import Sequence
from dataclasses import dataclass, field


@dataclass(frozen=True)
class BreadcrumbItem:
    title: str
    url: str | None = None


@dataclass(frozen=True)
class PageMenuLink:
    """A single, link-style page menu entry."""

    title: str
    icon_name: str
    url: str
    is_enabled: bool = True
    is_shortcut: bool = False
    is_suggested: bool = False


@dataclass(frozen=True)
class PageMenuTopic:
    title: str
    entries: Sequence[PageMenuLink] = field(default_factory=list)


@dataclass(frozen=True)
class PageMenuDropdown:
    name: str
    title: str
    topics: Sequence[PageMenuTopic] = field(default_factory=list)


@dataclass(frozen=True)
class PageContainerMenu:
    dropdowns: Sequence[PageMenuDropdown] = field(default_factory=list)


@dataclass(frozen=True)
class PageContainer:
    title: str
    breadcrumb: Sequence[BreadcrumbItem]
    content: str
    page_menu: PageContainerMenu | None = None
