load("@rules_pkg//pkg:pkg.bzl", "pkg_tar")
load("@rules_pkg//pkg:mappings.bzl", "pkg_files")


def score_pkg_bundle(name, bins, config_data= None, package_dir = None, other_package_files = []):
    """Creates a reusable bundle: pkg_files → pkg_tar → untar"""

    all_files_name = name + "_pkg_files"
    bundle_name = name + "_pkg_tar"
    all_cfg = name + "_configs"
    untar_name = name

    rename_dict = {}
    for s in bins:
        rename_dict[s] = "bin/" + Label(s).name

    if config_data != None:
        for s in config_data:
            rename_dict[s] = "configs/" + Label(s).name

    config_data_arr = []
    if config_data != None:
        config_data_arr = config_data

    # Step 1: pkg_files
    pkg_files(
        name = all_files_name,
        srcs = bins + config_data_arr,
        renames = rename_dict,
        visibility = ["//visibility:public"],
    )

    # Step 2: pkg_tar
    pkg_tar(
        name = bundle_name,
        srcs = [":" + all_files_name] + other_package_files,
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