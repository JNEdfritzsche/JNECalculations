from __future__ import annotations

from typing import Any

from nec_calc.common.formatting import fmt
from nec_calc.common.report_helper import (
    add_word_equation,
    get_first,
    omml_frac,
    omml_r,
    omml_sqrt,
    omml_sub,
)
from nec_calc.common.report_schedule import (
    Column,
    ReportSpec,
    render_schedule_commit,
    render_schedule_table,
)
from lib.nec_tables import TABLE_8, TABLE_9


# ============================================================
# Column value helpers
# ============================================================
SCHEDULE_METHOD_LABELS = {
    "table8_r": "Table 8 (R)",
    "table9_z": "Table 9 (Z)",
    "manual_r": "Manual R",
}


def _method(result: dict[str, Any]) -> str:
    mode = get_first(result, "vd_mode")
    return SCHEDULE_METHOD_LABELS.get(mode, str(mode or "—"))


def _size(result: dict[str, Any]) -> str:
    size = get_first(result, "conductor_size")
    unit = get_first(result, "size_unit", default="")
    return "—" if size is None else f"{size} {unit}".strip()


def _rz(result: dict[str, Any]) -> str:
    if get_first(result, "vd_mode") == "table9_z":
        z = get_first(result, "z_value")
        return f"{z:.4g} (Z)" if z is not None else "—"
    r = get_first(result, "r_value", "manual_r")
    return f"{r:.4g} (R)" if r is not None else "—"


def _table_value(result: dict[str, Any]) -> str:
    """The figure(s) read straight off the NEC table, before any adjustment.

    Paired with _rz (the as-applied value) this shows the whole chain, which
    matters wherever the two differ: Table 8 corrected off 75°C, and Table 9
    with a circuit power factor other than the tabulated 0.85.
    """
    mode = get_first(result, "vd_mode")

    if mode == "table8_r":
        r_1 = get_first(result, "r_base_value")
        return f"{r_1:.4g} R" if r_1 is not None else "—"

    if mode == "table9_z":
        r_1 = get_first(result, "r_base_value")
        x_l = get_first(result, "xl_value")
        if r_1 is not None and x_l is not None:
            return f"{r_1:.4g} R / {x_l:.4g} XL"
        # No custom pf — the tabulated effective Z is what was read.
        z = get_first(result, "z_value")
        return f"{z:.4g} Z" if z is not None else "—"

    return "—"


def _material(result: dict[str, Any]) -> str:
    return get_first(result, "conductor_material", default=None) or "—"


def _conduit(result: dict[str, Any]) -> str:
    return get_first(result, "conduit_material", default=None) or "—"


# ============================================================
# Code reference — edition comes from the table's own CSV front matter
# ============================================================
MODE_SOURCE_TABLES = {"table8_r": TABLE_8, "table9_z": TABLE_9}


def _nec_edition(table: dict[str, Any] | None = None) -> str:
    edition = (table or TABLE_9).get("edition") or TABLE_8.get("edition")
    return f"NEC {edition}" if edition else "NEC"


def _edition(result: dict[str, Any]) -> str:
    table = MODE_SOURCE_TABLES.get(get_first(result, "vd_mode"))
    return "—" if table is None else _nec_edition(table)


def _source_table(result: dict[str, Any]) -> str:
    mode = get_first(result, "vd_mode")
    if mode == "table8_r":
        return "Chapter 9, Table 8"
    if mode == "table9_z":
        return "Chapter 9, Table 9"
    return "User-entered R"


# ============================================================
# Report-wide text
# ============================================================
def _code_reference(results: list[dict[str, Any]]) -> str:
    modes = {get_first(r, "vd_mode") for r in results}
    parts = []
    if "table8_r" in modes:
        parts.append("Chapter 9, Table 8")
    if "table9_z" in modes:
        parts.append("Chapter 9, Table 9")
    if "manual_r" in modes:
        parts.append("user-entered resistance")
    return f"Per {_nec_edition()} " + ("; ".join(parts) if parts else "Chapter 9")


