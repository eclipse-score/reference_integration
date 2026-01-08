use crate::internals::persistency::{kvs_instance::kvs_instance, kvs_parameters::KvsParameters};
use rust_kvs::prelude::KvsApi;
use serde::Deserialize;
use serde_json::Value;
use test_scenarios_rust::scenario::Scenario;
use tracing::{field, info};

#[derive(Deserialize, Debug)]
pub struct TestInput {
    pub key: String,
    pub value_1: f64,
    pub value_2: f64,
}

impl TestInput {
    /// Parse `TestInput` from JSON string.
    /// JSON is expected to contain `test` field.
    pub fn from_json(json_str: &str) -> Result<Self, serde_json::Error> {
        let v: Value = serde_json::from_str(json_str)?;
        serde_json::from_value(v["test"].clone())
    }
}

pub struct MultipleKvsPerApp;

impl Scenario for MultipleKvsPerApp {
    fn name(&self) -> &str {
        "multiple_kvs_per_app"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        // Parameters.
        let v: Value = serde_json::from_str(input).expect("Failed to parse input string");
        let params1 =
            KvsParameters::from_value(&v["kvs_parameters_1"]).expect("Failed to parse parameters");
        let params2 =
            KvsParameters::from_value(&v["kvs_parameters_2"]).expect("Failed to parse parameters");
        let logic = TestInput::from_json(input).expect("Failed to parse input string");
        {
            // Create first KVS instance.
            let kvs1 = kvs_instance(params1.clone()).expect("Failed to create KVS instance");

            // Create second KVS instance.
            let kvs2 = kvs_instance(params2.clone()).expect("Failed to create KVS instance");

            // Set values to both KVS instances.
            kvs1.set_value(&logic.key, logic.value_1)
                .expect("Failed to set kvs1 value");
            kvs2.set_value(&logic.key, logic.value_2)
                .expect("Failed to set kvs2 value");

            // Flush KVS.
            kvs1.flush().expect("Failed to flush first instance");
            kvs2.flush().expect("Failed to flush second instance");
        }

        {
            // Second KVS run.
            let kvs1 = kvs_instance(params1).expect("Failed to create KVS1 instance");
            let kvs2 = kvs_instance(params2).expect("Failed to create KVS2 instance");

            let value1 = kvs1
                .get_value_as::<f64>(&logic.key)
                .expect("Failed to read kvs1 value");
            info!(
                instance = field::debug(kvs1.parameters().instance_id),
                key = logic.key,
                value = value1
            );
            let value2 = kvs2
                .get_value_as::<f64>(&logic.key)
                .expect("Failed to read kvs2 value");
            info!(
                instance = field::debug(kvs2.parameters().instance_id),
                key = logic.key,
                value = value2
            );
        }

        Ok(())
    }
}
