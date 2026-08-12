from calc_common.physics import calc_flas, transformer_type, turns_ratio


def _build_calc_result(calc, **inputs):
    return {
        **inputs,
        **calc,
    }

def calc_transformer_feeder(
    phase,
    current_factor,
    transformer_rating,
    V_data: dict[str, float],
):
    V_pri = V_data["V_primary"]
    V_sec = V_data["V_secondary"]

    inputs = {
        "phase": phase,
        "current_factor": current_factor,
        "transformer_rating": transformer_rating,
        "V_data": V_data,
    }

    calc = {
        **calc_flas(inputs),
        "turns_ratio": turns_ratio(V_pri, V_sec),
        "transformer_type": transformer_type(phase, V_pri, V_sec),
    }

    return _build_calc_result(
        calc=calc,
        phase=phase,
        transformer_rating=transformer_rating,
        V_primary=V_data["V_primary"],
        V_secondary=V_data["V_secondary"],
    )
