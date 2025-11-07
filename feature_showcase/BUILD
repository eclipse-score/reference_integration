filegroup(
    name = "all_examples",
    srcs = [
        "//feature_showcase/rust:kyron_example",
        "//feature_showcase/rust:orch_per_example",
    ],
)



genrule(
    name = "build_all",
    srcs = [
        "//feature_showcase/rust:kyron_example",
        "//feature_showcase/rust:orch_per_example",
    ],
    outs = ["done.txt"],
    cmd = "echo built > $@",
)