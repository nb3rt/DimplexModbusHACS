# Dimplex WPM — Home Assistant (Modbus TCP)

Custom HACS integration for Dimplex **WPM / NWPM** heat-pump controllers over
Modbus TCP. It is driven by a single canonical register table, groups entities
under a device tree, and — crucially — ships a **native estimation engine** so
installations **without** an electricity meter or heat meter still get power,
COP, heat-output, flow and energy figures.

> Reference spec: Dimplex NWPM Modbus TCP —
> https://dimplex.atlassian.net/wiki/spaces/DW/pages/3303571457/Modbus+TCP+Anbindung

## Highlights

- **Register-table driven** (`registers.py`): one source of truth → ~100 read
  entities. Status/lock/fault/sensor-error register **addresses are firmware-
  version-aware** (H / J / L / M).
- **Device profiles** (`profiles.py`): LAK9 calibration (Hz→W LUT, EN14511 COP
  table) + a generic profile. Community models = one new profile file.
- **Capabilities** (per install): electric meter, heat meter, external flow
  sensor, inverter frequency. Declared in the setup wizard with an auto-hint
  probe of the device.
- **Measurement source matrix** — each power/heat/flow/COP/energy value is
  `measured` (read from a meter register) when the hardware exists, otherwise
  `estimated` by the engine. Entities carry a `source` attribute.
- **Native energy** (kWh, `total_increasing`, restored across restarts) ready
  for the Energy Dashboard; measured heat-meter counters use the digit-group
  combination from the spec.
- **Live calibration** of the estimation engine via `number` entities (write to
  HA, not the pump).
- **Control behind a gate** (`enable_control`, off by default): setpoints
  (`number`) and modes (`select`, incl. SG Ready) write to the pump, range-
  validated.
- **Importable dashboards** (`dashboards/`), built-in cards only.

## Device tree

`Dimplex WPM` (controller) → `Heating circuit 1`, `Domestic hot water`,
`Heat source`, `Analytics`, and — when present — `Heating circuits 2/3`,
`Swimming pool`, `Ventilation`, `Solar`, `Passive cooling`.

## Installation (HACS custom repository)

1. HACS → Integrations → ⋮ → **Custom repositories** → add this repo URL, type
   **Integration**.
2. Install **Dimplex WPM**, restart Home Assistant.
3. Settings → Devices & Services → **Add Integration** → **Dimplex WPM**.

## Configuration

**Step 1 (connection):** Host, Port (502), Unit ID (1), heat-pump **profile**
(LAK9 / generic), **software version** (H/J/L/M, default M), scan interval,
timeout.

**Step 2 (modules & metering):** which optional modules exist (HC2/3, pool,
ventilation, solar, passive cooling) and which meters are present (electric /
heat / flow sensor / inverter frequency). Suggestions are pre-filled from a
device probe; without a meter the value is estimated.

**Options** (re-configurable): scan interval, modules, capabilities, flow-sensor
entity, include reverse-engineered registers, and **Enable control / write
entities** (the write gate).

## Removal

Settings → Devices & Services → Dimplex WPM → ⋮ → **Delete**. All entities and
devices are removed with the config entry. To uninstall the code, remove the
integration from HACS (or delete `custom_components/dimplex_wpm/`) and restart.

## Dashboards

Import `dashboards/dimplex_wpm.yaml` (Settings → Dashboards → New dashboard →
Edit → raw configuration editor → paste). Five views: Overview, Heat & Energy,
History, Control (only useful with the write gate on), Diagnostics/Calibration.

Entity ids follow the default-naming scheme documented in
[`spec/ENTITY_IDS.md`](spec/ENTITY_IDS.md) — if you renamed entities, adjust the
ids. The dashboards use only built-in cards; `apexcharts-card` is an optional
upgrade for the Energy view (see `spec/DASHBOARD_DESIGN.md`).

For the Energy Dashboard, add **one** electrical-energy entity
(`sensor.analytics_electrical_energy_est`, or the measured equivalent with an
electric meter). The thermal (heat-delivered) sensors are not electricity — do
not add them as grid consumption.

## Notes & limitations

- **Setpoint scaling** for some writable registers is assumed whole-°C (matches
  the working YAML) and should be **verified on a real device** before relying
  on writes. The control gate is off by default and writes are range-validated.
- **Climate** thermostats for HC1 and DHW are available behind the control gate
  (current temperature from a read sensor, target = the writable setpoint).
- Estimation requires the LAK9 profile (calibration) + the inverter-frequency
  register; the generic profile yields read-only entities.

## Status / design

This is the redesign branch. Architecture and rationale live in
[`DESIGN.md`](DESIGN.md); the verified register map in
[`spec/REGISTERS.md`](spec/REGISTERS.md). CI runs hassfest, HACS validation,
ruff and pytest.

**Quality scale** (self-assessment in
[`custom_components/dimplex_wpm/quality_scale.yaml`](custom_components/dimplex_wpm/quality_scale.yaml)):
most of Bronze and Silver is met (config flow, unload, error handling,
parallel-updates, diagnostics, entity translations, async client). Open items
before formally claiming a tier: HA-runtime test coverage (config flow +
coordinator), `entry.runtime_data` migration, and Gold polish (icon
translations, reconfigure flow, exception translations).
