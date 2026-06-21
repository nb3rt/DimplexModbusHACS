"""Canonical Dimplex WPM register table — single source of truth.

Pure data + helpers, intentionally FREE of Home Assistant imports so it can be
unit-tested stand-alone. Platform files map the string-typed metadata
(device_class / state_class / entity_category / unit) onto HA enums.

Derived from ``spec/REGISTERS.md`` (adversarially verified against the official
Dimplex NWPM Modbus TCP wiki). Key facts encoded here:

* Analog values are **holding** registers (FC03); digital are **coils** (FC01).
  There is no FC04 (input registers) on this device.
* Status / lock / fault / sensor-error register *addresses* are firmware-version
  dependent (see ``address`` dicts). Target firmware is L/M.
* Energy registers 5096-5129 are **digit groups of one counter**, not quarters
  (see :class:`EnergyGroup`).
* Real power/energy registers exist only on metered installs → gated by
  ``capability`` so estimation can take over when absent (M1).
"""

from __future__ import annotations

from dataclasses import dataclass

# ----- object types -------------------------------------------------------
HOLDING = "holding"
COIL = "coil"

# ----- device-tree modules (medium tree) ----------------------------------
M_CONTROLLER = "controller"
M_HC1 = "hc1"
M_HC2_3 = "hc2_3"
M_DHW = "dhw"
M_POOL = "pool"
M_VENT = "vent"
M_SOLAR = "solar"
M_SOURCE = "source"
M_COOLING = "cooling"
M_ENERGY = "energy"  # "Analytics" device (measured power/energy now; estimates in M1)

ALL_MODULES = (
    M_CONTROLLER, M_HC1, M_HC2_3, M_DHW, M_POOL, M_VENT, M_SOLAR,
    M_SOURCE, M_COOLING, M_ENERGY,
)
# Modules that are always present (cannot be toggled off).
CORE_MODULES = frozenset({M_CONTROLLER, M_HC1, M_DHW, M_SOURCE, M_ENERGY})
# Optional modules gated by profile/installation.
OPTIONAL_MODULES = (M_HC2_3, M_POOL, M_VENT, M_SOLAR, M_COOLING)

# ----- capabilities (per installation) ------------------------------------
CAP_ELECTRIC_METER = "electric_meter"
CAP_HEAT_METER = "heat_meter"
CAP_FLOW_SENSOR = "flow_sensor"
CAP_INVERTER_FREQ = "inverter_freq"

# ----- enum map keys (resolved in coordinator against const maps) ---------
ENUM_STATUS = "status"
ENUM_LOCK = "lock"
ENUM_FAULT = "fault"
ENUM_SENSOR_ERROR = "sensor_error"
ENUM_SG_READY = "sg_ready"
ENUM_OPERATING_MODE = "operating_mode"

# Max registers/coils per Modbus transaction (conservative; spec allows 125).
MAX_READ_CHUNK = 100
# Split a cluster when the address gap exceeds this (keeps reads tight).
CLUSTER_GAP = 8


@dataclass(frozen=True)
class RegisterSpec:
    """One readable datapoint → one entity."""

    key: str
    address: int | dict  # int, or {version: addr|None} for version-dependent regs
    obj: str = HOLDING
    signed: bool = False
    scale: float = 1.0
    unit: str | None = None
    device_class: str | None = None
    state_class: str | None = None
    entity_category: str | None = None  # "diagnostic" | "config" | None
    module: str = M_CONTROLLER
    enum: str | None = None
    module_flag: str | None = None  # optional module that must be enabled
    capability: str | None = None  # capability that must be present
    re_only: bool = False  # reverse-engineered (not in official spec)
    icon: str | None = None
    name: str | None = None

    def resolve_address(self, version: str) -> int | None:
        """Return the register address for ``version`` (None if N/A)."""
        if isinstance(self.address, dict):
            return self.address.get(version)
        return self.address


@dataclass(frozen=True)
class EnergyGroup:
    """A cumulative kWh counter split across three digit-group registers.

    ``total = reg_9_12 * 1e8 + reg_5_8 * 1e4 + reg_1_4`` (kWh).
    """

    key: str
    reg_1_4: int
    reg_5_8: int
    reg_9_12: int
    name: str
    module: str = M_ENERGY
    capability: str = CAP_HEAT_METER

    @property
    def registers(self) -> tuple[int, int, int]:
        return (self.reg_1_4, self.reg_5_8, self.reg_9_12)


