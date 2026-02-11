load("@rules_pkg//pkg:pkg.bzl", "pkg_tar")
load("@rules_pkg//pkg:mappings.bzl", "pkg_files")


def score_pkg_bundle(name, bins, config_data= None, package_dir = None, other_package_files = [], custom_layout = {}):
    """
    Creates a reusable bundle by chaining Bazel packaging rules:
      - Collects binaries and config files into a pkg_files target, renaming them into subdirectories.
      - Packs them into a tar archive using pkg_tar, optionally with additional package files and a custom package directory.
      - Extracts the tar archive using a custom untar rule.
    Why:
       - Group related binaries and config files into a single package for distribution or deployment.
       - Group files from multiple targets into one package so deploying them into image is easy, consistent and same for each image.
    Args:
        name: Base name for all generated targets.
        bins: List of binary file labels to include in the bundle (placed in 'bin/').
        config_data: Optional list of config file labels to include (placed in 'configs/').
        package_dir: Optional directory path for the package root inside the tar archive.
        other_package_files: Optional list of additional `NAME_pkg_files` to include in the tar archive that was created by other `score_pkg_bundle` targets.
        custom_layout: Optional dict mapping labels -> destination path inside the package. All destination will be prefixed with "data/NAME/".
            Example:
                custom_layout = {
                    "//app:data.txt": "resources/data.txt",
                    "//lib:helper.sh": "scripts/helper.sh",
                }
    """

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


    if custom_layout == None:
        custom_layout = {}

    for label, dst in custom_layout.items():
        rename_dict[label] = "data/" + name + "/" + dst
    
    # Step 1: pkg_files
    pkg_files(
        name = all_files_name,
        srcs = bins + config_data_arr  + list(custom_layout.keys()),
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