load("@aspect_rules_py//py:defs.bzl", "py_library")
load("@cmk_requirements//:requirements.bzl", "requirement")
load("//bazel/rules:py_cmk_test.bzl", "py_cmk_test")

package(default_visibility = ["//tests:__subpackages__"])

py_library(
    name = "performance",
    testonly = True,
    srcs = glob(
        ["**/*.py"],
        exclude = [
            "__init__.py",
            "sysmon.py",
        ],
    ),
    imports = ["../.."],
    deps = [
        ":sysmon",
        "//cmk:validate_plugins",
        requirement("pytest"),
        requirement("psycopg"),
        requirement("jira"),
        requirement("matplotlib"),
        requirement("requests"),
        requirement("playwright"),
        requirement("pytest_benchmark"),
        "//tests:scripts",
        "//tests/testlib",
        "//tests/testlib/common:repo",
        "//tests/testlib/common:utils",
    ],
)

py_library(
    name = "sysmon",
    testonly = True,
    srcs = [
        "__init__.py",
        "sysmon.py",
    ],
    imports = ["../.."],
    # Also used by performance suites living in their components, so their
    # resource tracking feeds the same reporting pipeline.
    visibility = ["//non-free/packages/cmk-metric-backend:__pkg__"],
    deps = [
        "//tests:pkg_marker",
        "//tests/testlib",
        requirement("psutil"),
    ],
)

py_cmk_test(
    name = "performance_test",
    size = "enormous",
    # No own srcs: the test files come in through the library deps; pytest
    # collects them from the runfiles tree via the args path.
    srcs = [],
    args = ["tests/performance"],
    # benchmarks, not pass/fail checks: run on demand, never from a wildcard build
    tags = ["manual"],
    use_project_pytest_config = True,
    deps = [
        ":performance",
        # tests/conftest.py loads the playwright plugin from the gui_e2e testlib
        "//tests:conftest",
        "//tests:gui_e2e",
        requirement("pytest-html"),
    ],
)

sh_library(
    name = "performance_sh",
    srcs = [
        "database/mk_client_cert.sh",
        "database/mk_server_cert.sh",
        "perftest.sh",
    ],
)
