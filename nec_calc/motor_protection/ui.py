from fractions import Fraction

import pandas as pd
import streamlit as st

from lib.nec_tables import TABLES
from calc_common.enums import ServiceFactors, SystemTypes
from calc_common.formatting import fmt
from calc_common.table_helpers import get_row_headers
from calc_common.ui_helpers import enum_selectbox, eq

from nec_calc.motor_feeder.calculation import get_appropriate_table, get_valid_voltages
from nec_calc.motor_protection.calculation import calc_motor_protection
from nec_calc.motor_protection.report import render_add_to_schedule, render_schedule_section


# For a three-phase motor, one selection drives both the full-load-current
# column (Table 430.250) and the 430.52 protection category / 430.251 design group.
THREE_PHASE_TYPES: dict[str, dict[str, str]] = {
    "Squirrel-cage induction (standard)": {
        "motor_type": "Induction", "category": "squirrel_cage", "design": "b_c_d",
    },
    "Design B energy-efficient (incl. BE / CE)": {
        "motor_type": "Induction", "category": "design_b_energy_efficient", "design": "be_ce",
    },
    "Synchronous": {
        "motor_type": "Synchronous", "category": "synchronous", "design": "b_c_d",
    },
    "Wound-rotor": {
        "motor_type": "Induction", "category": "wound_rotor", "design": "b_c_d",
    },
}

CODE_LETTERS = [r["code_letter"] for r in TABLES["table_430_7_b"]["rows"]]


def _get_hp_list(phase: str) -> dict[float, str]:
    rows = TABLES.get(get_appropriate_table(phase)).get("rows")
    hp_list = get_row_headers(rows, "horsepower")
    return {
        float(sum(Fraction(s) for s in str(item).split())): str(item)
        for item in hp_list
    }


def _resolve_motor(phase: SystemTypes):
    """Return (motor_type, category_key, design_group, type_label) for the chosen phase."""
    if phase == SystemTypes.DC:
        return None, "dc", "b_c_d", "DC motor"
    if phase == SystemTypes.SINGLE_PHASE:
        return None, "single_phase", "b_c_d", "Single-phase motor"

    label = st.selectbox("Motor type / design", list(THREE_PHASE_TYPES.keys()), key="mp_type")
    cfg = THREE_PHASE_TYPES[label]
    return cfg["motor_type"], cfg["category"], cfg["design"], label

@st.fragment
def render_calc():
    inputs_pane, result_pane = st.columns([1.45,1], gap="large")
    
    with inputs_pane, st.container(border=True,):
        st.markdown("### Inputs")

        c1, c2 = st.columns(2)
        phase = enum_selectbox(c1, "Phase", SystemTypes, index=2, key="mp_phase")
        hp_list = _get_hp_list(phase.key)
        hp = enum_selectbox(
            c2, "Horsepower (HP)", options=hp_list,
            format_func=lambda m: hp_list.get(m), key="mp_hp",
        )

        motor_type, category_key, design_group, type_label = _resolve_motor(phase)

        voltages = get_valid_voltages(phase.key, hp_list.get(hp), motor_type)
        voltage = c2.selectbox("Voltage (V)", options=voltages) if voltages else None
        if voltage is None:
            st.warning(
                "NEC Tables 430.247–430.250 list no full-load current for this HP / motor type. "
                "Enter a nameplate FLA below or choose a different motor."
            )

        with st.expander("Overload sizing (NEC 430.32) — nameplate data"):
            oc1, oc2, oc3 = st.columns(3)
            nameplate_fla = oc1.number_input(
                "Nameplate FLA (A)", min_value=0.0, value=None, step=0.1, placeholder="27.5", key="mp_np_fla"
            )
            sf = enum_selectbox(oc2, "Service factor", ServiceFactors, key="mp_sf")
            temp_rise = oc3.number_input(
                "Marked temp rise (°C)", min_value=0.0, value=None, step=1.0, placeholder="40", key="mp_temp"
            )

        with st.expander("Locked-rotor current (NEC 430.7(B) / 430.251)"):
            code_letter = st.selectbox(
                "Nameplate code letter (optional)", options=[None, *CODE_LETTERS],
                format_func=lambda x: "—" if x is None else x, key="mp_code_letter",
            )

        result = calc_motor_protection(
            phase=phase.key,
            phase_label=phase.label,
            phase_factor=phase.current_factor,
            hp=hp,
            hp_label=hp_list.get(hp),
            voltage=voltage,
            motor_type=motor_type,
            category_key=category_key,
            nameplate_fla=nameplate_fla,
            service_factor=sf.key if sf else None,
            service_factor_label=sf.label if sf else None,
            temp_rise_c=temp_rise,
            design_group=design_group,
            code_letter=code_letter,
        )

    with result_pane, st.container(border=True):
        st.markdown("### Results")
        st.metric(
            "Full-load current, I_FLC (A)",
            fmt(result["flc"], "A"),
            help=f"Source: {result['flc_source'] or '—'}",
        )
        _render_branch(st.expander("Branch-circuit protection — NEC 430.52(C)(1)"), result)
        _render_overload(result)
        _render_lrc_disconnect(result)

        st.divider()
        render_add_to_schedule(result)

        with st.expander("Parameters & equations used", expanded=False):
            _render_parameters(result)
            _render_equations(result)
    st.divider()
    render_schedule_section()


