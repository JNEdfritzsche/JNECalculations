from __future__ import annotations

from typing import Any

from calc_common.formatting import fmt
from calc_common.report_helper import (
    add_word_equation,
    get_first,
    omml_r,
    omml_sub,
)
from calc_common.report_schedule import (
    Column,
    ReportSpec,
    render_schedule_commit,
    render_schedule_table,
)
from oesc_calc.common.code_meta import cite, oesc_edition


# ============================================================
# Column value helpers
# ============================================================
def _row(result: dict[str, Any]) -> str:
    row = get_first(result, "table_29_row")
    return "—" if row is None else f"Row {row}"


def _multiplier(result: dict[str, Any]) -> str:
    multiplier = get_first(result, "multiplier")
    return "—" if multiplier is None else f"{multiplier:g}× ({multiplier * 100:g}%)"


def _selected(result: dict[str, Any]) -> str:
    selected = get_first(result, "selected_std")
    return "Below smallest rating" if selected is None else fmt(selected, "A")


def _starter(result: dict[str, Any]) -> str:
    return get_first(result, "starter_type", default="—")


def _edition(result: dict[str, Any]) -> str:
    return oesc_edition(get_first(result, "primary_table"))


def _source_tables(result: dict[str, Any]) -> str:
    return cite(get_first(result, "source_tables", default=[]))


# ============================================================
# Report-wide text
# ============================================================
def _code_reference(results: list[dict[str, Any]]) -> str:
    return f"Per {oesc_edition()} Rules 28-200 and 28-204, Table 29"


def _word_reference(doc, results: list[dict[str, Any]]) -> None:
    """Equations used across the calculations in the schedule (Word report only)."""
    doc.add_heading("Equations Used", level=1)

    add_word_equation(
        doc,
        "Overcurrent device setting",
        omml_sub("I", "OCPD") + omml_r(" = k × ") + omml_sub("I", "FLA"),
    )


def _footnotes(results: list[dict[str, Any]]) -> list[str]:
    edition = oesc_edition()

    notes = [
        f"Motor branch-circuit overcurrent device sizing follows the {edition} Table 29 "
        "flowchart of Rules 28-200 and 28-204. The Table 29 row is selected by voltage "
        "system, motor type and starter type, and by whether the full-load current exceeds "
        "30 A for auto-transformer and star-delta starting.",
        "The multiplier k is the maximum rating or setting permitted by Table 29 for the "
        "selected row and device type, applied to the motor nameplate full-load current.",
        "The selected rating is the largest standard overcurrent device rating below the "
        "calculated value, so the result never exceeds the Table 29 maximum. A value that "
        "lands exactly on a standard rating selects the next rating down.",
        "Full-load current is the motor nameplate value as entered; it is not read from "
        "Table 44, 45 or D2.",
        "This report is based on the input values entered into the calculator. Final "
        "selections and design decisions should be verified against the OESC, project "
        "specifications, equipment data, and engineering judgement.",
    ]

    if any(get_first(r, "selected_std") is None for r in results):
        notes.append(
            "Rows showing Below smallest rating produced a value under the smallest "
            "standard device rating; select a device by inspection for those circuits."
        )

    return notes


# ============================================================
# Schedule spec + entry point
# ============================================================
MP_SCHEDULE_SPEC = ReportSpec(
    code="oesc",
    calculator="motor_protection",
    report_title="Motor Protection — Calculation Results",
    sheet_name="Motor Protection Schedule",
    tag="Tag / ID",
    cols=[
        Column("Voltage system", lambda r: get_first(r, "voltage_system", default="—")),
        Column("Motor type", lambda r: get_first(r, "motor_type", default="—")),
        Column("Starter type", _starter),
        Column("I_FLA (A)", lambda r: fmt(get_first(r, "fla"), "A")),
        Column("Table 29 row", _row),
        Column("Row description", lambda r: get_first(r, "row_description", default="—")),
        Column("Device type", lambda r: get_first(r, "device_label", default="—")),
        Column("Multiplier, k", _multiplier),
        Column("OCPD raw (A)", lambda r: fmt(get_first(r, "ocpd_raw"), "A")),
        Column("Selected rating", _selected, color="green"),
        Column("Code Edition", _edition),
        Column("Source Tables", _source_tables),
    ],
    code_reference=_code_reference,
    notes=_footnotes,
    word_reference=_word_reference,
)


def render_add_to_schedule(result: dict[str, Any] | None) -> None:
    can_add = result is not None and get_first(result, "ocpd_raw") is not None
    render_schedule_commit(MP_SCHEDULE_SPEC, result, can_add=can_add)


def render_schedule_section() -> None:
    render_schedule_table(MP_SCHEDULE_SPEC)
