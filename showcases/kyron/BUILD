load("@rules_rust//rust:defs.bzl", "rust_binary")
load("//bazel_common:bundlers.bzl", "score_pkg_bundle")

rust_binary(
    name = "kyron_example",
    srcs = ["main.rs"],
    deps = [
        "@score_kyron//src/kyron:libkyron",
        "@score_kyron//src/kyron-foundation:libkyron_foundation",
        "@score_crates//:tracing_subscriber",
    ],
    visibility = ["//visibility:public"],
)


score_pkg_bundle(
    name = "kyron",
    bins = [":kyron_example"],
    config_data = ["//showcases/kyron:kyron.score.json"],
)
