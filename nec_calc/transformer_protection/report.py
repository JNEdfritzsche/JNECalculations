from __future__ import annotations

from typing import Any

from nec_calc.common.formatting import fmt
from nec_calc.common.report_helper import (
    add_word_equation,
    autosize_cols,
    build_standard_word_report,
    get_first,
    init_excel_report,
    omml_frac,
    omml_r,
    omml_sub,
    render_standard_export_report,
    wb_to_bytes,
    write_kv_sections_to_excel,
    yes_no,
)


REPORT_TITLE = "NEC Transformer Protection Calculation Report"
SHEET_NAME = "Transformer Protection"

PHASE_LABELS = {
    "dc": "DC",
    "single_phase": "Single-phase",
    "three_phase": "Three-phase",
}


# ============================================================
# Small helpers
# ============================================================
def _phase_label(phase: str | None) -> str:
    return PHASE_LABELS.get(str(phase or ""), str(phase or "—"))


def _enum_label(value: Any) -> str:
    return getattr(value, "label", None) or "—"


def _denominator_for_phase(phase: str | None, voltage_inner: str) -> str:
    return omml_r("√3 × ") + voltage_inner if phase == "three_phase" else voltage_inner


# ============================================================
# Equations
# ============================================================
def add_transformer_protection_equations(doc, context: dict[str, Any]) -> None:
    phase = context["phase"]
    doc.add_heading("Equations Used", level=1)

    if not context["nameplate_used"]:
        add_word_equation(
            doc,
            "Full-load current",
            omml_r("I = ") + omml_frac(omml_r("S"), _denominator_for_phase(phase, omml_r("V"))),
        )

    add_word_equation(
        doc,
        "Maximum OCPD rating",
        omml_sub("I", "OCPD,max") + omml_r(" = mult% × ") + omml_sub("I", "FLC"),
    )


# ============================================================
# Report sections
# ============================================================
def _ocpd_result_pairs(result: dict[str, Any]) -> list[tuple[str, Any]]:
    pairs: list[tuple[str, Any]] = []

    for side in ("primary", "secondary"):
        cb = result.get(f"{side}_cb")
        fr = result.get(f"{side}_fr")
        title = side.title()

        if cb.get("size") is None and fr.get("size") is None:
            pairs.append((f"{title} protection", "Not required"))
        elif cb == fr:
            pairs.append((f"Max {title} breaker/fuse ({cb.get('mult')}% × I_flc), A", cb.get("size")))
        else:
            pairs.append((f"Max {title} breaker ({cb.get('mult')}% × I_flc), A", cb.get("size")))
            pairs.append((f"Max {title} fuse ({fr.get('mult')}% × I_flc), A", fr.get("size")))

    return pairs


def _build_input_pairs(result: dict[str, Any]) -> list[tuple[str, Any]]:
    flas = result.get("flas", {})
    pairs: list[tuple[str, Any]] = []

    phase = get_first(result, "phase")
    if phase is not None:
        pairs.append(("System type", _phase_label(phase)))

    transformer_rating = get_first(result, "transformer_rating")
    if transformer_rating is not None:
        pairs.append(("Transformer rating, S (VA)", transformer_rating))

    pairs += [
        ("Primary transformer voltage, V1 (V)", get_first(result, "V_primary")),
        ("Secondary transformer voltage, V2 (V)", get_first(result, "V_secondary")),
        ("Voltage class", str(result.get("voltage_class")).title()),
        ("Nameplate FLA used", yes_no(result.get("nameplate_used"))),
        ("Primary full-load current, I1 (A)", flas.get("primary_fla")),
        ("Secondary full-load current, I2 (A)", flas.get("secondary_fla")),
    ]

    protection_method = result.get("protection_method")
    if protection_method is not None:
        pairs.append(("Protection configuration", _enum_label(protection_method)))

    location_type = result.get("location_type")
    if location_type is not None:
        pairs.append(("Location type", _enum_label(location_type)))

    tx_z = result.get("tx_z")
    if tx_z is not None:
        pairs.append(("Transformer rated impedance, %Z", tx_z))

    return pairs


