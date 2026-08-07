from typing import Any

import streamlit as st

from nec_calc.common.enums import (
    ConductorMaterial,
    ConduitMaterial,
    CopperCoating,
    SystemTypes,
    VDMode,
)

from nec_calc.common.formatting import fmt
from nec_calc.common.ui_helpers import enum_radio, enum_selectbox, eq
from nec_calc.common.units import Current, Voltage

from lib.nec_tables import (
    TABLE_9_LOOKUP_KEYS_kft,
    get_standard_conductor_sizes_t8,
    get_standard_conductor_sizes_t9,
    get_table9_row,
)

from nec_calc.voltage_drop.calculation import calc_voltage_drop
from nec_calc.voltage_drop.report import render_export_report

def enum_key(value):
    return value.key if value is not None else None

def enum_label(value):
    return value.label if value is not None else None


def _table9_has_value(size_label: str, conductor_material_key: str, conduit_material_key: str) -> bool:
    size_num, _size_unit = size_label.split()

    row = get_table9_row({"size_awg_kcmil": size_num})
    if row is None:
        return False

    col = TABLE_9_LOOKUP_KEYS_kft["impedance_map"][conductor_material_key][conduit_material_key]
    return row.get(col) is not None


def reset_to_default(cb_key: str, D: dict[str, Any]):
    if not st.session_state.get(cb_key, False):
        for key in D.keys():
            st.session_state[key] = D[key]


def _uses_temperature_adjustment(vd_mode: VDMode, use_custom_pf: bool, use_custom_T_op: bool) -> bool:
    return vd_mode == VDMode.TABLE8_R or (vd_mode == VDMode.TABLE9_Z and use_custom_pf and use_custom_T_op)


def _render_equations_used(vd_mode: VDMode, use_custom_pf: bool, use_custom_T_op: bool) -> None:
    st.markdown("### Equations used")

    eq(r"I_{eff}=\frac{I}{N_{parallel}}")

    if vd_mode == VDMode.TABLE8_R:
        eq(r"V_D=pf\cdot\frac{f\cdot R\cdot I_{eff}\cdot L}{1000}")

    elif vd_mode == VDMode.TABLE9_Z:
        if use_custom_pf:
            eq(r"Z_{eff}=R\cdot pf+X_L\cdot\sqrt{1-pf^2}")
            eq(r"V_D=\frac{f\cdot Z_{eff}\cdot I_{eff}\cdot L}{1000}")
        else:
            eq(r"V_D=\frac{f\cdot Z\cdot I_{eff}\cdot L}{1000}")

    elif vd_mode == VDMode.MANUAL_R:
        eq(r"V_D=pf\cdot\frac{f\cdot R_{manual}\cdot I_{eff}\cdot L}{1000}")

    eq(r"\%\Delta V = 100\cdot\frac{V_D}{V_{nom}}")
    
    if _uses_temperature_adjustment(vd_mode, use_custom_pf, use_custom_T_op):
        eq(r"R=R_1\left[1+\alpha\left(T_{op}-75\right)\right]")
        st.caption("Temperature coefficient used by r_temp_change: α = 0.00300 for copper, α = 0.00323 for aluminum.")


