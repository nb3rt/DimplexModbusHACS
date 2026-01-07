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

# Dimplex documentation uses 1-based register numbers and the device expects 1-based addresses.
REGISTER_OFFSET: Final = 0

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

STATUS_MAP_LM: Final = {
    0: "Off",
    1: "Off",
    2: "Heating",
    3: "Swimming pool",
    4: "Domestic hot water",
    5: "Cooling",
    6: "Reserved",
    7: "Reserved",
    8: "Reserved",
    9: "Reserved",
    10: "Defrost",
    11: "Flow monitoring",
    12: "Reserved",
    13: "Reserved",
    14: "Reserved",
    15: "Reserved",
    16: "Reserved",
    17: "Reserved",
    18: "Reserved",
    19: "Reserved",
    20: "Reserved",
    21: "Reserved",
    22: "Reserved",
    23: "Reserved",
    24: "Operating mode switch delay",
    25: "Reserved",
    26: "Reserved",
    27: "Reserved",
    28: "Reserved",
    29: "Passive cooling",
    30: "Lock (see lock register)",
}

STATUS_MAP_HJ: Final = {
    0: "Off",
    1: "Heat pump on – heating",
    2: "Heat pump on – heating",
    3: "Heat pump on – swimming pool",
    4: "Heat pump on – domestic hot water",
    5: "Heat pump on – heating + 2nd heat generator",
    6: "Heat pump on – swimming pool + 2nd heat generator",
    7: "Heat pump on – domestic hot water + 2nd heat generator",
    8: "Primary pump pre-run",
    9: "Heating purge",
    10: "Lock (see lock register for J software)",
    11: "Lower operating limit",
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
    24: "Cooling operating mode",
    25: "Frost protection (cooling)",
    26: "Flow temperature limit",
    27: "Dew point monitor",
    28: "Dew point",
    29: "Reserved",
    30: "Reserved",
}

LOCK_MAP_LM: Final = {
    0: "No lock",
    1: "High temperature operating limit",
    2: "Volume flow",
    3: "Reserved",
    4: "Reserved",
    5: "Function check",
    6: "High temperature operating limit",
    7: "System check",
    8: "Delay switching to cooling",
    9: "Pump pre-run",
    10: "Minimum standstill time",
    11: "Grid load limitation",
    12: "Anti short-cycling lock",
    13: "Domestic hot water post-heating",
    14: "Regenerative",
    15: "Utility (EVU) lockout",
    16: "Soft starter",
    17: "Flow",
    18: "Heat pump operating limit",
    19: "High pressure",
    20: "Low pressure",
    21: "Heat source operating limit",
    23: "System limit",
    24: "Primary circuit load",
    25: "External lock",
    29: "Inverter",
    31: "Warm-up",
    33: "EvD initialization",
    34: "Second heat generator enabled",
    35: "Fault (see fault register)",
    36: "Reserved",
    37: "Reserved",
    38: "Reserved",
    39: "Reserved",
    40: "Reserved",
    41: "Reserved",
    42: "Reserved",
    43: "Reserved",
}

LOCK_MAP_J: Final = {
    0: "No lock",
    1: "Outdoor temperature",
    2: "Heat pump operating limit",
    3: "Regenerative",
    4: "Reserved",
    5: "Domestic hot water post-heating",
    6: "System check",
    7: "Utility (EVU) lockout",
    8: "Reserved",
    9: "High pressure",
    10: "Low pressure",
    11: "Flow",
    12: "Soft starter",
    13: "Reserved",
    14: "Reserved",
    15: "Reserved",
    16: "Reserved",
    17: "Reserved",
    18: "Reserved",
    19: "Reserved",
    20: "Reserved",
    21: "Reserved",
    23: "Reserved",
    24: "Reserved",
    25: "Reserved",
    29: "Reserved",
    31: "Reserved",
    33: "Reserved",
    34: "Reserved",
    35: "Reserved",
    36: "Pump pre-run",
    37: "Minimum standstill time",
    38: "Grid load limitation",
    39: "Anti short-cycling lock",
    40: "Heat source operating limit",
    41: "External lock",
    42: "Second heat generator",
    43: "Fault (see fault register)",
}

LOCK_MAP_H: Final = {
    0: "No lock",
    1: "Reserved",
    2: "Bivalent alternative",
    3: "Bivalent regenerative",
    4: "Return temperature",
    5: "Domestic hot water",
    6: "System check",
    7: "Utility (EVU) lockout",
    8: "Reserved",
    9: "Reserved",
    10: "Reserved",
    11: "Reserved",
    12: "Reserved",
    13: "Reserved",
    14: "Reserved",
    15: "Reserved",
    16: "Reserved",
    17: "Reserved",
    18: "Reserved",
    19: "Reserved",
    20: "Reserved",
    21: "Reserved",
    23: "Reserved",
    24: "Reserved",
    25: "Reserved",
    29: "Reserved",
    31: "Reserved",
    33: "Reserved",
    34: "Reserved",
    35: "Reserved",
    36: "Reserved",
    37: "Reserved",
    38: "Reserved",
    39: "Reserved",
    40: "Reserved",
    41: "Reserved",
    42: "Reserved",
    43: "Reserved",
}

