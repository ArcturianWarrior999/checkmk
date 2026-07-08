#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from pathlib import Path

from omdlib.mcp import MCP_SERVER


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
