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
    Group,
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
def _entries(result: dict[str, Any], keyword: str) -> list[dict[str, Any]]:
    # Reference figures are informational — under primary-only protection the rule
    # requires no secondary device, so they must not fill the secondary columns.
    return [
        d for d in (result.get("devices") or [])
        if keyword in (d.get("label") or "").lower() and not d.get("reference")
    ]


def _kind(entry: dict[str, Any]) -> str:
    label = (entry.get("label") or "").lower()
    return "fuse" if "fuse" in label else ("breaker" if "breaker" in label else "either")


def _device(result: dict[str, Any], side: str, kind: str) -> dict[str, Any] | None:
    """The entry for one device slot.

    Rules 26-252 and 26-254 give a single maximum that applies whether a fuse or a
    breaker is used, so those rows fill both columns from the same entry; Rule
    26-250 rates fuses and breakers separately.
    """
    entries = _entries(result, side)
    return next(
        (e for e in entries if _kind(e) == kind),
        next((e for e in entries if _kind(e) == "either"), None),
    )


def _ocpd(result: dict[str, Any], side: str, kind: str, key: str) -> str:
    # The unit lives in the column header, so it is not repeated per device here.
    entry = _device(result, side, kind)
    if entry is not None:
        return fmt(entry.get(key))
    return "Not required" if result.get("devices") else "—"


def _mults(result: dict[str, Any]) -> str:
    parts = []
    for entry in (result.get("devices") or []):
        if entry.get("reference"):
            continue
        label = entry.get("label") or ""
        parts.append(label[label.find("(") + 1:label.find(")")] if "(" in label else label)
    return " / ".join(dict.fromkeys(parts)) if parts else "—"


def _rating_kva(result: dict[str, Any]) -> str:
    kva = get_first(result, "kva")
    return "—" if kva is None else fmt(kva, "kVA")


def _impedance(result: dict[str, Any]) -> str:
    return fmt(get_first(result, "z_pct"), "%")


def _edition(result: dict[str, Any]) -> str:
    return oesc_edition(get_first(result, "primary_table"))


def _source(result: dict[str, Any]) -> str:
    """Rules 26-252 and 26-254 carry their multipliers in the rule text, not a table."""
    tables = get_first(result, "source_tables", default=[])
    if tables:
        return cite(tables)
    rule = get_first(result, "rule_ref")
    return f"Rule {rule}" if rule else "—"


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
        "The max columns are the code-based maximums, mult% × FLC, and are what the rule "
        "limits. The selected columns are the next higher standard rating, shown where "
        "rounding to a standard rating is enabled.",
        "Rules 26-252 and 26-254 give a single maximum that applies whether a fuse or a "
        "breaker is used, so both device columns carry the same value on those rows; Rule "
        "26-250 rates fuses and breakers separately.",
        "Primary-only rows require no secondary device, so their secondary columns read Not "
        "required. The secondary figure the worksheet format shows for those rows is for "
        "information only and is not carried into this schedule.",
        "Rows at 750 V and under are sized by rule alone and cite no table, so their Source "
        "Tables entry is a dash; the Rule path column gives the rule applied.",
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
        # Inputs and the references the row was resolved against.
        Column("System", lambda r: get_first(r, "phase", default="—")),
        Column("Rating", _rating_kva),
        Column("V1 (V)", lambda r: fmt(get_first(r, "vpri"), "V"), group="volts"),
        Column("V2 (V)", lambda r: fmt(get_first(r, "vsec"), "V"), group="volts"),
        Column("Voltage class", lambda r: get_first(r, "voltage_class", default="—"), group="config"),
        Column("Transformer type", lambda r: get_first(r, "xfmr_type", default="—"), group="config"),
        Column("Protection", lambda r: get_first(r, "prot_config", default="—"), group="config"),
        Column("%Z", _impedance),
        Column("Nameplate FLA", lambda r: yes_no(r.get("use_nameplate"))),
        Column("Rule path", lambda r: get_first(r, "rule_path", default="—")),
        Column("Multipliers", _mults),
        Column("Code Edition", _edition),
        Column("Source", _source),

        # Calculated values.
        Column("I1 (A)", lambda r: fmt(get_first(r, "Ip"), "A"), result=True),
        Column("I2 (A)", lambda r: fmt(get_first(r, "Is"), "A"), result=True),
        Column("Pri. breaker max (A)", lambda r: _ocpd(r, "primary", "breaker", "raw"), result=True, group="pri_cb"),
        Column("Pri. breaker selected (A)", lambda r: _ocpd(r, "primary", "breaker", "selected"), color="green", result=True, group="pri_cb"),
        Column("Pri. fuse max (A)", lambda r: _ocpd(r, "primary", "fuse", "raw"), result=True, group="pri_fr"),
        Column("Pri. fuse selected (A)", lambda r: _ocpd(r, "primary", "fuse", "selected"), color="green", result=True, group="pri_fr"),
        Column("Sec. breaker max (A)", lambda r: _ocpd(r, "secondary", "breaker", "raw"), result=True, group="sec_cb"),
        Column("Sec. breaker selected (A)", lambda r: _ocpd(r, "secondary", "breaker", "selected"), color="green", result=True, group="sec_cb"),
        Column("Sec. fuse max (A)", lambda r: _ocpd(r, "secondary", "fuse", "raw"), result=True, group="sec_fr"),
        Column("Sec. fuse selected (A)", lambda r: _ocpd(r, "secondary", "fuse", "selected"), color="green", result=True, group="sec_fr"),
    ],
    groups={
        "volts": Group("V1 / V2 (V)"),
        "config": Group("Configuration"),
        "pri_cb": Group("Pri. breaker (A)", " → "),
        "pri_fr": Group("Pri. fuse (A)", " → "),
        "sec_cb": Group("Sec. breaker (A)", " → "),
        "sec_fr": Group("Sec. fuse (A)", " → "),
    },
    code_reference=_code_reference,
    notes=_footnotes,
    word_reference=_word_reference,
)


def render_add_to_schedule(result: dict[str, Any] | None) -> None:
    can_add = bool(result and result.get("devices"))
    render_schedule_commit(TP_SCHEDULE_SPEC, result, can_add=can_add)


def render_schedule_section() -> None:
    render_schedule_table(TP_SCHEDULE_SPEC)
