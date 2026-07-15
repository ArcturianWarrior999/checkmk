load("@aspect_rules_py//py:defs.bzl", "py_binary", "py_library")

package(default_visibility = ["//tests:__subpackages__"])

py_library(
    name = "change_quality",
    srcs = [
        "__init__.py",
        "components.py",
        "detect_test.py",
        "detect_test_rust.py",
        "repo.py",
        "rows.py",
        "state.py",
        "walk.py",
    ],
    data = ["schema.sql"],
    imports = ["../../.."],
    deps = [
        "//tests/qa_metrics/db",
    ],
)

py_binary(
    name = "push",
    srcs = ["push.py"],
    imports = ["../../.."],
    deps = [
        ":change_quality",
        "//packages/cmk-werks",
        "//tests/qa_metrics/db",
    ],
)
