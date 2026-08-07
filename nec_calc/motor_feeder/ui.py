from fractions import Fraction

import streamlit as st

from lib.nec_tables import TABLES
from nec_calc.common.enums import ConductorMaterial, ServiceFactors, SystemTypes
from nec_calc.common.formatting import fmt, format_cond_size
from nec_calc.common.table_helpers import get_row_headers
from nec_calc.common.ui_helpers import enum_selectbox, eq

from nec_calc.motor_feeder.calculation import (
    calc_motor_feeder,
    get_appropriate_table,
    get_valid_voltages,
)
from nec_calc.motor_feeder.report import render_export_report

TEMP_RATINGS = {"60 °C": 60, "75 °C": 75, "90 °C": 90}

MULT_OPTIONS = {
    "1.25 — Continuous duty single motor (NEC 430.22)": 1.25,
    "1.15 — Intermittent duty / 15-minute rating (NEC Table 430.22(E))": 1.15,
    "1.50 — Periodic duty (NEC Table 430.22(E))": 1.50,
    "1.00 — Short-time / non-continuous duty": 1.00,
}

def overload_sizing():
    if "np_fla" in st.session_state:
        st.session_state["np_fla"] = None
        st.session_state["sf"] = None

def get_hp_list(phase):
    rows = TABLES.get(get_appropriate_table(phase)).get("rows")
    hp_list = get_row_headers(rows, "horsepower")
    return { 
        float(sum(Fraction(s) for s in str(item).split())): str(item) 
        for item in hp_list 
    } 
    
        
def phase_change():
    st.session_state["hp_list"] = get_hp_list(st.session_state.get("phase").key)
    
    if st.session_state.get("phase") == SystemTypes.DC.key:
        st.session_state["v_idx"] = 2   # change these indexes to set default values
        st.session_state["hp_idx"] = 2  # change these indexes to set default values
    elif st.session_state.get("phase") == SystemTypes.SINGLE_PHASE:
        st.session_state["v_idx"] = 2   # change these indexes to set default values
        st.session_state["hp_idx"] = 2  # change these indexes to set default values
    elif st.session_state.get("phase") == SystemTypes.THREE_PHASE:
        st.session_state["v_idx"] = 4 #sets default voltage to 460 V
        st.session_state["hp_idx"] = 11 # sets default hp to 25
    

def render_calc():
    st.markdown("### Inputs")
    
    if "v_idx" not in st.session_state:
        st.session_state["v_idx"] = 4
    if "hp_idx" not in st.session_state:
        st.session_state["hp_idx"] = 11
    if "phase" not in st.session_state:
        st.session_state["phase"] = SystemTypes.THREE_PHASE

    hp_list = get_hp_list(st.session_state["phase"].key)

    c1, c2= st.columns(2)
    phase = enum_selectbox(c1, "Phase", SystemTypes, index=2, on_change=phase_change, key="phase")
    hp = enum_selectbox(c2, "Horsepower (HP)", options=hp_list, format_func=lambda m: hp_list.get(m), index=st.session_state["hp_idx"])

    m_type = None  # Feeder conductor sizing uses the induction full-load currents.

    voltages = get_valid_voltages(phase.key, hp_list.get(hp), m_type)
    v_idx = min(st.session_state["v_idx"], len(voltages) - 1) if voltages else 0
    v = c2.selectbox("Voltage (V)", options=voltages, index=v_idx) if voltages else None

    mult = enum_selectbox(c1, "Sizing multiplier (NEC 430.22 / 430.22(E))", MULT_OPTIONS)

    material = enum_selectbox(c1, "Conductor material", ConductorMaterial.exclude(ConductorMaterial.NA), index=1)
    temp_label = enum_selectbox(c2, "Insulation temp rating (Table 310.16)", TEMP_RATINGS, index=1)

    with c1.expander("Optional (Overload Sizing)", on_change=overload_sizing, key="overload_sizing_expander"):
        np_fla = st.number_input("Nameplate FLA (A)", min_value=0.1, value=None, step=0.1, placeholder=27.5, key="np_fla")
        sf = enum_selectbox(st, "Service Factor", ServiceFactors, key="sf")

    if v is None:
        st.warning("NEC Tables 430.247–430.250 list no full-load current for this HP / motor type. Enter a nameplate FLA or choose a different motor.")

    result = calc_motor_feeder(
        phase=phase.key,
        phase_label=phase.label,
        hp=hp,
        hp_label=hp_list.get(hp),
        voltage=v,
        motor_type=m_type,
        sizing_factor=MULT_OPTIONS[mult],
        sizing_factor_label=mult,
        nameplate_fla=np_fla,
        service_factor=sf.key if sf else None,
        service_factor_label=sf.label if sf else None,
        material=material.key,
        material_label=material.label,
        temp_rating=TEMP_RATINGS[temp_label],
    )

    st.divider()
    st.markdown("### Results")

    m1, m2, m3 = st.columns(3)
    m1.metric("Feeder conductor ampacity (A)", fmt(result["conductor_ampacity"], "A"))
    if result.get("conductor_size") is not None:
        m2.metric(
            "Minimum conductor size (Table 310.16)",
            format_cond_size(result["conductor_size"]),
            help=f"{result['material_label']}, {result['temp_rating']} °C column — "
                 f"rated {fmt(result['conductor_size_ampacity'], 'A')}",
        )
    elif result.get("conductor_ampacity") is not None:
        m2.metric("Minimum conductor size (Table 310.16)", "—")
        m2.caption("Required ampacity exceeds Table 310.16.")
    m3.metric("Max overload protection (A)", fmt(result["max_overload"], "A"))

    st.markdown("### Parameters used")

    st.write(f"- system: **{result['phase_label']}**")
    st.write(f"- motor size: **{result['hp_label']} HP**")
    if result.get("motor_type"):
        st.write(f"- motor type: **{result['motor_type']}**")
    st.write(f"- voltage: **{fmt(result['voltage'], 'V')}**")
    st.write(
        f"- full-load current (I_FLC): **{fmt(result['flc'], 'A')}** "
        f"({result['flc_source'] or '—'})"
    )
    st.write(f"- conductor sizing factor k: **{result['sizing_factor_label']}**")
    st.write(f"- conductor: **{result['material_label']}**, **{result['temp_rating']} °C** (Table 310.16)")
    if result.get("nameplate_fla") is not None:
        st.write(f"- nameplate FLA: **{fmt(result['nameplate_fla'], 'A')}**")
    if result.get("service_factor_label"):
        st.write(f"- service factor: **{result['service_factor_label']}**")

    st.markdown("### Equations used")
    eq(r"I_{cond}=k\cdot I_{FLC}")
    if result.get("max_overload") is not None:
        eq(r"I_{OL}=SF\cdot I_{FLA,nameplate}")

    st.divider()

    render_export_report(result=result)
