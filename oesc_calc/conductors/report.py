from __future__ import annotations

from typing import Any

from calc_common.formatting import fmt, format_cond_size
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
from oesc_calc.common.code_meta import cite, oesc_edition


# ============================================================
# Column value helpers
# ============================================================
def _size(result: dict[str, Any]) -> str:
    size = get_first(result, "selected_size")
    return "—" if size is None else format_cond_size(size)


def _factor(result: dict[str, Any], key: str, source_key: str) -> str:
    value = get_first(result, key)
    if value is None:
        return "—"
    source = get_first(result, source_key, default="")
    return f"{value:g} ({source})" if source and source != "None" else f"{value:g}"


def _table_column(result: dict[str, Any]) -> str:
    table = get_first(result, "amp_table", default="—")
    temp = get_first(result, "temp_choice")
    return f"{table} @ {temp}°C" if temp is not None else table


def _edition(result: dict[str, Any]) -> str:
    return oesc_edition(get_first(result, "primary_table"))


def _source_tables(result: dict[str, Any]) -> str:
    return cite(get_first(result, "source_tables", default=[]))


# ============================================================
# Report-wide text
# ============================================================
def _code_reference(results: list[dict[str, Any]]) -> str:
    return f"Per {oesc_edition()} Rule 4-004 — conductor ampacity"


def _word_reference(doc, results: list[dict[str, Any]]) -> None:
    """Equations used across the calculations in the schedule (Word report only)."""
    doc.add_heading("Equations Used", level=1)

    add_word_equation(
        doc, "Design current",
        omml_sub("I", "design") + omml_r(" = SF × ") + omml_sub("I", "load"),
    )
    add_word_equation(
        doc, "Design current per parallel set",
        omml_sub("I", "set") + omml_r(" = ") + omml_frac(omml_sub("I", "design"), omml_r("N")),
    )
    add_word_equation(
        doc, "Total correction factor",
        omml_sub("k", "total") + omml_r(" = ") + omml_sub("k", "corr") + omml_r(" × ") + omml_sub("k", "temp"),
    )
    add_word_equation(
        doc, "Required base-table ampacity",
        omml_sub("I", "table") + omml_r(" = ") + omml_frac(omml_sub("I", "set"), omml_sub("k", "total")),
    )
    add_word_equation(
        doc, "Adjusted ampacity",
        omml_sub("I", "adj") + omml_r(" = ") + omml_sub("I", "base") + omml_r(" × ") + omml_sub("k", "total"),
    )


def _footnotes(results: list[dict[str, Any]]) -> list[str]:
    edition = oesc_edition()

    notes = [
        f"The ampacity table for each row is selected by the {edition} Rule 4-004 subrule "
        "shown in the Subrule column: installation method, conductor form, spacing and the "
        "number of current-carrying conductors.",
        "Ampacities come from Table 1 or 2 for copper and Table 3 or 4 for aluminum — the "
        "free-air tables where the subrule calls for them, otherwise the raceway and cable "
        "tables.",
        "Correction factors come from Table 5B for four or fewer single conductors at less "
        "than 25% spacing, Table 5C for four or more conductors in a raceway or cable, and "
        "Table 5D for single conductors spaced 25% to 100%. Ambient temperature correction "
        "comes from Table 5A.",
        "The selected size is the smallest in the chosen table column whose base ampacity "
        "meets the required value after both correction factors are applied.",
        "Rows citing Diagrams D8 to D11 or IEEE 835 cannot be sized from Tables 1 to 4; "
        "those configurations must be taken from the diagrams or calculated.",
        "Termination temperature limits, voltage drop and overcurrent protection are not "
        "checked here.",
        "This report is based on the input values entered into the calculator. Final "
        "selections and design decisions should be verified against the OESC, project "
        "specifications, equipment data, and engineering judgement.",
    ]

    return notes


# ============================================================
# Schedule spec + entry point
# ============================================================
COND_SCHEDULE_SPEC = ReportSpec(
    code="oesc",
    calculator="conductors",
    report_title="Conductors — Calculation Results",
    sheet_name="Conductors Schedule",
    tag="Tag / ID",
    cols=[
        Column("Material", lambda r: get_first(r, "material", default="—"), group="conductor"),
        Column("Conductor form", lambda r: get_first(r, "conductor_form", default="—"), group="conductor"),
        Column("Installation", lambda r: get_first(r, "install", default="—")),
        Column("CCCs", lambda r: get_first(r, "n_conductors", default="—")),
        Column("Spacing", lambda r: get_first(r, "spacing", default="—")),
        Column("Load (A)", lambda r: fmt(get_first(r, "i_load"), "A")),
        Column("SF", lambda r: fmt(get_first(r, "sf"))),
        Column("Design current (A)", lambda r: fmt(get_first(r, "I_design_total"), "A"), result=True),
        Column("Parallel sets", lambda r: get_first(r, "n_parallel", default="—")),
        Column("Per set (A)", lambda r: fmt(get_first(r, "I_per_set"), "A"), result=True),
        Column("k_corr", lambda r: _factor(r, "corr_factor", "corr_factor_source"), result=True, group="k"),
        Column("k_temp", lambda r: _factor(r, "temp_factor", "temp_factor_source"), result=True, group="k"),
        Column("Required base (A)", lambda r: fmt(get_first(r, "I_table_required"), "A"), result=True),
        Column("Ampacity table", _table_column),
        Column("Conductor Size", _size, color="blue", result=True),
        Column("Base ampacity (A)", lambda r: fmt(get_first(r, "base_ampacity"), "A"), result=True),
        Column("Adjusted per set (A)", lambda r: fmt(get_first(r, "adjusted_ampacity_per_set"), "A"), color="green", result=True),
        Column("Subrule", lambda r: get_first(r, "subrule", default="—")),
        Column("Code Edition", _edition),
        Column("Source Tables", _source_tables),
    ],
    groups={
        "conductor": Group("Conductor"),
        "k": Group("k_corr / k_temp"),
    },
    code_reference=_code_reference,
    notes=_footnotes,
    word_reference=_word_reference,
)


def render_add_to_schedule(result: dict[str, Any] | None) -> None:
    can_add = result is not None and get_first(result, "I_table_required") is not None
    render_schedule_commit(COND_SCHEDULE_SPEC, result, can_add=can_add)


def render_schedule_section() -> None:
    render_schedule_table(COND_SCHEDULE_SPEC)
