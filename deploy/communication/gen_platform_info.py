# *******************************************************************************
# Copyright (c) 2026 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************
"""Generates the S-CORE platform version header from known_good.json."""

import json
import sys


def _cpp_string(value: str) -> str:
    return json.dumps(value)


def main(known_good_path: str, header_path: str) -> None:
    with open(known_good_path, encoding="utf-8") as f:
        known_good = json.load(f)

    modules = []
    for name, module in sorted(known_good["modules"]["target_sw"].items()):
        version = module.get("version") or module.get("hash")
        if not version:
            sys.exit(f"{known_good_path}: module {name} has neither 'version' nor 'hash'")
        modules.append((name, version))

    entries = "\n".join(f"    ModuleEntry{{{_cpp_string(n)}, {_cpp_string(v)}}}," for n, v in modules)
    header = f"""// Generated from known_good.json by //deploy/communication:gen_platform_info. Do not edit.
#ifndef DEPLOY_COMMUNICATION_PLATFORM_INFO_DATA_H
#define DEPLOY_COMMUNICATION_PLATFORM_INFO_DATA_H

#include <array>
#include <string_view>

namespace score::platform::heartbeat::generated
{{

struct ModuleEntry
{{
    std::string_view name;
    std::string_view version;
}};

inline constexpr std::string_view kKnownGoodTimestamp{{{_cpp_string(known_good.get("timestamp", ""))}}};

inline constexpr std::array<ModuleEntry, {len(modules)}U> kModules{{{{
{entries}
}}}};

}}  // namespace score::platform::heartbeat::generated

#endif  // DEPLOY_COMMUNICATION_PLATFORM_INFO_DATA_H
"""
    with open(header_path, "w", encoding="utf-8") as f:
        f.write(header)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: gen_platform_info.py <known_good.json> <output header>")
    main(sys.argv[1], sys.argv[2])
