load("//bazel/rules:py_cmk_test.bzl", "py_cmk_test")

py_cmk_test(
    name = "backend_unit",
    size = "small",
    srcs = glob(["backend/**/*.py"]),
    deps = [
        "//packages/cmk-profiling:backend",
    ],
)

py_cmk_test(
    name = "gui_unit",
    size = "small",
    srcs = glob(["gui/**/*.py"]),
    deps = [
        "//packages/cmk-profiling:gui",
    ],
)
