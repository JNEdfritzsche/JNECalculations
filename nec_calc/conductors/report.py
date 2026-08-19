from __future__ import annotations

from typing import Any

from calc_common.formatting import fmt
from calc_common.report_helper import (
    add_word_equation,
    get_first,
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
from lib.nec_tables import TABLE_310_16, TABLE_310_15_B_1_1, TABLE_310_15_B_1_2, TABLE_310_15_C_1


def _material(result: dict[str, Any]) -> str:
    mat = get_first(result, "material")
    if mat == "cu" or mat == "Copper":
        return "Copper"
    elif mat == "al":
        return "Aluminum"
    return str(mat or "—")


def _wire_type(result: dict[str, Any]) -> str:
    wt = get_first(result, "wire_type")
    if wt == "Not specified":
        return "—"
    return str(wt or "—")


def _rating(result: dict[str, Any]) -> str:
    tr = get_first(result, "temp_rating")
    return fmt(tr, "°C") if tr else "—"


def _ambient(result: dict[str, Any]) -> str:
    amb = get_first(result, "ambient_temp_c")
    return fmt(amb, "°C") if amb else "—"


def _terminal(result: dict[str, Any]) -> str:
    term = get_first(result, "terminal_temp_rating")
    if term and term not in ("None", "—", ""):
        return fmt(term, "°C")
    return "—"


def _yes_no(val) -> str:
    if val is None:
        return "—"
    return "Yes" if val else "No"


def _edition(result: dict[str, Any]) -> str:
    edition = TABLE_310_16.get("edition")
    return f"NEC {edition}" if edition else "NEC"


def _source_tables(result: dict[str, Any]) -> str:
    tables = ["310.16"]
    
    ambient_base = get_first(result, "ambient_base")
    if ambient_base == "40c":
        tables.append("310.15(B)(1)(2)")
    elif ambient_base == "30c":
        tables.append("310.15(B)(1)(1)")
        
    n_cond = get_first(result, "number_of_conductors")
    if n_cond not in ("1-3", "1", "2", "3"):
        tables.append("310.15(C)(1)")
        
    term = get_first(result, "terminal_temp_rating")
    if term and term not in ("None", "—", ""):
        tables.append("110.14(C)")
        
    return ", ".join(tables)


def _word_reference(doc, results: list[dict[str, Any]]) -> None:
    doc.add_heading("Equations Used", level=1)

    eq1 = (
        omml_sub("I", "derated")
        + omml_r(" = ")
        + omml_sub("I", "table")
        + omml_r(" × ")
        + omml_sub("CF", "temp")
        + omml_r(" × ")
        + omml_sub("AF", "cond")
    )

    eq2 = (
        omml_sub("I", "allowable")
        + omml_r(" = min(")
        + omml_sub("I", "derated")
        + omml_r(", ")
        + omml_sub("I", "terminal")
        + omml_r(")")
    )

    add_word_equation(doc, "Derated Ampacity (NEC 310.15)", eq1)
    add_word_equation(doc, "Final Allowable Ampacity (NEC 110.14(C))", eq2)


def _footnotes(results: list[dict[str, Any]]) -> list[str]:
    return [
        "Conductor ampacity calculations are performed in accordance with NEC Articles 310 and 110.14(C).",
        "Base ampacities are retrieved from NEC Table 310.16 (based on 30°C ambient and not more than 3 current-carrying conductors).",
        "Ambient temperature correction factors are determined from Table 310.15(B)(1)(1) or (2) based on conductor insulation rating.",
        "Adjustment factors for more than three current-carrying conductors in a raceway or cable are determined from Table 310.15(C)(1).",
        "Per NEC 110.14(C), equipment terminal temperature ratings restrict conductor ampacity; the final allowable ampacity cannot exceed the ampacity for the lowest temperature rating of any connected terminal, device, or conductor.",
    ]


COND_SCHEDULE_SPEC = ReportSpec(
    code="nec",
    calculator="conductors",
    report_title="Conductors — Calculation Results",
    sheet_name="Conductors Schedule",
    tag="Tag / ID",
    input_prefixes=("nec_cond_",),
    cols=[
        Column("Size", lambda r: get_first(r, "selected_size_display", default="—"), color="blue"),
        Column("Material", _material, group="conductor"),
        Column("Insulation Type", _wire_type, group="conductor"),
        Column("Rating", _rating, group="conductor"),
        Column("Ambient", _ambient, group="conditions"),
        Column("CCCs", lambda r: get_first(r, "number_of_conductors", default="—"), group="conditions"),
        Column("Term Limit", _terminal, group="conditions"),
        Column("Parallel", lambda r: get_first(r, "n_parallel", default="1")),
        Column("Load (A)", lambda r: fmt(get_first(r, "load_current"), "A")),
        Column("Derated (A)", lambda r: fmt(get_first(r, "derated_ampacity"), "A"), result=True),
        Column("Allowable (A)", lambda r: fmt(get_first(r, "calculated_value"), "A"), color="green", result=True),
        Column("Adequate?", lambda r: _yes_no(get_first(r, "is_adequate")), result=True),
        Column("Base Amp (A)", lambda r: fmt(get_first(r, "table_ampacity"), "A"), result=True),
        Column("Ambient CF", lambda r: fmt(get_first(r, "ambient_correction")), result=True, group="factors"),
        Column("Cond AF", lambda r: fmt(get_first(r, "conductor_adjustment")), result=True, group="factors"),
        Column("Code Edition", _edition),
        Column("Source Tables", _source_tables),
    ],
    groups={
        "conductor": Group("Conductor"),
        "conditions": Group("Ambient / CCCs / term"),
        "factors": Group("Ambient CF / cond AF"),
    },
    code_reference=lambda rs: "Per NEC 310.15 and 110.14(C)",
    notes=_footnotes,
    word_reference=_word_reference,
)


def render_add_to_schedule(result: dict[str, Any] | None) -> None:
    can_add = result is not None and get_first(result, "calculated_value") is not None
    render_schedule_commit(COND_SCHEDULE_SPEC, result, can_add=can_add)


def render_schedule_section() -> None:
    render_schedule_table(COND_SCHEDULE_SPEC)
