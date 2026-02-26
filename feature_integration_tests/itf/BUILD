load("@score_itf//:defs.bzl", "py_itf_test")
load("@score_itf//score/itf/plugins:plugins.bzl", "docker", "qemu")


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
    tags = [
        "manual",
    ],
)

py_itf_test(
    name = "qnx_x86_64",
    srcs = [
        ":all_tests",
    ],
    args = [
        "--qemu-config=$(location //feature_integration_tests/configs:qemu_bridge_config.json)",
        "--qemu-image=$(location //images/qnx_x86_64:image)",
    ],
    data = [
        "//feature_integration_tests/configs:qemu_bridge_config.json",
        "//images/qnx_x86_64:image",
    ],
    plugins = [
        qemu,
    ],
    tags = [
        "manual",
    ],
)
