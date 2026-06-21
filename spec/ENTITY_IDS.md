# Dimplex WPM — entity_id reference (derived scheme)

> How HA builds these (confirmed by the pre-M3 audit): entities use
> `has_entity_name = True` with `_attr_name`, **no** `translation_key` /
> `suggested_object_id`. So `entity_id = <platform>.slugify("<device name> <entity name>")`.
> The dashboards in `dashboards/` reference exactly these ids.
>
> **Assumes default naming** — if you rename a device/entity in HA, its
> entity_id changes and you must update the dashboard reference.

## Device-name → entity_id prefix

| Device (module) | Prefix |
|---|---|
| Controller (`controller`) | `dimplex_wpm_` |
| Heating circuit 1 (`hc1`) | `heating_circuit_1_` |
| Heating circuits 2/3 (`hc2_3`) | `heating_circuits_2_3_` |
| Domestic hot water (`dhw`) | `domestic_hot_water_` |
| Swimming pool (`pool`) | `swimming_pool_` |
| Ventilation (`vent`) | `ventilation_` |
| Solar (`solar`) | `solar_` |
| Heat source (`source`) | `heat_source_` |
| Passive cooling (`cooling`) | `passive_cooling_` |
| Analytics (`energy`) | `analytics_` |

Only the Controller carries the `dimplex_wpm_` prefix (it is the hub device,
named "Dimplex WPM"); sub-devices use their own short name as the prefix. This
is standard Home Assistant behaviour with `has_entity_name`.

## Controller (`sensor.` / `binary_sensor.` / `select.`)
- `sensor.dimplex_wpm_outdoor_temperature`
- `sensor.dimplex_wpm_status` (text) · `sensor.dimplex_wpm_status_code` [diag]
- `sensor.dimplex_wpm_lock` · `sensor.dimplex_wpm_lock_code` [diag]
- `sensor.dimplex_wpm_fault` · `sensor.dimplex_wpm_fault_code` [diag]
- `sensor.dimplex_wpm_sensor_error` · `sensor.dimplex_wpm_sensor_error_code` [diag, L/M only]
- `sensor.dimplex_wpm_operating_mode` · `sensor.dimplex_wpm_party_hours` · `sensor.dimplex_wpm_holiday_days`
- `sensor.dimplex_wpm_inverter_frequency` [diag, RE/cap]
- `sensor.dimplex_wpm_sg_ready_state` · `sensor.dimplex_wpm_sg_ready_code` [diag]
- `sensor.dimplex_wpm_controller_info` [diag; host/profile/capabilities in attrs]
- runtimes [diag]: `sensor.dimplex_wpm_compressor_1_runtime`, `..._compressor_2_runtime`,
  `..._primary_pump_fan_runtime`, `..._2nd_heat_generator_runtime`,
  `..._immersion_heater_runtime`, `..._auxiliary_circulation_pump_runtime`
- `binary_sensor.dimplex_wpm_fault_active` · `binary_sensor.dimplex_wpm_lock_active`
- inputs [diag]: `binary_sensor.dimplex_wpm_smartgrid_input_1`, `..._smartgrid_input_2`,
  `..._utility_evu_lockout`, `..._external_lockout`
- output coils [diag]: `binary_sensor.dimplex_wpm_compressor_1`, `..._compressor_2`,
  `..._primary_pump_fan`, `..._2nd_heat_generator`, `..._immersion_heater`,
  `..._auxiliary_circulation_pump`, `..._general_fault_output`,
  `..._heating_pump_m14`, `..._heating_pump_m20`
- control (only with `enable_control`): `select.dimplex_wpm_sg_ready_mode`,
  `select.dimplex_wpm_operating_mode`

## Heating circuit 1 (`hc1`)
- `sensor.heating_circuit_1_flow_temperature` · `..._return_temperature` ·
  `..._return_setpoint_temperature`
- `sensor.heating_circuit_1_room_temperature_1` · `..._room_temperature_2` ·
  `..._room_humidity_1` · `..._room_humidity_2`
- `sensor.heating_circuit_1_heating_pump_m13_runtime` [diag] ·
  `binary_sensor.heating_circuit_1_heating_pump_m13` [diag]
- control: `number.heating_circuit_1_hc1_room_setpoint`,
  `number.heating_circuit_1_hc1_fixed_flow_setpoint`,
  `number.heating_circuit_1_hc1_heating_curve_end`,
  `number.heating_circuit_1_hc1_curve_offset`
- control: `climate.heating_circuit_1_thermostat` (current = room temp/return,
  target = room setpoint)

## Domestic hot water (`dhw`)
- `sensor.domestic_hot_water_dhw_temperature` · `..._dhw_setpoint_temperature`
- `sensor.domestic_hot_water_dhw_pump_runtime` [diag] ·
  `binary_sensor.domestic_hot_water_dhw_pump` [diag]
- control: `number.domestic_hot_water_dhw_setpoint`, `..._dhw_setpoint_minimum`,
  `..._dhw_setpoint_maximum`
- control: `climate.domestic_hot_water_thermostat` (current = DHW temp,
  target = DHW setpoint)

## Heat source (`source`)
- `sensor.heat_source_source_inlet_temperature` · `..._source_outlet_temperature`

## Analytics (`energy`) — present when `estimation_possible` (lak9 profile + inverter freq)
- `sensor.analytics_cop_est` (+ `sensor.analytics_cop_measured` with both meters)
- `sensor.analytics_electrical_power` · `sensor.analytics_heat_output` (source attr)
- `sensor.analytics_compressor_power_est` · `..._heater_power_est` · `..._total_electrical_power_est`
- `sensor.analytics_compressor_heat_output_est` · `..._heater_heat_output_est` ·
  `..._defrost_heat_loss_est` · `..._loop_heat_output_est`
- `sensor.analytics_heat_to_house_est` · `..._heat_to_installation_est` · `..._house_heat_fraction`
- `sensor.analytics_flow_rate` · `sensor.analytics_flow_rate_smoothed`
- `sensor.analytics_temperature_difference` · `sensor.analytics_temperature_difference_rate`
- energy (kWh, total_increasing): `sensor.analytics_electrical_energy_est`,
  `sensor.analytics_heat_energy_est`, `sensor.analytics_heat_energy_to_house_est`,
  `sensor.analytics_heat_energy_to_installation_est`
- calibration [config]: `number.analytics_calibration_dhw_power_factor`,
  `..._calibration_defrost_power_factor`, `..._calibration_defrost_heat_loss_factor`,
  `..._calibration_2nd_source_heater_power`, `..._calibration_main_pump_power`,
  `..._calibration_floor_pump_power`, `..._calibration_alpha_base`,
  `..._calibration_alpha_sensitivity`, `..._calibration_alpha_deadband`

With a heat meter: `sensor.analytics_heating_energy_meter`, `..._dhw_energy_meter`,
`..._environmental_energy_meter` (+ `..._pool_energy_meter` with pool module);
the estimated `..._heat_energy_est` is then suppressed (no double count).
With an electric meter: `analytics_electrical_power` source becomes `measured`.

## Optional modules (only when enabled)
- HC2/3: `sensor.heating_circuits_2_3_hc2_temperature`, `..._hc3_temperature`, setpoints…
- Pool: `sensor.swimming_pool_*` · `number.swimming_pool_pool_setpoint` (control)
- Ventilation: `sensor.ventilation_supply_air_temperature`, `..._supply_fan_speed`, …
- Solar: `sensor.solar_solar_collector_temperature`, `..._solar_tank_temperature`
- Passive cooling: `sensor.passive_cooling_*`
