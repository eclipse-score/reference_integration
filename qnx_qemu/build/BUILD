load("@score_toolchains_qnx//rules/fs:ifs.bzl", "qnx_ifs")


qnx_ifs(
    name = "init",
    build_file = "init.build",
    srcs = [
        "system.build",
    ],
    visibility = [
        "//:__pkg__"
    ],
)