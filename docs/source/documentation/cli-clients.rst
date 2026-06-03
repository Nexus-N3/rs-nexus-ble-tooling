CLI Clients
===========

The repository includes two customer-facing sample clients built on the shared SDK.

Public repository root: `Nexus-N3/rs-nexus-ble-tooling <https://github.com/Nexus-N3/rs-nexus-ble-tooling>`_.

Movella DOT Client
------------------

``MovellaDot/stream_client.py`` is the current tutorial path and the most direct example of a supported sensor workflow.

Public source links:

- `MovellaDot/stream_client.py <https://github.com/Nexus-N3/rs-nexus-ble-tooling/blob/main/MovellaDot/stream_client.py>`_
- `MovellaDot/client.py <https://github.com/Nexus-N3/rs-nexus-ble-tooling/blob/main/MovellaDot/client.py>`_

Primary options:

- ``--port`` to select the gateway serial device
- ``--sensor-count`` to choose how many sensors to connect
- ``--scan-timeout-ms`` to control discovery duration
- ``--sampling-rate-hz`` to select the supported Movella rate
- ``--stream-seconds`` to control capture duration
- ``--use-startup-gate`` or ``--no-startup-gate`` to control startup validation

Programmatic API:

- ``MovellaDot.MovellaDotClient.discover()``
- ``MovellaDot.MovellaDotClient.connect()``
- ``MovellaDot.MovellaDotClient.configure()``
- ``MovellaDot.MovellaDotClient.start_streams()``
- ``MovellaDot.MovellaDotClient.stop_streams()``
- ``MovellaDot.MovellaDotClient.disconnect_all()``

Nexus N3 Dot Client
-------------------

``NexusN3Dot/stream_client.py`` follows the same overall lifecycle, with Nexus N3 Dot-specific UUIDs, output-rate settings, and device-status reads.

Public source links:

- `NexusN3Dot/stream_client.py <https://github.com/Nexus-N3/rs-nexus-ble-tooling/blob/main/NexusN3Dot/stream_client.py>`_
- `NexusN3Dot/client.py <https://github.com/Nexus-N3/rs-nexus-ble-tooling/blob/main/NexusN3Dot/client.py>`_

Primary options:

- ``--port`` to select the gateway serial device
- ``--sensor-count`` to choose how many sensors to connect
- ``--scan-timeout-ms`` to control discovery duration
- ``--sampling-rate-hz`` to select a supported output data rate
- ``--stream-seconds`` to control capture duration
- ``--use-startup-gate`` or ``--no-startup-gate`` to control startup validation

Programmatic API:

- ``NexusN3Dot.NexusN3DotClient.discover()``
- ``NexusN3Dot.NexusN3DotClient.connect()``
- ``NexusN3Dot.NexusN3DotClient.configure()``
- ``NexusN3Dot.NexusN3DotClient.start_streams()``
- ``NexusN3Dot.NexusN3DotClient.stop_streams()``
- ``NexusN3Dot.NexusN3DotClient.read_device_status_all()``
- ``NexusN3Dot.NexusN3DotClient.disconnect_all()``
