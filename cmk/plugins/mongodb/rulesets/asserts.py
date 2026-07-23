#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from typing import NamedTuple

from cmk.rulesets.v1 import Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    Float,
    LevelDirection,
    migrate_to_float_simple_levels,
    SimpleLevels,
    SimpleLevelsConfigModel,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, HostCondition, Topic


class AssertType(NamedTuple):
    id: str
    title: Title


ASSERT_TYPES = [
    AssertType("msg", Title("Message rate")),
    AssertType("rollovers", Title("Rollovers rate")),
    AssertType("regular", Title("Regular rate")),
    AssertType("warning", Title("Warning rate")),
    AssertType("user", Title("User rate")),
]


def _parameter_valuespec_mongodb_asserts() -> Dictionary:
    return Dictionary(
        elements={
            "%s_assert_rate" % assert_type.id: DictElement[SimpleLevelsConfigModel[float]](
                parameter_form=SimpleLevels[float](
                    title=assert_type.title,
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=DefaultValue((1.0, 2.0)),
                    form_spec_template=Float(unit_symbol="Asserts per second"),
                    migrate=migrate_to_float_simple_levels,
                )
            )
            for assert_type in ASSERT_TYPES
        }
    )


rule_spec_mongodb_asserts = CheckParameters(
    name="mongodb_asserts",
    title=Title("MongoDB assert rates"),
    topic=Topic.STORAGE,
    parameter_form=_parameter_valuespec_mongodb_asserts,
    condition=HostCondition(),
)
