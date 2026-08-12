from __future__ import annotations

from typing import Any

from lib.nec_tables import NEC_2406A_STANDARD, TABLES
from calc_common.formatting import next_standard_size
from calc_common.table_helpers import get_table_row

# Reuse the full-load-current lookup already implemented for the motor feeder.
from nec_calc.motor_feeder.calculation import _get_table_flc


# ============================================================
# Table 430.52(C)(1) — branch-circuit short-circuit / ground-fault protection
# ============================================================
# Map a calculator category key to the exact `type_of_motor` row string in
# TABLE_430_52_C_1 (see lib/nec_tables.py).
MOTOR_CATEGORY_ROWS: dict[str, str] = {
    "single_phase": "Single-phase motors",
    "ac_polyphase": "Alternating-current(ac) polyphase motors other than wound-rotor",
    "squirrel_cage": (
        "Squirrel cage - other than Design B or Cenergy-efficient - "
        "and Design B or Cpremium efficiency"
    ),
    "design_b_energy_efficient": (
        "Design B energy-efficient, Design B premium efficiency, "
        "Design BE and Design CE"
    ),
    "synchronous": "Synchronous",
    "wound_rotor": "Wound-rotor",
    "dc": "Direct-current(dc) (constant voltage)",
}

# The four device columns of Table 430.52(C)(1), in display order.
DEVICE_TYPES: list[dict[str, str]] = [
    {"key": "nontime_delay_fuse", "label": "Non-time-delay fuse"},
    {"key": "dual_element_time_delay_fuse", "label": "Dual-element (time-delay) fuse"},
    {"key": "instantaneous_trip_breaker", "label": "Instantaneous-trip breaker"},
    {"key": "inverse_time_breaker", "label": "Inverse-time breaker"},
]

# 430.52(C)(1) Exception No. 2 — absolute ceilings when the table value is not
# sufficient to start the motor. Percentages of full-load current.
#   * Instantaneous-trip breaker: 1300%, or 1700% for a Design B energy-efficient
#     motor.
#   * Inverse-time breaker / non-time-delay fuse: 400% for FLC <= 100 A, else 300%.
#   * Dual-element (time-delay) fuse: 225%.
def _exception2_ceiling_pct(device_key: str, flc: float, category_key: str) -> int | None:
    if device_key == "instantaneous_trip_breaker":
        return 1700 if category_key == "design_b_energy_efficient" else 1300
    if device_key == "dual_element_time_delay_fuse":
        return 225
    if device_key in ("nontime_delay_fuse", "inverse_time_breaker"):
        return 400 if flc <= 100 else 300
    return None


def _round_branch_device(device_key: str, raw: float | None) -> float | None:
    """430.52(C)(1) Exception No. 1 — where the value does not correspond to a
    standard rating, the next higher standard rating (240.6(A)) is permitted.

    Instantaneous-trip breakers are an adjustable *setting*, not a standard
    fuse/breaker rating, so they are not rounded to the 240.6(A) list."""
    if raw is None or device_key == "instantaneous_trip_breaker":
        return None
    return next_standard_size(raw, NEC_2406A_STANDARD, "up")


def calc_branch_protection(flc: float | None, category_key: str) -> dict[str, Any]:
    """Maximum branch-circuit SCGF device per NEC 430.52(C)(1) for all four
    device types."""
    row = get_table_row(TABLES["table_430_52_c_1"], {"type_of_motor": MOTOR_CATEGORY_ROWS.get(category_key)})
    devices: list[dict[str, Any]] = []

    for device in DEVICE_TYPES:
        pct = row.get(device["key"]) if row else None
        raw = flc * pct / 100 if (flc is not None and pct is not None) else None
        ceiling_pct = _exception2_ceiling_pct(device["key"], flc, category_key) if flc is not None else None
        devices.append(
            {
                "key": device["key"],
                "label": device["label"],
                "pct": pct,
                "raw": raw,
                "standard": _round_branch_device(device["key"], raw),
                "max_pct": ceiling_pct,
                "max_raw": flc * ceiling_pct / 100 if (flc is not None and ceiling_pct is not None) else None,
            }
        )

    return {
        "category_key": category_key,
        "category_label": MOTOR_CATEGORY_ROWS.get(category_key),
        "devices": devices,
    }


# ============================================================
# Overload protection — NEC 430.32
# ============================================================
def calc_overload(
    nameplate_fla: float | None,
    service_factor: float | None,
    temp_rise_c: float | None,
) -> dict[str, Any]:
    """430.32(A)(1): motors with a marked service factor >= 1.15 or a marked
    temperature rise <= 40 C use 125% of nameplate FLA; all other motors use
    115%. 430.32(C) permits raising to 140%/130% respectively when the base
    value will not allow the motor to start or carry the load."""
    if nameplate_fla is None:
        return {"factor": None, "max_overload": None, "start_factor": None, "max_overload_start": None, "basis": None}

    high = (service_factor is not None and service_factor >= 1.15) or (
        temp_rise_c is not None and temp_rise_c <= 40
    )
    factor = 1.25 if high else 1.15
    start_factor = 1.40 if high else 1.30
    basis = (
        "service factor >= 1.15 or temperature rise <= 40 C (125%)"
        if high
        else "all other motors (115%)"
    )
    return {
        "factor": factor,
        "max_overload": nameplate_fla * factor,
        "start_factor": start_factor,
        "max_overload_start": nameplate_fla * start_factor,
        "basis": basis,
    }


