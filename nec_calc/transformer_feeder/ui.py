import streamlit as st

from nec_calc.common.enums import SystemTypes
from nec_calc.common.formatting import fmt
from nec_calc.common.ui_helpers import eq, transformer_feeder_inputs

from nec_calc.transformer_feeder.calculation import calc_transformer_feeder
from nec_calc.transformer_feeder.report import render_export_report

def render_calc():
    st.markdown("### Inputs")
    inputs = transformer_feeder_inputs()
    
    result = calc_transformer_feeder(**inputs)

    st.divider()
    st.markdown("### Results")

    m1, m2, m3 = st.columns(3)
    m1.metric("Primary Full-Load Current", fmt(result["primary_fla"]) + " A")
    m2.metric("Secondary Full-Load Current", fmt(result["secondary_fla"]) + " A")
    m3.metric("Turns Ratio (V1/V2)", fmt(result["turns_ratio"]))
    st.write(f"**Transformer Type:** {result["transformer_type"]} Transformer")

    st.markdown("### Equations used")   
    
    if result["phase"] == SystemTypes.THREE_PHASE.key:
        eq(r"I=\frac{S}{\sqrt{3}\,V}")
    else:
        eq(r"I=\frac{S}{V}")
        
    eq(r"\text{Turns Ratio}=\frac{V_1}{V_2}=\frac{N_1}{N_2}=\frac{I_2}{I_1}")

    st.divider()

    render_export_report(
        result=result,
    )