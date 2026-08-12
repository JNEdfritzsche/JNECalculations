import streamlit as st

from calc_common.formatting import fmt
from calc_common.ui_helpers import eq
from content.charts.flowcharts import get_oesc_transformer_protection_flowchart

from oesc_calc.transformer_protection.calculation import (
    DRY,
    INRUSH_CHECKS,
    OVER_750,
    PHASES,
    PRIMARY_ONLY,
    PROTECTION_CONFIGS,
    THREE_PHASE,
    TRANSFORMER_TYPES,
    UPTO_750,
    VOLTAGE_CLASSES,
    calc_transformer_protection,
    oil_primary_multiplier,
)
from oesc_calc.transformer_protection.report import render_add_to_schedule, render_schedule_section


def _show_device(entry: dict, round_to_std: bool) -> None:
    label, raw, selected = entry["label"], entry["raw"], entry["selected"]
    if not round_to_std:
        st.success(f"{label}: **{fmt(raw, 'A')}**")
    elif selected is None:
        st.error(f"{label}: Raw = **{fmt(raw, 'A')}** → exceeds standard list. Enter final device manually.")
    else:
        st.success(f"{label}: Raw = **{fmt(raw, 'A')}** → Selected standard = **{fmt(selected, 'A')}**")


@st.fragment
def render_calc():
    st.markdown("### Transformer Protection Flowchart")
    st.graphviz_chart(get_oesc_transformer_protection_flowchart())
    st.caption("NOTE: P&S denotes direct secondary protection and **upstream** primary protection.")

    inputs_pane, result_pane = st.columns([1.45, 1], gap="large")

    with inputs_pane, st.container(border=True):
        st.markdown("### Inputs")

        c1, c2 = st.columns(2)
        phase = c1.selectbox("System", PHASES, index=0, key="oesc_transformer_protection_phase")
        kva = c2.number_input("Transformer size (kVA)", min_value=0.1, value=75.0, step=1.0,
                              key="oesc_transformer_protection_kva")

        c1, c2 = st.columns(2)
        vpri = c1.number_input("Primary voltage (V)", min_value=1.0, value=600.0, step=1.0,
                               key="oesc_transformer_protection_vpri")
        vsec = c2.number_input("Secondary voltage (V)", min_value=1.0, value=208.0, step=1.0,
                               key="oesc_transformer_protection_vsec")

        st.caption(
            "Units note: this calculator assumes kVA and volts. For 3Φ it uses line-to-line "
            "voltage. Use nameplate FLA when available."
        )

        use_nameplate = st.checkbox(
            "Use nameplate FLA instead of calculating from kVA/V", value=False,
            key="oesc_transformer_protection_use_nameplate",
        )

        nameplate_ip = nameplate_is = None
        if use_nameplate:
            c1, c2 = st.columns(2)
            nameplate_ip = c1.number_input("Nameplate Primary FLA (A)", min_value=0.01, value=72.0, step=0.01,
                                           key="oesc_transformer_protection_ip")
            nameplate_is = c2.number_input("Nameplate Secondary FLA (A)", min_value=0.01, value=208.0, step=0.01,
                                           key="oesc_transformer_protection_is")

        st.markdown("#### Code-based OCPD limits")

        c1, c2 = st.columns(2)
        xfmr_type = c1.selectbox("Transformer type", TRANSFORMER_TYPES, index=0,
                                 key="oesc_transformer_protection_type")
        voltage_class = c2.selectbox(
            "Voltage class selection", VOLTAGE_CLASSES,
            index=1 if vpri <= 750 else 0,
            key="oesc_transformer_protection_vclass",
        )

        prot_config = st.radio("Protection configuration", PROTECTION_CONFIGS, horizontal=True, index=0,
                               key="oesc_transformer_protection_config")

        z_pct = None
        if voltage_class == OVER_750 and prot_config != PRIMARY_ONLY:
            c1, _ = st.columns(2)
            z_pct = c1.number_input(
                "Transformer impedance Z (%)", min_value=0.01, value=6.0, step=0.1, format="%.2f",
                help="Nameplate impedance. Determines which Table 50 column applies (Z ≤ 7.5% or 7.5% < Z ≤ 10%).",
                key="oesc_transformer_protection_z",
            )

        round_to_std = st.checkbox("Round up to standard rating (Table 13 style)", value=True,
                                   key="oesc_transformer_protection_round")

        result = calc_transformer_protection(
            phase=phase,
            kva=kva,
            vpri=vpri,
            vsec=vsec,
            xfmr_type=xfmr_type,
            voltage_class=voltage_class,
            prot_config=prot_config,
            z_pct=z_pct,
            round_to_std=round_to_std,
            use_nameplate=use_nameplate,
            nameplate_ip=nameplate_ip,
            nameplate_is=nameplate_is,
        )

    with result_pane, st.container(border=True):
        st.markdown("### Results")

        m1, m2 = st.columns(2)
        m1.metric("Primary FLA", fmt(result["Ip"], "A"))
        m2.metric("Secondary FLA", fmt(result["Is"], "A"))

        st.caption(f"Rule path: **{result['rule_path']}**")

        if result["error"]:
            st.error(result["error"])
        else:
            for entry in result["devices"]:
                _show_device(entry, round_to_std)

        if result.get("inrush_12x") is not None:
            st.markdown("**Inrush withstand checks:**")
            for factor, seconds in INRUSH_CHECKS:
                st.write(f"{factor}× FLA for {seconds} s: **{fmt(result['Ip'] * factor, 'A')}**")
            st.caption("Verify manufacturer curves to confirm withstand/ride-through capability.")

        st.divider()
        render_add_to_schedule(result)

        with st.expander("Parameters & equations used", expanded=False):
            st.markdown("### Parameters used")
            st.write(f"- system: **{result['phase']}**")
            st.write(f"- transformer: **{fmt(result['kva'], 'kVA')}**, "
                     f"**{fmt(result['vpri'], 'V')}** → **{fmt(result['vsec'], 'V')}**")
            st.write(f"- transformer type: **{result['xfmr_type']}**")
            st.write(f"- voltage class: **{result['voltage_class']}**")
            st.write(f"- protection configuration: **{result['prot_config']}**")
            if result["z_pct"] is not None:
                st.write(f"- rated impedance: **{result['z_pct']:g} %**")
            st.write(f"- FLA source: **{'Nameplate' if result['use_nameplate'] else 'Calculated'}**")

            if (result["voltage_class"] == UPTO_750 and result["xfmr_type"] != DRY
                    and result["prot_config"] == PRIMARY_ONLY and result["Ip"] is not None):
                st.caption(oil_primary_multiplier(result["Ip"])[2])

            st.markdown("### Equations used")
            if not result["use_nameplate"]:
                if result["phase"] == THREE_PHASE:
                    eq(r"I=\frac{kVA\cdot 1000}{\sqrt{3}\cdot V}")
                else:
                    eq(r"I=\frac{kVA\cdot 1000}{V}")
            eq(r"I_{OCPD,max}=\text{mult}\%\times I_{FLC}")

    st.divider()
    render_schedule_section()
