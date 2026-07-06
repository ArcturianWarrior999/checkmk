#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
"""
Utility to discover subclass implementations
"""

from collections.abc import Callable, Mapping
from importlib import import_module
from inspect import isabstract
from pkgutil import iter_modules
from types import ModuleType
from typing import Any


def get_default_identifier(cls: type) -> str:
    return cls.__name__


def discover[T, V](
    root_module: ModuleType,
    base_class: type[T] | type[Any],
    get_identifier: Callable[[type[T]], V],
) -> Mapping[V, type[T]]:
    """
    Find all subclasses of `base_class` in module.

    Note: Private submodules are skipped!
    """
    subclasses = {}

    for mod_info in iter_modules(root_module.__path__, root_module.__name__ + "."):
        if mod_info.name.rsplit(".", 1)[-1].startswith("_"):
            # Private submodules are expected to not expose a backend!
            continue

        try:
            module = import_module(mod_info.name)
        except ImportError:
            continue

        for value in vars(module).values():
            if (
                isinstance(value, type)
                and issubclass(value, base_class)
                and value is not base_class
                and not isabstract(value)
            ):
                subclasses[get_identifier(value)] = value

    return subclasses
