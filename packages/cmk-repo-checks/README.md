# cmk-repo-checks

First-party checkers that enforce conventions of this repository itself.
The tools in this package analyze the repo's source and `BUILD` files rather than shipping as part of the product.

New checkers should be added as modules under `cmk/repo_checks/` with their own targets and tests under `tests/`.

## deballast

Reports over-declared Bazel `py_*` `deps` via AST-level src-vs-dep analysis.
It is implemented as a Bazel aspect (`deballast.bzl`): applied to a `py_library`/`py_binary`/`py_test` target, it runs one checker action per target that parses the target's own `srcs` for imports and flags declared deps whose direct `srcs` provide no imported module.
Results are cached per target and re-checked incrementally — only targets whose own `srcs` or whose deps' interfaces changed are re-analyzed.
It only inspects direct `srcs` of deps (not the transitive closure) and does not detect missing deps.
See the module docstring of `cmk/repo_checks/deballast.py` for the full list of heuristics and implicit-use exemptions.

### Usage

deballast is registered as a linter in `.aspect/cli/config.yaml`, so interactive use is plain `bazel lint`, which prints the findings alongside the other linters:

```console
bazel lint //cmk/gui/wato:wato
bazel lint //cmk/gui/...
```

For CI and scripted consumption, `--config=deballast` materializes the report files per analyzed target in `bazel-bin`:

```console
bazel build --config=deballast //cmk/gui/...
# quick check - human reports are empty when clean:
find bazel-bin -name "*.AspectRulesLintDeballast.out" -size +0c -exec cat {} +
# SARIF for tooling:
find bazel-bin -name "*.AspectRulesLintDeballast.report" -size +0c -exec jq -r '.runs[].results[].message.text' {} +
```

Deps confirmed unused should be removed from the corresponding `BUILD` file; verify with `bazel build`, `bazel lint`, and `bazel build --config=mypy`.

### Exemptions

A dep that is loaded at runtime (plugin discovery, fixtures) rather than imported by name is exempted per edge with a tag on the consuming target; the reason stays next to it as a comment:

```starlark
tags = ["deballast-keep=//cmk/base/modes:modes"],  # loaded at runtime via discover_modes()
```

A target whose deps are all runtime-loaded (e.g. sphinx autodoc builds) opts out entirely with `tags = ["no-deballast"]`; the generic `no-lint` tag is honored, too.
A `deballast-keep` tag that names no declared dep is reported as stale, so exemptions cannot outlive the dep they exempt.

### Development

```console
# Run the tests
bazel test //packages/cmk-repo-checks:test

# Format, lint, type-check
bazel run //:format packages/cmk-repo-checks
bazel lint //packages/cmk-repo-checks:all
bazel build --config=mypy //packages/cmk-repo-checks:all
```
