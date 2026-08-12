from __future__ import annotations

import math
from typing import Any

from lib import oesc_tables

COPPER = "Copper"
ALUMINUM = "Aluminum"
MATERIALS = (COPPER, ALUMINUM)

CABLE = "Cable"
RACEWAY = "Raceway"
DC = "DC"
LOCATIONS = (CABLE, RACEWAY, DC)

PF_CHOICES = ("100% pf", "90% pf", "80% pf")

TEMPERATURES = (60, 75, 90)
TEMP_MULTIPLIERS = {60: 0.95, 75: 1.00, 90: 1.05}
REFERENCE_TEMPERATURE = 75

DC_CIRCUIT_TYPES = [
    ("DC — 2-wire, positive-to-negative (VD line-to-line)", 2.0),
    ("DC — 2-wire, positive-to-ground (VD line-to-ground)", 2.0),
    ("DC — 2-wire, negative-to-ground (VD line-to-ground)", 2.0),
    ("DC — 3-wire, line-to-line with grounded conductor (VD line-to-line)", 2.0),
]

CIRCUIT_TYPES = DC_CIRCUIT_TYPES + [
    ("1-φ AC — 2-wire, line-to-grounded conductor (VD line-to-ground)", 2.0),
    ("1-φ AC — 2-wire, line-to-line (VD line-to-line)", 2.0),
    ("1-φ AC — 3-wire, line-to-line, with grounded conductor (VD line-to-line)", 2.0),
    ("3-φ AC — 2-wire, line-to-grounded conductor (VD line-to-ground)", 2.0),
    ("3-φ AC — 2-wire, line-to-line, no grounded conductor (VD line-to-line)", 2.0),
    ("3-φ AC — 3-wire, line-to-line, with grounded conductor (VD line-to-line)", 2.0),
    ("3-φ AC — 3-wire, line-to-grounded conductor (VD line-to-ground)", 2.0),
    ("3-φ AC — 3-wire, line-to-line, no grounded conductor (VD line-to-line)", math.sqrt(3)),
    ("3-φ AC — 4-wire, line-to-line, with grounded conductor (VD line-to-line)", math.sqrt(3)),
]


def _column(material: str, location: str, pf_choice: str) -> str:
    prefix = "copper" if material == COPPER else "aluminum"
    if location == DC:
        return f"{prefix}_dc"
    return f"{prefix}_{location.lower()}_{pf_choice.split('%')[0]}pf"


def conductor_sizes(material: str) -> list[str]:
    column = _column(material, CABLE, "100% pf")
    return [
        row["size_awg_kcmil"]
        for row in oesc_tables.TABLE_D3["rows"]
        if row.get(column) is not None
    ]


def table_k(material: str, location: str, pf_choice: str, size: str) -> tuple[float | None, str]:
    column = _column(material, location, pf_choice)
    label = "DC" if location == DC else f"{location} {pf_choice.split()[0]}"

    for row in oesc_tables.TABLE_D3["rows"]:
        if row.get("size_awg_kcmil") == size:
            value = row.get(column)
            return (None if value is None else float(value)), label
    return None, label


def temperature_multiplier(operating_temp_c: int) -> float:
    return TEMP_MULTIPLIERS.get(int(operating_temp_c), 1.00)


def calc_voltage_drop(
    current: float,
    length_m: float,
    v_nom: float,
    n_parallel: int,
    operating_temp_c: int,
    f_factor: float,
    f_label: str,
    use_table: bool = True,
    material: str | None = None,
    location: str | None = None,
    pf_choice: str = "100% pf",
    size: str | None = None,
    manual_k: float | None = None,
) -> dict[str, Any]:
    if use_table:
        k_base, column_label = table_k(material, location, pf_choice, size)
    else:
        k_base, column_label = manual_k, "Manual"

    multiplier = temperature_multiplier(operating_temp_c)
    k_used = k_base * multiplier if k_base is not None else None

    i_eff = current / n_parallel if n_parallel else None
    if k_used is None or i_eff is None or current <= 0 or length_m <= 0 or v_nom <= 0:
        vd = pct = None
    else:
        vd = (k_used * f_factor * i_eff * length_m) / 1000.0
        pct = (vd / v_nom) * 100.0

    return {
        "current": current,
        "length_m": length_m,
        "v_nom": v_nom,
        "n_parallel": n_parallel,
        "I_eff": i_eff,
        "use_table": use_table,
        "material": material if use_table else None,
        "location": location if use_table else None,
        "pf_choice": pf_choice if use_table and location != DC else None,
        "size": size if use_table else None,
        "column_label": column_label,
        "k_base": k_base,
        "operating_temp_c": operating_temp_c,
        "k_temp_multiplier": multiplier,
        "k_used": k_used,
        "f": f_factor,
        "f_label": f_label,
        "voltage_drop": vd,
        "percent_drop": pct,
        "primary_table": "D3" if use_table else None,
        "source_tables": ["D3"] if use_table else [],
    }
