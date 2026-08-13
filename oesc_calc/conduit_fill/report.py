from __future__ import annotations

from typing import Any

from calc_common.formatting import fmt
from calc_common.report_helper import (
    add_word_equation,
    get_first,
    omml_frac,
    omml_r,
    omml_sub,
    yes_no,
)
from calc_common.report_schedule import (
    Column,
    Group,
    ReportSpec,
    render_schedule_commit,
    render_schedule_table,
)
from oesc_calc.common.code_meta import cite, oesc_edition
from oesc_calc.conduit_fill.calculation import IMPERIAL, MM2_PER_IN2


# ============================================================
# Column value helpers
# ============================================================
def _area(result: dict[str, Any], key: str) -> str:
    value = get_first(result, key)
    if value is None:
        return "—"
    if get_first(result, "display_unit") == IMPERIAL:
        return fmt(value / MM2_PER_IN2, "in²")
    return fmt(value, "mm²")


def _trade_size(result: dict[str, Any]) -> str:
    return fmt(get_first(result, "trade_size_mm"), "mm")


def _min_size(result: dict[str, Any]) -> str:
    return fmt(get_first(result, "min_trade_size_mm"), "mm")


def _fits(result: dict[str, Any]) -> str:
    if result.get("is_low_voltage"):
        return "n/a (low voltage)"
    fits = result.get("fits")
    return "—" if fits is None else yes_no(fits)


def _edition(result: dict[str, Any]) -> str:
    return oesc_edition(get_first(result, "primary_table"))


def _source_tables(result: dict[str, Any]) -> str:
    return cite(get_first(result, "source_tables", default=[]))


# ============================================================
# Report-wide text
# ============================================================
def _code_reference(results: list[dict[str, Any]]) -> str:
    return f"Per {oesc_edition()} Rule 12-910 and Tables 9A to 9H"


def _word_reference(doc, results: list[dict[str, Any]]) -> None:
    """Equations used across the calculations in the schedule (Word report only)."""
    doc.add_heading("Equations Used", level=1)

    add_word_equation(
        doc, "Cable cross-sectional area",
        omml_sub("A", "cable") + omml_r(" = π × (OD ÷ 2)²"),
    )
    add_word_equation(
        doc, "Total cable area",
        omml_sub("A", "total") + omml_r(" = Σ (n × ") + omml_sub("A", "cable") + omml_r(")"),
    )
    add_word_equation(
        doc, "Conduit fill",
        omml_r("Fill % = ") + omml_frac(omml_sub("A", "total"), omml_sub("A", "internal")) + omml_r(" × 100"),
    )
    add_word_equation(
        doc, "Allowable fill",
        omml_sub("A", "total") + omml_r(" ≤ ") + omml_sub("A", "allowed"),
    )


def _footnotes(results: list[dict[str, Any]]) -> list[str]:
    edition = oesc_edition()

    notes = [
        f"Conduit internal areas are the 100% areas of {edition} Tables 9A and 9B for the "
        "selected conduit type and trade size.",
        "Allowable fill areas come from Tables 9C and 9D for one cable (53%), Tables 9E and "
        "9F for two cables (31%), and Tables 9G and 9H for three or more cables (40%). The "
        "Source Tables column records which pair each row used.",
        "Cable cross-sectional areas are computed from the overall diameters entered, or "
        "taken from the Table 6 series where a cable type and size were selected. Overall "
        "diameters come from manufacturer's data where a cable is not in those tables.",
        "Rows marked low voltage are not checked against the allowable fill; confirm the "
        "conditions under which the fill limits do not apply.",
        "Where the cables exceed the allowable area, the minimum trade size column gives the "
        "smallest size of the same conduit type that accepts them.",
        "This report is based on the input values entered into the calculator. Final "
        "selections and design decisions should be verified against the OESC, project "
        "specifications, equipment data, and engineering judgement.",
    ]

    return notes


# ============================================================
# Schedule spec + entry point
# ============================================================
CF_SCHEDULE_SPEC = ReportSpec(
    code="oesc",
    calculator="conduit_fill",
    report_title="Conduit Fill — Calculation Results",
    sheet_name="Conduit Fill Schedule",
    tag="Tag / ID",
    cols=[
        Column("Conduit / tubing", lambda r: get_first(r, "conduit_label", default="—"), group="conduit"),
        Column("Trade size", _trade_size, group="conduit"),
        Column("Cables", lambda r: get_first(r, "n_cables", default="—"), result=True),
        Column("Total cable area", lambda r: _area(r, "total_cable_area_mm2"), result=True),
        Column("Internal area (100%)", lambda r: _area(r, "internal_area_mm2"), result=True),
        Column("Allowable area", lambda r: _area(r, "allowed_area_mm2"), result=True, group="allowable"),
        Column("Allowable fill (%)", lambda r: fmt(get_first(r, "allowed_percent"), "%"), result=True, group="allowable"),
        Column("Actual fill (%)", lambda r: fmt(get_first(r, "fill_percent"), "%"), color="green", result=True),
        Column("Fits?", _fits, result=True, always=True),
        Column("Min trade size", _min_size, color="blue", result=True),
        Column("Low voltage", lambda r: yes_no(r.get("is_low_voltage"))),
        Column("Code Edition", _edition),
        Column("Source Tables", _source_tables),
    ],
    groups={
        "conduit": Group("Conduit"),
        "allowable": Group("Allowable (area / %)"),
    },
    code_reference=_code_reference,
    notes=_footnotes,
    word_reference=_word_reference,
)


def render_add_to_schedule(result: dict[str, Any] | None) -> None:
    can_add = result is not None and get_first(result, "fill_percent") is not None
    render_schedule_commit(CF_SCHEDULE_SPEC, result, can_add=can_add)


def render_schedule_section() -> None:
    render_schedule_table(CF_SCHEDULE_SPEC)
