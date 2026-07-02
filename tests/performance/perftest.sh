#!/usr/bin/env bash
# Copyright (C) 2025 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
#
# Usage: perftest.sh <benchmark-dir> [perftest_plot-options...]
#
# When running in CI, update the performance database from the benchmark
# results in the given benchmark directory and validate the baselines.
# Additional options are passed through to all perftest_plot.py calls.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
REPO_PATH="$(dirname "$(dirname "${SCRIPT_DIR}")")"
BRANCH="$(make --no-print-directory --file="${REPO_PATH}/defines.make" print-BRANCH_VERSION)"
EDITION="${EDITION:-pro}"
BENCHMARK_DIR="${1:?usage: ${0} <benchmark-dir> [perftest_plot-options...]}"
ROOT_DIR="$(dirname "${BENCHMARK_DIR}")"
shift
if [ -n "${CI}" ]; then
    # update database; generate report and check weekly baseline
    "${SCRIPT_DIR}/perftest_plot.py" --update --branch-version="${BRANCH}" \
        --edition="${EDITION}" \
        --root-dir="${ROOT_DIR}" --log-level=INFO --dbhost=qa.lan.checkmk.net \
        --validate-baselines --alert-on-failure --jira-url="https://jira.lan.tribe29.com/" \
        "${@}" || exit 200
    if [[ "$(date '+%Y-%m-%d')" > "2025-12-01" ]]; then
        # check monthly baseline
        "${SCRIPT_DIR}/perftest_plot.py" --branch-version="${BRANCH}" \
            --edition="${EDITION}" \
            --root-dir="${ROOT_DIR}" --log-level=INFO --dbhost=qa.lan.checkmk.net \
            --validate-baselines --alert-on-failure --jira-url="https://jira.lan.tribe29.com/" \
            --skip-filesystem-writes --skip-database-writes --baseline-offset=30 \
            "${@}" || exit 200
    fi
    if [[ "$(date '+%Y-%m-%d')" > "2026-11-01" ]]; then
        # check yearly baseline
        "${SCRIPT_DIR}/perftest_plot.py" --branch-version="${BRANCH}" \
            --edition="${EDITION}" \
            --root-dir="${ROOT_DIR}" --log-level=INFO --dbhost=qa.lan.checkmk.net \
            --validate-baselines --alert-on-failure --jira-url="https://jira.lan.tribe29.com/" \
            --skip-filesystem-writes --skip-database-writes --baseline-offset=365 \
            "${@}" || exit 200
    fi
fi
echo "ROOT_DIR=${ROOT_DIR}"