# Temperature defaults (most analog temps are int16, 0.1 °C, measurement).
def _temp(key, address, module, name, *, category=None, flag=None, cap=None, re=False):
    return RegisterSpec(
        key=key, address=address, obj=HOLDING, signed=True, scale=0.1,
        unit="°C", device_class="temperature", state_class="measurement",
        entity_category=category, module=module, name=name, module_flag=flag,
        capability=cap, re_only=re,
    )


REGISTERS: tuple[RegisterSpec, ...] = (
    # ===== Controller: ambient, mode, diagnostics =====
    _temp("outdoor_temperature", 1, M_CONTROLLER, "Outdoor temperature"),
    RegisterSpec(
        "inverter_frequency", 114, scale=0.1, unit="Hz", device_class="frequency",
        state_class="measurement", entity_category="diagnostic",
        module=M_CONTROLLER, name="Inverter frequency", re_only=True,
        capability=CAP_INVERTER_FREQ, icon="mdi:sine-wave",
    ),
    RegisterSpec(
        "operating_mode", 5015, module=M_CONTROLLER, enum=ENUM_OPERATING_MODE,
        name="Operating mode", icon="mdi:tune",
    ),
    RegisterSpec(
        "party_hours", 5016, unit="h", state_class="measurement",
        entity_category="diagnostic", module=M_CONTROLLER, name="Party hours",
        icon="mdi:party-popper",
    ),
    RegisterSpec(
        "holiday_days", 5017, unit="d", state_class="measurement",
        entity_category="diagnostic", module=M_CONTROLLER, name="Holiday days",
        icon="mdi:beach",
    ),
    # status / lock / fault / sensor-error — version-dependent ADDRESSES
    RegisterSpec(
        "status_code", {"L": 103, "M": 103, "J": 43, "H": 14},
        entity_category="diagnostic", module=M_CONTROLLER, name="Status code",
    ),
    RegisterSpec(
        "status_text", {"L": 103, "M": 103, "J": 43, "H": 14},
        module=M_CONTROLLER, enum=ENUM_STATUS, name="Status", icon="mdi:heat-pump",
    ),
    RegisterSpec(
        "lock_code", {"L": 104, "M": 104, "J": 59, "H": 94},
        entity_category="diagnostic", module=M_CONTROLLER, name="Lock code",
    ),
    RegisterSpec(
        "lock_text", {"L": 104, "M": 104, "J": 59, "H": 94},
        module=M_CONTROLLER, enum=ENUM_LOCK, name="Lock", icon="mdi:lock-alert",
    ),
    RegisterSpec(
        "fault_code", {"L": 105, "M": 105, "J": 42, "H": 13},
        entity_category="diagnostic", module=M_CONTROLLER, name="Fault code",
    ),
    RegisterSpec(
        "fault_text", {"L": 105, "M": 105, "J": 42, "H": 13},
        module=M_CONTROLLER, enum=ENUM_FAULT, name="Fault", icon="mdi:alert-circle",
    ),
    RegisterSpec(
        "sensor_error_code", {"L": 106, "M": 106, "J": None, "H": None},
        entity_category="diagnostic", module=M_CONTROLLER, name="Sensor error code",
    ),
    RegisterSpec(
        "sensor_error_text", {"L": 106, "M": 106, "J": None, "H": None},
        module=M_CONTROLLER, enum=ENUM_SENSOR_ERROR, name="Sensor error",
        icon="mdi:thermometer-alert",
    ),
    # ===== Runtimes (diagnostic, hours, total_increasing) =====
    RegisterSpec("runtime_compressor_1", 72, unit="h", state_class="total_increasing",
                 entity_category="diagnostic", module=M_CONTROLLER, name="Compressor 1 runtime", icon="mdi:timer-cog"),
    RegisterSpec("runtime_compressor_2", 73, unit="h", state_class="total_increasing",
                 entity_category="diagnostic", module=M_CONTROLLER, name="Compressor 2 runtime", icon="mdi:timer-cog"),
    RegisterSpec("runtime_primary_pump", 74, unit="h", state_class="total_increasing",
                 entity_category="diagnostic", module=M_CONTROLLER, name="Primary pump / fan runtime", icon="mdi:timer-cog"),
    RegisterSpec("runtime_2nd_heat_generator", 75, unit="h", state_class="total_increasing",
                 entity_category="diagnostic", module=M_CONTROLLER, name="2nd heat generator runtime", icon="mdi:timer-cog"),
    RegisterSpec("runtime_heating_pump_m13", 76, unit="h", state_class="total_increasing",
                 entity_category="diagnostic", module=M_HC1, name="Heating pump M13 runtime", icon="mdi:timer-cog"),
    RegisterSpec("runtime_dhw_pump", 77, unit="h", state_class="total_increasing",
                 entity_category="diagnostic", module=M_DHW, name="DHW pump runtime", icon="mdi:timer-cog"),
    RegisterSpec("runtime_immersion_heater", 78, unit="h", state_class="total_increasing",
                 entity_category="diagnostic", module=M_CONTROLLER, name="Immersion heater runtime", icon="mdi:timer-cog"),
    RegisterSpec("runtime_pool_pump", 79, unit="h", state_class="total_increasing",
                 entity_category="diagnostic", module=M_POOL, module_flag=M_POOL, name="Pool pump runtime", icon="mdi:timer-cog"),
    RegisterSpec("runtime_aux_circulation_pump", 71, unit="h", state_class="total_increasing",
                 entity_category="diagnostic", module=M_CONTROLLER, name="Auxiliary circulation pump runtime", icon="mdi:timer-cog"),

    # ===== HC1 =====
    _temp("flow_temperature", 5, M_HC1, "Flow temperature"),
    _temp("return_temperature", 2, M_HC1, "Return temperature"),
    _temp("return_setpoint_temperature", 53, M_HC1, "Return setpoint temperature", category="diagnostic"),
    _temp("room_temperature_1", 11, M_HC1, "Room temperature 1"),
    _temp("room_temperature_2", 12, M_HC1, "Room temperature 2"),
    RegisterSpec("room_humidity_1", 13, signed=True, scale=0.1, unit="%",
                 device_class="humidity", state_class="measurement", module=M_HC1, name="Room humidity 1"),
    RegisterSpec("room_humidity_2", 14, signed=True, scale=0.1, unit="%",
                 device_class="humidity", state_class="measurement", module=M_HC1, name="Room humidity 2"),

    # ===== HC2/3 (optional) =====
    _temp("hc2_temperature", 9, M_HC2_3, "HC2 temperature", flag=M_HC2_3),
    _temp("hc2_setpoint_temperature", 54, M_HC2_3, "HC2 setpoint temperature", category="diagnostic", flag=M_HC2_3),
    _temp("hc3_temperature", 10, M_HC2_3, "HC3 temperature", flag=M_HC2_3),
    _temp("hc3_setpoint_temperature", 55, M_HC2_3, "HC3 setpoint temperature", category="diagnostic", flag=M_HC2_3),

    # ===== DHW =====
    _temp("dhw_temperature", 3, M_DHW, "DHW temperature"),
    _temp("dhw_setpoint_temperature", 58, M_DHW, "DHW setpoint temperature", category="diagnostic"),

    # ===== Source =====
    _temp("source_inlet_temperature", 6, M_SOURCE, "Source inlet temperature"),
    _temp("source_outlet_temperature", 7, M_SOURCE, "Source outlet temperature"),

    # ===== Passive cooling (optional) =====
    _temp("cooling_flow_temperature", 19, M_COOLING, "Passive cooling flow temperature", flag=M_COOLING),
    _temp("cooling_return_temperature", 20, M_COOLING, "Passive cooling return temperature", flag=M_COOLING),
    _temp("cooling_primary_return_temperature", 21, M_COOLING, "Cooling primary return temperature", flag=M_COOLING),

    # ===== Solar (optional) — collector shares reg 10 with HC3 by config =====
    _temp("solar_collector_temperature", 10, M_SOLAR, "Solar collector temperature", flag=M_SOLAR, re=False),
    _temp("solar_tank_temperature", 23, M_SOLAR, "Solar tank temperature", flag=M_SOLAR),

    # ===== Ventilation (optional) =====
    _temp("vent_outdoor_air_temperature", 120, M_VENT, "Ventilation outdoor air temperature", flag=M_VENT),
    _temp("vent_supply_air_temperature", 121, M_VENT, "Ventilation supply air temperature", flag=M_VENT),
    _temp("vent_extract_air_temperature", 122, M_VENT, "Ventilation extract air temperature", flag=M_VENT),
    _temp("vent_exhaust_air_temperature", 123, M_VENT, "Ventilation exhaust air temperature", flag=M_VENT),
    RegisterSpec("vent_supply_fan_speed", 125, signed=True, unit="rpm", state_class="measurement",
                 module=M_VENT, module_flag=M_VENT, name="Ventilation supply fan speed", icon="mdi:fan"),
    RegisterSpec("vent_extract_fan_speed", 126, signed=True, unit="rpm", state_class="measurement",
                 module=M_VENT, module_flag=M_VENT, name="Ventilation extract fan speed", icon="mdi:fan"),
    RegisterSpec("vent_level", 5034, state_class="measurement", entity_category="diagnostic",
                 module=M_VENT, module_flag=M_VENT, name="Ventilation level", icon="mdi:fan-chevron-up"),

    # ===== Smart Grid (read; control select added in M2) =====
    RegisterSpec("sg_ready_code", 5167, entity_category="diagnostic", module=M_CONTROLLER, name="SG Ready code"),
    RegisterSpec("sg_ready_text", 5167, module=M_CONTROLLER, enum=ENUM_SG_READY,
                 name="SG Ready state", icon="mdi:solar-power"),

    # ===== Energy management: measured powers (metered installs only) =====
    RegisterSpec("heat_output_power", 5168, signed=True, scale=0.01, unit="kW",
                 device_class="power", state_class="measurement", module=M_ENERGY,
                 capability=CAP_HEAT_METER, name="Heat output power"),
    RegisterSpec("electrical_power", 5170, signed=True, scale=0.01, unit="kW",
                 device_class="power", state_class="measurement", module=M_ENERGY,
                 capability=CAP_ELECTRIC_METER, name="Electrical power"),
    RegisterSpec("pv_surplus", 5182, signed=True, scale=0.01, unit="kW",
                 device_class="power", state_class="measurement", module=M_ENERGY,
                 entity_category="diagnostic", capability=CAP_ELECTRIC_METER,
                 name="PV surplus", icon="mdi:solar-power-variant"),

    # ===== Coils — digital inputs (diagnostic) =====
    RegisterSpec("smartgrid_input_1", 3, obj=COIL, entity_category="diagnostic",
                 module=M_CONTROLLER, name="SmartGrid input 1"),
    RegisterSpec("smartgrid_input_2", 4, obj=COIL, entity_category="diagnostic",
                 module=M_CONTROLLER, name="SmartGrid input 2"),
    RegisterSpec("utility_lockout", 5, obj=COIL, device_class="lock",
                 entity_category="diagnostic", module=M_CONTROLLER, name="Utility (EVU) lockout"),
    RegisterSpec("external_lockout", 6, obj=COIL, device_class="lock",
                 entity_category="diagnostic", module=M_CONTROLLER, name="External lockout"),

    # ===== Coils — digital outputs (diagnostic, running indicators) =====
    RegisterSpec("output_compressor_1", 41, obj=COIL, device_class="running",
                 entity_category="diagnostic", module=M_CONTROLLER, name="Compressor 1"),
    RegisterSpec("output_compressor_2", 42, obj=COIL, device_class="running",
                 entity_category="diagnostic", module=M_CONTROLLER, name="Compressor 2"),
    RegisterSpec("output_primary_pump", 43, obj=COIL, device_class="running",
                 entity_category="diagnostic", module=M_CONTROLLER, name="Primary pump / fan"),
    RegisterSpec("output_2nd_heat_generator", 44, obj=COIL, device_class="running",
                 entity_category="diagnostic", module=M_CONTROLLER, name="2nd heat generator"),
    RegisterSpec("output_heating_pump_m13", 45, obj=COIL, device_class="running",
                 entity_category="diagnostic", module=M_HC1, name="Heating pump M13"),
    RegisterSpec("output_dhw_pump", 46, obj=COIL, device_class="running",
                 entity_category="diagnostic", module=M_DHW, name="DHW pump"),
    RegisterSpec("output_mixer_m21_open", 47, obj=COIL, entity_category="diagnostic",
                 module=M_HC2_3, module_flag=M_HC2_3, name="Mixer M21 open"),
    RegisterSpec("output_mixer_m21_close", 48, obj=COIL, entity_category="diagnostic",
                 module=M_HC2_3, module_flag=M_HC2_3, name="Mixer M21 close"),
    RegisterSpec("output_aux_circulation_pump", 49, obj=COIL, device_class="running",
                 entity_category="diagnostic", module=M_CONTROLLER, name="Auxiliary circulation pump"),
    RegisterSpec("output_immersion_heater", 50, obj=COIL, device_class="running",
                 entity_category="diagnostic", module=M_CONTROLLER, name="Immersion heater"),
    RegisterSpec("output_heating_pump_m15", 51, obj=COIL, device_class="running",
                 entity_category="diagnostic", module=M_HC2_3, module_flag=M_HC2_3, name="Heating pump M15"),
    RegisterSpec("output_mixer_m22_open", 52, obj=COIL, entity_category="diagnostic",
                 module=M_HC2_3, module_flag=M_HC2_3, name="Mixer M22 open"),
    RegisterSpec("output_mixer_m22_close", 53, obj=COIL, entity_category="diagnostic",
                 module=M_HC2_3, module_flag=M_HC2_3, name="Mixer M22 close"),
    RegisterSpec("output_pool_pump", 56, obj=COIL, device_class="running",
                 entity_category="diagnostic", module=M_POOL, module_flag=M_POOL, name="Pool pump"),
    RegisterSpec("output_general_fault", 57, obj=COIL, device_class="problem",
                 entity_category="diagnostic", module=M_CONTROLLER, name="General fault output"),
    RegisterSpec("output_heating_pump_m14", 59, obj=COIL, device_class="running",
                 entity_category="diagnostic", module=M_CONTROLLER, name="Heating pump M14"),
    RegisterSpec("output_cooling_pump", 60, obj=COIL, device_class="running",
                 entity_category="diagnostic", module=M_COOLING, module_flag=M_COOLING, name="Cooling pump"),
    RegisterSpec("output_heating_pump_m20", 61, obj=COIL, device_class="running",
                 entity_category="diagnostic", module=M_CONTROLLER, name="Heating pump M20"),
    RegisterSpec("output_heat_cool_changeover", 66, obj=COIL, entity_category="diagnostic",
                 module=M_COOLING, module_flag=M_COOLING, name="Heat/cool changeover"),
    RegisterSpec("output_primary_cooling_pump", 68, obj=COIL, device_class="running",
                 entity_category="diagnostic", module=M_COOLING, module_flag=M_COOLING, name="Primary cooling pump"),
    RegisterSpec("output_solar_pump", 71, obj=COIL, device_class="running",
                 entity_category="diagnostic", module=M_SOLAR, module_flag=M_SOLAR, name="Solar pump"),
)


