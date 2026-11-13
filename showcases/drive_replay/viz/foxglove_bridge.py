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
"""Bridge from the drive replay demo to Lichtblick (Foxglove WebSocket protocol).

Receives the JSON records of the demo apps (UDP, default 239.255.42.99:9001) and the DLT
stream of the datarouter (UDP, default 239.255.42.99:3490) and offers them as topics:

  /scene             foxglove.SceneUpdate    3D view: road, ego and lead vehicle
  /tf                foxglove.FrameTransform map -> ego, use "ego" as display frame
  /drive/frame       drive.Frame             speeds, gap, scenario phase
  /adas/fcw          adas.Fcw                time to collision, warning level, counters
  /system/state      system.State            active Run Target from the state manager
  /system/health     system.Health           liveness of the apps as seen by this bridge
  /log               foxglove.Log            all DLT messages (LM, DSM, RPLY, FCW, DR)
"""

import argparse
import asyncio
import ipaddress
import json
import re
import socket
import struct
import time
from collections.abc import Awaitable, Callable, Iterator
from dataclasses import dataclass
from typing import Any

from foxglove_websocket import run_cancellable
from foxglove_websocket.server import FoxgloveServer

DEFAULT_GROUP = "239.255.42.99"
VIZ_PORT = 9001
DLT_PORT = 3490
VEHICLE_LENGTH_M = 4.5
LANE_WIDTH_M = 3.5
STALE_AFTER_S = 0.5

IDENTITY = {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0}
COLOR_EGO = {"r": 0.2, "g": 0.5, "b": 1.0, "a": 1.0}
COLOR_BY_LEVEL = {
    0: {"r": 0.2, "g": 0.8, "b": 0.3, "a": 1.0},
    1: {"r": 1.0, "g": 0.75, "b": 0.0, "a": 1.0},
    2: {"r": 1.0, "g": 0.15, "b": 0.1, "a": 1.0},
}
COLOR_OFFLINE = {"r": 0.5, "g": 0.5, "b": 0.5, "a": 1.0}
COLOR_ROAD = {"r": 0.18, "g": 0.18, "b": 0.2, "a": 1.0}
COLOR_MARKING = {"r": 0.95, "g": 0.95, "b": 0.95, "a": 1.0}
COLOR_TEXT = {"r": 1.0, "g": 1.0, "b": 1.0, "a": 1.0}

# DLT log level (1 fatal .. 6 verbose) -> foxglove.Log level (1 debug .. 5 fatal)
DLT_TO_FOXGLOVE_LEVEL = {1: 5, 2: 4, 3: 3, 4: 2, 5: 1, 6: 1}


def _schema(properties: dict[str, str]) -> str:
    def _property(kind: str) -> dict[str, Any]:
        # Lichtblick's JSON schema parser needs "items" for every array.
        return {"type": kind, "items": {"type": "object"}} if kind == "array" else {"type": kind}

    return json.dumps(
        {
            "type": "object",
            "properties": {name: _property(kind) for name, kind in properties.items()},
        }
    )


TIME_PROPS = {"timestamp": "object"}
CHANNELS = {
    "/scene": ("foxglove.SceneUpdate", _schema({"deletions": "array", "entities": "array"})),
    "/tf": (
        "foxglove.FrameTransform",
        _schema(
            {
                **TIME_PROPS,
                "parent_frame_id": "string",
                "child_frame_id": "string",
                "translation": "object",
                "rotation": "object",
            }
        ),
    ),
    "/drive/frame": (
        "drive.Frame",
        _schema(
            {
                "seq": "integer",
                "lap": "integer",
                "t": "number",
                "ego_kmh": "number",
                "lead_kmh": "number",
                "gap": "number",
                "phase": "string",
            }
        ),
    ),
    "/adas/fcw": (
        "adas.Fcw",
        _schema(
            {
                "seq": "integer",
                "ttc": "number",
                "gap": "number",
                "closing": "number",
                "level": "string",
                "level_id": "integer",
                "warn_count": "integer",
                "start_count": "integer",
            }
        ),
    ),
    "/system/state": (
        "system.State",
        _schema({"run_target": "string", "source": "string", "degraded": "boolean", "recoveries": "integer"}),
    ),
    "/system/health": (
        "system.Health",
        _schema({"replay_alive": "boolean", "fcw_alive": "boolean", "fcw_silent_ms": "integer"}),
    ),
    "/log": (
        "foxglove.Log",
        _schema(
            {
                **TIME_PROPS,
                "level": "integer",
                "message": "string",
                "name": "string",
                "file": "string",
                "line": "integer",
            }
        ),
    ),
}


@dataclass
class DltMessage:
    ecu: str
    app_id: str
    context_id: str
    level: int
    text: str


def _id(raw: bytes) -> str:
    return raw.rstrip(b"\0").decode("ascii", "replace")


