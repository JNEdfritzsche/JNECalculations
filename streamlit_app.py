import math
from pathlib import Path
import re

import streamlit as st

# --- Keep your import, but prevent the whole app from crashing if packaging is wrong ---
try:
    from lib.theory import render_md  # type: ignore
    _THEORY_IMPORT_ERROR = None
except Exception as e:
    render_md = None  # type: ignore
    _THEORY_IMPORT_ERROR = str(e)

# Optional: OESC table library (for Table Library page)
try:
    from lib import oesc_tables  # type: ignore
    _TABLES_IMPORT_ERROR = None
except Exception as e:
    oesc_tables = None  # type: ignore
    _TABLES_IMPORT_ERROR = str(e)

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="Electrical Calculations Hub",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ Electrical Calculations Hub")
st.caption("Theory • Examples • Calculators")

# ----------------------------
# Helpers
# ----------------------------
# ----------------------------
# Conduit fill rule selector (CEC / OESC Table 9 logic)
# ----------------------------
def select_table9_fill_rule(num_cables: int):
    """
    Returns which Table 9 group to use based on number of cables.
    1 cable  -> 53% (Tables C/D)
    2 cables -> 31% (Tables E/F)
    >=3      -> 40% (Tables G/H)
    """
    if num_cables <= 1:
        return {
            "percent": 53,
            "tables": ["C", "D"],
            "label": "53% fill (1 cable – Tables C/D)"
        }
    elif num_cables == 2:
        return {
            "percent": 31,
            "tables": ["E", "F"],
            "label": "31% fill (2 cables – Tables E/F)"
        }
    else:
        return {
            "percent": 40,
            "tables": ["G", "H"],
            "label": "40% fill (3+ cables – Tables G/H)"
        }

def fmt(x, unit=""):
    if x is None:
        return "—"
    try:
        x = float(x)
    except Exception:
        return str(x)
    if abs(x) >= 1e6:
        s = f"{x:,.3g}"
    elif abs(x) >= 1:
        s = f"{x:,.4g}"
    else:
        s = f"{x:.6g}"
    return f"{s} {unit}".strip()


def safe_div(a, b):
    return None if b == 0 else a / b


def header(title: str, subtitle: str = ""):
    st.header(title)
    if subtitle:
        st.write(subtitle)


def show_code_note(selected_code: str):
    st.info(
        f"Code mode: **{selected_code}**. "
        "This site is written to be easy to follow. Always verify final selections against the code, "
        "project specs, equipment data, and a coordination study where required."
    )


def eq(latex: str):
    """Render a LaTeX equation in a consistent display style."""
    st.latex(latex)


# ----------------------------
# Content paths (reliable on Streamlit Cloud)
# ----------------------------
APP_DIR = Path(__file__).parent
CONTENT_DIR = APP_DIR / "content"


def render_md_safe(rel_path: str):
    """
    Render markdown from /content safely.
    - Uses lib.theory.render_md if available
    - Otherwise shows a friendly error instead of crashing the app
    """
    md_path = CONTENT_DIR / rel_path

    if render_md is None:
        st.error(
            "Theory renderer failed to import. This usually means the `lib/` package is missing in your repo. "
            "Make sure you have:\n\n"
            "- `lib/__init__.py`\n"
            "- `lib/theory.py`\n"
        )
        if _THEORY_IMPORT_ERROR is not None:
            with st.expander("Import error details"):
                st.exception(_THEORY_IMPORT_ERROR)
        st.info(f"Expected markdown path: `{md_path}`")
        if md_path.exists():
            st.warning("Markdown file exists, but renderer is unavailable due to the import error above.")
        else:
            st.warning("Markdown file not found at the expected path.")
        return

    # renderer exists
    render_md(str(md_path))


# Standard device rating helpers
NEC_2406A_STANDARD = [
    15, 20, 25, 30, 35, 40, 45, 50,
    60, 70, 80, 90, 100, 110, 125, 150,
    175, 200, 225, 250, 300, 350, 400, 450,
    500, 600, 700, 800, 1000, 1200, 1600, 2000,
    2500, 3000, 4000, 5000, 6000
]

# Practical "standard" list used by the attached OESC calc (Table 13 style). This list is commonly aligned with the NEC list.
OESC_TABLE13_STANDARD = NEC_2406A_STANDARD[:]


def next_standard(value, standard_list):
    """Return the next standard value >= value. If value exceeds list, return None."""
    try:
        v = float(value)
    except Exception:
        return None
    for s in standard_list:
        if s >= v - 1e-12:
            return s
    return None


def calc_fla(kva, volts, phase):
    """
    FLA from kVA and voltage.
    - 3Φ: I = S / (sqrt(3)*V_LL)
    - 1Φ: I = S / V
    """
    s_va = float(kva) * 1000.0
    v = float(volts)
    if phase == "3Φ":
        return s_va / (math.sqrt(3) * v) if v > 0 else None
    return s_va / v if v > 0 else None


# ----------------------------
# Sidebar navigation
# ----------------------------
PAGES = [
    "Transformer Protection",
    "Transformer Feeders",
    "Grounding/Bonding Conductor Sizing",
    "Motor Protection",
    "Motor Feeder",
    "Cable Tray Size & Fill & Bend Radius",
    "Conduit Size & Fill & Bend Radius",
    "Cable Tray Ampacity",
    "Demand Load",
    "Voltage Drop",
    "Conductors",
    "Table Library",
]

with st.sidebar:
    st.header("Navigate")
    page = st.radio("Go to", PAGES, index=0)

    st.divider()
    st.header("Jurisdiction")
    code_mode = st.selectbox("Select electrical code", ["NEC", "OESC"], index=0)

    st.divider()
    st.caption("Template site — expand/replace theory, tables, and calculators as needed.")

# ----------------------------
# Page shell with Theory/Calculator tabs
# (Tabs are disabled ONLY on Table Library)
# ----------------------------
if page != "Table Library":
    theory_tab, calc_tab = st.tabs(["📚 Theory", "🧮 Calculator"])
else:
    theory_tab = None
    calc_tab = None


