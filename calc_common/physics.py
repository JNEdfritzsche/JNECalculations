from __future__ import annotations

from typing import Any


def _rated_current(S, V_L, phase_factor):
    return abs(S / (V_L * phase_factor))

def calc_fla(S, phase_factor, voltage):
    return _rated_current(S, voltage, phase_factor)

def calc_flas(inputs: dict[str, Any]) -> dict[str, float]:
    fla = {}
    for v_key, v_val in inputs["V_data"].items():
        key = "primary_fla" if "primary" in v_key else "secondary_fla" if "secondary" in v_key else "fla"

        fla[key] = calc_fla(
            inputs["transformer_rating"],
            inputs["current_factor"],
            v_val,
        )

    return fla
