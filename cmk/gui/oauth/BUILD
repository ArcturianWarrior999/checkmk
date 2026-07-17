load("@aspect_rules_py//py:defs.bzl", "py_library")
load("@cmk_requirements//:requirements.bzl", "requirement")

py_library(
    name = "oauth",
    srcs = glob(
        include = ["**/*.py"],
    ),
    imports = ["../../.."],
    visibility = [
        "//cmk:__subpackages__",
        "//tests:__subpackages__",
    ],
    deps = [
        requirement("pydantic"),
        "//cmk/gui:core_toolkit",
        "//cmk/gui:page_toolkit",
        "//packages/cmk-ccc:site",
    ],
)