# ============================
# 1) Transformer Protection
# ============================
if page == "Transformer Protection":
    with theory_tab:
        header("Transformer Protection", "Code-focused theory and worked examples (moved to Markdown).")
        show_code_note(code_mode)

        if code_mode == "OESC":
            render_md_safe("transformer_protection_oesc.md")
        else:
            render_md_safe("transformer_protection_nec.md")

    # ----------------------------
    # Calculator tab for Transformer Protection
    # ----------------------------
    with calc_tab:
        header("Transformer Protection Calculator", "Compute transformer currents + code-based OCPD limits (per attached calc documents).")
        show_code_note(code_mode)

        st.markdown("### Inputs")
        c1, c2, c3, c4 = st.columns([1, 1, 1, 1], gap="large")
        with c1:
            phase = st.selectbox("System", ["3Φ", "1Φ"], index=0, key="tp_phase")
        with c2:
            kva = st.number_input("Transformer size (kVA)", min_value=0.1, value=75.0, step=1.0, key="tp_kva")
        with c3:
            vpri = st.number_input("Primary voltage (V)", min_value=1.0, value=600.0, step=1.0, key="tp_vpri")
        with c4:
            vsec = st.number_input("Secondary voltage (V)", min_value=1.0, value=208.0, step=1.0, key="tp_vsec")

        st.caption(
            "Units note: This calculator assumes kVA and volts. For 3Φ, it uses line-to-line voltage. "
            "Use nameplate FLA when available."
        )

        st.markdown("### Full-load current (nameplate optional)")
        use_nameplate = st.checkbox("Use nameplate FLA inputs instead of calculating from kVA/V", value=False, key="tp_use_nameplate")

        if use_nameplate:
            n1, n2 = st.columns(2, gap="large")
            with n1:
                Ip = st.number_input("Nameplate Primary FLA (A)", min_value=0.01, value=72.0, step=0.01, key="tp_Ip_nameplate")
            with n2:
                Is = st.number_input("Nameplate Secondary FLA (A)", min_value=0.01, value=208.0, step=0.01, key="tp_Is_nameplate")
        else:
            Ip = calc_fla(kva, vpri, phase)
            Is = calc_fla(kva, vsec, phase)

        m1, m2 = st.columns(2)
        m1.metric("Primary FLA", fmt(Ip, "A"))
        m2.metric("Secondary FLA", fmt(Is, "A"))

        st.divider()
        st.markdown("### Code-based OCPD limits")

        # ----------------------------
        # OESC calculator
        # ----------------------------
        if code_mode == "OESC":
            st.subheader("OESC — Rule-based sizing (implemented per the attached OESC calculation)")

            cc1, cc2, cc3 = st.columns([1.2, 1.2, 1.2], gap="large")
            with cc1:
                xfmr_type = st.selectbox("Transformer type", ["Oil-cooled (non-dry)", "Dry-type"], index=0, key="tp_oesc_type")
            with cc2:
                voltage_class = st.selectbox("Voltage class selection", ["> 750 V", "≤ 750 V"], index=1 if vpri <= 750 else 0, key="tp_oesc_vclass")
            with cc3:
                round_to_std = st.checkbox("Round up to standard rating (Table 13 style)", value=True, key="tp_oesc_round")

            rule_options = []
            if voltage_class == "> 750 V":
                rule_options = ["26-250 (>750V) — Primary fuses 150% / breakers 300% (direct primary protection)"]
            else:
                if xfmr_type == "Dry-type":
                    rule_options = [
                        "26-254 (≤750V dry-type) — Primary 125% (direct primary protection)",
                        "26-254 (≤750V dry-type) — Secondary device 125% + Primary feeder device 300% (no individual primary at transformer)",
                    ]
                else:
                    rule_options = [
                        "26-252 (≤750V non-dry) — Primary per 150% / 167% / 300% allowances (direct primary protection)",
                        "26-252 (≤750V non-dry) — Secondary device 125% + Primary feeder device 300% (no individual primary at transformer)",
                    ]

            rule_path = st.selectbox("OESC rule path", rule_options, index=0, key="tp_oesc_rule_path")
            std_list = OESC_TABLE13_STANDARD

            def show_oesc_result(label, raw):
                std = next_standard(raw, std_list) if round_to_std else None
                if round_to_std:
                    if std is None:
                        st.error(f"{label}: Raw = **{fmt(raw,'A')}** → exceeds standard list. Enter final device manually.")
                    else:
                        st.success(f"{label}: Raw = **{fmt(raw,'A')}** → Selected standard = **{fmt(std,'A')}**")
                else:
                    st.success(f"{label}: **{fmt(raw,'A')}**")

            if rule_path.startswith("26-250"):
                st.markdown("#### 26-250 (>750 V) — Direct primary protection (per calc document)")
                if Ip is None:
                    st.error("Primary FLA could not be computed. Check inputs.")
                else:
                    raw_fuse = 1.50 * Ip
                    raw_brk = 3.00 * Ip
                    show_oesc_result("Max Primary Fuse (150%)", raw_fuse)
                    show_oesc_result("Max Primary Breaker (300%)", raw_brk)

                    with st.expander("Optional: show secondary reference values (not a required selection in this direct-primary example)", expanded=False):
                        if Is is None:
                            st.warning("Secondary FLA unavailable.")
                        else:
                            st.info("The attached calculation worksheet also shows secondary-side reference values using the same multipliers.")
                            show_oesc_result("Secondary @ 150% (reference)", 1.50 * Is)
                            show_oesc_result("Secondary @ 300% (reference)", 3.00 * Is)

            elif rule_path.startswith("26-252") and "direct primary" in rule_path.lower():
                st.markdown("#### 26-252 (≤750 V, non-dry) — Direct primary protection (per calc document)")
                if Ip is None:
                    st.error("Primary FLA could not be computed. Check inputs.")
                else:
                    if Ip < 2.0:
                        mult = 3.00
                        reason = "Ip < 2 A → up to 300% permitted."
                    elif Ip < 9.0:
                        mult = 1.67
                        reason = "Ip < 9 A → up to 167% permitted."
                    else:
                        mult = 1.50
                        reason = "Ip ≥ 9 A → up to 150% permitted; if not a standard size, next higher standard permitted."

                    raw_primary = mult * Ip
                    st.caption(reason)
                    show_oesc_result(f"Max Primary OCPD ({mult:.2f}×)", raw_primary)

                    with st.expander("Optional: show secondary reference value from worksheet style", expanded=False):
                        if Is is None:
                            st.warning("Secondary FLA unavailable.")
                        else:
                            st.info("The attached worksheet also shows a secondary reference value using the same multiplier for this example format.")
                            show_oesc_result(f"Secondary @ {mult:.2f}× (reference)", mult * Is)

            elif rule_path.startswith("26-252") and "secondary device" in rule_path.lower():
                st.markdown("#### 26-252 (≤750 V, non-dry) — Secondary device + primary feeder allowance (per calc document)")
                if (Ip is None) or (Is is None):
                    st.error("Primary/Secondary FLA could not be computed. Check inputs.")
                else:
                    raw_sec_dev = 1.25 * Is
                    raw_pri_feeder = 3.00 * Ip
                    show_oesc_result("Max Secondary OCPD (125% of secondary FLA)", raw_sec_dev)
                    show_oesc_result("Max Primary Feeder OCPD (300% of primary FLA)", raw_pri_feeder)
                    st.caption(
                        "This path reflects the allowance summarized in the attached OESC calculation: "
                        "secondary-side device ≤125% and upstream primary feeder device ≤300% (verify rule conditions for your installation)."
                    )

            elif rule_path.startswith("26-254") and "direct primary" in rule_path.lower():
                st.markdown("#### 26-254 (≤750 V, dry-type) — Direct primary protection (per calc document)")
                if Ip is None:
                    st.error("Primary FLA could not be computed. Check inputs.")
                else:
                    raw_primary = 1.25 * Ip
                    show_oesc_result("Max Primary OCPD (125%)", raw_primary)

                    st.markdown("**Inrush withstand checks (Appendix guidance in calc):**")
                    st.write(f"12× FLA for 0.1 s: **{fmt(Ip * 12, 'A')}**")
                    st.write(f"25× FLA for 0.01 s: **{fmt(Ip * 25, 'A')}**")
                    st.caption("Verify manufacturer curves to confirm withstand/ride-through capability.")

                    with st.expander("Optional: show secondary reference value from worksheet style", expanded=False):
                        if Is is None:
                            st.warning("Secondary FLA unavailable.")
                        else:
                            show_oesc_result("Secondary @ 125% (reference)", 1.25 * Is)

            elif rule_path.startswith("26-254") and "secondary device" in rule_path.lower():
                st.markdown("#### 26-254 (≤750 V, dry-type) — Secondary device + primary feeder allowance (per calc document)")
                if (Ip is None) or (Is is None):
                    st.error("Primary/Secondary FLA could not be computed. Check inputs.")
                else:
                    raw_sec_dev = 1.25 * Is
                    raw_pri_feeder = 3.00 * Ip
                    show_oesc_result("Max Secondary OCPD (125% of secondary FLA)", raw_sec_dev)
                    show_oesc_result("Max Primary Feeder OCPD (300% of primary FLA)", raw_pri_feeder)

                    st.markdown("**Inrush withstand checks (Appendix guidance in calc):**")
                    st.write(f"12× FLA for 0.1 s: **{fmt(Ip * 12, 'A')}**")
                    st.write(f"25× FLA for 0.01 s: **{fmt(Ip * 25, 'A')}**")

                    st.caption(
                        "This path reflects the allowance summarized in the attached OESC calculation: "
                        "secondary-side device ≤125% and upstream primary feeder device ≤300% (verify rule conditions for your installation)."
                    )

            else:
                st.warning("Selected OESC path not recognized. Check selections.")

        # ----------------------------
        # NEC calculator
        # ----------------------------
        else:
            st.subheader("NEC — Table-based sizing (implemented per the attached NEC calculation)")

            nc1, nc2, nc3 = st.columns([1.1, 1.1, 1.1], gap="large")
            with nc1:
                nec_case = st.selectbox(
                    "NEC case",
                    [
                        "450.3(A) — Transformers >1000V (Z ≤ 6%, Any location) — multipliers per attached calc",
                        "450.3(B) — Transformers ≤1000V (currents ≥ 9A) — multipliers per attached calc",
                    ],
                    index=1 if vpri <= 1000 else 0,
                    key="tp_nec_case",
                )
            with nc2:
                round_to_std = st.checkbox("Round up to standard rating (NEC 240.6(A) list)", value=True, key="tp_nec_round")
            with nc3:
                show_notes = st.checkbox("Show table-note reminders (Note 1 / Note 2)", value=True, key="tp_nec_notes")

            std_list = NEC_2406A_STANDARD

            def show_nec_result(label, raw, over_1000v=False):
                std = next_standard(raw, std_list) if round_to_std else None
                if round_to_std:
                    if std is None:
                        st.error(f"{label}: Raw = **{fmt(raw,'A')}** → exceeds standard list. Enter final device manually.")
                    else:
                        st.success(f"{label}: Raw = **{fmt(raw,'A')}** → Selected = **{fmt(std,'A')}**")
                else:
                    st.success(f"{label}: **{fmt(raw,'A')}**")

                if over_1000v:
                    st.caption("For >1000 V cases, Table 450.3 Note 1 allows next higher **commercially available** rating/setting (not strictly the 240.6(A) list).")

            if show_notes:
                st.markdown(
                    """
**Table-note reminders (from the attached NEC calc narrative):**  
- **Note 1:** If the calculated rating/setting is not standard, the next higher is permitted (standard for ≤1000 V; commercially available for >1000 V).  
- **Note 2:** If secondary protection is required, up to **six** breakers or **six** fuse sets may be grouped; the **sum** of device ratings must not exceed the allowed single-device value.
"""
                )

            if nec_case.startswith("450.3(A)"):
                st.markdown("#### 450.3(A) (>1000 V) — Implemented multipliers (Z ≤ 6%, Any location) per attached calc")
                if (Ip is None) or (Is is None):
                    st.error("Primary/Secondary FLA could not be computed. Check inputs.")
                else:
                    raw_pri_brk = 6.00 * Ip
                    raw_pri_fuse = 3.00 * Ip
                    raw_sec_brk = 3.00 * Is
                    raw_sec_fuse = 2.50 * Is

                    show_nec_result("Max Primary Breaker (6.00×)", raw_pri_brk, over_1000v=True)
                    show_nec_result("Max Primary Fuse (3.00×)", raw_pri_fuse, over_1000v=True)
                    show_nec_result("Max Secondary Breaker (3.00×)", raw_sec_brk, over_1000v=True)
                    show_nec_result("Max Secondary Fuse (2.50×)", raw_sec_fuse, over_1000v=True)

                    st.caption(
                        "These multipliers match the attached NEC calculation example for a >1000 V transformer with impedance ≤ 6% in an 'any location' installation."
                    )

            else:
                st.markdown("#### 450.3(B) (≤1000 V) — Implemented multipliers (currents ≥ 9A) per attached calc")
                scheme = st.radio(
                    "Protection scheme",
                    ["Primary-only protection", "Primary + Secondary protection"],
                    horizontal=True,
                    key="tp_nec_4503b_scheme",
                )

                if (Ip is None) or (Is is None):
                    st.error("Primary/Secondary FLA could not be computed. Check inputs.")
                else:
                    if Ip < 9.0:
                        st.warning(
                            "The attached NEC worksheet implements the ≥9A case. Your primary FLA is < 9A. "
                            "Refer directly to NEC Table 450.3(B) for the correct small-current conditions."
                        )

                    if scheme == "Primary-only protection":
                        raw_primary = 1.25 * Ip
                        show_nec_result("Max Primary OCPD (1.25×)", raw_primary, over_1000v=False)
                        st.caption("This matches the attached NEC calculation 'Primary Only ≥9A Multiplier: 1.25'.")
                    else:
                        raw_primary = 2.50 * Ip
                        raw_secondary = 1.25 * Is
                        show_nec_result("Max Primary OCPD (2.50×)", raw_primary, over_1000v=False)
                        show_nec_result("Max Secondary OCPD (1.25×)", raw_secondary, over_1000v=False)
                        st.caption(
                            "These multipliers match the attached NEC calculation 'Primary + Secondary' scheme for ≤1000 V with currents ≥ 9A."
                        )

        st.divider()
        st.markdown("### Equations used")
        if phase == "3Φ":
            eq(r"I=\frac{S}{\sqrt{3}\,V}")
        else:
            eq(r"I=\frac{S}{V}")
        st.caption("Where S is in VA and V is in volts (or kVA with kV).")


# ============================
# 2) Transformer Feeders
# ============================
elif page == "Transformer Feeders":
    with theory_tab:
        header("Transformer Feeders — Theory")
        show_code_note(code_mode)
        render_md_safe("transformer_feeders.md")

    with calc_tab:
        header("Transformer Feeder Calculator", "Compute secondary FLA and a simple ampacity target.")
        show_code_note(code_mode)

        col1, col2 = st.columns(2, gap="large")
        with col1:
            kva = st.number_input("Transformer size (kVA)", min_value=0.1, value=150.0, step=1.0, key="tf_kva")
        with col2:
            vsec = st.number_input("Secondary voltage (V LL)", min_value=1.0, value=208.0, step=1.0, key="tf_vsec")

        continuous = st.checkbox("Treat as continuous load (125%)", value=True, key="tf_cont")
        Is = (kva * 1000.0) / (math.sqrt(3) * vsec)
        target = Is * (1.25 if continuous else 1.0)

        st.metric("Secondary full-load current (A)", fmt(Is, "A"))
        st.success(f"Feeder ampacity target: **{fmt(target, 'A')}**")
        st.markdown("### Equations used")
        eq(r"I_{sec}=\frac{S}{\sqrt{3}\,V_{sec}}")
        eq(r"I_{target}=1.25\cdot I_{sec}")


# ============================
# 3) Grounding/Bonding Conductor Sizing
# ============================
elif page == "Grounding/Bonding Conductor Sizing":
    with theory_tab:
        header("Grounding & Bonding — Theory")
        show_code_note(code_mode)
        render_md_safe("grounding_bonding.md")

    with calc_tab:
        header("Grounding/Bonding Helper", "Simple placeholder — replace with real NEC/OESC table logic.")
        show_code_note(code_mode)

        ocpd = st.number_input("Upstream OCPD rating (A)", min_value=1.0, value=200.0, step=1.0)

        if ocpd <= 60:
            egc = "10 AWG Cu (placeholder)"
        elif ocpd <= 100:
            egc = "8 AWG Cu (placeholder)"
        elif ocpd <= 200:
            egc = "6 AWG Cu (placeholder)"
        elif ocpd <= 400:
            egc = "3 AWG Cu (placeholder)"
        else:
            egc = "See table / engineer (placeholder)"

        st.success(f"Equipment grounding conductor (example placeholder): **{egc}**")
        st.markdown("### Equation used")
        eq(r"\text{EGC size} = f(\text{OCPD rating})")


# ============================
# 4) Motor Protection
# ============================
elif page == "Motor Protection":
    with theory_tab:
        header("Motor Protection — Theory")
        show_code_note(code_mode)
        render_md_safe("motor_protection.md")

    with calc_tab:
        header("Motor Protection Calculator", "Estimate overload and short-circuit device settings.")
        show_code_note(code_mode)

        fla = st.number_input("Motor full-load amps (FLA)", min_value=0.1, value=28.0, step=0.1)
        ol_mult = st.selectbox("Overload multiplier (k)", ["1.15", "1.25"], index=1)
        sc_mult = st.selectbox("Short-circuit multiplier (m)", ["1.75", "2.50"], index=0)

        ol = fla * float(ol_mult)
        sc = fla * float(sc_mult)

        c1, c2 = st.columns(2)
        c1.metric("Overload setting (A)", fmt(ol, "A"))
        c2.metric("Short-circuit device (A)", fmt(sc, "A"))

        st.markdown("### Equations used")
        eq(r"I_{OL}=k\cdot I_{FLA}")
        eq(r"I_{SC}=m\cdot I_{FLA}")


# ============================
# 5) Motor Feeder
# ============================
elif page == "Motor Feeder":
    with theory_tab:
        header("Motor Feeder — Theory")
        show_code_note(code_mode)
        render_md_safe("motor_feeder.md")

    with calc_tab:
        header("Motor Feeder Calculator", "Single-motor conductor ampacity target (template).")
        show_code_note(code_mode)

        fla = st.number_input("Motor FLA (A)", min_value=0.1, value=40.0, step=0.1, key="mf_fla")
        cont = st.checkbox("Apply 125% factor", value=True)
        target = fla * (1.25 if cont else 1.0)
        st.success(f"Conductor ampacity target: **{fmt(target, 'A')}**")

        st.markdown("### Equation used")
        eq(r"I_{target}=1.25\cdot I_{FLA}")


# ============================
# 6) Cable Tray Size & Fill & Bend Radius
# ============================
elif page == "Cable Tray Size & Fill & Bend Radius":
    with theory_tab:
        header("Cable Tray Size, Fill & Bend Radius — Theory")
        show_code_note(code_mode)
        render_md_safe("cable_tray_fill.md")

    with calc_tab:
        header("Tray Fill & Bend Radius Calculator", "Estimate cable area + bend radius.")
        show_code_note(code_mode)

        col1, col2, col3 = st.columns(3, gap="large")
        with col1:
            n = st.number_input("Number of cables", min_value=1, value=20, step=1)
        with col2:
            od_mm = st.number_input("Cable OD (mm)", min_value=1.0, value=20.0, step=0.5)
        with col3:
            br_mult = st.selectbox("Bend radius multiplier (k)", ["8", "12", "16"], index=1)

        cable_area_mm2 = n * math.pi * (od_mm / 2.0) ** 2
        bend_radius_mm = float(br_mult) * od_mm

        st.metric("Estimated total cable area", fmt(cable_area_mm2, "mm²"))
        st.success(f"Suggested bend radius (rule-of-thumb): **{fmt(bend_radius_mm, 'mm')}**")

        st.markdown("### Equations used")
        eq(r"A_{cables}\approx n\cdot \pi\left(\frac{d}{2}\right)^2")
        eq(r"R_{min}=k\cdot d")


# ============================
# 7) Conduit Size & Fill & Bend Radius
# ============================