FAULT_MAP_LM: Final = {
    0: "No fault",
    1: "Fault N17.1",
    2: "Fault N17.2",
    3: "Fault N17.3",
    4: "Fault N17.4",
    5: "Reserved",
    6: "Electronic expansion valve",
    7: "Reserved",
    8: "Reserved",
    9: "Reserved",
    10: "WPIO",
    11: "Reserved",
    12: "Inverter",
    13: "WQIF",
    14: "Reserved",
    15: "Sensor fault",
    16: "Low pressure brine",
    17: "Reserved",
    19: "Primary circuit fault",
    20: "Defrost fault",
    21: "Low pressure brine fault",
    22: "Domestic hot water fault",
    23: "Compressor load fault",
    24: "Coding fault",
    25: "Low pressure fault",
    26: "Frost protection fault",
    28: "High pressure fault",
    29: "Temperature difference fault",
    30: "Hot gas thermostat fault",
    31: "Flow fault",
    32: "Warm-up fault",
}

FAULT_MAP_HJ: Final = {
    0: "No fault",
    1: "Fault N17.1",
    2: "Fault N17.2",
    3: "Compressor load",
    4: "Coding",
    5: "Low pressure",
    6: "Frost protection",
    7: "Outdoor sensor short or open circuit",
    8: "Return sensor short or open circuit",
    9: "Domestic hot water sensor short or open circuit",
    10: "Frost protection sensor short or open circuit",
    11: "2nd heating circuit sensor short or open circuit",
    12: "Anti-freeze sensor short or open circuit",
    13: "Low pressure brine",
    14: "Motor protection primary",
    15: "Flow",
    16: "Domestic hot water",
    17: "High pressure",
    19: "Hot gas thermostat",
    20: "Cooling operating limit",
    21: "Reserved",
    22: "Reserved",
    23: "Temperature difference",
    24: "Reserved",
    25: "Reserved",
    26: "Reserved",
    28: "Reserved",
    29: "Reserved",
    30: "Reserved",
    31: "Reserved",
    32: "Reserved",
}

SENSOR_ERROR_MAP_LM: Final = {
    1: "Outdoor sensor (R1)",
    2: "Return sensor (R2)",
    3: "Domestic hot water sensor (R3)",
    4: "Coding (R7)",
    5: "Flow sensor (R9)",
    6: "2nd heating circuit sensor (R5)",
    7: "3rd heating circuit sensor (R13)",
    8: "Regenerative sensor (R13)",
    9: "Room sensor 1",
    10: "Room sensor 2",
    11: "Heat source outlet sensor (R6)",
    12: "Heat source inlet sensor (R24)",
    14: "Collector sensor (R23)",
    15: "Low-pressure sensor (R25)",
    16: "High-pressure sensor (R26)",
    17: "Room humidity 1",
    18: "Room humidity 2",
    19: "Frost protection cooling sensor",
    20: "Hot gas",
    21: "Return sensor (R2.1)",
    22: "Swimming pool sensor (R20)",
    23: "Flow sensor passive cooling (R11)",
    24: "Return sensor passive cooling (R4)",
    26: "Solar storage sensor (R22)",
    28: "Heating demand sensor (R2.2)",
    29: "RTM Econ",
    30: "Cooling demand sensor (R39)",
}
SENSOR_ERROR_MAP_EMPTY: Final = {}
SENSOR_ERROR_MAP: Final = SENSOR_ERROR_MAP_LM

SG_READY_MAP: Final = {
    0: "Hardware",
    10: "Yellow",
    11: "Green",
    12: "Red",
    13: "Deep Green",
}

SG_READY_REVERSE: Final = {value: key for key, value in SG_READY_MAP.items()}

STATUS_MAP_BY_VERSION: Final = {
    "H": STATUS_MAP_HJ,
    "J": STATUS_MAP_HJ,
    "L": STATUS_MAP_LM,
    "M": STATUS_MAP_LM,
}
LOCK_MAP_BY_VERSION: Final = {
    "H": LOCK_MAP_H,
    "J": LOCK_MAP_J,
    "L": LOCK_MAP_LM,
    "M": LOCK_MAP_LM,
}
FAULT_MAP_BY_VERSION: Final = {
    "H": FAULT_MAP_HJ,
    "J": FAULT_MAP_HJ,
    "L": FAULT_MAP_LM,
    "M": FAULT_MAP_LM,
}
SENSOR_ERROR_MAP_BY_VERSION: Final = {
    "H": SENSOR_ERROR_MAP_EMPTY,
    "J": SENSOR_ERROR_MAP_EMPTY,
    "L": SENSOR_ERROR_MAP_LM,
    "M": SENSOR_ERROR_MAP_LM,
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
