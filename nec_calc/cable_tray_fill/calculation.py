from __future__ import annotations

import math
import re
from typing import Any

from lib.nec_tables import TABLES
from nec_calc.common.formatting import _to_float

AREA_UNITS = {"metric": "mm²", "imperial": "in²"}
LENGTH_UNITS = {"metric": "mm", "imperial": "in"}

# Table 392.22 publishes each figure in both unit systems, as a pair of columns.
AREA_SUFFIX = {"metric": "mm2", "imperial": "in2"}
LENGTH_SUFFIX = {"metric": "mm", "imperial": "in"}


# ----------------------------
# cable types, tray types and size bands
# ----------------------------
# 392.22 splits into three sets of rules: multiconductor cables and single-conductor
# cables rated 2000 V or less, and Type MV / MC cables rated over 2000 V.
CABLE_TYPES = {
    "multiconductor": "Multiconductor cables, 2000 V or less — 392.22(A)",
    "single_conductor": "Single-conductor cables, 2000 V or less — 392.22(B)",
    "medium_voltage": "Type MV and Type MC cables, over 2000 V — 392.22(C)",
}

TRAY_TYPES = {
    "ladder_ventilated": "Ladder, ventilated trough, or wire mesh cable tray",
    "solid_bottom": "Solid bottom cable tray",
    "ventilated_channel": "Ventilated channel cable tray",
    "solid_channel": "Solid channel cable tray",
}

# The size band a cable falls into is what selects the rule, so each cable type gets its
# own set of bands rather than a conductor-size lookup.
SIZE_BANDS = {
    "multiconductor": {
        "large": "4/0 AWG and larger",
        "small": "Smaller than 4/0 AWG",
    },
    "single_conductor": {
        "large": "1000 kcmil and larger",
        "medium": "250 kcmil through 900 kcmil",
        "small": "1/0 AWG through 4/0 AWG",
    },
    "medium_voltage": {
        "any": "Type MV or Type MC cable",
    },
}

# Which table and which pair of columns each tray type reads. Table 392.22(A)(1) carries
# both the ladder / ventilated trough / wire mesh columns and the solid bottom columns;
# the channel trays get their own tables, where the pair is one cable / more than one.
TRAY_FILL_SOURCES = {
    "ladder_ventilated": ("table_392_22_a_1", "column_1", "column_2"),
    "solid_bottom": ("table_392_22_a_1", "column_3", "column_4"),
    "ventilated_channel": ("table_392_22_a_5", "column_1", "column_2"),
    "solid_channel": ("table_392_22_a_6", "column_1", "column_2"),
}

SINGLE_CONDUCTOR_SOURCE = ("table_392_22_b_1", "column_1", "column_2")

# 392.22(A)(3)(a): the single layer of 4/0-and-larger cables in a solid bottom tray is
# limited to 90 percent of the tray width rather than the full width.
WIDTH_FACTORS = {
    "ladder_ventilated": 1.0,
    "solid_bottom": 0.90,
}

# Subsection numbering runs (A)(1) for ladder / ventilated trough / wire mesh and (A)(3)
# for solid bottom, with the same (a) / (b) / (c) breakdown under each.
MULTICONDUCTOR_RULES = {
    "ladder_ventilated": {"a": "392.22(A)(1)(a)", "b": "392.22(A)(1)(b)", "c": "392.22(A)(1)(c)"},
    "solid_bottom": {"a": "392.22(A)(3)(a)", "b": "392.22(A)(3)(b)", "c": "392.22(A)(3)(c)"},
}

CHANNEL_RULES = {
    "ventilated_channel": "392.22(A)(5)",
    "solid_channel": "392.22(A)(6)",
}


def get_cable_types() -> dict[str, str]:
    return CABLE_TYPES


def get_tray_types(cable_type: str) -> dict[str, str]:
    # 392.22(B)(1) publishes fill areas for ladder, ventilated trough and wire mesh trays
    # only; 392.22(C) is a width rule, so it needs no fill area at all.
    if cable_type == "single_conductor":
        return {"ladder_ventilated": TRAY_TYPES["ladder_ventilated"]}
    if cable_type == "medium_voltage":
        return {key: TRAY_TYPES[key] for key in ("ladder_ventilated", "solid_bottom")}
    return TRAY_TYPES


