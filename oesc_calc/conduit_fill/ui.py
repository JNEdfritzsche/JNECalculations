import streamlit as st

from calc_common.formatting import fmt
from calc_common.ui_helpers import eq

from oesc_calc.conduit_fill.calculation import (
    DISPLAY_UNITS,
    IMPERIAL,
    METRIC,
    MM2_PER_IN2,
    MM_PER_INCH,
    cable_area_from_od_mm2,
    calc_conduit_fill,
    conduit_types,
    trade_sizes,
)
from oesc_calc.conduit_fill.diagram import build_cross_section_svg, group_swatch_svg
from oesc_calc.conduit_fill.report import render_add_to_schedule, render_schedule_section

ROWS_KEY = "oesc_conduit_fill_rows"


def _rows() -> list[dict]:
    if ROWS_KEY not in st.session_state:
        st.session_state[ROWS_KEY] = [{"id": 0, "name": "", "conductor": "", "size": "",
                                       "od": 12.0, "od_unit": "mm", "qty": 3, "n_cond": 3}]
    return st.session_state[ROWS_KEY]


def _add_row() -> None:
    rows = _rows()
    rows.append({"id": max((r["id"] for r in rows), default=-1) + 1, "name": "", "conductor": "",
                 "size": "", "od": 12.0, "od_unit": "mm", "qty": 1, "n_cond": 3})