ENERGY_GROUPS: tuple[EnergyGroup, ...] = (
    EnergyGroup("energy_heating", 5096, 5097, 5098, "Heating energy (meter)"),
    EnergyGroup("energy_dhw", 5099, 5100, 5101, "DHW energy (meter)"),
    EnergyGroup("energy_pool", 5102, 5103, 5104, "Pool energy (meter)", module=M_POOL),
    EnergyGroup("energy_environment", 5127, 5128, 5129, "Environmental energy (meter)"),
)


def is_spec_active(
    spec: RegisterSpec,
    *,
    version: str,
    enabled_modules: frozenset[str],
    capabilities: frozenset[str],
    include_re: bool,
) -> bool:
    """Return True if ``spec`` should produce an entity for this config."""
    if spec.resolve_address(version) is None:
        return False
    if spec.re_only and not include_re:
        return False
    if spec.module_flag and spec.module_flag not in enabled_modules:
        return False
    if spec.capability and spec.capability not in capabilities:
        return False
    return True


def active_registers(
    *,
    version: str,
    enabled_modules: frozenset[str],
    capabilities: frozenset[str],
    include_re: bool,
) -> list[RegisterSpec]:
    """Return register specs active for the given configuration."""
    return [
        s for s in REGISTERS
        if is_spec_active(
            s, version=version, enabled_modules=enabled_modules,
            capabilities=capabilities, include_re=include_re,
        )
    ]


