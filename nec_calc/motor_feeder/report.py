from __future__ import annotations

from typing import Any

from nec_calc.common.report_helper import (
    add_word_equation,
    build_standard_excel_report,
    build_standard_word_report,
    get_first,
    omml_r,
    omml_sub,
    render_standard_export_report,
)


REPORT_TITLE = "NEC Motor Feeder Calculation Report"
SHEET_NAME = "Motor Feeder"


# ============================================================
# Equations
# ============================================================
def add_motor_feeder_equations(doc, context: dict[str, Any]) -> None:
    doc.add_heading("Equations Used", level=1)

    add_word_equation(
        doc,
        "Feeder conductor ampacity",
        omml_sub("I", "cond") + omml_r(" = k × ") + omml_sub("I", "FLC"),
    )
    if context["has_overload"]:
        add_word_equation(
            doc,
            "Maximum overload protection",
            omml_sub("I", "OL") + omml_r(" = SF × ") + omml_sub("I", "FLA,nameplate"),
        )


def _build_equations_for_excel(context: dict[str, Any]) -> list[tuple[str, str]]:
    equations = [("Feeder conductor ampacity", "I_cond = k × I_FLC")]
    if context["has_overload"]:
        equations.append(("Maximum overload protection", "I_OL = SF × I_FLA,nameplate"))
    return equations


# ============================================================
# Report sections
# ============================================================
def _build_result_pairs(result: dict[str, Any]) -> list[tuple[str, Any]]:
    pairs: list[tuple[str, Any]] = [
        ("Feeder conductor ampacity, I_cond (A)", get_first(result, "conductor_ampacity")),
    ]
    if get_first(result, "conductor_size") is not None:
        pairs.append(("Minimum conductor size (Table 310.16)", get_first(result, "conductor_size")))
    pairs.append(("Maximum overload protection, I_OL (A)", get_first(result, "max_overload")))
    return pairs


def _build_input_pairs(result: dict[str, Any]) -> list[tuple[str, Any]]:
    pairs = [
        ("System", get_first(result, "phase_label")),
        ("Motor size (HP)", get_first(result, "hp_label")),
    ]
    if result.get("motor_type"):
        pairs.append(("Motor type", get_first(result, "motor_type")))
    pairs += [
        ("Voltage (V)", get_first(result, "voltage")),
        ("Full-load current, I_FLC (A)", get_first(result, "flc")),
        ("Full-load current source", get_first(result, "flc_source")),
        ("Conductor sizing factor, k", get_first(result, "sizing_factor_label")),
    ]
    if result.get("material_label"):
        pairs.append(("Conductor material", get_first(result, "material_label")))
    if result.get("temp_rating") is not None:
        pairs.append(("Insulation temp rating (°C)", get_first(result, "temp_rating")))
    if result.get("nameplate_fla") is not None:
        pairs.append(("Nameplate FLA (A)", get_first(result, "nameplate_fla")))
    if result.get("service_factor_label"):
        pairs.append(("Service factor, SF", get_first(result, "service_factor_label")))
    return pairs


def _build_notes(context: dict[str, Any]) -> list[str]:
    notes = [
        "This report is based on the input values entered into the calculator.",
        "Per NEC 430.6(A), branch-circuit and feeder conductor sizing uses the full-load current from Tables 430.247 through 430.250, not the motor nameplate current.",
        "The feeder conductor ampacity shown is the minimum for a single motor per NEC 430.22. Apply temperature correction, ambient and conduit-fill adjustment, voltage drop, and NEC 430.24 for multiple-motor feeders as applicable.",
    ]
    if context["has_overload"]:
        notes.append(
            "The maximum overload protection is sized per NEC 430.32 using the marked nameplate full-load current and service factor. Verify against the selected device rating and the specific conditions of 430.32."
        )
    notes.append(
        "Final selections and design decisions should be verified against the NEC, project specifications, equipment data, and engineering judgement."
    )
    return notes


def _build_report_context(result: dict[str, Any]) -> dict[str, Any]:
    context = {
        "has_overload": get_first(result, "max_overload") is not None,
    }
    context.update(
        {
            "notes": _build_notes(context),
            "input_pairs": _build_input_pairs(result),
            "result_pairs": _build_result_pairs(result),
            "source_table": None,
        }
    )
    return context


# ============================================================
# Builders
# ============================================================
def build_word_report(result: dict[str, Any]) -> bytes:
    return build_standard_word_report(
        report_title=REPORT_TITLE,
        result=result,
        context_builder=_build_report_context,
        word_equation_builder=add_motor_feeder_equations,
    )


def build_excel_report(result: dict[str, Any]) -> bytes:
    return build_standard_excel_report(
        report_title=REPORT_TITLE,
        sheet_name=SHEET_NAME,
        result=result,
        context_builder=_build_report_context,
        excel_equation_builder=_build_equations_for_excel,
    )


def render_export_report(result: dict[str, Any] | None) -> None:
    render_standard_export_report(
        prefix="nec_motor_feeder",
        docx_file="nec_motor_feeder_report.docx",
        xlsx_file="nec_motor_feeder_report.xlsx",
        result=result,
        required_keys=("conductor_ampacity",),
        word_builder=build_word_report,
        excel_builder=build_excel_report,
    )
