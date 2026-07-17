# Nexus N3 HDR Dot

This directory contains the customer-facing Nexus N3 HDR Dot host sample for the Nexus BLE gateway.

`stream_client.py` is the recommended starting point for customers who want to connect a supported gateway board, discover Nexus N3 HDR Dot sensors, start streaming, and verify that data is flowing correctly.

## What This Sample Does

The sample client:

- opens the gateway serial interface
- resets the gateway host session
- scans for Nexus N3 HDR Dot sensors
- connects the requested number of sensors
- subscribes to the HDR streaming characteristic
- sets the requested HDR stream mode
- starts streaming
- applies a mode-aware startup stability gate before measurement, if enabled
- optionally writes parsed measurement samples to CSV
- prints a stream and gateway summary at the end

During a run, the client prints operator-facing progress messages for the main phases, including scanning, connecting, link settling, configuration, stream start, startup-gate status, official measurement activation, stream stop, device-status readout, and final summary output.

## Requirements

- a programmed Nexus BLE gateway board connected over USB
- at least one powered Nexus N3 HDR Dot sensor advertising nearby
- Python 3
- the Python `pyserial` package available in your environment

## Stream Modes

The HDR client exposes six stream modes through `--stream-mode`:

- `MAG`: magnitude only, the default and lowest-bandwidth option
- `X`, `Y`, `Z`: single-axis acceleration streams
- `XYZ`: three-axis acceleration stream
- `ALL`: `X`, `Y`, `Z`, and magnitude in each sample

The sensor output rate is fixed at 2048 Hz. The host calculates the expected BLE notification rate from the selected stream mode and uses that rate to tune the startup gate defaults.

## Single-Sensor Test

Run the customer-facing sample with one sensor in the default magnitude mode:

```bash
python NexusN3HDRDot/stream_client.py \
  --sensor-count 1 \
  --stream-mode MAG \
  --stream-seconds 10
```

To test a higher-bandwidth mode:

```bash
python NexusN3HDRDot/stream_client.py \
  --sensor-count 1 \
  --stream-mode XYZ \
  --stream-seconds 10
```

To explicitly keep the startup gate enabled:

```bash
python NexusN3HDRDot/stream_client.py \
  --sensor-count 1 \
  --stream-mode MAG \
  --stream-seconds 10 \
  --use-startup-gate
```

To disable the startup gate for debugging:

```bash
python NexusN3HDRDot/stream_client.py \
  --sensor-count 1 \
  --stream-mode MAG \
  --stream-seconds 10 \
  --no-startup-gate
```

If your gateway appears at a different serial path:

```bash
python NexusN3HDRDot/stream_client.py \
  --port /dev/serial/by-id/your-gateway-device \
  --sensor-count 1 \
  --stream-mode MAG
```

## Writing Parsed Output

Use `--write-to-file` to save parsed measurement rows under `output-files/` in the current working directory:

```bash
python NexusN3HDRDot/stream_client.py \
  --sensor-count 1 \
  --stream-mode ALL \
  --stream-seconds 10 \
  --write-to-file
```

When file output is enabled, the client writes a CSV with:

- gateway timestamp
- sensor timestamp
- selected stream mode
- per-notification sample count
- parsed acceleration and magnitude fields for the active mode

Rows are only written after the startup gate has passed, or immediately if the startup gate is disabled.

## Expected Output

For a healthy single-sensor run, you should see:

- `Scanning for up to ...`
- `SCAN MATCH: ...` and `SCAN COMPLETE: ...`
- `CONNECTED: ...`
- `Startup gate config: expected_notification_rate=... min_rate=... packets_required=...`
- `All sensors connected. Waiting ... for BLE links/params to settle.`
- `CONFIG ...: pre-stop`, `subscribe`, and `set-stream-mode ...`
- `All sensors configured. Waiting ... before stream start.`
- `Starting stream. mode=... expected_notification_rate=... total stream budget: ...`
- `Waiting for startup stability gate: ...` when the startup gate is enabled
- `Startup stability gate passed. Official measurement is now active.` once the stream is stable
- a `Selected addresses: [...]` line
- no disconnect or timeout failure during configure or streaming
- `STOP STREAM ...` lines during shutdown
- summary output with non-zero startup and measurement packet counts
- `observed_rate_hz` close to the expected notification rate for the chosen stream mode
- `Device status address=... running=... stream_mode=... output_rate_hz=2048 ...` near the end of the run
