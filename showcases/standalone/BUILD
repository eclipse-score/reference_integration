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

score_pkg_bundle(
    name = "kyron",
    package_dir = "standalone",
    bins = ["@score_kyron//examples:select", "@score_kyron//examples:safety_task", "@score_kyron//examples:main_macro"],

    config_data = [
        "//showcases/standalone:kyron.score.json",
    ],
)
