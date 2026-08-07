from __future__ import annotations

from typing import Any

from nec_calc.common.report_helper import (
    add_bullets,
    add_kv_section_to_word,
    add_source_table_to_word,
    add_word_equation,
    autosize_cols,
    build_nec_table_row_source,
    get_first,
    init_excel_report,
    init_word_doc,
    notes_to_pairs,
    omml_frac,
    omml_r,
    omml_sub,
    render_export_buttons,
    save_word_doc,
    wb_to_bytes,
    write_kv_sections_to_excel,
    write_source_table_to_excel,
    yes_no,
)

REPORT_TITLE = "NEC Conduit Size, Fill & Bend Radius Report"

def _table_4_columns(units: str) -> list[str]:
    suffix = "mm2" if units == "metric" else "in2"
    return [
        "metric_designator",
        "trade_size",
        f"over_2_wires_40_area_{suffix}",
        f"one_wire_53_area_{suffix}",
        f"two_wires_31_area_{suffix}",
        f"total_area_100_{suffix}",
    ]


def _table_4_column_labels(units: str, area_unit: str) -> dict[str, str]:
    suffix = "mm2" if units == "metric" else "in2"
    return {
        "metric_designator": "Metric Designator",
        "trade_size": "Trade Size",
        f"over_2_wires_40_area_{suffix}": f"40% Fill ({area_unit})",
        f"one_wire_53_area_{suffix}": f"53% Fill ({area_unit})",
        f"two_wires_31_area_{suffix}": f"31% Fill ({area_unit})",
        f"total_area_100_{suffix}": f"100% Area ({area_unit})",
    }

TABLE_2_COLUMNS = [
    "metric_designator",
    "trade_size",
    "one_shot_and_full_shoe_benders_mm",
    "one_shot_and_full_shoe_benders_in",
    "other_bends_mm",
    "other_bends_in",
]

TABLE_2_COLUMN_LABELS = {
    "metric_designator": "Metric Designator",
    "trade_size": "Trade Size",
    "one_shot_and_full_shoe_benders_mm": "One Shot / Full Shoe (mm)",
    "one_shot_and_full_shoe_benders_in": "One Shot / Full Shoe (in.)",
    "other_bends_mm": "Other Bends (mm)",
    "other_bends_in": "Other Bends (in.)",
}


# ============================================================
# Word equation helpers
# ============================================================
def add_conduit_fill_equations(doc) -> None:
    doc.add_heading("Equations Used", level=1)

    eq1 = (
        omml_sub("A", "total")
        + omml_r(" = Σ (N × ")
        + omml_sub("A", "conductor")
        + omml_r(")")
    )

    eq2 = (
        omml_r("Fill % = ")
        + omml_frac(
            omml_sub("A", "total"),
            omml_sub("A", "100%"),
        )
        + omml_r(" × 100")
    )

    eq3 = (
        omml_sub("A", "total")
        + omml_r(" ≤ ")
        + omml_sub("A", "allowed")
    )

    add_word_equation(doc, "Total conductor area", eq1)
    add_word_equation(doc, "Conduit fill", eq2)
    add_word_equation(doc, "Table 1 fill limit", eq3)


def _build_equations_for_excel() -> list[tuple[str, str]]:
    return [
        ("Total conductor area", "A_total = Σ (N × A_conductor)"),
        ("Conduit fill", "Fill % = A_total / A_100% × 100"),
        ("Table 1 fill limit", "A_total ≤ A_allowed"),
    ]


# ============================================================
# Report sections
# ============================================================
def _build_result_pairs(result: dict[str, Any]) -> list[tuple[str, Any]]:
    area_unit = get_first(result, "area_unit", default="mm²")
    return [
        (f"Total conductor area ({area_unit})", get_first(result, "total_conductor_area")),
        ("Allowed fill percent (Table 1)", get_first(result, "allowed_percent")),
        (f"Allowed fill area ({area_unit})", get_first(result, "allowed_area")),
        ("Actual fill percent", get_first(result, "fill_percent")),
        ("Within Table 1 limit", yes_no(get_first(result, "fits"))),
        ("Minimum trade size (this conduit type)", get_first(result, "min_trade_size")),
        ("Bend radius — one shot / full shoe (mm)", get_first(result, "bend_one_shot_mm")),
        ("Bend radius — one shot / full shoe (in.)", get_first(result, "bend_one_shot_in")),
        ("Bend radius — other bends (mm)", get_first(result, "bend_other_mm")),
        ("Bend radius — other bends (in.)", get_first(result, "bend_other_in")),
    ]


