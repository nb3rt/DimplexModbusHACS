"""Estimation engine — power / COP / heat / flow.

Pure functions (HA-free, unit-tested). Ported from the user's working YAML
estimator, with the COP 2D-interpolation rounding bug fixed. Used when a real
meter is absent (see the measurement-source matrix in DESIGN.md §6).

Status codes are interpreted against the **L/M** firmware map (the calibrated
target). Other firmwares would need their own status semantics in the profile.
"""

from __future__ import annotations

# L/M status semantics (register 103).
STATUS_OFF_LOCK = frozenset({0, 1, 11, 30})  # off / idle / flow-monitoring / lock
STATUS_DEFROST = 10
STATUS_DHW = 4
STATUS_HEATING_DHW = frozenset({2, 4})  # compressor delivering usable heat

# Water heat capacity for the hydraulic flow estimate.
_CP_WATER = 4180.0  # J/(kg·K)


def interp_lut(lut: tuple[tuple[float, float], ...], x: float) -> float:
    """Piecewise-linear interpolation of an (x, y) LUT, clamped to its ends."""
    if not lut:
        return 0.0
    if x <= lut[0][0]:
        return float(lut[0][1])
    if x >= lut[-1][0]:
        return float(lut[-1][1])
    for (x0, y0), (x1, y1) in zip(lut, lut[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * ((x - x0) / (x1 - x0))
    return float(lut[-1][1])


def compressor_power_w(
    hz: float | None,
    status: int,
    lut: tuple[tuple[float, float], ...],
    k_dhw: float = 1.0,
    k_defrost: float = 1.05,
) -> float:
    """Estimate compressor electrical power (W) from inverter frequency."""
    if hz is None or hz <= 0:
        return 0.0
    base = interp_lut(lut, hz)
    if base <= 0:
        return 0.0
    if status in STATUS_OFF_LOCK:
        return 0.0
    if status == STATUS_DEFROST:
        return round(base * k_defrost)
    if status == STATUS_DHW:
        return round(base * k_dhw)
    return round(base)


def heater_power_w(on: bool, heater_w: float) -> float:
    """2nd-source heater electrical power (W): fixed power when active."""
    return float(heater_w) if on else 0.0


def total_power_w(compressor_w: float, heater_w: float, pumps_w: float = 0.0) -> float:
    return compressor_w + heater_w + pumps_w


def cop_en14511(
    t_out: float | None,
    t_flow: float | None,
    table: dict[int, dict[int, float]],
) -> float:
    """Bilinear interpolation of an EN14511 COP table on (outdoor A, flow W)."""
    if not table or t_out is None or t_flow is None:
        return 0.0
    a_pts = sorted(table)
    w_pts = sorted(next(iter(table.values())))
    a = min(max(t_out, a_pts[0]), a_pts[-1])
    w = min(max(t_flow, w_pts[0]), w_pts[-1])
    a0 = max(p for p in a_pts if p <= a)
    a1 = min(p for p in a_pts if p >= a)
    w0 = max(p for p in w_pts if p <= w)
    w1 = min(p for p in w_pts if p >= w)
    q11 = table[a0][w0]
    q21 = table[a1][w0]
    q12 = table[a0][w1]
    q22 = table[a1][w1]
    if a0 == a1 and w0 == w1:
        return round(q11, 3)
    if a0 == a1:
        return round(q11 + (q12 - q11) * ((w - w0) / (w1 - w0)), 3)
    if w0 == w1:
        return round(q11 + (q21 - q11) * ((a - a0) / (a1 - a0)), 3)
    # Full bilinear — whole expression rounded (the YAML bracketed round() wrong).
    value = (
        q11 * (a1 - a) * (w1 - w)
        + q21 * (a - a0) * (w1 - w)
        + q12 * (a1 - a) * (w - w0)
        + q22 * (a - a0) * (w - w0)
    ) / ((a1 - a0) * (w1 - w0))
    return round(value, 3)


def thermal_power_compressor_w(p_el_w: float, cop: float, status: int) -> float:
    """Compressor heat output (W) = electrical × COP, only when heating/DHW."""
    if status in STATUS_HEATING_DHW:
        return round(p_el_w * cop)
    return 0.0


def thermal_power_defrost_loss_w(p_el_w: float, k_loss: float, status: int) -> float:
    """Heat drawn from the system during defrost (W)."""
    return round(p_el_w * k_loss) if status == STATUS_DEFROST else 0.0


def thermal_power_loop_w(compressor_w: float, heater_w: float, defrost_loss_w: float) -> float:
    return compressor_w + heater_w - defrost_loss_w


def alpha_house(
    ddelta_t_dt: float, base: float, sensitivity: float, deadband: float, enabled: bool = True
) -> float:
    """Fraction of loop heat delivered to the house (heuristic on dΔT/dt)."""
    if not enabled:
        return 1.0
    d = ddelta_t_dt
    if -deadband < d < deadband:
        d = 0.0
    return round(min(1.0, max(0.0, base - sensitivity * d)), 3)


def thermal_split(loop_w: float, alpha: float) -> tuple[float, float]:
    """Split loop heat into (house, installation)."""
    house = loop_w * alpha
    return house, loop_w - house


def estimated_flow_m3h(
    q_w: float, delta_t: float, status: int, clamp_max: float = 3.8
) -> float:
    """Hydraulic flow estimate from the energy balance V̇ = Q/(cp·ΔT)·3.6."""
    if status not in STATUS_HEATING_DHW or q_w <= 0 or delta_t <= 0.5:
        return 0.0
    v = (q_w / (_CP_WATER * delta_t)) * 3.6
    return min(clamp_max, max(0.0, round(v, 2)))
