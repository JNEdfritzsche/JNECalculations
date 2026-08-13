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
from oesc_calc.common.code_meta import oesc_edition
from oesc_calc.motor_feeder.calculation import DC, HP, SINGLE_PHASE, THREE_PHASE


# ============================================================
# Column value helpers
# ============================================================
def _power(result: dict[str, Any]) -> str:
    return fmt(get_first(result, "power_value"), get_first(result, "power_unit", default=""))


def _pf(result: dict[str, Any]) -> str:
    if get_first(result, "phase") == DC:
        return "N/A (DC)"
    return fmt(get_first(result, "pf"))


def _efficiency(result: dict[str, Any]) -> str:
    return fmt(get_first(result, "eff"), "%")


def _factor(result: dict[str, Any]) -> str:
    return fmt(get_first(result, "sizing_factor"))


def _edition(result: dict[str, Any]) -> str:
    return oesc_edition()


def _reference(result: dict[str, Any]) -> str:
    return "Rule 28-106"


# ============================================================
# Report-wide text
# ============================================================
def _code_reference(results: list[dict[str, Any]]) -> str:
    return f"Per {oesc_edition()} Rule 28-106 — motor feeder conductor sizing"


def _systems_present(results: list[dict[str, Any]]) -> list[str]:
    phases = {get_first(r, "phase") for r in results}
    return [p for p in (THREE_PHASE, SINGLE_PHASE, DC) if p in phases]


def _word_reference(doc, results: list[dict[str, Any]]) -> None:
    """Equations used across the calculations in the schedule (Word report only)."""
    doc.add_heading("Equations Used", level=1)

    systems = _systems_present(results)
    uses_hp = any(get_first(r, "power_unit") == HP for r in results)
    numerator = omml_r("HP × 745.7") if uses_hp else omml_r("kW × 1000")

    for phase in systems:
        if phase == DC:
            denominator = omml_r("V × η")
        elif phase == THREE_PHASE:
            denominator = omml_r("√3 × ") + omml_sub("V", "LL") + omml_r(" × cosθ × η")
        else:
            denominator = omml_r("V × cosθ × η")

        add_word_equation(
            doc,
            f"Full-load current — {phase}",
            omml_sub("I", "FLA") + omml_r(" = ") + omml_frac(numerator, denominator),
        )

    add_word_equation(
        doc,
        "Conductor ampacity target",
        omml_sub("I", "target") + omml_r(" = k × ") + omml_sub("I", "FLA"),
    )


def _footnotes(results: list[dict[str, Any]]) -> list[str]:
    edition = oesc_edition()

    notes = [
        f"{edition} Rule 28-106 requires the conductors supplying a single motor to have "
        "an ampacity of not less than 125% of the motor full-load current. The ampacity "
        "target column applies the sizing factor selected for each row.",
        "Full-load current is estimated from nameplate power, voltage, power factor and "
        "efficiency. It is not read from Table 44, 45 or D2, and the motor nameplate value "
        "should be preferred for the final design.",
        f"Duty other than continuous is covered by {edition} Rule 28-108 and Table 27; the "
        "sizing factor column records the factor applied, but the duty rating itself is not "
        "checked by this calculator.",
        "Conductor ampacity corrections for ambient temperature, conductor grouping and "
        "insulation rating (Table 37), and the 3% branch-circuit voltage drop limit of "
        "Rule 8-102, should be checked separately.",
        "This report is based on the input values entered into the calculator. Final "
        "selections and design decisions should be verified against the OESC, project "
        "specifications, equipment data, and engineering judgement.",
    ]

    return notes


# ============================================================
# Schedule spec + entry point
# ============================================================
MF_SCHEDULE_SPEC = ReportSpec(
    code="oesc",
    calculator="motor_feeder",
    report_title="Motor Feeder — Calculation Results",
    sheet_name="Motor Feeder Schedule",
    tag="Tag / ID",
    cols=[
        Column("System", lambda r: get_first(r, "phase", default="—")),
        Column("Motor power", _power),
        Column("Voltage (V)", lambda r: fmt(get_first(r, "volts"), "V")),
        Column("Power factor", _pf),
        Column("Efficiency", _efficiency),
        Column("I_FLA (A)", lambda r: fmt(get_first(r, "ifla"), "A"), color="blue", result=True),
        Column("Sizing factor, k", _factor, result=True),
        Column("Ampacity target (A)", lambda r: fmt(get_first(r, "target"), "A"), color="green", result=True),
        Column("Code Edition", _edition),
        Column("Code Reference", _reference),
    ],
    code_reference=_code_reference,
    notes=_footnotes,
    word_reference=_word_reference,
)


def render_add_to_schedule(result: dict[str, Any] | None) -> None:
    can_add = result is not None and get_first(result, "target") is not None
    render_schedule_commit(MF_SCHEDULE_SPEC, result, can_add=can_add)


def render_schedule_section() -> None:
    render_schedule_table(MF_SCHEDULE_SPEC)
