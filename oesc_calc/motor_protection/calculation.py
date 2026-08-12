from __future__ import annotations

from typing import Any

from lib import oesc_tables

DEVICE_TYPES = {
    "TD": ("Time-delay fuse (TD)", "Maximum fuse rating — Time-delay* fuses"),
    "NTD": ("Non-time-delay fuse (NTD)", "Maximum fuse rating — Non-time-delay"),
    "CB": ("Inverse-time circuit breaker (CB)", "Maximum setting — Inverse-time circuit breaker"),
}

SINGLE_PHASE = "1Φ AC"
THREE_PHASE = "3Φ AC"
DC = "DC"

WOUND_ROTOR = "Wound Rotor"
SQUIRREL_CAGE = "Squirrel-cage or Synchronous"

AUTO_TX = "Auto-TX or Star-Delta"
FULL_VOLTAGE = "Full-voltage, resistor and reactor starting"

AUTO_TX_FLA_BREAK = 30.0


def select_table_29_row(
    fla: float,
    voltage_system: str,
    motor_type: str | None,
    starter_type: str | None,
) -> tuple[int, str]:
    if voltage_system == SINGLE_PHASE:
        return 1, "1Φ AC (Row 1)"
    if voltage_system == DC:
        return 6, "DC (Row 6)"
    if motor_type == WOUND_ROTOR:
        return 5, "Wound Rotor (Row 5)"
    if starter_type == FULL_VOLTAGE:
        return 2, "FV&R (Row 2)"
    if fla > AUTO_TX_FLA_BREAK:
        return 4, "Auto-TX or Star-Delta, FLA > 30A (Row 4)"
    return 3, "Auto-TX or Star-Delta, FLA ≤ 30A (Row 3)"


def table_29_entry(row: int, device: str) -> tuple[float | None, str | None]:
    rows = oesc_tables.TABLE_29["rows"]
    if not 1 <= row <= len(rows):
        return None, None

    table_row = rows[row - 1]
    percent = table_row.get(DEVICE_TYPES[device][1])
    if percent is None:
        return None, table_row.get("Type of motor")
    return percent / 100.0, table_row.get("Type of motor")


def prev_standard(value: float | None, ratings: list[int]) -> int | None:
    if value is None:
        return None
    try:
        target = float(value)
    except (TypeError, ValueError):
        return None

    for rating in reversed(ratings):
        if rating <= target:
            return rating
    return None


def flowchart_path(voltage_system: str, motor_type: str | None, starter_type: str | None, fla: float) -> str:
    path = f"Voltage system: {voltage_system}"
    if voltage_system == THREE_PHASE:
        path += f" → Motor type: {motor_type}"
        if motor_type == SQUIRREL_CAGE:
            path += f" → Starter type: {starter_type}"
            if starter_type == AUTO_TX:
                path += f" → FLA {'>' if fla > AUTO_TX_FLA_BREAK else '≤'} 30A"
    return path


def calc_motor_protection(
    fla: float,
    voltage_system: str,
    motor_type: str | None,
    starter_type: str | None,
    device: str,
) -> dict[str, Any]:
    table_29_row, table_29_row_desc = select_table_29_row(fla, voltage_system, motor_type, starter_type)
    multiplier, row_description = table_29_entry(table_29_row, device)

    ocpd_raw = None if multiplier is None else fla * multiplier
    selected_std = prev_standard(ocpd_raw, oesc_tables.STANDARD_DEVICE_RATINGS)

    return {
        "fla": fla,
        "voltage_system": voltage_system,
        "motor_type": motor_type,
        "starter_type": starter_type,
        "device": device,
        "device_label": DEVICE_TYPES[device][0],
        "table_29_row": table_29_row,
        "table_29_row_desc": table_29_row_desc,
        "row_description": row_description,
        "multiplier": multiplier,
        "ocpd_raw": ocpd_raw,
        "selected_std": selected_std,
        "flowchart_path": flowchart_path(voltage_system, motor_type, starter_type, fla),
        "primary_table": "29",
        "source_tables": ["29", "13"],
    }
