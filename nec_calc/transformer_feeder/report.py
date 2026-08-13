from __future__ import annotations

from typing import Any

from calc_common.formatting import fmt
from calc_common.report_helper import (
    add_word_equation,
    get_first,
    omml_frac,
    omml_r,
    omml_sub,
)
from calc_common.report_schedule import (
    Column,
    Group,
    ReportSpec,
    render_schedule_commit,
    render_schedule_table,
)
from lib.nec_tables import TABLE_450_5A


PHASE_LABELS = {
    "single_phase": "Single-phase",
    "three_phase": "Three-phase",
}

PHASE_ORDER = ("single_phase", "three_phase")


# ============================================================
# Column value helpers
# ============================================================
def _phase(result: dict[str, Any]) -> str | None:
    return get_first(result, "phase", "system_type")


def _phase_label(result: dict[str, Any]) -> str:
    phase = _phase(result)
    return PHASE_LABELS.get(str(phase or ""), str(phase or "—"))


def _configuration(result: dict[str, Any]) -> str:
    label = get_first(result, "transformer_type")
    if not label:
        return "—"

    text = str(label)
    for phase_label in PHASE_LABELS.values():
        if text.startswith(phase_label):
            return text[len(phase_label):].strip() or text
    return text


def _rating_kva(result: dict[str, Any]) -> str:
    rating = get_first(result, "transformer_rating", "S", "rating_va")
    return "—" if rating is None else fmt(float(rating) / 1000.0, "kVA")


# ============================================================
# Code reference — edition comes from the table's own CSV front matter
# ============================================================
def _nec_edition() -> str:
    edition = TABLE_450_5A.get("edition")
    return f"NEC {edition}" if edition else "NEC"


def _edition(result: dict[str, Any]) -> str:
    return _nec_edition()


def _reference(result: dict[str, Any]) -> str:
    return "Art. 450"


# ============================================================
# Report-wide text
# ============================================================
def _code_reference(results: list[dict[str, Any]]) -> str:
    return (
        f"Per {_nec_edition()} Article 450 — full-load currents calculated from the "
        "transformer rating and voltages"
    )


def _phases_present(results: list[dict[str, Any]]) -> list[str]:
    phases = {_phase(r) for r in results}
    return [p for p in PHASE_ORDER if p in phases]


def _denominator_for_phase(phase: str | None, voltage_inner: str) -> str:
    return omml_r("√3 × ") + voltage_inner if phase == "three_phase" else voltage_inner


def _word_reference(doc, results: list[dict[str, Any]]) -> None:
    """Equations used across the calculations in the schedule (Word report only)."""
    phases = _phases_present(results)
    doc.add_heading("Equations Used", level=1)

    for phase in phases:
        suffix = f" — {PHASE_LABELS[phase]}" if len(phases) > 1 else ""

        add_word_equation(
            doc,
            f"Primary full-load current{suffix}",
            omml_sub("I", "1")
            + omml_r(" = ")
            + omml_frac(omml_r("S"), _denominator_for_phase(phase, omml_sub("V", "1"))),
        )
        add_word_equation(
            doc,
            f"Secondary full-load current{suffix}",
            omml_sub("I", "2")
            + omml_r(" = ")
            + omml_frac(omml_r("S"), _denominator_for_phase(phase, omml_sub("V", "2"))),
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


def _footnotes(results: list[dict[str, Any]]) -> list[str]:
    edition = _nec_edition()
    phases = _phases_present(results)

    notes = [
        "Full-load currents are calculated from the transformer rating and voltages; "
        "they are not read from an NEC table. The Code Edition and Code Reference columns "
        f"cite {edition} Article 450, which governs the transformer installation these "
        "currents are calculated for.",
    ]

    if "three_phase" in phases:
        notes.append(
            "For the three-phase calculation, transformer voltages are treated as "
            "line-to-line voltages and current is calculated using S / (√3 × V)."
        )
    if "single_phase" in phases:
        notes.append("For the single-phase calculation, current is calculated using S / V.")

    notes += [
        "The turns ratio shown is an ideal transformer ratio and does not account for "
        "losses, impedance, voltage regulation, tap position, or loading effects.",
        "The calculated currents are transformer full-load currents only. Final feeder "
        "conductor sizing, overcurrent protection, voltage drop, temperature correction, "
        "and project-specific requirements should be checked separately.",
        "This report is based on the input values entered into the calculator. Final "
        "selections and design decisions should be verified against the NEC, project "
        "specifications, equipment data, and engineering judgement.",
    ]

    return notes


# ============================================================
# Schedule spec + entry point
# ============================================================
TF_SCHEDULE_SPEC = ReportSpec(
    code="nec",
    calculator="transformer_feeder",
    report_title="Transformer Feeder — Calculation Results",
    sheet_name="Transformer Feeder Schedule",
    tag="Tag / ID",
    cols=[
        Column("System", _phase_label, group="system"),
        Column("Configuration", _configuration, group="system"),
        Column("Rating, S", _rating_kva),
        Column("V1 (V)", lambda r: fmt(get_first(r, "V_primary", "v_primary", "primary_voltage"), "V"), group="volts"),
        Column("V2 (V)", lambda r: fmt(get_first(r, "V_secondary", "v_secondary", "secondary_voltage"), "V"), group="volts"),
        Column("I1 (A)", lambda r: fmt(get_first(r, "primary_fla", "primary_flc"), "A"), color="green", result=True),
        Column("I2 (A)", lambda r: fmt(get_first(r, "secondary_fla", "secondary_flc"), "A"), color="green", result=True),
        Column("Turns ratio (V1/V2)", lambda r: fmt(get_first(r, "turns_ratio")), color="blue", result=True),
        Column("Code Edition", _edition),
        Column("Code Reference", _reference),
    ],
    groups={
        "system": Group("System"),
        "volts": Group("V1 / V2 (V)"),
    },
    code_reference=_code_reference,
    notes=_footnotes,
    word_reference=_word_reference,
)


def render_add_to_schedule(result: dict[str, Any] | None) -> None:
    can_add = result is not None and get_first(result, "primary_fla", "primary_flc") is not None
    render_schedule_commit(TF_SCHEDULE_SPEC, result, can_add=can_add)


def render_schedule_section() -> None:
    render_schedule_table(TF_SCHEDULE_SPEC)
