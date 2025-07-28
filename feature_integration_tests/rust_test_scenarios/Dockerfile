FROM rust:latest

RUN apt-get update && apt-get install -y \
    protobuf-compiler \
    libclang-dev 

WORKDIR /app

COPY ./Cargo.lock ./Cargo.toml ./

COPY ./test_data ./test_data
COPY ./src ./src

RUN cargo build

CMD ["./target/debug/rust_test_scenarios", "--help"]
