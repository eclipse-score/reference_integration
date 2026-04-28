// *******************************************************************************
// Copyright (c) 2026 Contributors to the Eclipse Foundation
//
// See the NOTICE file(s) distributed with this work for additional
// information regarding copyright ownership.
//
// This program and the accompanying materials are made available under the
// terms of the Apache License Version 2.0 which is available at
// https://www.apache.org/licenses/LICENSE-2.0
//
// SPDX-License-Identifier: Apache-2.0
// *******************************************************************************

#include "../../internals/persistency/kvs_parameters.h"

#include "tracing.hpp"

#include <kvs.hpp>
#include <kvsbuilder.hpp>
#include <scenario.hpp>

#include <cmath>
#include <sstream>
#include <string>
#include <vector>

using namespace score::mw::per::kvs;

namespace {
const std::string kTargetName{
    "cpp_test_scenarios::scenarios::persistency::default_values"};

/// Map C++ KVS library error messages to the Rust-style identifiers used in
/// test assertions, so both implementations produce identical log output.
std::string normalize_error(const std::string &msg) {
  if (msg == "Key not found") {
    return "KeyNotFound";
  }
  if (msg == "KVS file read error") {
    return "KvsFileReadError";
  }
  if (msg == "JSON parser error") {
    return "JsonParserError";
  }
  return msg;
}

std::optional<bool> to_need_flag(const std::optional<KvsDefaults> &mode) {
  if (!mode.has_value()) {
    return std::nullopt;
  }
  if (*mode == KvsDefaults::Required) {
    return true;
  }
  return false;
}

std::optional<bool> to_need_flag(const std::optional<KvsLoad> &mode) {
  if (!mode.has_value()) {
    return std::nullopt;
  }
  if (*mode == KvsLoad::Required) {
    return true;
  }
  return false;
}

Kvs create_kvs(const KvsParameters &params) {
  KvsBuilder builder{score::mw::per::kvs::InstanceId{params.instance_id.value}};

  if (const auto defaults = to_need_flag(params.defaults)) {
    builder = builder.need_defaults_flag(*defaults);
  }
  if (const auto kvs_load = to_need_flag(params.kvs_load)) {
    builder = builder.need_kvs_flag(*kvs_load);
  }
  if (params.dir.has_value()) {
    builder = builder.dir(std::string(*params.dir));
  }

  auto build_result = builder.build();
  if (!build_result) {
    throw std::runtime_error(
        normalize_error(std::string(build_result.error().Message())));
  }

  return std::move(build_result.value());
}

std::string format_f64(double value) {
  std::ostringstream oss;
  oss.precision(1);
  oss << std::fixed << value;
  return oss.str();
}

/// Format score::Result<KvsValue> as a Rust-style debug string.
std::string result_value_to_string(const score::Result<KvsValue> &result) {
  if (result && result.value().getType() == KvsValue::Type::f64) {
    const double value = std::get<double>(result.value().getValue());
    return "Ok(F64(" + format_f64(value) + "))";
  }
  if (!result) {
    return std::string("Err(") +
           normalize_error(std::string(result.error().Message())) + ")";
  }
  return "Err(KeyNotFound)";
}

bool f64_equal(double lhs, double rhs) { return std::fabs(lhs - rhs) <= 1e-5; }

double expect_f64(const score::Result<KvsValue> &result,
                  const std::string &context) {
  if (!result) {
    throw std::runtime_error(context + ": " +
                             std::string(result.error().Message()));
  }
  if (result.value().getType() != KvsValue::Type::f64) {
    throw std::runtime_error(context + ": unexpected value type");
  }
  return std::get<double>(result.value().getValue());
}

/// Compute the Rust-style Result<bool> string for is_value_default using the
/// available has_default_value() + get_default_value() + get_value() APIs.
/// This is a workaround for the pinned commit not having is_value_default().
std::string
value_is_default_string(const score::Result<bool> &has_default_result,
                        const score::Result<KvsValue> &default_result,
                        const score::Result<KvsValue> &current_result) {
  if (!has_default_result) {
    return std::string("Err(") +
           normalize_error(std::string(has_default_result.error().Message())) +
           ")";
  }
  if (!has_default_result.value()) {
    if (!current_result) {
      return std::string("Err(") +
             normalize_error(std::string(current_result.error().Message())) +
             ")";
    }
    return "Ok(false)";
  }
  if (!default_result) {
    return std::string("Err(") +
           normalize_error(std::string(default_result.error().Message())) + ")";
  }
  if (!current_result) {
    return std::string("Err(") +
           normalize_error(std::string(current_result.error().Message())) + ")";
  }
  if (default_result.value().getType() != KvsValue::Type::f64 ||
      current_result.value().getType() != KvsValue::Type::f64) {
    return "Err(KeyNotFound)";
  }
  const double default_value =
      std::get<double>(default_result.value().getValue());
  const double current_value =
      std::get<double>(current_result.value().getValue());
  return f64_equal(default_value, current_value) ? "Ok(true)" : "Ok(false)";
}

void log_state(const std::string &key, const std::string &value_is_default,
               const std::string &default_value,
               const std::string &current_value) {
  TRACING_INFO(kTargetName, std::pair{std::string{"key"}, key},
               std::pair{std::string{"value_is_default"}, value_is_default},
               std::pair{std::string{"default_value"}, default_value},
               std::pair{std::string{"current_value"}, current_value});
}

void log_state(const std::string &key, bool value_is_default,
               double current_value) {
  TRACING_INFO(kTargetName, std::pair{std::string{"key"}, key},
               std::pair{std::string{"value_is_default"}, value_is_default},
               std::pair{std::string{"current_value"}, current_value});
}

std::string normalize_dir(const std::string &dir) {
  if (!dir.empty() && dir.back() == '/') {
    return dir.substr(0, dir.size() - 1);
  }
  return dir;
}

class DefaultValues final : public Scenario {
public:
  std::string name() const final { return "default_values"; }

