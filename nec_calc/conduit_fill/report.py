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
from lib.nec_tables import TABLE_1, TABLE_2


# ============================================================
# Column value helpers
# ============================================================
def _area_unit(result: dict[str, Any]) -> str:
    return get_first(result, "area_unit", default="mm²")


def _units(result: dict[str, Any]) -> str:
    units = get_first(result, "units")
    return "—" if units is None else f"{str(units).title()} ({_area_unit(result)})"


def _conduit(result: dict[str, Any]) -> str:
    """The Table 4 sub-table titles read 'Table 4 Article 358 — Electrical Metallic
    Tubing (EMT)'. table_4_emt.csv carries the overall Table 4 title instead, with no
    article, so that one falls back to the conduit key.
    """
    key = get_first(result, "conduit_key")
    label = get_first(result, "conduit_label")
    _article, _sep, name = str(label or "").partition("—")
    return name.strip() or (str(key).upper() if key else "—")


def _inches(value: Any) -> str:
    """Table 2 prints its inch column as text ('9 1/2') where the value is fractional."""
    text = fmt(value, "in")
    return text if text.endswith(" in") or text == "—" else f"{text} in"


def _bend(result: dict[str, Any], mm_key: str, in_key: str) -> str:
    mm = get_first(result, mm_key)
    inches = get_first(result, in_key)
    if mm is None and inches is None:
        return "—"
    return f"{fmt(mm, 'mm')} ({_inches(inches)})"


def _min_size(result: dict[str, Any]) -> str:
    size = get_first(result, "min_trade_size")
    if size is None:
        return "—"
    designator = get_first(result, "min_metric_designator")
    return f"{size} ({designator})" if designator is not None else str(size)


# ============================================================
# Code reference — edition comes from the table's own CSV front matter
# ============================================================
def _nec_edition() -> str:
    edition = TABLE_1.get("edition") or TABLE_2.get("edition")
    return f"NEC {edition}" if edition else "NEC"


def _edition(result: dict[str, Any]) -> str:
    return _nec_edition()


def _source_tables(result: dict[str, Any]) -> str:
    tables = ["1", "4"]

    if any((g or {}).get("conductor_type") for g in result.get("groups") or []):
        tables.append("5")

    if get_first(result, "bend_one_shot_mm") is not None:
        tables.append("2")

    return ", ".join(tables)


# ============================================================
# Report-wide text
# ============================================================
def _code_reference(results: list[dict[str, Any]]) -> str:
    return f"Per {_nec_edition()} Chapter 9, Tables 1, 2, 4 and 5"


def _word_reference(doc, results: list[dict[str, Any]]) -> None:
    """Equations used across the calculations in the schedule (Word report only)."""
    doc.add_heading("Equations Used", level=1)

    add_word_equation(
        doc,
        "Total conductor area",
        omml_sub("A", "total") + omml_r(" = Σ (N × ") + omml_sub("A", "conductor") + omml_r(")"),
    )
    add_word_equation(
        doc,
        "Conduit fill",
        omml_r("Fill % = ")
        + omml_frac(omml_sub("A", "total"), omml_sub("A", "100%"))
        + omml_r(" × 100"),
    )
    add_word_equation(
        doc,
        "Table 1 fill limit",
        omml_sub("A", "total") + omml_r(" ≤ ") + omml_sub("A", "allowed"),
    )


def _footnotes(results: list[dict[str, Any]]) -> list[str]:
    edition = _nec_edition()

    notes = [
        f"Conduit fill is evaluated per {edition} Chapter 9, Table 1 (53% for one conductor, "
        "31% for two, 40% for three or more), using conduit dimensions from Table 4 and "
        "conductor dimensions from Table 5.",
        "The Code Edition and Source Tables columns give the Chapter 9 tables each row was "
        "read from. Rows using a manually entered conductor area cite no Table 5.",
        f"Bend radii are the minimums from {edition} Chapter 9, Table 2 for the selected "
        "trade size, and are shown in millimetres with the inch value in brackets.",
        "Chapter 9 notes such as Note 4 (equipment grounding conductors count toward fill) "
        "and Note 7 (rounding of same-size conductor counts) must be applied by the designer "
        "where relevant.",
        "Areas are shown in the unit system each row was calculated in, as the Chapter 9 "
        "tables publish both.",
        "This report is based on the input values entered into the calculator. Final "
        "selections and design decisions should be verified against the NEC, project "
        "specifications, equipment data, and engineering judgement.",
    ]

    return notes


# ============================================================
# Schedule spec + entry point
# ============================================================
CF_SCHEDULE_SPEC = ReportSpec(
    code="nec",
    calculator="conduit_fill",
    report_title="Conduit Fill — Calculation Results",
    sheet_name="Conduit Fill Schedule",
    tag="Tag / ID",
    cols=[
        Column("Units", _units),
        Column("Conduit / tubing", _conduit),
        Column("Trade size", lambda r: get_first(r, "trade_size", default="—")),
        Column("Metric designator", lambda r: get_first(r, "metric_designator", default="—")),
        Column("Conductors", lambda r: get_first(r, "n_conductors", default="—")),
        Column("Total conductor area", lambda r: fmt(get_first(r, "total_conductor_area"), _area_unit(r))),
        Column("Internal area (100%)", lambda r: fmt(get_first(r, "internal_area"), _area_unit(r))),
        Column("Allowed fill (Table 1)", lambda r: fmt(get_first(r, "allowed_percent"), "%")),
        Column("Allowed area", lambda r: fmt(get_first(r, "allowed_area"), _area_unit(r))),
        Column("Actual fill (%)", lambda r: fmt(get_first(r, "fill_percent"), "%"), color="green"),
        Column("Fits?", lambda r: yes_no(get_first(r, "fits"))),
        Column("Min trade size", _min_size, color="blue"),
        Column("Bend — one shot / full shoe", lambda r: _bend(r, "bend_one_shot_mm", "bend_one_shot_in")),
        Column("Bend — other bends", lambda r: _bend(r, "bend_other_mm", "bend_other_in")),
        Column("Code Edition", _edition),
        Column("Source Tables (Ch. 9)", _source_tables),
    ],
    code_reference=_code_reference,
    notes=_footnotes,
    word_reference=_word_reference,
)


def render_add_to_schedule(result: dict[str, Any] | None) -> None:
    can_add = result is not None and get_first(result, "fill_percent") is not None
    render_schedule_commit(CF_SCHEDULE_SPEC, result, can_add=can_add)


def render_schedule_section() -> None:
    render_schedule_table(CF_SCHEDULE_SPEC)