def get_size_bands(cable_type: str) -> dict[str, str]:
    return SIZE_BANDS.get(cable_type, {})


# ----------------------------
# table 392.22 helpers
# ----------------------------
def width_column(units: str) -> str:
    """The inside-tray-width column for the chosen unit system."""
    return f"inside_width_{LENGTH_SUFFIX[units]}"


def area_column(column_key: str, units: str) -> str:
    """The fill-area column for one of the table's numbered columns."""
    return f"{column_key}_{AREA_SUFFIX[units]}"


def get_fill_source(cable_type: str, tray_type: str) -> tuple[dict[str, Any] | None, str, str]:
    """Return the table plus the plain and mixed-size column tokens for this combination."""
    key, plain, mixed = (
        SINGLE_CONDUCTOR_SOURCE if cable_type == "single_conductor" else TRAY_FILL_SOURCES[tray_type]
    )
    return TABLES.get(key), plain, mixed


def get_fill_table_key(cable_type: str, tray_type: str) -> str:
    key, _, _ = (
        SINGLE_CONDUCTOR_SOURCE if cable_type == "single_conductor" else TRAY_FILL_SOURCES[tray_type]
    )
    return key


def get_tray_widths(cable_type: str, tray_type: str, units: str = "metric") -> list[Any]:
    table, _, _ = get_fill_source(cable_type, tray_type)
    if table is None:
        return []
    col = width_column(units)
    return [row[col] for row in table["rows"] if row.get(col) is not None]


def get_fill_row(
    table: dict[str, Any] | None,
    tray_width: str | float | None,
    units: str = "metric",
) -> dict[str, Any] | None:
    """Match the row on the numeric width — the tables print '2.0' in one place and '2'
    in another for the same tray."""
    target = _to_float(tray_width)
    if table is None or target is None:
        return None
    col = width_column(units)
    for row in table["rows"]:
        if _to_float(row.get(col)) == target:
            return row
    return None


# The mixed-size columns are published as a formula: '9,000 – (30 Sd)' in one row and
# '11.0 – Sd' in another, with footnote markers attached to either.
_SD_PATTERN = re.compile(r"^\s*([\d,.]+)\s*[-–—−]\s*\(?\s*([\d.]*)\s*Sd", re.IGNORECASE)


def parse_fill_area(value: Any, sd: float | None = None) -> float | None:
    """Read a Table 392.22 fill-area cell. A plain entry is a fixed area; a mixed-size
    entry deducts the summed diameter (Sd) of the larger cables sharing the tray, where a
    bare `Sd` carries a coefficient of 1."""
    area = _to_float(value)
    if area is not None:
        return area

    match = _SD_PATTERN.match(str(value or ""))
    if match is None or sd is None:
        return None

    constant = _to_float(match.group(1))
    if constant is None:
        return None
    coefficient = _to_float(match.group(2))
    coefficient = 1.0 if coefficient is None else coefficient
    return max(0.0, constant - coefficient * float(sd))


def fill_area(
    table: dict[str, Any] | None,
    row: dict[str, Any] | None,
    column_key: str,
    units: str,
    sd: float | None = None,
) -> float | None:
    if row is None:
        return None
    return parse_fill_area(row.get(area_column(column_key, units)), sd)


# ----------------------------
# cable geometry
# ----------------------------
def cable_area(diameter: float | None) -> float | None:
    """Cross-sectional area of one cable from its overall diameter."""
    if not diameter:
        return None
    return math.pi * (float(diameter) / 2.0) ** 2


def _band_totals(groups: list[dict[str, Any]], bands: tuple[str, ...]) -> dict[str, Any]:
    """Cable count, summed diameter and summed area for the groups in the given bands."""
    selected = [g for g in groups if g.get("size_band") in bands]
    return {
        "count": sum(int(g.get("count") or 0) for g in selected),
        "sum_diameters": sum(
            float(g.get("diameter") or 0.0) * int(g.get("count") or 0) for g in selected
        ),
        "sum_areas": sum(float(g.get("area") or 0.0) * int(g.get("count") or 0) for g in selected),
    }


