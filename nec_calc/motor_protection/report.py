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
    Group,
    ReportSpec,
    render_schedule_commit,
    render_schedule_table,
)
from lib.nec_tables import (
    TABLE_430_52_C_1,
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

LRC_TABLE_LABELS = {
    "table_430_251_a": "430.251(A)",
    "table_430_251_b": "430.251(B)",
    "table_430_251_c": "430.251(C)",
}

CATEGORY_LABELS = {
    "single_phase": "Single-phase",
    "ac_polyphase": "AC polyphase",
    "squirrel_cage": "Squirrel cage",
    "design_b_energy_efficient": "Design B energy-efficient",
    "synchronous": "Synchronous",
    "wound_rotor": "Wound-rotor",
    "dc": "DC",
}

DEVICE_HEADERS = [
    ("nontime_delay_fuse", "Non-time-delay fuse"),
    ("dual_element_time_delay_fuse", "Dual-element fuse"),
    ("instantaneous_trip_breaker", "Inst.-trip breaker"),
    ("inverse_time_breaker", "Inverse-time breaker"),
]


# ============================================================
# Column value helpers
# ============================================================
def _hp(result: dict[str, Any]) -> str:
    label = get_first(result, "hp_label", "hp")
    return "—" if label is None else f"{label} HP"


def _category(result: dict[str, Any]) -> str:
    key = get_first(result, "category_key")
    return CATEGORY_LABELS.get(str(key or ""), str(key or "—"))


def _device_entry(result: dict[str, Any], key: str) -> dict[str, Any] | None:
    devices = (result.get("branch") or {}).get("devices") or []
    return next((d for d in devices if d.get("key") == key), None)


def _device(result: dict[str, Any], key: str, field: str) -> str:
    device = _device_entry(result, key)
    return "—" if device is None else fmt(device.get(field), "A")


def _overload(result: dict[str, Any], size_key: str, factor_key: str) -> str:
    overload = result.get("overload") or {}
    size = overload.get(size_key)
    if size is None:
        return "—"

    factor = overload.get(factor_key)
    return f"{fmt(size, 'A')} ({int(factor * 100)}%)" if factor is not None else fmt(size, "A")


def _disconnect(result: dict[str, Any]) -> str:
    return fmt((result.get("disconnect") or {}).get("min_disconnect_ampere"), "A")


def _lrc(result: dict[str, Any], key: str) -> str:
    return fmt((result.get(key) or {}).get("locked_rotor_current"), "A")


# ============================================================
# Code reference — edition comes from the table's own CSV front matter
# ============================================================
def _nec_edition(table: dict[str, Any] | None = None) -> str:
    edition = (table or TABLE_430_52_C_1).get("edition") or TABLE_430_250.get("edition")
    return f"NEC {edition}" if edition else "NEC"


def _edition(result: dict[str, Any]) -> str:
    table = PHASE_FLC_TABLES.get(get_first(result, "phase")) or TABLE_430_52_C_1
    return _nec_edition(table)


def _source_tables(result: dict[str, Any]) -> str:
    tables = []

    flc_table = FLC_TABLE_LABELS.get(get_first(result, "phase"))
    if flc_table and get_first(result, "table_flc") is not None:
        tables.append(flc_table)

    devices = (result.get("branch") or {}).get("devices") or []
    if any(d.get("pct") is not None for d in devices):
        tables.append("430.52(C)(1)")

    if (result.get("overload") or {}).get("max_overload") is not None:
        tables.append("430.32")

    lrc_table = result.get("lrc_table") or {}
    if lrc_table.get("locked_rotor_current") is not None:
        tables.append(LRC_TABLE_LABELS.get(lrc_table.get("table"), "430.251"))

    if (result.get("lrc_code") or {}).get("locked_rotor_current") is not None:
        tables.append("430.7(B)")

    return ", ".join(tables) if tables else "—"


# ============================================================
# Report-wide text
# ============================================================
def _code_reference(results: list[dict[str, Any]]) -> str:
    return f"Per {_nec_edition()} 430.52(C)(1), 430.32 and 430.110"


def _has_overload(results: list[dict[str, Any]]) -> bool:
    return any((r.get("overload") or {}).get("max_overload") is not None for r in results)


def _has_code_letter(results: list[dict[str, Any]]) -> bool:
    return any((r.get("lrc_code") or {}).get("locked_rotor_current") is not None for r in results)


def _word_reference(doc, results: list[dict[str, Any]]) -> None:
    """Equations used across the calculations in the schedule (Word report only)."""
    doc.add_heading("Equations Used", level=1)

    add_word_equation(
        doc,
        "Branch-circuit device (430.52)",
        omml_sub("I", "branch") + omml_r(" = mult% × ") + omml_sub("I", "FLC"),
    )

    if _has_overload(results):
        add_word_equation(
            doc,
            "Overload protection (430.32)",
            omml_sub("I", "OL") + omml_r(" = k × ") + omml_sub("I", "FLA,nameplate"),
        )

    add_word_equation(
        doc,
        "Disconnecting means (430.110(C)(1))",
        omml_sub("I", "disc") + omml_r(" = 1.15 × ") + omml_sub("I", "FLC"),
    )

    if _has_code_letter(results):
        add_word_equation(
            doc,
            "Locked-rotor current from code letter (430.7(B))",
            omml_sub("I", "LR")
            + omml_r(" = ")
            + omml_frac(
                omml_r("(kVA/hp) × hp × 1000"),
                omml_r("V × ") + omml_sub("k", "φ"),
            ),
        )


def _footnotes(results: list[dict[str, Any]]) -> list[str]:
    edition = _nec_edition()

    notes = [
        f"Per {edition} 430.6(A), branch-circuit sizing uses the full-load current from "
        "Tables 430.247 through 430.250, not the motor nameplate current. Rows whose FLC "
        "source is Nameplate had no table value for the selected horsepower and voltage.",
        "Branch-circuit short-circuit and ground-fault device ratings are the maximums from "
        "Table 430.52(C)(1), shown as the next higher standard rating permitted by Exception "
        "No. 1 (240.6(A)). The instantaneous-trip value is an adjustable setting rather than a "
        "standard rating, so it is shown unrounded.",
        "Exception No. 2 ceilings (permitted only where the table value will not start the "
        "motor) are not shown in this schedule; check them on the calculator before selecting "
        "a device above the table maximum.",
        "The Code Edition and Source Tables columns give the tables each row was read from: "
        "the full-load current table for the system type, Table 430.52(C)(1) for the branch "
        "device, and 430.32, 430.251 and 430.7(B) where those values were calculated.",
    ]

    if _has_overload(results):
        notes.append(
            f"Overload protection is sized per {edition} 430.32 from the marked nameplate "
            "full-load current and service factor / temperature rise. The start allowance is "
            "the 430.32(C) value, permitted only where the base value will not allow the motor "
            "to start or carry the load."
        )

    notes.append(
        f"The minimum disconnecting means rating is 115% of the full-load current per "
        f"{edition} 430.110(C)(1). Locked-rotor currents are for selecting disconnects and "
        "controllers; the Table 430.251 value and the code-letter value are independent bases."
    )

    notes.append(
        "This report is based on the input values entered into the calculator. Final "
        "selections should be verified against the NEC, project specifications, equipment "
        "data, a coordination study where required, and engineering judgement."
    )

    return notes


# ============================================================
# Schedule spec + entry point
# ============================================================
MP_SCHEDULE_SPEC = ReportSpec(
    code="nec",
    calculator="motor_protection",
    report_title="Motor Protection — Calculation Results",
    sheet_name="Motor Protection Schedule",
    tag="Tag / ID",
    input_prefixes=("mp_",),
    cols=[
        Column("System", lambda r: get_first(r, "phase_label", default="—")),
        Column("Motor", _hp),
        Column("Voltage (V)", lambda r: fmt(get_first(r, "voltage"), "V")),
        Column("Motor category", _category),
        Column("I_FLC (A)", lambda r: fmt(get_first(r, "flc"), "A"), result=True),
        Column("FLC source", lambda r: get_first(r, "flc_source", default="—")),
        *[
            column
            for key, header in DEVICE_HEADERS
            for column in (
                Column(f"{header} max (A)", lambda r, key=key: _device(r, key, "raw"),
                       result=True, group=key),
                # An instantaneous-trip breaker is an adjustable setting, not a
                # standard rating, so 240.6(A) supplies nothing to select.
                *([] if key == "instantaneous_trip_breaker" else [
                    Column(f"{header} selected (A)",
                           lambda r, key=key: _device(r, key, "standard"),
                           color="green", result=True, group=key),
                ]),
            )
        ],
        Column("Nameplate FLA (A)", lambda r: fmt(get_first(r, "nameplate_fla"), "A")),
        Column("SF", lambda r: get_first(r, "service_factor_label", default="—")),
        Column("Max overload", lambda r: _overload(r, "max_overload", "factor"), color="green", result=True),
        Column("Start allowance", lambda r: _overload(r, "max_overload_start", "start_factor"), result=True),
        Column("Min disconnect (A)", _disconnect, color="blue", result=True),
        Column("LRC, Table 430.251 (A)", lambda r: _lrc(r, "lrc_table"), result=True, group="lrc"),
        Column("LRC, code letter (A)", lambda r: _lrc(r, "lrc_code"), result=True, group="lrc"),
        Column("Code letter", lambda r: get_first(r, "code_letter", default="—")),
        Column("Code Edition", _edition),
        Column("Source Tables", _source_tables),
    ],
    groups={
        "nontime_delay_fuse": Group("Non-time-delay fuse (A)", " → "),
        "dual_element_time_delay_fuse": Group("Dual-element fuse (A)", " → "),
        "inverse_time_breaker": Group("Inverse-time breaker (A)", " → "),
        "lrc": Group("LRC, table / code letter (A)"),
    },
    code_reference=_code_reference,
    notes=_footnotes,
    word_reference=_word_reference,
)


def render_add_to_schedule(result: dict[str, Any] | None) -> None:
    can_add = result is not None and get_first(result, "flc") is not None
    render_schedule_commit(MP_SCHEDULE_SPEC, result, can_add=can_add)


def render_schedule_section() -> None:
    render_schedule_table(MP_SCHEDULE_SPEC)
