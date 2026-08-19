import streamlit as st

from calc_common.formatting import fmt
from calc_common.report_schedule import apply_restore
from calc_common.ui_helpers import eq

from nec_calc.cable_tray_fill.calculation import (
    AREA_UNITS,
    CHANNEL_RULES,
    LENGTH_UNITS,
    cable_area,
    get_cable_types,
    get_size_bands,
    get_tray_types,
    get_tray_widths,
    main_calc_cable_tray_fill,
)
from nec_calc.cable_tray_fill.report import (
    CT_SCHEDULE_SPEC,
    render_add_to_schedule,
    render_schedule_section,
)

MAX_GROUPS = 8

@st.fragment
def render_calc():
    apply_restore(CT_SCHEDULE_SPEC)

    inputs_pane, result_pane = st.columns([1.45,1], gap="large")
    
    with inputs_pane, st.container(border=True):
        st.markdown("### Inputs")

        # --------------------
        # UNITS
        # --------------------
        units_choice = st.radio(
            "Display units",
            ["imperial", "metric"],
            format_func=lambda u: f"Imperial ({AREA_UNITS[u]})" if u == "imperial" else f"Metric ({AREA_UNITS[u]})",
            horizontal=True,
            key="ctfn_units",
        )
        area_unit = AREA_UNITS[units_choice]
        length_unit = LENGTH_UNITS[units_choice]

        # --------------------
        # CABLE TYPE + TRAY (TABLE 392.22)
        # --------------------
        st.markdown("#### 1) Cable and tray selection — Article 392.22")

        cable_types = get_cable_types()
        cable_type = st.selectbox(
            "Cables installed in the tray",
            list(cable_types.keys()),
            format_func=lambda k: cable_types[k],
            key="ctfn_cable_type",
        )

        tray_types = get_tray_types(cable_type)

        c1, c2 = st.columns([3, 1])
        tray_type = c1.selectbox(
            "Cable tray type",
            list(tray_types.keys()),
            format_func=lambda k: tray_types[k],
            key=f"ctfn_tray_type_{cable_type}",
        )

        widths = get_tray_widths(cable_type, tray_type, units_choice)
        if not widths:
            st.error(
                "The NEC Table 392.22 fill areas for this tray are not loaded in "
                "`lib/nec_tables.py`, so tray widths cannot be looked up."
            )
            st.stop()

        tray_width = c2.selectbox(
            f"Inside tray width ({length_unit})",
            widths,
            key=f"ctfn_tray_width_{cable_type}_{tray_type}_{units_choice}",
        )

        # --------------------
        # CABLE GROUPS
        # --------------------
        st.markdown("#### 2) Cables")
        st.caption(
            "Enter the overall diameter of each cable from the manufacturer's data; the NEC does "
            "not publish cable diameters."
        )

        n_groups = st.number_input(
            "Number of cable groups",
            min_value=1,
            max_value=MAX_GROUPS,
            value=1,
            step=1,
            key="ctfn_n_groups",
        )

        size_bands = get_size_bands(cable_type)
        band_keys = list(size_bands.keys())

        by_cable_count = tray_type in CHANNEL_RULES
        if by_cable_count:
            st.caption(
                f"NEC {CHANNEL_RULES[tray_type]} sizes a channel tray on the number of cables "
                "rather than the cable size, so no size band is needed."
            )

        groups = []
        for i in range(int(n_groups)):
            st.markdown(f"**Group {i + 1}**")

            columns = st.columns([1, 1] if by_cable_count else [3, 1, 1])
            g1 = None if by_cable_count else columns[0]
            g2, g3 = columns[-2], columns[-1]

            size_band = (
                band_keys[0]
                if g1 is None
                else g1.selectbox(
                    "Cable size band",
                    band_keys,
                    format_func=lambda k: size_bands[k],
                    key=f"ctfn_band_{cable_type}_{i}",
                    disabled=len(band_keys) == 1,
                )
            )
            diameter = g2.number_input(
                f"Cable OD ({length_unit})",
                min_value=0.0001,
                value=25.0 if units_choice == "metric" else 1.0,
                step=1.0 if units_choice == "metric" else 0.01,
                format="%.2f",
                key=f"ctfn_od_{units_choice}_{i}",
            )
            count = g3.number_input(
                "Quantity",
                min_value=1,
                max_value=200,
                value=3 if i == 0 else 1,
                step=1,
                key=f"ctfn_count_{i}",
            )

            groups.append(
                {
                    "size_band": size_band,
                    "size_band_label": "Multiconductor cable" if by_cable_count else size_bands[size_band],
                    "diameter": diameter,
                    "count": int(count),
                    "area": cable_area(diameter),
                }
            )

        result = main_calc_cable_tray_fill(
            cable_type=cable_type,
            tray_type=tray_type,
            tray_width=tray_width,
            groups=groups,
            units=units_choice,
        )

    with result_pane, st.container(border=True):
        st.markdown("### Results")

        # --------------------
        # GOVERNING RULE
        # --------------------
        st.markdown(f"#### Governing rule — NEC {result['rule']}")
        st.caption(result["rule_description"] + ".")

        basis_unit = area_unit if result["limit_basis"] == "area" else length_unit
        m1, m2, m3 = st.columns(3)
        m1.metric(f"Total cable area ({area_unit})", fmt(result["total_cable_area"]))
        m2.metric(f"Sum of cable diameters ({length_unit})", fmt(result["sum_diameters"]))
        m3.metric("Utilization of the limit", fmt(result["utilization_percent"], "%"))

        if result["allowed_value"] is None:
            st.warning(
                f"NEC {result['rule']} could not be evaluated — Table 392.22 publishes no "
                f"allowable value for this tray width and cable combination."
            )
        elif result["fits"]:
            st.success(
                f"Fill OK: **{fmt(result['limited_value'], basis_unit)}** ≤ allowed "
                f"**{fmt(result['allowed_value'], basis_unit)}** per NEC {result['rule']}."
            )
        else:
            st.error(
                f"Over the limit: **{fmt(result['limited_value'], basis_unit)}** > allowed "
                f"**{fmt(result['allowed_value'], basis_unit)}** per NEC {result['rule']}."
            )

        if result["sd"] is not None:
            st.info(
                f"Mixed cable sizes: the allowable area is reduced by the single layer of larger "
                f"cables, Sd = **{fmt(result['sd'], length_unit)}**."
            )

        if result["single_layer"]:
            st.caption(
                "This rule also requires a single layer of cables — verify the physical "
                "arrangement in the tray, not just the totals."
            )

        # --------------------
        # MINIMUM WIDTH
        # --------------------
        if result["min_tray_width"] is not None:
            st.info(
                f"Minimum tray width for these cables in a {result['tray_type_label'].lower()}: "
                f"**{fmt(result['min_tray_width'], length_unit)}**."
            )
        else:
            st.warning(
                "No published tray width satisfies this rule for these cables — split the run "
                "or use a wider tray family."
            )
            
        st.divider()     
        render_add_to_schedule(result)
        
        with st.expander("Parameters & equations used", expanded=False):
            st.markdown("### Parameters used")
            st.write(f"- cables: **{result['cable_type_label']}**")
            st.write(f"- tray: **{result['tray_type_label']}**, inside width **{fmt(result['tray_width'], length_unit)}**")
            st.write(f"- total cables: **{result['n_cables']}**")
            for i, g in enumerate(result["groups"]):
                st.write(
                    f"- group {i + 1}: **{g['count']}× {g['size_band_label']}** at "
                    f"**{fmt(g['diameter'], length_unit)}** OD "
                    f"(**{fmt(g['area'], area_unit)}** each)"
                )

            st.markdown("### Equations used")
            eq(r"A_{cable}=\pi\left(\frac{OD}{2}\right)^2")
            eq(r"A_{total}=\sum_{i} N_i \cdot A_i")
            eq(r"S_d=\sum_{i} N_i \cdot OD_i")
            eq(r"A_{allowed}=A_{const}-k\cdot S_d\;(\text{Table 392.22 mixed-size columns})")

    st.divider()
    render_schedule_section()
