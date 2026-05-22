#!/usr/bin/env python3
from __future__ import annotations

import sys
import time
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from NexusBLESdk import GatewayClient, DEFAULT_PORT, open_gateway_serial
from NexusN3Dot.profile import (
    NEXUS_N3_DOT_CONTROL_COMMAND_UUID,
    NEXUS_N3_DOT_IMU_MEASUREMENT_UUID,
    NEXUS_N3_DOT_NAME,
    NEXUS_N3_DOT_STOP_HEX,
    select_addresses,
)


def main():
    with open_gateway_serial(DEFAULT_PORT) as ser:
        gateway = GatewayClient(ser, client_name="nexus_n3_dot_subscribe_only_test")

        gateway.phase = "reset_session"
        gateway.reset_session()

        gateway.phase = "hello"
        gateway.hello()

        print("Scanning...")
        gateway.phase = "scan"
        matches = gateway.scan(5000, name_filter=NEXUS_N3_DOT_NAME)
        addresses = select_addresses(matches, 2)

        print(f"Selected: {addresses}")

        gateway.phase = "connect"
        connections = gateway.connect(addresses, timeout_s=30.0)

        try:
            print("Connected. Waiting 2s.")
            gateway.phase = "post_connect_settle"
            time.sleep(2.0)

            for connection in connections:
                print(f"PRE-STOP NOWAIT {connection.address}")
                gateway.phase = "pre_stop_nowait"
                gateway.write_gatt_nowait(
                    connection.address,
                    NEXUS_N3_DOT_CONTROL_COMMAND_UUID,
                    NEXUS_N3_DOT_STOP_HEX,
                    without_response=True,
                )
                time.sleep(0.5)

            print("Pre-stop complete. Waiting 1s before subscriptions.")
            time.sleep(1.0)

            for connection in connections:
                print(f"SUBSCRIBE {connection.address}")
                gateway.phase = "subscribe_only"
                gateway.subscribe_with_retry(
                    connection.address,
                    NEXUS_N3_DOT_IMU_MEASUREMENT_UUID,
                    timeout_s=15.0,
                    binary_notifications=True,
                )
                print(f"SUBSCRIBE COMPLETE {connection.address}")
                time.sleep(1.0)

            print("Both subscriptions completed.")

        finally:
            print("Disconnecting")
            gateway.phase = "disconnect"
            gateway.disconnect(
                [connection.address for connection in connections],
                timeout_s=10.0,
                allow_timeout=True,
            )


if __name__ == "__main__":
    main()