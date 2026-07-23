load("@aspect_rules_py//py:defs.bzl", "py_library")
load("@cmk_requirements//:requirements.bzl", "requirement")
load("//bazel/rules:doctest.bzl", "py_doc_test")

py_library(
    name = "plugins-bakery",
    srcs = glob(["**/*.py"]),
    imports = ["../../.."],
    visibility = [
        "//cmk:__pkg__",
        "//cmk/base:__subpackages__",
        "//non-free/packages/cmk-bakery:__pkg__",
    ],
    deps = [
        "//cmk/base/api",
        "//cmk/utils",
        "//packages/cmk-ccc:exceptions",
        "//packages/cmk-plugin-apis:bakery",
        requirement("pyyaml"),
    ],
)

py_doc_test(
    name = "doctest",
    size = "small",
    srcs = [":plugins-bakery"],
)
