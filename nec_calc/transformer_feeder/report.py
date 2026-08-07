from __future__ import annotations

from typing import Any

from nec_calc.common.report_helper import (
    add_word_equation,
    build_standard_excel_report,
    build_standard_word_report,
    get_first,
    omml_frac,
    omml_r,
    omml_sub,
    render_standard_export_report,
)


REPORT_TITLE = "NEC Transformer Feeder Calculation Report"
SHEET_NAME = "Transformer Feeder"

PHASE_LABELS = {
    "single_phase": "Single-phase",
    "three_phase": "Three-phase",
}


# ============================================================
# Small helpers
# ============================================================
def _phase_label(phase: str | None) -> str:
    return PHASE_LABELS.get(str(phase or ""), str(phase or "—"))


def _phase_factor_text(phase: str | None) -> str:
    return "√3" if phase == "three_phase" else "1"


def _denominator_for_phase(phase: str | None, voltage_inner: str) -> str:
    return omml_r("√3 × ") + voltage_inner if phase == "three_phase" else voltage_inner


# ============================================================
# Equations
# ============================================================
def add_transformer_feeder_equations(doc, context: dict[str, Any]) -> None:
    phase = context["phase"]
    doc.add_heading("Equations Used", level=1)

    add_word_equation(
        doc,
        "Primary full-load current",
        omml_sub("I", "1") + omml_r(" = ") + omml_frac(omml_r("S"), _denominator_for_phase(phase, omml_sub("V", "1"))),
    )
    add_word_equation(
        doc,
        "Secondary full-load current",
        omml_sub("I", "2") + omml_r(" = ") + omml_frac(omml_r("S"), _denominator_for_phase(phase, omml_sub("V", "2"))),
    )
    add_word_equation(
        doc,
        "Turns ratio",
        omml_r("Turns Ratio = ")
        + omml_frac(omml_sub("V", "1"), omml_sub("V", "2"))
        + omml_r(" = ")
        + omml_frac(omml_sub("N", "1"), omml_sub("N", "2"))
        + omml_r(" = ")
        + omml_frac(omml_sub("I", "2"), omml_sub("I", "1")),
    )


def _build_equations_for_excel(context: dict[str, Any]) -> list[tuple[str, str]]:
    phase = context["phase"]
    return [
        (
            "Primary full-load current",
            "I1 = S / (√3 × V1)" if phase == "three_phase" else "I1 = S / V1",
        ),
        (
            "Secondary full-load current",
            "I2 = S / (√3 × V2)" if phase == "three_phase" else "I2 = S / V2",
        ),
        ("Turns ratio", "Turns Ratio = V1 / V2 = N1 / N2 = I2 / I1"),
    ]


# ============================================================
# Report sections
# ============================================================
def _build_result_pairs(result: dict[str, Any]) -> list[tuple[str, Any]]:
    return [
        ("Primary full-load current, I1 (A)", get_first(result, "primary_fla", "primary_flc")),
        ("Secondary full-load current, I2 (A)", get_first(result, "secondary_fla", "secondary_flc")),
        ("Turns ratio, V1/V2", get_first(result, "turns_ratio")),
        ("Transformer type", get_first(result, "transformer_type")),
    ]


def _build_input_pairs(result: dict[str, Any]) -> list[tuple[str, Any]]:
    phase = get_first(result, "phase", "system_type")
    return [
        ("System type", _phase_label(phase)),
        ("Transformer rating, S (VA)", get_first(result, "transformer_rating", "S", "rating_va")),
        ("Primary transformer voltage, V1 (V)", get_first(result, "V_primary", "v_primary", "primary_voltage")),
        ("Secondary transformer voltage, V2 (V)", get_first(result, "V_secondary", "v_secondary", "secondary_voltage")),
        ("Phase factor used", _phase_factor_text(phase)),
    ]


def _build_notes(phase: str | None) -> list[str]:
    notes = [
        "This report is based on the input values entered into the calculator.",
        "The calculated currents are transformer full-load currents only. Final feeder conductor sizing, overcurrent protection, voltage drop, temperature correction, and project-specific requirements should be checked separately.",
        "Final selections and design decisions should be verified against the NEC, project specifications, equipment data, and engineering judgement.",
    ]
    notes.append(
        "For the three-phase calculation, transformer voltages are treated as line-to-line voltages and current is calculated using S / (√3 × V)."
        if phase == "three_phase"
        else "For the single-phase calculation, current is calculated using S / V."
    )
    notes.append("The turns ratio shown is an ideal transformer ratio and does not account for losses, impedance, voltage regulation, tap position, or loading effects.")
    return notes


def _build_report_context(result: dict[str, Any]) -> dict[str, Any]:
    phase = get_first(result, "phase", "system_type")
    return {
        "phase": phase,
        "notes": _build_notes(phase),
        "input_pairs": _build_input_pairs(result),
        "result_pairs": _build_result_pairs(result),
        "source_table": None,
    }


# ============================================================
# Builders
# ============================================================
def build_word_report(result: dict[str, Any]) -> bytes:
    return build_standard_word_report(
        report_title=REPORT_TITLE,
        result=result,
        context_builder=_build_report_context,
        word_equation_builder=add_transformer_feeder_equations,
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
        prefix="nec_transformer_feeder",
        docx_file="nec_transformer_feeder_report.docx",
        xlsx_file="nec_transformer_feeder_report.xlsx",
        result=result,
        required_keys=("primary_fla", "secondary_fla", "turns_ratio"),
        word_builder=build_word_report,
        excel_builder=build_excel_report,
    )
