load("@aspect_rules_py//py:defs.bzl", "py_library")
load("//bazel/rules:doctest.bzl", "py_doc_test")

py_library(
    name = "server_side_calls_backend",
    srcs = glob(["**/*.py"]),
    imports = ["../.."],
    visibility = [
        "//cmk:__subpackages__",
        "//packages/cmk-check-engine:__subpackages__",
        "//tests:__subpackages__",
    ],
    deps = [
        "//cmk/utils",
        "//packages/cmk-plugin-apis:discover_plugins",
        "//packages/cmk-plugin-apis:server_side_calls",
    ],
)

py_doc_test(
    name = "doctest",
    size = "small",
    srcs = [":server_side_calls_backend"],
)
