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
    ReportSpec,
    render_schedule_commit,
    render_schedule_table,
)
from oesc_calc.common.code_meta import cite, oesc_edition


# ============================================================
# Column value helpers
# ============================================================
def _size(result: dict[str, Any]) -> str:
    size = get_first(result, "size")
    return "—" if size is None else str(size)


def _k_base(result: dict[str, Any]) -> str:
    k_base = get_first(result, "k_base")
    if k_base is None:
        return "—"
    return f"{k_base:.6g} ({get_first(result, 'column_label', default='—')})"


def _k_used(result: dict[str, Any]) -> str:
    k_used = get_first(result, "k_used")
    return "—" if k_used is None else f"{k_used:.6g}"


def _temperature(result: dict[str, Any]) -> str:
    temp = get_first(result, "operating_temp_c")
    multiplier = get_first(result, "k_temp_multiplier")
    if temp is None:
        return "—"
    return f"{temp}°C (×{multiplier:.2f})" if multiplier is not None else f"{temp}°C"


def _edition(result: dict[str, Any]) -> str:
    return oesc_edition(get_first(result, "primary_table"))


def _source_tables(result: dict[str, Any]) -> str:
    return cite(get_first(result, "source_tables", default=[]))


# ============================================================
# Report-wide text
# ============================================================
def _code_reference(results: list[dict[str, Any]]) -> str:
    return f"Per {oesc_edition()} Rule 8-102 and Appendix B Table D3"


def _word_reference(doc, results: list[dict[str, Any]]) -> None:
    """Equations used across the calculations in the schedule (Word report only)."""
    doc.add_heading("Equations Used", level=1)

    add_word_equation(
        doc,
        "Effective current",
        omml_sub("I", "eff") + omml_r(" = ") + omml_frac(omml_r("I"), omml_sub("N", "parallel")),
    )
    add_word_equation(
        doc,
        "Temperature-adjusted k-value",
        omml_r("k = ") + omml_sub("k", "75") + omml_r(" × ") + omml_sub("m", "temp"),
    )
    add_word_equation(
        doc,
        "Voltage drop",
        omml_sub("V", "D") + omml_r(" = ")
        + omml_frac(omml_r("k × f × ") + omml_sub("I", "eff") + omml_r(" × L"), omml_r("1000")),
    )
    add_word_equation(
        doc,
        "Voltage drop percentage",
        omml_r("%ΔV = ") + omml_frac(omml_r("100 × ") + omml_sub("V", "D"), omml_sub("V", "nom")),
    )


def _footnotes(results: list[dict[str, Any]]) -> list[str]:
    edition = oesc_edition()

    notes = [
        f"Voltage drop is calculated with the k-values of {edition} Appendix B, Table D3, "
        "which are Ω/km at a 75°C conductor operating temperature. Length is one-way in "
        "metres, so the divisor of 1000 converts the k-value to the run length.",
        "The k base column records the Table D3 column each row was read from — conductor "
        "material, cable or raceway installation, and the power-factor column. The DC column "
        "is used for DC circuits, where the power factor does not apply.",
        "Operating temperatures other than 75°C apply the Table D3 multipliers of 0.95 at "
        "60°C and 1.05 at 90°C.",
        "The factor f comes from the circuit type selected from Appendix D: 2 for the "
        "two-wire and line-to-ground cases, √3 for three-phase line-to-line cases.",
        f"{edition} Rule 8-102 limits voltage drop to 3% on a branch circuit and 5% from the "
        "supply to the point of utilization, unless project specifications dictate otherwise.",
        "This report is based on the input values entered into the calculator. Final "
        "selections and design decisions should be verified against the OESC, project "
        "specifications, equipment data, and engineering judgement.",
    ]

    if any(not r.get("use_table") for r in results):
        notes.append(
            "Rows with a Manual k base use a k-value entered directly, treated as a 75°C "
            "base value before the operating-temperature multiplier is applied."
        )

    return notes


# ============================================================
# Schedule spec + entry point
# ============================================================
VD_SCHEDULE_SPEC = ReportSpec(
    code="oesc",
    calculator="voltage_drop",
    report_title="Voltage Drop — Calculation Results",
    sheet_name="Voltage Drop Schedule",
    tag="Tag / ID",
    cols=[
        Column("Circuit type", lambda r: get_first(r, "f_label", default="—")),
        Column("f", lambda r: fmt(get_first(r, "f"))),
        Column("I (A)", lambda r: fmt(get_first(r, "current"), "A")),
        Column("Vnom (V)", lambda r: fmt(get_first(r, "v_nom"), "V")),
        Column("Length (m)", lambda r: fmt(get_first(r, "length_m"), "m")),
        Column("Parallel", lambda r: get_first(r, "n_parallel", default="—")),
        Column("I_eff (A)", lambda r: fmt(get_first(r, "I_eff"), "A")),
        Column("Material", lambda r: get_first(r, "material", default="—")),
        Column("Installation", lambda r: get_first(r, "location", default="—")),
        Column("Conductor Size", _size, color="blue"),
        Column("k base (Ω/km)", _k_base),
        Column("Temperature", _temperature),
        Column("k used (Ω/km)", _k_used),
        Column("VD (V)", lambda r: fmt(get_first(r, "voltage_drop"), "V")),
        Column("VD (%)", lambda r: fmt(get_first(r, "percent_drop"), "%"), color="green"),
        Column("Code Edition", _edition),
        Column("Source Tables", _source_tables),
    ],
    code_reference=_code_reference,
    notes=_footnotes,
    word_reference=_word_reference,
)


def render_add_to_schedule(result: dict[str, Any] | None) -> None:
    can_add = result is not None and get_first(result, "percent_drop") is not None
    render_schedule_commit(VD_SCHEDULE_SPEC, result, can_add=can_add)


def render_schedule_section() -> None:
    render_schedule_table(VD_SCHEDULE_SPEC)
