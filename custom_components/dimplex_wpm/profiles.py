"""Device profiles — per-model calibration & defaults.

The WPM register map is identical across models; profiles only carry
model-specific calibration (Hz→W power LUT, EN14511 COP table, heater power)
and per-model defaults. Community contributions add a new profile here without
touching the register map. HA-free / pure data.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .registers import CAP_INVERTER_FREQ


@dataclass(frozen=True)
class DeviceProfile:
    """Model calibration + sensible defaults for one heat-pump model."""

    key: str
    name: str  # shown as the device model
    # Estimation calibration (consumed by the M1 estimation engine):
    power_lut: tuple[tuple[float, float], ...] = ()  # (Hz, W) interpolation points
    cop_table: dict[int, dict[int, float]] = field(default_factory=dict)  # {A:{W:COP}}
    heater_default_w: int = 6000
    k_dhw: float = 1.00
    k_defrost: float = 1.05
    k_defrost_loss: float = 2.35
    alpha_base: float = 0.85
    alpha_sensitivity: float = 0.40
    alpha_deadband: float = 0.03
    # Defaults applied at config time (user can override):
    default_modules: frozenset[str] = frozenset()
    default_capabilities: frozenset[str] = frozenset({CAP_INVERTER_FREQ})


# Calibration for the Dimplex LAK 9S-TU (reverse-engineered + EN14511 datasheet),
# ported from the user's working YAML estimator.
LAK9 = DeviceProfile(
    key="lak9",
    name="Dimplex LAK 9S-TU",
    power_lut=(
        (32, 1050), (35, 1110), (39, 1190), (41, 1290),
        (45, 1340), (49, 1500), (53, 1570), (57, 1720),
        (61, 1850), (63, 1940), (65, 2010), (67, 2050),
        (71, 2200), (75, 2320), (79, 2450), (83, 2550),
    ),
    cop_table={
        -7: {35: 2.40, 45: 2.24, 55: 1.72},
        2: {35: 3.60, 45: 2.96, 55: 2.44},
        7: {35: 4.80, 45: 3.30, 55: 2.86},
        10: {35: 5.10, 45: 3.57, 55: 2.98},
    },
    heater_default_w=6000,
)

# Generic fallback — no calibration (estimation degrades to on/off heuristics).
GENERIC_WPM = DeviceProfile(
    key="generic_wpm",
    name="Dimplex WPM (generic)",
    default_capabilities=frozenset(),
)

PROFILES: dict[str, DeviceProfile] = {
    LAK9.key: LAK9,
    GENERIC_WPM.key: GENERIC_WPM,
}


def get_profile(key: str | None) -> DeviceProfile:
    """Return the profile for ``key`` (falls back to the generic profile)."""
    if key and key in PROFILES:
        return PROFILES[key]
    return GENERIC_WPM
