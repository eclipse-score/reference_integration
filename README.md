# reference_integration
Score project integration repository

not working:
bazel build @feo//... --verbose_failures
need to install
sudo apt-get install protobuf-compiler
sudo apt-get install libclang-dev

https://github.com/eclipse-score/tooling/blob/main/starpls/starpls.bzl
uses curl, which does not work with proxy
possible workaround in the script:
    local_path_override(module_name = "score_tooling",path = "../tooling")
            export "http_proxy=http://127.0.0.1:3128"
            export "https_proxy=http://127.0.0.1:3128"
            export "HTTP_PROXY=http://127.0.0.1:3128"
            export "HTTPS_PROXY=http://127.0.0.1:3128"


working:

bazel build --config bl-x86_64-linux  @score-baselibs//score/... --verbose_failures