def _word_reference(doc, results: list[dict[str, Any]]) -> None:
    """Equations used across the calculations in the schedule (Word report only)."""
    modes = {get_first(r, "vd_mode") for r in results}
    uses_custom_pf = any(
        get_first(r, "vd_mode") == "table9_z" and get_first(r, "use_custom_pf") for r in results
    )
    uses_temp_adj = "table8_r" in modes or any(
        get_first(r, "vd_mode") == "table9_z"
        and get_first(r, "use_custom_pf")
        and get_first(r, "use_custom_T_op")
        for r in results
    )

    doc.add_heading("Equations Used", level=1)

    add_word_equation(
        doc,
        "Effective current",
        omml_sub("I", "eff") + omml_r(" = ") + omml_frac(omml_r("I"), omml_sub("N", "parallel")),
    )

    if uses_temp_adj:
        add_word_equation(
            doc,
            "Temperature-adjusted resistance",
            omml_r("R = ") + omml_sub("R", "1") + omml_r(" × [1 + α × (") + omml_sub("T", "op") + omml_r(" - 75)]"),
        )

    if uses_custom_pf:
        add_word_equation(
            doc,
            "Effective impedance",
            omml_sub("Z", "eff") + omml_r(" = R × pf + ") + omml_sub("X", "L") + omml_r(" × ") + omml_sqrt(omml_r("1 - pf²")),
        )

    if "table8_r" in modes:
        add_word_equation(
            doc,
            "Voltage drop — Table 8 (resistance)",
            omml_sub("V", "D") + omml_r(" = ") + omml_frac(omml_r("pf × f × R × ") + omml_sub("I", "eff") + omml_r(" × L"), omml_r("1000")),
        )
    if "table9_z" in modes:
        z_term = omml_sub("Z", "eff") if uses_custom_pf else omml_r("Z")
        add_word_equation(
            doc,
            "Voltage drop — Table 9 (impedance)",
            omml_sub("V", "D") + omml_r(" = ") + omml_frac(omml_r("f × ") + z_term + omml_r(" × ") + omml_sub("I", "eff") + omml_r(" × L"), omml_r("1000")),
        )
    if "manual_r" in modes:
        add_word_equation(
            doc,
            "Voltage drop — Manual R",
            omml_sub("V", "D") + omml_r(" = ") + omml_frac(omml_r("pf × f × ") + omml_sub("R", "manual") + omml_r(" × ") + omml_sub("I", "eff") + omml_r(" × L"), omml_r("1000")),
        )

    add_word_equation(
        doc,
        "Voltage drop percentage",
        omml_r("%ΔV = ") + omml_frac(omml_r("100 × ") + omml_sub("V", "D"), omml_sub("V", "nom")),
    )

    if uses_temp_adj:
        caption = doc.add_paragraph()
        caption_run = caption.add_run("Temperature coefficient α = 0.00300 for copper, 0.00323 for aluminum.")
        caption_run.italic = True


def _footnotes(results: list[dict[str, Any]]) -> list[str]:
    edition = _nec_edition()

    notes = [
        f"Voltage drop per {edition} Chapter 9 — Table 8 uses conductor DC resistance; "
        "Table 9 uses effective AC impedance (Z), tabulated at 0.85 power factor; "
        "Manual R uses a user-entered resistance value.",
        "The Code Edition and Source Table columns give the table each row's R or Z value "
        "was read from; From table is the tabulated figure at 75°C and R/Z used is the value "
        "actually applied, after any temperature or power-factor adjustment. Rows using a "
        "user-entered resistance cite no table.",
    ]

    if any(
        get_first(r, "vd_mode") == "table8_r"
        or (get_first(r, "use_custom_pf") and get_first(r, "use_custom_T_op"))
        for r in results
    ):
        notes.append(
            f"Resistance adjusted from the 75°C tabulated value using the temperature-change "
            f"equation of {edition} Chapter 9, Table 8, Note 2: R2 = R1 [1 + α (T2 − 75)]."
        )

    notes += [
        "Target voltage drop is typically ≤ 3% for branch circuits and ≤ 5% total, per the "
        f"Informational Notes to {edition} 210.19(A) and 215.2(A), unless project "
        "specifications or the authority having jurisdiction dictate otherwise.",
        "This report is based on the input values entered into the calculator. Final selections "
        "and design decisions should be verified against the NEC, project specifications, "
        "equipment data, and engineering judgement.",
    ]

    return notes


# ============================================================
# Schedule spec + entry point
# ============================================================
VD_SCHEDULE_SPEC = ReportSpec(
    prefix="nec_voltage_drop_schedule",
    report_title="Voltage Drop — Calculation Results",
    sheet_name="Voltage Drop Schedule",
    tag="Tag / ID",
    cols=[
        Column("System", lambda r: get_first(r, "system_type_label", default="—")),
        Column("Method", _method),
        Column("I (A)", lambda r: fmt(get_first(r, "current"), "A")),
        Column("Vnom (V)", lambda r: fmt(get_first(r, "v_nom", "voltage"), "V")),
        Column("Length (ft)", lambda r: fmt(get_first(r, "length"), "ft")),
        Column("Parallel", lambda r: get_first(r, "parallel_conductors")),
        Column("Conductor Size", _size, color="blue"),
        Column("Material", _material),
        Column("Conduit", _conduit),
        Column("From table (Ω/kft)", _table_value),
        Column("R/Z used (Ω/kft)", _rz),
        Column("VD (V)", lambda r: fmt(get_first(r, "voltage_drop"), "V")),
        Column("VD (%)", lambda r: fmt(get_first(r, "percent_drop"), "%"), color="green"),
        Column("Code Edition", _edition),
        Column("Source Table", _source_table),
    ],
    code_reference=_code_reference,
    notes=_footnotes,
    word_reference=_word_reference,
)


def render_add_to_schedule(result: dict[str, Any] | None) -> None:
    """Tag + add button — belongs beside the result, in the right-hand pane."""
    can_add = result is not None and get_first(result, "voltage_drop") is not None
    render_schedule_commit(VD_SCHEDULE_SPEC, result, can_add=can_add)


def render_schedule_section() -> None:
    """The accumulated schedule table + exports — full width, below both panes."""
    render_schedule_table(VD_SCHEDULE_SPEC)
