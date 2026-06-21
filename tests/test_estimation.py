"""Pure-Python tests for the estimation engine (no Home Assistant needed).

Run:  python3 tests/test_estimation.py   |   pytest tests/test_estimation.py
"""

from __future__ import annotations

import importlib.util
import os
import sys

_HERE = os.path.dirname(__file__)
_PATH = os.path.abspath(
    os.path.join(_HERE, "..", "custom_components", "dimplex_wpm", "estimation.py")
)


def _load():
    spec = importlib.util.spec_from_file_location("dwpm_estimation", _PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules["dwpm_estimation"] = mod
    spec.loader.exec_module(mod)
    return mod


est = _load()

LUT = ((32, 1050), (35, 1110), (39, 1190), (83, 2550))
COP = {
    -7: {35: 2.40, 45: 2.24, 55: 1.72},
    2: {35: 3.60, 45: 2.96, 55: 2.44},
    7: {35: 4.80, 45: 3.30, 55: 2.86},
    10: {35: 5.10, 45: 3.57, 55: 2.98},
}


def test_interp_lut_clamp_and_mid():
    assert est.interp_lut(LUT, 10) == 1050      # below range -> clamp low
    assert est.interp_lut(LUT, 999) == 2550     # above range -> clamp high
    assert est.interp_lut(LUT, 33.5) == 1080.0  # 1050 + 60*(1.5/3)


def test_compressor_power_status_aware():
    assert est.compressor_power_w(0, 2, LUT) == 0.0          # hz<=0
    assert est.compressor_power_w(35, 0, LUT) == 0.0         # off
    assert est.compressor_power_w(35, 30, LUT) == 0.0        # lock
    assert est.compressor_power_w(35, 2, LUT) == 1110        # heating -> base
    assert est.compressor_power_w(35, 4, LUT, k_dhw=1.1) == round(1110 * 1.1)
    assert est.compressor_power_w(35, 10, LUT, k_defrost=1.05) == round(1110 * 1.05)


def test_cop_grid_and_bilinear():
    assert est.cop_en14511(2, 35, COP) == 3.6            # exact grid point
    assert est.cop_en14511(2, 45, COP) == 2.96
    assert est.cop_en14511(4.5, 45, COP) == 3.13         # midpoint in A
    assert est.cop_en14511(-20, 35, COP) == 2.40         # clamp A low
    assert est.cop_en14511(2, 100, COP) == 2.44          # clamp W high
    assert est.cop_en14511(None, 45, COP) == 0.0
    assert est.cop_en14511(2, 45, {}) == 0.0


def test_thermal_and_defrost():
    assert est.thermal_power_compressor_w(1000, 4.0, 2) == 4000
    assert est.thermal_power_compressor_w(1000, 4.0, 0) == 0.0   # not heating
    assert est.thermal_power_defrost_loss_w(1000, 2.35, 10) == round(1000 * 2.35)
    assert est.thermal_power_defrost_loss_w(1000, 2.35, 2) == 0.0
    assert est.thermal_power_loop_w(4000, 6000, 1000) == 9000


def test_alpha_house():
    assert est.alpha_house(0.0, 0.85, 0.4, 0.03, enabled=False) == 1.0
    assert est.alpha_house(0.01, 0.85, 0.4, 0.03) == 0.85   # within deadband -> d=0
    assert est.alpha_house(1.0, 0.85, 0.4, 0.03) == 0.45    # 0.85 - 0.4*1.0
    assert est.alpha_house(-10, 0.85, 0.4, 0.03) == 1.0     # clamp high


def test_estimated_flow():
    assert est.estimated_flow_m3h(4000, 0.0, 2) == 0.0       # dt too small
    assert est.estimated_flow_m3h(4000, 5.0, 0) == 0.0       # not heating
    # 4000 W, 5 K: 4000/(4180*5)*3.6 = 0.689...
    assert est.estimated_flow_m3h(4000, 5.0, 2) == 0.69
    assert est.estimated_flow_m3h(999999, 5.0, 2) == 3.8     # clamp


def _run():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"FAIL {t.__name__}: {exc!r}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return failed


if __name__ == "__main__":
    raise SystemExit(_run())
