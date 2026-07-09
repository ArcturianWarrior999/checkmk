#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import re
from pathlib import Path

import pytest

from omdlib.mcp import MCP_SERVER, MCP_TRACE_FORWARD_TOKEN, MCP_TRACE_FORWARD_URL


def test_mcp_conf_proxies_the_public_prm_route_when_enabled(tmp_path: Path) -> None:
    site_home = tmp_path
    (site_home / "etc" / "apache" / "conf.d").mkdir(parents=True)

    MCP_SERVER.activation("unit", site_home, {"MCP_SERVER": "on"})

    conf = (site_home / "etc" / "apache" / "conf.d" / "mcp.conf").read_text()
    assert "http://localhost/.well-known/oauth-protected-resource/unit/check_mk/mcp" in conf
    assert "ProxyPreserveHost On" in conf
    assert "Require all granted" in conf


def test_mcp_conf_is_removed_when_disabled(tmp_path: Path) -> None:
    site_home = tmp_path
    conf_dir = site_home / "etc" / "apache" / "conf.d"
    conf_dir.mkdir(parents=True)
    (conf_dir / "mcp.conf").write_text("stale")

    MCP_SERVER.activation("unit", site_home, {"MCP_SERVER": "off"})

    assert not (conf_dir / "mcp.conf").exists()


@pytest.mark.parametrize(
    "value",
    [
        "",  # default: forwarding disabled
        "http://collector.example.com:4317",
        "https://collector.example.com:44317",
    ],
)
def test_mcp_trace_forward_url_accepts(value: str) -> None:
    pattern = MCP_TRACE_FORWARD_URL.choices
    assert isinstance(pattern, re.Pattern)
    assert pattern.match(value)


@pytest.mark.parametrize(
    "value",
    [
        "collector.example.com:4317",  # scheme required
        "http://collector.example.com",  # port required
        "http://collector.example.com:99",  # port too short
        "ftp://collector.example.com:4317",
    ],
)
def test_mcp_trace_forward_url_rejects(value: str) -> None:
    pattern = MCP_TRACE_FORWARD_URL.choices
    assert isinstance(pattern, re.Pattern)
    assert not pattern.match(value)


@pytest.mark.parametrize(
    "value",
    [
        "",  # default: no Authorization header
        "glsa_4kCEXAMPLEUAJ8LMY7Op_0AA00a0A",
        "dGhpcyBpcyBhIHRva2Vu==",  # base64 with padding
        "abc.DEF-123_~+/x==",  # full token68 charset
    ],
)
def test_mcp_trace_forward_token_accepts(value: str) -> None:
    pattern = MCP_TRACE_FORWARD_TOKEN.choices
    assert isinstance(pattern, re.Pattern)
    assert pattern.match(value)


@pytest.mark.parametrize(
    "value",
    [
        "this is a token",  # inner space
        "token\nwith-newline",
    ],
)
def test_mcp_trace_forward_token_rejects(value: str) -> None:
    pattern = MCP_TRACE_FORWARD_TOKEN.choices
    assert isinstance(pattern, re.Pattern)
    assert not pattern.match(value)