def _decode_verbose(payload: bytes, count: int, endian: str) -> str:
    parts: list[str] = []
    pos = 0
    for _ in range(count):
        type_info = struct.unpack_from(endian + "I", payload, pos)[0]
        pos += 4
        type_length = type_info & 0x0F
        if type_info & 0x0800:  # VARI: names/units are not supported
            parts.append("<variable info>")
            break
        if type_info & 0x0200:  # STRG
            length = struct.unpack_from(endian + "H", payload, pos)[0]
            parts.append(payload[pos + 2 : pos + 2 + length].rstrip(b"\0").decode("utf-8", "replace"))
            pos += 2 + length
        elif type_info & 0x0010:  # BOOL
            parts.append(str(bool(payload[pos])))
            pos += 1
        elif type_info & 0x0060:  # SINT / UINT
            size, code = {1: (1, "b"), 2: (2, "h"), 3: (4, "i"), 4: (8, "q")}[type_length]
            code = code.upper() if type_info & 0x0040 else code
            parts.append(str(struct.unpack_from(endian + code, payload, pos)[0]))
            pos += size
        elif type_info & 0x0080:  # FLOA
            size, code = {3: (4, "f"), 4: (8, "d")}[type_length]
            parts.append(f"{struct.unpack_from(endian + code, payload, pos)[0]:g}")
            pos += size
        elif type_info & 0x0400:  # RAWD
            length = struct.unpack_from(endian + "H", payload, pos)[0]
            parts.append(payload[pos + 2 : pos + 2 + length].hex())
            pos += 2 + length
        else:
            parts.append("<unsupported argument>")
            break
    return " ".join(parts)


def _parse_dlt_message(message: bytes) -> DltMessage | None:
    header_type = message[0]
    pos = 4
    ecu = ""
    if header_type & 0x04:  # WEID
        ecu = _id(message[pos : pos + 4])
        pos += 4
    if header_type & 0x08:  # WSID
        pos += 4
    if header_type & 0x10:  # WTMS
        pos += 4
    if not header_type & 0x01:  # without extended header there is no app id and level
        return None
    message_info, argument_count = message[pos], message[pos + 1]
    app_id, context_id = _id(message[pos + 2 : pos + 6]), _id(message[pos + 6 : pos + 10])
    pos += 10
    if (message_info >> 1) & 0x07 != 0:  # not a log message
        return None
    endian = ">" if header_type & 0x02 else "<"
    payload = message[pos:]
    if message_info & 0x01:
        text = _decode_verbose(payload, argument_count, endian)
    else:
        text = f"[non-verbose message {payload[:4].hex()}]"
    return DltMessage(ecu, app_id, context_id, (message_info >> 4) & 0x0F, text)


DLT_LEVEL_INFO = 4
# Measurement lines logged every 0.5 s for DLT charts; Lichtblick plots these values from /drive/frame and /adas/fcw.
_MEASUREMENT_LINE = re.compile(r"published via mw::com:|processed: gap")


def is_noise(message: DltMessage) -> bool:
    """Messages kept out of the log topic: debug/verbose output, mw::log statistics, the
    datarouter's own info output and the periodic measurement lines."""
    return (
        message.level > DLT_LEVEL_INFO
        or message.context_id == "STAT"
        or (message.app_id == "DR" and message.level >= DLT_LEVEL_INFO)
        or bool(_MEASUREMENT_LINE.search(message.text))
    )


def parse_dlt(datagram: bytes) -> Iterator[DltMessage]:
    """Yields the log messages of a UDP datagram, which may carry several DLT messages."""
    offset = 0
    while offset + 4 <= len(datagram):
        if datagram[offset : offset + 4] == b"DLT\x01":  # storage header
            offset += 16
            continue
        length = struct.unpack_from(">H", datagram, offset + 2)[0]
        if length < 4 or offset + length > len(datagram):
            return
        try:
            parsed = _parse_dlt_message(datagram[offset : offset + length])
        except (IndexError, KeyError, struct.error):
            parsed = None
        if parsed is not None:
            yield parsed
        offset += length


def open_udp_socket(port: int, group: str, interface: str) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if hasattr(socket, "SO_REUSEPORT"):
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.bind(("", port))
    if ipaddress.ip_address(group).is_multicast:
        membership = socket.inet_aton(group) + socket.inet_aton(interface)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
    sock.settimeout(0.0)
    return sock


class _Receiver(asyncio.DatagramProtocol):
    def __init__(self, queue: "asyncio.Queue[tuple[Handler, bytes]]", handler: "Handler") -> None:
        self._queue = queue
        self._handler = handler

    def datagram_received(self, data: bytes, addr: Any) -> None:
        self._queue.put_nowait((self._handler, data))


Handler = Callable[[bytes], Awaitable[None]]


