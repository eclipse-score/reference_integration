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

//! Standalone *consumer* for the communication feature integration tests.
//!
//! It discovers the `VehicleInterface` service instance offered by `fit_sender`
//! (retrying, so start order does not matter), subscribes to `left_tire`, and
//! prints each received sequence number as `FIT_RECV seq=<n>`. Because the
//! sender encodes a monotonically increasing counter in the payload, the ITF
//! can assert on this output that delivery happened, that samples arrived in
//! order, and that their values were not corrupted -- all from data the
//! consumer actually observed.
//!
//! Exit code: 0 when it received the requested number of samples, 1 otherwise
//! (so a delivery regression surfaces as a non-zero exit, not a silent
//! under-count).

use std::path::{Path, PathBuf};
use std::thread::sleep;
use std::time::Duration;

use com_api::{
    Builder, FindServiceSpecifier, InstanceSpecifier, LolaRuntimeBuilderImpl, LolaRuntimeImpl, Runtime, RuntimeBuilder,
    SampleContainer, ServiceDiscovery, Subscriber, Subscription,
};
use com_api_gen::VehicleInterface;

/// Default instance specifier, matching com-api-example's deployment manifest.
/// Overridable via `-i` so tests can target a dedicated (e.g. ASIL-B) instance
/// without disturbing the default exchange scenario.
const DEFAULT_INSTANCE_SPECIFIER: &str = "/Vehicle/Service1/Instance";

struct Arguments {
    /// Deployment manifest read at runtime (feat_req__com__depl_config_runtime).
    service_instance_manifest: PathBuf,
    /// Number of samples to receive before exiting successfully.
    cycles: u32,
    /// Poll interval in milliseconds (discovery retry and receive loop).
    interval_ms: u64,
    /// Maximum number of poll iterations before giving up (bounds the run).
    max_polls: u32,
    /// Service instance specifier to subscribe to.
    instance_specifier: String,
}

fn parse_args() -> Arguments {
    let mut manifest = PathBuf::from("./etc/mw_com_config.json");
    let mut cycles: u32 = 10;
    let mut interval_ms: u64 = 100;
    let mut max_polls: u32 = 100;
    let mut instance_specifier = DEFAULT_INSTANCE_SPECIFIER.to_string();

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
            "--max-polls" => {
                i += 1;
                max_polls = argv
                    .get(i)
                    .expect("missing value for --max-polls")
                    .parse()
                    .expect("invalid --max-polls");
            },
            "-i" | "--instance-specifier" => {
                i += 1;
                instance_specifier = argv.get(i).expect("missing value for -i").clone();
            },
            other => eprintln!("FIT_RECV_IGNORED_ARG {other}"),
        }
        i += 1;
    }

    Arguments {
        service_instance_manifest: manifest,
        cycles,
        interval_ms,
        max_polls,
        instance_specifier,
    }
}

fn init_lola_runtime(config_path: &Path) -> LolaRuntimeImpl {
    let mut builder = LolaRuntimeBuilderImpl::new();
    if config_path.exists() {
        builder.load_config(config_path);
    } else {
        eprintln!("FIT_RECV_CONFIG_MISSING path={}", config_path.display());
    }
    builder.build().expect("Failed to build Lola runtime")
}

/// Discover and build the consumer, retrying so start order does not matter.
fn discover_consumer(
    runtime: &LolaRuntimeImpl,
    service_id: &InstanceSpecifier,
    retries: u32,
    interval_ms: u64,
) -> Option<<VehicleInterface as com_api::Interface>::Consumer<LolaRuntimeImpl>> {
    for _ in 0..retries {
        let discovery = runtime.find_service::<VehicleInterface>(FindServiceSpecifier::Specific(service_id.clone()));
        if let Ok(instances) = discovery.get_available_instances() {
            if let Some(builder) = instances.into_iter().next() {
                return builder.build().ok();
            }
        }
        sleep(Duration::from_millis(interval_ms));
    }
    None
}

fn main() {
    let args = parse_args();
    let runtime = init_lola_runtime(&args.service_instance_manifest);

    let service_id = InstanceSpecifier::new(&args.instance_specifier).expect("Failed to create InstanceSpecifier");

    let consumer = match discover_consumer(&runtime, &service_id, args.max_polls, args.interval_ms) {
        Some(consumer) => consumer,
        None => {
            eprintln!("FIT_RECV_NO_SERVICE");
            std::process::exit(1);
        },
    };
    println!("FIT_FOUND_SERVICE");

    let subscription = consumer
        .left_tire
        .subscribe(args.cycles as usize)
        .expect("Failed to subscribe");

    let mut received: u32 = 0;
    let mut buffer = SampleContainer::new(args.cycles as usize);
    for _ in 0..args.max_polls {
        if received >= args.cycles {
            break;
        }
        match subscription.try_receive(&mut buffer, args.cycles as usize) {
            Ok(0) => sleep(Duration::from_millis(args.interval_ms)),
            Ok(_) => {
                while let Some(sample) = buffer.pop_front() {
                    // Sequence number was encoded in the payload by fit_sender;
                    // the sample derefs to the generated Tire type.
                    let pressure = sample.pressure;
                    println!("FIT_RECV seq={}", pressure as i64);
                    received += 1;
                }
            },
            Err(error) => eprintln!("FIT_RECV_ERROR {error:?}"),
        }
    }

    let _ = subscription.unsubscribe();

    if received >= args.cycles {
        println!("FIT_RECV_DONE count={received}");
    } else {
        eprintln!("FIT_RECV_INCOMPLETE count={received} expected={}", args.cycles);
        std::process::exit(1);
    }
}
