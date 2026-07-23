#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import subprocess
from email.message import Message
from unittest.mock import MagicMock

import pytest
from pytest import MonkeyPatch

from cmk.utils.mail import MailString, send_mail_sendmail


def test_send_mail_sendmail_success(monkeypatch: MonkeyPatch) -> None:
    run_mock = MagicMock(
        return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
    )
    monkeypatch.setattr(subprocess, "run", run_mock)

    send_mail_sendmail(Message(), MailString("me@example.com"), None)

    assert run_mock.call_args.kwargs["capture_output"] is True


def test_send_mail_sendmail_includes_output_on_failure(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(
        subprocess,
        "run",
        MagicMock(
            return_value=subprocess.CompletedProcess(
                args=[],
                returncode=1,
                stdout="stdout details",
                stderr="stderr details",
            )
        ),
    )

    with pytest.raises(RuntimeError) as excinfo:
        send_mail_sendmail(Message(), MailString("me@example.com"), None)

    message = str(excinfo.value)
    assert "exit code: 1" in message
    assert "stderr details" in message
    assert "stdout details" in message
