from __future__ import annotations

from typing import Any

from calc_common.formatting import fmt
from calc_common.report_helper import (
    add_word_equation,
    get_first,
    omml_frac,
    omml_r,
    omml_sub,
    yes_no,
)
from calc_common.report_schedule import (
    Column,
    ReportSpec,
    render_schedule_commit,
    render_schedule_table,
)
from oesc_calc.common.code_meta import cite, oesc_edition
from oesc_calc.transformer_protection.calculation import (
    DRY,
    OVER_750,
    THREE_PHASE,
    UPTO_750,
)


# ============================================================
# Column value helpers
# ============================================================
def _devices(result: dict[str, Any], keyword: str) -> str:
    entries = [d for d in (result.get("devices") or []) if keyword in d.get("label", "").lower()]
    if not entries:
        return "—"

    parts = []
    for entry in entries:
        value = entry.get("selected") if entry.get("selected") is not None else entry.get("raw")
        label = entry.get("label", "")
        pct = label[label.find("(") + 1:label.find(")")] if "(" in label else ""
        parts.append(f"{fmt(value, 'A')} ({pct})" if pct else fmt(value, "A"))
    return " / ".join(parts)


def _rating_kva(result: dict[str, Any]) -> str:
    kva = get_first(result, "kva")
    return "—" if kva is None else fmt(kva, "kVA")


def _impedance(result: dict[str, Any]) -> str:
    z_pct = get_first(result, "z_pct")
    return "—" if z_pct is None else f"{z_pct:g} %"


def _edition(result: dict[str, Any]) -> str:
    return oesc_edition(get_first(result, "primary_table"))


def _source_tables(result: dict[str, Any]) -> str:
    return cite(get_first(result, "source_tables", default=[]))


# ============================================================
# Report-wide text
# ============================================================
def _code_reference(results: list[dict[str, Any]]) -> str:
    rules = []
    for result in results:
        if get_first(result, "voltage_class") == OVER_750:
            rules.append("26-250")
        elif get_first(result, "xfmr_type") == DRY:
            rules.append("26-254")
        else:
            rules.append("26-252")
    ordered = [r for r in ("26-250", "26-252", "26-254") if r in rules]
    return f"Per {oesc_edition()} Rule " + ("; ".join(ordered) if ordered else "26-250")


def _word_reference(doc, results: list[dict[str, Any]]) -> None:
    """Equations used across the calculations in the schedule (Word report only)."""
    doc.add_heading("Equations Used", level=1)

    if any(not r.get("use_nameplate") for r in results):
        phases = {get_first(r, "phase") for r in results}
        for phase in [p for p in (THREE_PHASE, "1Φ") if p in phases]:
            denominator = omml_r("√3 × V") if phase == THREE_PHASE else omml_r("V")
            suffix = f" — {phase}" if len(phases) > 1 else ""
            add_word_equation(
                doc,
                f"Full-load current{suffix}",
                omml_r("I = ") + omml_frac(omml_r("kVA × 1000"), denominator),
            )

    add_word_equation(
        doc,
        "Maximum OCPD rating",
        omml_sub("I", "OCPD,max") + omml_r(" = mult% × ") + omml_sub("I", "FLC"),
    )

    if any(r.get("inrush_12x") is not None for r in results):
        add_word_equation(
            doc,
            "Inrush withstand check",
            omml_sub("I", "inrush") + omml_r(" = 12 × ") + omml_sub("I", "FLA")
            + omml_r(" at 0.1 s,  25 × ") + omml_sub("I", "FLA") + omml_r(" at 0.01 s"),
        )


def _footnotes(results: list[dict[str, Any]]) -> list[str]:
    edition = oesc_edition()
    classes = {get_first(r, "voltage_class") for r in results}

    notes = [
        "The rule applied to each row is shown in the Rule path column: it is selected by "
        "voltage class, protection configuration, transformer type and, above 750 V, by the "
        "transformer rated impedance.",
    ]

    if OVER_750 in classes:
        notes.append(
            f"Transformers over 750 V are sized to {edition} Rule 26-250 and Table 50. That "
            "table covers rated impedances up to 10% for primary and secondary protection; "
            "rows above 10% cannot be sized from it."
        )
    if UPTO_750 in classes:
        notes.append(
            f"Transformers 750 V and under are sized to {edition} Rule 26-254 for dry-type "
            "and Rule 26-252 for other than dry-type. For oil-cooled transformers with "
            "primary-only protection the permitted multiplier steps with the primary "
            "current: 300% below 2 A, 167% below 9 A, and 150% at 9 A or more."
        )

    notes += [
        "Values are the code-based maximums. Where rounding to a standard rating is enabled, "
        "the next higher standard rating is shown; the raw calculated value is what the rule "
        "limits.",
        "Secondary reference values on primary-only rows are shown for the worksheet format "
        "only; they are not a required device.",
    ]

    if any(r.get("inrush_12x") is not None for r in results):
        notes.append(
            "Inrush withstand figures for dry-type transformers are 12× full-load current for "
            "0.1 s and 25× for 0.01 s. Confirm against the manufacturer's curves."
        )

    notes.append(
        "This report is based on the input values entered into the calculator. Final "
        "selections and design decisions should be verified against the OESC, project "
        "specifications, equipment data, a coordination study where required, and "
        "engineering judgement."
    )

    return notes


# ============================================================
# Schedule spec + entry point
# ============================================================
TP_SCHEDULE_SPEC = ReportSpec(
    code="oesc",
    calculator="transformer_protection",
    report_title="Transformer Protection — Calculation Results",
    sheet_name="Transformer Protection Schedule",
    tag="Tag / ID",
    cols=[
        Column("System", lambda r: get_first(r, "phase", default="—")),
        Column("Rating", _rating_kva),
        Column("V1 (V)", lambda r: fmt(get_first(r, "vpri"), "V")),
        Column("V2 (V)", lambda r: fmt(get_first(r, "vsec"), "V")),
        Column("Voltage class", lambda r: get_first(r, "voltage_class", default="—")),
        Column("Transformer type", lambda r: get_first(r, "xfmr_type", default="—")),
        Column("Protection", lambda r: get_first(r, "prot_config", default="—")),
        Column("%Z", _impedance),
        Column("Nameplate FLA", lambda r: yes_no(r.get("use_nameplate"))),
        Column("I1 (A)", lambda r: fmt(get_first(r, "Ip"), "A")),
        Column("I2 (A)", lambda r: fmt(get_first(r, "Is"), "A")),
        Column("Primary OCPD", lambda r: _devices(r, "primary"), color="green"),
        Column("Secondary OCPD", lambda r: _devices(r, "secondary"), color="green"),
        Column("Rule path", lambda r: get_first(r, "rule_path", default="—")),
        Column("Code Edition", _edition),
        Column("Source Tables", _source_tables),
    ],
    code_reference=_code_reference,
    notes=_footnotes,
    word_reference=_word_reference,
)


def render_add_to_schedule(result: dict[str, Any] | None) -> None:
    can_add = bool(result and result.get("devices"))
    render_schedule_commit(TP_SCHEDULE_SPEC, result, can_add=can_add)


def render_schedule_section() -> None:
    render_schedule_table(TP_SCHEDULE_SPEC)
