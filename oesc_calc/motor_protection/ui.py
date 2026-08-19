import streamlit as st

from calc_common.formatting import fmt
from calc_common.report_schedule import apply_restore
from calc_common.ui_helpers import eq

from oesc_calc.motor_protection.calculation import (
    AUTO_TX,
    DC,
    DEVICE_TYPES,
    FULL_VOLTAGE,
    SINGLE_PHASE,
    SQUIRREL_CAGE,
    THREE_PHASE,
    WOUND_ROTOR,
    calc_motor_protection,
)
from oesc_calc.motor_protection.report import (
    MP_SCHEDULE_SPEC,
    render_add_to_schedule,
    render_schedule_section,
)


@st.fragment
def render_calc():
    apply_restore(MP_SCHEDULE_SPEC)

    inputs_pane, result_pane = st.columns([1.45, 1], gap="large")

    with inputs_pane, st.container(border=True):
        st.markdown("### Inputs")

        fla = st.number_input(
            "Motor full-load current (FLA) (A)",
            min_value=0.1,
            value=28.0,
            step=0.1,
            key="oesc_motor_protection_fla",
        )

        st.markdown("#### Table 29 selection — follow the flowchart")

        c1, c2 = st.columns(2)

        voltage_system = c1.selectbox(
            "Voltage System",
            [SINGLE_PHASE, THREE_PHASE, DC],
            index=1,
            key="oesc_motor_protection_voltage_system",
        )

        motor_type = None
        starter_type = None

        if voltage_system == THREE_PHASE:
            motor_type = c2.selectbox(
                "Motor Type",
                [SQUIRREL_CAGE, WOUND_ROTOR],
                index=0,
                key="oesc_motor_protection_motor_type",
            )

            if motor_type == SQUIRREL_CAGE:
                c1, _ = st.columns(2)
                starter_type = c1.selectbox(
                    "Starter or Controller Type",
                    [AUTO_TX, FULL_VOLTAGE],
                    index=0,
                    key="oesc_motor_protection_starter_type",
                )

        c1, _ = st.columns(2)
        device = c1.selectbox(
            "Overcurrent Device Type",
            list(DEVICE_TYPES),
            format_func=lambda key: DEVICE_TYPES[key][0],
            index=0,
            key="oesc_motor_protection_device",
        )

        result = calc_motor_protection(
            fla=fla,
            voltage_system=voltage_system,
            motor_type=motor_type,
            starter_type=starter_type,
            device=device,
        )

    with result_pane, st.container(border=True):
        st.markdown("### Results")

        st.info(
            f"**Table 29 {result['table_29_row_desc']}** → Multiplier: "
            f"**{result['multiplier']}×** ({result['device_label']})"
        )

        m1, m2 = st.columns(2)
        m1.metric("Overcurrent device setting (raw)", fmt(result["ocpd_raw"], "A"))
        m2.metric(
            "Selected standard OCPD rating",
            fmt(result["selected_std"], "A") if result["selected_std"] is not None else "—",
        )

        if result["selected_std"] is None:
            st.error("The calculated value is below the smallest standard device rating.")
        else:
            st.caption("Rounded down to a standard rating, so the Table 29 maximum is not exceeded.")

        st.divider()
        render_add_to_schedule(result)

        with st.expander("Parameters & equations used", expanded=False):
            st.markdown("### Parameters used")
            st.write(f"- motor FLA: **{fmt(result['fla'], 'A')}**")
            st.write(f"- flowchart path: **{result['flowchart_path']}**")
            st.write(f"- Table 29 row: **{result['table_29_row']}** — {result['row_description']}")
            st.write(f"- device type: **{result['device_label']}**")
            st.write(f"- multiplier k: **{result['multiplier']}**")

            st.markdown("### Equations used")
            eq(r"I_{OCPD}=k\cdot I_{FLA}")
            st.caption(
                f"where k = {result['multiplier']} (Table 29 Row {result['table_29_row']}, "
                f"{result['device_label']})"
            )

    st.divider()
    render_schedule_section()
