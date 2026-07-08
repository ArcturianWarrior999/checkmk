load("@aspect_rules_py//py:defs.bzl", "py_binary", "py_library")
load("//bazel/rules:py_cmk_test.bzl", "py_cmk_test")

py_library(
    name = "library",
    srcs = [
        "cmk/repo_checks/__init__.py",
        "cmk/repo_checks/deballast.py",
    ],
    data = ["cmk/repo_checks/py.typed"],
    imports = ["."],
)

# Per-target checker behind the deballast_aspect in deballast.bzl; not
# meant to be run directly.
py_binary(
    name = "deballast_bin",
    srcs = ["cmk/repo_checks/deballast.py"],
    imports = ["."],
    main = "cmk/repo_checks/deballast.py",
    visibility = ["//visibility:public"],
    deps = [":library"],
)

py_cmk_test(
    name = "test",
    size = "small",
    srcs = glob(["tests/test_*.py"]),
    deps = [":library"],
)
