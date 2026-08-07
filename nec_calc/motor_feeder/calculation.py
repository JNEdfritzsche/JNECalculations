from __future__ import annotations

from typing import Any

from lib.nec_tables import TABLES
from nec_calc.common.table_helpers import (
    get_col_integers,
    get_populated_columns,
    get_table_row,
)


# ----------------------------
# results helper functions
# ----------------------------

def _build_calc_result(calc: dict[str, Any], **inputs: Any) -> dict[str, Any]:
    return {
        **inputs,
        **calc,
    }


# ----------------------------
# calculator helper functions
# ----------------------------
def get_appropriate_table(phase: str):
    if phase == "dc":
        return "table_430_247"
    elif phase == "single_phase":
        return "table_430_248"
    elif phase == "three_phase":
        return "table_430_250"


def _column_prefix(phase: str, motor_type: str | None = None) -> str:
    if phase == "three_phase" and (motor_type or "").lower() == "synchronous":
        return "synchronous_unity_pf_"
    if phase == "three_phase":
        return "induction_"
    if phase == "single_phase":
        return "current_"
    return ""


def _entry_key(phase: str, voltage: int, motor_type: str | None = None) -> str | None:
    if phase == "dc":
        return f"{voltage}_volts"
    if phase in ("single_phase", "three_phase"):
        return f"{_column_prefix(phase, motor_type)}{voltage}v"
    return None


def _hp_criteria(hp) -> dict[str, Any]:
    label = hp[0] if isinstance(hp, (tuple, list)) else hp
    return {"horsepower": label}


def _get_table_flc(phase, voltage, hp, motor_type=None):
    table = TABLES.get(get_appropriate_table(phase))
    row = get_table_row(table, _hp_criteria(hp))
    if row is None:
        return None
    return row.get(_entry_key(phase, voltage, motor_type))


def get_valid_voltages(phase: str, hp, motor_type: str | None = None) -> list[int]:
    table = TABLES.get(get_appropriate_table(phase))
    row = get_table_row(table, _hp_criteria(hp))
    if row is None:
        return []
    prefix = _column_prefix(phase, motor_type)
    voltage_cols = [c for c in table["columns"] if c != "horsepower" and c.startswith(prefix)]
    populated = get_populated_columns(row, voltage_cols)
    return sorted({v for col in populated for v in get_col_integers([col])})


def _calc_conductor_ampacity(flc: float | None, sizing_factor: float | None) -> float | None:
    if flc is None or sizing_factor is None:
        return None
    return flc * sizing_factor


# Table 310.16 column for a given conductor material + insulation temperature rating.
_T310_16_COLUMN = {
    ("cu", 60): "copper_60c_ampacity",
    ("cu", 75): "copper_75c_ampacity",
    ("cu", 90): "copper_90c_ampacity",
    ("al", 60): "aluminum_or_copper_clad_aluminum_60c_ampacity",
    ("al", 75): "aluminum_or_copper_clad_aluminum_75c_ampacity",
    ("al", 90): "aluminum_or_copper_clad_aluminum_90c_ampacity",
}


def select_conductor_size(
    required_ampacity: float | None,
    material: str | None,
    temp_rating: int | None,
) -> dict[str, Any] | None:
    """Smallest standard conductor from Table 310.16 whose ampacity meets the
    required value, for the chosen material and insulation temperature column.
    Rows in Table 310.16 are ordered smallest-to-largest."""
    if required_ampacity is None:
        return None
    col = _T310_16_COLUMN.get((material, temp_rating))
    if col is None:
        return None
    table = TABLES.get("table_310_16")
    for row in table["rows"]:
        amp = row.get(col)
        if amp is not None and amp >= required_ampacity:
            return {"size": row["size_awg_kcmil"], "ampacity": amp, "column": col}
    return None


def _calc_max_overload(nameplate_fla: float | None, service_factor: float | None) -> float | None:
    if nameplate_fla is None or service_factor is None:
        return None
    return nameplate_fla * service_factor


# ----------------------------
# main calculator function
# ----------------------------
def calc_motor_feeder(
    phase: str,
    phase_label: str,
    hp: float,
    hp_label: str,
    voltage: int | None,
    motor_type: str | None,
    sizing_factor: float,
    sizing_factor_label: str,
    nameplate_fla: float | None,
    service_factor: float | None,
    service_factor_label: str | None,
    material: str | None = None,
    material_label: str | None = None,
    temp_rating: int | None = None,
) -> dict[str, Any]:
    table_flc = _get_table_flc(phase, voltage, (hp_label, hp), motor_type)
    flc_for_conductor = table_flc if table_flc is not None else nameplate_fla
    flc_is_estimate = table_flc is not None
    flc_source = "NEC Table" if table_flc is not None else ("Nameplate" if nameplate_fla is not None else None)

    conductor_ampacity = _calc_conductor_ampacity(flc_for_conductor, sizing_factor)
    conductor = select_conductor_size(conductor_ampacity, material, temp_rating)

    calc = {
        "table_flc": table_flc,
        "flc": flc_for_conductor,
        "flc_source": flc_source,
        "flc_is_estimate": flc_is_estimate,
        "conductor_ampacity": conductor_ampacity,
        "conductor_size": conductor["size"] if conductor else None,
        "conductor_size_ampacity": conductor["ampacity"] if conductor else None,
        "max_overload": _calc_max_overload(nameplate_fla, service_factor),
    }

    return _build_calc_result(
        calc=calc,
        phase=phase,
        phase_label=phase_label,
        hp=hp,
        hp_label=hp_label,
        voltage=voltage,
        motor_type=motor_type,
        sizing_factor=sizing_factor,
        sizing_factor_label=sizing_factor_label,
        nameplate_fla=nameplate_fla,
        service_factor=service_factor,
        service_factor_label=service_factor_label,
        material=material,
        material_label=material_label,
        temp_rating=temp_rating,
    )