# ----------------------------
# 392.22 rule selection
# ----------------------------
def _multiconductor_check(tray_type, tray_width, groups, table, row, plain, mixed, units):
    rules = MULTICONDUCTOR_RULES[tray_type]
    large = _band_totals(groups, ("large",))
    small = _band_totals(groups, ("small",))

    if small["count"] == 0:
        # (a) every cable is 4/0 AWG or larger — a single layer limited by tray width
        return {
            "rule": rules["a"],
            "description": "Sum of the cable diameters, installed in a single layer",
            "basis": "diameter",
            "value": large["sum_diameters"],
            "limit": tray_width * WIDTH_FACTORS[tray_type] if tray_width is not None else None,
            "sd": None,
            "single_layer": True,
        }

    if large["count"] == 0:
        # (b) every cable is smaller than 4/0 AWG — the whole published fill area
        return {
            "rule": rules["b"],
            "description": "Sum of the cable cross-sectional areas",
            "basis": "area",
            "value": small["sum_areas"],
            "limit": fill_area(table, row, plain, units),
            "sd": None,
            "single_layer": False,
        }

    # (c) a mixture — the smaller cables get what is left after the single layer of
    # 4/0-and-larger cables is deducted
    return {
        "rule": rules["c"],
        "description": "Sum of the cross-sectional areas of the cables smaller than 4/0 AWG",
        "basis": "area",
        "value": small["sum_areas"],
        "limit": fill_area(table, row, mixed, units, large["sum_diameters"]),
        "sd": large["sum_diameters"],
        "single_layer": True,
    }


def _channel_check(tray_type, groups, table, row, plain, mixed, units):
    """392.22(A)(5) and (A)(6) split on cable count, not cable size: one cable gets the
    Column 1 area, more than one shares the smaller Column 2 area."""
    total = _band_totals(groups, tuple(SIZE_BANDS["multiconductor"]))
    one_cable = total["count"] == 1
    return {
        "rule": CHANNEL_RULES[tray_type],
        "description": (
            "Cross-sectional area of the single cable"
            if one_cable
            else "Sum of the cable cross-sectional areas"
        ),
        "basis": "area",
        "value": total["sum_areas"],
        "limit": fill_area(table, row, plain if one_cable else mixed, units),
        "sd": None,
        "single_layer": False,
    }


def _single_conductor_check(tray_width, groups, table, row, plain, mixed, units):
    large = _band_totals(groups, ("large",))
    medium = _band_totals(groups, ("medium",))
    small = _band_totals(groups, ("small",))

    if small["count"]:
        # (d) one 1/0 through 4/0 conductor puts every conductor in the tray on the
        # width rule, whatever else is installed
        return {
            "rule": "392.22(B)(1)(d)",
            "description": "Sum of all single-conductor diameters, installed in a single layer",
            "basis": "diameter",
            "value": large["sum_diameters"] + medium["sum_diameters"] + small["sum_diameters"],
            "limit": tray_width,
            "sd": None,
            "single_layer": True,
        }

    if medium["count"] == 0:
        # (a) every conductor is 1000 kcmil or larger
        return {
            "rule": "392.22(B)(1)(a)",
            "description": "Sum of the single-conductor diameters",
            "basis": "diameter",
            "value": large["sum_diameters"],
            "limit": tray_width,
            "sd": None,
            "single_layer": False,
        }

    if large["count"] == 0:
        # (b) every conductor is 250 kcmil through 900 kcmil
        return {
            "rule": "392.22(B)(1)(b)",
            "description": "Sum of the single-conductor cross-sectional areas",
            "basis": "area",
            "value": medium["sum_areas"],
            "limit": fill_area(table, row, plain, units),
            "sd": None,
            "single_layer": False,
        }

    # (c) a mixture — the 250 through 900 kcmil conductors get what is left after the
    # single layer of 1000 kcmil and larger conductors is deducted
    return {
        "rule": "392.22(B)(1)(c)",
        "description": "Sum of the cross-sectional areas of the 250 through 900 kcmil conductors",
        "basis": "area",
        "value": medium["sum_areas"],
        "limit": fill_area(table, row, mixed, units, large["sum_diameters"]),
        "sd": large["sum_diameters"],
        "single_layer": True,
    }


