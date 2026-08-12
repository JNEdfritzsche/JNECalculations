from calc_common.physics import calc_flas

# ----------------------------
# results helper functions
# ----------------------------

def _build_calc_result(calc, **inputs):
    return {
        **inputs,
        **calc,
    }

# ----------------------------
# calculator helper functions
# ----------------------------

def _turns_ratio(V_1, V_2):
    return V_1 / V_2

def _transformer_type(phase, V_1, V_2):
    if phase == "three_phase":
        ph = "Three-phase"
    else:
        ph = "Single-phase"
    if V_1 > V_2:
        type = "Step-down"
    elif V_1 < V_2:
        type = "Step-up"
    else:
        type = "Isolation (1:1)"
    
    return ph + " " + type
        

# ----------------------------
# main calculator function
# ----------------------------
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
        "turns_ratio": _turns_ratio(V_pri, V_sec),
        "transformer_type": _transformer_type(phase, V_pri, V_sec),
    }
    
    return _build_calc_result(
        calc=calc,
        phase=phase,
        transformer_rating=transformer_rating,
        V_primary=V_data["V_primary"],
        V_secondary=V_data["V_secondary"],
    )