def _build_input_pairs(result: dict[str, Any]) -> list[tuple[str, Any]]:
    area_unit = get_first(result, "area_unit", default="mm²")
    pairs: list[tuple[str, Any]] = [
        ("Display units", get_first(result, "units")),
        ("Conduit / tubing type", get_first(result, "conduit_label")),
        ("Trade size", get_first(result, "trade_size")),
        ("Metric designator", get_first(result, "metric_designator")),
        ("Total number of conductors", get_first(result, "n_conductors")),
    ]

    for i, g in enumerate(result.get("groups") or []):
        label = f"{g.get('conductor_type')} {g.get('size')}" if g.get("conductor_type") else "manual area"
        pairs.append(
            (f"Group {i + 1}", f"{g.get('count')}× {label} at {g.get('area')} {area_unit} each")
        )

    return pairs


def _build_notes() -> list[str]:
    return [
        "Conduit fill is evaluated per NEC Chapter 9, Table 1 (53% for one conductor, 31% for two, 40% for three or more), using conduit dimensions from Table 4 and conductor dimensions from Table 5.",
        "Bend radii are the minimums from NEC Chapter 9, Table 2 for the selected trade size.",
        "Chapter 9 notes such as Note 4 (equipment grounding conductors count toward fill) and Note 7 (rounding of same-size conductor counts) must be applied by the designer where relevant.",
        "Final selections and design decisions should be verified against the NEC, project specifications, equipment data, and engineering judgement.",
    ]


def _build_source_tables_from_result(result: dict[str, Any]) -> list[dict[str, Any]]:
    tables = []

    conduit_key = get_first(result, "conduit_key")
    trade_size = get_first(result, "trade_size")
    units = get_first(result, "units", default="metric")
    area_unit = get_first(result, "area_unit", default="mm²")
    if conduit_key and trade_size:
        table_4_source = build_nec_table_row_source(
            table_name=f"TABLE_4_{str(conduit_key).upper()}",
            criteria={"trade_size": trade_size},
            columns=_table_4_columns(units),
            column_labels=_table_4_column_labels(units, area_unit),
            title=f"Selected NEC Chapter 9 Table 4 Row — {get_first(result, 'conduit_label')}",
        )
        if table_4_source:
            tables.append(table_4_source)

    metric_designator = get_first(result, "metric_designator")
    if metric_designator:
        table_2_source = build_nec_table_row_source(
            table_name="TABLE_2",
            criteria={"metric_designator": metric_designator},
            columns=TABLE_2_COLUMNS,
            column_labels=TABLE_2_COLUMN_LABELS,
            title="Selected NEC Chapter 9 Table 2 Row — Radius of Conduit and Tubing Bends",
        )
        if table_2_source:
            tables.append(table_2_source)

    return tables


def _build_report_context(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "notes": _build_notes(),
        "input_pairs": _build_input_pairs(result),
        "result_pairs": _build_result_pairs(result),
        "source_tables": _build_source_tables_from_result(result),
    }


# ============================================================
# Builders
# ============================================================
def build_word_report(result: dict[str, Any]) -> bytes:
    doc = init_word_doc(REPORT_TITLE)
    report_context = _build_report_context(result)

    add_conduit_fill_equations(doc)

    add_bullets(doc, report_context["notes"], heading="Notes and Assumptions")

    add_kv_section_to_word(doc, "Inputs and Parameters Used", report_context["input_pairs"])

    for source_table in report_context["source_tables"]:
        add_source_table_to_word(
            doc,
            source_table,
            font_size_header=7,
            font_size=7,
        )

    add_kv_section_to_word(doc, "Results", report_context["result_pairs"])

    return save_word_doc(doc)


def build_excel_report(result: dict[str, Any]) -> bytes:
    wb, ws, row = init_excel_report(REPORT_TITLE, "Conduit Fill")
    report_context = _build_report_context(result)

    row = write_kv_sections_to_excel(
        ws,
        row,
        [
            ("Equations Used", _build_equations_for_excel()),
            ("Notes and Assumptions", notes_to_pairs(report_context["notes"])),
            ("Inputs and Parameters Used", report_context["input_pairs"]),
        ],
    )

    for source_table in report_context["source_tables"]:
        row = write_source_table_to_excel(ws, row, source_table)

    row = write_kv_sections_to_excel(
        ws,
        row,
        [("Results", report_context["result_pairs"])],
    )

    autosize_cols(ws)
    return wb_to_bytes(wb)


def render_export_report(result: dict[str, Any] | None) -> None:
    can_export = (
        result is not None
        and get_first(result, "fill_percent") is not None
    )

    render_export_buttons(
        prefix="nec_conduit_fill",
        docx_file="nec_conduit_fill_report.docx",
        xlsx_file="nec_conduit_fill_report.xlsx",
        can_export=can_export,
        word_builder=lambda: build_word_report(result or {}),
        excel_builder=lambda: build_excel_report(result or {}),
    )