def _medium_voltage_check(tray_width, groups):
    total = _band_totals(groups, ("any",))
    return {
        "rule": "392.22(C)",
        "description": "Sum of the cable diameters, installed in a single layer",
        "basis": "diameter",
        "value": total["sum_diameters"],
        "limit": tray_width,
        "sd": None,
        "single_layer": True,
    }


def evaluate_fill(
    cable_type: str,
    tray_type: str,
    tray_width: str | float | None,
    groups: list[dict[str, Any]],
    units: str = "metric",
) -> dict[str, Any]:
    """Pick the 392.22 rule that governs this set of cables and return the quantity it
    limits together with the allowable value, plus whether the cables meet it."""
    table, plain, mixed = get_fill_source(cable_type, tray_type)
    row = get_fill_row(table, tray_width, units)
    width = _to_float(tray_width)

    if cable_type == "medium_voltage":
        check = _medium_voltage_check(width, groups)
    elif cable_type == "single_conductor":
        check = _single_conductor_check(width, groups, table, row, plain, mixed, units)
    elif tray_type in CHANNEL_RULES:
        check = _channel_check(tray_type, groups, table, row, plain, mixed, units)
    else:
        check = _multiconductor_check(tray_type, width, groups, table, row, plain, mixed, units)

    limit = check["limit"]
    check["fits"] = None if limit is None else check["value"] <= float(limit)
    check["utilization_percent"] = 100.0 * check["value"] / float(limit) if limit else None
    return check


# ----------------------------
# minimum tray width
# ----------------------------
def find_min_tray_width(
    cable_type: str,
    tray_type: str,
    groups: list[dict[str, Any]],
    units: str = "metric",
) -> str | None:
    """Narrowest published tray width whose 392.22 limit these cables still meet."""
    for width in get_tray_widths(cable_type, tray_type, units):
        if evaluate_fill(cable_type, tray_type, width, groups, units)["fits"]:
            return width
    return None


# ----------------------------
# main calculator function
# ----------------------------
def main_calc_cable_tray_fill(
    cable_type: str,
    tray_type: str,
    tray_width: str,
    groups: list[dict[str, Any]],
    units: str = "metric",
) -> dict[str, Any]:
    # groups: [{"size_band": str, "diameter": float, "count": int, "area": float}]
    # diameters and areas are in the selected unit system, matching the table columns
    check = evaluate_fill(cable_type, tray_type, tray_width, groups, units)
    totals = _band_totals(groups, tuple(get_size_bands(cable_type)))

    return {
        "units": units,
        "area_unit": AREA_UNITS.get(units, "mm²"),
        "length_unit": LENGTH_UNITS.get(units, "mm"),
        "cable_type": cable_type,
        "cable_type_label": CABLE_TYPES.get(cable_type, cable_type),
        "tray_type": tray_type,
        "tray_type_label": TRAY_TYPES.get(tray_type, tray_type),
        "tray_width": tray_width,
        "fill_table_key": get_fill_table_key(cable_type, tray_type),
        "groups": groups,
        "n_cables": totals["count"],
        "total_cable_area": totals["sum_areas"],
        "sum_diameters": totals["sum_diameters"],
        "rule": check["rule"],
        "rule_description": check["description"],
        "limit_basis": check["basis"],
        "limited_value": check["value"],
        "allowed_value": check["limit"],
        "sd": check["sd"],
        "single_layer": check["single_layer"],
        "utilization_percent": check["utilization_percent"],
        "fits": check["fits"],
        "min_tray_width": find_min_tray_width(cable_type, tray_type, groups, units),
    }