def _stamp(now_ns: int) -> dict[str, int]:
    return {"sec": now_ns // 1_000_000_000, "nsec": now_ns % 1_000_000_000}


def _pose(x: float, y: float, z: float) -> dict[str, Any]:
    return {"position": {"x": x, "y": y, "z": z}, "orientation": IDENTITY}


def _entity(entity_id: str, now_ns: int, **primitives: list[dict[str, Any]]) -> dict[str, Any]:
    entity: dict[str, Any] = {
        "timestamp": _stamp(now_ns),
        "frame_id": "map",
        "id": entity_id,
        "lifetime": {"sec": 0, "nsec": 0},
        "frame_locked": False,
        "metadata": [],
    }
    for kind in ("arrows", "cubes", "spheres", "cylinders", "lines", "triangles", "texts", "models"):
        entity[kind] = primitives.get(kind, [])
    return entity


def _text(x: float, y: float, z: float, text: str, color: dict[str, float], size: float = 1.2) -> dict[str, Any]:
    return {
        "pose": _pose(x, y, z),
        "billboard": True,
        "font_size": size,
        "scale_invariant": False,
        "color": color,
        "text": text,
    }


class DemoBridge:
    def __init__(self, server: FoxgloveServer) -> None:
        self._server = server
        self._channels: dict[str, int] = {}
        self._fcw: dict[str, Any] = {}
        self._fcw_rx = 0.0
        self._replay_rx = 0.0

    async def advertise(self) -> None:
        for topic, (schema_name, schema) in CHANNELS.items():
            self._channels[topic] = await self._server.add_channel(
                {
                    "topic": topic,
                    "encoding": "json",
                    "schemaName": schema_name,
                    "schema": schema,
                    "schemaEncoding": "jsonschema",
                }
            )

    async def _publish(self, topic: str, message: dict[str, Any], now_ns: int) -> None:
        await self._server.send_message(self._channels[topic], now_ns, json.dumps(message).encode("utf-8"))

    async def on_record(self, datagram: bytes) -> None:
        try:
            record = json.loads(datagram)
        except (UnicodeDecodeError, json.JSONDecodeError):
            return
        now_ns = time.time_ns()
        kind = record.get("type")
        if kind == "drive":
            self._replay_rx = time.monotonic()
            await self._on_drive(record, now_ns)
        elif kind == "warn":
            self.update_fcw(record)
            await self._publish("/adas/fcw", record, now_ns)
        elif kind == "system":
            await self._publish("/system/state", record, now_ns)

    async def on_dlt(self, datagram: bytes) -> None:
        now_ns = time.time_ns()
        for message in parse_dlt(datagram):
            if is_noise(message):
                continue
            await self._publish(
                "/log",
                {
                    "timestamp": _stamp(now_ns),
                    "level": DLT_TO_FOXGLOVE_LEVEL.get(message.level, 0),
                    "message": message.text,
                    "name": f"{message.app_id}.{message.context_id}",
                    "file": message.ecu,
                    "line": 0,
                },
                now_ns,
            )

    async def publish_health(self) -> None:
        while True:
            now = time.monotonic()
            await self._publish(
                "/system/health",
                {
                    "replay_alive": now - self._replay_rx < STALE_AFTER_S,
                    "fcw_alive": now - self._fcw_rx < STALE_AFTER_S,
                    "fcw_silent_ms": int((now - self._fcw_rx) * 1000) if self._fcw_rx else -1,
                },
                time.time_ns(),
            )
            await asyncio.sleep(0.2)

    async def _on_drive(self, record: dict[str, Any], now_ns: int) -> None:
        await self._publish(
            "/drive/frame",
            {
                "seq": record["seq"],
                "lap": record["lap"],
                "t": record["t"],
                "ego_kmh": record["ego_v"] * 3.6,
                "lead_kmh": record["lead_v"] * 3.6,
                "gap": record["gap"],
                "phase": record["phase"],
            },
            now_ns,
        )
        await self._publish(
            "/tf",
            {
                "timestamp": _stamp(now_ns),
                "parent_frame_id": "map",
                "child_frame_id": "ego",
                "translation": {"x": record["ego_x"], "y": 0.0, "z": 0.0},
                "rotation": IDENTITY,
            },
            now_ns,
        )
        await self._publish("/scene", {"deletions": [], "entities": self.scene(record, now_ns)}, now_ns)

    def update_fcw(self, record: dict[str, Any]) -> None:
        """Remembers the latest warning record; the scene colors the lead vehicle with it."""
        self._fcw_rx = time.monotonic()
        self._fcw = record

    def scene(self, record: dict[str, Any], now_ns: int) -> list[dict[str, Any]]:
        ego_x, lead_x = record["ego_x"], record["lead_x"]
        fcw_alive = time.monotonic() - self._fcw_rx < STALE_AFTER_S
        level = self._fcw.get("level_id", 0) if fcw_alive else -1

        start, end = ego_x - 40.0, ego_x + 160.0
        center_y = LANE_WIDTH_M / 2
        dashes = []
        dash_x = start - (start % 12.0)
        while dash_x < end:
            dashes += [{"x": dash_x, "y": center_y, "z": 0.02}, {"x": dash_x + 3.0, "y": center_y, "z": 0.02}]
            dash_x += 12.0
        edges = []
        for y in (-LANE_WIDTH_M / 2, LANE_WIDTH_M * 1.5):
            edges += [{"x": start, "y": y, "z": 0.02}, {"x": end, "y": y, "z": 0.02}]
        road_surface = {
            "pose": _pose(ego_x + 60.0, center_y, -0.05),
            "size": {"x": end - start, "y": 2 * LANE_WIDTH_M + 1.0, "z": 0.1},
            "color": COLOR_ROAD,
        }
        markings = [
            {
                "type": 2,  # LINE_LIST
                "pose": _pose(0.0, 0.0, 0.0),
                "thickness": 0.15,
                "scale_invariant": False,
                "points": points,
                "color": COLOR_MARKING,
                "colors": [],
                "indices": [],
            }
            for points in (dashes, edges)
        ]
        road = _entity("road", now_ns, cubes=[road_surface], lines=markings)

        vehicle = {"x": VEHICLE_LENGTH_M, "y": 1.8, "z": 1.5}
        ego_texts = [_text(ego_x, 0.0, 2.6, f"EGO {record['ego_v'] * 3.6:.0f} km/h", COLOR_TEXT)]
        if level == 2:
            ego_texts.append(_text(ego_x, 0.0, 4.2, "BRAKE!", COLOR_BY_LEVEL[2], 2.0))
        elif level == 1:
            ego_texts.append(_text(ego_x, 0.0, 4.2, "COLLISION WARNING", COLOR_BY_LEVEL[1], 1.4))
        elif level < 0:
            ego_texts.append(_text(ego_x, 0.0, 4.2, "FCW OFFLINE", COLOR_OFFLINE, 1.4))
        ego_cube = {"pose": _pose(ego_x, 0.0, 0.75), "size": vehicle, "color": COLOR_EGO}
        ego = _entity("ego", now_ns, cubes=[ego_cube], texts=ego_texts)

        ttc = self._fcw.get("ttc", 99.0)
        lead_label = f"{record['lead_v'] * 3.6:.0f} km/h" + (f" | TTC {ttc:.1f} s" if fcw_alive and ttc < 10.0 else "")
        lead_color = COLOR_BY_LEVEL.get(level, COLOR_OFFLINE)
        lead_cube = {"pose": _pose(lead_x, 0.0, 0.75), "size": vehicle, "color": lead_color}
        lead = _entity("lead", now_ns, cubes=[lead_cube], texts=[_text(lead_x, 0.0, 2.6, lead_label, COLOR_TEXT)])
        return [road, ego, lead]


async def main(args: argparse.Namespace) -> None:
    async with FoxgloveServer(args.host, args.port, "S-CORE drive replay", supported_encodings=["json"]) as server:
        bridge = DemoBridge(server)
        await bridge.advertise()

        loop = asyncio.get_running_loop()
        queue: asyncio.Queue[tuple[Handler, bytes]] = asyncio.Queue()
        viz_sock = open_udp_socket(args.viz_port, args.group, args.interface)
        dlt_sock = open_udp_socket(args.dlt_port, args.group, args.interface)
        await loop.create_datagram_endpoint(lambda: _Receiver(queue, bridge.on_record), sock=viz_sock)
        await loop.create_datagram_endpoint(lambda: _Receiver(queue, bridge.on_dlt), sock=dlt_sock)
        print(f"Lichtblick: open connection -> Foxglove WebSocket -> ws://{args.host}:{args.port}")
        print(f"listening for demo records on :{args.viz_port} and DLT on :{args.dlt_port} (group {args.group})")

        health = asyncio.create_task(bridge.publish_health())
        try:
            while True:
                handler, data = await queue.get()
                await handler(data)
        finally:
            health.cancel()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--host", default="127.0.0.1", help="WebSocket bind address (0.0.0.0 to serve other machines)")
    parser.add_argument("--port", type=int, default=8765, help="WebSocket port")
    parser.add_argument("--group", default=DEFAULT_GROUP, help="multicast group of the demo records and DLT")
    parser.add_argument("--interface", default="0.0.0.0", help="IPv4 address of the interface to join the group on")
    parser.add_argument("--viz-port", type=int, default=VIZ_PORT)
    parser.add_argument("--dlt-port", type=int, default=DLT_PORT)
    run_cancellable(main(parser.parse_args()))
