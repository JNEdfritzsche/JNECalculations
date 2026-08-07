from __future__ import annotations

from html import escape
from typing import Any

from nec_calc.common.report_helper import (
    add_bullets,
    add_kv_section_to_word,
    add_omml_equation_to_paragraph,
    add_source_table_to_word,
    autosize_cols,
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

REPORT_TITLE = "NEC Template Calculation Report"

METHOD_LABELS = {
    "example_method": "Example Method",
}


# ============================================================
# Small helpers
# ============================================================
def _method_label(template_mode: str) -> str:
    return METHOD_LABELS.get(template_mode, str(template_mode))


def _add_word_equation(doc, label: str, omml_inner: str) -> None:
    p = doc.add_paragraph()
    p.add_run(f"{label}: ").bold = True
    add_omml_equation_to_paragraph(p, omml_inner)


def add_template_equations(doc, template_mode: str) -> None:
    doc.add_heading("Equations Used", level=1)

    eq1 = (
        omml_sub("X", "intermediate")
        + omml_r(" = A × M")
    )

    eq2 = (
        omml_sub("X", "final")
        + omml_r(" = ")
        + omml_sub("X", "intermediate")
        + omml_r(" + B")
    )

    _add_word_equation(doc, "Intermediate value", eq1)
    _add_word_equation(doc, "Final value", eq2)


def _build_equations_for_excel(template_mode: str) -> list[tuple[str, str]]:
    return [
        ("Intermediate value", "X_intermediate = A × M"),
        ("Final value", "X_final = X_intermediate + B"),
    ]


# ============================================================
# Report sections
# ============================================================
def _build_result_pairs(result: dict[str, Any]) -> list[tuple[str, Any]]:
    return [
        ("Calculated value", get_first(result, "calculated_value")),
        ("Intermediate value", get_first(result, "intermediate_value")),
    ]


def _build_input_pairs(
    result: dict[str, Any],
    template_mode: str,
) -> list[tuple[str, Any]]:
    return [
        ("Calculation method", _method_label(template_mode)),
        ("Base quantity, A", get_first(result, "base_quantity")),
        ("Multiplier, M", get_first(result, "multiplier")),
        ("Adder, B", get_first(result, "adder")),
    ]


def _build_notes(template_mode: str) -> list[str]:
    return [
        "This report is based on the input values entered into the calculator.",
        "Final selections and design decisions should be verified against the NEC, project specifications, equipment data, and engineering judgement.",
        "Replace this template note with assumptions specific to the calculator being created.",
    ]


def _build_source_table_from_result(
    result: dict[str, Any],
    template_mode: str,
):
    return None

    # Example source-row pattern:
    # return build_nec_table_row_source(
    #     table_name="TABLE_XXX",
    #     criteria={"column_key": get_first(result, "input_key")},
    #     columns=["column_key", "value_key"],
    #     column_labels={
    #         "column_key": "Column Label",
    #         "value_key": "Value Label",
    #     },
    #     title="Selected NEC Table XXX Row",
    # )


def _build_report_context(
    result: dict[str, Any],
    template_mode: str,
) -> dict[str, Any]:
    return {
        "notes": _build_notes(template_mode),
        "input_pairs": _build_input_pairs(
            result=result,
            template_mode=template_mode,
        ),
        "result_pairs": _build_result_pairs(result),
        "source_table": _build_source_table_from_result(
            result=result,
            template_mode=template_mode,
        ),
    }


# ============================================================
# Builders
# ============================================================
def build_word_report(
    result: dict[str, Any],
    template_mode: str,
) -> bytes:
    doc = init_word_doc(REPORT_TITLE)
    report_context = _build_report_context(
        result=result,
        template_mode=template_mode,
    )

    add_template_equations(doc, template_mode)

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


def build_excel_report(
    result: dict[str, Any],
    template_mode: str,
) -> bytes:
    wb, ws, row = init_excel_report(REPORT_TITLE, "Template")
    report_context = _build_report_context(
        result=result,
        template_mode=template_mode,
    )

    row = write_kv_sections_to_excel(
        ws,
        row,
        [
            ("Equations Used", _build_equations_for_excel(template_mode)),
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


def render_export_report(
    result: dict[str, Any] | None,
    template_mode: str,
) -> None:
    can_export = (
        result is not None
        and get_first(result, "calculated_value") is not None
    )

    render_export_buttons(
        prefix="nec_template",
        docx_file="nec_template_report.docx",
        xlsx_file="nec_template_report.xlsx",
        can_export=can_export,
        word_builder=lambda: build_word_report(
            result=result or {},
            template_mode=template_mode,
        ),
        excel_builder=lambda: build_excel_report(
            result=result or {},
            template_mode=template_mode,
        ),
    )
