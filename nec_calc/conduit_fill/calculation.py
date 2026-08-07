from __future__ import annotations

from typing import Any

from lib.nec_tables import TABLE_2, TABLE_4, TABLE_5, get_cross_sectional_area_percent
from nec_calc.common.table_helpers import get_table_row

AREA_UNITS = {"metric": "mm²", "imperial": "in²"}
LENGTH_UNITS = {"metric": "mm", "imperial": "in"}


def _area_suffix(units: str) -> str:
    return "mm2" if units == "metric" else "in2"


# ----------------------------
# table 4 helpers (conduit dimensions)
# ----------------------------
def get_conduit_types() -> dict[str, str]:
    # key -> display title, e.g. 'emt' -> 'Article 358 — Electrical Metallic Tubing (EMT)'
    return {key: sub["title"] for key, sub in TABLE_4["tables"].items()}


def get_conduit_table(conduit_key: str) -> dict[str, Any] | None:
    return TABLE_4["tables"].get(conduit_key)


def get_trade_sizes(conduit_key: str) -> list[str]:
    sub = get_conduit_table(conduit_key)
    if sub is None:
        return []
    return [row["trade_size"] for row in sub["rows"]]


def get_conduit_row(conduit_key: str, trade_size: str) -> dict[str, Any] | None:
    sub = get_conduit_table(conduit_key)
    if sub is None:
        return None
    return get_table_row(sub, {"trade_size": trade_size})


def allowed_fill_area(row: dict[str, Any] | None, n_conductors: int, units: str = "metric") -> float | None:
    # table 1 percentages map onto the precomputed table 4 fill columns
    if row is None:
        return None
    suffix = _area_suffix(units)
    if n_conductors <= 1:
        key = f"one_wire_53_area_{suffix}"
    elif n_conductors == 2:
        key = f"two_wires_31_area_{suffix}"
    else:
        key = f"over_2_wires_40_area_{suffix}"
    return row.get(key)


# ----------------------------
# table 5 helpers (conductor dimensions)
# ----------------------------
def get_conductor_types() -> list[str]:
    types: list[str] = []
    for row in TABLE_5["rows"]:
        t = row["type"]
        if t not in types:
            types.append(t)
    return types


def get_conductor_sizes(conductor_type: str) -> list[str]:
    sizes: list[str] = []
    for row in TABLE_5["rows"]:
        if row["type"] == conductor_type:
            size = row["size_awg_kcmil"]
            if size not in sizes:
                sizes.append(size)
    return sizes


def get_conductor_area(conductor_type: str, size: str, units: str = "metric") -> float | None:
    row = get_table_row(TABLE_5, {"type": conductor_type, "size_awg_kcmil": size})
    if row is None:
        return None
    col = "approximate_area_mm2" if units == "metric" else "approximate_area_in2"
    return row.get(col)


# ----------------------------
# table 2 helpers (bend radius)
# ----------------------------
def get_bend_radius_row(metric_designator: str) -> dict[str, Any] | None:
    # keyed on metric designator: table 2 trade sizes use '1 1/4' while table 4 uses '1-1/4'
    return get_table_row(TABLE_2, {"metric_designator": metric_designator})


# ----------------------------
# minimum conduit size
# ----------------------------
def find_min_trade_size(
    conduit_key: str,
    total_conductor_area: float,
    n_conductors: int,
    units: str = "metric",
) -> dict[str, Any] | None:
    sub = get_conduit_table(conduit_key)
    if sub is None:
        return None
    for row in sub["rows"]:
        allowed = allowed_fill_area(row, n_conductors, units)
        if allowed is not None and allowed >= total_conductor_area:
            return row
    return None


# ----------------------------
# main calculator function
# ----------------------------
def main_calc_conduit_fill(
    conduit_key: str,
    trade_size: str,
    groups: list[dict[str, Any]],
    units: str = "metric",
) -> dict[str, Any]:
    # groups: [{"conductor_type": str | None, "size": str | None, "count": int, "area": float}]
    # all areas/lengths are in the selected unit system, read from the matching table columns
    suffix = _area_suffix(units)
    conduit_row = get_conduit_row(conduit_key, trade_size)

    n_conductors = sum(int(g.get("count") or 0) for g in groups)
    total_area = sum(
        float(g.get("area") or 0.0) * int(g.get("count") or 0) for g in groups
    )

    allowed_percent = get_cross_sectional_area_percent(n_conductors) if n_conductors >= 1 else None
    allowed_area = allowed_fill_area(conduit_row, n_conductors, units)
    internal_area = conduit_row.get(f"total_area_100_{suffix}") if conduit_row else None

    fill_percent = None
    if internal_area:
        fill_percent = 100.0 * total_area / float(internal_area)

    fits = None
    if allowed_area is not None:
        fits = total_area <= float(allowed_area)

    min_row = find_min_trade_size(conduit_key, total_area, n_conductors, units) if n_conductors >= 1 else None

    metric_designator = conduit_row.get("metric_designator") if conduit_row else None
    bend_row = get_bend_radius_row(metric_designator) if metric_designator else None

    return {
        "units": units,
        "area_unit": AREA_UNITS.get(units, "mm²"),
        "length_unit": LENGTH_UNITS.get(units, "mm"),
        "conduit_key": conduit_key,
        "conduit_label": get_conduit_types().get(conduit_key, conduit_key),
        "trade_size": trade_size,
        "metric_designator": metric_designator,
        "groups": groups,
        "n_conductors": n_conductors,
        "total_conductor_area": total_area,
        "internal_area": internal_area,
        "allowed_percent": allowed_percent,
        "allowed_area": allowed_area,
        "fill_percent": fill_percent,
        "fits": fits,
        "min_trade_size": min_row.get("trade_size") if min_row else None,
        "min_metric_designator": min_row.get("metric_designator") if min_row else None,
        "bend_one_shot_mm": bend_row.get("one_shot_and_full_shoe_benders_mm") if bend_row else None,
        "bend_one_shot_in": bend_row.get("one_shot_and_full_shoe_benders_in") if bend_row else None,
        "bend_other_mm": bend_row.get("other_bends_mm") if bend_row else None,
        "bend_other_in": bend_row.get("other_bends_in") if bend_row else None,
    }
