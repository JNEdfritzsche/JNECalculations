from __future__ import annotations

from typing import Any

from calc_common.formatting import fmt, format_cond_size
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
from lib.nec_tables import (
    TABLE_310_16,
    TABLE_430_247,
    TABLE_430_248,
    TABLE_430_250,
)


PHASE_FLC_TABLES = {
    "dc": TABLE_430_247,
    "single_phase": TABLE_430_248,
    "three_phase": TABLE_430_250,
}

FLC_TABLE_LABELS = {
    "dc": "430.247",
    "single_phase": "430.248",
    "three_phase": "430.250",
}


# ============================================================
# Column value helpers
# ============================================================
def _hp(result: dict[str, Any]) -> str:
    label = get_first(result, "hp_label", "hp")
    return "—" if label is None else f"{label} HP"


def _duty(result: dict[str, Any]) -> str:
    label = get_first(result, "sizing_factor_label")
    if not label:
        return "—"
    _factor, _sep, description = str(label).partition("—")
    return description.strip() or str(label)


def _size(result: dict[str, Any]) -> str:
    size = get_first(result, "conductor_size")
    return "—" if size is None else format_cond_size(size)


def _insulation(result: dict[str, Any]) -> str:
    return fmt(get_first(result, "temp_rating"), "°C")


# ============================================================
# Code reference — edition comes from the table's own CSV front matter
# ============================================================
def _nec_edition(table: dict[str, Any] | None = None) -> str:
    edition = (table or TABLE_310_16).get("edition") or TABLE_430_250.get("edition")
    return f"NEC {edition}" if edition else "NEC"


def _edition(result: dict[str, Any]) -> str:
    table = PHASE_FLC_TABLES.get(get_first(result, "phase")) or TABLE_310_16
    return _nec_edition(table)


def _source_tables(result: dict[str, Any]) -> str:
    tables = []

    flc_table = FLC_TABLE_LABELS.get(get_first(result, "phase"))
    if flc_table and get_first(result, "table_flc") is not None:
        tables.append(flc_table)

    if get_first(result, "conductor_size") is not None:
        tables.append("310.16")

    if get_first(result, "max_overload") is not None:
        tables.append("430.32")

    return ", ".join(tables) if tables else "—"


# ============================================================
# Report-wide text
# ============================================================
def _code_reference(results: list[dict[str, Any]]) -> str:
    return f"Per {_nec_edition()} 430.22 and 430.6(A)"


def _word_reference(doc, results: list[dict[str, Any]]) -> None:
    """Equations used across the calculations in the schedule (Word report only)."""
    doc.add_heading("Equations Used", level=1)

    add_word_equation(
        doc,
        "Feeder conductor ampacity",
        omml_sub("I", "cond") + omml_r(" = k × ") + omml_sub("I", "FLC"),
    )

    if any(get_first(r, "max_overload") is not None for r in results):
        add_word_equation(
            doc,
            "Maximum overload protection",
            omml_sub("I", "OL") + omml_r(" = SF × ") + omml_sub("I", "FLA,nameplate"),
        )


def _footnotes(results: list[dict[str, Any]]) -> list[str]:
    edition = _nec_edition()

    notes = [
        f"Per {edition} 430.6(A), branch-circuit and feeder conductor sizing uses the "
        "full-load current from Tables 430.247 through 430.250, not the motor nameplate "
        "current. Rows whose FLC source is Nameplate had no table value for the selected "
        "horsepower and voltage.",
        "The Code Edition and Source Tables columns give the tables each row was read "
        "from: the full-load current table for the system type, Table 310.16 for the "
        "conductor size, and 430.32 where an overload maximum was calculated.",
        f"The feeder conductor ampacity shown is the minimum for a single motor per "
        f"{edition} 430.22. Apply temperature correction, ambient and conduit-fill "
        "adjustment, voltage drop, and 430.24 for multiple-motor feeders as applicable.",
        "Conductor sizes are the smallest Table 310.16 entry meeting the required "
        "ampacity in the selected material and insulation temperature column, before "
        "any 110.14(C) terminal temperature limit is applied.",
    ]

    if any(get_first(r, "max_overload") is not None for r in results):
        notes.append(
            f"The maximum overload protection is sized per {edition} 430.32 using the "
            "marked nameplate full-load current and service factor. Verify against the "
            "selected device rating and the specific conditions of 430.32."
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
MF_SCHEDULE_SPEC = ReportSpec(
    code="nec",
    calculator="motor_feeder",
    report_title="Motor Feeder — Calculation Results",
    sheet_name="Motor Feeder Schedule",
    tag="Tag / ID",
    cols=[
        Column("System", lambda r: get_first(r, "phase_label", default="—")),
        Column("Motor", _hp),
        Column("Voltage (V)", lambda r: fmt(get_first(r, "voltage"), "V")),
        Column("I_FLC (A)", lambda r: fmt(get_first(r, "flc"), "A"), result=True),
        Column("FLC source", lambda r: get_first(r, "flc_source", default="—")),
        Column("k", lambda r: fmt(get_first(r, "sizing_factor")), result=True),
        Column("Duty basis", _duty),
        Column("Required ampacity (A)", lambda r: fmt(get_first(r, "conductor_ampacity"), "A"), color="green", result=True),
        Column("Conductor Size", _size, color="blue", result=True),
        Column("Size ampacity (A)", lambda r: fmt(get_first(r, "conductor_size_ampacity"), "A"), result=True),
        Column("Material", lambda r: get_first(r, "material_label", default="—"), group="conductor"),
        Column("Insulation", _insulation, group="conductor"),
        Column("Nameplate FLA (A)", lambda r: fmt(get_first(r, "nameplate_fla"), "A"), group="nameplate"),
        Column("SF", lambda r: get_first(r, "service_factor_label", default="—"), group="nameplate"),
        Column("Max overload (A)", lambda r: fmt(get_first(r, "max_overload"), "A"), color="green", result=True),
        Column("Code Edition", _edition),
        Column("Source Tables", _source_tables),
    ],
    groups={
        "conductor": Group("Conductor material / insulation"),
        "nameplate": Group("Nameplate FLA / SF"),
    },
    code_reference=_code_reference,
    notes=_footnotes,
    word_reference=_word_reference,
)


def render_add_to_schedule(result: dict[str, Any] | None) -> None:
    can_add = result is not None and get_first(result, "conductor_ampacity") is not None
    render_schedule_commit(MF_SCHEDULE_SPEC, result, can_add=can_add)


def render_schedule_section() -> None:
    render_schedule_table(MF_SCHEDULE_SPEC)
