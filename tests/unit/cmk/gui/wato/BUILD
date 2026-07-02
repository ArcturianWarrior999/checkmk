load("@cmk_requirements//:requirements.bzl", "requirement")
load("//bazel/rules:py_cmk_test.bzl", "py_cmk_test")

py_cmk_test(
    name = "wato",
    srcs = glob(["**/*.py"]),
    args = [
        "tests/unit/cmk/gui/wato",
    ],
    env = {"EDITION": "community"},
    tags = [
        "deballast-keep=//cmk/gui/background_job/process:process",  # background jobs launched at runtime via the inline_background_jobs fixture
    ],
    use_project_pytest_config = True,
    deps = [
        "//cmk/gui:config",
        "//cmk/gui:core_toolkit",
        "//cmk/gui:page_toolkit",
        "//cmk/gui/background_job/process",
        "//cmk/gui/plugins/wato",
        "//cmk/gui/valuespec",
        "//cmk/gui/wato",
        "//cmk/gui/wato:base",
        "//cmk/gui/watolib",
        "//cmk/gui/watolib:config_infra",
        "//cmk/gui/watolib:registries",
        "//tests/unit:conftest",
        "//tests/unit/cmk/gui:conftest",
        requirement("beautifulsoup4"),
        requirement("flask"),
        requirement("pytest-mock"),
    ],
)