def _render_parameters(result: dict) -> None:
    st.markdown("### Parameters used")

    st.write(f"- system: **{result['phase_label']}**")
    st.write(f"- motor size: **{result['hp_label']} HP**")
    if result.get("motor_type"):
        st.write(f"- motor type: **{result['motor_type']}**")
    st.write(f"- voltage: **{fmt(result['voltage'], 'V')}**")
    st.write(
        f"- full-load current (I_FLC): **{fmt(result['flc'], 'A')}** "
        f"({result['flc_source'] or '—'})"
    )
    st.write(f"- motor category (430.52): **{result['branch']['category_label'] or '—'}**")

    if result.get("nameplate_fla") is not None:
        st.write(f"- nameplate FLA: **{fmt(result['nameplate_fla'], 'A')}**")
    if result.get("service_factor_label"):
        st.write(f"- service factor: **{result['service_factor_label']}**")
    if result.get("temp_rise_c") is not None:
        st.write(f"- marked temperature rise: **{result['temp_rise_c']} °C**")
    if result["overload"]["basis"]:
        st.write(f"- overload basis (430.32): **{result['overload']['basis']}**")
    if result.get("lrc_table"):
        st.write(f"- locked-rotor table: **{TABLES[result['lrc_table']['table']]['title']}**")
    if result.get("code_letter"):
        st.write(f"- nameplate code letter: **{result['code_letter']}**")
    if result.get("lrc_code"):
        st.write(f"- code letter kVA/hp: **{fmt(result['lrc_code']['kva_per_hp'])}**")


def _render_equations(result: dict) -> None:
    st.markdown("### Equations used")

    eq(r"I_{branch}=\text{mult}\%\times I_{FLC}")
    if result["overload"]["max_overload"] is not None:
        eq(r"I_{OL}=k_{OL}\times I_{FLA,nameplate}")
    eq(r"I_{disc}=1.15\times I_{FLC}")
    if result.get("lrc_code"):
        eq(r"I_{LR}=\frac{(kVA/hp)\times hp\times 1000}{V\times k_{\phi}}")


def _render_branch(c, result: dict) -> None:
    branch = result["branch"]
    if result["flc"] is None:
        c.info("Enter a valid motor (or nameplate FLA) to size the branch device.")
        return

    rows = []
    for d in branch["devices"]:
        rows.append({
            "Device type": d["label"],
            "% FLC (Table 430.52)": f"{d['pct']}%" if d["pct"] is not None else "—",
            "Max rating (A)": fmt(d["raw"]),
            "Next standard, 240.6 (A)": fmt(d["standard"]) if d["standard"] is not None else "—",
            "Exc. 2 ceiling (A)": f"{fmt(d['max_raw'])} ({d['max_pct']}%)" if d["max_raw"] is not None else "—",
        })
    c.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    c.caption(
        f"Motor category: **{branch['category_label']}**. "
        "Exception 1 permits the next higher standard rating (240.6(A)); the instantaneous-trip "
        "value is an adjustable setting, not a standard rating. Exception 2 is the ceiling where "
        "the table value will not start the motor."
    )


def _render_overload(result: dict) -> None:
    st.markdown("##### Overload protection — NEC 430.32")
    ol = result["overload"]
    if ol["max_overload"] is None:
        st.info("Enter the nameplate FLA to size overload protection.")
        return
    m1, m2 = st.columns(2)
    m1.metric(f"Max overload ({int(ol['factor'] * 100)}%)", fmt(ol["max_overload"], "A"))
    m2.metric(f"Start allowance, 430.32(C) ({int(ol['start_factor'] * 100)}%)", fmt(ol["max_overload_start"], "A"))
    st.caption(f"Basis: {ol['basis']}. Sized on nameplate FLA per 430.32, not the Table FLC.")


def _render_lrc_disconnect(result: dict) -> None:
    st.markdown("##### Disconnecting means & locked-rotor current (NEC 430.110 / 430.251)")
    dis = result["disconnect"]
    lrc_t = result["lrc_table"]
    lrc_c = result["lrc_code"]

    cols = st.columns(3)
    cols[0].metric("Min. disconnect rating (115% FLC)", fmt(dis["min_disconnect_ampere"], "A"))
    cols[1].metric(
        "Locked-rotor current, Table 430.251 (A)",
        fmt(lrc_t["locked_rotor_current"], "A") if lrc_t else "—",
    )
    cols[2].metric(
        "Locked-rotor current, code letter (A)",
        fmt(lrc_c["locked_rotor_current"], "A") if lrc_c else "—",
    )
    if lrc_c:
        st.caption(
            f"Code letter {result['code_letter']} → {fmt(lrc_c['kva_per_hp'])} kVA/hp "
            f"→ LR = {fmt(lrc_c['locked_rotor_kva'])} kVA. "
            "Table 430.251 values are for selecting disconnects and controllers."
        )
