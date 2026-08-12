from __future__ import annotations

import math
from typing import Any

from lib import oesc_tables

MM2_PER_IN2 = 645.16
MM_PER_INCH = 25.4

METRIC = "Metric (mm)"
IMPERIAL = "Imperial (inches)"
DISPLAY_UNITS = (METRIC, IMPERIAL)


def conduit_types() -> dict[str, str]:
    # CONDUIT_TYPE_LABELS is label -> internal key; calculators key off the internal key.
    return {key: label for label, key in oesc_tables.CONDUIT_TYPE_LABELS.items()}


def trade_sizes(conduit_type: str) -> list[int]:
    sizes = []
    for size in sorted(set(list(oesc_tables.TABLE_9A) + list(oesc_tables.TABLE_9B))):
        if oesc_tables.get_conduit_9a9b(conduit_type, size):
            sizes.append(size)
    return sizes


def internal_area_mm2(conduit_type: str, trade_size_mm: int) -> float | None:
    entry = oesc_tables.get_conduit_9a9b(conduit_type, trade_size_mm)
    if not entry:
        return None
    area = entry.get("area_mm2")
    return None if area is None else float(area)


def allowable_area_mm2(conduit_type: str, trade_size_mm: int, n_cables: int) -> tuple[float | None, str]:
    area = oesc_tables.get_allowable_conduit_area_mm2(conduit_type, trade_size_mm, max(1, n_cables))
    table = "9C/9D" if n_cables <= 1 else ("9E/9F" if n_cables == 2 else "9G/9H")
    return (None if area is None else float(area)), table


def cable_area_from_od_mm2(od_mm: float) -> float:
    return math.pi * (od_mm / 2.0) ** 2


def smallest_conduit_for(conduit_type: str, total_cable_area_mm2: float, n_cables: int) -> int | None:
    for size in trade_sizes(conduit_type):
        allowed, _table = allowable_area_mm2(conduit_type, size, n_cables)
        if allowed is not None and allowed >= total_cable_area_mm2:
            return size
    return None


def calc_conduit_fill(
    conduit_type: str,
    trade_size_mm: int | None,
    cables: list[dict[str, Any]],
    display_unit: str = METRIC,
    is_low_voltage: bool = False,
    manual_internal_area_mm2: float | None = None,
) -> dict[str, Any]:
    groups = []
    for cable in cables:
        qty = int(cable.get("qty") or 0)
        area_each = cable.get("area_mm2")
        if area_each is None and cable.get("od_mm"):
            area_each = cable_area_from_od_mm2(float(cable["od_mm"]))
        area_each = float(area_each or 0.0)
        groups.append({
            "name": cable.get("name", ""),
            "conductor": cable.get("conductor", ""),
            "size": cable.get("size", ""),
            "qty": qty,
            "conductors_per_cable": int(cable.get("conductors_per_cable") or 1),
            "od_mm": cable.get("od_mm"),
            "area_each_mm2": area_each,
            "area_mm2": area_each * qty,
        })

    n_cables = sum(g["qty"] for g in groups)
    total_area = sum(g["area_mm2"] for g in groups)

    if manual_internal_area_mm2 is not None:
        internal = manual_internal_area_mm2
        allowed, allowed_table = allowable_area_mm2(conduit_type, trade_size_mm, n_cables) if trade_size_mm else (None, "")
    else:
        internal = internal_area_mm2(conduit_type, trade_size_mm) if trade_size_mm else None
        allowed, allowed_table = allowable_area_mm2(conduit_type, trade_size_mm, n_cables) if trade_size_mm else (None, "")

    fill_percent = (total_area / internal * 100.0) if internal else None
    allowed_percent = (allowed / internal * 100.0) if (allowed is not None and internal) else None
    remaining = (allowed - total_area) if allowed is not None else None
    fits = None if (allowed is None or is_low_voltage) else total_area <= allowed + 1e-9

    min_size = None
    if not is_low_voltage and fits is False:
        min_size = smallest_conduit_for(conduit_type, total_area, n_cables)

    source_tables = []
    if trade_size_mm and manual_internal_area_mm2 is None:
        source_tables.append("9A/9B")
    if allowed is not None:
        source_tables.append(allowed_table)

    return {
        "conduit_type": conduit_type,
        "conduit_label": conduit_types().get(conduit_type, conduit_type),
        "trade_size_mm": trade_size_mm,
        "display_unit": display_unit,
        "is_low_voltage": is_low_voltage,
        "manual_internal_area": manual_internal_area_mm2 is not None,
        "groups": groups,
        "n_cables": n_cables,
        "total_cable_area_mm2": total_area,
        "internal_area_mm2": internal,
        "allowed_area_mm2": allowed,
        "allowed_percent": allowed_percent,
        "allowed_table": allowed_table,
        "remaining_area_mm2": remaining,
        "fill_percent": fill_percent,
        "fits": fits,
        "min_trade_size_mm": min_size,
        "primary_table": "9A/9B",
        "source_tables": source_tables,
    }