@st.fragment
def render_calc():
    inputs_pane, result_pane = st.columns([1.45, 1], gap="large")

    with inputs_pane, st.container(border=True):
        st.markdown("### Inputs")

        display_unit = st.radio("Display units", DISPLAY_UNITS, horizontal=True,
                                key="oesc_conduit_fill_display_unit")
        area_unit = "in²" if display_unit == IMPERIAL else "mm²"
        conversion = 1.0 / MM2_PER_IN2 if display_unit == IMPERIAL else 1.0

        types = conduit_types()
        c1, c2 = st.columns([3, 2])
        conduit_type = c1.selectbox("Conduit / tubing type", list(types), index=0,
                                    format_func=lambda k: types[k], key="oesc_conduit_fill_type")

        sizes = trade_sizes(conduit_type)
        trade_size = c2.selectbox("Trade size (mm)", sizes, index=min(2, len(sizes) - 1) if sizes else 0,
                                  key=f"oesc_conduit_fill_size_{conduit_type}") if sizes else None

        is_low_voltage = st.checkbox(
            "Low-voltage installation (fill limits not applied)", value=False,
            key="oesc_conduit_fill_low_voltage",
        )

        st.markdown("#### Cables")
        rows = _rows()
        for index, row in enumerate(list(rows)):
            row_id = row["id"]
            st.markdown(f"**Cable {index + 1}**")

            c1, c2, c3, remove = st.columns([3, 2, 2, 1], vertical_alignment="bottom")
            row["name"] = c1.text_input("Name", value=row["name"], placeholder="e.g., 'Feeder A'",
                                        key=f"oesc_conduit_fill_name_{row_id}")
            row["conductor"] = c2.text_input("Conductor", value=row["conductor"], placeholder="e.g., 'RW90'",
                                             key=f"oesc_conduit_fill_conductor_{row_id}")
            row["size"] = c3.text_input("Size", value=row["size"], placeholder="e.g., '2/0'",
                                        key=f"oesc_conduit_fill_cable_size_{row_id}")
            row["_removed"] = remove.button("✕", key=f"oesc_conduit_fill_remove_{row_id}",
                                            help="Remove this cable", width="stretch")

            c1, c2, c3, c4 = st.columns([2, 3, 2, 2])
            row["od_unit"] = c1.selectbox("OD unit", ["mm", "in"], index=0 if row["od_unit"] == "mm" else 1,
                                          key=f"oesc_conduit_fill_od_unit_{row_id}")
            row["od"] = c2.number_input(f"Cable OD ({row['od_unit']})", min_value=0.0001,
                                        value=float(row["od"]), step=1.0 if row["od_unit"] == "mm" else 0.01,
                                        format="%.2f", key=f"oesc_conduit_fill_od_{row_id}")
            row["qty"] = c3.number_input("Qty", min_value=1, value=int(row["qty"]), step=1,
                                         key=f"oesc_conduit_fill_qty_{row_id}")
            row["n_cond"] = c4.number_input("Conductors per cable", min_value=1,
                                            value=int(row.get("n_cond") or 1), step=1,
                                            key=f"oesc_conduit_fill_ncond_{row_id}")

            od_mm = row["od"] * (MM_PER_INCH if row["od_unit"] == "in" else 1.0)
            st.caption(f"Area per cable: {cable_area_from_od_mm2(od_mm) * conversion:.2f} {area_unit}")
            st.divider()

        if st.button("➕ Add cable", key="oesc_conduit_fill_add", width="stretch"):
            _add_row()
            st.rerun()

        if any(r.get("_removed") for r in rows) and len(rows) > 1:
            st.session_state[ROWS_KEY] = [r for r in rows if not r.get("_removed")]
            st.rerun()

        result = calc_conduit_fill(
            conduit_type=conduit_type,
            trade_size_mm=trade_size,
            display_unit=display_unit,
            is_low_voltage=is_low_voltage,
            cables=[
                {"name": r["name"], "conductor": r["conductor"], "size": r["size"],
                 "od_mm": r["od"] * (MM_PER_INCH if r["od_unit"] == "in" else 1.0), "qty": r["qty"],
                 "conductors_per_cable": r.get("n_cond", 1)}
                for r in rows
            ],
        )

    with result_pane, st.container(border=True):
        st.markdown("### Results")

        m1, m2, m3 = st.columns(3)
        m1.metric("Cables in raceway", result["n_cables"])
        m2.metric(f"Total cable area ({area_unit})", f"{result['total_cable_area_mm2'] * conversion:,.2f}")
        m3.metric(
            f"Conduit internal area ({area_unit})",
            f"{result['internal_area_mm2'] * conversion:,.2f}" if result["internal_area_mm2"] else "—",
        )

        m1, m2, m3 = st.columns(3)
        m1.metric(f"Allowable area ({area_unit})",
                  f"{result['allowed_area_mm2'] * conversion:,.2f}" if result["allowed_area_mm2"] else "—")
        m2.metric(f"Remaining ({area_unit})",
                  f"{result['remaining_area_mm2'] * conversion:,.2f}" if result["remaining_area_mm2"] is not None else "—")
        m3.metric("Actual fill", fmt(result["fill_percent"], "%"))

        if result["is_low_voltage"]:
            st.info("Low-voltage installation — the Table 9 fill limits are not applied.")
        elif result["fits"] is None:
            st.warning("Select a conduit type and trade size to check the fill.")
        elif result["fits"]:
            st.success(
                f"Fill is within the allowable limit "
                f"({fmt(result['allowed_percent'], '%')} per Tables {result['allowed_table']})."
            )
        else:
            st.error(
                f"Fill exceeds the allowable limit "
                f"({fmt(result['allowed_percent'], '%')} per Tables {result['allowed_table']})."
            )
            if result["min_trade_size_mm"]:
                st.info(f"Smallest {result['conduit_label']} that accepts these cables: "
                        f"**{result['min_trade_size_mm']} mm**.")
            else:
                st.warning("No trade size of this conduit type accepts these cables.")

        if st.checkbox("Show conduit cross-section diagram", value=True,
                       key="oesc_conduit_fill_show_viz"):
            if not result["internal_area_mm2"]:
                st.warning("Select a conduit type and trade size to render the cross-section.")
            else:
                svg = build_cross_section_svg(result)
                if svg is None:
                    st.info("Add at least one cable with an area to render the layout.")
                else:
                    st.markdown(svg, unsafe_allow_html=True)
                    for index, group in enumerate(result["groups"]):
                        swatch = group_swatch_svg(group, index)
                        legend, label = st.columns([1, 6], vertical_alignment="center")
                        if swatch:
                            legend.markdown(swatch, unsafe_allow_html=True)
                        label.caption(
                            f"{group['name'] or '[unnamed]'} — {group['qty']}× "
                            f"{group['conductors_per_cable']}-conductor"
                        )

        st.divider()
        render_add_to_schedule(result)

        with st.expander("Parameters & equations used", expanded=False):
            st.markdown("### Parameters used")
            st.write(f"- conduit: **{result['conduit_label']}**, trade size **{result['trade_size_mm']} mm**")
            st.write(f"- cables: **{result['n_cables']}** in **{len(result['groups'])}** groups")
            for group in result["groups"]:
                st.write(f"  - **{group['name'] or '[unnamed]'}**: {group['qty']}× "
                         f"{fmt(group['area_each_mm2'] * conversion, area_unit)} each, "
                         f"{group['conductors_per_cable']} conductors per cable")
            st.write(f"- allowable fill from Tables **{result['allowed_table']}**")

            st.markdown("### Equations used")
            eq(r"A_{cable}=\pi\left(\frac{OD}{2}\right)^2")
            eq(r"A_{total}=\sum\left(n\cdot A_{cable}\right)")
            eq(r"\text{Fill (\%)}=\frac{A_{total}}{A_{internal}}\cdot 100")
            eq(r"A_{total}\leq A_{allowed}")

    st.divider()
    render_schedule_section()
