from __future__ import annotations

from typing import Any

from calc_common.formatting import fmt
from calc_common.report_helper import (
    add_word_equation,
    get_first,
    omml_frac,
    omml_r,
    omml_sub,
)
from calc_common.report_schedule import (
    Column,
    ReportSpec,
    render_schedule_commit,
    render_schedule_table,
)
from oesc_calc.cable_tray_fill.calculation import IMPERIAL, MM_PER_INCH
from oesc_calc.common.code_meta import oesc_edition


# ============================================================
# Column value helpers
# ============================================================
def _display_area(result: dict[str, Any], key: str) -> str:
    value = get_first(result, key)
    if value is None:
        return "—"
    return fmt(value / get_first(result, "area_conversion", default=1.0), get_first(result, "area_unit", default="mm²"))


def _display_length(result: dict[str, Any], key: str) -> str:
    value = get_first(result, key)
    if value is None:
        return "—"
    if get_first(result, "tray_unit") == IMPERIAL:
        value = value / MM_PER_INCH
    return fmt(value, get_first(result, "length_unit", default="mm"))


def _tray_size(result: dict[str, Any]) -> str:
    return f"{_display_length(result, 'tray_width_mm')} × {_display_length(result, 'tray_depth_mm')}"


def _groups(result: dict[str, Any]) -> str:
    groups = result.get("groups") or []
    return str(len(groups)) if groups else "—"


def _largest_group(result: dict[str, Any]) -> str:
    groups = result.get("groups") or []
    if not groups:
        return "—"
    biggest = max(groups, key=lambda g: g.get("area_mm2") or 0)
    name = biggest.get("name") or "[unnamed]"
    percent = biggest.get("percent_of_tray")
    return f"{name} ({percent:.1f}%)" if percent is not None else name


def _edition(result: dict[str, Any]) -> str:
    return oesc_edition()


# ============================================================
# Report-wide text
# ============================================================
def _code_reference(results: list[dict[str, Any]]) -> str:
    return f"Per {oesc_edition()} Rule 12-2202 — cable tray fill"


def _word_reference(doc, results: list[dict[str, Any]]) -> None:
    """Equations used across the calculations in the schedule (Word report only)."""
    doc.add_heading("Equations Used", level=1)

    add_word_equation(doc, "Tray usable area", omml_sub("A", "tray") + omml_r(" = w × d"))
    add_word_equation(
        doc, "Cable cross-sectional area",
        omml_sub("A", "cable") + omml_r(" = π × (OD ÷ 2)²"),
    )
    add_word_equation(
        doc, "Total cable area",
        omml_sub("A", "total") + omml_r(" = Σ (n × ") + omml_sub("A", "cable") + omml_r(")"),
    )
    add_word_equation(
        doc, "Tray fill",
        omml_r("Fill % = ") + omml_frac(omml_sub("A", "total"), omml_sub("A", "tray")) + omml_r(" × 100"),
    )


def _footnotes(results: list[dict[str, Any]]) -> list[str]:
    edition = oesc_edition()

    notes = [
        "Tray fill is the summed cross-sectional area of the cables as a percentage of the "
        "tray's usable cross-section, taken as inside width × inside depth.",
        "Cable cross-sectional areas are computed from the overall diameters entered into "
        "the calculator; these come from manufacturer's data, not from an OESC table.",
        f"The permitted fill and the cable spacing, layering and securing requirements of "
        f"{edition} Section 12 must be applied by the designer; this calculator reports the "
        "fill percentage only.",
        "Cable tray ampacity adjustment for grouped cables is outside the scope of this "
        "calculation.",
        "Values are shown in the unit system each row was entered in.",
        "This report is based on the input values entered into the calculator. Final "
        "selections and design decisions should be verified against the OESC, project "
        "specifications, equipment data, and engineering judgement.",
    ]

    return notes


# ============================================================
# Schedule spec + entry point
# ============================================================
CT_SCHEDULE_SPEC = ReportSpec(
    code="oesc",
    calculator="cable_tray_fill",
    report_title="Cable Tray Fill — Calculation Results",
    sheet_name="Cable Tray Fill Schedule",
    tag="Tag / ID",
    cols=[
        Column("Tray name", lambda r: get_first(r, "tray_name", default="—")),
        Column("Units", lambda r: get_first(r, "tray_unit", default="—")),
        Column("Tray size (w × d)", _tray_size),
        Column("Usable area", lambda r: _display_area(r, "tray_area_mm2")),
        Column("Cable groups", _groups),
        Column("No. of cables", lambda r: get_first(r, "n_cables", default="—")),
        Column("Area used", lambda r: _display_area(r, "total_cable_area_mm2")),
        Column("Largest group", _largest_group),
        Column("Fill (%)", lambda r: fmt(get_first(r, "fill_percentage"), "%"), color="green"),
        Column("Code Edition", _edition),
    ],
    code_reference=_code_reference,
    notes=_footnotes,
    word_reference=_word_reference,
)


def render_add_to_schedule(result: dict[str, Any] | None) -> None:
    can_add = bool(result and result.get("groups"))
    render_schedule_commit(CT_SCHEDULE_SPEC, result, can_add=can_add)


def render_schedule_section() -> None:
    render_schedule_table(CT_SCHEDULE_SPEC)