def render_calc():
    st.markdown("### Inputs")

    # --------------------
    # DEFAULTS
    # --------------------
    manual_r = None
    conductor_material = ConductorMaterial.NA
    size_num = None
    size_unit = ""
    coating_type = None
    conduit_material = None

    T_op = 75.0
    power_factor = 0.85
    use_custom_pf = False
    use_custom_T_op = False

    # --------------------
    # VD CALC MODE & SYSTEM TYPE
    # --------------------
    c1, c2 = st.columns(2)
    vd_mode = enum_radio(c1, "Calculation method", VDMode)
     
    ex = (SystemTypes.DC,) if vd_mode == VDMode.TABLE9_Z else ()
    system_type = enum_selectbox(c2, "System Type", SystemTypes.exclude(ex))
    system_type_label = system_type.label
    
    # --------------------
    # COMMON INPUTS
    # --------------------
    c1, c2 = st.columns(2)

    I_calc = c1.number_input(
        "Calculation current (A)",
        min_value=0.0,
        value=50.0,
        step=0.1
    )
    current = Current(I_calc)

    V_nom = c2.number_input(
        "Nominal voltage (V)",
        min_value=1.0,
        value=600.0,
        step=1.0
    )
    voltage = Voltage(V_nom)
    
    if vd_mode == VDMode.TABLE9_Z and voltage.value > 600:
        st.warning("Table 9 is based on 600 V cable assumptions. Confirm applicability before using this method above 600 V.")

    c1, c2 = st.columns(2)

    L_ft = c1.number_input("One-way length (ft)", min_value=0.0, value=80.0, step=1.0)
    n_parallel = c2.number_input("Parallel conductors per phase/pole", min_value=1, value=1, step=1)

    # ----------
    # Resistance Method (NEC: Chapter 9, Table 8)
    # ----------
    if vd_mode == VDMode.TABLE8_R:
        power_factor = st.number_input(
            "Load power factor",
            min_value=0.1,
            max_value=1.0,
            step=0.01,
            value=0.85,
            key="power_factor"
        )

        size = st.selectbox(
            "Conductor size",
            list(get_standard_conductor_sizes_t8().keys()),
            index=0,
        )
        size_num, size_unit = size.split()

        c1, c2 = st.columns(2)

        conductor_material = enum_selectbox(c1, "Conductor material", ConductorMaterial.exclude(ConductorMaterial.NA))

        if conductor_material == ConductorMaterial.CU:
            coating_type = enum_selectbox(c2, "Coating type", CopperCoating)
        else:
            coating_type = None

        T_op = st.number_input(
            "Operating temperature (°C)",
            min_value=0.0,
            value=75.0,
            step=1.0,
        )

        # skin_effect = ... maybe??
        # if size_unit == 'AWG' and size_num.isdigit() and int(size_num) >= 8:
        #     construction = st.selectbox("Construction Type", ["Solid", "Stranded"], index=0,)

    # ----------
    # AC Impedance Method (NEC: Chapter 9, Table 9)
    # ----------
    if vd_mode == VDMode.TABLE9_Z:
        c1, c2 = st.columns(2)

        conductor_material = enum_selectbox(c1, "Conductor material", ConductorMaterial.exclude(ConductorMaterial.NA))

        conduit_material = enum_selectbox(c2, "Conduit material", ConduitMaterial, index=1)

        valid_sizes = [
            size for size in list(get_standard_conductor_sizes_t9().keys())
            if _table9_has_value(size, conductor_material.key, conduit_material.key)
        ]

        if not valid_sizes:
            st.error("No valid NEC Table 9 conductor sizes found for this material/conduit combination.")
            return

        size = st.selectbox(
            "Conductor size",
            valid_sizes,
            index=0,
        )
        size_num, size_unit = size.split()

        c1, c2 = st.columns(2, vertical_alignment="bottom")

        use_custom_pf = c1.checkbox(
            "Use custom power factor",
            value=False,
            on_change=reset_to_default,
            args=(
                "use_custom_pf",
                {
                    "power_factor": 0.85,
                    "use_custom_T_op": False,
                    "T_op": 75.0,
                },
            ),
            key="use_custom_pf",
        )

        power_factor = c2.number_input(
            "Load power factor",
            min_value=0.1,
            max_value=1.0,
            step=0.01,
            value=0.85,
            disabled=not use_custom_pf,
            key="power_factor"
        )

        c1, c2 = st.columns(2, vertical_alignment="bottom")

        use_custom_T_op = c1.checkbox(
            "Use custom operating temperature",
            value=False,
            disabled=not use_custom_pf,
            on_change=reset_to_default,
            args=(
                "use_custom_T_op",
                {
                    "T_op": 75.0,
                },
            ),
            key="use_custom_T_op",
        )

        T_op = c2.number_input(
            "Operating temperature (°C)",
            min_value=0.0,
            value=75.0,
            step=1.0,
            disabled=not use_custom_T_op,
            key="T_op",
        )

    # ----------
    # Manual Resistance
    # ----------
    if vd_mode == VDMode.MANUAL_R:
        power_factor = st.number_input(
            "Load power factor",
            min_value=0.1,
            max_value=1.0,
            step=0.01,
            value=0.85,
            key="power_factor"
        )

        manual_r = st.number_input("Manual R-value (Ω/kft)", min_value=0.0, value=0.05)
        st.caption("Enter the resistance value to use directly. This should already reflect the conductor size, material, and temperature you intend to use.")

        # OPTIONAL INPUTS FOR DOCUMENTATION
        with st.expander("Optional conductor reference fields", expanded=False):
            c1, c2, c3 = st.columns(3)

            conductor_material = enum_selectbox(c1, "Conductor material", ConductorMaterial)
            
            coating_type = enum_selectbox(c2, "Coating type", CopperCoating)


            size = c2.selectbox(
                "Conductor size",
                ["Not specified"] + list(get_standard_conductor_sizes_t8().keys()),
                index=0,
            )

            T_op = c3.number_input(
                "Operating temperature (°C, reference only)",
                min_value=0.0,
                value=75.0,
                step=1.0,
            )

            if size != "Not specified":
                size_num, size_unit = size.split()
            else:
                size_num = None
                size_unit = ""

    result = calc_voltage_drop(
        vd_mode=vd_mode.key,
        system_type=system_type.key,
        system_type_label=system_type.label,
        temperature=T_op,
        current=current.to(),
        length=L_ft,
        voltage=voltage.to(),
        parallel_conductors=n_parallel,
        manual_r=manual_r,
        conductor_material=enum_key(conductor_material),
        conductor_material_label=enum_label(conductor_material),
        conductor_size=size_num,
        size_unit=size_unit,
        # construction=construction,
        coating_type=enum_key(coating_type),
        coating_type_label=enum_label(coating_type),
        conduit_material=enum_key(conduit_material),
        conduit_material_label=enum_label(conduit_material),
        pf=power_factor,
        use_custom_pf=use_custom_pf,
        use_custom_T_op=use_custom_T_op,
    )

    st.divider()
    st.markdown("### Results")

    m1, m2 = st.columns(2)

    m1.metric("Estimated voltage drop", fmt(result["voltage_drop"], "V"))
    m2.metric("Voltage drop (%)", fmt(result["percent_drop"], "%"))

    st.markdown("### Parameters used")

    # COMMON PARAMETERS
    st.write(f"- system type: **{result['system_type_label']}**")
    st.write(f"- power factor pf: **{result['pf']}**")
    st.write(f"- I: **{fmt(result['current'], 'A')}**")
    st.write(f"- **$V_{{nom}}$: {fmt(result['v_nom'], 'V')}**")
    st.write(f"- one-way length: **{fmt(result['length'], 'ft')}**")
    st.write(
        f"- parallel conductors: **{result['parallel_conductors']}** "
        f"→ I per conductor = **{fmt(result['I_eff'], 'A')}**"
    )
    st.write(f"- factor f: **{result['f']}**")

    # TABLE 8 PARAMETERS
    if vd_mode == VDMode.TABLE8_R:
        st.write(f"- conductor size: **{result['conductor_size']} {size_unit}**")
        st.write(f"- conductor material: **{result['conductor_material']}**")

        if result.get("coating_type"):
            st.write(f"- coating type: **{result['coating_type']}**")

        st.write(f"- operating temperature: **{result['temperature']} °C**")

    # TABLE 9 PARAMETERS
    if vd_mode == VDMode.TABLE9_Z:
        st.write(f"- conductor size: **{result['conductor_size']} {result['size_unit']}**")
        st.write(f"- conductor material: **{result['conductor_material']}**")
        st.write(f"- conduit material: **{result['conduit_material']}**")
        st.write(f"- power factor: **{result['pf']}**")
        st.write(f"- operating temperature: **{result['temperature']} °C**")
    # MANUAL R PARAMETERS
    if vd_mode == VDMode.MANUAL_R:
        st.write(f"- manual R-value : **{result['manual_r']} Ω/kft**")

    _render_equations_used(
        vd_mode=vd_mode,
        use_custom_pf=use_custom_pf,
        use_custom_T_op=use_custom_T_op,
    )

    st.divider()

    render_export_report(
        result=result,
        vd_mode=vd_mode,
        system_type_label=system_type_label,
        conduit_material=conduit_material,
        use_custom_pf=use_custom_pf,
        use_custom_T_op=use_custom_T_op,
    )
