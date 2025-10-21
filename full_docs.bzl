
load("@rules_pkg//pkg:mappings.bzl", "pkg_files", "strip_prefix")
load("@rules_python//sphinxdocs:sphinx.bzl", "sphinx_build_binary", "sphinx_docs")

def _drop_path(path, prefix_count):
    parts = path.split("/")
    if len(parts) <= prefix_count:
        return ""
    return "/".join(parts[prefix_count:])

def _full_docs_impl(ctx):
    # Generate symlinks to dependency documentation
    output = []
    for tgt in ctx.attr.subdocs:
        name = ctx.attr.subdocs[tgt]
        for f in tgt.files.to_list():
            s = ctx.actions.declare_file(name + "/" + _drop_path(f.path,3))
            ctx.actions.symlink(output = s, target_file = f)
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
    ctx.actions.write(output = index, content = contents)
    output.append(index)

    return [DefaultInfo(files = depset(output))]


docs_combo = rule(
    implementation = _full_docs_impl,
    attrs = {
        "subdocs": attr.label_keyed_string_dict(default = {}),
    },
)


def all_docs(subdocs ={}):
    docs_combo(
        name = "all_docs",
        subdocs = subdocs,
    )
    sphinx_docs(
        name = "full_html",
        srcs = [":all_docs"],
        config = "docs/conf.py",
        extra_opts = [
            #"-W",
            "--keep-going",
            "-T",  # show more details in case of errors
            "--jobs",
            "auto",
        ],
        formats = ["html"],
        sphinx = ":sphinx_build",
        strip_prefix = "docs/",
        visibility = ["//visibility:public"],
    )
