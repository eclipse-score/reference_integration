# reference_integration
Score project integration repository



working:

bazel build --config bl-x86_64-linux  @score-baselibs//score/... --verbose_failures

bazel build @communication//score/... @communication//third_party/...
# score/mw/com/requirements is causing problems when building from a different repo
- BUILD files contain "@//third_party instead of "//third_party
- runtime_test.cpp:get_path is not checking external/communication+/ instead it is checking safe_posix_platform (old module name?)

bazel build \
    @score_persistency//src/... \
    @score_persistency//tests/cpp_test_scenarios/... \
    @score_persistency//tests/rust_test_scenarios/... \
    --extra_toolchains=@llvm_toolchain//:cc-toolchain-x86_64-linux \
    --copt=-Wno-deprecated-declarations
# The Python tests cannot be built from the integration workspace due to Bazel's repository visibility design. This is a fundamental limitation, not a configuration issue. The pip extension and Python dependencies must be accessed from within their defining module context. (according to Claude Sonnet 4)

not working:

bazel build @score_persistency//src/cpp/... --extra_toolchains=@llvm_toolchain//:cc-toolchain-x86_64-linux
per is using llvm_toolchain 1.2.0 and baselibs 1.4.0

bazel build @feo//... --verbose_failures
need to install
sudo apt-get install protobuf-compiler
sudo apt-get install libclang-dev

https://github.com/eclipse-score/tooling/blob/main/starpls/starpls.bzl
uses curl, which does not work with proxy (and is bad for dependency tracking)
possible workaround in the script:
    local_path_override(module_name = "score_tooling",path = "../tooling")
            export "http_proxy=http://127.0.0.1:3128"
            export "https_proxy=http://127.0.0.1:3128"
            export "HTTP_PROXY=http://127.0.0.1:3128"
            export "HTTPS_PROXY=http://127.0.0.1:3128"