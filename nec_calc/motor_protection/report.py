from __future__ import annotations

from typing import Any

from nec_calc.common.formatting import fmt
from nec_calc.common.report_helper import (
    add_word_equation,
    build_standard_excel_report,
    build_standard_word_report,
    get_first,
    omml_r,
    omml_sub,
    render_standard_export_report,
)


REPORT_TITLE = "NEC Motor Protection Calculation Report"
SHEET_NAME = "Motor Protection"


# ============================================================
# Equations
# ============================================================
def add_equations(doc, context: dict[str, Any]) -> None:
    doc.add_heading("Equations Used", level=1)
    add_word_equation(
        doc,
        "Branch-circuit device (430.52)",
        omml_sub("I", "branch") + omml_r(" = mult% × ") + omml_sub("I", "FLC"),
    )
    if context["has_overload"]:
        add_word_equation(
            doc,
            "Overload protection (430.32)",
            omml_sub("I", "OL") + omml_r(" = k × ") + omml_sub("I", "FLA,nameplate"),
        )


def _build_equations_for_excel(context: dict[str, Any]) -> list[tuple[str, str]]:
    equations = [("Branch-circuit device (430.52)", "I_branch = mult% × I_FLC")]
    if context["has_overload"]:
        equations.append(("Overload protection (430.32)", "I_OL = k × I_FLA,nameplate"))
    return equations


# ============================================================
# Report sections
# ============================================================
def _build_result_pairs(result: dict[str, Any]) -> list[tuple[str, Any]]:
    pairs: list[tuple[str, Any]] = [
        ("Full-load current, I_FLC (A)", fmt(get_first(result, "flc"))),
    ]
    branch = result.get("branch") or {}
    for d in branch.get("devices", []):
        std = d.get("standard")
        value = fmt(std) if std is not None else fmt(d.get("raw"))
        pairs.append((f"Branch device — {d['label']} ({d['pct']}%)", value))

    overload = result.get("overload") or {}
    if overload.get("max_overload") is not None:
        pairs.append((f"Max overload ({int(overload['factor'] * 100)}%) (A)", fmt(overload["max_overload"])))

    disconnect = result.get("disconnect") or {}
    if disconnect.get("min_disconnect_ampere") is not None:
        pairs.append(("Min. disconnect rating (115% FLC) (A)", fmt(disconnect["min_disconnect_ampere"])))

    lrc_t = result.get("lrc_table") or {}
    if lrc_t.get("locked_rotor_current") is not None:
        pairs.append(("Locked-rotor current, Table 430.251 (A)", fmt(lrc_t["locked_rotor_current"])))
    return pairs


def _build_input_pairs(result: dict[str, Any]) -> list[tuple[str, Any]]:
    pairs = [
        ("System", get_first(result, "phase_label")),
        ("Motor size (HP)", get_first(result, "hp_label")),
    ]
    if result.get("motor_type"):
        pairs.append(("Motor type", get_first(result, "motor_type")))
    branch = result.get("branch") or {}
    if branch.get("category_label"):
        pairs.append(("Motor category (430.52)", branch["category_label"]))
    pairs += [
        ("Voltage (V)", get_first(result, "voltage")),
        ("Full-load current source", get_first(result, "flc_source")),
    ]
    if result.get("nameplate_fla") is not None:
        pairs.append(("Nameplate FLA (A)", get_first(result, "nameplate_fla")))
    if result.get("service_factor_label"):
        pairs.append(("Service factor", get_first(result, "service_factor_label")))
    if result.get("code_letter"):
        pairs.append(("Locked-rotor code letter", get_first(result, "code_letter")))
    return pairs


def _build_notes(context: dict[str, Any]) -> list[str]:
    notes = [
        "This report is based on the input values entered into the calculator.",
        "Per NEC 430.6(A), branch-circuit and feeder sizing uses the full-load current from Tables 430.247 through 430.250, not the motor nameplate current.",
        "Branch-circuit short-circuit and ground-fault device ratings are the maximums from Table 430.52(C)(1). Exception 1 permits the next higher standard rating (240.6(A)); Exception 2 is the ceiling permitted where the motor will not start.",
    ]
    if context["has_overload"]:
        notes.append(
            "Overload protection is sized per NEC 430.32 from the marked nameplate full-load current and service factor / temperature rise."
        )
    notes.append(
        "Final selections should be verified against the NEC, project specifications, equipment data, a coordination study where required, and engineering judgement."
    )
    return notes


def _build_report_context(result: dict[str, Any]) -> dict[str, Any]:
    overload = result.get("overload") or {}
    context = {"has_overload": overload.get("max_overload") is not None}
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
        word_equation_builder=add_equations,
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
        prefix="nec_motor_protection",
        docx_file="nec_motor_protection_report.docx",
        xlsx_file="nec_motor_protection_report.xlsx",
        result=result,
        required_keys=("flc",),
        word_builder=build_word_report,
        excel_builder=build_excel_report,
    )
