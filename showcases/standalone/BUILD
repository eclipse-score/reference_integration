load("//bazel_common:bundlers.bzl", "score_pkg_bundle")


score_pkg_bundle(
    name = "comm",
    package_dir = "standalone",
    bins = ["@score_communication//score/mw/com/example/ipc_bridge:ipc_bridge_cpp"],
    custom_layout = {
        "@score_communication//score/mw/com/example/ipc_bridge:etc/mw_com_config.json": "etc/mw_com_config.json"
    },
    config_data = [
        "//showcases/standalone:com.score.json",
    ],
)
