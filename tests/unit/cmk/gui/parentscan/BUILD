load("@cmk_requirements//:requirements.bzl", "requirement")
load("//bazel/rules:py_cmk_test.bzl", "py_cmk_test")

py_cmk_test(
    name = "parentscan",
    srcs = glob(["**/*.py"]),
    args = [
        "tests/unit/cmk/gui/parentscan",
    ],
    env = {"EDITION": "community"},
    tags = [
        "deballast-keep=//cmk/gui:auth",  # loaded at runtime by test fixtures (inline_background_jobs / parent-scan jobs)
        "deballast-keep=//cmk/gui:config",  # loaded at runtime by test fixtures (inline_background_jobs / parent-scan jobs)
        "deballast-keep=//cmk/gui:core_toolkit",  # loaded at runtime by test fixtures (inline_background_jobs / parent-scan jobs)
        "deballast-keep=//cmk/gui/background_job/job:job",  # loaded at runtime by test fixtures (inline_background_jobs / parent-scan jobs)
        "deballast-keep=//cmk/gui/background_job/process:process",  # loaded at runtime by test fixtures (inline_background_jobs / parent-scan jobs)
        "deballast-keep=//cmk/gui/wato:wato",  # loaded at runtime by test fixtures (inline_background_jobs / parent-scan jobs)
        "deballast-keep=//cmk/utils:redis",  # loaded at runtime by test fixtures (inline_background_jobs / parent-scan jobs)
        "deballast-keep=//omd/packages/omd:omdlib",  # loaded at runtime by test fixtures (inline_background_jobs / parent-scan jobs)
    ],
    use_project_pytest_config = True,
    deps = [
        "//cmk/gui:auth",
        "//cmk/gui:config",
        "//cmk/gui:core_toolkit",
        "//cmk/gui/background_job/job",
        "//cmk/gui/background_job/process",
        "//cmk/gui/parentscan",
        "//cmk/gui/wato",
        "//cmk/gui/watolib",
        "//cmk/gui/watolib:config_infra",
        "//cmk/utils:redis",
        "//omd/packages/omd:omdlib",
        "//packages/cmk-wsgi",
        "//tests/unit:conftest",
        "//tests/unit/cmk/gui:conftest",
        requirement("flask"),
        requirement("pytest-mock"),
        requirement("responses"),
        requirement("time-machine"),
    ],
)
