//
// Copyright (c) 2025 Contributors to the Eclipse Foundation
//
// See the NOTICE file(s) distributed with this work for additional
// information regarding copyright ownership.
//
// This program and the accompanying materials are made available under the
// terms of the Apache License Version 2.0 which is available at
// <https://www.apache.org/licenses/LICENSE-2.0>
//
// SPDX-License-Identifier: Apache-2.0
//

use kyron::channels::spsc::*;
use kyron::spawn;
use kyron_foundation::prelude::*;

/// Example entry point demonstrating the usage of the kyron async runtime
///
/// This example shows how to set up a Kyron async runtime with default engine parameters.
/// It spawns a sender and receiver task using Kyron's channel and spawn utilities.
/// Useful for learning how to structure Kyron async applications and macro usage.
/// For more visit https://github.com/eclipse-score/orchestrator
#[kyron::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_target(false)
        .with_max_level(Level::INFO)
        .init();

    let (sender, mut receiver) = create_channel_default::<u32>();

    let r = spawn(async move {
        while let Some(value) = receiver.recv().await {
            info!("Received {}", value);
        }
    });

    let s = spawn(async move {
        info!("Hello from Kyron sender!");

        for i in 0..5_u32 {
            info!("Sending {}", i);
            sender.send(&i).unwrap();
        }
    });

    s.await.unwrap();
    r.await.unwrap();
}
