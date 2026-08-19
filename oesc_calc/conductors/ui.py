import streamlit as st

from calc_common.formatting import fmt, format_cond_size
from calc_common.report_schedule import apply_restore
from calc_common.ui_helpers import eq

from oesc_calc.common import tables
from oesc_calc.conductors.calculation import (
    ALUMINUM,
    COPPER,
    FREE_AIR,
    INSTALLATIONS,
    MULTI,
    RACEWAY,
    SINGLE,
    SIZE_CLASSES,
    SPACING_100,
    SPACING_25_100,
    SPACING_UNDER_25,
    SPACINGS,
    calc_conductors,
    select_subrule,
)
from oesc_calc.conductors.report import (
    COND_SCHEDULE_SPEC,
    render_add_to_schedule,
    render_schedule_section,
)


def _correction_factor(corr_table: str | None, n_conductors: int) -> tuple[float, str]:
    if corr_table is None:
        return 1.0, "None"

    if corr_table == "5B":
        factor = tables.correction_5b(n_conductors)
        if factor is not None:
            st.caption(f"Table 5B — {n_conductors} conductors → k_corr = {factor}")
            return factor, "Table 5B"
        st.warning("Table 5B covers 2 to 4 conductors; enter the factor manually.")

    if corr_table == "5C":
        factor, band = tables.correction_5c(n_conductors)
        if factor is not None:
            st.caption(f"Table 5C — {band} conductors → k_corr = {factor}")
            return factor, "Table 5C"
        st.warning("Table 5C has no band for this conductor count; enter the factor manually.")

    if corr_table == "5D":
        options = tables.correction_5d_options()
        if options:
            choice = st.selectbox(
                "Table 5D — cables per layer × layers",
                options,
                format_func=lambda o: f"{o[0]} across × {o[1]} layers → {o[2]}",
                key="oesc_conductors_5d",
            )
            return choice[2], "Table 5D"

    factor = st.number_input(
        f"Correction factor k_corr (Table {corr_table})",
        min_value=0.01, max_value=1.00, value=0.80, step=0.01,
        key=f"oesc_conductors_manual_corr_{corr_table}",
    )
    return factor, f"Manual (Table {corr_table})"


