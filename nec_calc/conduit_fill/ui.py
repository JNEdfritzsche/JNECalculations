import streamlit as st

from calc_common.formatting import fmt
from calc_common.ui_helpers import eq

from nec_calc.conduit_fill.calculation import (
    AREA_UNITS,
    get_conductor_area,
    get_conductor_sizes,
    get_conductor_types,
    get_conduit_types,
    get_trade_sizes,
    main_calc_conduit_fill,
)
from nec_calc.conduit_fill.report import render_add_to_schedule, render_schedule_section

MAX_GROUPS = 8

@st.fragment
def render_calc():
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
            key="cfn_units",
        )
        area_unit = AREA_UNITS[units_choice]

        # --------------------
        # CONDUIT SELECTION (TABLE 4)
        # --------------------
        st.markdown("#### 1) Conduit selection — Chapter 9, Table 4")

        conduit_types = get_conduit_types()
        conduit_keys = list(conduit_types.keys())

        c1, c2 = st.columns([3, 1])
        conduit_key = c1.selectbox(
            "Conduit / tubing type",
            conduit_keys,
            format_func=lambda k: conduit_types[k],
            key="cfn_conduit_type",
        )

        trade_sizes = get_trade_sizes(conduit_key)
        trade_size = c2.selectbox(
            "Trade size",
            trade_sizes,
            key="cfn_trade_size",
        )

        # --------------------
        # CONDUCTOR GROUPS (TABLE 5)
        # --------------------
        st.markdown("#### 2) Conductors — Chapter 9, Table 5")

        n_groups = st.number_input(
            "Number of conductor groups",
            min_value=1,
            max_value=MAX_GROUPS,
            value=1,
            step=1,
            key="cfn_n_groups",
        )

        conductor_types = get_conductor_types()

        groups = []
        for i in range(int(n_groups)):
            st.markdown(f"**Group {i + 1}**")
            manual = st.checkbox(
                "Enter conductor area manually",
                value=False,
                key=f"cfn_manual_{i}",
            )

            g1, g2, g3 = st.columns([3, 1, 1])

            if manual:
                area = g1.number_input(
                    f"Area per conductor ({area_unit})",
                    min_value=0.0001,
                    value=100.0 if units_choice == "metric" else 0.15,
                    step=1.0 if units_choice == "metric" else 0.01,
                    format="%.4f" if units_choice == "imperial" else "%.2f",
                    key=f"cfn_area_{units_choice}_{i}",
                )
                conductor_type = None
                cond_size = None
            else:
                conductor_type = g1.selectbox(
                    "Insulation type",
                    conductor_types,
                    key=f"cfn_type_{i}",
                )
                sizes = get_conductor_sizes(conductor_type)
                cond_size = g2.selectbox(
                    "Size (AWG/kcmil)",
                    sizes,
                    key=f"cfn_size_{i}",
                )
                area = get_conductor_area(conductor_type, cond_size, units_choice)

            count = g3.number_input(
                "Quantity",
                min_value=1,
                max_value=200,
                value=3 if i == 0 else 1,
                step=1,
                key=f"cfn_count_{i}",
            )

            if area is None:
                st.error(f"Group {i + 1}: no Table 5 area found for this selection.")

            groups.append(
                {
                    "conductor_type": conductor_type,
                    "size": cond_size,
                    "count": int(count),
                    "area": area,
                }
            )

        if any(g["area"] is None for g in groups):
            st.stop()

        result = main_calc_conduit_fill(
            conduit_key=conduit_key,
            trade_size=trade_size,
            groups=groups,
            units=units_choice,
    )

    with result_pane, st.container(border=True):
        st.markdown("### Results")

        # --------------------
        # FILL
        # --------------------
        m1, m2, m3 = st.columns(3)
        m1.metric("Total conductor area", fmt(result["total_conductor_area"], area_unit))
        m2.metric(
            "Allowed fill (Table 1)",
            fmt(result["allowed_percent"], "%"),
            help="53% for 1 conductor, 31% for 2, 40% for 3 or more.",
        )
        m3.metric("Actual fill", fmt(result["fill_percent"], "%"))

        if result["fits"] is None:
            st.warning("Fill could not be evaluated for this selection.")
        elif result["fits"]:
            st.success(
                f"Fill OK: **{fmt(result['total_conductor_area'], area_unit)}** ≤ allowed "
                f"**{fmt(result['allowed_area'], area_unit)}** "
                f"({fmt(result['allowed_percent'], '%')} of {fmt(result['internal_area'], area_unit)})."
            )
        else:
            st.error(
                f"Overfilled: **{fmt(result['total_conductor_area'], area_unit)}** > allowed "
                f"**{fmt(result['allowed_area'], area_unit)}** "
                f"({fmt(result['allowed_percent'], '%')} of {fmt(result['internal_area'], area_unit)})."
            )

        # --------------------
        # MINIMUM SIZE
        # --------------------
        if result["min_trade_size"] is not None:
            st.info(
                f"Minimum {result['conduit_label']} size for these conductors: "
                f"**{result['min_trade_size']}** (metric designator {result['min_metric_designator']})."
            )
        else:
            st.warning("No trade size of this conduit type can hold these conductors — split the run or choose a larger conduit family.")

        # --------------------
        # BEND RADIUS (TABLE 2)
        # --------------------
        st.markdown("#### Bend radius — Chapter 9, Table 2")
        if result["bend_one_shot_mm"] is not None:
            b1, b2 = st.columns(2)
            b1.metric(
                "One shot / full shoe benders",
                f"{fmt(result['bend_one_shot_mm'], 'mm')} ({fmt(result['bend_one_shot_in'], 'in')})",
            )
            b2.metric(
                "Other bends",
                f"{fmt(result['bend_other_mm'], 'mm')} ({fmt(result['bend_other_in'], 'in')})",
            )
        else:
            st.warning("No Table 2 bend radius entry for this trade size.")
            
        st.divider()
        render_add_to_schedule(result)
        
        with st.expander("Parameters & equations used:"):  
            st.markdown("### Parameters used")
            st.write(f"- conduit: **{result['conduit_label']}**, trade size **{result['trade_size']}**")
            st.write(f"- total conductors: **{result['n_conductors']}**")
            for i, g in enumerate(result["groups"]):
                label = f"{g['conductor_type']} {g['size']}" if g["conductor_type"] else "manual area"
                st.write(f"- group {i + 1}: **{g['count']}× {label}** at **{fmt(g['area'], area_unit)}** each")

            st.markdown("### Equations used")
            eq(r"A_{total}=\sum_{i} N_i \cdot A_i")
            eq(r"\text{Fill \%}=\frac{A_{total}}{A_{100\%}}\times 100")
            eq(r"A_{total}\leq A_{allowed}\;(\text{Table 1: 53\%, 31\%, or 40\% of } A_{100\%})")

    st.divider()
    render_schedule_section()    
