load("@rules_cc//cc:cc_library.bzl", "cc_library")
load("//bazel_common:bundlers.bzl", "score_pkg_bundle")

score_pkg_bundle(
    name = "simple_lifecycle",
    bins = [
        "@score_lifecycle_health//src/launch_manager_daemon:launch_manager",
        "@score_lifecycle_health//examples/cpp_supervised_app",
        "@score_lifecycle_health//examples/rust_supervised_app",
        "@score_lifecycle_health//examples/control_application:control_daemon",
        ":lifecycle_demo.sh"
    ],
    config_data = [
        "//showcases/simple_lifecycle:simple_lifecycle.score.json",
    ],

    custom_layout = {
        ":lm_demo.bin": "etc/lm_demo.bin",
        ":hm_demo.bin": "etc/hm_demo.bin",
        ":cpp_supervised_app_demo.bin": "etc/cpp_supervised_app_demo.bin",
        ":rust_supervised_app_demo.bin": "etc/rust_supervised_app_demo.bin",
    },
)

genrule(
    name = "gen_lm_demo.bin",
    srcs = ["@score_lifecycle_health//src/launch_manager_daemon:lm_flatcfg_fbs", "//showcases/simple_lifecycle/configs:lm_demo.json"],
    outs = ["lm_demo.bin"],
    tools = ["@flatbuffers//:flatc"],
    cmd = "$(location @flatbuffers//:flatc) --binary $(SRCS) && mv lm_demo.bin $(location lm_demo.bin)",
    visibility = ["//visibility:public"],
)

genrule(
    name = "gen_hm_demo.bin",
    srcs = ["@score_lifecycle_health//src/launch_manager_daemon/health_monitor_lib:hm_flatcfg_fbs", "//showcases/simple_lifecycle/configs:hm_demo.json"],
    outs = ["hm_demo.bin"],
    tools = ["@flatbuffers//:flatc"],
    cmd = "$(location @flatbuffers//:flatc) --binary $(SRCS) && mv hm_demo.bin $(location hm_demo.bin)",
    visibility = ["//visibility:public"],
)

genrule(
    name = "gen_cpp_supervised_app_demo.bin",
    srcs = ["@score_lifecycle_health//src/launch_manager_daemon/health_monitor_lib:hm_flatcfg_fbs", "//showcases/simple_lifecycle/configs:cpp_supervised_app_demo.json"],
    outs = ["cpp_supervised_app_demo.bin"],
    tools = ["@flatbuffers//:flatc"],
    cmd = "$(location @flatbuffers//:flatc) --binary $(SRCS) && mv cpp_supervised_app_demo.bin $(location cpp_supervised_app_demo.bin)",
    visibility = ["//visibility:public"],
)

genrule(
    name = "gen_rust_supervised_app_demo.bin",
    srcs = ["@score_lifecycle_health//src/launch_manager_daemon/health_monitor_lib:hm_flatcfg_fbs", "//showcases/simple_lifecycle/configs:rust_supervised_app_demo.json"],
    outs = ["rust_supervised_app_demo.bin"],
    tools = ["@flatbuffers//:flatc"],
    cmd = "$(location @flatbuffers//:flatc) --binary $(SRCS) && mv rust_supervised_app_demo.bin $(location rust_supervised_app_demo.bin)",
    visibility = ["//visibility:public"],
)

