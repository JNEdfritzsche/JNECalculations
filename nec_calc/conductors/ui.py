import streamlit as st

from nec_calc.common.formatting import fmt
from nec_calc.common.ui_helpers import eq
from nec_calc.conductors.calculation import calc_conductors
from lib.nec_tables import (
    TABLE_310_15_B_1_1,
    TABLE_310_15_B_1_2,
    TABLE_310_15_C_1,
    TABLE_310_16,
    get_standard_conductor_sizes,
)
from nec_calc.conductors.report import render_add_to_schedule, render_schedule_section


# Temperature conversions and mappings
RATING_MAP_C = {"60 °C": "60", "75 °C": "75", "90 °C": "90"}
RATING_MAP_F = {"140 °F": "60", "167 °F": "75", "194 °F": "90"}

TERM_MAP_C = {"75 °C": "75", "60 °C": "60", "90 °C": "90", "None": None}
TERM_MAP_F = {"167 °F": "75", "140 °F": "60", "194 °F": "90", "None": None}

WIRE_TYPE_OPTIONS = [
    "THHN / THWN-2 (90°C)",
    "XHHW-2 (90°C)",
    "USE-2 / RHW-2 (90°C)",
    "THW / THWN (75°C)",
    "XHHW (75°C)",
    "TW / UF (60°C)",
    "Custom / Other",
]

WIRE_TYPE_TO_RATING = {
    "THHN / THWN-2 (90°C)": "90",
    "XHHW-2 (90°C)": "90",
    "USE-2 / RHW-2 (90°C)": "90",
    "THW / THWN (75°C)": "75",
    "XHHW (75°C)": "75",
    "TW / UF (60°C)": "60",
    "Custom / Other": None,
}


def _c_to_f(c_val: float) -> float:
    return (c_val * 9.0 / 5.0) + 32.0


def _build_ambient_options(table):
    """Build (celsius_labels, fahrenheit_labels, label_to_table_key) for an ambient correction table."""
    options_c: list[str] = []
    options_f: list[str] = []
    key_map: dict[str, str] = {}

    for row in table["rows"]:
        key = row["ambient_temp_c"]
        s = key.replace("–", "-")
        parts = s.split("-")
        label_c = f"{key} °C"

        if len(parts) == 2:
            try:
                c1, c2 = float(parts[0].strip()), float(parts[1].strip())
                f1, f2 = _c_to_f(c1), _c_to_f(c2)
                label_f = f"{f1:.0f}–{f2:.0f} °F"
            except Exception:
                label_f = f"{key} °F"
        elif "or less" in s:
            try:
                val = float(s.replace("or less", "").strip())
                f_val = _c_to_f(val)
                label_f = f"{f_val:.0f} or less °F"
            except Exception:
                label_f = f"{key} °F"
        elif "and above" in s or "or more" in s:
            try:
                val = float(s.replace("and above", "").replace("or more", "").strip())
                f_val = _c_to_f(val)
                label_f = f"{f_val:.0f} and above °F"
            except Exception:
                label_f = f"{key} °F"
        else:
            label_f = f"{key} °F"

        options_c.append(label_c)
        options_f.append(label_f)
        key_map[label_c] = key
        key_map[label_f] = key

    return options_c, options_f, key_map


AMBIENT_OPTIONS_BY_BASE = {
    "30c": _build_ambient_options(TABLE_310_15_B_1_1),
    "40c": _build_ambient_options(TABLE_310_15_B_1_2),
}