def active_energy_groups(
    *, enabled_modules: frozenset[str], capabilities: frozenset[str],
) -> list[EnergyGroup]:
    """Return energy groups readable for the given configuration."""
    groups = []
    for g in ENERGY_GROUPS:
        if g.capability not in capabilities:
            continue
        if g.module in OPTIONAL_MODULES and g.module not in enabled_modules:
            continue
        groups.append(g)
    return groups


def build_read_plan(
    specs: list[RegisterSpec],
    energy_groups: list[EnergyGroup],
    version: str,
    extra_holding: set[int] | None = None,
) -> list[tuple[str, int, int]]:
    """Cluster the needed addresses into ``(obj, start, count)`` read chunks.

    Addresses are grouped per object type, sorted, then split on gaps larger
    than :data:`CLUSTER_GAP` and capped at :data:`MAX_READ_CHUNK`.
    ``extra_holding`` adds writable-control addresses so their current values
    are read back.
    """
    holding: set[int] = set(extra_holding or ())
    coils: set[int] = set()
    for s in specs:
        addr = s.resolve_address(version)
        if addr is None:
            continue
        (coils if s.obj == COIL else holding).add(addr)
    for g in energy_groups:
        holding.update(g.registers)

    plan: list[tuple[str, int, int]] = []
    for obj, addresses in ((HOLDING, holding), (COIL, coils)):
        for start, count in _cluster(sorted(addresses)):
            plan.append((obj, start, count))
    return plan


