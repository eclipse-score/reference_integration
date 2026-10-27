// *******************************************************************************
// Copyright (c) 2026 Contributors to the Eclipse Foundation
//
// See the NOTICE file(s) distributed with this work for additional
// information regarding copyright ownership.
//
// This program and the accompanying materials are made available under the
// terms of the Apache License Version 2.0 which is available at
// <https://www.apache.org/licenses/LICENSE-2.0>
//
// SPDX-License-Identifier: Apache-2.0
// *******************************************************************************
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

// Demonstrates score_kyron and score_logging integration: async tasks run on
// the kyron runtime and emit structured log messages via score's logging
// framework throughout their lifecycle.

use kyron::futures::sleep::sleep;
use score_log as log;
use stdout_logger::StdoutLoggerBuilder;

#[kyron::main]
async fn main() {
    StdoutLoggerBuilder::new()
        .show_module(false)
        .show_file(false)
        .show_line(false)
        .set_as_default_logger();

    log::info!("Kyron async runtime started with structured logging");

    let handles: Vec<_> = (0u32..4)
        .map(|i| {
            kyron::spawn(async move {
                log::info!("Async task {} started on kyron runtime", i);
                sleep(core::time::Duration::from_millis(300)).await;
                log::info!("Async task {} completed", i);
            })
        })
        .collect();

    for handle in handles {
        handle.await.expect("async task panicked");
    }

    log::info!("All async tasks completed — kyron runtime shutting down");
}
