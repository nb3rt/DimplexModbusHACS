"""Sensor platform — entities generated from the register table."""

from __future__ import annotations

from typing import Any

from dataclasses import dataclass

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfEnergy
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN, MODULE_ROOT
from .entity import DimplexEntityMixin
from .registers import (
    CAP_ELECTRIC_METER,
    CAP_FLOW_SENSOR,
    CAP_HEAT_METER,
    HOLDING,
    M_ENERGY,
    EnergyGroup,
    RegisterSpec,
)

DEVICE_CLASS_MAP = {
    "temperature": SensorDeviceClass.TEMPERATURE,
    "power": SensorDeviceClass.POWER,
    "energy": SensorDeviceClass.ENERGY,
    "humidity": SensorDeviceClass.HUMIDITY,
    "frequency": SensorDeviceClass.FREQUENCY,
}
STATE_CLASS_MAP = {
    "measurement": SensorStateClass.MEASUREMENT,
    "total_increasing": SensorStateClass.TOTAL_INCREASING,
    "total": SensorStateClass.TOTAL,
}
ENTITY_CATEGORY_MAP = {
    "diagnostic": EntityCategory.DIAGNOSTIC,
    "config": EntityCategory.CONFIG,
}


@dataclass(frozen=True)
class ComputedSpec:
    key: str
    name: str
    unit: str | None = None
    device_class: str | None = None
    icon: str | None = None