def _cluster(addresses: list[int]) -> list[tuple[int, int]]:
    """Turn a sorted address list into (start, count) chunks."""
    chunks: list[tuple[int, int]] = []
    if not addresses:
        return chunks
    start = prev = addresses[0]
    for addr in addresses[1:]:
        if addr - prev > CLUSTER_GAP or (addr - start + 1) > MAX_READ_CHUNK:
            chunks.append((start, prev - start + 1))
            start = addr
        prev = addr
    chunks.append((start, prev - start + 1))
    return chunks


def decode_value(spec: RegisterSpec, raw: int) -> float | int:
    """Decode a raw holding register value per the spec (sign + scale)."""
    value = raw
    if spec.signed and value > 0x7FFF:
        value -= 0x10000
    if spec.scale == 1.0:
        return value
    scaled = value * spec.scale
    # 0.1-scaled values → 1 decimal; 0.01 → 2 decimals.
    decimals = 1 if spec.scale >= 0.1 else 2
    return round(scaled, decimals)


def energy_total_kwh(reg_1_4: int, reg_5_8: int, reg_9_12: int) -> int:
    """Combine the three digit-group registers into total kWh."""
    return reg_9_12 * 100_000_000 + reg_5_8 * 10_000 + reg_1_4


# ==========================================================================
# Writable controls (M2) — behind the enable_control gate.
#
# NOTE: exact raw encoding of setpoint registers is not fully confirmed without
# a real device. Direct registers are assumed integer in their unit; enum-coded
# registers use the documented offset mappings below. All writes are range
# clamped. Verify against hardware before trusting writes.
# ==========================================================================

