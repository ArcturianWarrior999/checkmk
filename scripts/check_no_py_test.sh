#!/usr/bin/env bash

# Direct use of py_test in BUILD files is forbidden — use the py_cmk_test
# macro from //bazel/rules:py_cmk_test.bzl instead, which enforces the
# standard Checkmk pytest defaults.
#
# Two patterns are needed to catch all direct usages:
# - the quoted "py_test" load symbol, which also catches aliased and
#   multi-line load statements while ignoring comments and py_pytest_main
# - a bare py_test( call site, since Bazel autoloading resolves the name
#   even without a load statement (e.g. packages/cmk-ec/BUILD used this)

current_offenders() {
    git grep --files-with-matches -E '"py_test"|^\s*py_test\(' -- '*BUILD' '*BUILD.bazel' | sort
}

known_offenders() {
    # Deliberate exceptions that are allowed to keep using py_test directly.
    # New targets must use py_cmk_test instead of being added here.
    while [ "$1" == "--known-offender" ]; do
        echo "$2"
        shift 2
    done
}

main() {
    current=$(current_offenders)
    expected=$(known_offenders "$@" | sort)

    fixed=$(comm -13 <(echo "${current}") <(echo "${expected}"))
    broken=$(comm -23 <(echo "${current}") <(echo "${expected}"))

    if [ -n "${fixed}" ]; then
        echo "BUILD files no longer using py_test but still listed as exception:"
        echo "${fixed}"
    fi

    if [ -n "${broken}" ]; then
        echo "Found BUILD files using py_test directly, use py_cmk_test instead:"
        echo "${broken}"
    fi

    [ -z "${fixed}${broken}" ]
}

main "$@"
