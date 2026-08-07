import streamlit as st

from nec_calc.common.formatting import fmt
from nec_calc.common.ui_helpers import eq

from nec_calc._template.calculation import calc_template
from nec_calc._template.report import render_export_report

TEMPLATE_MODE_OPTIONS = {
    "Example Method": "example_method",
}


METHOD_LABELS = {
    "example_method": "Example Method",
}


def _method_label(template_mode: str) -> str:
    return METHOD_LABELS.get(template_mode, str(template_mode))


def render_calc():
    st.markdown("### Inputs")

    # --------------------
    # CALC MODE
    # --------------------
    template_mode_input = st.radio(
        "Calculation method",
        list(TEMPLATE_MODE_OPTIONS.keys()),
        index=0,
        key="nec_template_mode",
    )
    template_mode = TEMPLATE_MODE_OPTIONS[template_mode_input]

    # --------------------
    # COMMON INPUTS
    # --------------------
    c1, c2 = st.columns(2)

    base_quantity = c1.number_input(
        "Base quantity",
        min_value=0.0,
        value=100.0,
        step=1.0,
        key="nec_template_base_quantity",
    )

    multiplier = c2.number_input(
        "Multiplier",
        min_value=0.0,
        value=1.25,
        step=0.01,
        key="nec_template_multiplier",
    )

    st.divider()
    st.markdown("### Optional Add-Ons")
    show_adder = st.checkbox("Include adder in final calculation", key="nec_template_show_adder")
    
    if show_adder:
        adder = st.number_input(
            "Adder",
            min_value=0.0,
            value=0.0,
            step=1.0,
            key="nec_template_adder",
        )
    else:
        adder = 0.0

    result = calc_template(
        template_mode=template_mode,
        base_quantity=base_quantity,
        multiplier=multiplier,
        adder=adder,
    )

    st.divider()
    st.markdown("### Results")

    m1, m2 = st.columns(2)
    m1.metric("Calculated value", fmt(result["calculated_value"], " units"))
    m2.metric("Intermediate value", fmt(result["intermediate_value"], " units"))

    st.markdown("### Parameters used")
    st.write(f"- calculation method: **{_method_label(template_mode)}**")
    st.write(f"- base quantity: **{fmt(result['base_quantity'], ' units')}**")
    st.write(f"- multiplier: **{fmt(result['multiplier'])}**")
    if show_adder:
        st.write(f"- adder: **{fmt(result['adder'], ' units')}**")

    st.markdown("### Equations used")
    eq(r"X_{intermediate}=A\cdot M")
    eq(r"X_{final}=X_{intermediate}+B")

    st.divider()

    render_export_report(
        result=result,
        template_mode=template_mode,
    )
