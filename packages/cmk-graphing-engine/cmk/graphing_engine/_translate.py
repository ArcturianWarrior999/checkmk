#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import re
from collections.abc import Mapping

from ._perfdata import (
    CheckCommand,
    MetricName,
    MetricTranslation,
    RawMetricNames,
)

_PREDICT_PREFIXES = ("predict_lower_", "predict_")


def _split_predict_prefix(metric_name: str) -> tuple[str, str]:
    for prefix in _PREDICT_PREFIXES:
        if metric_name.startswith(prefix):
            return prefix, metric_name[len(prefix) :]
    return "", metric_name


def _translations_for_command(
    check_command: CheckCommand,
    translations: Mapping[CheckCommand, Mapping[MetricName, MetricTranslation]],
) -> Mapping[MetricName, MetricTranslation]:
    if not check_command:
        return {}
    if check_command in translations:
        return translations[check_command]
    if check_command.startswith("check_mk-mgmt_"):
        return translations.get(
            CheckCommand(check_command.replace("check_mk-mgmt_", "check_mk-", 1)), {}
        )
    return {}


def _find_translation(
    metric_name: MetricName,
    translations: Mapping[MetricName, MetricTranslation],
) -> MetricTranslation:
    if (translation := translations.get(metric_name)) is not None:
        return translation
    for pattern, translation in translations.items():
        if pattern.startswith("~") and re.compile(pattern[1:]).match(metric_name):
            return translation
    return MetricTranslation(name=metric_name)


def translate_metric_names(
    raw_metrics: RawMetricNames,
    translations: Mapping[CheckCommand, Mapping[MetricName, MetricTranslation]],
) -> frozenset[MetricName]:
    command_translations = _translations_for_command(raw_metrics.check_command, translations)
    names = set()
    for metric_name in raw_metrics.metric_names:
        prefix, bare_name = _split_predict_prefix(metric_name)
        translation = _find_translation(MetricName(bare_name), command_translations)
        names.add(MetricName(f"{prefix}{translation.name}"))
    return frozenset(names)
