import math
import streamlit as st

from lib.theory import render_md

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
# ----------------------------
theory_tab, calc_tab = st.tabs(["📚 Theory", "🧮 Calculator"])


# ============================
# 1) Transformer Protection
# ============================
if page == "Transformer Protection":
    with theory_tab:
        header("Transformer Protection", "Code-focused theory and worked examples (moved to Markdown).")
        show_code_note(code_mode)

        if code_mode == "OESC":
            render_md("content/transformer_protection_oesc.md")
        else:
            render_md("content/transformer_protection_nec.md")

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
        render_md("content/transformer_feeders.md")

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
        render_md("content/grounding_bonding.md")

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
        render_md("content/motor_protection.md")

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
        render_md("content/motor_feeder.md")

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
        render_md("content/cable_tray_fill.md")

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
        render_md("content/conduit_fill.md")

    with calc_tab:
        header("Conduit Fill Calculator", "Compute fill % and a bend-radius placeholder.")
        show_code_note(code_mode)

        col1, col2 = st.columns(2, gap="large")
        with col1:
            conduit_area = st.number_input("Conduit internal area (mm²)", min_value=1.0, value=500.0, step=10.0)
        with col2:
            wire_area = st.number_input("Total conductor area (mm²)", min_value=0.0, value=150.0, step=5.0)

        fill = safe_div(wire_area, conduit_area)
        if fill is None:
            st.warning("Conduit area must be > 0.")
        else:
            st.metric("Fill (%)", fmt(fill * 100.0, "%"))

        conduit_id_mm = st.number_input("Conduit ID (mm)", min_value=0.0, value=25.0, step=1.0)
        br = 6.0 * conduit_id_mm
        st.success(f"Rule-of-thumb bend radius: **{fmt(br, 'mm')}**")

        st.markdown("### Equations used")
        eq(r"\text{Fill}=\frac{A_{wires}}{A_{conduit}}")
        eq(r"R_{min}=6\cdot D_{ID}")


# ============================
# 8) Cable Tray Ampacity
# ============================
elif page == "Cable Tray Ampacity":
    with theory_tab:
        header("Cable Tray Ampacity — Theory")
        show_code_note(code_mode)
        render_md("content/cable_tray_ampacity.md")

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
        render_md("content/demand_load.md")

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
# 10) Voltage Drop
# ============================
elif page == "Voltage Drop":
    with theory_tab:
        header("Voltage Drop — Theory")
        show_code_note(code_mode)
        render_md("content/voltage_drop.md")

    with calc_tab:
        header("Voltage Drop Calculator", "Estimate voltage drop (resistive model).")
        show_code_note(code_mode)

        system = st.radio("System", ["Single-phase (2-wire)", "Three-phase (balanced)"], horizontal=True)
        col1, col2, col3 = st.columns(3, gap="large")
        with col1:
            I = st.number_input("Load current (A)", min_value=0.0, value=50.0, step=0.1)
        with col2:
            L = st.number_input("One-way length (m)", min_value=0.0, value=80.0, step=1.0)
        with col3:
            R_per_m = st.number_input(
                "Conductor resistance (Ω/m)",
                min_value=0.0,
                value=0.0004,
                step=0.00005,
                format="%.6f",
            )

        V_nom = st.number_input("Nominal voltage (V)", min_value=1.0, value=400.0, step=1.0)

        if system.startswith("Single"):
            Vd = 2.0 * I * R_per_m * L
            eq_used = r"\Delta V \approx 2\,I\,R\,L"
        else:
            Vd = math.sqrt(3) * I * R_per_m * L
            eq_used = r"\Delta V \approx \sqrt{3}\,I\,R\,L"

        pct = (Vd / V_nom) * 100.0 if V_nom > 0 else 0.0

        c1, c2 = st.columns(2)
        c1.metric("Estimated voltage drop", fmt(Vd, "V"))
        c2.metric("Voltage drop (%)", fmt(pct, "%"))

        st.markdown("### Equations used")
        eq(eq_used)
        eq(r"\%\Delta V = 100\cdot\frac{\Delta V}{V_{nom}}")


# ============================
# 11) Conductors
# ============================
elif page == "Conductors":
    with theory_tab:
        header("Conductors — Theory", "OESC Section 4 (Rule 4-004) workflow + worked example case study.")
        show_code_note(code_mode)
        render_md("content/conductors.md")

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
