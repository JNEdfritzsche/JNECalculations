import streamlit as st

from calc_common.formatting import fmt
from calc_common.ui_helpers import eq

from oesc_calc.cable_tray_fill.calculation import (
    IMPERIAL,
    METRIC,
    MM_PER_INCH,
    TRAY_UNITS,
    calc_cable_tray_fill,
    to_mm,
)
from oesc_calc.cable_tray_fill.report import render_add_to_schedule, render_schedule_section

ROWS_KEY = "oesc_cable_tray_fill_rows"


def _rows() -> list[dict]:
    if ROWS_KEY not in st.session_state:
        st.session_state[ROWS_KEY] = [{"id": 0, "name": "", "conductor": "", "gauge": "",
                                       "od": 25.0, "od_unit": "mm", "qty": 3}]
    return st.session_state[ROWS_KEY]


def _add_row() -> None:
    rows = _rows()
    next_id = max((r["id"] for r in rows), default=-1) + 1
    rows.append({"id": next_id, "name": "", "conductor": "", "gauge": "",
                 "od": 25.0, "od_unit": "mm", "qty": 1})


def _render_row(row: dict, index: int, area_unit: str, conversion: float) -> dict:
    row_id = row["id"]
    st.markdown(f"**Cable group {index + 1}**")

    c1, c2, c3, remove = st.columns([3, 2, 2, 1], vertical_alignment="bottom")
    row["name"] = c1.text_input("Cable name", value=row["name"], placeholder="e.g., 'Main feeds'",
                                key=f"oesc_cable_tray_fill_name_{row_id}")
    row["conductor"] = c2.text_input("Conductor", value=row["conductor"], placeholder="e.g., 'RW90'",
                                     key=f"oesc_cable_tray_fill_conductor_{row_id}")
    row["gauge"] = c3.text_input("Gauge", value=row["gauge"], placeholder="e.g., '3/0 AWG'",
                                 key=f"oesc_cable_tray_fill_gauge_{row_id}")

    removed = remove.button("✕", key=f"oesc_cable_tray_fill_remove_{row_id}",
                            help="Remove this cable group", width="stretch")

    c1, c2, c3 = st.columns([2, 3, 2])
    row["od_unit"] = c1.selectbox("OD unit", ["mm", "in"], index=0 if row["od_unit"] == "mm" else 1,
                                  key=f"oesc_cable_tray_fill_od_unit_{row_id}")
    row["od"] = c2.number_input(f"Cable OD ({row['od_unit']})", min_value=0.0001, value=float(row["od"]),
                                step=1.0 if row["od_unit"] == "mm" else 0.01, format="%.2f",
                                key=f"oesc_cable_tray_fill_od_{row_id}")
    row["qty"] = c3.number_input("Qty", min_value=1, value=int(row["qty"]), step=1,
                                 key=f"oesc_cable_tray_fill_qty_{row_id}")

    od_mm = to_mm(row["od"], row["od_unit"])
    single = 3.141592653589793 * (od_mm / 2.0) ** 2
    st.caption(f"Area per cable: {single / conversion:.2f} {area_unit}  |  "
               f"group total: {row['qty'] * single / conversion:.2f} {area_unit}")

    row["_removed"] = removed
    return row


