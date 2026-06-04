from __future__ import annotations

import json
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
ECG_SAMPLE_SCALE_MV = 0.38147 * 0.001
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


def parse_ecg_sample_values_mv(payload: bytes) -> list[float]:
    if len(payload) < MOVESENSE_MIN_PACKET_LEN or payload[0] != MOVESENSE_PACKET_TYPE_DATA:
        return []

    payload_len = len(payload) - 6
    if payload_len <= 0:
        return []

    if payload_len == 64:
        return [
            struct.unpack("<i", payload[6 + index * 4:10 + index * 4])[0] * ECG_SAMPLE_SCALE_MV
            for index in range(MOVESENSE_ECG_SAMPLES_PER_PACKET)
        ]
    if payload_len == 32:
        return [
            struct.unpack("<h", payload[6 + index * 2:8 + index * 2])[0] * ECG_SAMPLE_SCALE_MV
            for index in range(MOVESENSE_ECG_SAMPLES_PER_PACKET)
        ]

    values: list[float] = []
    sample_count = payload_len // 4
    for index in range(sample_count):
        offset = 6 + index * 4
        if offset + 4 > len(payload):
            break
        values.append(struct.unpack("<i", payload[offset:offset + 4])[0] * ECG_SAMPLE_SCALE_MV)
    return values


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


def parse_ecg_sample_timestamps_ms(payload: bytes, sampling_rate_hz: int) -> list[int]:
    sample_count = parse_ecg_packet_sample_count(payload)
    if sample_count <= 0:
        return []
    packet_timestamp_ms = int(struct.unpack_from("<I", payload, 2)[0])
    return [
        packet_timestamp_ms + int(index * 1000 / sampling_rate_hz)
        for index in range(sample_count)
    ]


def summarize_payload(payload: bytes, sampling_rate_hz: int) -> dict:
    packet_type = payload[0] if payload else None
    stream_id = payload[1] if len(payload) >= 2 else None
    summary = {
        "packet_type": packet_type,
        "stream_id": stream_id,
        "payload_hex": payload.hex(),
        "payload_len": len(payload),
    }
    if packet_type == MOVESENSE_PACKET_TYPE_DATA:
        if stream_id == MOVESENSE_ECG_STREAM_ID and len(payload) >= MOVESENSE_MIN_PACKET_LEN:
            sample_timestamps_ms = parse_ecg_sample_timestamps_ms(payload, sampling_rate_hz)
            summary.update(
                {
                    "packet_timestamp_ms": int(struct.unpack_from("<I", payload, 2)[0]),
                    "packet_timestamp_us": parse_ecg_packet_timestamp_us(payload),
                    "ecg_sample_count": parse_ecg_packet_sample_count(payload),
                    "ecg_values_mv": parse_ecg_sample_values_mv(payload),
                    "sample_timestamps_ms": sample_timestamps_ms,
                    "first_sample_timestamp_ms": sample_timestamps_ms[0] if sample_timestamps_ms else None,
                    "last_sample_timestamp_ms": sample_timestamps_ms[-1] if sample_timestamps_ms else None,
                }
            )
        elif stream_id == MOVESENSE_HR_STREAM_ID:
            summary["hr_value"] = parse_hr_value(payload)
        elif stream_id == MOVESENSE_TEMP_STREAM_ID:
            summary["temp_c"] = parse_temp_value(payload)
    return summary


def iter_parsed_rows(
    payload: bytes,
    *,
    sampling_rate_hz: int,
    address: str | None,
    sensor_id: int,
    gateway_timestamp_us: int,
) -> list[dict]:
    if len(payload) < 2 or payload[0] != MOVESENSE_PACKET_TYPE_DATA:
        return []

    stream_id = payload[1]
    if stream_id == MOVESENSE_ECG_STREAM_ID:
        timestamps_ms = parse_ecg_sample_timestamps_ms(payload, sampling_rate_hz)
        values_mv = parse_ecg_sample_values_mv(payload)
        packet_timestamp_ms = int(struct.unpack_from("<I", payload, 2)[0])
        rows = []
        for index, (timestamp_ms, value_mv) in enumerate(zip(timestamps_ms, values_mv)):
            rows.append(
                {
                    "address": address or "",
                    "sensor_id": sensor_id,
                    "stream": "ecg",
                    "timestamp_ms": timestamp_ms,
                    "gateway_timestamp_us": gateway_timestamp_us,
                    "packet_timestamp_ms": packet_timestamp_ms,
                    "sample_index": index,
                    "sampling_rate_hz": sampling_rate_hz,
                    "value": value_mv,
                    "unit": "mV",
                }
            )
        return rows

    if stream_id == MOVESENSE_HR_STREAM_ID:
        hr_value = parse_hr_value(payload)
        if hr_value is None:
            return []
        return [
            {
                "address": address or "",
                "sensor_id": sensor_id,
                "stream": "hr",
                "timestamp_ms": int(gateway_timestamp_us / 1000),
                "gateway_timestamp_us": gateway_timestamp_us,
                "packet_timestamp_ms": "",
                "sample_index": 0,
                "sampling_rate_hz": "",
                "value": hr_value,
                "unit": "bpm",
            }
        ]

    if stream_id == MOVESENSE_TEMP_STREAM_ID:
        temp_value = parse_temp_value(payload)
        if temp_value is None:
            return []
        return [
            {
                "address": address or "",
                "sensor_id": sensor_id,
                "stream": "temp",
                "timestamp_ms": int(gateway_timestamp_us / 1000),
                "gateway_timestamp_us": gateway_timestamp_us,
                "packet_timestamp_ms": "",
                "sample_index": 0,
                "sampling_rate_hz": "",
                "value": temp_value,
                "unit": "C",
            }
        ]

    return []


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
