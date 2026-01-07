# Dimplex WPM – Home Assistant Modbus TCP integration

Custom HACS integration for connecting Dimplex WPM / NWPM heat pump controllers over Modbus TCP. The integration batches Modbus reads through a dedicated async pymodbus client, exposes sensors and binary sensors via a `DataUpdateCoordinator`, builds a device tree (Controller → HC1 → DHW → Smart Grid), and allows writing SG Ready mode as a select entity.

## Features (v0.1.0)

- Config Flow and Options Flow (UI-first, stored in Config Entries).
- Periodic batch polling of key registers (temperatures, status/lock/fault codes, SG Ready).
- Human-friendly text sensors for status, lock, fault, and SG Ready.
- Diagnostic binary sensors for `fault_active` and `lock_active`.
- Controller info diagnostic sensor with host/port/unit, last update, and capabilities.
- SG Ready mode writable as a select (`Hardware`, `Yellow`, `Green`, `Red`, `Deep Green`) gated by the Options Flow (disabled by default).
- Optional toggles for write entities and future EMS/BMS features.

### Entities

| Type | Entity | Register | Notes |
| --- | --- | --- | --- |
| sensor | controller_info | — | Attributes: host/port/unit_id, last_update, failure counter, capabilities |
| sensor | outdoor_temperature | 1 (int16, 0.1°C) | Temperature °C |
| sensor | return_temperature | 2 (int16, 0.1°C) | Temperature °C |
| sensor | return_setpoint_temperature | 53 (int16, 0.1°C) | Temperature °C |
| sensor | flow_temperature | 5 (int16, 0.1°C) | Temperature °C |
| sensor | dhw_temperature | 3 (int16, 0.1°C) | Temperature °C |
| sensor | status_code / status | 103 | Diagnostic + mapped text |
| sensor | lock_code / lock | 104 | Diagnostic + mapped text |
| sensor | fault_code / fault | 105 | Diagnostic + mapped text |
| sensor | sensor_error_code / sensor_error | 106 | Diagnostic + mapped text |
| sensor | sg_ready_code / sg_ready_state | 5167 | Diagnostic code + text |
| binary_sensor | fault_active | derived | `True` when fault code ≠ 0 |
| binary_sensor | lock_active | derived | `True` when lock code ≠ 0 |
| select | sg_ready_mode | 5167 | Writable: Hardware / Yellow / Green / Red / Deep Green |

## Installation (HACS custom repository)

1. In HACS → Integrations → ⋮ → **Custom repositories**, add this repo URL and select **Integration**.
2. Install “Dimplex WPM”.
3. Restart Home Assistant.
4. Go to Settings → Devices & Services → **Add Integration** → search for “Dimplex WPM”.

## Configuration

Config Flow fields:

- **Host** (IP/DNS)
- **Port** (default `502`)
- **Unit ID** (default `1`)
- **Scan interval** (seconds, default `30`)
- **Timeout** (seconds, default `5`)
- **Register bank strategy**: `auto` (try input then holding), `holding`, or `input`

Options Flow:

- **Scan interval** override.
- **Enable write entities** (gate for SG Ready select, default **off**).
- **Enable EMS entities**, **BMS outdoor temp**, **external lock** (placeholders for upcoming releases).

## How it works

- A dedicated async `pymodbus` TCP client manages connection/reconnect and register reads/writes.
- `DataUpdateCoordinator` batches reads into contiguous ranges for efficiency.
- Entities are thin wrappers reading from `coordinator.data` (`raw` and `derived` dicts).
- SG Ready writes call `write_register` on register `5167`, mapping friendly strings to numeric codes.
- Register addresses match the Dimplex documentation (1-based); the integration applies the Modbus client offset automatically.

## Development roadmap

- v0.1.0 (this repo): MVP read + SG Ready write.
- v0.2.0: EMS/power registers, external lock, BMS outdoor temperature number entity.
- Additional status/lock/fault map coverage based on field feedback.

## Dashboard example

A sample Lovelace board is available in `dimplex_dashboard.yaml` demonstrating status and temperature graphs. Import it into a manual dashboard to start visualizing the entities.
