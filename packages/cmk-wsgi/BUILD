load("@aspect_rules_py//py:defs.bzl", "py_library")
load("@bazel_skylib//rules:build_test.bzl", "build_test")
load("@cmk_requirements//:requirements.bzl", "requirement")
load("@rules_python//python:packaging.bzl", "py_wheel")
load("//bazel/rules:package_wheel.bzl", "package_wheel")

exports_files([
    "pyproject.toml",
    "requirements.in",
])

py_library(
    name = "utils",
    srcs = ["cmk/gui/wsgi/utils.py"],
    imports = ["."],
    visibility = [
        "//cmk:__subpackages__",
        "//tests:__subpackages__",
    ],
    deps = [
        requirement("flask"),
    ],
)

py_library(
    name = "cmk-wsgi",
    srcs = glob(
        include = ["cmk/gui/wsgi/**/*.py"],
        exclude = ["cmk/gui/wsgi/utils.py"],
    ) + ["cmk/gui/wsgi/applications/index.wsgi"],
    imports = ["."],
    visibility = [
        "//bin:__pkg__",
        "//cmk:__subpackages__",
        "//non-free/packages/cmk-agent-registration-extended:__pkg__",
        "//omd/packages/check_mk:__pkg__",
        "//tests:__subpackages__",
    ],
    deps = [
        ":utils",
        "//cmk/gui:auth",
        "//cmk/gui:config",
        "//cmk/gui:core_toolkit",
        "//cmk/gui:html_toolkit",
        "//cmk/gui:page_toolkit",
        "//cmk/gui/dashboard:page_token_error",
        "//cmk/gui/openapi:utils",
        "//cmk/gui/openapi:versioned_endpoint_map",
        "//cmk/gui/openapi/framework",
        "//cmk/gui/openapi/framework:api_config",
        "//cmk/gui/openapi/framework:core",
        "//cmk/gui/openapi/framework:types",
        "//cmk/gui/openapi/restful_objects",
        "//cmk/gui/openapi/restful_objects:type_defs",
        "//cmk/gui/openapi/spec:utils",
        "//cmk/gui/token_auth",
        "//cmk/gui/userdb",
        "//cmk/gui/utils:cookies",
        "//cmk/gui/utils:escaping",
        "//cmk/gui/utils:html",
        "//cmk/gui/utils:mobile",
        "//cmk/gui/utils:output_funnel",
        "//cmk/gui/utils:roles",
        "//cmk/gui/utils:timeout_manager",
        "//cmk/gui/utils:urls",
        "//cmk/gui/utils:user_errors",
        "//cmk/gui/watolib",
        "//cmk/gui/watolib:config_infra",
        "//cmk/utils:paths",
        "//packages/cmk-ccc:exceptions",
        "//packages/cmk-ccc:site",
        "//packages/cmk-ccc:store",
        "//packages/cmk-ccc:version",
        "//packages/cmk-crypto",
        "//packages/cmk-livestatus-client",
        "//packages/cmk-trace",
        requirement("apispec"),
        requirement("flask"),
        requirement("opentelemetry-api"),
        requirement("opentelemetry-instrumentation-redis"),
        requirement("opentelemetry-instrumentation-requests"),
        requirement("opentelemetry-instrumentation-wsgi"),
        requirement("pyprof2calltree"),
        requirement("pyyaml"),
        requirement("werkzeug"),
    ],
)

py_wheel(
    name = "wheel",
    distribution = "cmk-wsgi",
    strip_path_prefixes = ["packages/cmk-wsgi"],
    # TODO: Duplicated from pyproject.toml
    version = "1.0.0",
    visibility = ["//visibility:public"],
    deps = [
        ":cmk-wsgi",
        ":utils",
    ],
)

build_test(
    name = "build_test",
    targets = [
        ":wheel",
    ],
)

package_wheel(
    name = "pkg_tar",
    visibility = ["//visibility:public"],
    whl = "wheel",
)

sh_library(
    name = "f12",
    srcs = [
        "cmk/gui/wsgi/.f12",
    ],
)
