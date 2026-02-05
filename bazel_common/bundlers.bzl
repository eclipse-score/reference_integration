load("@rules_pkg//pkg:pkg.bzl", "pkg_tar")
load("@rules_pkg//pkg:mappings.bzl", "pkg_files")

def pkg_bundle(name, bins, package_dir):
    """Creates a reusable bundle: pkg_files → pkg_tar → untar"""

    all_files_name = name + "_all_files"
    bundle_name = name + "_tar"
    untar_name = name

    rename_bin_dict = {}
    for s in bins:
        # Extract last path component of label as filename
        # e.g. @score_scrample//src:scrample → scrample
        target_name = s.split(":")[-1]
        rename_bin_dict[s] = "bin/" + target_name

    # Step 1: pkg_files
    pkg_files(
        name = all_files_name,
        srcs = bins,
        renames = rename_bin_dict,
    )

    # Step 2: pkg_tar
    pkg_tar(
        name = bundle_name,
        srcs = [":" + all_files_name],
        strip_prefix = "/",
        package_dir = package_dir,
        visibility = ["//visibility:public"],
    )

    # Step 3: untar
    untar(
        name = untar_name,
        src = ":" + bundle_name,
        visibility = ["//visibility:public"],
    )

    # Return the main targets
    return {
        "all_files": ":" + all_files_name,
        "tar": ":" + bundle_name,
        "tree": ":" + untar_name,
    }


def _untar_impl(ctx):
    out = ctx.actions.declare_directory(ctx.label.name)

    ctx.actions.run(
        inputs = [ctx.file.src],
        outputs = [out],
        executable = "tar",
        arguments = ["-xf", ctx.file.src.path, "-C", out.path],
    )

    return [DefaultInfo(files = depset([out]))]

untar = rule(
    implementation = _untar_impl,
    attrs = {
        "src": attr.label(allow_single_file = True),
    },
)