  void run(const std::string &input) const final {
    std::string key{"test_number"};

    auto params{KvsParameters::from_json_section(input, "kvs_parameters_1")};
    {
      auto kvs{create_kvs(params)};

      auto is_default_result = kvs.has_default_value(key);
      auto default_value_result = kvs.get_default_value(key);
      auto current_value_result = kvs.get_value(key);
      std::string value_is_default{value_is_default_string(
          is_default_result, default_value_result, current_value_result)};
      std::string default_value{result_value_to_string(default_value_result)};
      std::string current_value{result_value_to_string(current_value_result)};
      log_state(key, value_is_default, default_value, current_value);

      auto set_result{kvs.set_value(key, KvsValue{432.1})};
      if (!set_result) {
        throw std::runtime_error{"Failed to set value"};
      }

      auto flush_result{kvs.flush()};
      if (!flush_result) {
        throw std::runtime_error{"Failed to flush"};
      }
    }

    {
      auto kvs{create_kvs(params)};

      auto is_default_result = kvs.has_default_value(key);
      auto default_value_result = kvs.get_default_value(key);
      auto current_value_result = kvs.get_value(key);
      std::string value_is_default{value_is_default_string(
          is_default_result, default_value_result, current_value_result)};
      std::string default_value{result_value_to_string(default_value_result)};
      std::string current_value{result_value_to_string(current_value_result)};
      log_state(key, value_is_default, default_value, current_value);
    }
  }
};

class RemoveKey final : public Scenario {
public:
  std::string name() const final { return "remove_key"; }

  void run(const std::string &input) const final {
    std::string key{"test_number"};

    auto params{KvsParameters::from_json_section(input, "kvs_parameters_1")};
    auto kvs{create_kvs(params)};

    {
      auto is_default_result = kvs.has_default_value(key);
      auto default_value_result = kvs.get_default_value(key);
      auto current_value_result = kvs.get_value(key);
      std::string value_is_default{value_is_default_string(
          is_default_result, default_value_result, current_value_result)};
      std::string default_value{result_value_to_string(default_value_result)};
      std::string current_value{result_value_to_string(current_value_result)};
      log_state(key, value_is_default, default_value, current_value);
    }

    auto set_result{kvs.set_value(key, KvsValue{432.1})};
    if (!set_result) {
      throw std::runtime_error{"Failed to set value"};
    }

    {
      auto is_default_result = kvs.has_default_value(key);
      auto default_value_result = kvs.get_default_value(key);
      auto current_value_result = kvs.get_value(key);
      std::string value_is_default{value_is_default_string(
          is_default_result, default_value_result, current_value_result)};
      std::string default_value{result_value_to_string(default_value_result)};
      std::string current_value{result_value_to_string(current_value_result)};
      log_state(key, value_is_default, default_value, current_value);
    }

    auto remove_result{kvs.remove_key(key)};
    if (!remove_result) {
      throw std::runtime_error{"Failed to remove key"};
    }

    {
      auto is_default_result = kvs.has_default_value(key);
      auto default_value_result = kvs.get_default_value(key);
      auto current_value_result = kvs.get_value(key);
      std::string value_is_default{value_is_default_string(
          is_default_result, default_value_result, current_value_result)};
      std::string default_value{result_value_to_string(default_value_result)};
      std::string current_value{result_value_to_string(current_value_result)};
      log_state(key, value_is_default, default_value, current_value);
    }
  }
};

class ResetAllKeys final : public Scenario {
public:
  std::string name() const final { return "reset_all_keys"; }

