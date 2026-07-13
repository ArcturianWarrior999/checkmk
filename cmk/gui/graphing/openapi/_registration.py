#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from cmk.gui.openapi.framework.registry import VersionedEndpointRegistry
from cmk.gui.openapi.restful_objects.endpoint_family import EndpointFamilyRegistry

from ._family import GRAPH_FAMILY
from .discover_template_graphs import ENDPOINT_DISCOVER_TEMPLATE_GRAPHS
from .fetch_graph_data import ENDPOINT_FETCH_GRAPH_DATA
from .set_graph_pin import ENDPOINT_SET_GRAPH_PIN


def register(
    versioned_endpoint_registry: VersionedEndpointRegistry,
    endpoint_family_registry: EndpointFamilyRegistry,
) -> None:
    endpoint_family_registry.register(GRAPH_FAMILY)
    versioned_endpoint_registry.register(ENDPOINT_DISCOVER_TEMPLATE_GRAPHS)
    versioned_endpoint_registry.register(ENDPOINT_FETCH_GRAPH_DATA)
    versioned_endpoint_registry.register(ENDPOINT_SET_GRAPH_PIN)
