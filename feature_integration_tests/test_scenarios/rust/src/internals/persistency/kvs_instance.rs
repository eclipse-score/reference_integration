//! KVS instance test helpers.

use crate::internals::persistency::kvs_parameters::KvsParameters;
use rust_kvs::json_backend::JsonBackendBuilder;
use rust_kvs::prelude::{ErrorCode, Kvs, KvsBuilder};

/// Create KVS instance based on provided parameters.
pub fn kvs_instance(kvs_parameters: KvsParameters) -> Result<Kvs, ErrorCode> {
    let mut builder = KvsBuilder::new(kvs_parameters.instance_id);

    if let Some(flag) = kvs_parameters.defaults {
        builder = builder.defaults(flag);
    }

    if let Some(flag) = kvs_parameters.kvs_load {
        builder = builder.kvs_load(flag);
    }

    if let Some(dir) = kvs_parameters.dir {
        // Use JsonBackendBuilder to configure directory and snapshot_max_count
        // (these methods not available directly on KvsBuilder in Rust)
        // change back to dir, if https://github.com/eclipse-score/persistency/issues/222 is resolved.
        let backend = JsonBackendBuilder::new()
            .working_dir(dir)
            .snapshot_max_count(kvs_parameters.snapshot_max_count.unwrap_or(1))
            .build();
        builder = builder.backend(Box::new(backend));
    } else if let Some(snapshot_max_count) = kvs_parameters.snapshot_max_count {
        // Configure snapshot_max_count via backend
        // change back to snapshot_max_count, if https://github.com/eclipse-score/persistency/issues/222 is resolved.
        let backend = JsonBackendBuilder::new()
            .snapshot_max_count(snapshot_max_count)
            .build();
        builder = builder.backend(Box::new(backend));
    }

    let kvs: Kvs = builder.build()?;

    Ok(kvs)
}