elif page == "Conduit Size & Fill & Bend Radius":
    with theory_tab:
        header("Conduit Size, Fill & Bend Radius — Theory")
        show_code_note(code_mode)
        render_md_safe("conduit_fill.md")

    with calc_tab:
        header("Conduit Fill Calculator — OESC Table 6 + Table 9 (dynamic cables)", "Select a conduit, add any number of cable groups, and the app computes conduit fill.")
        show_code_note(code_mode)

        st.markdown(
            "This tool is designed to behave like common conduit-fill calculators:\n"
            "- Pick a **conduit type** and **trade size** (Table 9)\n"
            "- Add one or more **cable groups** (Table 6)\n"
            "- The calculator totals cable areas and compares against **Table 9 allowable fill**\n\n"
            "If the embedded OESC Table Library is unavailable in your deployment, a **manual fallback** is provided."
        )

        # ----------------------------
        # Table helpers (Table 6 + Table 9)
        # ----------------------------
        try:
            import pandas as pd  # type: ignore
        except Exception:
            pd = None  # type: ignore

        def _norm(s):
            return str(s).strip()

        def _lower(s):
            return _norm(s).lower()

        def _to_float(x):
            try:
                if x is None:
                    return None
                if isinstance(x, (int, float)):
                    return float(x)
                s = str(x).strip()
                if s in ("", "—", "-", "–", "None"):
                    return None
                # remove commas
                s = s.replace(",", "")
                return float(s)
            except Exception:
                return None

        def _best_col(cols, include=(), exclude=()):
            """Return first column name that contains ALL include tokens and NONE of exclude tokens (case-insensitive)."""
            for c in cols:
                lc = _lower(c)
                ok = True
                for t in include:
                    if t not in lc:
                        ok = False
                        break
                if not ok:
                    continue
                for t in exclude:
                    if t in lc:
                        ok = False
                        break
                if ok:
                    return c
            return None

        @st.cache_data(show_spinner=False)
        def _load_table_df(table_id: str):
            if oesc_tables is None:
                return None
            try:
                return oesc_tables.get_table_dataframe(table_id)
            except Exception:
                return None

        def _table6_to_maps(df):
            """
            Convert Table 6 into:
              - types: list[str]
              - sizes_by_type: dict[type -> list[size]]
              - area_lookup: dict[type -> dict[size -> area_mm2]]
            Works with both "wide" and "long" table layouts.
            """
            if df is None:
                return [], {}, {}

            # Normalize to DataFrame if possible
            if pd is not None and not isinstance(df, pd.DataFrame):
                try:
                    df = pd.DataFrame(df)
                except Exception:
                    return [], {}, {}

            if pd is None or not hasattr(df, "columns"):
                return [], {}, {}

            cols = list(df.columns)

            # Guess a "size" column
            size_col = _best_col(cols, include=("size",)) or cols[0]

            # LONG format candidates: has columns like Type/Insulation, Size, Area
            type_col = _best_col(cols, include=("type",)) or _best_col(cols, include=("cable",)) or _best_col(cols, include=("insul",))
            area_col = _best_col(cols, include=("area",)) or _best_col(cols, include=("mm",)) or _best_col(cols, include=("mm2",)) or _best_col(cols, include=("mm²",))

            # If we can confidently interpret as long format, do it
            if type_col and area_col:
                area_lookup = {}
                for _, r in df.iterrows():
                    t = _norm(r.get(type_col, ""))
                    s = _norm(r.get(size_col, ""))
                    a = _to_float(r.get(area_col, None))
                    if not t or not s or a is None:
                        continue
                    area_lookup.setdefault(t, {})[s] = a
                types = sorted(area_lookup.keys())
                sizes_by_type = {t: list(area_lookup[t].keys()) for t in types}
                # Keep a stable (human-ish) order if possible
                for t in types:
                    sizes_by_type[t] = sorted(sizes_by_type[t], key=lambda x: (len(x), x))
                return types, sizes_by_type, area_lookup

            # Otherwise, treat as WIDE:
            # - First column is size, other columns are cable types holding areas
            other_cols = [c for c in cols if c != size_col]
            area_lookup = {}
            for c in other_cols:
                t = _norm(c)
                for _, r in df.iterrows():
                    s = _norm(r.get(size_col, ""))
                    a = _to_float(r.get(c, None))
                    if not s or a is None:
                        continue
                    area_lookup.setdefault(t, {})[s] = a
            types = [t for t in other_cols if t in area_lookup]
            sizes_by_type = {t: list(area_lookup[t].keys()) for t in types}
            for t in types:
                sizes_by_type[t] = sorted(sizes_by_type[t], key=lambda x: (len(x), x))
            return types, sizes_by_type, area_lookup

        def _table9_to_index(df):
            """
            Convert Table 9 into a normalized index:
              rows[(conduit_type, trade_size)] = dict of the original row values
            Attempts to find the conduit type and size columns.
            """
            if df is None:
                return None, None, {}

            if pd is not None and not isinstance(df, pd.DataFrame):
                try:
                    df = pd.DataFrame(df)
                except Exception:
                    return None, None, {}

            cols = list(df.columns) if hasattr(df, "columns") else []
            if not cols:
                return None, None, {}

            type_col = (
                _best_col(cols, include=("type",), exclude=("cable",))
                or _best_col(cols, include=("conduit",), exclude=("area", "id", "internal"))
                or cols[0]
            )
            size_col = (
                _best_col(cols, include=("trade", "size"))
                or _best_col(cols, include=("size",), exclude=("internal", "area", "mm"))
                or (cols[1] if len(cols) > 1 else cols[0])
            )

            idx = {}
            try:
                for _, r in df.iterrows():
                    t = _norm(r.get(type_col, ""))
                    s = _norm(r.get(size_col, ""))
                    if not t or not s:
                        continue
                    idx[(t, s)] = {c: r.get(c, None) for c in cols}
            except Exception:
                pass

            return type_col, size_col, idx

        def _infer_internal_area(row_dict):
            """Try to find an internal area field (mm²)."""
            cols = list(row_dict.keys())
            # Strong signals first
            c = _best_col(cols, include=("internal", "area")) or _best_col(cols, include=("area",), exclude=("allow", "max", "fill", "cable", "cond"))
            if c:
                return _to_float(row_dict.get(c))
            # Next: any numeric-looking column with 'mm' and '2'
            for cc in cols:
                lc = _lower(cc)
                if ("mm" in lc and ("2" in lc or "²" in lc)) and ("allow" not in lc and "fill" not in lc and "max" not in lc):
                    v = _to_float(row_dict.get(cc))
                    if v:
                        return v
            return None

        def _infer_allowed_area_and_pct(row_dict, n_cables_total, internal_area):
            """
            Try to infer allowed area and allowed percent from Table 9 row.
            Returns (allowed_area_mm2, allowed_pct_fraction, source_label)
            """
            cols = list(row_dict.keys())

            # Candidate columns by count bucket
            if n_cables_total <= 1:
                tokens = ("1",)
            elif n_cables_total == 2:
                tokens = ("2",)
            else:
                tokens = ("3",)  # could be "3+", "3 or more"
            # Area-first lookup
            area_candidates = []
            for c in cols:
                lc = _lower(c)
                if all(t in lc for t in tokens) and ("area" in lc or "mm" in lc or "mm2" in lc or "mm²" in lc) and ("%" not in lc):
                    area_candidates.append(c)
            # Also accept "3+" written forms
            if n_cables_total >= 3:
                for c in cols:
                    lc = _lower(c)
                    if (("3+" in lc) or ("3 or" in lc) or ("3 or more" in lc) or ("more" in lc)) and ("area" in lc or "mm" in lc) and ("%" not in lc):
                        if c not in area_candidates:
                            area_candidates.append(c)

            for c in area_candidates:
                a = _to_float(row_dict.get(c))
                if a is not None:
                    pct = (a / internal_area) if (a is not None and internal_area) else None
                    return a, pct, f"Table 9 column: {c}"

            # Percent columns (if table stores % directly)
            pct_candidates = []
            for c in cols:
                lc = _lower(c)
                if all(t in lc for t in tokens) and ("%" in lc or "percent" in lc or "fill" in lc or "max" in lc):
                    pct_candidates.append(c)
            if n_cables_total >= 3:
                for c in cols:
                    lc = _lower(c)
                    if (("3+" in lc) or ("3 or" in lc) or ("more" in lc)) and ("%" in lc or "percent" in lc or "fill" in lc or "max" in lc):
                        if c not in pct_candidates:
                            pct_candidates.append(c)

            for c in pct_candidates:
                p = _to_float(row_dict.get(c))
                if p is None:
                    continue
                # If stored like 40 (meaning %), convert to fraction
                pct_fraction = p / 100.0 if p > 1.0 else p
                a = internal_area * pct_fraction if internal_area else None
                return a, pct_fraction, f"Table 9 column: {c}"

            # Fallback: standard conduit-fill rules (common convention)
            if internal_area:
                if n_cables_total <= 1:
                    pct_fraction = 0.53
                elif n_cables_total == 2:
                    pct_fraction = 0.31
                else:
                    pct_fraction = 0.40
                return internal_area * pct_fraction, pct_fraction, "Fallback: 53%/31%/40% rule (no Table 9 match found)"

            return None, None, "No allowable fill available"

        # ----------------------------
        # Load tables (best effort)
        # ----------------------------
        t6_df = None
        t9_df = None
        if _TABLES_IMPORT_ERROR:
            st.warning(f"Embedded table library unavailable: `{_TABLES_IMPORT_ERROR}`")
        else:
            # Table IDs are typically "6" and "9" in the library; if your library uses variants like "6A"/"9H",
            # the manual fallback below still works and you can adjust IDs in lib/oesc_tables.py later.
            t6_df = _load_table_df("6")
            t9_df = _load_table_df("9")

        t6_types, t6_sizes_by_type, t6_area = _table6_to_maps(t6_df)
        t9_type_col, t9_size_col, t9_index = _table9_to_index(t9_df)

        # ----------------------------
        # Conduit selection (Table 9 or manual fallback)
        # ----------------------------
        st.markdown("## 1) Conduit selection (Table 9)")

        use_manual_conduit = st.checkbox(
            "Use manual conduit data (if Table 9 is missing or you want to override it)",
            value=False if t9_index else True,
            key="cf_use_manual_conduit",
        )

        conduit_internal_area = None
        conduit_allowed_area = None
        conduit_allowed_pct = None
        allowed_source = "—"

        if use_manual_conduit:
            c1, c2, c3 = st.columns([1, 1, 1], gap="large")
            with c1:
                conduit_type = st.text_input("Conduit type (label)", value="(Manual)", key="cf_manual_type")
            with c2:
                conduit_trade = st.text_input("Trade size (label)", value="(Manual)", key="cf_manual_size")
            with c3:
                conduit_internal_area = st.number_input("Conduit internal area (mm²)", min_value=0.01, value=500.0, step=10.0, key="cf_manual_area")

            st.caption("Manual mode: allowable fill uses 53%/31%/40% convention (unless you override below).")
            n_cables_dummy = st.number_input("Cables in raceway (for allowable fill selection)", min_value=1, value=3, step=1, key="cf_manual_n_cables")
            conduit_allowed_area, conduit_allowed_pct, allowed_source = _infer_allowed_area_and_pct(
                {}, int(n_cables_dummy), conduit_internal_area
            )
        else:
            # Prefer using the combined Table 9 dataframe column headers as conduit-type labels when available.
            # ======= OESC Table 9 column -> OESC trimmed header mapping =======
            # This mapping maps the dataframe column headers (as produced by _df_table9)
            # to the human-friendly OESC Table header strings (trimmed of the leading
            # "Internal diameter and cross-sectional areas of"). The display names are
            # what the user will see in the dropdown; the code will still use the
            # dataframe column keys for lookups.
            OESC_COLUMN_TO_HEADER = {
                "Rigid Metal": "Rigid metal conduit",
                "Flexible Metal": "Flexible metal conduit",
                "Rigid Pvc": "Rigid PVC conduit",
                "Rigid Pvc Db2 Es2": "Rigid Type EB1/DB2/ES2 PVC conduit",
                "Metallic Liquid Tight Flex": "metallic liquid-tight flexible conduit",
                "Nonmetallic Liquid Tight Flex": "non-metallic liquid-tight flexible conduit",
                "Emt": "electrical metallic tubing",
                "Ent": "electrical non-metallic tubing",
                "Rtrc Ips": "rigid RTRC conduit marked IPS",
                "Rtrc Id": "rigid RTRC conduit marked ID",
                "Hdpe Sch40": "HDPE conduit Schedule 40",
                "Hdpe Sch80": "HDPE conduit Schedule 80",
                "Hdpe Dr9": "HDPE DR9 conduit",
                "Hdpe Dr11": "HDPE DR11 conduit",
                "Hdpe Dr13 5": "HDPE DR13.5 conduit",
                "Hdpe Dr15 5": "HDPE DR15.5 conduit",
            }

            # Build conduit type display list (and reverse map) when t9_df is present.
            if t9_df is not None and hasattr(t9_df, "columns") and len(t9_df.columns) > 0:
                # t9_df.columns contain names like "Hdpe Dr9 ID (mm)", "Hdpe Dr9 Area (mm²)".
                # We need to extract the base column token (e.g., "Hdpe Dr9") to map to OESC header.
                available_cols = list(t9_df.columns)
                # extract base tokens (strip trailing " ID (mm)" or " Area (mm²)")
                base_tokens = []
                col_to_base = {}
                for col in available_cols:
                    token = col
                    # remove trailing parts
                    token = re.sub(r"\s+ID\s*\(mm\)$", "", token)
                    token = re.sub(r"\s+Area\s*\(mm²\)$", "", token)
                    token = token.strip()
                    col_to_base[col] = token
                    base_tokens.append(token)

                # unique base tokens preserving order
                seen = set()
                base_order = []
                for b in base_tokens:
                    if b not in seen:
                        seen.add(b)
                        base_order.append(b)

                # Filter out non-conduit header tokens such as 'Subtable' or 'Trade size'
                filtered_base_order = [x for x in base_order if not re.search(r"subtable|trade\s*size", x, flags=re.IGNORECASE)]

                # Build display names and reverse mapping
                conduit_display_names = []
                display_to_colbase = {}
                for base in filtered_base_order:
                    display = OESC_COLUMN_TO_HEADER.get(base, base)
                    conduit_display_names.append(display)
                    display_to_colbase[display] = base

                # We also need a mapping from display name back to the actual dataframe column
                # For lookups we will prefer the "ID (mm)" column for diameter and the "Area (mm²)"
                # for area values. We'll construct helpers when the user selects the display value.
            else:
                conduit_display_names = None
                display_to_colbase = {}
            conduit_types = sorted({k[0] for k in t9_index.keys()}) if t9_index else []
            if not conduit_types:
                st.error("Table 9 could not be loaded/parsed. Enable manual conduit mode above.")
                conduit_type = "(Unknown)"
                conduit_trade = "(Unknown)"
            else:
                c1, c2 = st.columns([1, 1], gap="large")
                with c1:
                        
                    # Present the human-friendly OESC header names to the user when available.
                    if conduit_display_names:
                        sel_idx = 0
                        conduit_choice_display = st.selectbox("Conduit type", conduit_display_names, index=sel_idx, key="cf_conduit_type")
                        # map the chosen display back to the dataframe base token (e.g., "Hdpe Dr9")
                        chosen_base = display_to_colbase.get(conduit_choice_display)
                        # build the corresponding dataframe column names we'll use for ID and Area lookups
                        chosen_id_col = None
                        chosen_area_col = None
                        if chosen_base:
                            # prefer exact matches for "ID (mm)" and "Area (mm²)"
                            possible_id = f"{chosen_base} ID (mm)"
                            possible_area = f"{chosen_base} Area (mm²)"
                            if possible_id in t9_df.columns:
                                chosen_id_col = possible_id
                            if possible_area in t9_df.columns:
                                chosen_area_col = possible_area
                        # fallback: pick the first matching column that contains the base token
                        if chosen_id_col is None or chosen_area_col is None:
                            for c in t9_df.columns:
                                if chosen_base and chosen_base in c:
                                    if "ID" in c and chosen_id_col is None:
                                        chosen_id_col = c
                                    if "Area" in c and chosen_area_col is None:
                                        chosen_area_col = c
                        conduit_type = chosen_base if chosen_base else conduit_choice_display
                    else:
                        conduit_type = st.selectbox("Conduit type", conduit_types, index=0, key="cf_conduit_type")
                        chosen_id_col = None
                        chosen_area_col = None
                    # Build trade-size options for the selected conduit type.
                    sizes_for_type = []
                    try:
                        if t9_df is not None and hasattr(t9_df, 'columns') and 't9_size_col' in globals() and t9_size_col:
                            # If we have a chosen_base (from display mapping), try to find ID/Area columns for it
                            if 'chosen_base' in locals() and chosen_base:
                                possible_id = f"{chosen_base} ID (mm)"
                                possible_area = f"{chosen_base} Area (mm²)"
                                chosen_area_col_local = possible_area if possible_area in t9_df.columns else (possible_id if possible_id in t9_df.columns else None)
                                if chosen_area_col_local:
                                    try:
                                        sizes_for_type = sorted([str(x) for x in pd.Series(t9_df.loc[t9_df[chosen_area_col_local].notna(), t9_size_col]).dropna().astype(str).unique()])
                                    except Exception:
                                        sizes_for_type = []
                                else:
                                    # No explicit ID/Area column for base token; fallback to scanning rows where any column contains the base token
                                    try:
                                        mask = t9_df.apply(lambda r: any((str(v) is not None and str(v).strip() != '') for v in [r.get(possible_id, None), r.get(possible_area, None)]), axis=1)
                                        if mask.any():
                                            sizes_for_type = sorted([str(x) for x in pd.Series(t9_df.loc[mask, t9_size_col]).dropna().astype(str).unique()])
                                    except Exception:
                                        sizes_for_type = []
                        # final fallback to t9_index keys matching chosen_base or conduit_type
                        if not sizes_for_type:
                            key_token = chosen_base if ('chosen_base' in locals() and chosen_base) else conduit_type
                            sizes_for_type = sorted({k[1] for k in t9_index.keys() if key_token and key_token in k[0]})
                            if not sizes_for_type:
                                sizes_for_type = sorted({k[1] for k in t9_index.keys() if k[0] == conduit_type})
                    except Exception:
                        sizes_for_type = sorted({k[1] for k in t9_index.keys() if k[0] == conduit_type})
                    with c2:
                        conduit_trade = st.selectbox("Conduit trade size", sizes_for_type, index=0, key="cf_conduit_size")

                    # Attempt to find the Table 9 row using the combined dataframe when available
                    row = {}
                    if t9_df is not None and hasattr(t9_df, 'columns') and 't9_size_col' in globals() and t9_size_col:
                        try:
                            mask = t9_df[t9_size_col].astype(str).str.strip() == str(conduit_trade).strip()
                            df_rows = t9_df.loc[mask]
                            if not df_rows.empty:
                                sel = None
                                if 'chosen_area_col' in locals() and chosen_area_col in t9_df.columns:
                                    for _, r in df_rows.iterrows():
                                        if pd.notna(r.get(chosen_area_col)):
                                            sel = r
                                            break
                                if sel is None:
                                    sel = df_rows.iloc[0]
                                try:
                                    row = {c: sel.get(c, None) for c in list(t9_df.columns)}
                                except Exception:
                                    row = {c: sel[c] if c in sel.index else None for c in list(t9_df.columns)}
                        except Exception:
                            row = {}
                    if not row:
                        row = t9_index.get((conduit_type, conduit_trade), {})

                    conduit_internal_area = _infer_internal_area(row)

                    if conduit_internal_area is None:
                        st.warning("Could not infer internal area from Table 9 row — using manual entry for internal area.")
                        conduit_internal_area = st.number_input("Conduit internal area override (mm²)", min_value=0.01, value=500.0, step=10.0, key="cf_area_override")

        # ----------------------------
        # Cable groups (Table 6)
        # ----------------------------
        st.markdown("## 2) Cable groups (Table 6)")

        if not t6_types:
            st.warning("Table 6 could not be loaded/parsed. You can still proceed by entering areas manually per group.")
            default_rows = [
                {"Cable type": "(Manual)", "Conductor size": "(Manual)", "Conductors per cable": 3, "Qty (cables)": 1, "Area per conductor (mm²)": 50.0},
            ]
        else:
            default_rows = [
                {"Cable type": t6_types[0], "Conductor size": (t6_sizes_by_type.get(t6_types[0]) or [""])[0], "Conductors per cable": 3, "Qty (cables)": 1, "Area per conductor (mm²)": None},
            ]

        if pd is None:
            st.error("pandas is required for the dynamic cable table UI. Please add pandas to your environment.")
            st.stop()

        if "cf_cable_df" not in st.session_state:
            st.session_state["cf_cable_df"] = pd.DataFrame(default_rows)

        df_in = st.session_state["cf_cable_df"].copy()

        # Pre-fill areas where possible
        def _lookup_area(row):
            t = _norm(row.get("Cable type", ""))
            s = _norm(row.get("Conductor size", ""))
            if t in t6_area and s in t6_area[t]:
                return float(t6_area[t][s])
            return row.get("Area per conductor (mm²)", None)

        try:
            df_in["Area per conductor (mm²)"] = df_in.apply(_lookup_area, axis=1)
        except Exception:
            pass

        type_options = t6_types if t6_types else ["(Manual)"]
        # Use union of sizes to keep editor simple; on calculation we still attempt per-type lookup
        all_sizes = sorted({s for t in t6_sizes_by_type.values() for s in t} ) if t6_sizes_by_type else ["(Manual)"]

        edited = st.data_editor(
            df_in,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            column_config={
                "Cable type": st.column_config.SelectboxColumn("Cable type", options=type_options, required=True),
                "Conductor size": st.column_config.SelectboxColumn("Conductor size", options=all_sizes, required=True),
                "Conductors per cable": st.column_config.NumberColumn("Conductors per cable", min_value=1, step=1, required=True),
                "Qty (cables)": st.column_config.NumberColumn("Qty (cables)", min_value=1, step=1, required=True),
                "Area per conductor (mm²)": st.column_config.NumberColumn("Area per conductor (mm²)", min_value=0.0, step=0.01, help="Auto-filled from Table 6 when possible; editable."),
            },
            key="cf_cable_editor",
        )

        st.session_state["cf_cable_df"] = edited

        # ----------------------------
        # Calculations
        # ----------------------------
        st.markdown("## 3) Results")

        # total # of cables (for Table 9 allowable selection)
        try:
            n_cables_total = int(pd.to_numeric(edited["Qty (cables)"], errors="coerce").fillna(0).sum())
        except Exception:
            n_cables_total = 0

        # total conductor area
        def _row_total_area(r):
            ncond = _to_float(r.get("Conductors per cable"))
            qty = _to_float(r.get("Qty (cables)"))
            area_per = _to_float(r.get("Area per conductor (mm²)"))

            # Attempt a lookup if area_per missing
            if (area_per is None) and t6_area:
                t = _norm(r.get("Cable type", ""))
                s = _norm(r.get("Conductor size", ""))
                area_per = _to_float(t6_area.get(t, {}).get(s, None))

            if ncond is None or qty is None or area_per is None:
                return 0.0
            return float(ncond) * float(qty) * float(area_per)

        try:
            total_cable_area = float(edited.apply(_row_total_area, axis=1).sum())
        except Exception:
            total_cable_area = 0.0

        # Determine allowable based on conduit selection + n_cables_total
        if not use_manual_conduit and t9_index:
            row = t9_index.get((conduit_type, conduit_trade), {})
            conduit_allowed_area, conduit_allowed_pct, allowed_source = _infer_allowed_area_and_pct(
                row, max(1, n_cables_total), conduit_internal_area
            )
        else:
            # manual conduit mode already handled earlier
            if conduit_allowed_area is None and conduit_internal_area:
                conduit_allowed_area, conduit_allowed_pct, allowed_source = _infer_allowed_area_and_pct(
                    {}, max(1, n_cables_total), conduit_internal_area
                )

        fill_pct = safe_div(total_cable_area, conduit_internal_area) if conduit_internal_area else None

        m1, m2, m3 = st.columns([1, 1, 1], gap="large")
        m1.metric("Total cables in raceway", fmt(n_cables_total, ""))
        m2.metric("Total cable area", fmt(total_cable_area, "mm²"))
        m3.metric("Conduit internal area", fmt(conduit_internal_area, "mm²") if conduit_internal_area else "—")

        if fill_pct is None:
            st.warning("Provide a conduit internal area to compute fill.")
        else:
            st.metric("Actual fill (%)", fmt(fill_pct * 100.0, "%"))

        if conduit_allowed_area is not None and conduit_internal_area:
            allowed_pct_disp = (conduit_allowed_area / conduit_internal_area) * 100.0
            st.info(f"Allowable fill: **{fmt(allowed_pct_disp, '%')}**  (allowable area: **{fmt(conduit_allowed_area, 'mm²')}**)  — {allowed_source}")
            ok = total_cable_area <= conduit_allowed_area + 1e-9
            if ok:
                st.success("✅ Fill is within the allowable limit for the selected conduit.")
            else:
                st.error("❌ Fill exceeds the allowable limit for the selected conduit.")

            # Suggest next trade size (same type) if we have Table 9
            if (not use_manual_conduit) and t9_index and not ok:
                # Build candidate sizes for same type and pick smallest allowed_area >= total_cable_area
                candidates = []
                for (t, s), r in t9_index.items():
                    if t != conduit_type:
                        continue
                    ia = _infer_internal_area(r)
                    if ia is None:
                        continue
                    a_allow, _, _ = _infer_allowed_area_and_pct(r, max(1, n_cables_total), ia)
                    if a_allow is None:
                        continue
                    candidates.append((s, a_allow, ia))
                # sort candidates by allowed area, then label
                candidates.sort(key=lambda x: (x[1], x[0]))
                suggestion = None
                for s, a_allow, ia in candidates:
                    if a_allow >= total_cable_area - 1e-9:
                        suggestion = (s, a_allow, ia)
                        break
                if suggestion:
                    s, a_allow, ia = suggestion
                    st.success(
                        f"Suggested next size (same conduit type) that meets fill: **{conduit_type} — {s}** "
                        f"(allowable area ≈ {fmt(a_allow,'mm²')}, internal area ≈ {fmt(ia,'mm²')})."
                    )
                else:
                    st.warning("No larger trade size found in Table 9 that meets fill (based on parsed data).")

        else:
            st.warning("Allowable fill could not be determined (Table 9 not available or columns not recognized).")

        st.divider()
        st.markdown("### Equation used")
        eq(r"\text{Fill}=\frac{\sum\left(A_{cond}\cdot N_{cond/cable}\cdot N_{cables}\right)}{A_{conduit}}")

        with st.expander("Show calculation details", expanded=False):
            st.write(f"- Conduit: **{conduit_type}** — **{conduit_trade}**")
            st.write(f"- Conduit internal area: **{fmt(conduit_internal_area, 'mm²')}**")
            st.write(f"- Total cables: **{n_cables_total}**")
            st.write(f"- Total cable area: **{fmt(total_cable_area, 'mm²')}**")
            if conduit_allowed_area is not None:
                st.write(f"- Allowable area: **{fmt(conduit_allowed_area, 'mm²')}**  ({allowed_source})")

            st.markdown("#### Cable group breakdown")
            try:
                show_df = edited.copy()
                show_df["Area per conductor (mm²) (used)"] = show_df.apply(lambda r: _to_float(r.get("Area per conductor (mm²)")) or _to_float(t6_area.get(_norm(r.get("Cable type","")), {}).get(_norm(r.get("Conductor size","")), None)) or None, axis=1)
                show_df["Total group area (mm²)"] = show_df.apply(_row_total_area, axis=1)
                st.dataframe(show_df, use_container_width=True, hide_index=True)
            except Exception:
                st.write("(Unable to render breakdown table in this environment.)")

        st.caption(
            "Important: Always verify Table 6/Table 9 interpretations against the current OESC edition and project specs. "
            "Different table layouts may exist depending on how the table library is encoded."
        )


