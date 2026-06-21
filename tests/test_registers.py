"""Pure-Python tests for the register table logic (no Home Assistant needed).

Run directly:  python3 tests/test_registers.py
Or via pytest (in CI with HA installed):  pytest tests/test_registers.py
"""

from __future__ import annotations

import importlib.util
import os
import sys

_HERE = os.path.dirname(__file__)
_REG_PATH = os.path.abspath(
    os.path.join(_HERE, "..", "custom_components", "dimplex_wpm", "registers.py")
)


def _load_registers():
    spec = importlib.util.spec_from_file_location("dwpm_registers", _REG_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules["dwpm_registers"] = mod  # needed for dataclass annotation resolution
    spec.loader.exec_module(mod)
    return mod


reg = _load_registers()


def test_decode_signed_and_scale():
    # int16 negative outdoor temp: 0xFFF6 = -10 raw -> -1.0 °C
    spec = reg.RegisterSpec("t", 1, signed=True, scale=0.1)
    assert reg.decode_value(spec, 0xFFF6) == -1.0
    assert reg.decode_value(spec, 215) == 21.5
    # power W/10 -> kW (0.01)
    p = reg.RegisterSpec("p", 5170, signed=True, scale=0.01)
    assert reg.decode_value(p, 150) == 1.5
    assert reg.decode_value(p, 0xFFFF) == -0.01
    # plain code (scale 1) returns int unchanged
    c = reg.RegisterSpec("c", 103)
    assert reg.decode_value(c, 30) == 30


def test_energy_digit_groups():
    # total = 9-12*1e8 + 5-8*1e4 + 1-4
    assert reg.energy_total_kwh(1234, 56, 7) == 7 * 100_000_000 + 56 * 10_000 + 1234


def test_version_dependent_address():
    spec = next(s for s in reg.REGISTERS if s.key == "status_text")
    assert spec.resolve_address("M") == 103
    assert spec.resolve_address("J") == 43
    assert spec.resolve_address("H") == 14
    se = next(s for s in reg.REGISTERS if s.key == "sensor_error_text")
    assert se.resolve_address("M") == 106
    assert se.resolve_address("H") is None  # not available on H


def test_active_registers_filtering():
    # L/M, only core modules, no meters, with RE -> inverter freq present,
    # power/energy registers absent, optional-module entities absent.
    core = frozenset({"controller", "hc1", "dhw", "source", "energy"})
    specs = reg.active_registers(
        version="M", enabled_modules=core,
        capabilities=frozenset({"inverter_freq"}), include_re=True,
    )
    keys = {s.key for s in specs}
    assert "inverter_frequency" in keys           # RE + capability present
    assert "electrical_power" not in keys         # needs electric_meter capability
    assert "hc2_temperature" not in keys          # hc2_3 module not enabled
    assert "sensor_error_text" in keys            # available on M
    # Drop RE -> inverter frequency disappears
    specs2 = reg.active_registers(
        version="M", enabled_modules=core,
        capabilities=frozenset({"inverter_freq"}), include_re=False,
    )
    assert "inverter_frequency" not in {s.key for s in specs2}
    # H firmware -> sensor_error_text address is None -> excluded
    specs_h = reg.active_registers(
        version="H", enabled_modules=core,
        capabilities=frozenset(), include_re=False,
    )
    assert "sensor_error_text" not in {s.key for s in specs_h}


def test_read_plan_clusters_and_caps():
    core = frozenset({"controller", "hc1", "dhw", "source", "energy"})
    specs = reg.active_registers(
        version="M", enabled_modules=core,
        capabilities=frozenset({"heat_meter", "electric_meter", "inverter_freq"}),
        include_re=True,
    )
    groups = reg.active_energy_groups(
        enabled_modules=core, capabilities=frozenset({"heat_meter"})
    )
    plan = reg.build_read_plan(specs, groups, "M")
    assert plan, "plan must not be empty"
    # No chunk exceeds the max read size, all counts positive.
    for obj, start, count in plan:
        assert obj in (reg.HOLDING, reg.COIL)
        assert 1 <= count <= reg.MAX_READ_CHUNK
        assert start >= 1
    # Energy registers (5096-5098) must be covered by some holding chunk.
    covered = any(
        obj == reg.HOLDING and start <= 5096 and 5098 <= start + count - 1
        for obj, start, count in plan
    )
    assert covered, "energy registers not covered by read plan"


def test_no_duplicate_keys():
    keys = [s.key for s in reg.REGISTERS]
    assert len(keys) == len(set(keys)), "duplicate register keys"
    gkeys = [g.key for g in reg.ENERGY_GROUPS]
    assert len(gkeys) == len(set(gkeys))
    wkeys = [w.key for w in reg.WRITE_REGISTERS]
    assert len(wkeys) == len(set(wkeys)), "duplicate write keys"


def test_write_direct_encode_clamp():
    dhw = next(w for w in reg.WRITE_REGISTERS if w.key == "set_dhw_setpoint")
    assert dhw.to_raw(50) == 50
    assert dhw.from_raw(50) == 50
    assert dhw.to_raw(200) == 85   # clamp to max
    assert dhw.to_raw(-5) == 10    # clamp to min


def test_write_offset19_encode():
    off = next(w for w in reg.WRITE_REGISTERS if w.key == "set_hc1_curve_offset")
    assert off.to_raw(0) == 19
    assert off.to_raw(-19) == 0
    assert off.to_raw(19) == 38
    assert off.to_raw(100) == 38   # clamp then encode
    assert off.from_raw(19) == 0
    assert off.from_raw(38) == 19


def test_write_cool_setpoint_encoder():
    ws = reg.WriteSpec("x", 5089, "cool", reg.M_HC2_3, min_value=15, max_value=30,
                       encode="cool_setpoint")
    assert ws.to_raw(15) == 0
    assert ws.to_raw(30) == 30
    assert ws.to_raw(22.5) == 15
    assert ws.from_raw(30) == 30.0
    assert ws.from_raw(0) == 15.0


def test_active_write_registers_module_gate():
    no_pool = reg.active_write_registers(enabled_modules=frozenset({"controller", "hc1", "dhw"}))
    assert "set_pool_setpoint" not in {w.key for w in no_pool}
    with_pool = reg.active_write_registers(enabled_modules=frozenset({"controller", "pool"}))
    assert "set_pool_setpoint" in {w.key for w in with_pool}
    assert "set_dhw_setpoint" in {w.key for w in no_pool}  # ungated always present


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
