#!/usr/bin/env python3
# Copyright (C) 2023 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

"""Handling of site-internal init scripts"""

import contextlib
import os
import subprocess
import sys
from typing import Literal, NamedTuple

from cmk.ccc import tty
from cmk.utils.local_secrets import SiteInternalSecret
from cmk.utils.security_event import log_security_event, SiteStartStoppedEvent


class _InitScript(NamedTuple):
    daemon: str
    executable: str


def call_init_scripts(
    site_dir: str,
    command: Literal["start", "stop", "restart", "reload", "status"],
    daemon: str | None = None,
) -> Literal[0, 2]:
    if daemon:
        executables = [s.executable for s in _daemon_init_scripts(daemon, site_dir)]
        if not executables:
            sys.stderr.write("ERROR: This daemon does not exist.\n")
            return 2
    else:
        executables = [s.executable for s in _init_scripts(site_dir)]
    # Restart: Do not restart each service after another,
    # but first do stop all, then start all again! This
    # preserves the order.
    if command == "restart":
        log_security_event(SiteStartStoppedEvent(event="restart", daemon=daemon))
        code_stop = call_init_scripts(site_dir, "stop", daemon)
        code_start = call_init_scripts(site_dir, "start", daemon)
        return 0 if (code_stop, code_start) == (0, 0) else 2

    # OMD guarantees OMD_ROOT to be the current directory
    with contextlib.chdir(site_dir):
        if command == "start":
            log_security_event(SiteStartStoppedEvent(event="start", daemon=daemon))
            SiteInternalSecret().regenerate()
        elif command == "stop":
            log_security_event(SiteStartStoppedEvent(event="stop", daemon=daemon))

        # Call stop scripts in reverse order. If daemon is set,
        # then only that start script will be affected
        if command == "stop":
            executables.reverse()

        success = True
        for script in executables:
            if not _call_init_script(script, command):
                success = False

    return 0 if success else 2


def check_status(
    site_dir: str,
    *,
    verbose: bool,
    display: bool = True,
    daemon: str | None = None,
    bare: bool = False,
) -> int:
    if not daemon:
        return _check_status_all(site_dir, verbose=verbose, display=display, bare=bare)
    return _check_status_daemon(site_dir, daemon, verbose=verbose, display=display, bare=bare)


def _check_status_all(
    site_dir: str,
    *,
    verbose: bool,
    display: bool,
    bare: bool,
) -> int:
    scripts = _init_scripts(site_dir)
    return _check_scripts_status(
        scripts,
        verbose=verbose,
        display=display,
        bare=bare,
    )


def _check_status_daemon(
    site_dir: str,
    daemon: str,
    *,
    verbose: bool,
    display: bool,
    bare: bool,
) -> int:
    daemon_scripts = _daemon_init_scripts(daemon, site_dir)
    if not daemon_scripts:
        if not bare:
            sys.stderr.write("ERROR: This daemon does not exist.\n")
        return 3
    return _check_scripts_status(daemon_scripts, verbose=verbose, display=display, bare=bare)


def _check_scripts_status(
    scripts: list[_InitScript],
    *,
    verbose: bool,
    display: bool,
    bare: bool,
) -> int:
    states = [
        _check_script_status(
            script,
            verbose=verbose,
            display=display,
            bare=bare,
        )
        for script in scripts
    ]
    return _summarize_status(states, display=display, bare=bare)


def _check_script_status(
    script: _InitScript,
    *,
    verbose: bool,
    display: bool,
    bare: bool,
) -> int:
    state = subprocess.call(
        [script.executable, "status"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    if display and (state != 5 or verbose):
        if bare:
            sys.stdout.write(script.daemon + " ")
        else:
            sys.stdout.write("%-20s" % (script.daemon + ":"))
            sys.stdout.write(tty.bold)

    if bare:
        if state != 5 or verbose:
            sys.stdout.write("%d\n" % state)

    if state == 0:
        if display and not bare:
            sys.stdout.write(tty.green + "running\n")
    elif state == 5:
        if display and verbose and not bare:
            sys.stdout.write(tty.blue + "unused\n")
    elif display and not bare:
        sys.stdout.write(tty.red + "stopped\n")
    if display and not bare:
        sys.stdout.write(tty.normal)

    return state


def _summarize_status(states: list[int], *, display: bool, bare: bool) -> int:
    num_running = sum(1 for state in states if state == 0)
    num_stopped = sum(1 for state in states if state not in (0, 5))

    if num_stopped > 0 and num_running == 0:
        exit_code = 1
        ovstate = tty.red + "stopped"
    elif num_running > 0 and num_stopped == 0:
        exit_code = 0
        ovstate = tty.green + "running"
    elif num_running == 0 and num_stopped == 0:
        exit_code = 0
        ovstate = tty.blue + "unused"
    else:
        exit_code = 2
        ovstate = tty.yellow + "partially running"
    if display:
        if bare:
            sys.stdout.write("OVERALL %d\n" % exit_code)
        else:
            sys.stdout.write("---------------------------\n")
            sys.stdout.write("Overall state:      %s\n" % (tty.bold + ovstate + tty.normal))
    return exit_code


def _daemon_init_scripts(daemon: str, site_dir: str) -> list[_InitScript]:
    daemon_scripts = [script for script in _init_scripts(site_dir) if script.daemon == daemon]
    if daemon_scripts:
        return daemon_scripts
    # We symlink the core script here, so let's keep reading this directory for backward
    # compatibility.
    init_d_exectuable = os.path.join("etc/init.d/", daemon)
    if os.path.exists(init_d_exectuable):
        return [_InitScript(daemon=daemon, executable=init_d_exectuable)]
    return []


def _init_scripts(site_dir: str) -> list[_InitScript]:
    rc_dir = f"{site_dir}/etc/rc.d"
    try:
        scripts = sorted(os.listdir(rc_dir))
        return [
            _InitScript(script.split("-", 1)[-1], os.path.join(rc_dir, script))
            for script in scripts
        ]
    except Exception:
        return []


def _call_init_script(scriptpath: str, command: str) -> bool:
    try:
        return subprocess.call([scriptpath, command]) in [0, 5]
    except OSError as e:
        sys.stderr.write(f"ERROR: Failed to run '{scriptpath}': {e}\n")
        return False