# ============================
# 8) Cable Tray Ampacity

# ============================
elif page == "Cable Tray Ampacity":
    with theory_tab:
        header("Cable Tray Ampacity — Theory")
        show_code_note(code_mode)
        render_md_safe("cable_tray_ampacity.md")

    with calc_tab:
        header("Ampacity Derating Calculator", "Apply base ampacity and derating factors.")
        show_code_note(code_mode)

        base = st.number_input("Base ampacity (A)", min_value=0.1, value=200.0, step=1.0)
        grouping = st.number_input("Grouping factor", min_value=0.0, max_value=1.0, value=0.80, step=0.01)
        ambient = st.number_input("Ambient factor", min_value=0.0, max_value=1.50, value=1.00, step=0.01)

        adj = base * grouping * ambient
        st.success(f"Adjusted ampacity: **{fmt(adj, 'A')}**")

        st.markdown("### Equation used")
        eq(r"I_{adj}=I_{base}\cdot k_{group}\cdot k_{ambient}")


# ============================
# 9) Demand Load
# ============================
elif page == "Demand Load":
    with theory_tab:
        header("Demand Load — Theory")
        show_code_note(code_mode)
        render_md_safe("demand_load.md")

    with calc_tab:
        header("Demand Load Calculator", "Compute demand load from connected load and factor.")
        show_code_note(code_mode)

        connected = st.number_input("Connected load (kW)", min_value=0.0, value=120.0, step=1.0)
        factor = st.number_input("Demand factor (0–1)", min_value=0.0, max_value=1.0, value=0.65, step=0.01)
        demand = connected * factor
        st.success(f"Demand load: **{fmt(demand, 'kW')}**")

        st.markdown("### Equation used")
        eq(r"P_{demand}=P_{connected}\cdot f_{demand}")