KIND_NUMBER = "number"
KIND_SELECT = "select"

# Enum-coded register encoders: (encode display->raw, decode raw->display).
_ENCODERS = {
    # 5036/5086 Parallelverschiebung: raw 0..38 ↔ −19..+19 K  (K = raw − 19)
    "offset19": (lambda v: int(round(v)) + 19, lambda r: r - 19),
    # 5089 cooling room setpoint: raw 0..30 ↔ 15.0..30.0 °C (°C = 15 + 0.5·raw)
    "cool_setpoint": (lambda v: int(round((v - 15.0) / 0.5)), lambda r: round(15.0 + r * 0.5, 1)),
}


@dataclass(frozen=True)
class WriteSpec:
    """A writable control (number or select) backed by a holding register."""

    key: str
    address: int
    name: str
    module: str
    kind: str = KIND_NUMBER
    # number:
    min_value: float = 0.0
    max_value: float = 0.0
    step: float = 1.0
    unit: str | None = None
    device_class: str | None = None
    encode: str | None = None  # None => raw int == display; else key into _ENCODERS
    # select:
    options_map: dict[int, str] | None = None
    # gating:
    module_flag: str | None = None
    icon: str | None = None

    def to_raw(self, display: float) -> int:
        """Clamp the display value to range and encode it to a raw register value."""
        clamped = min(self.max_value, max(self.min_value, display))
        if self.encode:
            return _ENCODERS[self.encode][0](clamped)
        return int(round(clamped))

    def from_raw(self, raw: int) -> float | int:
        """Decode a raw register value to the display value."""
        if self.encode:
            return _ENCODERS[self.encode][1](raw)
        return raw


