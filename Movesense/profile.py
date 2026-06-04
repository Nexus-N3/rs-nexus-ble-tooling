from __future__ import annotations

import struct


MOVESENSE_NAME_PREFIX = "Movesense"
MOVESENSE_WRITE_UUID = "34800001-7185-4d5d-b431-630e7050e8f0"
MOVESENSE_NOTIFY_UUID = "34800002-7185-4d5d-b431-630e7050e8f0"
MOVESENSE_SAMPLING_RATES_HZ = (200,)
MOVESENSE_ECG_STREAM_ID = 100
MOVESENSE_HR_STREAM_ID = 1
MOVESENSE_TEMP_STREAM_ID = 2
MOVESENSE_ECG_SAMPLES_PER_PACKET = 16
MOVESENSE_PACKET_TYPE_GET_RESPONSE = 1
MOVESENSE_PACKET_TYPE_DATA = 2
MOVESENSE_MIN_PACKET_LEN = 6
DEFAULT_STARTUP_GATE = {
    "enabled": True,
    "stability_window_seconds": 5.0,
    "packets_required": 20,
    "min_rate_hz": 10.0,
    "min_observation_seconds": 1.5,
    "max_gap_events": 0,
    "gap_grace_seconds": 0.5,
}
DEFAULT_LOCATIONS = [
    "CHEST",
]


def parse_ecg_packet_timestamp_us(payload: bytes) -> int:
    if len(payload) < MOVESENSE_MIN_PACKET_LEN:
        raise ValueError(f"Movesense payload too short: {len(payload)} bytes")
    if payload[0] != MOVESENSE_PACKET_TYPE_DATA:
        raise ValueError(f"Movesense payload is not a data packet: type={payload[0]}")
    # Movesense ECG packets carry a millisecond timestamp at offset 2.
    return int(struct.unpack_from("<I", payload, 2)[0]) * 1000


def parse_ecg_packet_sample_count(payload: bytes) -> int:
    if len(payload) < MOVESENSE_MIN_PACKET_LEN or payload[0] != MOVESENSE_PACKET_TYPE_DATA:
        return 0

    payload_len = len(payload) - 6
    if payload_len == 64 or payload_len == 32:
        return MOVESENSE_ECG_SAMPLES_PER_PACKET
    if payload_len <= 0:
        return 0
    return payload_len // 4


def parse_hr_value(payload: bytes) -> float | None:
    if len(payload) < 8:
        return None
    return float(struct.unpack("<f", payload[2:6])[0])


def parse_temp_value(payload: bytes) -> float | None:
    if len(payload) < 6:
        return None
    if len(payload) >= 10:
        temp = struct.unpack("<f", payload[2:6])[0]
    else:
        values = struct.unpack("<" + ((len(payload) - 6) // 4) * "f", payload[6:])
        if not values:
            return None
        temp = float(values[0])
    if temp > 200:
        temp -= 273.15
    return float(temp)


def build_subscribe_command(stream_id: int, path: str) -> str:
    return (bytes([1, stream_id]) + path.encode("utf-8")).hex()


def build_stop_command(stream_id: int) -> str:
    return bytes([2, stream_id]).hex()


def is_movesense_match(name: str) -> bool:
    return name.startswith(MOVESENSE_NAME_PREFIX)


def select_addresses(matches, count: int) -> list[str]:
    filtered = [entry.address for entry in matches if is_movesense_match(entry.name)]
    if len(filtered) < count:
        raise RuntimeError(f"Requested {count} Movesense sensors, found {len(filtered)}")
    return filtered[:count]
