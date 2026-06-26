#!/usr/bin/env python3

from __future__ import annotations

import argparse
import time
from typing import Any

from NexusBLESdk.client import GatewayClient
from NexusBLESdk.transport import DEFAULT_BAUD, DEFAULT_PORT, open_gateway_serial


def main() -> None:
    parser = argparse.ArgumentParser(description="Button Test")

    parser.add_argument("--port", default=DEFAULT_PORT)
    parser.add_argument("--baud", type=int, default=DEFAULT_BAUD)
    parser.add_argument("--duration-ms", type=int, default=5000)

    args = parser.parse_args()

    # open the gateway serial port
    with open_gateway_serial(args.port, args.baud) as ser:
        gateway = GatewayClient(
            ser,
            client_name="button_test",
            verbose=True,
        )

        print("Sending hello...")
        hello = gateway.hello()
        print("HELLO:", hello)

        print(f"Listening for button events for {args.duration_ms} ms...")
        print("Press the gateway button now.")

        deadline = time.monotonic() + (args.duration_ms / 1000.0)
        button_press_count = 0

        while time.monotonic() < deadline:
            timeout_s = max(0.1, deadline - time.monotonic())

            try:
                msg: dict[str, Any] = gateway.read_json(timeout_s=timeout_s)
            except TimeoutError:
                break

            if msg.get("type") != "button_pressed":
                continue

            button_press_count += 1

            print(
                "BUTTON:",
                "count=", button_press_count,
                "source=", msg.get("source"),
                "timestamp_ms=", msg.get("timestamp_ms"),
            )

        print(f"Button test duration complete. Presses seen: {button_press_count}")


if __name__ == "__main__":
    main()