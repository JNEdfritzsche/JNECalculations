from __future__ import annotations

from typing import Any

from nec_calc.common.formatting import fmt
from nec_calc.common.report_helper import (
    add_word_equation,
    get_first,
    omml_frac,
    omml_r,
    omml_sub,
)
from nec_calc.common.report_schedule import (
    Column,
    ReportSpec,
    render_schedule_commit,
    render_schedule_table,
)
from lib.nec_tables import TABLE_450_5A, TABLE_450_5B


PHASE_LABELS = {
    "dc": "DC",
    "single_phase": "Single-phase",
    "three_phase": "Three-phase",
}

PHASE_ORDER = ("single_phase", "three_phase")

VOLTAGE_CLASS_LABELS = {
    "low": "≤ 1000 V",
    "high": "> 1000 V",
}

SOURCE_TABLE_LABELS = {
    "table_450_5_a": "Table 450.5(A)",
    "table_450_5_b": "Table 450.5(B)",
}

TABLE_SOURCES = {
    "table_450_5_a": TABLE_450_5A,
    "table_450_5_b": TABLE_450_5B,
}


# ============================================================
# Column value helpers
# ============================================================
def _phase(result: dict[str, Any]) -> str | None:
    return get_first(result, "phase", "system_type")


def _phase_label(result: dict[str, Any]) -> str:
    if result.get("nameplate_used"):
        return "—"
    phase = _phase(result)
    return PHASE_LABELS.get(str(phase or ""), str(phase or "—"))


def _enum_label(value: Any) -> str:
    return getattr(value, "label", None) or "—"


def _flc_source(result: dict[str, Any]) -> str:
    return "Nameplate" if result.get("nameplate_used") else "Calculated"


def _rating_kva(result: dict[str, Any]) -> str:
    rating = get_first(result, "transformer_rating")
    return "—" if rating is None else fmt(float(rating) / 1000.0, "kVA")


def _fla(result: dict[str, Any], key: str) -> str:
    return fmt((result.get("flas") or {}).get(key), "A")


def _voltage_class(result: dict[str, Any]) -> str:
    voltage_class = get_first(result, "voltage_class")
    return VOLTAGE_CLASS_LABELS.get(str(voltage_class or ""), "—")


def _ocpd(result: dict[str, Any], side: str) -> str:
    cb = result.get(f"{side}_cb") or {}
    fr = result.get(f"{side}_fr") or {}

    if cb.get("size") is None and fr.get("size") is None:
        return "Not required"
    if cb == fr:
        return f"{fmt(cb.get('size'), 'A')} ({cb.get('mult')}%)"
    return (
        f"CB {fmt(cb.get('size'), 'A')} ({cb.get('mult')}%) / "
        f"Fuse {fmt(fr.get('size'), 'A')} ({fr.get('mult')}%)"
    )


# ============================================================
# Code reference — edition comes from the table's own CSV front matter
# ============================================================
def _nec_edition(table: dict[str, Any] | None = None) -> str:
    edition = (table or TABLE_450_5B).get("edition") or TABLE_450_5A.get("edition")
    return f"NEC {edition}" if edition else "NEC"


def _edition(result: dict[str, Any]) -> str:
    table = TABLE_SOURCES.get(get_first(result, "table_used"))
    return "—" if table is None else _nec_edition(table)


def _source_table(result: dict[str, Any]) -> str:
    return SOURCE_TABLE_LABELS.get(str(get_first(result, "table_used") or ""), "—")


# ============================================================
# Report-wide text
# ============================================================
def _code_reference(results: list[dict[str, Any]]) -> str:
    tables = {get_first(r, "table_used") for r in results}
    parts = [SOURCE_TABLE_LABELS[key] for key in SOURCE_TABLE_LABELS if key in tables]
    return f"Per {_nec_edition()} 450.3 " + ("; ".join(parts) if parts else "Table 450.5")


def _phases_present(results: list[dict[str, Any]]) -> list[str]:
    phases = {_phase(r) for r in results if not r.get("nameplate_used")}
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
            f"Full-load current{suffix}",
            omml_r("I = ") + omml_frac(omml_r("S"), _denominator_for_phase(phase, omml_r("V"))),
        )

    add_word_equation(
        doc,
        "Maximum OCPD rating",
        omml_sub("I", "OCPD,max") + omml_r(" = mult% × ") + omml_sub("I", "FLC"),
    )


def _footnotes(results: list[dict[str, Any]]) -> list[str]:
    edition = _nec_edition()

    notes = [
        f"Maximum OCPD ratings are taken from {edition} Table 450.5(A) for transformers "
        "over 1000 V and Table 450.5(B) for transformers 1000 V and less, based on "
        "protection configuration, location, and transformer rated impedance.",
        "The Code Edition and Source Table columns give the table each row's multipliers "
        "were read from. Where the breaker and fuse multipliers differ, both maximums are "
        "shown; where the table gives one multiplier for both devices, a single figure is shown.",
        "OCPD values are the code-based maximums; the next standard rating at or below each "
        "value should be selected.",
    ]

    if _phases_present(results):
        notes.append(
            "Full-load currents are calculated from the transformer rating and voltages; "
            "three-phase voltages are treated as line-to-line."
        )
    if any(r.get("nameplate_used") for r in results):
        notes.append(
            "Rows marked Nameplate use the full-load currents entered from the transformer "
            "nameplate rather than calculated values."
        )

    notes.append(
        "This report is based on the input values entered into the calculator. Final "
        "selections and design decisions should be verified against the NEC, project "
        "specifications, equipment data, and engineering judgement."
    )

    return notes


# ============================================================
# Schedule spec + entry point
# ============================================================
TP_SCHEDULE_SPEC = ReportSpec(
    prefix="nec_transformer_protection_schedule",
    report_title="Transformer Protection — Calculation Results",
    sheet_name="Transformer Protection Schedule",
    tag="Tag / ID",
    cols=[
        Column("System", _phase_label),
        Column("Rating, S", _rating_kva),
        Column("V1 (V)", lambda r: fmt(get_first(r, "V_primary"), "V")),
        Column("V2 (V)", lambda r: fmt(get_first(r, "V_secondary"), "V")),
        Column("Voltage class", _voltage_class),
        Column("FLA source", _flc_source),
        Column("I1 (A)", lambda r: _fla(r, "primary_fla")),
        Column("I2 (A)", lambda r: _fla(r, "secondary_fla")),
        Column("Protection", lambda r: _enum_label(r.get("protection_method"))),
        Column("Location", lambda r: _enum_label(r.get("location_type"))),
        Column("%Z", lambda r: fmt(get_first(r, "tx_z"), "%")),
        Column("Max primary OCPD", lambda r: _ocpd(r, "primary"), color="green"),
        Column("Max secondary OCPD", lambda r: _ocpd(r, "secondary"), color="green"),
        Column("Code Edition", _edition),
        Column("Source Table", _source_table),
    ],
    code_reference=_code_reference,
    notes=_footnotes,
    word_reference=_word_reference,
)


def render_add_to_schedule(result: dict[str, Any] | None) -> None:
    can_add = result is not None and get_first(result, "table_used") is not None
    render_schedule_commit(TP_SCHEDULE_SPEC, result, can_add=can_add)


def render_schedule_section() -> None:
    render_schedule_table(TP_SCHEDULE_SPEC)
