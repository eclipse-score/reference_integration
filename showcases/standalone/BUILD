load("//bazel_common:bundlers.bzl", "score_pkg_bundle")

score_pkg_bundle(
    name = "comm",
    bins = ["@score_communication//score/mw/com/example/ipc_bridge:ipc_bridge_cpp"],
    config_data = [
        "//showcases/standalone:com.score.json",
    ],
    custom_layout = {
        "@score_communication//score/mw/com/example/ipc_bridge:etc/mw_com_config.json": "etc/mw_com_config.json",
    },
    package_dir = "standalone",
)

score_pkg_bundle(
    name = "kyron",
    bins = [
        "@score_kyron//examples:select",
        "@score_kyron//examples:safety_task",
        "@score_kyron//examples:main_macro",
    ],
    config_data = [
        "//showcases/standalone:kyron.score.json",
    ],
    package_dir = "standalone",
)
