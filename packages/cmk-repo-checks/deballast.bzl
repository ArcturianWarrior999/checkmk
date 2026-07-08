"""deballast aspect - report over-declared deps of py_* targets.

Applied to a py_library/py_binary/py_test target, the aspect spawns one
checker action per target. The action parses the target's own srcs for
imports and compares them against the Python modules provided by each
declared dep's direct srcs (described by per-dep JSON files the aspect
writes while propagating along `deps`). Findings are reported through
the aspect_rules_lint output contract, so they surface wherever the
other linters do.

Interactive use (prints findings to the terminal):
    bazel lint //cmk/...

CI / scripted use (materializes the report files):
    bazel build --config=deballast //cmk/...
    find bazel-bin -name "*.AspectRulesLintDeballast.out" -size +0c -exec cat {} +

For further information have a look at deballast.py.
"""

load("@aspect_rules_lint//lint:defs.bzl", "output_files")

DeballastInfo = provider(
    doc = "Dep-side interface of a py_* target for the deballast checker",
    fields = {
        "dep_json": "File describing the modules the target's direct srcs provide",
    },
)

_MNEMONIC = "AspectRulesLintDeballast"

_PY_RULE_KINDS = ("py_library", "py_binary", "py_test")

def _label_str(label):
    """Plain //pkg:name form for main-repo labels (no canonical @@ prefix)."""
    return "//" + label.package + ":" + label.name

def _write_empty_outputs(ctx, outputs):
    ctx.actions.write(outputs.human.out, "")
    ctx.actions.write(outputs.machine.out, "")
    if outputs.human.exit_code:
        ctx.actions.write(outputs.human.exit_code, "0\n")
    if outputs.machine.exit_code:
        ctx.actions.write(outputs.machine.exit_code, "0\n")

def _deballast_aspect_impl(target, ctx):
    if ctx.rule.kind not in _PY_RULE_KINDS:
        return []
    if target.label.workspace_name:
        # External targets (pip libs etc.) are neither analyzed nor described:
        # deps without dep info are treated as implicitly used by the checker.
        return []

    src_attr_labels = []
    srcs = []
    for src in getattr(ctx.rule.attr, "srcs", []):
        src_attr_labels.append(_label_str(src.label))
        for f in src.files.to_list():
            srcs.append(f)

    imports = list(getattr(ctx.rule.attr, "imports", []))

    keep_deps = [
        tag[len("deballast-keep="):]
        for tag in ctx.rule.attr.tags
        if tag.startswith("deballast-keep=")
    ]

    dep_json = ctx.actions.declare_file(target.label.name + ".deballast_dep.json")
    ctx.actions.write(dep_json, json.encode({
        "imports": imports,
        "label": _label_str(target.label),
        "package": target.label.package,
        "srcs": [f.short_path for f in srcs],
    }))

    outputs, info = output_files(_MNEMONIC, target, ctx)

    skip_tags = ("no-deballast", "no-lint")
    if not srcs or any([tag in ctx.rule.attr.tags for tag in skip_tags]):
        _write_empty_outputs(ctx, outputs)
        return [DeballastInfo(dep_json = dep_json), info]

    dep_jsons = [
        dep[DeballastInfo].dep_json
        for dep in getattr(ctx.rule.attr, "deps", [])
        if DeballastInfo in dep
    ]

    spec = ctx.actions.declare_file(target.label.name + ".deballast_spec.json")
    ctx.actions.write(spec, json.encode({
        "dep_attr_labels": [
            _label_str(dep.label)
            for dep in getattr(ctx.rule.attr, "deps", [])
        ],
        "dep_json_paths": [f.path for f in dep_jsons],
        "imports": imports,
        "keep_deps": keep_deps,
        "label": _label_str(target.label),
        "package": target.label.package,
        "src_attr_labels": src_attr_labels,
        "srcs": [
            {
                "is_source": f.is_source,
                "path": f.path,
                "short_path": f.short_path,
            }
            for f in srcs
        ],
    }))

    arguments = [
        "--spec",
        spec.path,
        "--human",
        outputs.human.out.path,
        "--machine",
        outputs.machine.out.path,
    ]
    all_outputs = [outputs.human.out, outputs.machine.out]
    if outputs.human.exit_code and outputs.machine.exit_code:
        # Exit codes land in files so the build succeeds; `bazel lint` reads
        # them. Without them (--fail-on-violation) the checker's own exit
        # code fails the action.
        arguments += [
            "--human-exit-code",
            outputs.human.exit_code.path,
            "--machine-exit-code",
            outputs.machine.exit_code.path,
        ]
        all_outputs += [outputs.human.exit_code, outputs.machine.exit_code]

    # Only source files are action inputs: generated srcs (py_pytest_main
    # outputs, doctest runners) contribute no imports and requesting them
    # would force building their generators.
    ctx.actions.run(
        inputs = [spec] + dep_jsons + [f for f in srcs if f.is_source],
        outputs = all_outputs,
        executable = ctx.executable._checker,
        arguments = arguments,
        mnemonic = _MNEMONIC,
        progress_message = "Checking deps of %{label} with deballast",
    )

    return [DeballastInfo(dep_json = dep_json), info]

def lint_deballast_aspect(binary):
    return aspect(
        implementation = _deballast_aspect_impl,
        attr_aspects = ["deps"],
        attrs = {
            "_checker": attr.label(
                default = binary,
                executable = True,
                cfg = "exec",
            ),
            "_options": attr.label(default = "@aspect_rules_lint//lint:options"),
        },
    )
