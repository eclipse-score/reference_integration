use async_runtime::runtime::async_runtime::{AsyncRuntime, AsyncRuntimeBuilder};
use async_runtime::scheduler::execution_engine::ExecutionEngineBuilder;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use tracing::debug;

/// Execution engine configuration.
#[derive(Serialize, Deserialize, Debug)]
pub struct ExecEngineConfig {
    task_queue_size: u32,
    workers: usize,
    thread_priority: Option<u8>,
    thread_affinity: Option<usize>,
    thread_stack_size: Option<u64>,
}

/// Runtime configuration.
/// Used by serde for serialization.
#[derive(Serialize, Deserialize, Debug)]
#[serde(untagged)]
enum RuntimeConfig {
    /// Single engine is defined.
    Object(ExecEngineConfig),
    /// List of engines is defined.
    Array(Vec<ExecEngineConfig>),
}

#[derive(Debug)]
pub struct Runtime {
    exec_engines: Vec<ExecEngineConfig>,
}

impl Runtime {
    pub fn new(inputs: &Option<String>) -> Self {
        let v: Value = serde_json::from_str(inputs.as_deref().unwrap()).unwrap();
        let runtime_config: RuntimeConfig = serde_json::from_value(v["runtime"].clone()).unwrap();
        let exec_engines = match runtime_config {
            RuntimeConfig::Object(cfg) => vec![cfg],
            RuntimeConfig::Array(cfgs) => cfgs,
        };

        Self { exec_engines }
    }

    pub fn build(&self) -> AsyncRuntime {
        debug!("Creating AsyncRuntime with {} execution engines", self.exec_engines.len());

        let mut async_rt_builder = AsyncRuntimeBuilder::new();
        for exec_engine in self.exec_engines.as_slice() {
            debug!("Creating ExecutionEngine with: {:?}", exec_engine);

            let mut exec_engine_builder = ExecutionEngineBuilder::new()
                .task_queue_size(exec_engine.task_queue_size)
                .workers(exec_engine.workers);
            if let Some(thread_priority) = exec_engine.thread_priority {
                exec_engine_builder = exec_engine_builder.thread_priority(thread_priority);
            }
            if let Some(thread_affinity) = exec_engine.thread_affinity {
                exec_engine_builder = exec_engine_builder.thread_affinity(thread_affinity);
            }
            if let Some(thread_stack_size) = exec_engine.thread_stack_size {
                exec_engine_builder = exec_engine_builder.thread_stack_size(thread_stack_size);
            }

            let (builder, _) = async_rt_builder.with_engine(exec_engine_builder);
            async_rt_builder = builder;
        }

        async_rt_builder.build().unwrap()
    }
}