@st.fragment
def render_calc():
    apply_restore(COND_SCHEDULE_SPEC)

    inputs_pane, result_pane = st.columns([1.45, 1], gap="large")

    with inputs_pane, st.container(border=True):
        st.markdown("### Inputs")

        c1, c2 = st.columns(2)
        i_load = c1.number_input("Load current (A)", min_value=0.0, value=100.0, step=1.0,
                                 key="oesc_conductors_load")
        sf = c2.number_input("Service factor (SF)", min_value=1.0, value=1.25, step=0.05,
                             key="oesc_conductors_sf")

        c1, c2 = st.columns(2)
        use_parallel = c1.checkbox("Parallel conductor sets", value=False, key="oesc_conductors_use_parallel")
        n_parallel = c2.number_input("Number of parallel sets", min_value=1, value=2, step=1,
                                     disabled=not use_parallel, key="oesc_conductors_parallel") if use_parallel else 1

        c1, c2 = st.columns(2)
        material = c1.selectbox("Conductor material", [COPPER, ALUMINUM], index=0,
                                key="oesc_conductors_material")
        conductor_form = c2.selectbox("Conductor form", [SINGLE, MULTI], index=0,
                                      key="oesc_conductors_form")

        install = st.selectbox("Installation", INSTALLATIONS, index=1, key="oesc_conductors_install")

        n_conductors = 3
        spacing = SPACING_100
        size_class = SIZE_CLASSES[0]
        in_diagrams = "Yes"

        if install == FREE_AIR and conductor_form == SINGLE:
            c1, c2 = st.columns(2)
            spacing = c1.radio("Spacing (% of largest cable diameter)", SPACINGS, index=0,
                               key="oesc_conductors_spacing")
            if spacing != SPACING_25_100:
                n_conductors = c2.number_input("Number of single conductors in the group", min_value=1,
                                               value=4, step=1, key="oesc_conductors_n_single")
        elif install == FREE_AIR:
            n_conductors = st.number_input("Current-carrying conductors in cable", min_value=1, value=3,
                                           step=1, key="oesc_conductors_n_multi")
        elif install == RACEWAY:
            n_conductors = st.number_input("Current-carrying conductors in raceway/cable", min_value=1,
                                           value=3, step=1, key="oesc_conductors_n_raceway")
        else:
            c1, c2 = st.columns(2)
            size_class = c1.selectbox("Conductor size class", SIZE_CLASSES, index=0,
                                      key="oesc_conductors_size_class")
            in_diagrams = c2.radio("Configuration covered by Diagrams D8–D11?", ["Yes", "No"], index=0,
                                   horizontal=True, key="oesc_conductors_diagrams")

        path = select_subrule(material, conductor_form, install, n_conductors, spacing, size_class, in_diagrams)
        st.success(f"**Subrule path:** {path['subrule']}")
        st.success(f"**Use ampacity from:** {path['amp_table']}")

        corr_factor, corr_source = _correction_factor(path["corr_table"], n_conductors)

        use_temp_corr = st.checkbox("Apply ambient temperature correction (Table 5A)", value=False,
                                    key="oesc_conductors_use_temp")
        temp_factor, temp_source = 1.0, "None"
        temp_choice = 75

        c1, c2 = st.columns(2)
        temp_choice = c1.selectbox("Table column (insulation temp rating)", tables.temperature_columns("2"),
                                   index=1, format_func=lambda t: f"{t}°C", key="oesc_conductors_temp_col")

        if use_temp_corr:
            ambient = c2.selectbox("Ambient temperature (°C)", tables.ambient_options(), index=0,
                                   key="oesc_conductors_ambient")
            looked_up = tables.temperature_correction(ambient, temp_choice)
            if looked_up is not None:
                temp_factor, temp_source = looked_up, "Table 5A"
                st.caption(f"Table 5A — {ambient}°C ambient, {temp_choice}°C column → k_temp = {temp_factor}")
            else:
                temp_factor = st.number_input("Temperature factor k_temp", min_value=0.01, max_value=1.50,
                                              value=1.00, step=0.01, key="oesc_conductors_manual_temp")
                temp_source = "Manual"

        result = calc_conductors(
            i_load=i_load, sf=sf, n_parallel=n_parallel, material=material,
            conductor_form=conductor_form, install=install, corr_factor=corr_factor,
            temp_factor=temp_factor, temp_choice=temp_choice, n_conductors=n_conductors,
            spacing=spacing, size_class=size_class, in_diagrams=in_diagrams,
            corr_factor_source=corr_source, temp_factor_source=temp_source,
        )

    with result_pane, st.container(border=True):
        st.markdown("### Results")

        m1, m2 = st.columns(2)
        m1.metric("Design current (total)", fmt(result["I_design_total"], "A"))
        m2.metric("Design current per set", fmt(result["I_per_set"], "A"))

        m1, m2 = st.columns(2)
        m1.metric("Total correction factor (k_total)", fmt(result["k_total"]))
        m2.metric("Minimum base-table ampacity", fmt(result["I_table_required"], "A"))

        if result["selected_size"] is None:
            if result["amp_table_id"] is None:
                st.info(f"Ampacity for this configuration comes from {result['amp_table']}.")
            else:
                st.warning(
                    "No size in the selected table column meets the required base ampacity. "
                    "Consider a higher temperature column or parallel sets."
                )
        else:
            st.markdown(f"## **{format_cond_size(result['selected_size'])}**")
            st.caption(f"Smallest size in {result['amp_table']} at the {result['temp_choice']}°C column.")
            m1, m2 = st.columns(2)
            m1.metric("Base ampacity (table)", fmt(result["base_ampacity"], "A"))
            m2.metric("Adjusted ampacity per set", fmt(result["adjusted_ampacity_per_set"], "A"))
            if result["n_parallel"] > 1:
                st.caption(f"All {result['n_parallel']} sets: "
                           f"**{fmt(result['adjusted_ampacity_total'], 'A')}**")

        st.divider()
        render_add_to_schedule(result)

        with st.expander("Parameters & equations used", expanded=False):
            st.markdown("### Parameters used")
            st.write(f"- load: **{fmt(result['i_load'], 'A')}** × SF **{result['sf']}** "
                     f"→ **{fmt(result['I_design_total'], 'A')}**")
            st.write(f"- parallel sets: **{result['n_parallel']}**")
            st.write(f"- subrule: **{result['subrule']}**")
            st.write(f"- ampacity table: **{result['amp_table']}**, {result['temp_choice']}°C column")
            st.write(f"- k_corr: **{result['corr_factor']}** ({result['corr_factor_source']})")
            st.write(f"- k_temp: **{result['temp_factor']}** ({result['temp_factor_source']})")
            st.write(f"- k_total: **{fmt(result['k_total'])}**")

            st.markdown("### Equations used")
            eq(r"I_{design}=SF\cdot I_{load}")
            eq(r"I_{set}=\frac{I_{design}}{N}")
            eq(r"k_{total}=k_{corr}\cdot k_{temp}")
            eq(r"I_{table}=\frac{I_{set}}{k_{total}}")
            eq(r"I_{adj}=I_{base}\cdot k_{total}")

    st.divider()
    render_schedule_section()
