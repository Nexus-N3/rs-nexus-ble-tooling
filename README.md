# Nexus BLE Tooling

This repository contains the Python tooling for the Nexus BLE gateway and supported sensor integrations.

The layout is split into two parts:

- `NexusBLESdk/`: shared serial transport, command handling, stream monitoring, startup-gate logic, and generic stream statistics
- `MovellaDot/`: the Movella DOT sample client built on top of `NexusBLESdk`
- `NexusN3Dot/`: the Nexus N3 Dot sample client built on top of `NexusBLESdk`

Additional sensor integrations can be added beside `MovellaDot/` using the same structure.

## Capture Client

The repository now includes an interactive capture workflow under `Capture/cli.py`.

This client is intended for operator-driven recording sessions where the user:

- chooses a supported sensor family
- chooses how many sensors to use
- assigns one location per connected sensor
- optionally uses guided identify for Movella DOT placement
- starts and stops the capture manually
- gets a dedicated session directory under `output-files/captures/`

Example:

- `python Capture/cli.py --sensor-type movelladot --sensor-count 2 --tag walk_trial`
- type `quit` at any interactive prompt, or press `Ctrl+C`, to cancel the workflow; if sensors are already connected, the client disconnects them before exiting

## Directory Layout

- `NexusBLESdk/`
  Reusable Python code for talking to the gateway over the serial link. This layer handles gateway protocol messages, mixed JSON and binary stream parsing, connection lifecycle operations, and generic monitoring utilities that can be reused across supported sensors.

- `MovellaDot/`
  The Movella DOT integration. This directory contains Movella DOT-specific constants, payload parsing, sensor operations, and a runnable `stream_client.py` example.

- `NexusN3Dot/`
  The Nexus N3 Dot integration. This directory contains Nexus N3 Dot-specific constants, payload parsing, sensor operations, and a runnable `stream_client.py` example.

- `Capture/`
  The operator-facing capture workflow. This directory contains the shared capture session CLI, sensor adapter layer, and manifest/session helpers.

## Getting Started

To start with the supported samples:

- run `python Capture/cli.py`
- see [MovellaDot/README.md](/home/mike/Desktop/apps/dev/rs-nexus-project/rs-nexus-ble/rs-nexus-ble-tooling/MovellaDot/README.md)
- run `python MovellaDot/stream_client.py --sensor-count 1 --stream-seconds 10`
- see [NexusN3Dot/README.md](/home/mike/Desktop/apps/dev/rs-nexus-project/rs-nexus-ble/rs-nexus-ble-tooling/NexusN3Dot/README.md)
- run `python NexusN3Dot/stream_client.py --sensor-count 1 --stream-seconds 10`
- run `python Movesense/stream_client.py --sensor-count 1 --stream-seconds 10`

## Design Intent

The goal of this layout is to keep shared gateway behavior separate from sensor-specific workflows:

- use `NexusBLESdk` for shared gateway behavior
- keep each sensor CLI focused and sensor-specific
- keep reusable monitoring, startup-gate, and stream-health reporting generic where possible
