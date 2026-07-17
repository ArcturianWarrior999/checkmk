load("@aspect_rules_py//py:defs.bzl", "py_library")
load("@cmk_requirements//:requirements.bzl", "requirement")

py_library(
    name = "matchers",
    srcs = ["matchers.py"],
    imports = ["../../.."],
    visibility = [
        "//cmk:__subpackages__",
        "//tests:__subpackages__",
    ],
    deps = [
        "//cmk/gui/utils:loading_transition",
        "//cmk/gui/utils:roles",
    ],
)

py_library(
    name = "permissions",
    srcs = ["permissions.py"],
    imports = ["../../.."],
    visibility = [
        "//cmk:__subpackages__",
        "//tests:__subpackages__",
    ],
    deps = [
        "//cmk/gui:page_toolkit",
        "//packages/cmk-ccc:plugin-registry",
        "//packages/cmk-shared-typing:cmk_shared_typing_py",
    ],
)

py_library(
    name = "search",
    srcs = glob(
        include = ["**/*.py"],
        exclude = [
            "matchers.py",
            "permissions.py",
        ],
    ),
    imports = ["../../.."],
    visibility = [
        "//cmk:__subpackages__",
        "//tests:__subpackages__",
    ],
    deps = [
        ":matchers",
        ":permissions",
        "//cmk/gui:config",
        "//cmk/gui:core_toolkit",
        "//cmk/gui:page_toolkit",
        "//cmk/gui:session_context",
        "//cmk/gui/background_job/job",
        "//cmk/gui/utils:loading_transition",
        "//cmk/gui/utils:regex",
        "//cmk/gui/utils:roles",
        "//cmk/gui/utils:urls",
        "//cmk/utils",
        "//cmk/utils:redis",
        "//packages/cmk-ccc:exceptions",
        "//packages/cmk-shared-typing:cmk_shared_typing_py",
        requirement("pydantic"),
        requirement("redis"),
    ],
)