@st.fragment
def render_calc():
    inputs_pane, result_pane = st.columns([1.45,1], gap="large")
    
    with inputs_pane, st.container(border=True,):
        st.markdown("### Display Settings")
        temp_unit = st.radio(
            "Temperature display unit",
            options=["C", "F"],
            format_func=lambda u: "Metric (°C)" if u == "C" else "Imperial (°F)",
            horizontal=True,
            key="nec_cond_temp_unit",
        )

        check_wire_type = st.session_state.get("nec_cond_check_wire_type", False)
        wire_type = st.session_state.get("nec_cond_wire_type", WIRE_TYPE_OPTIONS[0]) if check_wire_type else None
        forced_rating = WIRE_TYPE_TO_RATING.get(wire_type) if check_wire_type else None

        st.markdown("### Inputs")

        c1, c2 = st.columns(2, gap="large")
        with c1:
            std_size_dict = get_standard_conductor_sizes(TABLE_310_16) or {}
            std_size_labels = list(std_size_dict.keys())
            conductor_size_label = st.selectbox(
                "Conductor size",
                options=std_size_labels,
                index=2 if len(std_size_labels) > 2 else 0, # Default 12 AWG
                key="nec_cond_conductor_size_label",
            )
            conductor_size = std_size_dict.get(conductor_size_label, "12")

            material = st.selectbox(
                "Conductor material",
                options=["cu", "al"],
                format_func=lambda k: "Copper" if k == "cu" else "Aluminum / Copper-Clad Aluminum",
                key="nec_cond_material",
            )

            rating_map = RATING_MAP_C if temp_unit == "C" else RATING_MAP_F

            if forced_rating is not None:
                rating_choice = next(k for k, v in rating_map.items() if v == forced_rating)
                temp_rating = forced_rating
                st.selectbox(
                    "Conductor insulation rating",
                    options=[rating_choice],
                    index=0,
                    disabled=True,
                    key=f"nec_cond_temp_rating_forced_{temp_unit}_{forced_rating}",
                    help=(
                        f"Locked to {rating_choice} because it's implied by the selected wire/cable "
                        "insulation type below. Choose \"Custom / Other\" there to set this manually."
                    ),
                )
            else:
                rating_choice = st.selectbox(
                    "Conductor insulation rating",
                    options=list(rating_map.keys()),
                    index=1, # 75 °C / 167 °F
                    key=f"nec_cond_temp_rating_{temp_unit}",
                )
                temp_rating = rating_map[rating_choice]

            if temp_unit == "C":
                terminal_choice = st.selectbox(
                    "Equipment terminal limit rating",
                    options=list(TERM_MAP_C.keys()),
                    index=0, # 75 °C
                    key="nec_cond_terminal_temp_C",
                )
                terminal_temp_rating = TERM_MAP_C[terminal_choice]
            else:
                terminal_choice = st.selectbox(
                    "Equipment terminal limit rating",
                    options=list(TERM_MAP_F.keys()),
                    index=0, # 167 °F
                    key="nec_cond_terminal_temp_F",
                )
                terminal_temp_rating = TERM_MAP_F[terminal_choice]

        with c2:
            ambient_base = st.selectbox(
                "Ambient temperature base table",
                options=["30c", "40c"],
                format_func=lambda k: "30°C (86°F) Base — Table 310.15(B)(1)(1)" if k == "30c" else "40°C (104°F) Base — Table 310.15(B)(1)(2)",
                key="nec_cond_ambient_base",
            )
            ambient_options_c, ambient_options_f, ambient_key_map = AMBIENT_OPTIONS_BY_BASE[ambient_base]

            if temp_unit == "C":
                default_amb_idx = ambient_options_c.index("26-30 °C") if "26-30 °C" in ambient_options_c else 0
                ambient_choice = st.selectbox(
                    "Ambient operating temperature",
                    options=ambient_options_c,
                    index=default_amb_idx,
                    key=f"nec_cond_ambient_{ambient_base}_C",
                )
            else:
                default_amb_idx = ambient_options_f.index("79–86 °F") if "79–86 °F" in ambient_options_f else 0
                ambient_choice = st.selectbox(
                    "Ambient operating temperature",
                    options=ambient_options_f,
                    index=default_amb_idx,
                    key=f"nec_cond_ambient_{ambient_base}_F",
                )
            ambient_temp_c = ambient_key_map[ambient_choice]

            cond_ranges = [r["number_of_conductors"] for r in TABLE_310_15_C_1["rows"]]
            if "1-3" not in cond_ranges:
                cond_ranges = ["1-3"] + cond_ranges
            number_of_conductors = st.selectbox(
                "Current-carrying conductors in raceway/cable",
                options=cond_ranges,
                index=0,
                key="nec_cond_number_of_conductors",
            )

        check_load = st.session_state.get("nec_cond_check_load", False)
        check_parallel = st.session_state.get("nec_cond_check_parallel", False)

        n_parallel = st.session_state.get("nec_cond_n_parallel", 1) if check_parallel else 1
        load_current_val = st.session_state.get("nec_cond_load_current", 100.0) if check_load else None

        # Perform core calculation immediately
        result = calc_conductors(
            conductor_size=conductor_size,
            material=material,
            temp_rating=temp_rating,
            ambient_base=ambient_base,
            ambient_temp_c=ambient_temp_c,
            number_of_conductors=number_of_conductors,
            terminal_temp_rating=terminal_temp_rating,
            load_current=load_current_val,
            n_parallel=n_parallel,
            wire_type=wire_type,
            temp_unit=temp_unit,
        )
        
        st.divider()
        
        st.markdown("### Optional Add-ons")
                    
        opt_col1, opt_col2, opt_col3 = st.columns(3)
        with opt_col1:
            st.checkbox("Check against design load & auto-size", key="nec_cond_check_load")
        with opt_col2:
            st.checkbox("Multiple parallel runs per phase", key="nec_cond_check_parallel")
        with opt_col3:
            st.checkbox("Specify wire / cable insulation type", key="nec_cond_check_wire_type")


        if check_load or check_parallel or check_wire_type:
            st.write("") # Spacer
            add_col1, add_col2, add_col3 = st.columns(3, gap="large")
            
            with add_col1:
                if check_load:
                    st.markdown("#### Design Load Sizing")
                    st.number_input(
                        "Design load current (A)",
                        min_value=0.0,
                        value=100.0,
                        step=1.0,
                        key="nec_cond_load_current",
                    )
                    st.write("")
                    is_ok = result.get("is_adequate")
                    if is_ok:
                        st.success("**Adequate for load:** Yes")
                    else:
                        st.error("**Adequate for load:** No (ampacity exceeded)")
                    st.metric("Minimum required conductor size", str(result.get("min_recommended_size_display", "—")))
                    
            with add_col2:
                if check_parallel:
                    st.markdown("#### Parallel Runs  \n($N_{parallel}$)")
                    st.number_input(
                        "Number of parallel runs per phase",
                        min_value=1,
                        value=2,
                        step=1,
                        key="nec_cond_n_parallel",
                    )
                    st.write("")
                    st.metric("Derated ampacity per conductor", fmt(result.get("derated_ampacity"), "A"))
                    st.metric(f"Total allowable ampacity ({n_parallel} runs)", fmt(result.get("calculated_value"), "A"))
                    
            with add_col3:
                if check_wire_type:
                    st.markdown("#### Cable Insulation Type")
                    st.selectbox(
                        "Wire / cable insulation designation",
                        options=WIRE_TYPE_OPTIONS,
                        key="nec_cond_wire_type",
                    )
                    st.write("")
                    if forced_rating is not None:
                        st.info(
                            f"**Insulation type:** {wire_type}  \n"
                            f"This locks **Conductor insulation rating** (above) to **{forced_rating}°C**."
                        )
                    else:
                        st.info(
                            f"**Insulation type:** {wire_type}  \n"
                            "Pick a specific type to auto-set the conductor insulation rating, "
                            "or leave Custom/Other and set it manually above."
                        )
        

    with result_pane, st.container(border=True):
        st.markdown("### Allowable Ampacity Results")

        m1, m2 = st.columns(2)
        
        if n_parallel > 1:
            m1.metric(f"Allowable total ampacity across {n_parallel} runs", f"{fmt(result.get('calculated_value'), 'A')}")
            st.caption(f"Based on {n_parallel} parallel runs × {fmt(result.get('allowable_single'), 'A')} per conductor.")
        else:
            m1.metric("Allowable ampacity per run  \n($I_{allowable}$)", fmt(result.get("calculated_value"), "A"))
            
        derated_val = result.get("derated_ampacity")
        m2.metric("Derated ampacity   \n($I_{derated}$)", fmt(derated_val, "A"))

        st.divider()
        render_add_to_schedule(result)  
                    
        with st.expander("Parameters & equations used:", expanded=False):
            st.markdown("### Parameters used")
            st.write(f"- conductor material: **{result.get('material_label', material)}**")
            st.write(f"- selected conductor size: **{result.get('selected_size_display', conductor_size)}**")
            if check_wire_type and wire_type:
                st.write(f"- wire / cable insulation type: **{wire_type}**")
            if check_load and load_current_val is not None:
                st.write(f"- minimum required conductor size: **{result.get('min_recommended_size_display', '—')}**")
            st.write(f"- conductor insulation temperature rating: **{rating_choice}**")
            st.write(f"- equipment terminal temperature limit: **{terminal_choice if terminal_choice else 'None'}**")
            st.write(f"- ambient temperature base table: **{result.get('ambient_base_label', ambient_base)}**")
            st.write(f"- ambient operating temperature: **{ambient_choice}**")
            st.write(f"- number of current-carrying conductors: **{number_of_conductors}**")
            if n_parallel > 1:
                st.write(f"- parallel runs per phase ($N_{{parallel}}$): **{n_parallel}**")
            if load_current_val is not None:
                st.write(f"- design load current: **{fmt(load_current_val, 'A')}**")
    
            st.write(f"- Table 310.16 base ampacity (per conductor): **{fmt(result.get('table_ampacity'), 'A')}**")
            st.write(f"- ambient correction factor ($CF_{{temp}}$): **{fmt(result.get('ambient_correction'))}**")
            st.write(f"- conductor adjustment factor ($AF_{{cond}}$): **{fmt(result.get('conductor_adjustment'))}**")
            st.write(f"- derated ampacity per conductor ($I_{{derated}}$): **{fmt(derated_val, 'A')}**")
            term_single = result.get("terminal_limit_ampacity")
            st.write(f"- terminal limit ampacity per conductor ($I_{{terminal}}$): **{fmt(term_single, 'A') if term_single is not None else 'None'}**")
            if n_parallel > 1:
                st.write(f"- total allowable circuit ampacity across {n_parallel} runs: **{fmt(result.get('calculated_value'), 'A')}**")
    
            st.markdown("### Equations used")
            eq(r"I_{\text{derated}} = I_{\text{table}} \times CF_{\text{temp}} \times AF_{\text{cond}}")
            if n_parallel > 1:
                eq(r"I_{\text{allowable, total}} = N_{\text{parallel}} \times \min(I_{\text{derated}}, I_{\text{terminal}})")
            else:
                eq(r"I_{\text{allowable}} = \min(I_{\text{derated}}, I_{\text{terminal}})")
                    
    st.divider()
    render_schedule_section()
        
