"""Sensor entities for Dimplex WPM."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_ENABLE_BMS_TEMP,
    CONF_ENABLE_EMS,
    CONF_ENABLE_EXTERNAL_LOCK,
    CONF_ENABLE_WRITE_ENTITIES,
    DOMAIN,
    MODULE_DHW,
    MODULE_HC1,
    MODULE_ROOT,
    MODULE_SG,
    DEFAULT_ENABLE_WRITE,
    REG_DHW_TEMPERATURE,
    REG_FAULT_CODE,
    REG_FLOW_TEMPERATURE,
    REG_LOCK_CODE,
    REG_OUTDOOR_TEMPERATURE,
    REG_RETURN_SETPOINT_TEMPERATURE,
    REG_RETURN_TEMPERATURE,
    REG_SENSOR_ERROR_CODE,
    REG_SG_READY_MODE,
    REG_STATUS_CODE,
)
from .device import build_device_info

LOGGER = logging.getLogger(__name__)


@dataclass
class DimplexSensorEntityDescription(SensorEntityDescription):
    """Describes Dimplex sensor entity."""

    value_fn: Callable[[dict[str, Any]], Any] | None = None
    attrs_fn: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any] | None] | None = None
    register: int | None = None
    module: str = MODULE_ROOT


SENSOR_DESCRIPTIONS: tuple[DimplexSensorEntityDescription, ...] = (
    DimplexSensorEntityDescription(
        key="controller_info",
        translation_key="controller_info",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: "online" if data else None,
        attrs_fn=lambda data, entry_data: {
            "host": entry_data.get("host"),
            "port": entry_data.get("port"),
            "unit_id": entry_data.get("unit_id"),
            "register_strategy": data.get("meta", {}).get("register_strategy"),
            "last_update": data.get("meta", {}).get("last_update"),
            "update_success": data.get("meta", {}).get("update_success"),
            "consecutive_failures": data.get("meta", {}).get("consecutive_failures"),
            "capabilities": {
                "sg_ready_write": entry_data.get("enable_write", False),
                "ems_entities": entry_data.get("enable_ems", False),
                "bms_temp": entry_data.get("enable_bms_temp", False),
                "external_lock": entry_data.get("enable_external_lock", False),
            },
        },
    ),
    DimplexSensorEntityDescription(
        key="outdoor_temperature",
        translation_key="outdoor_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data["derived"].get("outdoor_temperature"),
    ),
    DimplexSensorEntityDescription(
        key="return_temperature",
        translation_key="return_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data["derived"].get("return_temperature"),
        module=MODULE_HC1,
    ),
    DimplexSensorEntityDescription(
        key="return_setpoint_temperature",
        translation_key="return_setpoint_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data["derived"].get("return_setpoint_temperature"),
        module=MODULE_HC1,
    ),
    DimplexSensorEntityDescription(
        key="flow_temperature",
        translation_key="flow_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data["derived"].get("flow_temperature"),
        module=MODULE_HC1,
    ),
    DimplexSensorEntityDescription(
        key="dhw_temperature",
        translation_key="dhw_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data["derived"].get("dhw_temperature"),
        module=MODULE_DHW,
    ),
    DimplexSensorEntityDescription(
        key="status_code",
        translation_key="status_code",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["raw"].get(REG_STATUS_CODE),
        register=REG_STATUS_CODE,
    ),
    DimplexSensorEntityDescription(
        key="status_text",
        translation_key="status_text",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["derived"].get("status_text"),
    ),
    DimplexSensorEntityDescription(
        key="lock_code",
        translation_key="lock_code",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["raw"].get(REG_LOCK_CODE),
        register=REG_LOCK_CODE,
    ),
    DimplexSensorEntityDescription(
        key="lock_text",
        translation_key="lock_text",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["derived"].get("lock_text"),
    ),
    DimplexSensorEntityDescription(
        key="fault_code",
        translation_key="fault_code",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["raw"].get(REG_FAULT_CODE),
        register=REG_FAULT_CODE,
    ),
    DimplexSensorEntityDescription(
        key="fault_text",
        translation_key="fault_text",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["derived"].get("fault_text"),
    ),
    DimplexSensorEntityDescription(
        key="sensor_error_code",
        translation_key="sensor_error_code",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["raw"].get(REG_SENSOR_ERROR_CODE),
        register=REG_SENSOR_ERROR_CODE,
    ),
    DimplexSensorEntityDescription(
        key="sensor_error_text",
        translation_key="sensor_error_text",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["derived"].get("sensor_error_text"),
    ),
    DimplexSensorEntityDescription(
        key="sg_ready_code",
        translation_key="sg_ready_code",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["raw"].get(REG_SG_READY_MODE),
        register=REG_SG_READY_MODE,
        module=MODULE_SG,
    ),
    DimplexSensorEntityDescription(
        key="sg_ready_text",
        translation_key="sg_ready_text",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data["derived"].get("sg_ready_text"),
        module=MODULE_SG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    register_usage: dict[int, str] = {}
    entities: list[SensorEntity] = []
    integration_flags = {
        "host": data.get("host"),
        "port": data.get("port"),
        "unit_id": data.get("unit_id"),
        "enable_write": data.get(CONF_ENABLE_WRITE_ENTITIES, DEFAULT_ENABLE_WRITE),
        "enable_ems": data.get(CONF_ENABLE_EMS, False),
        "enable_bms_temp": data.get(CONF_ENABLE_BMS_TEMP, False),
        "enable_external_lock": data.get(CONF_ENABLE_EXTERNAL_LOCK, False),
    }

    for description in SENSOR_DESCRIPTIONS:
        if description.register is not None:
            if description.register in register_usage:
                LOGGER.warning(
                    "Skipping duplicate register %s for %s (already used by %s)",
                    description.register,
                    description.key,
                    register_usage[description.register],
                )
                continue
            register_usage[description.register] = description.key
        entities.append(DimplexSensor(coordinator, entry, description, integration_flags))

    async_add_entities(entities)


class DimplexSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Dimplex sensor."""

    entity_description: DimplexSensorEntityDescription

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        description: DimplexSensorEntityDescription,
        integration_flags: dict[str, Any],
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_has_entity_name = True
        self._attr_translation_key = description.translation_key
        self._integration_flags = integration_flags
        configuration_url = None
        if integration_flags.get("host"):
            configuration_url = f"http://{integration_flags['host']}"
        self._attr_device_info = build_device_info(
            entry,
            description.module,
            host=integration_flags.get("host"),
            configuration_url=configuration_url,
        )
        self._attr_unique_id = f"{entry.entry_id}_{description.module}_{description.key}"

    @property
    def native_value(self):
        data = self.coordinator.data
        if not data or not self.entity_description.value_fn:
            return None
        return self.entity_description.value_fn(data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        data = self.coordinator.data or {}
        if not self.entity_description.attrs_fn:
            return None
        return self.entity_description.attrs_fn(data, self._integration_flags)
