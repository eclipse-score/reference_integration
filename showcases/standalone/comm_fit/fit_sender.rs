/********************************************************************************
 * Copyright (c) 2026 Contributors to the Eclipse Foundation
 *
 * See the NOTICE file(s) distributed with this work for additional
 * information regarding copyright ownership.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Apache License Version 2.0 which is available at
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * SPDX-License-Identifier: Apache-2.0
 ********************************************************************************/

//! Standalone *producer* for the communication feature integration tests.
//!
//! It offers the `VehicleInterface` service instance and publishes `left_tire`
//! samples whose `pressure` field carries a monotonically increasing sequence
//! number (0, 1, 2, ...). Running the sender and `fit_receiver` as two separate
//! OS processes over real shared memory lets the ITF assert delivery, ordering
//! and value-integrity on the data the consumer actually observes, rather than
//! on strings the app prints about itself.
//!
//! Kept deliberately close to `com-api-example` (score/mw/com) so it tracks the
//! same public `com_api` surface BMW ships. Arguments are parsed with `std`
//! (no `clap`) to avoid depending on the communication module's crate index.
//!
//! Usage: `fit_sender [-s <manifest>] [-n <cycles>] [-t <interval_ms>]`

use std::path::{Path, PathBuf};
use std::thread::sleep;
use std::time::Duration;

use com_api::{
    Builder, InstanceSpecifier, LolaRuntimeBuilderImpl, LolaRuntimeImpl, Producer, Publisher, Runtime, RuntimeBuilder,
    SampleMaybeUninit, SampleMut,
};
use com_api_gen::{Tire, VehicleInterface};

/// Same instance specifier as com-api-example's deployment manifest.
const INSTANCE_SPECIFIER: &str = "/Vehicle/Service1/Instance";

struct Arguments {
    /// Deployment manifest read at runtime (feat_req__com__depl_config_runtime).
    service_instance_manifest: PathBuf,
    /// Number of samples to send.
    cycles: u32,
    /// Delay between samples in milliseconds.
    interval_ms: u64,
}

fn parse_args() -> Arguments {
    let mut manifest = PathBuf::from("./etc/mw_com_config.json");
    let mut cycles: u32 = 50;
    let mut interval_ms: u64 = 100;

    let argv: Vec<String> = std::env::args().collect();
    let mut i = 1;
    while i < argv.len() {
        match argv[i].as_str() {
            "-s" | "--service-instance-manifest" => {
                i += 1;
                manifest = PathBuf::from(argv.get(i).expect("missing value for -s"));
            },
            "-n" | "--cycles" => {
                i += 1;
                cycles = argv
                    .get(i)
                    .expect("missing value for -n")
                    .parse()
                    .expect("invalid -n/--cycles");
            },
            "-t" | "--interval-ms" => {
                i += 1;
                interval_ms = argv
                    .get(i)
                    .expect("missing value for -t")
                    .parse()
                    .expect("invalid -t/--interval-ms");
            },
            other => eprintln!("FIT_SEND_IGNORED_ARG {other}"),
        }
        i += 1;
    }

    Arguments {
        service_instance_manifest: manifest,
        cycles,
        interval_ms,
    }
}

fn init_lola_runtime(config_path: &Path) -> LolaRuntimeImpl {
    let mut builder = LolaRuntimeBuilderImpl::new();
    if config_path.exists() {
        builder.load_config(config_path);
    } else {
        eprintln!("FIT_SEND_CONFIG_MISSING path={}", config_path.display());
    }
    builder.build().expect("Failed to build Lola runtime")
}

fn main() {
    let args = parse_args();
    let runtime = init_lola_runtime(&args.service_instance_manifest);

    let service_id = InstanceSpecifier::new(INSTANCE_SPECIFIER).expect("Failed to create InstanceSpecifier");
    let producer = runtime
        .producer_builder::<VehicleInterface>(service_id)
        .build()
        .expect("Failed to build producer instance");
    let offered = producer.offer().expect("Failed to offer producer instance");
    println!("FIT_SEND_OFFERED");

    for seq in 0..args.cycles {
        let uninit_sample = offered.left_tire.allocate().expect("Failed to allocate sample");
        // Encode the sequence number in the payload so the receiver can verify
        // ordering and value-integrity independently of anything printed here.
        let sample = uninit_sample.write(Tire { pressure: seq as f32 });
        sample.send().expect("Failed to send sample");
        println!("FIT_SEND seq={seq}");
        sleep(Duration::from_millis(args.interval_ms));
    }

    println!("FIT_SEND_DONE count={}", args.cycles);
}
