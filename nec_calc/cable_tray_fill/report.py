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
    omml_r,
    omml_sub,
    render_export_buttons,
    save_word_doc,
    wb_to_bytes,
    write_kv_sections_to_excel,
    write_source_table_to_excel,
    yes_no,
)

from nec_calc.cable_tray_fill.calculation import area_column, get_fill_source, width_column

REPORT_TITLE = "NEC Cable Tray Size & Fill Report"

# ============================================================
# Word equation helpers
# ============================================================
def add_cable_tray_fill_equations(doc, context: dict[str, Any]) -> None:
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
    if context["has_reduced_area"]:
        add_word_equation(
            doc,
            "Allowable fill area, mixed cable sizes",
            omml_sub("A", "allowed")
            + omml_r(" = ")
            + omml_sub("A", "const")
            + omml_r(" − k × ")
            + omml_sub("S", "d"),
        )


def _build_equations_for_excel(context: dict[str, Any]) -> list[tuple[str, str]]:
    equations = [
        ("Cable cross-sectional area", "A_cable = π × (OD / 2)²"),
        ("Total cable area", "A_total = Σ (N × A_cable)"),
        ("Sum of cable diameters", "S_d = Σ (N × OD)"),
    ]
    if context["has_reduced_area"]:
        equations.append(("Allowable fill area, mixed cable sizes", "A_allowed = A_const − k × S_d"))
    return equations


# ============================================================
# Report sections
# ============================================================
def _build_result_pairs(result: dict[str, Any]) -> list[tuple[str, Any]]:
    area_unit = get_first(result, "area_unit", default="mm²")
    length_unit = get_first(result, "length_unit", default="mm")
    basis_unit = area_unit if get_first(result, "limit_basis") == "area" else length_unit

    pairs: list[tuple[str, Any]] = [
        ("Governing rule", f"NEC {get_first(result, 'rule')}"),
        ("Quantity limited by the rule", get_first(result, "rule_description")),
        (f"Total cable area ({area_unit})", get_first(result, "total_cable_area")),
        (f"Sum of cable diameters ({length_unit})", get_first(result, "sum_diameters")),
        (f"Value checked against the limit ({basis_unit})", get_first(result, "limited_value")),
        (f"Allowable value ({basis_unit})", get_first(result, "allowed_value")),
        ("Utilization of the limit (%)", get_first(result, "utilization_percent")),
        ("Within the 392.22 limit", yes_no(get_first(result, "fits"))),
        ("Single layer required", yes_no(get_first(result, "single_layer"))),
        (f"Minimum tray width ({length_unit})", get_first(result, "min_tray_width")),
    ]
    if result.get("sd") is not None:
        pairs.insert(5, (f"Summed diameter of the larger cables, Sd ({length_unit})", get_first(result, "sd")))
    return pairs


def _build_input_pairs(result: dict[str, Any]) -> list[tuple[str, Any]]:
    area_unit = get_first(result, "area_unit", default="mm²")
    length_unit = get_first(result, "length_unit", default="mm")

    pairs: list[tuple[str, Any]] = [
        ("Display units", get_first(result, "units")),
        ("Cables installed in the tray", get_first(result, "cable_type_label")),
        ("Cable tray type", get_first(result, "tray_type_label")),
        (f"Inside tray width ({length_unit})", get_first(result, "tray_width")),
        ("Total number of cables", get_first(result, "n_cables")),
    ]

    for i, g in enumerate(result.get("groups") or []):
        pairs.append(
            (
                f"Group {i + 1}",
                f"{g.get('count')}× {g.get('size_band_label')} at {g.get('diameter')} {length_unit} OD "
                f"({g.get('area')} {area_unit} each)",
            )
        )

    return pairs