  void run(const std::string &input) const final {
    const int num_values{5};
    auto params{KvsParameters::from_json_section(input, "kvs_parameters_1")};
    auto kvs{create_kvs(params)};

    std::vector<std::pair<std::string, double>> key_values;
    for (int i{0}; i < num_values; ++i) {
      key_values.emplace_back("test_number_" + std::to_string(i), 123.4 * i);
    }

    for (const auto &[key, value] : key_values) {
      const double default_value =
          expect_f64(kvs.get_default_value(key), "Failed to get default value");
      const double current_value =
          expect_f64(kvs.get_value(key), "Failed to get value");
      const bool value_is_default{f64_equal(default_value, current_value)};
      log_state(key, value_is_default, current_value);

      auto set_result{kvs.set_value(key, KvsValue{value})};
      if (!set_result) {
        throw std::runtime_error{"Failed to set value"};
      }

      const double default_value_after =
          expect_f64(kvs.get_default_value(key), "Failed to get default value");
      const double current_value_after =
          expect_f64(kvs.get_value(key), "Failed to get value");
      const bool value_is_default_after{
          f64_equal(default_value_after, current_value_after)};
      log_state(key, value_is_default_after, current_value_after);
    }

    auto reset_result{kvs.reset()};
    if (!reset_result) {
      throw std::runtime_error{"Failed to reset KVS instance"};
    }

    for (const auto &[key, _] : key_values) {
      const double default_value =
          expect_f64(kvs.get_default_value(key), "Failed to get default value");
      const double current_value =
          expect_f64(kvs.get_value(key), "Failed to get value");
      const bool value_is_default{f64_equal(default_value, current_value)};
      log_state(key, value_is_default, current_value);
    }
  }
};

class ResetSingleKey final : public Scenario {
public:
  std::string name() const final { return "reset_single_key"; }

  void run(const std::string &input) const final {
    const int num_values{5};
    const int reset_index{2};
    auto params{KvsParameters::from_json_section(input, "kvs_parameters_1")};
    auto kvs{create_kvs(params)};

    std::vector<std::pair<std::string, double>> key_values;
    for (int i{0}; i < num_values; ++i) {
      key_values.emplace_back("test_number_" + std::to_string(i), 123.4 * i);
    }

    for (const auto &[key, value] : key_values) {
      const double default_value =
          expect_f64(kvs.get_default_value(key), "Failed to get default value");
      const double current_value =
          expect_f64(kvs.get_value(key), "Failed to get value");
      const bool value_is_default{f64_equal(default_value, current_value)};
      log_state(key, value_is_default, current_value);

      auto set_result{kvs.set_value(key, KvsValue{value})};
      if (!set_result) {
        throw std::runtime_error{"Failed to set value"};
      }

      const double default_value_after =
          expect_f64(kvs.get_default_value(key), "Failed to get default value");
      const double current_value_after =
          expect_f64(kvs.get_value(key), "Failed to get value");
      const bool value_is_default_after{
          f64_equal(default_value_after, current_value_after)};
      log_state(key, value_is_default_after, current_value_after);
    }

    auto reset_result{kvs.reset_key(key_values[reset_index].first)};
    if (!reset_result) {
      throw std::runtime_error{"Failed to reset key"};
    }

    for (const auto &[key, _] : key_values) {
      const double default_value =
          expect_f64(kvs.get_default_value(key), "Failed to get default value");
      const double current_value =
          expect_f64(kvs.get_value(key), "Failed to get value");
      const bool value_is_default{f64_equal(default_value, current_value)};
      log_state(key, value_is_default, current_value);
    }
  }
};

class Checksum final : public Scenario {
public:
  std::string name() const final { return "checksum"; }

  void run(const std::string &input) const final {
    auto params{KvsParameters::from_json_section(input, "kvs_parameters_1")};
    auto working_dir{*params.dir};
    std::string kvs_path;
    std::string hash_path;
    {
      auto kvs{create_kvs(params)};
      auto flush_result{kvs.flush()};
      if (!flush_result) {
        throw std::runtime_error{"Failed to flush"};
      }
      std::string dir = normalize_dir(working_dir);
      kvs_path =
          dir + "/kvs_" + std::to_string(params.instance_id.value) + "_0.json";
      hash_path =
          dir + "/kvs_" + std::to_string(params.instance_id.value) + "_0.hash";
    }

    TRACING_INFO(kTargetName, std::pair{std::string{"kvs_path"}, kvs_path},
                 std::pair{std::string{"hash_path"}, hash_path});
  }
};

} // namespace

ScenarioGroup::Ptr default_values_group() {
  return ScenarioGroup::Ptr{new ScenarioGroupImpl{
      "default_values",
      {std::make_shared<DefaultValues>(), std::make_shared<RemoveKey>(),
       std::make_shared<ResetAllKeys>(), std::make_shared<ResetSingleKey>(),
       std::make_shared<Checksum>()},
      {}}};
}
