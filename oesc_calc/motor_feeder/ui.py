import streamlit as st

from calc_common.formatting import fmt
from calc_common.report_schedule import apply_restore
from calc_common.ui_helpers import eq

from oesc_calc.motor_feeder.calculation import (
    DC,
    HP,
    KW,
    POWER_UNITS,
    SIZING_FACTORS,
    SYSTEMS,
    THREE_PHASE,
    calc_motor_feeder,
)
from oesc_calc.motor_feeder.report import (
    MF_SCHEDULE_SPEC,
    render_add_to_schedule,
    render_schedule_section,
)


def _render_equations(result: dict) -> None:
    st.markdown("### Equations used")

    if result["power_unit"] == KW:
        if result["phase"] == THREE_PHASE:
            eq(r"I_{FLA}=\frac{kW\cdot 1000}{\sqrt{3}\cdot V_{LL}\cdot \cos\theta\cdot \eta}")
        elif result["phase"] == DC:
            eq(r"I_{FLA}=\frac{kW\cdot 1000}{V\cdot \eta}")
        else:
            eq(r"I_{FLA}=\frac{kW\cdot 1000}{V\cdot \cos\theta\cdot \eta}")
    else:
        if result["phase"] == THREE_PHASE:
            eq(r"I_{FLA}=\frac{HP\cdot 745.7}{\sqrt{3}\cdot V_{LL}\cdot \cos\theta\cdot \eta}")
        elif result["phase"] == DC:
            eq(r"I_{FLA}=\frac{HP\cdot 745.7}{V\cdot \eta}")
        else:
            eq(r"I_{FLA}=\frac{HP\cdot 745.7}{V\cdot \cos\theta\cdot \eta}")

    eq(r"I_{target}=k\cdot I_{FLA}")


@st.fragment
def render_calc():
    apply_restore(MF_SCHEDULE_SPEC)

    inputs_pane, result_pane = st.columns([1.45, 1], gap="large")

    with inputs_pane, st.container(border=True):
        st.markdown("### Inputs")

        c1, c2 = st.columns(2)

        phase = c1.selectbox("System", SYSTEMS, index=0, key="oesc_motor_feeder_phase")
        power_unit = c2.selectbox("Power unit", POWER_UNITS, index=0, key="oesc_motor_feeder_power_unit")

        c1, c2 = st.columns(2)

        if power_unit == HP:
            power_value = c1.number_input(
                "Motor power (HP)", min_value=0.1, value=25.0, step=0.1,
                key="oesc_motor_feeder_hp",
            )
        else:
            power_value = c1.number_input(
                "Motor power (kW)", min_value=0.001, value=18.65, step=0.001,
                key="oesc_motor_feeder_kw",
            )

        volts = c2.number_input(
            "Voltage (V)", min_value=1.0, value=600.0, step=1.0,
            help="Use line-to-line voltage for 3-phase motors.",
            key="oesc_motor_feeder_volts",
        )

        c1, c2 = st.columns(2)

        if phase == DC:
            pf = 1.0
            c1.text_input("Power factor (cosθ)", value="N/A (DC)", disabled=True,
                          key="oesc_motor_feeder_pf_dc")
        else:
            pf = c1.number_input(
                "Power factor (cosθ)", min_value=0.10, max_value=1.00, value=0.90, step=0.01,
                key="oesc_motor_feeder_pf",
            )

        eff = c2.number_input(
            "Efficiency (%)", min_value=1.0, max_value=100.0, value=92.0, step=0.1,
            key="oesc_motor_feeder_eff",
        )

        c1, _ = st.columns(2)
        sizing_mult = c1.selectbox(
            "Conductor sizing factor", SIZING_FACTORS, index=2,
            help="Rule 28-106 requires 125% for a continuous-duty single motor.",
            key="oesc_motor_feeder_mult",
        )

        result = calc_motor_feeder(
            phase=phase,
            power_unit=power_unit,
            power_value=power_value,
            volts=volts,
            pf=pf,
            eff=eff,
            sizing_mult=sizing_mult,
        )

    with result_pane, st.container(border=True):
        st.markdown("### Results")

        m1, m2 = st.columns(2)
        m1.metric("Calculated I_FLA (A)", fmt(result["ifla"], "A"))
        m2.metric("Conductor ampacity target (A)", fmt(result["target"], "A"))
        st.caption(
            f"Rule 28-106 — conductor ampacity of at least {result['sizing_factor']:g}× the "
            "full-load current."
        )

        st.divider()
        render_add_to_schedule(result)

        with st.expander("Parameters & equations used", expanded=False):
            st.markdown("### Parameters used")
            st.write(f"- system: **{result['phase']}**")
            st.write(f"- motor power: **{result['power_value']:g} {result['power_unit']}** "
                     f"(**{fmt(result['watts'], 'W')}**)")
            st.write(f"- voltage: **{fmt(result['volts'], 'V')}**")
            if result["pf"] is not None:
                st.write(f"- power factor: **{result['pf']}**")
            st.write(f"- efficiency: **{result['eff']:g} %**")
            st.write(f"- sizing factor k: **{result['sizing_factor']:g}**")

            _render_equations(result)

    st.divider()
    render_schedule_section()
