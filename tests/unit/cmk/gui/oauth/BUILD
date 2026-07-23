load("@cmk_requirements//:requirements.bzl", "requirement")
load("//bazel/rules:py_cmk_test.bzl", "py_cmk_test")

py_cmk_test(
    name = "oauth",
    srcs = glob(["**/*.py"]),
    args = [
        "tests/unit/cmk/gui/oauth",
    ],
    env = {"EDITION": "community"},
    use_project_pytest_config = True,
    deps = [
        "//cmk/gui:config",
        "//cmk/gui:core_toolkit",
        "//cmk/gui:page_toolkit",
        "//cmk/gui/oauth",
        "//tests/unit:conftest",
        "//tests/unit/cmk/gui:conftest",
        requirement("fakeredis"),
        requirement("flask"),
        requirement("pytest-mock"),
        requirement("werkzeug"),
    ],
)