WRITE_REGISTERS: tuple[WriteSpec, ...] = (
    # DHW
    WriteSpec("set_dhw_setpoint", 5047, "DHW setpoint", M_DHW, min_value=10, max_value=85,
              unit="°C", device_class="temperature", icon="mdi:water-thermometer"),
    WriteSpec("set_dhw_setpoint_min", 5145, "DHW setpoint minimum", M_DHW, min_value=10, max_value=85,
              unit="°C", device_class="temperature"),
    WriteSpec("set_dhw_setpoint_max", 5048, "DHW setpoint maximum", M_DHW, min_value=10, max_value=85,
              unit="°C", device_class="temperature"),
    # HC1
    # NOTE: setpoint scaling assumed whole-°C (matches the working YAML which read
    # these as plain uint16 °C). Verify on device before trusting writes.
    WriteSpec("set_hc1_room_setpoint", 46, "HC1 room setpoint", M_HC1, min_value=15, max_value=30,
              step=1, unit="°C", device_class="temperature", icon="mdi:home-thermometer"),
    WriteSpec("set_hc1_fixed_flow", 5037, "HC1 fixed flow setpoint", M_HC1, min_value=18, max_value=60,
              unit="°C", device_class="temperature"),
    WriteSpec("set_hc1_curve_end", 5038, "HC1 heating curve end", M_HC1, min_value=20, max_value=70,
              unit="°C", device_class="temperature"),
    WriteSpec("set_hc1_curve_offset", 5036, "HC1 curve offset", M_HC1, min_value=-19, max_value=19,
              step=1, unit="K", encode="offset19", icon="mdi:tune-variant"),
    # Pool (optional)
    WriteSpec("set_pool_setpoint", 5051, "Pool setpoint", M_POOL, min_value=5, max_value=60,
              unit="°C", device_class="temperature", module_flag=M_POOL, icon="mdi:pool-thermometer"),
    # HC2/3 cooling room setpoint (enum-coded; uses the cool_setpoint encoder)
    WriteSpec("set_hc23_cooling_setpoint", 5089, "HC2/3 cooling room setpoint", M_HC2_3,
              min_value=15, max_value=30, step=0.5, unit="°C", encode="cool_setpoint",
              device_class="temperature", module_flag=M_HC2_3, icon="mdi:snowflake-thermometer"),
    # Operating mode (select)
    WriteSpec("set_operating_mode", 5015, "Operating mode", M_CONTROLLER, kind=KIND_SELECT,
              options_map={0: "Summer", 1: "Winter", 2: "Holiday", 3: "Party",
                           4: "2nd heat generator", 5: "Cooling"}, icon="mdi:tune"),
)


def active_write_registers(
    *, enabled_modules: frozenset[str], include_all_modules: bool = False
) -> list[WriteSpec]:
    """Return writable controls active for the enabled modules."""
    out = []
    for ws in WRITE_REGISTERS:
        if ws.module_flag and not include_all_modules and ws.module_flag not in enabled_modules:
            continue
        out.append(ws)
    return out
