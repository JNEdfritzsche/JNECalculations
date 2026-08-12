import streamlit as st

from calc_common.formatting import fmt
from calc_common.ui_helpers import eq

from oesc_calc.voltage_drop.calculation import (
    CIRCUIT_TYPES,
    DC,
    DC_CIRCUIT_TYPES,
    LOCATIONS,
    MATERIALS,
    PF_CHOICES,
    TEMPERATURES,
    calc_voltage_drop,
    conductor_sizes,
)
from oesc_calc.voltage_drop.report import render_add_to_schedule, render_schedule_section


@st.fragment
def render_calc():
    inputs_pane, result_pane = st.columns([1.45, 1], gap="large")

    with inputs_pane, st.container(border=True):
        st.markdown("### Inputs")

        k_mode = st.radio(
            "k-value input mode",
            ("Lookup k-value from Table D3 (recommended)", "Manual k-value (enter value)"),
            index=0,
            key="oesc_voltage_drop_k_mode",
        )
        use_table = k_mode.startswith("Lookup")

        c1, c2 = st.columns(2)
        current = c1.number_input("Load current (A)", min_value=0.0, value=50.0, step=0.1,
                                  key="oesc_voltage_drop_current")
        length_m = c2.number_input("One-way length (m)", min_value=0.0, value=80.0, step=1.0,
                                   key="oesc_voltage_drop_length")

        c1, c2 = st.columns(2)
        v_nom = c1.number_input("Nominal voltage (V)", min_value=1.0, value=600.0, step=1.0,
                                key="oesc_voltage_drop_vnom")
        n_parallel = c2.number_input("Parallel conductors per phase/pole", min_value=1, value=1, step=1,
                                     key="oesc_voltage_drop_parallel")

        material = location = size = None
        pf_choice = "100% pf"
        manual_k = None

        if use_table:
            c1, c2 = st.columns(2)
            material = c1.selectbox("Conductor material (table to use)", MATERIALS, index=0,
                                    key="oesc_voltage_drop_material")
            location = c2.selectbox("Installation (table column family)", LOCATIONS, index=0,
                                    key="oesc_voltage_drop_location")

            c1, c2 = st.columns(2)
            if location != DC:
                pf_choice = c1.selectbox("Power-factor column (for Cable/Raceway)", PF_CHOICES, index=0,
                                         key="oesc_voltage_drop_pf")
            else:
                st.caption("Power-factor selection hidden for DC — DC uses the 'DC' column in Table D3.")

            sizes = conductor_sizes(material)
            default_index = sizes.index("1000") if material == "Copper" and "1000" in sizes else 0
            size = c2.selectbox("Select conductor size (Table D3)", sizes, index=default_index,
                                key=f"oesc_voltage_drop_size_{material}")
        else:
            st.caption("Manual k-value mode: table lookup controls are hidden. Enter k directly in Ω/km below.")
            manual_k = st.number_input("Manual k-value (Ω/km)", min_value=0.0, value=0.10, step=0.00001,
                                       format="%.6f", key="oesc_voltage_drop_manual_k")

        c1, _ = st.columns(2)
        operating_temp_c = c1.selectbox(
            "Conductor operating temperature (°C)", TEMPERATURES, index=1,
            format_func=lambda t: f"{t}°C", key="oesc_voltage_drop_temp",
        )

        options = DC_CIRCUIT_TYPES if location == DC else CIRCUIT_TYPES
        default_f_index = 0 if location == DC else 4
        circuit = st.selectbox(
            "Voltage-drop factor (f) — select circuit type", options,
            format_func=lambda x: x[0], index=default_f_index,
            key=f"oesc_voltage_drop_circuit_{'dc' if location == DC else 'all'}",
        )

        result = calc_voltage_drop(
            current=current,
            length_m=length_m,
            v_nom=v_nom,
            n_parallel=n_parallel,
            operating_temp_c=operating_temp_c,
            f_factor=float(circuit[1]),
            f_label=circuit[0],
            use_table=use_table,
            material=material,
            location=location,
            pf_choice=pf_choice,
            size=size,
            manual_k=manual_k,
        )

    with result_pane, st.container(border=True):
        st.markdown("### Results")

        if result["k_base"] is None:
            st.error(
                f"Table D3 has no k-value for {result['material']} {result['size']} in the "
                f"{result['column_label']} column."
            )
        elif result["voltage_drop"] is None:
            st.info("Enter positive current, length and voltage to compute voltage drop.")
        else:
            m1, m2 = st.columns(2)
            m1.metric("Estimated voltage drop", fmt(result["voltage_drop"], "V"))
            m2.metric("Voltage drop (%)", fmt(result["percent_drop"], "%"))

            if result["percent_drop"] > 3.0:
                st.warning("Over the 3% branch-circuit limit of Rule 8-102.")

        st.divider()
        render_add_to_schedule(result)

        with st.expander("Parameters & equations used", expanded=False):
            st.markdown("### Parameters used")
            if result["k_base"] is not None:
                st.write(f"- k base (75°C): **{result['k_base']:.6g} Ω/km** "
                         f"(column **{result['column_label']}**)")
                st.write(f"- operating temperature: **{result['operating_temp_c']}°C** "
                         f"→ multiplier **{result['k_temp_multiplier']:.2f}**")
                st.write(f"- k used: **{result['k_used']:.6g} Ω/km**")
            st.write(f"- factor f: **{result['f']:.6g}** ({result['f_label']})")
            st.write(f"- I = **{fmt(result['current'], 'A')}**, L = **{fmt(result['length_m'], 'm')}**, "
                     f"Vnom = **{fmt(result['v_nom'], 'V')}**")
            st.write(f"- parallel conductors: **{result['n_parallel']}** "
                     f"→ I per conductor = **{fmt(result['I_eff'], 'A')}**")

            st.markdown("### Equations used")
            eq(r"I_{eff}=\frac{I}{N_{parallel}}")
            eq(r"V_D=\frac{k\cdot f\cdot I_{eff}\cdot L}{1000}")
            eq(r"\%\Delta V = 100\cdot\frac{V_D}{V_{nom}}")

    st.divider()
    render_schedule_section()
