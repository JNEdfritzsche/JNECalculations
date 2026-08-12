from __future__ import annotations

import math
from typing import Any

THREE_PHASE = "3-phase"
SINGLE_PHASE = "1-phase"
DC = "DC motor"

SYSTEMS = (THREE_PHASE, SINGLE_PHASE, DC)

HP = "HP"
KW = "kW"
POWER_UNITS = (HP, KW)

WATTS_PER_HP = 745.7

SIZING_FACTORS = ("1.00", "1.15", "1.25")


def input_watts(power_value: float, power_unit: str) -> float:
    return power_value * WATTS_PER_HP if power_unit == HP else power_value * 1000.0


def phase_factor(phase: str) -> float:
    return math.sqrt(3) if phase == THREE_PHASE else 1.0


def full_load_current(
    watts: float,
    phase: str,
    volts: float,
    pf: float,
    eff: float,
) -> float | None:
    if phase == DC:
        denom = volts * (eff / 100.0)
    else:
        denom = phase_factor(phase) * volts * pf * (eff / 100.0)
    return watts / denom if denom > 0 else None


def calc_motor_feeder(
    phase: str,
    power_unit: str,
    power_value: float,
    volts: float,
    pf: float,
    eff: float,
    sizing_mult: str,
) -> dict[str, Any]:
    watts = input_watts(power_value, power_unit)
    ifla = full_load_current(watts, phase, volts, pf, eff)
    factor = float(sizing_mult)
    target = ifla * factor if ifla is not None else None

    return {
        "phase": phase,
        "power_unit": power_unit,
        "power_value": power_value,
        "volts": volts,
        "pf": None if phase == DC else pf,
        "eff": eff,
        "watts": watts,
        "sizing_mult": sizing_mult,
        "sizing_factor": factor,
        "ifla": ifla,
        "target": target,
        "primary_table": None,
        "source_tables": [],
    }
