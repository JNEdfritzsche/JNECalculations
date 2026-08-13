from __future__ import annotations

from typing import Any

from calc_common.formatting import fmt
from calc_common.report_helper import (
    add_word_equation,
    get_first,
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
from lib.nec_tables import (
    TABLE_392_22_A_1,
    TABLE_392_22_A_5,
    TABLE_392_22_A_6,
    TABLE_392_22_B_1,
)


CABLE_TYPE_LABELS = {
    "multiconductor": "Multiconductor",
    "single_conductor": "Single-conductor",
    "medium_voltage": "Type MV / MC",
}

TRAY_TYPE_LABELS = {
    "ladder_ventilated": "Ladder / vent. trough / wire mesh",
    "solid_bottom": "Solid bottom",
    "ventilated_channel": "Ventilated channel",
    "solid_channel": "Solid channel",
}

FILL_TABLES = {
    "table_392_22_a_1": TABLE_392_22_A_1,
    "table_392_22_a_5": TABLE_392_22_A_5,
    "table_392_22_a_6": TABLE_392_22_A_6,
    "table_392_22_b_1": TABLE_392_22_B_1,
}

FILL_TABLE_LABELS = {
    "table_392_22_a_1": "392.22(A)(1)",
    "table_392_22_a_5": "392.22(A)(5)",
    "table_392_22_a_6": "392.22(A)(6)",
    "table_392_22_b_1": "392.22(B)(1)",
}


# ============================================================
# Column value helpers
# ============================================================
def _area_unit(result: dict[str, Any]) -> str:
    return get_first(result, "area_unit", default="mm²")


def _length_unit(result: dict[str, Any]) -> str:
    return get_first(result, "length_unit", default="mm")


def _basis_unit(result: dict[str, Any]) -> str:
    return _area_unit(result) if get_first(result, "limit_basis") == "area" else _length_unit(result)


def _units(result: dict[str, Any]) -> str:
    units = get_first(result, "units")
    return "—" if units is None else f"{str(units).title()} ({_length_unit(result)}/{_area_unit(result)})"


def _cable_type(result: dict[str, Any]) -> str:
    key = get_first(result, "cable_type")
    return CABLE_TYPE_LABELS.get(str(key or ""), get_first(result, "cable_type_label", default="—"))


def _tray_type(result: dict[str, Any]) -> str:
    key = get_first(result, "tray_type")
    return TRAY_TYPE_LABELS.get(str(key or ""), get_first(result, "tray_type_label", default="—"))


def _basis(result: dict[str, Any]) -> str:
    basis = get_first(result, "limit_basis")
    return {"area": "Cable area", "diameter": "Cable diameters"}.get(str(basis or ""), "—")


def _uses_fill_table(result: dict[str, Any]) -> bool:
    """Diameter-basis rules are limited by the tray width itself, not a published area."""
    return get_first(result, "limit_basis") == "area"


# ============================================================
# Code reference — edition comes from the table's own CSV front matter
# ============================================================
def _nec_edition(table: dict[str, Any] | None = None) -> str:
    edition = (table or TABLE_392_22_A_1).get("edition") or TABLE_392_22_B_1.get("edition")
    return f"NEC {edition}" if edition else "NEC"


def _edition(result: dict[str, Any]) -> str:
    return _nec_edition(FILL_TABLES.get(get_first(result, "fill_table_key")))


def _source_table(result: dict[str, Any]) -> str:
    if not _uses_fill_table(result):
        return "—"
    return FILL_TABLE_LABELS.get(str(get_first(result, "fill_table_key") or ""), "—")


# ============================================================
# Report-wide text
# ============================================================
def _code_reference(results: list[dict[str, Any]]) -> str:
    return f"Per {_nec_edition()} 392.22"


def _has_reduced_area(results: list[dict[str, Any]]) -> bool:
    return any(get_first(r, "sd") is not None for r in results)


def _word_reference(doc, results: list[dict[str, Any]]) -> None:
    """Equations used across the calculations in the schedule (Word report only)."""
    doc.add_heading("Equations Used", level=1)

    add_word_equation(
        doc,
        "Cable cross-sectional area",
        omml_sub("A", "cable") + omml_r(" = π × (OD ÷ 2)²"),
    )
    add_word_equation(
        doc,
        "Total cable area",
        omml_sub("A", "total") + omml_r(" = Σ (N × ") + omml_sub("A", "cable") + omml_r(")"),
    )
    add_word_equation(
        doc,
        "Sum of cable diameters",
        omml_sub("S", "d") + omml_r(" = Σ (N × OD)"),
    )

    if _has_reduced_area(results):
        add_word_equation(
            doc,
            "Allowable fill area, mixed cable sizes",
            omml_sub("A", "allowed")
            + omml_r(" = ")
            + omml_sub("A", "const")
            + omml_r(" − k × ")
            + omml_sub("S", "d"),
        )


def _footnotes(results: list[dict[str, Any]]) -> list[str]:
    edition = _nec_edition()

    notes = [
        f"Cable tray fill is evaluated per {edition} 392.22 using the allowable fill areas "
        "of Tables 392.22(A)(1), 392.22(A)(5) and 392.22(A)(6) for multiconductor cables and "
        "Table 392.22(B)(1) for single-conductor cables, rated 2000 volts or less.",
        "The Governing rule column gives the 392.22 subsection each row was evaluated under; "
        "Limited by gives the quantity that rule restricts. Rows limited by cable diameters "
        "are checked against the tray width itself, so they cite no fill table.",
        "Cable cross-sectional areas are computed from the overall cable diameters entered "
        "into the calculator; these come from manufacturer's data, not from an NEC table.",
    ]

    if _has_reduced_area(results):
        notes.append(
            "Where cables of both size bands share the tray, the allowable fill area for the "
            "smaller cables is reduced by the summed diameter (Sd) of the larger cables, per "
            "the mixed-size column of the applicable table."
        )

    if any(r.get("single_layer") for r in results):
        notes.append(
            "Rows marked Single layer are governed by a rule that also requires the cables to "
            "be installed in a single layer. This calculator checks the summed diameters and "
            "areas only; confirm the physical arrangement in the tray."
        )

    notes += [
        "Values are shown in the unit system each row was calculated in, as Table 392.22 "
        "publishes both.",
        "Cable tray ampacity adjustment (392.80), tray support and the securing requirements "
        "of 392.18 and 392.30 are outside the scope of this calculation.",
        "This report is based on the input values entered into the calculator. Final "
        "selections and design decisions should be verified against the NEC, project "
        "specifications, equipment data, and engineering judgement.",
    ]

    return notes


# ============================================================
# Schedule spec + entry point
# ============================================================
CT_SCHEDULE_SPEC = ReportSpec(
    code="nec",
    calculator="cable_tray_fill",
    report_title="Cable Tray Fill — Calculation Results",
    sheet_name="Cable Tray Fill Schedule",
    tag="Tag / ID",
    cols=[
        Column("Units", _units),
        Column("Cables", _cable_type),
        Column("Tray type", _tray_type, group="tray"),
        Column("Tray width", lambda r: fmt(get_first(r, "tray_width"), _length_unit(r)), group="tray"),
        Column("No. of cables", lambda r: get_first(r, "n_cables", default="—"), result=True),
        Column("Total cable area", lambda r: fmt(get_first(r, "total_cable_area"), _area_unit(r)), result=True),
        Column("Sum of diameters", lambda r: fmt(get_first(r, "sum_diameters"), _length_unit(r)), result=True),
        Column("Governing rule", lambda r: get_first(r, "rule", default="—")),
        Column("Limited by", _basis),
        Column("Allowed", lambda r: fmt(get_first(r, "allowed_value"), _basis_unit(r)), result=True),
        Column("Sd", lambda r: fmt(get_first(r, "sd"), _length_unit(r)), result=True),
        Column("Utilization (%)", lambda r: fmt(get_first(r, "utilization_percent"), "%"), color="green", result=True),
        Column("Fits?", lambda r: yes_no(get_first(r, "fits")), result=True, always=True),
        Column("Single layer", lambda r: yes_no(get_first(r, "single_layer"))),
        Column("Min tray width", lambda r: fmt(get_first(r, "min_tray_width"), _length_unit(r)), color="blue", result=True),
        Column("Code Edition", _edition),
        Column("Source Table", _source_table),
    ],
    groups={
        "tray": Group("Tray"),
    },
    code_reference=_code_reference,
    notes=_footnotes,
    word_reference=_word_reference,
)


def render_add_to_schedule(result: dict[str, Any] | None) -> None:
    can_add = result is not None and get_first(result, "limited_value") is not None
    render_schedule_commit(CT_SCHEDULE_SPEC, result, can_add=can_add)


def render_schedule_section() -> None:
    render_schedule_table(CT_SCHEDULE_SPEC)
