exports_files(
    ["win_printers.ps1"],
    visibility = ["//agents/windows/plugins:__pkg__"],
)

filegroup(
    name = "powershell_scripts",
    srcs = ["win_printers.ps1"],
    tags = ["lint-with-psscriptanalyzer"],
)