# Estimated power/heat quantities (created only when estimation is possible).
ESTIMATED_COMPUTED: tuple[ComputedSpec, ...] = (
    ComputedSpec("compressor_power_estimated", "Compressor power (est.)", "kW", "power", "mdi:gauge"),
    ComputedSpec("heater_power_estimated", "Heater power (est.)", "kW", "power", "mdi:radiator"),
    ComputedSpec("total_power_estimated", "Total electrical power (est.)", "kW", "power", "mdi:flash"),
    ComputedSpec("thermal_power_compressor", "Compressor heat output (est.)", "kW", "power", "mdi:fire"),
    ComputedSpec("thermal_power_heater", "Heater heat output (est.)", "kW", "power", "mdi:fire"),
    ComputedSpec("thermal_power_defrost_loss", "Defrost heat loss (est.)", "kW", "power", "mdi:snowflake-melt"),
    ComputedSpec("thermal_power_loop", "Loop heat output (est.)", "kW", "power", "mdi:fire"),
    ComputedSpec("thermal_power_to_house", "Heat to house (est.)", "kW", "power", "mdi:home-thermometer"),
    ComputedSpec("thermal_power_to_installation", "Heat to installation (est.)", "kW", "power", "mdi:pipe-valve"),
    ComputedSpec("alpha_house", "House heat fraction (α)", None, None, "mdi:home-percent"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create sensor entities from the coordinator's active register set."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    host = data.get("host")
    version = coordinator.software_version
    model = data.get("model")

    entities: list[SensorEntity] = [
        DimplexControllerInfo(coordinator, entry, host=host, version=version, model=model)
    ]
    for spec in coordinator.specs:
        if spec.obj == HOLDING:
            entities.append(
                DimplexSensor(coordinator, entry, spec, host=host, version=version, model=model)
            )
    for group in coordinator.energy_groups:
        entities.append(
            DimplexEnergySensor(coordinator, entry, group, host=host, version=version, model=model)
        )

    # ----- Analytics: computed (measured vs estimated) -----
    caps = coordinator.capabilities

    def computed(key, name, unit, dc, icon, source):
        entities.append(
            DimplexComputedSensor(
                coordinator, entry, key, name, unit, dc, icon, source,
                host=host, version=version, model=model,
            )
        )

    computed("delta_t", "ΔT (flow − return)", "K", None, "mdi:delta", "measured")
    if coordinator.estimation_possible:
        computed("ddelta_t_dt", "ΔT rate", "K/min", None, "mdi:delta", "estimated")
        for cs in ESTIMATED_COMPUTED:
            computed(cs.key, cs.name, cs.unit, cs.device_class, cs.icon, "estimated")
        flow_src = "measured" if CAP_FLOW_SENSOR in caps else "estimated"
        computed("flow_rate", "Flow rate", "m³/h", None, "mdi:water-pump", flow_src)
    if coordinator.profile.cop_table:
        computed("cop_estimated", "COP (est.)", None, None, "mdi:chart-bell-curve", "estimated")
    if CAP_HEAT_METER in caps and CAP_ELECTRIC_METER in caps:
        computed("cop_measured", "COP (measured)", None, None, "mdi:chart-bell-curve", "measured")
    if CAP_ELECTRIC_METER in caps or coordinator.estimation_possible:
        computed(
            "electrical_power_best", "Electrical power", "kW", "power", "mdi:flash",
            "measured" if CAP_ELECTRIC_METER in caps else "estimated",
        )
    if CAP_HEAT_METER in caps or coordinator.estimation_possible:
        computed(
            "heat_output_best", "Heat output", "kW", "power", "mdi:fire",
            "measured" if CAP_HEAT_METER in caps else "estimated",
        )

    # ----- Analytics: integrated energy (kWh) -----
    def energy(key, source_key, name, source):
        entities.append(
            DimplexIntegrationSensor(
                coordinator, entry, key, source_key, name, source,
                host=host, version=version, model=model,
            )
        )

    if CAP_ELECTRIC_METER in caps or coordinator.estimation_possible:
        energy(
            "electrical_energy_kwh", "electrical_power_best", "Electrical energy",
            "measured" if CAP_ELECTRIC_METER in caps else "estimated",
        )
    if CAP_HEAT_METER in caps or coordinator.estimation_possible:
        energy(
            "heat_energy_kwh", "heat_output_best", "Heat energy",
            "measured" if CAP_HEAT_METER in caps else "estimated",
        )
    if coordinator.estimation_possible:
        energy("heat_energy_to_house_kwh", "thermal_power_to_house", "Heat energy to house", "estimated")
        energy(
            "heat_energy_to_installation_kwh", "thermal_power_to_installation",
            "Heat energy to installation", "estimated",
        )

    async_add_entities(entities)


class DimplexSensor(DimplexEntityMixin, CoordinatorEntity, SensorEntity):
    """A register-backed sensor."""

    def __init__(self, coordinator, entry, spec: RegisterSpec, *, host, version, model) -> None:
        CoordinatorEntity.__init__(self, coordinator)
        self._spec = spec
        self._apply_common(
            entry, key=spec.key, module=spec.module, name=spec.name,
            host=host, software_version=version, model=model,
        )
        if spec.device_class:
            self._attr_device_class = DEVICE_CLASS_MAP.get(spec.device_class)
        if spec.state_class:
            self._attr_state_class = STATE_CLASS_MAP.get(spec.state_class)
        if spec.entity_category:
            self._attr_entity_category = ENTITY_CATEGORY_MAP.get(spec.entity_category)
        if spec.unit:
            self._attr_native_unit_of_measurement = spec.unit
        if spec.icon:
            self._attr_icon = spec.icon

    @property
    def native_value(self) -> Any:
        return (self.coordinator.data or {}).get("values", {}).get(self._spec.key)


class DimplexEnergySensor(DimplexEntityMixin, CoordinatorEntity, SensorEntity):
    """A combined digit-group energy counter (kWh)."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR

    def __init__(self, coordinator, entry, group: EnergyGroup, *, host, version, model) -> None:
        CoordinatorEntity.__init__(self, coordinator)
        self._group = group
        self._apply_common(
            entry, key=group.key, module=group.module, name=group.name,
            host=host, software_version=version, model=model,
        )
        self._attr_extra_state_attributes = {"source": "measured"}

    @property
    def native_value(self) -> Any:
        return (self.coordinator.data or {}).get("values", {}).get(self._group.key)


class DimplexControllerInfo(DimplexEntityMixin, CoordinatorEntity, SensorEntity):
    """Diagnostic sensor exposing connection/config metadata."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:heat-pump"

    def __init__(self, coordinator, entry, *, host, version, model) -> None:
        CoordinatorEntity.__init__(self, coordinator)
        self._meta_extra = {
            "host": host,
            "software_version": version,
            "model": model,
        }
        self._apply_common(
            entry, key="controller_info", module=MODULE_ROOT, name="Controller info",
            host=host, software_version=version, model=model,
        )

    @property
    def native_value(self) -> Any:
        return (self.coordinator.data or {}).get("values", {}).get("controller_info")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        meta = (self.coordinator.data or {}).get("meta", {})
        return {
            **self._meta_extra,
            "port": meta.get("port"),
            "unit_id": meta.get("unit_id"),
            "profile": meta.get("profile"),
            "last_update": meta.get("last_update"),
            "consecutive_failures": meta.get("consecutive_failures"),
            "estimation_possible": self.coordinator.estimation_possible,
            "enabled_modules": sorted(self.coordinator.enabled_modules),
            "capabilities": sorted(self.coordinator.capabilities),
        }


class DimplexComputedSensor(DimplexEntityMixin, CoordinatorEntity, SensorEntity):
    """A derived/estimated value read from the coordinator's computed values."""

    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self, coordinator, entry, key, name, unit, device_class, icon, source,
        *, host, version, model,
    ) -> None:
        CoordinatorEntity.__init__(self, coordinator)
        self._key = key
        self._apply_common(
            entry, key=key, module=M_ENERGY, name=name,
            host=host, software_version=version, model=model,
        )
        if device_class:
            self._attr_device_class = DEVICE_CLASS_MAP.get(device_class)
        if unit:
            self._attr_native_unit_of_measurement = unit
        if icon:
            self._attr_icon = icon
        self._attr_extra_state_attributes = {"source": source}

    @property
    def native_value(self) -> Any:
        return (self.coordinator.data or {}).get("values", {}).get(self._key)


class DimplexIntegrationSensor(DimplexEntityMixin, CoordinatorEntity, RestoreSensor):
    """Trapezoidal Riemann integration of a kW power value into kWh."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_suggested_display_precision = 3

    def __init__(
        self, coordinator, entry, key, source_key, name, source,
        *, host, version, model,
    ) -> None:
        CoordinatorEntity.__init__(self, coordinator)
        self._source_key = source_key
        self._energy = 0.0
        self._last_power: float | None = None
        self._last_ts = None
        self._apply_common(
            entry, key=key, module=M_ENERGY, name=name,
            host=host, software_version=version, model=model,
        )
        self._attr_extra_state_attributes = {"source": source, "integrates": source_key}

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_sensor_data()
        if last is not None and last.native_value is not None:
            try:
                self._energy = float(last.native_value)
            except (ValueError, TypeError):
                pass

    @callback
    def _handle_coordinator_update(self) -> None:
        power = (self.coordinator.data or {}).get("values", {}).get(self._source_key)
        now = dt_util.utcnow()
        if power is not None:
            if self._last_power is not None and self._last_ts is not None:
                dt_h = (now - self._last_ts).total_seconds() / 3600
                if dt_h > 0:
                    self._energy += (self._last_power + power) / 2 * dt_h
            self._last_power = power
            self._last_ts = now
        super()._handle_coordinator_update()

    @property
    def native_value(self) -> float:
        return round(self._energy, 3)

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success
