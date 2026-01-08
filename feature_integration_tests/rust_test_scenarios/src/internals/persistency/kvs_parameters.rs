//! KVS parameters test helpers.

use rust_kvs::prelude::{InstanceId, KvsDefaults, KvsLoad};
use serde::{de, Deserialize, Deserializer};
use std::path::PathBuf;

/// KVS parameters in serde-compatible format.
#[derive(Deserialize, Debug, Clone)]
#[serde(deny_unknown_fields)]
pub struct KvsParameters {
    #[serde(deserialize_with = "deserialize_instance_id")]
    pub instance_id: InstanceId,
    #[serde(default, deserialize_with = "deserialize_defaults")]
    pub defaults: Option<KvsDefaults>,
    #[serde(default, deserialize_with = "deserialize_kvs_load")]
    pub kvs_load: Option<KvsLoad>,
    pub dir: Option<PathBuf>,
    pub snapshot_max_count: Option<usize>,
}

impl KvsParameters {
    /// Parse `KvsParameters` from `Value`.
    /// `Value` is expected to contain `kvs_parameters` field.
    pub fn from_value(value: &serde_json::Value) -> Result<Self, serde_json::Error> {
        serde_json::from_value(value["kvs_parameters"].clone())
    }
}

fn deserialize_instance_id<'de, D>(deserializer: D) -> Result<InstanceId, D::Error>
where
    D: Deserializer<'de>,
{
    let value = usize::deserialize(deserializer)?;
    Ok(InstanceId(value))
}

fn deserialize_defaults<'de, D>(deserializer: D) -> Result<Option<KvsDefaults>, D::Error>
where
    D: Deserializer<'de>,
{
    let value_opt: Option<String> = Option::deserialize(deserializer)?;
    if let Some(value_str) = value_opt {
        let value = match value_str.as_str() {
            "ignored" => KvsDefaults::Ignored,
            "optional" => KvsDefaults::Optional,
            "required" => KvsDefaults::Required,
            _ => return Err(de::Error::custom("Invalid \"defaults\" mode")),
        };
        return Ok(Some(value));
    }

    Ok(None)
}

fn deserialize_kvs_load<'de, D>(deserializer: D) -> Result<Option<KvsLoad>, D::Error>
where
    D: Deserializer<'de>,
{
    let value_opt: Option<String> = Option::deserialize(deserializer)?;
    if let Some(value_str) = value_opt {
        let value = match value_str.as_str() {
            "ignored" => KvsLoad::Ignored,
            "optional" => KvsLoad::Optional,
            "required" => KvsLoad::Required,
            _ => return Err(de::Error::custom("Invalid \"kvs_load\" mode")),
        };
        return Ok(Some(value));
    }

    Ok(None)
}
