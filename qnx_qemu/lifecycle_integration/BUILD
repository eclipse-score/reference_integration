load("@rules_cc//cc:cc_library.bzl", "cc_library")

genrule(
    name = "generate_launch_manager_config",
    srcs = ["@score_lifecycle_health//src/launch_manager_daemon:lm_flatcfg_fbs", ":launch_manager_config"],
    outs = ["lm_demo.bin"],
    tools = ["@flatbuffers//:flatc"],
    cmd = "$(location @flatbuffers//:flatc) --binary $(SRCS) && mv lm_demo.bin $(location lm_demo.bin)",
    visibility = ["//visibility:public"],
)

genrule(
    name = "generate_launch_manager_health_config",
    srcs = ["@score_lifecycle_health//src/launch_manager_daemon/health_monitor_lib:hm_flatcfg_fbs", ":launch_manager_health_config"],
    outs = ["hm_demo.bin"],
    tools = ["@flatbuffers//:flatc"],
    cmd = "$(location @flatbuffers//:flatc) --binary $(SRCS) && mv hm_demo.bin $(location hm_demo.bin)",
    visibility = ["//visibility:public"],
)

genrule(
    name = "generate_supervised_app_health_config",
    srcs = ["@score_lifecycle_health//src/launch_manager_daemon/health_monitor_lib:hm_flatcfg_fbs", ":supervised_app_health_config"],
    outs = ["supervised_app_demo.bin"],
    tools = ["@flatbuffers//:flatc"],
    cmd = "$(location @flatbuffers//:flatc) --binary $(SRCS) && mv supervised_app_demo.bin $(location supervised_app_demo.bin)",
    visibility = ["//visibility:public"],
)

filegroup(
    name = "lifecycle_start",
    srcs = ["start.sh"],
    visibility = ["//visibility:public"]
)

filegroup(
    name = "launch_manager_config",
    srcs = ["lm_demo.json"],
    visibility = ["//visibility:public"]
)

filegroup(
    name = "launch_manager_health_config",
    srcs = ["hm_demo.json"],
    visibility = ["//visibility:public"]
)

filegroup(
    name = "supervised_app_health_config",
    srcs = ["supervised_app_demo.json"],
    visibility = ["//visibility:public"]
)
