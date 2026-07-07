#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Mapping

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    SingleChoice,
    SingleChoiceElement,
)
from cmk.rulesets.v1.rule_specs import AgentConfig, Topic

_VALID_VALUES = frozenset(("inetd", "no_service"))


def migrate(value: object) -> Mapping[str, object]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str) and value in _VALID_VALUES:
        return {"deployment": value}
    raise ValueError(f"Unexpected value: {value!r}")


def _parameter_form_super_server_solaris() -> Dictionary:
    return Dictionary(
        title=Title("Checkmk agent network service (Solaris)"),
        help_text=Help(
            "The Checkmk agent does not listen on its own for incoming network connections."
            " By default, it makes use of so called super servers, which"
            " listen on the network and dispatch incoming requests to applications like"
            " the Checkmk agent. Baked agent packages for Solaris come with an"
            " installation script for an inetd service."
            " With this rule, you can optionally disable the service installation"
            " , e.g., if you connect to the agent via SSH.\n"
        ),
        elements={
            "deployment": DictElement(
                required=True,
                parameter_form=SingleChoice(
                    elements=[
                        SingleChoiceElement(
                            name="inetd",
                            title=Title("Install and activate inetd service"),
                        ),
                        SingleChoiceElement(
                            name="no_service",
                            title=Title("Don't install Checkmk service"),
                        ),
                    ],
                    prefill=DefaultValue("inetd"),
                ),
            ),
        },
        migrate=migrate,
    )


rule_spec_super_server_solaris = AgentConfig(
    name="super_server_solaris",
    title=Title("Checkmk agent network service (Solaris)"),
    topic=Topic.LINUX,
    parameter_form=_parameter_form_super_server_solaris,
)
