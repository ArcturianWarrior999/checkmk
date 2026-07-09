#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import re
from pathlib import Path

from omdlib.config_api import Config, Hook, null_action


def _write_mcp_apache_conf(site_name: str, site_home: Path, config: Config) -> None:
    conf_path = site_home / "etc" / "apache" / "conf.d" / "mcp.conf"
    if config["MCP_SERVER"] == "on":
        sock = site_home / "tmp" / "run" / "mcp.sock"
        prm = f"/.well-known/oauth-protected-resource/{site_name}/check_mk/mcp"
        conf_path.write_text(
            f"""\
# Written by MCP_SERVER hook
# Guard the LoadModule directives: other hooks (e.g. TRACE_RECEIVE/jaeger) may
# already have loaded these proxy modules. Without the guards Apache logs
# "AH01574: module ... is already loaded, skipping" on startup.
<IfModule !proxy_module>
LoadModule proxy_module /omd/sites/{site_name}/lib/apache/modules/mod_proxy.so
</IfModule>
<IfModule !proxy_http_module>
LoadModule proxy_http_module /omd/sites/{site_name}/lib/apache/modules/mod_proxy_http.so
</IfModule>

ProxyPass "/{site_name}/check_mk/mcp" "unix://{sock}|http://localhost/" retry=0 timeout=120
ProxyPassReverse "/{site_name}/check_mk/mcp" "unix://{sock}|http://localhost/"

# OAuth 2.0 Protected Resource Metadata (RFC 9728). Public discovery document,
# proxied to the MCP server preserving the full path so its PRM route matches.
<Location "{prm}">
  ProxyPreserveHost On
  Require all granted
</Location>
# No retry=/timeout= here: mod_proxy keys workers by the socket origin (the
# "unix://...sock|http://localhost" prefix, path excluded), so this ProxyPass
# reuses the worker the "/{site_name}/check_mk/mcp" line above already defined.
# Those parameters are worker-scoped and set there; repeating them is ignored
# ("AH01146: Ignoring parameter ... because of worker sharing" at startup).
ProxyPass "{prm}" "unix://{sock}|http://localhost{prm}"
ProxyPassReverse "{prm}" "unix://{sock}|http://localhost{prm}"
"""
        )
    else:
        conf_path.unlink(missing_ok=True)


MCP_SERVER = Hook(
    name="MCP_SERVER",
    default=lambda _edition: "off",
    activation=_write_mcp_apache_conf,
    choices=[("on", "enable"), ("off", "disable")],
)

# Additional OTLP target for the MCP server's traces, independent of the
# site-wide TRACE_SEND pipeline: spans go to both. Empty (the default)
# disables it. Same URL shape as TRACE_SEND_TARGET.
MCP_TRACE_FORWARD_URL = Hook(
    name="MCP_TRACE_FORWARD_URL",
    choices=re.compile(r"^(|https?://[^\:]+:[0-9]{4,5})$"),
    default=lambda _edition: "",
    activation=null_action,
)

# Bearer token sent as the Authorization header with every export to
# MCP_TRACE_FORWARD_URL, for collectors that require authentication.
# Empty (the default) sends no header. Charset per RFC 6750 token68.
MCP_TRACE_FORWARD_TOKEN = Hook(
    name="MCP_TRACE_FORWARD_TOKEN",
    choices=re.compile(r"^[A-Za-z0-9._~+/-]*=*$"),
    default=lambda _edition: "",
    activation=null_action,
)