def _build_notes(context: dict[str, Any]) -> list[str]:
    notes = [
        "Cable tray fill is evaluated per NEC 392.22 using the allowable fill areas of Tables 392.22(A)(1), 392.22(A)(5) and 392.22(A)(6) for multiconductor cables and Table 392.22(B)(1) for single-conductor cables, rated 2000 volts or less.",
        "Cable cross-sectional areas are computed from the overall cable diameters entered into the calculator; these come from manufacturer's data, not from an NEC table.",
    ]
    if context["has_reduced_area"]:
        notes.append(
            "Where cables of both size bands share the tray, the allowable fill area for the smaller cables is reduced by the summed diameter (Sd) of the larger cables, per the mixed-size column of the applicable table."
        )
    if context["single_layer"]:
        notes.append(
            "The governing rule requires a single layer of cables. This calculator checks the summed diameters and areas only; confirm the physical arrangement in the tray."
        )
    notes += [
        "Cable tray ampacity adjustment (392.80), tray support and the securing requirements of 392.18 and 392.30 are outside the scope of this calculation.",
        "Final selections and design decisions should be verified against the NEC, project specifications, equipment data, and engineering judgement.",
    ]
    return notes


def _build_source_table_from_result(result: dict[str, Any]) -> dict[str, Any] | None:
    cable_type = get_first(result, "cable_type")
    tray_type = get_first(result, "tray_type")
    tray_width = get_first(result, "tray_width")
    units = get_first(result, "units", default="metric")
    area_unit = get_first(result, "area_unit", default="mm²")
    length_unit = get_first(result, "length_unit", default="mm")
    if not cable_type or not tray_type or tray_width is None:
        return None

    table, plain, mixed = get_fill_source(cable_type, tray_type)
    if table is None:
        return None

    width_col = width_column(units)
    plain_col = area_column(plain, units)
    mixed_col = area_column(mixed, units)

    return build_nec_table_row_source(
        table_name=get_first(result, "fill_table_key", default="").upper(),
        criteria={width_col: tray_width},
        columns=[width_col, plain_col, mixed_col],
        column_labels={
            width_col: f"Inside Width ({length_unit})",
            plain_col: f"{plain.replace('_', ' ').title()} ({area_unit})",
            mixed_col: f"{mixed.replace('_', ' ').title()} ({area_unit})",
        },
        title="Selected NEC Table 392.22 Row — Allowable Cable Fill Area",
    )


def _build_report_context(result: dict[str, Any]) -> dict[str, Any]:
    context = {
        "has_reduced_area": get_first(result, "sd") is not None,
        "single_layer": bool(result.get("single_layer")),
    }
    context.update(
        {
            "notes": _build_notes(context),
            "input_pairs": _build_input_pairs(result),
            "result_pairs": _build_result_pairs(result),
            "source_table": _build_source_table_from_result(result),
        }
    )
    return context


# ============================================================
# Builders
# ============================================================
def build_word_report(result: dict[str, Any]) -> bytes:
    doc = init_word_doc(REPORT_TITLE)
    report_context = _build_report_context(result)

    add_cable_tray_fill_equations(doc, report_context)

    add_bullets(doc, report_context["notes"], heading="Notes and Assumptions")

    add_kv_section_to_word(doc, "Inputs and Parameters Used", report_context["input_pairs"])

    add_source_table_to_word(
        doc,
        report_context["source_table"],
        font_size_header=7,
        font_size=7,
    )

    add_kv_section_to_word(doc, "Results", report_context["result_pairs"])

    return save_word_doc(doc)


def build_excel_report(result: dict[str, Any]) -> bytes:
    wb, ws, row = init_excel_report(REPORT_TITLE, "Cable Tray Fill")
    report_context = _build_report_context(result)

    row = write_kv_sections_to_excel(
        ws,
        row,
        [
            ("Equations Used", _build_equations_for_excel(report_context)),
            ("Notes and Assumptions", notes_to_pairs(report_context["notes"])),
            ("Inputs and Parameters Used", report_context["input_pairs"]),
        ],
    )

    row = write_source_table_to_excel(ws, row, report_context["source_table"])

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
        and get_first(result, "limited_value") is not None
    )

    render_export_buttons(
        prefix="nec_cable_tray_fill",
        docx_file="nec_cable_tray_fill_report.docx",
        xlsx_file="nec_cable_tray_fill_report.xlsx",
        can_export=can_export,
        word_builder=lambda: build_word_report(result or {}),
        excel_builder=lambda: build_excel_report(result or {}),
    )
