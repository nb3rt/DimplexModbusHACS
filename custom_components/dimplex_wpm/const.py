"""Constants for the Dimplex WPM integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "dimplex_wpm"

DEFAULT_PORT: Final = 502
DEFAULT_UNIT_ID: Final = 1
DEFAULT_SCAN_INTERVAL: Final = 30
DEFAULT_TIMEOUT: Final = 5
DEFAULT_ENABLE_WRITE: Final = False
DEFAULT_SOFTWARE_VERSION: Final = "H"

CONF_HOST: Final = "host"
CONF_PORT: Final = "port"
CONF_UNIT_ID: Final = "unit_id"
CONF_SCAN_INTERVAL: Final = "scan_interval"
CONF_TIMEOUT: Final = "timeout"
CONF_SOFTWARE_VERSION: Final = "software_version"
CONF_REGISTER_STRATEGY: Final = "register_strategy"
CONF_ENABLE_WRITE_ENTITIES: Final = "enable_write_entities"
CONF_ENABLE_EMS: Final = "enable_ems_entities"
CONF_ENABLE_BMS_TEMP: Final = "enable_bms_temp"
CONF_ENABLE_EXTERNAL_LOCK: Final = "enable_external_lock"

REGISTER_STRATEGY_AUTO: Final = "auto"
REGISTER_STRATEGY_HOLDING: Final = "holding"
REGISTER_STRATEGY_INPUT: Final = "input"

REGISTER_STRATEGY_MAP: Final = {
    REGISTER_STRATEGY_AUTO: REGISTER_STRATEGY_AUTO,
    REGISTER_STRATEGY_HOLDING: REGISTER_STRATEGY_HOLDING,
    REGISTER_STRATEGY_INPUT: REGISTER_STRATEGY_INPUT,
}

SOFTWARE_VERSIONS: Final = ["H", "J", "L", "M"]

REG_OUTDOOR_TEMPERATURE: Final = 1
REG_RETURN_TEMPERATURE: Final = 2
REG_DHW_TEMPERATURE: Final = 3
REG_FLOW_TEMPERATURE: Final = 5
REG_RETURN_SETPOINT_TEMPERATURE: Final = 53

REG_STATUS_CODE: Final = 103
REG_LOCK_CODE: Final = 104
REG_FAULT_CODE: Final = 105
REG_SENSOR_ERROR_CODE: Final = 106

REG_SG_READY_MODE: Final = 5167

STATUS_MAP: Final = {
    0: "Off",
    1: "Heat pump on – heating",
    2: "Heating",
    3: "Heat pump on – swimming pool",
    4: "Domestic hot water",
    5: "Cooling (heat pump + 2nd heat generator)",
    6: "Swimming pool + 2nd heat generator",
    7: "Domestic hot water + 2nd heat generator",
    8: "Primary pump pre-run",
    9: "Heating purge",
    10: "Defrost (locked – see locks)",
    11: "Flow monitoring / lower operating limit",
    12: "Low-pressure limit",
    13: "Low-pressure shutdown",
    14: "High-pressure safety",
    15: "Anti short-cycling lock",
    16: "Minimum standstill time",
    17: "Grid load limitation",
    18: "Flow monitoring",
    19: "Second heat generator active",
    20: "Low-pressure (brine/source)",
    21: "Heat pump on – defrost",
    22: "Upper operating limit",
    23: "External lock",
    24: "Cooling mode switch delay / cooling operating mode",
    25: "Frost protection (cooling)",
    26: "Flow temperature limit",
    27: "Dew point monitor",
    28: "Dew point",
    29: "Passive cooling",
    30: "Lock (see lock register)",
}

LOCK_MAP: Final = {
    0: "No lock",
    1: "High-temperature operating limit / outdoor temperature",
    2: "Volume flow / heat-pump operating limit / bivalent-alternative",
    3: "Regenerative / bivalent-regenerative",
    4: "Return temperature limit",
    5: "Function check / DHW post-heating / DHW",
    6: "High-temperature operating limit / system check",
    7: "System check / utility (EVU) lockout",
    8: "Delay switching to cooling",
    9: "Pump pre-run / high pressure",
    10: "Minimum standstill time / low pressure",
    11: "Grid load limitation / flow",
    12: "Anti short-cycling lock / soft starter",
    13: "DHW post-heating",
    14: "Regenerative",
    15: "Utility (EVU) lockout",
    16: "Soft starter",
    17: "Flow",
    18: "Heat-pump operating limit",
    19: "High pressure",
    20: "Low pressure",
    21: "Heat-source operating limit",
    23: "System limit",
    24: "Primary-circuit load",
    25: "External lock",
    31: "Warm-up",
    33: "EvD initialization",
    34: "Second heat generator enabled",
    35: "Fault (see fault register)",
    36: "Pump pre-run",
    37: "Minimum standstill time",
    38: "Grid load limitation",
    39: "Anti short-cycling lock",
    40: "Heat-source operating limit",
    41: "External lock",
    42: "Second heat generator",
    43: "Fault (see fault register)",
}

FAULT_MAP: Final = {
    0: "No fault",
    1: "Fault N17.1",
    2: "Fault N17.2",
    3: "Fault N17.3 / compressor load",
    4: "Fault N17.4 / coding",
    5: "Low pressure",
    6: "Electronic expansion valve / frost protection",
    7: "Outdoor sensor short or open circuit",
    8: "Return sensor short or open circuit",
    9: "DHW sensor short or open circuit",
    10: "WPIO / frost protection sensor short or open circuit",
    11: "2nd heating circuit sensor short or open circuit",
    12: "Inverter / anti-freeze sensor short or open circuit",
    13: "WQIF / low pressure brine",
    14: "Motor protection primary",
    15: "Sensor fault / flow",
    16: "Low pressure brine / DHW",
    17: "High pressure",
    19: "Primary circuit fault / hot gas thermostat",
    20: "Defrost fault / cooling operating limit",
    21: "Low pressure brine fault",
    22: "DHW fault",
    23: "Compressor load fault / temperature difference",
    24: "Coding fault",
    25: "Low pressure fault",
    26: "Frost protection fault",
    28: "High pressure fault",
    29: "Temperature difference fault",
    30: "Hot gas thermostat fault",
    31: "Flow fault",
}

SENSOR_ERROR_MAP: Final = {}

SG_READY_MAP: Final = {
    0: "Hardware",
    10: "Yellow",
    11: "Green",
    12: "Red",
    13: "Deep Green",
}

SG_READY_REVERSE: Final = {value: key for key, value in SG_READY_MAP.items()}

STATUS_MAP_BY_VERSION: Final = {version: STATUS_MAP for version in SOFTWARE_VERSIONS}
LOCK_MAP_BY_VERSION: Final = {version: LOCK_MAP for version in SOFTWARE_VERSIONS}
FAULT_MAP_BY_VERSION: Final = {version: FAULT_MAP for version in SOFTWARE_VERSIONS}
SENSOR_ERROR_MAP_BY_VERSION: Final = {
    version: SENSOR_ERROR_MAP for version in SOFTWARE_VERSIONS
}

DEVICE_MANUFACTURER: Final = "Dimplex"
DEVICE_NAME: Final = "Dimplex WPM"

MODULE_ROOT: Final = "controller"
MODULE_HC1: Final = "hc1"
MODULE_DHW: Final = "dhw"
MODULE_SG: Final = "sg"

MODULE_NAME_MAP: Final = {
    MODULE_ROOT: "Dimplex WPM Controller",
    MODULE_HC1: "Dimplex Heating Circuit 1",
    MODULE_DHW: "Dimplex Domestic Hot Water",
    MODULE_SG: "Dimplex Smart Grid",
}
