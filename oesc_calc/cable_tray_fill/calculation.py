from __future__ import annotations

import math
from typing import Any

METRIC = "Metric (mm)"
IMPERIAL = "Imperial (inches)"
TRAY_UNITS = (METRIC, IMPERIAL)

MM_PER_INCH = 25.4
MM2_PER_IN2 = 645.16


def area_unit(tray_unit: str) -> str:
    return "in²" if tray_unit == IMPERIAL else "mm²"


def length_unit(tray_unit: str) -> str:
    return "in" if tray_unit == IMPERIAL else "mm"


def area_conversion(tray_unit: str) -> float:
    return MM2_PER_IN2 if tray_unit == IMPERIAL else 1.0


def to_mm(value: float, unit: str) -> float:
    return value * (MM_PER_INCH if unit == "in" else 1.0)


def cable_area_mm2(od_mm: float) -> float:
    return math.pi * (od_mm / 2.0) ** 2


def calc_cable_tray_fill(
    tray_unit: str,
    tray_width_mm: float,
    tray_depth_mm: float,
    cables: list[dict[str, Any]],
    tray_name: str = "",
) -> dict[str, Any]:
    tray_area = tray_width_mm * tray_depth_mm

    groups = []
    for cable in cables:
        od_mm = float(cable.get("od_mm") or 0.0)
        qty = int(cable.get("qty") or 0)
        single = cable_area_mm2(od_mm)
        total = qty * single
        groups.append({
            "name": cable.get("name", ""),
            "conductor": cable.get("conductor", ""),
            "gauge": cable.get("gauge", ""),
            "od_mm": od_mm,
            "qty": qty,
            "area_single_mm2": single,
            "area_mm2": total,
            "percent_of_tray": (total / tray_area * 100) if tray_area > 0 else None,
        })

    total_area = sum(g["area_mm2"] for g in groups)
    fill_percent = (total_area / tray_area * 100) if tray_area > 0 else 0

    return {
        "tray_name": tray_name,
        "tray_unit": tray_unit,
        "area_unit": area_unit(tray_unit),
        "length_unit": length_unit(tray_unit),
        "area_conversion": area_conversion(tray_unit),
        "tray_width_mm": tray_width_mm,
        "tray_depth_mm": tray_depth_mm,
        "tray_area_mm2": tray_area,
        "groups": groups,
        "n_cables": sum(g["qty"] for g in groups),
        "total_cable_area_mm2": total_area,
        "fill_percentage": fill_percent,
        "primary_table": None,
        "source_tables": [],
    }