# ============================
# 10) Voltage Drop  (FULL BLOCK — Table D3 expander always shown; f-list filtered for DC; size order matches Table D3)
# ============================

# ============================
# Table Library (browse/search embedded OESC tables)
# ============================
elif page == "Table Library":

    # ---- NO TABS ON THIS PAGE ----
    header("Table Library — OESC Tables")
    show_code_note(code_mode)

    st.markdown(
        "Browse and search the embedded OESC tables included with this app. "
        "Tables are stored in **lib/oesc_tables.py** and exposed through a small registry API."
    )
    st.markdown(
        "- Use the search box to quickly filter by table number (e.g., `5A`) or keywords (e.g., `ampacity`, `conduit`).\n"
        "- A dash/blank entry in the source tables is shown as `—` (stored internally as `None`)."
    )

    st.divider()

    header("Table Lookup")

    if _TABLES_IMPORT_ERROR:
        st.error(
            "Table library failed to import. Confirm your repo has `lib/oesc_tables.py` and `lib/__init__.py`.\n\n"
            f"Import error: `{_TABLES_IMPORT_ERROR}`"
        )
    else:
        q = st.text_input(
            "Search tables",
            value="",
            placeholder="Examples: 1, 2, 5A, 9H, ampacity, conduit fill …",
        )

        table_ids = oesc_tables.search_tables(q)

        if not table_ids:
            st.warning("No tables match your search.")
        else:
            def _label(tid: str) -> str:
                meta = oesc_tables.get_table_meta(tid)
                title = meta.get("title") if meta else ""
                if title and title.lower().startswith("table"):
                    return title
                return f"Table {tid} — {title}" if title else f"Table {tid}"

            selected = st.selectbox(
                "Select a table",
                table_ids,
                format_func=_label,
            )

            meta = oesc_tables.get_table_meta(selected) or {}
            st.markdown(f"### {_label(selected)}")

            if meta.get("units"):
                st.caption(f"Units: **{meta['units']}**")

            df = oesc_tables.get_table_dataframe(selected)

            if df is None:
                st.info(
                    "This table is available in the library, but it is stored in a specialized structure "
                    "(raw format). Showing the raw object below."
                )
                st.json(meta.get("raw", {}))
            else:
                try:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                except TypeError:
                    st.dataframe(df, use_container_width=True)

                # Download CSV
                try:
                    import pandas as _pd
                    if isinstance(df, _pd.DataFrame):
                        csv_bytes = df.to_csv(index=False).encode("utf-8")
                    else:
                        csv_bytes = _pd.DataFrame(df).to_csv(index=False).encode("utf-8")

                    st.download_button(
                        "Download table as CSV",
                        data=csv_bytes,
                        file_name=f"oesc_table_{str(selected).lower()}.csv",
                        mime="text/csv",
                    )
                except Exception:
                    st.caption("CSV download unavailable in this environment.")


