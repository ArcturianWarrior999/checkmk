load("@aspect_rules_py//py:defs.bzl", "py_library")

py_library(
    name = "diagnostics",
    srcs = glob(["**/*.py"]),
    imports = ["../.."],
    visibility = ["//cmk:__subpackages__"],
    deps = [
        "//packages/cmk-ccc:site",
    ],
)