# ============================================================
# Locked-rotor current & disconnecting means — NEC 430.7(B) / 430.251 / 430.110
# ============================================================
def _kva_per_hp_upper(code_letter: str) -> float | None:
    """Upper bound of the kVA/hp band for a locked-rotor code letter
    (Table 430.7(B)). Used to bound the maximum locked-rotor kVA."""
    row = get_table_row(TABLES["table_430_7_b"], {"code_letter": code_letter})
    if row is None:
        return None
    band = str(row["kilovolt_amperes_per_horsepower_with_locked_rotor"])
    if "and up" in band:
        return float(band.split()[0])
    parts = band.split("-")
    try:
        return float(parts[-1])
    except ValueError:
        return None


def calc_lrc_from_code_letter(
    code_letter: str,
    hp: float,
    voltage: float,
    phase_factor: float,
) -> dict[str, Any]:
    """Locked-rotor current from the nameplate code letter (430.7(B)).

    LR kVA = (kVA/hp) x hp;  I_LR = LR kVA x 1000 / (V x phase_factor)."""
    kva_per_hp = _kva_per_hp_upper(code_letter)
    if kva_per_hp is None or not voltage:
        return {"kva_per_hp": kva_per_hp, "locked_rotor_kva": None, "locked_rotor_current": None}
    lr_kva = kva_per_hp * hp
    return {
        "kva_per_hp": kva_per_hp,
        "locked_rotor_kva": lr_kva,
        "locked_rotor_current": lr_kva * 1000 / (voltage * phase_factor),
    }


# 430.251 table + column selection.
_LRC_DESIGN_TABLES = {
    "b_c_d": ("table_430_251_b", "_b_c_d"),
    "be_ce": ("table_430_251_c", "_be_ce"),
}


def calc_lrc_from_table(
    phase: str,
    hp_label: str,
    voltage: int,
    design_group: str | None,
) -> dict[str, Any]:
    """Locked-rotor current from the conversion tables (430.251) by horsepower,
    voltage and design letter — for selecting disconnects and controllers."""
    if phase == "single_phase":
        table_key = "table_430_251_a"
        col = f"{voltage}_volts"
    else:
        table_key, suffix = _LRC_DESIGN_TABLES.get(design_group or "b_c_d", _LRC_DESIGN_TABLES["b_c_d"])
        col = f"{voltage}_volts{suffix}"

    table = TABLES.get(table_key)
    # Tables 430.251(A)/(B)/(C) name their horsepower column "rated_horsepower"
    # (unlike the 430.247–430.250 full-load-current tables, which use "horsepower").
    row = get_table_row(table, {"rated_horsepower": hp_label}) if table else None
    lrc = row.get(col) if row else None
    return {"table": table_key, "column": col, "locked_rotor_current": lrc}


def calc_disconnect(flc: float | None) -> dict[str, Any]:
    """430.110(C)(1): the disconnecting means ampere rating shall be at least
    115% of the motor full-load current."""
    if flc is None:
        return {"min_disconnect_ampere": None}
    return {"min_disconnect_ampere": 1.15 * flc}


# ============================================================
# Full-load current + top-level orchestration (single motor)
# ============================================================
def _lookup_flc(phase: str, voltage: int | None, hp_label: str, motor_type: str | None) -> float | None:
    return _get_table_flc(phase, voltage, (hp_label, None), motor_type)


def calc_motor_protection(
    phase: str,
    phase_label: str,
    phase_factor: float,
    hp: float,
    hp_label: str,
    voltage: int | None,
    motor_type: str | None,
    category_key: str,
    nameplate_fla: float | None,
    service_factor: float | None,
    service_factor_label: str | None,
    temp_rise_c: float | None,
    design_group: str | None,
    code_letter: str | None,
) -> dict[str, Any]:
    table_flc = _lookup_flc(phase, voltage, hp_label, motor_type)
    flc = table_flc if table_flc is not None else nameplate_fla
    flc_source = "NEC Table" if table_flc is not None else ("Nameplate" if nameplate_fla is not None else None)

    branch = calc_branch_protection(flc, category_key)
    overload = calc_overload(nameplate_fla, service_factor, temp_rise_c)
    disconnect = calc_disconnect(flc)

    lrc_table = None
    lrc_code = None
    if voltage is not None:
        lrc_table = calc_lrc_from_table(phase, hp_label, voltage, design_group)
        if code_letter:
            lrc_code = calc_lrc_from_code_letter(code_letter, hp, float(voltage), phase_factor)

    return {
        "phase": phase,
        "phase_label": phase_label,
        "hp": hp,
        "hp_label": hp_label,
        "voltage": voltage,
        "motor_type": motor_type,
        "category_key": category_key,
        "flc": flc,
        "table_flc": table_flc,
        "flc_source": flc_source,
        "nameplate_fla": nameplate_fla,
        "service_factor": service_factor,
        "service_factor_label": service_factor_label,
        "temp_rise_c": temp_rise_c,
        "design_group": design_group,
        "code_letter": code_letter,
        "branch": branch,
        "overload": overload,
        "disconnect": disconnect,
        "lrc_table": lrc_table,
        "lrc_code": lrc_code,
    }
