"""Bazel rules for combining multiple Sphinx documentation sets into a unified documentation site."""

load("@rules_pkg//pkg:mappings.bzl", "pkg_files", "strip_prefix")
load("@rules_python//sphinxdocs:sphinx.bzl", "sphinx_build_binary", "sphinx_docs")

def _adapt_path(path):
    """Adapt the file path by removing leading segments such that index.rst has no leading segments."""
    parts = path.split("/")
    if parts[0] == "external":
        # Necessary for files from other Bazel modules
        parts = parts[3:]
    else:
        # Necessary for files in this module
        parts = parts[1:]
    return "/".join(parts)

def _full_docs_impl(ctx):
    """Implementation function for the docs_combo rule.

    This function aggregates multiple documentation targets by creating symlinks
    to their files and generating a top-level index.rst with a table of contents
    that references all subdocumentation.
    """
    # Generate symlinks to dependency documentation
    output = []
    for tgt in ctx.attr.subdocs:
        name = ctx.attr.subdocs[tgt]
        for f in tgt.files.to_list():
            s = ctx.actions.declare_file(name + "/" + _adapt_path(f.path))
            ctx.actions.symlink(output = s, target_file = f)
            print("s.path: " + s.path + " f.path: " + f.path)
            output.append(s)

    # Generate index with toctree
    index = ctx.actions.declare_file("index.rst")
    contents = ""
    contents += "All of S-CORE\n"
    contents += "=============\n\n"
    contents += ".. toctree::\n"
    contents += "   :maxdepth: 2\n\n"
    for tgt in ctx.attr.subdocs:
        name = ctx.attr.subdocs[tgt]
        contents += "   " + name + "/index\n"
    contents += "\nThis overview document is automatically generated.\n"
    ctx.actions.write(output = index, content = contents)
    output.append(index)

    return [DefaultInfo(files = depset(output))]


docs_combo = rule(
    implementation = _full_docs_impl,
    attrs = {
        "subdocs": attr.label_keyed_string_dict(
            doc = "Dictionary mapping documentation targets to their display names",
            default = {},
        ),
    },
)


def all_docs(subdocs = {}, conf = "full_docs/conf.py"):
    """Macro to create a complete documentation build combining multiple doc sources."""
    docs_combo(
        name = "all_docs",
        subdocs = subdocs,
    )
    sphinx_docs(
        name = "full_html",
        srcs = [":all_docs"],
        config = conf,
        extra_opts = [
            #"-W",
            "--keep-going",
            "-T",  # show more details in case of errors
            "--jobs",
            "auto",
        ],
        formats = ["html"],
        sphinx = ":sphinx_build",
        strip_prefix = "full_docs/",
        visibility = ["//visibility:public"],
    )
