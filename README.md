# reference_integration
Score project integration repository



working:

bazel build --config bl-x86_64-linux  @score-baselibs//score/... --verbose_failures

bazel build @communication//score/... @communication//third_party/...
# score/mw/com/requirements is causing problems when building from a different repo
- BUILD files contain "@//third_party instead of "//third_party
- runtime_test.cpp:get_path is not checking external/communication+/ instead it is checking safe_posix_platform (old module name?)


not working:
bazel build @communication//... --verbose_failure
The @communication//... wildcard pattern fails due to:

Infinite symlink expansion through bazel-communication/external/ directories
Repository visibility conflicts where external repositories in the symlinked directories expect repositories (like @rules_cc, @trlc_dependencies) that aren't visible in the @@communication+ namespace


bazel build  @score_persistency//...

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