@st.fragment
def render_calc():
    inputs_pane, result_pane = st.columns([1.45, 1], gap="large")

    with inputs_pane, st.container(border=True):
        st.markdown("### Inputs")

        tray_name = st.text_input("Cable tray name (optional)", placeholder="e.g., 'Main Feeder Tray'",
                                  key="oesc_cable_tray_fill_tray_name")

        tray_unit = st.radio("Tray dimensions unit", TRAY_UNITS, horizontal=True,
                             key="oesc_cable_tray_fill_unit")

        c1, c2 = st.columns(2)
        if tray_unit == METRIC:
            width = c1.number_input("Tray width (mm)", min_value=1.0, value=300.0, step=10.0,
                                    key="oesc_cable_tray_fill_width_mm")
            depth = c2.number_input("Tray depth (mm)", min_value=1.0, value=100.0, step=10.0,
                                    key="oesc_cable_tray_fill_depth_mm")
            width_mm, depth_mm = width, depth
        else:
            width = c1.number_input("Tray width (inches)", min_value=0.1, value=12.0, step=0.1,
                                    key="oesc_cable_tray_fill_width_in")
            depth = c2.number_input("Tray depth (inches)", min_value=0.1, value=4.0, step=0.1,
                                    key="oesc_cable_tray_fill_depth_in")
            width_mm, depth_mm = width * MM_PER_INCH, depth * MM_PER_INCH

        area_unit = "in²" if tray_unit == IMPERIAL else "mm²"
        conversion = 645.16 if tray_unit == IMPERIAL else 1.0
        st.info(f"**Tray usable area: {width_mm * depth_mm / conversion:,.2f} {area_unit}**")

        st.markdown("#### Cable groups")
        rows = _rows()
        for index, row in enumerate(list(rows)):
            _render_row(row, index, area_unit, conversion)
            st.divider()

        if st.button("➕ Add cable group", key="oesc_cable_tray_fill_add", width="stretch"):
            _add_row()
            st.rerun()

        removed = [r for r in rows if r.get("_removed")]
        if removed and len(rows) > 1:
            st.session_state[ROWS_KEY] = [r for r in rows if not r.get("_removed")]
            st.rerun()

        result = calc_cable_tray_fill(
            tray_unit=tray_unit,
            tray_width_mm=width_mm,
            tray_depth_mm=depth_mm,
            tray_name=tray_name,
            cables=[
                {"name": r["name"], "conductor": r["conductor"], "gauge": r["gauge"],
                 "od_mm": to_mm(r["od"], r["od_unit"]), "qty": r["qty"]}
                for r in rows
            ],
        )

    with result_pane, st.container(border=True):
        st.markdown("### Results")

        m1, m2, m3 = st.columns(3)
        m1.metric(f"Usable area ({area_unit})", f"{result['tray_area_mm2'] / conversion:,.2f}")
        m2.metric(f"Area used ({area_unit})", f"{result['total_cable_area_mm2'] / conversion:,.2f}")
        m3.metric("Fill percentage", f"{result['fill_percentage']:.2f}%")

        if result["fill_percentage"] > 100:
            st.error("The cables do not fit the tray cross-section.")

        st.markdown("#### Cable group breakdown")
        for group in result["groups"]:
            od = group["od_mm"] / MM_PER_INCH if tray_unit == IMPERIAL else group["od_mm"]
            od_unit = "in" if tray_unit == IMPERIAL else "mm"
            st.write(
                f"- **{group['name'] or '[unnamed]'}** — {group['qty']}× "
                f"{fmt(od, od_unit)} OD → {fmt(group['area_mm2'] / conversion, area_unit)} "
                f"({group['percent_of_tray']:.2f}% of tray)"
            )

        st.divider()
        render_add_to_schedule(result)

        with st.expander("Parameters & equations used", expanded=False):
            st.markdown("### Parameters used")
            st.write(f"- tray: **{fmt(width, 'mm' if tray_unit == METRIC else 'in')}** wide × "
                     f"**{fmt(depth, 'mm' if tray_unit == METRIC else 'in')}** deep")
            st.write(f"- cable groups: **{len(result['groups'])}**, total cables: **{result['n_cables']}**")

            st.markdown("### Equations used")
            eq(r"A_{tray}=w\cdot d")
            eq(r"A_{cable}=\pi\left(\frac{OD}{2}\right)^2")
            eq(r"A_{total}=\sum\left(n\cdot A_{cable}\right)")
            eq(r"\text{Fill (\%)}=\frac{A_{total}}{A_{tray}}\cdot 100")

    st.divider()
    render_schedule_section()