def _build_notes(result: dict[str, Any]) -> list[str]:
    phase = get_first(result, "phase")
    notes = [
        "This report is based on the input values entered into the calculator.",
        "Maximum OCPD ratings are taken from NEC Table 450.5(A) for transformers over 1000 V and Table 450.5(B) for transformers 1000 V and less, based on protection configuration, location, and transformer rated impedance.",
        "OCPD values are the code-based maximums; the next standard rating at or below each value should be selected.",
        "Final selections and design decisions should be verified against the NEC, project specifications, equipment data, and engineering judgement.",
    ]
    if not result.get("nameplate_used"):
        notes.append(
            "Full-load currents are calculated from the transformer rating and voltages using S / (√3 × V)."
            if phase == "three_phase"
            else "Full-load currents are calculated from the transformer rating and voltages using S / V."
        )
    else:
        notes.append("Full-load currents are taken from the transformer nameplate values entered by the user.")
    return notes


def _excel_input_pairs(result: dict[str, Any]) -> list[tuple[str, Any]]:
    pairs: list[tuple[str, Any]] = []

    phase = get_first(result, "phase")
    if phase is not None:
        pairs.append(("System type", _phase_label(phase)))

    transformer_rating = get_first(result, "transformer_rating")
    if transformer_rating is not None:
        pairs.append(("Transformer rating, S (VA)", transformer_rating))

    pairs += [
        ("Primary transformer voltage, V1 (V)", get_first(result, "V_primary")),
        ("Secondary transformer voltage, V2 (V)", get_first(result, "V_secondary")),
        ("Nameplate FLA used", yes_no(result.get("nameplate_used"))),
    ]

    return pairs


def _excel_flc_pairs(result: dict[str, Any]) -> list[tuple[str, Any]]:
    flas = result.get("flas", {})
    return [
        ("Primary full-load current, I1 (A)", flas.get("primary_fla")),
        ("Secondary full-load current, I2 (A)", flas.get("secondary_fla")),
    ]


def _excel_protection_pairs(result: dict[str, Any]) -> list[tuple[str, Any]]:
    pairs: list[tuple[str, Any]] = [("Voltage class", str(result.get("voltage_class")).title())]

    protection_method = result.get("protection_method")
    if protection_method is not None:
        pairs.append(("Protection configuration", _enum_label(protection_method)))

    location_type = result.get("location_type")
    if location_type is not None:
        pairs.append(("Location type", _enum_label(location_type)))

    tx_z = result.get("tx_z")
    if tx_z is not None:
        pairs.append(("Transformer rated impedance, %Z", tx_z))

    return pairs + _ocpd_result_pairs(result)


def _build_report_context(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "phase": get_first(result, "phase"),
        "nameplate_used": bool(result.get("nameplate_used")),
        "notes": _build_notes(result),
        "input_pairs": _build_input_pairs(result),
        "result_pairs": _ocpd_result_pairs(result),
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
        word_equation_builder=add_transformer_protection_equations,
    )


def build_excel_report(result: dict[str, Any]) -> bytes:
    wb, ws, row = init_excel_report(REPORT_TITLE, SHEET_NAME)

    write_kv_sections_to_excel(
        ws,
        row,
        [
            ("Inputs", _excel_input_pairs(result)),
            ("Full-Load Currents", _excel_flc_pairs(result)),
            ("Code-Based Protection", _excel_protection_pairs(result)),
        ],
    )

    autosize_cols(ws)
    return wb_to_bytes(wb)


def render_export_report(result: dict[str, Any] | None) -> None:
    render_standard_export_report(
        prefix="nec_transformer_protection",
        docx_file="nec_transformer_protection_report.docx",
        xlsx_file="nec_transformer_protection_report.xlsx",
        result=result,
        required_keys=("primary_cb", "secondary_cb"),
        word_builder=build_word_report,
        excel_builder=build_excel_report,
    )