"""Data update coordinator — register-table driven."""

from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from . import estimation as est
from .const import DEFAULT_SCAN_INTERVAL, get_enum_map
from .modbus_client import DimplexModbusClient
from .profiles import DeviceProfile
from .registers import (
    CAP_ELECTRIC_METER,
    CAP_FLOW_SENSOR,
    CAP_HEAT_METER,
    CAP_INVERTER_FREQ,
    COIL,
    HOLDING,
    active_energy_groups,
    active_registers,
    active_write_registers,
    build_read_plan,
    decode_value,
    energy_total_kwh,
)

LOGGER = logging.getLogger(__name__)


class DimplexDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate Modbus reads and decode them into a flat ``values`` map."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: DimplexModbusClient,
        *,
        scan_interval: int = DEFAULT_SCAN_INTERVAL,
        software_version: str,
        enabled_modules: frozenset[str],
        capabilities: frozenset[str],
        include_re: bool,
        profile: DeviceProfile,
        flow_sensor_entity: str | None = None,
        enable_control: bool = False,
        host: str | None = None,
        port: int | None = None,
        unit_id: int | None = None,
    ) -> None:
        super().__init__(
            hass,
            LOGGER,
            name="Dimplex WPM coordinator",
            update_interval=timedelta(seconds=scan_interval),
        )
        self._client = client
        self.software_version = software_version
        self.enabled_modules = enabled_modules
        self.capabilities = capabilities
        self.profile = profile
        self._flow_sensor_entity = flow_sensor_entity

        # Estimation is possible only with a power LUT and the inverter-frequency
        # register; otherwise we fall back to measured registers where present.
        self.estimation_possible = bool(profile.power_lut) and (
            CAP_INVERTER_FREQ in capabilities
        )
        # Live-tunable calibration (mutated by the number platform).
        self.tunables: dict[str, float | bool] = {
            "k_dhw": profile.k_dhw,
            "k_defrost": profile.k_defrost,
            "k_defrost_loss": profile.k_defrost_loss,
            "heater_w": float(profile.heater_default_w),
            "pump_main_w": 0.0,
            "pump_floor_w": 0.0,
            "alpha_base": profile.alpha_base,
            "alpha_sensitivity": profile.alpha_sensitivity,
            "alpha_deadband": profile.alpha_deadband,
        }
        self._prev_delta_t: float | None = None
        self._prev_delta_t_ts = None
        self._flow_ema: float | None = None

        self.specs = active_registers(
            version=software_version,
            enabled_modules=enabled_modules,
            capabilities=capabilities,
            include_re=include_re,
        )
        self.energy_groups = active_energy_groups(
            enabled_modules=enabled_modules, capabilities=capabilities
        )
        self.enable_control = enable_control
        self.write_specs = (
            active_write_registers(enabled_modules=enabled_modules) if enable_control else []
        )
        extra_holding = {ws.address for ws in self.write_specs}
        self._plan = build_read_plan(
            self.specs, self.energy_groups, software_version, extra_holding
        )

        self._connection_info = {
            "host": host,
            "port": port,
            "unit_id": unit_id,
            "software_version": software_version,
            "profile": profile.key,
        }
        self._consecutive_failures = 0

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            holding, coils = await self._execute_plan()
        except Exception as err:
            self._consecutive_failures += 1
            raise UpdateFailed(f"Error communicating with Modbus device: {err}") from err
        self._consecutive_failures = 0

        values: dict[str, Any] = {"controller_info": "online"}

        for spec in self.specs:
            addr = spec.resolve_address(self.software_version)
            if addr is None:
                continue
            if spec.obj == COIL:
                if addr in coils:
                    values[spec.key] = bool(coils[addr])
                continue
            if addr not in holding:
                continue
            raw = holding[addr]
            if spec.enum:
                mapping = get_enum_map(spec.enum, self.software_version)
                values[spec.key] = mapping.get(raw, f"Unknown ({raw})")
            else:
                values[spec.key] = decode_value(spec, raw)

        for group in self.energy_groups:
            regs = [holding.get(r) for r in group.registers]
            if all(r is not None for r in regs):
                values[group.key] = energy_total_kwh(*regs)  # type: ignore[arg-type]

        # Writable controls: decode current value (number=display, select=raw code).
        for ws in self.write_specs:
            if ws.address in holding:
                values[ws.key] = ws.from_raw(holding[ws.address])

        # Derived problem flags from the raw codes.
        if "fault_code" in values:
            values["fault_active"] = values["fault_code"] != 0
        if "lock_code" in values:
            values["lock_active"] = values["lock_code"] != 0

        self._add_estimation(values)

        meta = {
            "last_update": dt_util.utcnow().isoformat(),
            "update_success": True,
            "consecutive_failures": self._consecutive_failures,
            **self._connection_info,
        }
        return {"values": values, "raw_holding": holding, "raw_coils": coils, "meta": meta}

    def _add_estimation(self, values: dict[str, Any]) -> None:
        """Compute derived power/COP/heat/flow + measured-vs-estimated selection."""
        flow = values.get("flow_temperature")
        ret = values.get("return_temperature")
        outdoor = values.get("outdoor_temperature")
        status = values.get("status_code")
        hz = values.get("inverter_frequency")
        heater_on = bool(values.get("output_2nd_heat_generator"))
        t = self.tunables

        # ΔT and its time derivative (K/min).
        if flow is not None and ret is not None:
            delta_t = round(flow - ret, 2)
            values["delta_t"] = delta_t
            now = dt_util.utcnow()
            if self._prev_delta_t is not None and self._prev_delta_t_ts is not None:
                minutes = (now - self._prev_delta_t_ts).total_seconds() / 60
                if minutes > 0:
                    values["ddelta_t_dt"] = round((delta_t - self._prev_delta_t) / minutes, 3)
            self._prev_delta_t = delta_t
            self._prev_delta_t_ts = now

        # COP from the EN14511 table (independent of metering).
        cop = est.cop_en14511(outdoor, flow, self.profile.cop_table)
        if cop:
            values["cop_estimated"] = cop

        if self.estimation_possible and status is not None:
            comp_w = est.compressor_power_w(
                hz, status, self.profile.power_lut, t["k_dhw"], t["k_defrost"]
            )
            heat_w = est.heater_power_w(heater_on, t["heater_w"])
            pumps_w = t["pump_main_w"] + t["pump_floor_w"]
            total_w = est.total_power_w(comp_w, heat_w, pumps_w)
            values["compressor_power_estimated"] = round(comp_w / 1000, 3)
            values["heater_power_estimated"] = round(heat_w / 1000, 3)
            values["total_power_estimated"] = round(total_w / 1000, 3)

            tc_w = est.thermal_power_compressor_w(comp_w, cop, status)
            tdl_w = est.thermal_power_defrost_loss_w(comp_w, t["k_defrost_loss"], status)
            loop_w = est.thermal_power_loop_w(tc_w, heat_w, tdl_w)
            values["thermal_power_compressor"] = round(tc_w / 1000, 3)
            values["thermal_power_heater"] = round(heat_w / 1000, 3)
            values["thermal_power_defrost_loss"] = round(tdl_w / 1000, 3)
            values["thermal_power_loop"] = round(loop_w / 1000, 3)

            alpha = est.alpha_house(
                values.get("ddelta_t_dt", 0.0),
                t["alpha_base"], t["alpha_sensitivity"], t["alpha_deadband"],
            )
            house_w, inst_w = est.thermal_split(loop_w, alpha)
            values["alpha_house"] = alpha
            values["thermal_power_to_house"] = round(house_w / 1000, 3)
            values["thermal_power_to_installation"] = round(inst_w / 1000, 3)

            # Flow: real sensor when present, else hydraulic estimate.
            flow_rate = self._measured_flow()
            if flow_rate is None:
                flow_rate = est.estimated_flow_m3h(tc_w, values.get("delta_t", 0.0), status)
            values["flow_rate"] = flow_rate
            # EMA-smoothed flow for stabler charts (and stabler downstream use).
            ema_alpha = 0.3
            self._flow_ema = (
                flow_rate
                if self._flow_ema is None
                else round(ema_alpha * flow_rate + (1 - ema_alpha) * self._flow_ema, 2)
            )
            values["flow_rate_smoothed"] = self._flow_ema

        # Preferred (best) power sources + measured COP.
        if CAP_ELECTRIC_METER in self.capabilities and values.get("electrical_power") is not None:
            values["electrical_power_best"] = values["electrical_power"]
        elif "total_power_estimated" in values:
            values["electrical_power_best"] = values["total_power_estimated"]

        if CAP_HEAT_METER in self.capabilities and values.get("heat_output_power") is not None:
            values["heat_output_best"] = values["heat_output_power"]
        elif "thermal_power_loop" in values:
            values["heat_output_best"] = values["thermal_power_loop"]

        elec = values.get("electrical_power")
        heat = values.get("heat_output_power")
        if heat is not None and elec:
            values["cop_measured"] = round(heat / elec, 2)

    def _measured_flow(self) -> float | None:
        """Read an external flow-sensor entity (m³/h) if configured."""
        if not self._flow_sensor_entity or CAP_FLOW_SENSOR not in self.capabilities:
            return None
        state = self.hass.states.get(self._flow_sensor_entity)
        if state is None or state.state in ("unknown", "unavailable", "", None):
            return None
        try:
            return round(float(state.state), 2)
        except (ValueError, TypeError):
            return None

    async def _execute_plan(self) -> tuple[dict[int, int], dict[int, bool]]:
        holding: dict[int, int] = {}
        coils: dict[int, bool] = {}
        for obj, start, count in self._plan:
            if obj == HOLDING:
                data = await self._client.read_holding_registers(start, count)
                if data:
                    for offset, value in enumerate(data):
                        holding[start + offset] = value
            elif obj == COIL:
                bits = await self._client.read_coils(start, count)
                if bits:
                    for offset, value in enumerate(bits):
                        coils[start + offset] = bool(value)
        return holding, coils

    @property
    def write_register(self) -> Callable[[int, int], Any]:
        """Return helper for writing a holding register (used by M2 controls)."""
        return self._client.write_register

    # Backwards-compatible alias used by the SG Ready select.
    @property
    def write_sg_ready(self) -> Callable[[int, int], Any]:
        return self._client.write_register
