import streamlit as st

from calc_common.report_schedule import apply_restore
from calc_common.enums import SystemTypes
from calc_common.formatting import fmt
from calc_common.ui_helpers import eq, transformer_feeder_inputs

from nec_calc.transformer_feeder.calculation import calc_transformer_feeder
from nec_calc.transformer_feeder.report import (
    TF_SCHEDULE_SPEC,
    render_add_to_schedule,
    render_schedule_section,
)

@st.fragment
def render_calc():
    apply_restore(TF_SCHEDULE_SPEC)

    inputs_pane, result_pane = st.columns([1.45,1], gap="large")
    
    with inputs_pane, st.container(border=True):
        st.markdown("### Inputs")
        inputs = transformer_feeder_inputs(key_prefix="nec_tf")
        
        result = calc_transformer_feeder(**inputs)

    with result_pane, st.container(border=True):
        st.markdown("### Results")

        m1, m2, m3 = st.columns(3)
        m1.metric("Primary Full-Load Current", fmt(result["primary_fla"]) + " A")
        m2.metric("Secondary Full-Load Current", fmt(result["secondary_fla"]) + " A")
        m3.metric("Turns Ratio (V1/V2)", fmt(result["turns_ratio"]))
        st.caption(f"**Transformer Type:** {result["transformer_type"]} Transformer")
        
        st.divider()
        render_add_to_schedule(result)  
        
        with st.expander("Parameters & equations used", expanded=False):
            st.markdown("### Equations used")   
            
            if result["phase"] == SystemTypes.THREE_PHASE.key:
                eq(r"I=\frac{S}{\sqrt{3}\,V}")
            else:
                eq(r"I=\frac{S}{V}")
                
            eq(r"\text{Turns Ratio}=\frac{V_1}{V_2}=\frac{N_1}{N_2}=\frac{I_2}{I_1}")
    
    st.divider()
    render_schedule_section()
