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
"""Unit tests of the Lichtblick bridge: DLT parsing, log filtering, schemas and the 3D scene."""

import json
import struct
import sys
import types
from pathlib import Path

import pytest

# foxglove-websocket is only installed on the laptop that runs the bridge.
_foxglove = types.ModuleType("foxglove_websocket")
_foxglove.run_cancellable = lambda _: None
_foxglove_server = types.ModuleType("foxglove_websocket.server")
_foxglove_server.FoxgloveServer = object
sys.modules.setdefault("foxglove_websocket", _foxglove)
sys.modules.setdefault("foxglove_websocket.server", _foxglove_server)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import foxglove_bridge  # noqa: E402

VERB, UEH, MSBF, WEID, WTMS, VERSION_1 = 0x01, 0x01, 0x02, 0x04, 0x10, 0x20
TYPE_STRG, TYPE_UINT32, TYPE_FLOA64 = 0x200, 0x40 | 3, 0x80 | 4


def dlt_message(app_id: str, context_id: str, level: int, args: list, *, big_endian: bool = False) -> bytes:
    """Builds a verbose DLT log message as the datarouter sends it over UDP."""
    endian = ">" if big_endian else "<"
    payload = b""
    for arg in args:
        if isinstance(arg, str):
            raw = arg.encode() + b"\0"
            payload += struct.pack(endian + "IH", TYPE_STRG, len(raw)) + raw
        elif isinstance(arg, float):
            payload += struct.pack(endian + "Id", TYPE_FLOA64, arg)
        else:
            payload += struct.pack(endian + "II", TYPE_UINT32, arg)
    header_type = UEH | WEID | WTMS | VERSION_1 | (MSBF if big_endian else 0)
    ids = app_id.ljust(4, "\0").encode() + context_id.ljust(4, "\0").encode()
    extended = bytes([VERB | (level << 4), len(args)]) + ids
    body = b"SCPP" + struct.pack(">I", 1234) + extended + payload
    return bytes([header_type, 0]) + struct.pack(">H", 4 + len(body)) + body


def test_parse_dlt_reads_several_messages_of_both_byte_orders():
    datagram = dlt_message("FCW", "FCW", 3, ["FORWARD COLLISION WARNING"]) + dlt_message(
        "LM", "LM", 2, ["process", 17, 1.5], big_endian=True
    )

    messages = list(foxglove_bridge.parse_dlt(datagram))

    assert [(m.ecu, m.app_id, m.context_id, m.level) for m in messages] == [
        ("SCPP", "FCW", "FCW", 3),
        ("SCPP", "LM", "LM", 2),
    ]
    assert messages[0].text == "FORWARD COLLISION WARNING"
    assert messages[1].text == "process 17 1.5"


def test_parse_dlt_skips_storage_header_and_stops_at_truncated_message():
    message = dlt_message("RPLY", "DRV", 4, ["lap 2 started"])
    datagram = b"DLT\x01" + bytes(12) + message + message[:10]

    assert [m.text for m in foxglove_bridge.parse_dlt(datagram)] == ["lap 2 started"]


@pytest.mark.parametrize(
    ("app_id", "context_id", "level", "text", "noise"),
    [
        ("FCW", "FCW", 3, "frame #235: FORWARD COLLISION WARNING - TTC 3.0 s", False),
        ("LM", "LM", 3, "Alive Supervision ( warn_app ) switched to FAILED", False),
        ("DSM", "SM", 2, "launch manager recovered a failure", False),
        ("DR", "DFLT", 2, "datarouter error", False),
        ("LM", "LM", 5, "Starting process ( warn_app )", True),
        ("RPLY", "DRV", 4, "frame #10 published via mw::com: ego 79 km/h, lead 79 km/h, gap 35.5 m", True),
        ("FCW", "FCW", 4, "frame #10 processed: gap 35.5 m, closing 0.0 m/s, TTC 10.0 s, OK", True),
        ("DR", "STAT", 4, "statistics", True),
        ("DR", "DFLT", 4, "successfully completed initialization", True),
    ],
)
def test_log_topic_keeps_the_story_and_drops_noise(app_id, context_id, level, text, noise):
    message = foxglove_bridge.DltMessage("SCPP", app_id, context_id, level, text)

    assert foxglove_bridge.is_noise(message) is noise


def test_channel_schemas_define_items_for_arrays():
    for topic, (_, schema) in foxglove_bridge.CHANNELS.items():
        for name, prop in json.loads(schema)["properties"].items():
            if prop["type"] == "array":
                assert "items" in prop, f"{topic}.{name}: Lichtblick needs 'items' for arrays"


def test_scene_shows_road_ego_and_lead_colored_by_warning_level():
    bridge = foxglove_bridge.DemoBridge(server=None)
    bridge.update_fcw({"level_id": 2, "ttc": 1.8})
    record = {"ego_x": 100.0, "lead_x": 120.0, "ego_v": 20.0, "lead_v": 5.0}

    road, ego, lead = bridge.scene(record, now_ns=0)

    assert (road["id"], ego["id"], lead["id"]) == ("road", "ego", "lead")
    assert lead["cubes"][0]["color"] == foxglove_bridge.COLOR_BY_LEVEL[2]
    assert "TTC 1.8 s" in lead["texts"][0]["text"]
    assert any(text["text"] == "BRAKE!" for text in ego["texts"])


def test_scene_marks_the_warning_offline_without_fresh_fcw_records():
    bridge = foxglove_bridge.DemoBridge(server=None)
    record = {"ego_x": 0.0, "lead_x": 40.0, "ego_v": 22.0, "lead_v": 22.0}

    _, ego, lead = bridge.scene(record, now_ns=0)

    assert lead["cubes"][0]["color"] == foxglove_bridge.COLOR_OFFLINE
    assert any(text["text"] == "FCW OFFLINE" for text in ego["texts"])
