#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import re
from collections.abc import Collection, Iterator, Mapping, Sequence
from dataclasses import dataclass
from typing import assert_never

from cmk.graphing.v1 import translations as translations_v1
from cmk.graphing_engine import MetricName, PerformanceData, RawPerformanceValue

_PREDICT_PREFIXES = ("predict_lower_", "predict_")

type _TranslationSpec = (
    translations_v1.RenameTo | translations_v1.ScaleBy | translations_v1.RenameToAndScaleBy
)


@dataclass(frozen=True, kw_only=True)
class RRDOriginal:
    metric_name: MetricName
    scale: float


def normalize_check_command(
    check_command: (
        translations_v1.PassiveCheck
        | translations_v1.ActiveCheck
        | translations_v1.HostCheckCommand
        | translations_v1.NagiosPlugin
    ),
) -> str:
    match check_command:
        case translations_v1.PassiveCheck():
            name = check_command.name
            return name if name.startswith("check_mk-") else f"check_mk-{name}"
        case translations_v1.ActiveCheck():
            name = check_command.name
            return name if name.startswith("check_mk_active-") else f"check_mk_active-{name}"
        case translations_v1.HostCheckCommand():
            name = check_command.name
            return name if name.startswith("check-mk-") else f"check-mk-{name}"
        case translations_v1.NagiosPlugin():
            name = (
                check_command.name
                if check_command.name.startswith("check_")
                else f"check_{check_command.name}"
            )
            return name.replace(".", "_")
        case _:
            assert_never(check_command)


def _specs_for_command(
    check_command: str,
    translations: Sequence[translations_v1.Translation],
) -> Mapping[str, _TranslationSpec]:
    if not check_command:
        return {}

    def _matches(candidate: str) -> Mapping[str, _TranslationSpec]:
        merged: dict[str, _TranslationSpec] = {}
        for translation in translations:
            if candidate in (normalize_check_command(cmd) for cmd in translation.check_commands):
                merged.update(translation.translations)
        return merged

    if direct := _matches(check_command):
        return direct
    if check_command.startswith("check_mk-mgmt_"):
        return _matches(check_command.replace("check_mk-mgmt_", "check_mk-", 1))
    return {}


def _name_and_scale(old_name: MetricName, spec: _TranslationSpec) -> tuple[MetricName, float]:
    match spec:
        case translations_v1.RenameTo():
            return MetricName(spec.metric_name), 1.0
        case translations_v1.ScaleBy():
            return old_name, spec.factor
        case translations_v1.RenameToAndScaleBy():
            return MetricName(spec.metric_name), spec.factor
        case _:
            assert_never(spec)


def _split_predict_prefix(metric_name: str) -> tuple[str, str]:
    for prefix in _PREDICT_PREFIXES:
        if metric_name.startswith(prefix):
            return prefix, metric_name[len(prefix) :]
    return "", metric_name


def _find_name_and_scale(
    metric_name: MetricName,
    specs: Mapping[str, _TranslationSpec],
) -> tuple[MetricName, float]:
    if (spec := specs.get(metric_name)) is not None:
        return _name_and_scale(metric_name, spec)
    for pattern, spec in specs.items():
        if pattern.startswith("~") and re.compile(pattern[1:]).match(metric_name):
            return _name_and_scale(metric_name, spec)
    return metric_name, 1.0


def _reverse_names(
    canonical_name: MetricName,
    specs: Mapping[str, _TranslationSpec],
) -> Mapping[MetricName, float]:
    result: dict[MetricName, float] = {}
    for old_name, spec in specs.items():
        if old_name.startswith("~"):
            continue
        name, scale = _name_and_scale(MetricName(old_name), spec)
        if name == canonical_name:
            result[MetricName(old_name)] = scale
    return result


def _deprecated_originals(
    metric_name: MetricName,
    specs: Mapping[str, _TranslationSpec],
    present: Collection[MetricName],
) -> Iterator[RRDOriginal]:
    prefix, bare_name = _split_predict_prefix(metric_name)
    for old_name, scale in _reverse_names(MetricName(bare_name), specs).items():
        if (column := MetricName(f"{prefix}{old_name}")) not in present:
            yield RRDOriginal(metric_name=column, scale=scale)


def originals_for_metric_name(
    metric_name: MetricName,
    check_command: str,
    translations: Sequence[translations_v1.Translation],
) -> Sequence[RRDOriginal]:
    specs = _specs_for_command(check_command, translations)
    return [
        RRDOriginal(metric_name=metric_name, scale=1.0),
        *_deprecated_originals(metric_name, specs, {metric_name}),
    ]


def _scaled(value: float | None, scale: float) -> float | None:
    return None if value is None else value * scale


def translate_performance_data(
    check_command: str,
    raw_values: Mapping[MetricName, RawPerformanceValue],
    translations: Sequence[translations_v1.Translation],
) -> Mapping[MetricName, PerformanceData]:
    specs = _specs_for_command(check_command, translations)
    scaled_by_name: dict[MetricName, tuple[RawPerformanceValue, float]] = {}
    for original_name, raw_value in raw_values.items():
        prefix, bare_name = _split_predict_prefix(original_name)
        name, scale = _find_name_and_scale(MetricName(bare_name), specs)
        scaled_by_name[MetricName(f"{prefix}{name}")] = (raw_value, scale)
    return {
        name: PerformanceData(
            value=_scaled(raw_value.value, scale),
            lower_warning=_scaled(raw_value.lower_warning, scale),
            lower_critical=_scaled(raw_value.lower_critical, scale),
            warning=_scaled(raw_value.warning, scale),
            critical=_scaled(raw_value.critical, scale),
            minimum=_scaled(raw_value.minimum, scale),
            maximum=_scaled(raw_value.maximum, scale),
        )
        for name, (raw_value, scale) in scaled_by_name.items()
    }