elif page == "Voltage Drop":
    with theory_tab:
        header("Voltage Drop — Theory")
        show_code_note(code_mode)
        render_md_safe("voltage_drop.md")

    with calc_tab:
        header("Voltage Drop Calculator — Table D3 (OESC) + k-value helper")
        show_code_note(code_mode)

        st.markdown(
            "This calculator looks up an **exact k-value** from Table D3 (embedded) "
            "or accepts a manual k-value. It uses the OESC table formula:\n\n"
            r"$$V_D = \frac{k \cdot f \cdot I \cdot L}{1000}$$"
            "\n\nWhere:\n- \(k\) is the table voltage-drop factor (Ω per circuit kilometre)\n- \(f\) is the system/connection factor\n- \(I\) is the load current (A)\n- \(L\) is the one-way length (m)\n"
        )

        # --------------------------
        # Exact Table D3 embedded (from supplied images)
        # --------------------------
        TABLE_D3 = {
            "Copper": {
                "14":  {"DC":10.2,"Cable 100%":10.2,"Cable 90%":9.92,"Cable 80%":9.67,"Raceway 90%":10.0,"Raceway 80%":9.67},
                "12":  {"DC":6.38,"Cable 100%":6.38,"Cable 90%":6.25,"Cable 80%":6.10,"Raceway 90%":6.26,"Raceway 80%":6.11},
                "10":  {"DC":4.03,"Cable 100%":4.03,"Cable 90%":3.96,"Cable 80%":3.87,"Raceway 90%":3.96,"Raceway 80%":3.87},
                "8":   {"DC":2.54,"Cable 100%":2.54,"Cable 90%":2.50,"Cable 80%":2.45,"Raceway 90%":2.51,"Raceway 80%":2.45},
                "6":   {"DC":1.59,"Cable 100%":1.59,"Cable 90%":1.58,"Cable 80%":1.55,"Raceway 90%":1.58,"Raceway 80%":1.55},
                "4":   {"DC":1.01,"Cable 100%":1.01,"Cable 90%":1.01,"Cable 80%":0.987,"Raceway 90%":1.01,"Raceway 80%":1.00},
                "3":   {"DC":0.792,"Cable 100%":0.792,"Cable 90%":0.797,"Cable 80%":0.787,"Raceway 90%":0.801,"Raceway 80%":0.792},
                "2":   {"DC":0.626,"Cable 100%":0.627,"Cable 90%":0.636,"Cable 80%":0.629,"Raceway 90%":0.639,"Raceway 80%":0.635},
                "1":   {"DC":0.50,"Cable 100%":0.50,"Cable 90%":0.512,"Cable 80%":0.509,"Raceway 90%":0.516,"Raceway 80%":0.515},
                "1/0": {"DC":0.395,"Cable 100%":0.396,"Cable 90%":0.410,"Cable 80%":0.409,"Raceway 90%":0.414,"Raceway 80%":0.415},
                "2/0": {"DC":0.314,"Cable 100%":0.316,"Cable 90%":0.331,"Cable 80%":0.332,"Raceway 90%":0.335,"Raceway 80%":0.338},
                "3/0": {"DC":0.249,"Cable 100%":0.251,"Cable 90%":0.267,"Cable 80%":0.270,"Raceway 90%":0.271,"Raceway 80%":0.275},
                "4/0": {"DC":0.197,"Cable 100%":0.200,"Cable 90%":0.217,"Cable 80%":0.221,"Raceway 90%":0.221,"Raceway 80%":0.226},
                "250": {"DC":0.167,"Cable 100%":0.171,"Cable 90%":0.188,"Cable 80%":0.193,"Raceway 90%":0.192,"Raceway 80%":0.198},
                "300": {"DC":0.140,"Cable 100%":0.144,"Cable 90%":0.162,"Cable 80%":0.167,"Raceway 90%":0.166,"Raceway 80%":0.172},
                "350": {"DC":0.120,"Cable 100%":0.125,"Cable 90%":0.143,"Cable 80%":0.148,"Raceway 90%":0.147,"Raceway 80%":0.154},
                "400": {"DC":0.105,"Cable 100%":0.111,"Cable 90%":0.129,"Cable 80%":0.135,"Raceway 90%":0.133,"Raceway 80%":0.140},
                "500": {"DC":0.0836,"Cable 100%":0.0912,"Cable 90%":0.110,"Cable 80%":0.116,"Raceway 90%":0.114,"Raceway 80%":0.121},
                "600": {"DC":0.0697,"Cable 100%":0.0785,"Cable 90%":0.0969,"Cable 80%":0.104,"Raceway 90%":0.101,"Raceway 80%":0.109},
                "750": {"DC":0.0558,"Cable 100%":0.0668,"Cable 90%":0.0850,"Cable 80%":0.0915,"Raceway 90%":0.0889,"Raceway 80%":0.097},
                "1000":{"DC":0.0417,"Cable 100%":0.0558,"Cable 90%":0.0739,"Cable 80%":0.0805,"Raceway 90%":0.0778,"Raceway 80%":0.086},
            },
            "Aluminum": {
                "12":  {"DC":10.5,"Cable 100%":10.5,"Cable 90%":10.3,"Cable 80%":10.0,"Raceway 90%":10.3,"Raceway 80%":9.99},
                "10":  {"DC":6.58,"Cable 100%":6.58,"Cable 90%":6.44,"Cable 80%":6.28,"Raceway 90%":6.45,"Raceway 80%":6.29},
                "8":   {"DC":4.14,"Cable 100%":4.14,"Cable 90%":4.07,"Cable 80%":3.97,"Raceway 90%":4.07,"Raceway 80%":3.98},
                "6":   {"DC":2.62,"Cable 100%":2.62,"Cable 90%":2.58,"Cable 80%":2.52,"Raceway 90%":2.58,"Raceway 80%":2.53},
                "4":   {"DC":1.65,"Cable 100%":1.65,"Cable 90%":1.63,"Cable 80%":1.60,"Raceway 90%":1.64,"Raceway 80%":1.61},
                "3":   {"DC":1.31,"Cable 100%":1.31,"Cable 90%":1.30,"Cable 80%":1.27,"Raceway 90%":1.30,"Raceway 80%":1.28},
                "2":   {"DC":1.04,"Cable 100%":1.04,"Cable 90%":1.04,"Cable 80%":1.02,"Raceway 90%":1.04,"Raceway 80%":1.03},
                "1":   {"DC":0.82,"Cable 100%":0.82,"Cable 90%":0.823,"Cable 80%":0.812,"Raceway 90%":0.827,"Raceway 80%":0.818},
                "1/0": {"DC":0.651,"Cable 100%":0.652,"Cable 90%":0.659,"Cable 80%":0.652,"Raceway 90%":0.663,"Raceway 80%":0.657},
                "2/0": {"DC":0.516,"Cable 100%":0.517,"Cable 90%":0.526,"Cable 80%":0.522,"Raceway 90%":0.530,"Raceway 80%":0.528},
                "3/0": {"DC":0.408,"Cable 100%":0.409,"Cable 90%":0.420,"Cable 80%":0.419,"Raceway 90%":0.424,"Raceway 80%":0.425},
                "4/0": {"DC":0.326,"Cable 100%":0.327,"Cable 90%":0.341,"Cable 80%":0.341,"Raceway 90%":0.345,"Raceway 80%":0.347},
                "250": {"DC":0.275,"Cable 100%":0.277,"Cable 90%":0.291,"Cable 80%":0.293,"Raceway 90%":0.295,"Raceway 80%":0.299},
                "300": {"DC":0.229,"Cable 100%":0.231,"Cable 90%":0.247,"Cable 80%":0.249,"Raceway 90%":0.250,"Raceway 80%":0.255},
                "350": {"DC":0.196,"Cable 100%":0.199,"Cable 90%":0.215,"Cable 80%":0.218,"Raceway 90%":0.219,"Raceway 80%":0.224},
                "400": {"DC":0.172,"Cable 100%":0.175,"Cable 90%":0.191,"Cable 80%":0.195,"Raceway 90%":0.195,"Raceway 80%":0.201},
                "500": {"DC":0.138,"Cable 100%":0.141,"Cable 90%":0.158,"Cable 80%":0.163,"Raceway 90%":0.162,"Raceway 80%":0.168},
                "600": {"DC":0.115,"Cable 100%":0.119,"Cable 90%":0.136,"Cable 80%":0.142,"Raceway 90%":0.140,"Raceway 80%":0.147},
                "750": {"DC":0.0916,"Cable 100%":0.0968,"Cable 90%":0.115,"Cable 80%":0.121,"Raceway 90%":0.119,"Raceway 80%":0.126},
                "1000":{"DC":0.0686,"Cable 100%":0.0758,"Cable 90%":0.0933,"Cable 80%":0.0994,"Raceway 90%":0.0973,"Raceway 80%":0.105},
            },
        }

        # --------------------------
        # Ensure "Raceway 100%" exists and equals "Cable 100%" where appropriate
        # --------------------------
        for mat_key, sizes_dict in TABLE_D3.items():
            for size_key, cols in sizes_dict.items():
                if "Cable 100%" in cols and "Raceway 100%" not in cols:
                    cols["Raceway 100%"] = cols["Cable 100%"]

        # ---------------- Inputs
        k_mode = st.radio(
            "k-value input mode",
            ("Lookup k-value from Table D3 (recommended)", "Manual k-value (enter value)"),
            index=0,
            key="vd_k_mode",
        )
        use_table = k_mode.startswith("Lookup")

        c1, c2, c3 = st.columns([1,1,1], gap="large")
        with c1:
            I = st.number_input("Load current (A)", min_value=0.0, value=50.0, step=0.1, key="vd_I")
        with c2:
            L_m = st.number_input("One-way length (m)", min_value=0.0, value=80.0, step=1.0, key="vd_Lm")
        with c3:
            V_nom = st.number_input("Nominal voltage (V)", min_value=1.0, value=600.0, step=1.0, key="vd_Vnom")

        if use_table:
            mat = st.selectbox("Conductor material (table to use)", ["Copper", "Aluminum"], index=0, key="vd_mat")
            location = st.selectbox("Installation (table column family)", ["Cable", "Raceway", "DC"], index=0, key="vd_location")

            if location != "DC":
                pf_choice = st.selectbox("Power-factor column (for Cable/Raceway)", ["100% pf", "90% pf", "80% pf"], index=0, key="vd_pf")
            else:
                pf_choice = "100% pf"
                st.caption("Power-factor selection hidden for DC — DC uses the 'DC' column in Table D3.")

            # ✅ keep conductor sizes in the same order as Table D3 (dict insertion order)
            sizes = list(TABLE_D3[mat].keys())

            # pick a stable default index (prefer 1000 if present for Copper, else first entry)
            default_size_index = 0
            try:
                if mat == "Copper" and "1000" in sizes:
                    default_size_index = sizes.index("1000")
            except Exception:
                default_size_index = 0

            size = st.selectbox(
                "Select conductor size (Table D3)",
                sizes,
                index=default_size_index,
                key="vd_size",
            )
        else:
            st.caption("Manual k-value mode: table lookup controls are hidden. Enter k directly in Ω/km below.")
            mat = None
            location = None
            pf_choice = "100% pf"
            size = None

        if not use_table:
            k_used = st.number_input(
                "Manual k-value (Ω/km)",
                min_value=0.0,
                value=0.10,
                step=0.00001,
                format="%.6f",
                key="vd_k_manual_only",
            )
            selected_col_suffix = "Manual"
        else:
            pf_short = pf_choice.split()[0] if isinstance(pf_choice, str) else str(pf_choice)

            if location == "DC":
                candidates = ["DC"]
            else:
                primary = f"{location} {pf_short}"
                alt1 = f"{location} {pf_short} pf"
                alt2 = f"{location} {pf_short.replace('%','')}"
                candidates = [primary, alt1, alt2]

            table_entry = TABLE_D3[mat].get(size, {}) if mat is not None and size is not None else {}
            k_found = None
            found_key = None

            for c in candidates:
                if c in table_entry:
                    k_found = table_entry[c]
                    found_key = c
                    break

            if k_found is None and table_entry:
                pf_numeric = pf_short.replace('%','')
                for colname in table_entry.keys():
                    low = colname.lower()
                    if location is not None and location.lower() in low and pf_numeric in low:
                        k_found = table_entry[colname]
                        found_key = colname
                        break

            if k_found is None:
                available = ", ".join(list(table_entry.keys())) if table_entry else "(no table available)"
                st.error(
                    f"Table value not found for {mat} {size} / {location} {pf_short}. "
                    f"Available columns for this size: {available}"
                )
                k_used = None
                selected_col_suffix = None
            else:
                k_used = float(k_found)
                selected_col_suffix = found_key
                st.caption(f"Table D3 k-value selected for {mat} {size} ({selected_col_suffix}): **{k_used} Ω/km**")

        # --------------------------
        # f-factor options (used in both table + manual modes)
        # NOTE: filter to DC-only list ONLY when installation is DC.
        # --------------------------
        # When manual k-value mode is active, "location" is None, so we show the full list (as before).
        if I <= 0 or L_m <= 0 or V_nom <= 0 or k_used is None:
            st.warning("Enter positive values and ensure a k-value is selected to compute voltage drop.")
            f_choice = None
            f = None
            f_label = None
            Vd = None
            pct = None
        else:
            if location == "DC":
                f_options = [
                    ("DC — 2-wire, positive-to-negative (VD line-to-line)", 2.0),
                    ("DC — 2-wire, positive-to-ground (VD line-to-ground)", 2.0),
                    ("DC — 2-wire, negative-to-ground (VD line-to-ground)", 2.0),
                    ("DC — 3-wire, line-to-line with grounded conductor (VD line-to-line)", 2.0),
                ]
                default_f_index = 0
            else:
                f_options = [
                    ("DC — 2-wire, positive-to-negative (VD line-to-line)", 2.0),
                    ("DC — 2-wire, positive-to-ground (VD line-to-ground)", 2.0),
                    ("DC — 2-wire, negative-to-ground (VD line-to-ground)", 2.0),
                    ("DC — 3-wire, line-to-line with grounded conductor (VD line-to-line)", 2.0),
                    ("1-φ AC — 2-wire, line-to-grounded conductor (VD line-to-ground)", 2.0),
                    ("1-φ AC — 2-wire, line-to-line (VD line-to-line)", 2.0),
                    ("1-φ AC — 3-wire, line-to-line, with grounded conductor (VD line-to-line)", 2.0),
                    ("3-φ AC — 2-wire, line-to-grounded conductor (VD line-to-ground)", 2.0),
                    ("3-φ AC — 2-wire, line-to-line, no grounded conductor (VD line-to-line)", 2.0),
                    ("3-φ AC — 3-wire, line-to-line, with grounded conductor (VD line-to-line)", 2.0),
                    ("3-φ AC — 3-wire, line-to-grounded conductor (VD line-to-ground)", 2.0),
                    ("3-φ AC — 3-wire, line-to-line, no grounded conductor (VD line-to-line)", math.sqrt(3)),
                    ("3-φ AC — 4-wire, line-to-line, with grounded conductor (VD line-to-line)", math.sqrt(3)),
                ]
                default_f_index = 4 if len(f_options) > 4 else 0

            f_choice = st.selectbox(
                "Voltage-drop factor (f) — select circuit type",
                f_options,
                format_func=lambda x: x[0],
                index=default_f_index,
                key="vd_f_choice_full",
            )
            f = float(f_choice[1])
            f_label = f_choice[0]
            st.caption(f"Selected circuit type: **{f_label}** → f = **{f:.6g}** (used in formula \(V_D = k f I L / 1000\)).")

            Vd = (k_used * f * I * L_m) / 1000.0
            pct = (Vd / V_nom) * 100.0

            m1, m2 = st.columns(2)
            m1.metric("Estimated voltage drop", fmt(Vd, "V"))
            m2.metric("Voltage drop (%)", fmt(pct, "%"))

            st.markdown("### Parameters used")
            st.write(f"- k-value: **{k_used} Ω/km** (source: Table D3, column **{selected_col_suffix}**)")
            st.write(f"- factor f: **{f:.6g}** (selected: {f_label})")
            st.write(f"- I = **{fmt(I, 'A')}**, L = **{fmt(L_m, 'm')}**, V_nom = **{fmt(V_nom, 'V')}**")

            st.markdown("### Equation used")
            eq(r"V_D=\frac{k\cdot f\cdot I\cdot L}{1000}")
            eq(r"\%\Delta V = 100\cdot\frac{V_D}{V_{nom}}")

        st.caption(
            "Notes: Table D3 values are transcribed exactly from the supplied images (cable vs raceway and pf columns). "
            "When using Manual k-value mode the table lookup controls are hidden and k is used exactly as entered."
        )

        # -------------------------------------------------
        # NEW FEATURE: Download a Word report or Excel report
        # Includes: equations, assumptions, variables, constants, selected inputs, results, and full used tables.
        # -------------------------------------------------
        st.markdown("### 📄 Export calculation report")

        assumptions = [
            "Uses OESC Appendix D Table D3 k-values in Ω per circuit kilometre (Ω/km) when Table mode is selected.",
            "Uses voltage-drop factor f from the Appendix D system factor list.",
            "Uses one-way length L (m) directly in the formula; table equation divides by 1000 to convert m → km.",
            "Percent voltage drop is computed against nominal voltage V_nom.",
        ]

        constants = [
            {"Name": "1000", "Meaning": "m per km (unit conversion for L)", "Value": 1000},
            {"Name": "√3", "Meaning": "Three-phase factor for specific circuit types per table note", "Value": float(math.sqrt(3))},
        ]

        variables = [
            {"Symbol": "k", "Description": "Voltage-drop factor from Table D3 (Ω/km) or manual entry", "Value": k_used},
            {"Symbol": "f", "Description": "System/connection factor from Appendix D", "Value": f},
            {"Symbol": "I", "Description": "Load current (A)", "Value": I},
            {"Symbol": "L", "Description": "One-way length (m)", "Value": L_m},
            {"Symbol": "V_nom", "Description": "Nominal voltage (V)", "Value": V_nom},
            {"Symbol": "V_D", "Description": "Estimated voltage drop (V)", "Value": Vd},
            {"Symbol": "%ΔV", "Description": "Voltage drop percent (%)", "Value": pct},
        ]

        equations_text = [
            ("Voltage drop", r"V_D=\frac{k\cdot f\cdot I\cdot L}{1000}"),
            ("Percent drop", r"\%\Delta V = 100\cdot\frac{V_D}{V_{nom}}"),
        ]

        # f-factor reference (full) used in expander below; also exported
        f_table_rows = [
            {"System / Connection": "DC — 2-wire (positive-to-negative)", "f (used in formula)": 2.0, "Voltage reference": "Positive-to-negative"},
            {"System / Connection": "DC — 2-wire (positive-to-ground)", "f (used in formula)": 2.0, "Voltage reference": "Positive-to-ground"},
            {"System / Connection": "DC — 2-wire (negative-to-ground)", "f (used in formula)": 2.0, "Voltage reference": "Negative-to-ground"},
            {"System / Connection": "DC — 3-wire, line-to-line with grounded conductor", "f (used in formula)": 2.0, "Voltage reference": "Line-to-line"},
            {"System / Connection": "1-φ AC — 2-wire, line-to-grounded conductor", "f (used in formula)": 2.0, "Voltage reference": "Line-to-ground"},
            {"System / Connection": "1-φ AC — 2-wire, line-to-line", "f (used in formula)": 2.0, "Voltage reference": "Line-to-line"},
            {"System / Connection": "1-φ AC — 3-wire, line-to-line, with grounded conductor", "f (used in formula)": 2.0, "Voltage reference": "Line-to-line"},
            {"System / Connection": "3-φ AC — 2-wire, line-to-grounded conductor", "f (used in formula)": 2.0, "Voltage reference": "Line-to-ground"},
            {"System / Connection": "3-φ AC — 2-wire, line-to-line, no grounded conductor", "f (used in formula)": 2.0, "Voltage reference": "Line-to-line"},
            {"System / Connection": "3-φ AC — 3-wire, line-to-line with grounded conductor", "f (used in formula)": 2.0, "Voltage reference": "Line-to-line"},
            {"System / Connection": "3-φ AC — 3-wire, line-to-grounded conductor", "f (used in formula)": 2.0, "Voltage reference": "Line-to-ground"},
            {"System / Connection": "3-φ AC — 3-wire, line-to-line, no grounded conductor", "f (used in formula)": math.sqrt(3), "Voltage reference": "Line-to-line"},
            {"System / Connection": "3-φ AC — 4-wire, line-to-line, with grounded conductor", "f (used in formula)": math.sqrt(3), "Voltage reference": "Line-to-line"},
        ]

        # Build the DataFrame-ish rows for export (same columns you display)
        display_cols = [
            "Size",
            "DC",
            "Cable 100%",
            "Cable 90%",
            "Cable 80%",
            "Raceway 100%",
            "Raceway 90%",
            "Raceway 80%",
        ]
        cu_rows = []
        for size_key, cols in TABLE_D3["Copper"].items():
            cu_rows.append({
                "Size": size_key,
                "DC": cols.get("DC", None),
                "Cable 100%": cols.get("Cable 100%", None),
                "Cable 90%": cols.get("Cable 90%", None),
                "Cable 80%": cols.get("Cable 80%", None),
                "Raceway 100%": cols.get("Raceway 100%", None),
                "Raceway 90%": cols.get("Raceway 90%", None),
                "Raceway 80%": cols.get("Raceway 80%", None),
            })
        al_rows = []
        for size_key, cols in TABLE_D3["Aluminum"].items():
            al_rows.append({
                "Size": size_key,
                "DC": cols.get("DC", None),
                "Cable 100%": cols.get("Cable 100%", None),
                "Cable 90%": cols.get("Cable 90%", None),
                "Cable 80%": cols.get("Cable 80%", None),
                "Raceway 100%": cols.get("Raceway 100%", None),
                "Raceway 90%": cols.get("Raceway 90%", None),
                "Raceway 80%": cols.get("Raceway 80%", None),
            })

        # Create report bytes (Word / Excel) on demand
        import io
        from datetime import datetime

        def _safe_float(x):
            try:
                return None if x is None else float(x)
            except Exception:
                return None

        # ✅ FIX: safe formatter for Word tables (prevents "Unknown format code 'g' for object of type 'str'")
        def _cell_text(val):
            """Safe text for Word/Excel cells: format numbers, otherwise stringify."""
            if val is None:
                return "—"
            if isinstance(val, (int, float)):
                return f"{val:g}"
            # try numeric conversion for numeric-looking strings
            try:
                fval = float(val)
                return f"{fval:g}"
            except Exception:
                return str(val)

        def build_word_report_bytes():
            from docx import Document
            from docx.shared import Pt

            doc = Document()
            doc.add_heading("Voltage Drop Calculation Report", level=1)

            meta = doc.add_paragraph()
            meta.add_run(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n").bold = True
            meta.add_run(f"k-mode: {k_mode}\n")
            if use_table:
                meta.add_run(f"Material: {mat}\n")
                meta.add_run(f"Installation: {location}\n")
                if location != "DC":
                    meta.add_run(f"Power factor column: {pf_choice}\n")
                meta.add_run(f"Conductor size: {size}\n")
                meta.add_run(f"Selected Table D3 column: {selected_col_suffix}\n")
            else:
                meta.add_run("Material/Installation/Size selection: (not used; manual k-value mode)\n")
                meta.add_run("k source: Manual entry\n")

            doc.add_heading("Equations", level=2)
            for title, latex in equations_text:
                p = doc.add_paragraph()
                p.add_run(f"{title}: ").bold = True
                # Word doesn't render LaTeX natively; we include readable LaTeX + plain-text form
                p.add_run(latex)

            doc.add_heading("Assumptions", level=2)
            for a in assumptions:
                doc.add_paragraph(a, style="List Bullet")

            doc.add_heading("Variables (inputs and results)", level=2)
            t = doc.add_table(rows=1, cols=3)
            hdr = t.rows[0].cells
            hdr[0].text = "Symbol"
            hdr[1].text = "Description"
            hdr[2].text = "Value"
            for v in variables:
                row = t.add_row().cells
                row[0].text = str(v["Symbol"])
                row[1].text = str(v["Description"])
                val = v["Value"]
                try:
                    row[2].text = "—" if val is None else f"{float(val):.6g}"
                except Exception:
                    row[2].text = "—" if val is None else str(val)

            doc.add_heading("Constants", level=2)
            tc = doc.add_table(rows=1, cols=3)
            hdr = tc.rows[0].cells
            hdr[0].text = "Name"
            hdr[1].text = "Meaning"
            hdr[2].text = "Value"
            for c in constants:
                row = tc.add_row().cells
                row[0].text = str(c["Name"])
                row[1].text = str(c["Meaning"])
                try:
                    row[2].text = f'{float(c["Value"]):.6g}'
                except Exception:
                    row[2].text = str(c["Value"])

            doc.add_heading("System factor (f) reference (Appendix D)", level=2)
            tf = doc.add_table(rows=1, cols=3)
            hdr = tf.rows[0].cells
            hdr[0].text = "System / Connection"
            hdr[1].text = "f (used in formula)"
            hdr[2].text = "Voltage reference"
            for r in f_table_rows:
                row = tf.add_row().cells
                row[0].text = r["System / Connection"]
                row[1].text = f'{float(r["f (used in formula)"]):.6g}'
                row[2].text = r["Voltage reference"]

            doc.add_heading("Table D3 (Copper) — Ω/km", level=2)
            tcu = doc.add_table(rows=1, cols=len(display_cols))
            for j, col in enumerate(display_cols):
                tcu.rows[0].cells[j].text = col
            for r in cu_rows:
                rr = tcu.add_row().cells
                for j, col in enumerate(display_cols):
                    val = r.get(col, None)
                    rr[j].text = _cell_text(val)  # ✅ FIXED

            doc.add_heading("Table D3 (Aluminum) — Ω/km", level=2)
            tal = doc.add_table(rows=1, cols=len(display_cols))
            for j, col in enumerate(display_cols):
                tal.rows[0].cells[j].text = col
            for r in al_rows:
                rr = tal.add_row().cells
                for j, col in enumerate(display_cols):
                    val = r.get(col, None)
                    rr[j].text = _cell_text(val)  # ✅ FIXED

            # basic style tweak
            style = doc.styles["Normal"]
            style.font.name = "Calibri"
            style.font.size = Pt(11)

            bio = io.BytesIO()
            doc.save(bio)
            return bio.getvalue()

        def build_excel_report_bytes():
            from openpyxl import Workbook
            from openpyxl.utils import get_column_letter
            from openpyxl.styles import Font, Alignment

            wb = Workbook()

            def autosize(ws):
                for col in ws.columns:
                    max_len = 0
                    col_letter = get_column_letter(col[0].column)
                    for cell in col:
                        try:
                            v = "" if cell.value is None else str(cell.value)
                            max_len = max(max_len, len(v))
                        except Exception:
                            pass
                    ws.column_dimensions[col_letter].width = min(60, max(10, max_len + 2))

            # --- Summary
            ws = wb.active
            ws.title = "Summary"
            ws["A1"] = "Voltage Drop Calculation Report"
            ws["A1"].font = Font(bold=True, size=14)
            ws["A3"] = "Generated"
            ws["B3"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ws["A4"] = "k-mode"
            ws["B4"] = k_mode

            row = 6
            if use_table:
                summary_pairs = [
                    ("Material", mat),
                    ("Installation", location),
                    ("Power factor column", pf_choice if location != "DC" else "(N/A — DC)"),
                    ("Conductor size", size),
                    ("Selected Table D3 column", selected_col_suffix),
                ]
            else:
                summary_pairs = [
                    ("Material", "(N/A — manual k)"),
                    ("Installation", "(N/A — manual k)"),
                    ("Power factor column", "(N/A — manual k)"),
                    ("Conductor size", "(N/A — manual k)"),
                    ("k source", "Manual entry"),
                ]

            for kname, kval in summary_pairs:
                ws[f"A{row}"] = kname
                ws[f"B{row}"] = "" if kval is None else str(kval)
                row += 1

            row += 1
            ws[f"A{row}"] = "Results"
            ws[f"A{row}"].font = Font(bold=True)
            row += 1
            ws[f"A{row}"] = "V_D (V)"
            ws[f"B{row}"] = _safe_float(Vd)
            row += 1
            ws[f"A{row}"] = "%ΔV (%)"
            ws[f"B{row}"] = _safe_float(pct)
            autosize(ws)

            # --- Variables
            ws = wb.create_sheet("Variables")
            ws.append(["Symbol", "Description", "Value"])
            for cell in ws[1]:
                cell.font = Font(bold=True)
            for v in variables:
                val = v["Value"]
                ws.append([v["Symbol"], v["Description"], None if val is None else float(val)])
            autosize(ws)

            # --- Assumptions
            ws = wb.create_sheet("Assumptions")
            ws.append(["Assumptions"])
            ws["A1"].font = Font(bold=True)
            for a in assumptions:
                ws.append([a])
            ws.column_dimensions["A"].width = 110
            for r in range(2, 2 + len(assumptions)):
                ws[f"A{r}"].alignment = Alignment(wrap_text=True, vertical="top")

            # --- Equations
            ws = wb.create_sheet("Equations")
            ws.append(["Name", "Equation (LaTeX)"])
            for cell in ws[1]:
                cell.font = Font(bold=True)
            for title, latex in equations_text:
                ws.append([title, latex])
            ws.column_dimensions["A"].width = 22
            ws.column_dimensions["B"].width = 70

            # --- Constants
            ws = wb.create_sheet("Constants")
            ws.append(["Name", "Meaning", "Value"])
            for cell in ws[1]:
                cell.font = Font(bold=True)
            for c in constants:
                ws.append([c["Name"], c["Meaning"], c["Value"]])
            autosize(ws)

            # --- Table D3 Copper
            ws = wb.create_sheet("Table D3 - Copper")
            ws.append(display_cols)
            for cell in ws[1]:
                cell.font = Font(bold=True)
            for r in cu_rows:
                ws.append([r.get(col, None) for col in display_cols])
            autosize(ws)

            # --- Table D3 Aluminum
            ws = wb.create_sheet("Table D3 - Aluminum")
            ws.append(display_cols)
            for cell in ws[1]:
                cell.font = Font(bold=True)
            for r in al_rows:
                ws.append([r.get(col, None) for col in display_cols])
            autosize(ws)

            # --- f-factor reference
            ws = wb.create_sheet("f-factor reference")
            ws.append(["System / Connection", "f (used in formula)", "Voltage reference"])
            for cell in ws[1]:
                cell.font = Font(bold=True)
            for r in f_table_rows:
                ws.append([r["System / Connection"], float(r["f (used in formula)"]), r["Voltage reference"]])
            ws.column_dimensions["A"].width = 75
            ws.column_dimensions["B"].width = 18
            ws.column_dimensions["C"].width = 25

            bio = io.BytesIO()
            wb.save(bio)
            return bio.getvalue()

        # Only enable downloads when we have enough info to populate the report meaningfully
        can_export = (k_used is not None) and (I is not None) and (L_m is not None) and (V_nom is not None)

        exp_c1, exp_c2 = st.columns([1, 1], gap="large")
        with exp_c1:
            if st.button("Prepare Word report (.docx)", key="vd_build_docx"):
                try:
                    st.session_state["vd_docx_bytes"] = build_word_report_bytes()
                    st.success("Word report prepared. Use the download button below.")
                except Exception as e:
                    st.error(f"Failed to build Word report: {e}")

            docx_bytes = st.session_state.get("vd_docx_bytes", None)
            st.download_button(
                "⬇️ Download Word report (.docx)",
                data=docx_bytes if docx_bytes else b"",
                file_name="Voltage_Drop_Report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                disabled=(not can_export) or (docx_bytes is None),
                key="vd_download_docx",
            )

        with exp_c2:
            if st.button("Prepare Excel report (.xlsx)", key="vd_build_xlsx"):
                try:
                    st.session_state["vd_xlsx_bytes"] = build_excel_report_bytes()
                    st.success("Excel report prepared. Use the download button below.")
                except Exception as e:
                    st.error(f"Failed to build Excel report: {e}")

            xlsx_bytes = st.session_state.get("vd_xlsx_bytes", None)
            st.download_button(
                "⬇️ Download Excel report (.xlsx)",
                data=xlsx_bytes if xlsx_bytes else b"",
                file_name="Voltage_Drop_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                disabled=(not can_export) or (xlsx_bytes is None),
                key="vd_download_xlsx",
            )

        st.caption(
            "Export includes: equations (LaTeX), assumptions, variables/inputs/results, constants, the full Table D3 (Cu/Al), "
            "and the full system factor (f) reference table. (Word stores equations as LaTeX text; Excel stores them as text.)"
        )

        # -------------------------------------------------
        # Display exact Table D3 data used by the calculator (always shown)
        # (Raceway columns ordered: 100% -> 90% -> 80%)
        # -------------------------------------------------
        with st.expander("📋 Show Table D3 values used in this calculator", expanded=False):
            if not use_table:
                st.info("Table D3 shown for reference only while in Manual k-value mode — it does not affect the calculation unless you switch to 'Lookup' mode.")

            st.markdown("### Copper Conductors — Table D3 (Ω/km)")

            display_cols = [
                "Size",
                "DC",
                "Cable 100%",
                "Cable 90%",
                "Cable 80%",
                "Raceway 100%",
                "Raceway 90%",
                "Raceway 80%",
            ]

            cu_rows_display = []
            for size_key, cols in TABLE_D3["Copper"].items():
                row = {
                    "Size": size_key,
                    "DC": cols.get("DC", None),
                    "Cable 100%": cols.get("Cable 100%", None),
                    "Cable 90%": cols.get("Cable 90%", None),
                    "Cable 80%": cols.get("Cable 80%", None),
                    "Raceway 100%": cols.get("Raceway 100%", None),
                    "Raceway 90%": cols.get("Raceway 90%", None),
                    "Raceway 80%": cols.get("Raceway 80%", None),
                }
                cu_rows_display.append(row)

            try:
                import pandas as pd
                df_cu = pd.DataFrame(cu_rows_display, columns=display_cols)
                st.dataframe(df_cu, use_container_width=True, hide_index=True)
            except Exception:
                st.dataframe(cu_rows_display, use_container_width=True, hide_index=True)

            st.markdown("### Aluminum Conductors — Table D3 (Ω/km)")
            al_rows_display = []
            for size_key, cols in TABLE_D3["Aluminum"].items():
                row = {
                    "Size": size_key,
                    "DC": cols.get("DC", None),
                    "Cable 100%": cols.get("Cable 100%", None),
                    "Cable 90%": cols.get("Cable 90%", None),
                    "Cable 80%": cols.get("Cable 80%", None),
                    "Raceway 100%": cols.get("Raceway 100%", None),
                    "Raceway 90%": cols.get("Raceway 90%", None),
                    "Raceway 80%": cols.get("Raceway 80%", None),
                }
                al_rows_display.append(row)

            try:
                df_al = pd.DataFrame(al_rows_display, columns=display_cols)
                st.dataframe(df_al, use_container_width=True, hide_index=True)
            except Exception:
                st.dataframe(al_rows_display, use_container_width=True, hide_index=True)

            st.caption(
                "These tables are transcribed **exactly** from OESC Appendix D – Table D3 "
                "(75 °C conductors). Values are in Ω per circuit kilometre and are the "
                "same values used internally by the calculator above."
            )

        # -------------------------------------------------
        # Display the F-factor lookup table used by the calculator
        # -------------------------------------------------
        with st.expander("📐 Show system factor (f) table used in calculations", expanded=False):
            try:
                import pandas as pd

                df_f = pd.DataFrame(f_table_rows)
                st.markdown("### System factor (f) — reference table (from Appendix D)")
                st.dataframe(df_f, use_container_width=True, hide_index=True)

                try:
                    current_label = f_choice[0] if isinstance(f_choice, tuple) else str(f_choice)
                    current_f = f_choice[1] if isinstance(f_choice, tuple) else float(f_choice)
                    st.markdown(f"**Current selection:** `{current_label}` → f = **{current_f:.6g}**")
                except Exception:
                    st.info("Current f selection shown in the calculator inputs above.")

                st.caption(
                    "Notes: The 'Voltage reference' column shows whether the VD is line-to-line or line-to-ground for that circuit type."
                )
            except Exception:
                st.markdown("### System factor (f) — reference (plain)")
                for r in f_table_rows:
                    st.write(f"- **{r['System / Connection']}** — f = {r['f (used in formula)']} — {r['Voltage reference']}")
                st.caption("Pandas not available; shown as plaintext.")

# ============================
# 11) Conductors
# ============================
elif page == "Conductors":
    with theory_tab:
        header("Conductors — Theory", "OESC Section 4 (Rule 4-004) workflow + worked example case study.")
        show_code_note(code_mode)
        render_md_safe("conductors.md")

    with calc_tab:
        header("Conductors — Calculator", "Workflow helper: design current, table selection, correction-factor math, and k-value voltage drop check.")
        show_code_note(code_mode)

        if code_mode == "NEC":
            st.info(
                "Calculator logic below follows the OESC/CEC workflow summary (Rule 4-004 style). "
                "Switch the sidebar jurisdiction to **OESC** for best alignment."
            )

        st.markdown("## 1) Ampacity workflow helper (service factor + table selection)")

        c1, c2, c3 = st.columns([1, 1, 1], gap="large")
        with c1:
            I_load = st.number_input("Load current (A)", min_value=0.0, value=100.0, step=1.0, key="cond_I_load")
        with c2:
            sf = st.number_input("Service factor (SF)", min_value=1.0, value=1.25, step=0.05, key="cond_sf")
        with c3:
            n_parallel = st.number_input("Parallel sets", min_value=1, value=1, step=1, key="cond_n_parallel")

        mat = st.selectbox(
            "Conductor material (table family)",
            ["Copper (Tables 1–2)", "Aluminum (Tables 3–4)"],
            index=0,
            key="cond_material",
        )

        install = st.selectbox(
            "Installation method / condition",
            [
                "Free air (ventilated / ladder tray)",
                "Raceway or cable (conduit/tubing/cable)",
                "Underground (direct buried / direct-buried raceway)",
            ],
            index=0,
            key="cond_install",
        )

        I_design_total = I_load * sf
        I_per_set = safe_div(I_design_total, n_parallel) if n_parallel else None

        m1, m2 = st.columns(2, gap="large")
        m1.metric("Design current (total)", fmt(I_design_total, "A"))
        m2.metric("Design current per parallel set", fmt(I_per_set, "A"))

        def cu_table(free_air: bool):
            return "Table 1" if free_air else "Table 2"

        def al_table(free_air: bool):
            return "Table 3" if free_air else "Table 4"

        is_cu = mat.startswith("Copper")

        subrule = "—"
        amp_table = "—"
        corr_table = None
        corr_needed = False
        corr_hint = ""

        if install.startswith("Free air"):
            n_single = st.number_input(
                "Number of single conductors in the group",
                min_value=1,
                value=4,
                step=1,
                key="cond_freeair_nsingle",
            )

            spacing = st.radio(
                "Spacing between cables (% of largest cable diameter)",
                ["≥ 100%", "25% to 100%", "< 25%"],
                index=0,
                horizontal=True,
                key="cond_freeair_spacing",
            )

            if spacing == "≥ 100%":
                subrule = "4-004 (1) & (2) — single in free air"
                amp_table = cu_table(True) if is_cu else al_table(True)
            elif spacing == "25% to 100%":
                subrule = "4-004 (8) — single in free air"
                amp_table = cu_table(True) if is_cu else al_table(True)
                corr_table = "Table 5D"
                corr_needed = True
                corr_hint = "Enter k_corr from Table 5D (spacing 25%–100%)."
            else:
                if n_single <= 4:
                    subrule = "4-004 (9) — ≤4 single in free air"
                    amp_table = cu_table(True) if is_cu else al_table(True)
                    corr_table = "Table 5B"
                    corr_needed = True
                    corr_hint = "Enter k_corr from Table 5B (spacing <25%, ≤4 singles)."
                else:
                    subrule = "4-004 (11) — ≥5 single in free air"
                    amp_table = cu_table(False) if is_cu else al_table(False)
                    corr_table = "Table 5C"
                    corr_needed = True
                    corr_hint = "Enter k_corr from Table 5C (spacing <25%, ≥5 singles)."

        elif install.startswith("Raceway"):
            n_ccc = st.number_input(
                "Number of conductors in raceway/cable (use current-carrying count per your code interpretation)",
                min_value=1,
                value=3,
                step=1,
                key="cond_raceway_nccc",
            )

            if n_ccc <= 3:
                subrule = "4-004 (1) & (2) — 1 to 3 in raceway/cable"
                amp_table = cu_table(False) if is_cu else al_table(False)
            else:
                subrule = "4-004 (1) & (2) — 4 or more in raceway/cable"
                amp_table = cu_table(False) if is_cu else al_table(False)
                corr_table = "Table 5C"
                corr_needed = True
                corr_hint = "Enter k_corr from Table 5C (4+ in raceway/cable)."

        else:
            size_class = st.selectbox(
                "Conductor size class (per chart split)",
                ["No. 1/0 AWG and larger", "Smaller than No. 1/0 AWG"],
                index=0,
                key="cond_ug_sizeclass",
            )
            in_diagrams = st.radio(
                "Is the configuration covered in Diagrams D8 to D11?",
                ["Yes", "No"],
                index=0,
                horizontal=True,
                key="cond_ug_diagrams",
            )

            if size_class.startswith("No. 1/0") and in_diagrams == "Yes":
                subrule = "4-004 (1) & (2)(d) — underground, ≥1/0, config in D8–D11"
                amp_table = "Tables D8A to D11B (or IEEE 835)"
            elif size_class.startswith("No. 1/0") and in_diagrams == "No":
                subrule = "4-004 (1) & (2)(e) — underground, ≥1/0, config NOT in D8–D11"
                amp_table = "IEEE 835 calculation method"
            elif size_class.startswith("Smaller") and in_diagrams == "No":
                subrule = "4-004 (1) & (2)(f) — underground, <1/0, config NOT in D8–D11"
                amp_table = f"{cu_table(False) if is_cu else al_table(False)} (or IEEE 835)"
            else:
                subrule = "Underground case (not explicitly shown in the chart)"
                amp_table = f"{cu_table(False) if is_cu else al_table(False)} (confirm applicability)"
                st.warning(
                    "The chart explicitly calls out diagram usage for ≥1/0 AWG. "
                    "For <1/0 AWG, the summary points to IEEE 835 or Tables 2/4 depending on configuration. "
                    "Confirm in the full code/diagrams for your exact installation."
                )

        st.divider()
        st.markdown("### Table / factor guidance result")
        st.success(f"**Subrule path:** {subrule}")
        st.success(f"**Use ampacity from:** {amp_table}")

        corr_factor = 1.0
        if corr_needed:
            corr_factor = st.number_input(
                f"Correction factor k_corr ({corr_table})",
                min_value=0.01,
                max_value=1.00,
                value=0.80,
                step=0.01,
                key="cond_corr_factor",
                help=corr_hint,
            )
            st.info(f"Correction factor source: **{corr_table}**")

        I_table_required = None
        if I_per_set is not None:
            I_table_required = safe_div(I_per_set, corr_factor) if corr_needed else I_per_set

        st.metric("Minimum base-table ampacity to look for", fmt(I_table_required, "A"))

        st.markdown("### Equations used")
        eq(r"I_{design} = I_{load}\times SF")
        eq(r"I_{per\_set} = \frac{I_{design}}{N_{parallel}}")
        eq(r"I_{table} = \frac{I_{per\_set}}{k_{corr}}")

        st.divider()
        st.markdown("## 2) Voltage drop — k-value helper (Task 5 style)")

        vd1, vd2, vd3 = st.columns([1, 1, 1], gap="large")
        with vd1:
            vd_system = st.selectbox(
                "System model",
                ["Single-phase (2-wire) — k-value form", "Three-phase (balanced) — k-value form"],
                index=0,
                key="cond_vd_system",
            )
        with vd2:
            V_nom = st.number_input("Nominal voltage (V)", min_value=1.0, value=600.0, step=1.0, key="cond_vd_vnom")
        with vd3:
            pct_allow = st.number_input("Max voltage drop (%)", min_value=0.1, value=5.0, step=0.1, key="cond_vd_pct")

        vd4, vd5 = st.columns([1, 1], gap="large")
        with vd4:
            I_vd = st.number_input("Design current (A)", min_value=0.0, value=125.0, step=1.0, key="cond_vd_I")
        with vd5:
            L_km = st.number_input("One-way length (km)", min_value=0.0, value=1.5, step=0.1, key="cond_vd_Lkm")

        dV_allow = V_nom * (pct_allow / 100.0)

        if L_km <= 0 or I_vd <= 0:
            st.warning("Enter a non-zero length and current to compute k_max.")
        else:
            if vd_system.startswith("Single"):
                k_max = dV_allow / (2.0 * I_vd * L_km)
                eq_used = r"k_{max}=\frac{\Delta V_{allow}}{2IL_{km}}"
            else:
                k_max = dV_allow / (math.sqrt(3) * I_vd * L_km)
                eq_used = r"k_{max}=\frac{\Delta V_{allow}}{\sqrt{3}IL_{km}}"

            s1, s2 = st.columns(2, gap="large")
            s1.metric("Allowed voltage drop (V)", fmt(dV_allow, "V"))
            s2.metric("Maximum allowable k-value", fmt(k_max, "Ω/km"))

            st.markdown("### Equation used")
            eq(eq_used)
            st.caption(
                "Compare k_max to manufacturer k-values (Ω/km). Select a conductor with k ≤ k_max to meet the voltage-drop target."
            )

        with st.expander("Show the Knowledge File’s worked example results (Tasks 1–5)", expanded=False):
            st.markdown(
                """
- Task 1 result: **500 MCM**  
- Task 2 results: **No. 6 AWG**, **No. 2 AWG**, **No. 3/0 AWG**  
- Task 3 results: **No. 2/0 AWG**, **350 MCM**  
- Task 4 results: **No. 4/0 AWG**, **No. 3 AWG**  
- Task 5 result: **k_max = 0.08 Ω/km** → **1000 MCM**
"""
            )

# End of app