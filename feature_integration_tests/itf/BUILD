load("@score_itf//:defs.bzl", "py_itf_test")
load("@score_itf//score/itf/plugins:plugins.bzl", "docker")


filegroup(
    name = "all_tests",
    srcs = [
        "test_showcases.py",
        "test_ssh.py",
    ],
    visibility = [
        "//images/qnx_x86_64:__pkg__",
    ],
)

py_itf_test(
    name = "linux_x86_64",
    srcs = [
        ":all_tests",
    ],
    args = [
        "--docker-image-bootstrap=$(location //images/linux_x86_64:docker_image_tarball)",
        "--docker-image=score_showcases:latest",
    ],
    data = [
        "//images/linux_x86_64:docker_image_tarball",
    ],
    plugins = [
        docker,
    ],
)
