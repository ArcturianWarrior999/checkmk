#!/usr/bin/env python3
# Copyright (C) 2025 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.gui import hooks
from cmk.gui.background_job.job import BackgroundJobRegistry
from cmk.gui.pages import PageEndpoint, PageRegistry

from .engines import livestatus as livestatus_engine
from .engines.redis import launch_requests_processing_background, SearchIndexBackgroundJob
from .matchers import MatchPluginRegistry
from .pages import PageUnifiedSearch


def register(
    page_registry: PageRegistry,
    job_registry: BackgroundJobRegistry,
    match_plugin_registry: MatchPluginRegistry,
) -> None:
    page_registry.register(PageEndpoint("ajax_unified_search", PageUnifiedSearch()))
    hooks.register_builtin("request-start", launch_requests_processing_background)
    job_registry.register(SearchIndexBackgroundJob)
    livestatus_engine.register(match_plugin_registry)
