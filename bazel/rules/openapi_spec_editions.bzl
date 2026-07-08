"""Repository rule detecting which per-edition OpenAPI spec generator packages exist.

CI strips edition directories before bazel runs (versioning.groovy
REPO_PATCH_RULES), so the set of buildable generators varies per checkout.
"""

_OPENAPI_SPEC_EDITION_PACKAGES = [
    ("community", "cmk/gui/openapi/spec/editions/community"),
    ("pro", "cmk/gui/openapi/spec/editions/nonfree/pro"),
    ("cloud", "cmk/gui/openapi/spec/editions/nonfree/cloud"),
    ("ultimate", "cmk/gui/openapi/spec/editions/nonfree/ultimate"),
    ("ultimatemt", "cmk/gui/openapi/spec/editions/nonfree/ultimatemt"),
]

def _detect_openapi_spec_editions_impl(repository_ctx):
    # A Label() into a stripped package would fail to resolve.
    repo_root = repository_ctx.path(Label("//:MODULE.bazel")).dirname
    generators = {}
    for edition, package in _OPENAPI_SPEC_EDITION_PACKAGES:
        build_file = repo_root.get_child(package).get_child("BUILD")
        repository_ctx.watch(build_file)
        if build_file.exists:
            generators[edition] = "//" + package + ":generate_api_spec"
    repository_ctx.file(
        "editions.bzl",
        content = "OPENAPI_SPEC_EDITION_GENERATORS = %r" % generators,
        executable = False,
    )
    repository_ctx.file("BUILD.bazel", 'exports_files(["editions.bzl"])')

detect_openapi_spec_editions = repository_rule(
    implementation = _detect_openapi_spec_editions_impl,
    doc = "Detects which edition-specific OpenAPI spec generators are available",
)
