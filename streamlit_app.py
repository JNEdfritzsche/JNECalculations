import math
import streamlit as st

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
]

with st.sidebar:
    st.header("Navigate")
    page = st.radio("Go to", PAGES, index=0)

    st.divider()
    st.header("Unit Preferences")
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
        header("Transformer Protection", "Code-focused theory and worked examples (full content).")
        show_code_note(code_mode)

        # OESC Theory (full, corrected + reintroduced)
        if code_mode == "OESC":
            st.subheader("OESC — Transformer Protection (Full Theory, simplified)")

            st.markdown("### Document metadata / header (example)")
            st.markdown(
                """
**Associated with WI-8.3-.06 Rev. 0, May 2019**  
**Project #:** XX-XX-XXXX-XX — **Client:** JNE  
**Project Title:** OESC Transformer Protection Design Calculation  
**Calculation #:** EC-XXXX — **Revision:** A — **Date Initiated:** 08/17/2022
"""
            )

            st.markdown("### Objective")
            st.write(
                "Determine required overcurrent protection for a transformer (primary breaker/fuse sizing) "
                "so the transformer operates safely and the installation meets OESC requirements."
            )

            st.markdown("### Scope")
            st.write(
                "This calculation covers selecting primary (and when applicable secondary) overcurrent devices "
                "for typical power/distribution transformers using OESC as the reference."
            )

            st.markdown("### Technical Criteria / Applicable Codes")
            st.write(
                "Primary reference: Ontario Electrical Safety Code (OESC) — relevant rules include 26-240 through 26-258 and Section 8 (Rule 8-104) for continuous loading."
            )

            st.markdown("### Assumptions (example template used in the document)")
            st.markdown(
                """
- Ambient temperature: **40 °C**  
- Conductor temperature rating: **75 °C**  
- Copper conductors routed in free-air (field routed)  
- No more than 3 conductors per cable (including equipment grounding conductor)  
- Maximum cable length: **50 m (~164 ft)**  
- Transformer operating with **natural cooling** (no fans/pumps)
"""
            )

            st.markdown("### Input Data")
            st.write(
                "Use transformer nameplate data where available. If using OEM documentation, include document name/number and equipment ID."
            )

            st.markdown("### Rated current formula (when FLA is not known)")
            st.write("For three-phase transformers the rated line current is:")
            eq(r"I_L=\frac{S}{\sqrt{3}\,V_L}")
            st.write(
                "where S = apparent power, V_L = line-to-line voltage. Use consistent units "
                "(e.g., **S in VA with V in V**, or **S in kVA with V in kV**) so the result is in amperes."
            )
            st.write("Use this to calculate primary and secondary FLA:")
            eq(r"I_{pri}=\frac{S}{\sqrt{3}\,V_{pri}}")
            eq(r"I_{sec}=\frac{S}{\sqrt{3}\,V_{sec}}")

            st.markdown("### Methodology (practical steps)")
            st.write(
                "1. Use nameplate FLA if available; otherwise compute FLA using the equations above.\n"
                "2. Identify transformer type (oil-cooled vs dry-type) and voltage class (>750 V or ≤750 V).\n"
                "3. Apply the relevant OESC rule to determine the permitted OCPD multiplier(s) and any conditions/exceptions.\n"
                "4. If the calculated device rating does not match a standard device rating, select the **next higher** standard rating as permitted by the rule.\n"
                "5. Confirm whether an **individual primary device at the transformer** is required, or whether upstream feeder/branch protection is permitted to serve this role (rule-dependent).\n"
                "6. Verify continuous loading limits (Rule 26-258 and Rule 8-104) and conductor ampacity separately."
            )

            st.markdown("### OESC Rule highlights (key subrules summarized — corrected)")
            st.markdown(
                """
**OESC 26-250 — Overcurrent protection for power and distribution transformer circuits rated over 750 V (oil-cooled / power & distribution)**  
- Each ungrounded conductor of the transformer feeder shall have overcurrent protection.  
- **Fuses:** rated at not more than **150%** of rated primary current.  
- **Breakers:** rated/set at not more than **300%** of rated primary current.  
- If **150%** does not correspond to a standard fuse rating, the **next higher standard fuse rating** is permitted.  
- **An individual overcurrent device is not required** where the feeder/branch overcurrent device provides the protection specified in this rule.

**OESC 26-252 — Overcurrent protection for transformers 750 V or less (oil-cooled / other than dry-type)**  
- Primary overcurrent protection generally **≤ 150%** of rated primary current.  
- If rated primary current is **9 A or more** and **150%** does not correspond to a standard rating of a fuse or non-adjustable breaker, the **next higher standard rating** is permitted.  
- If rated primary current is **less than 9 A**, an overcurrent device **≤ 167%** is permitted.  
- If rated primary current is **less than 2 A**, an overcurrent device **≤ 300%** is permitted.  
- **An individual overcurrent device is not required** where the feeder/branch overcurrent device provides the protection specified in this rule.  
- **Secondary-protection pathway (common allowance):** A transformer with a **secondary-side device ≤ 125%** of rated secondary current **need not have an individual primary device**, provided that the **primary feeder overcurrent device ≤ 300%** of rated primary current (rule conditions apply).

**OESC 26-254 — Overcurrent protection for dry-type transformers 750 V or less**  
- Primary overcurrent protection generally **≤ 125%** of rated primary current.  
- If the required device rating does not correspond to a standard rating, the **next higher standard rating** may be permitted as allowed by the rule.  
- **An individual overcurrent device is not required** where the feeder/branch overcurrent device provides the protection specified in this rule.  
- **Secondary-protection pathway (common allowance):** A transformer with a **secondary-side device ≤ 125%** of rated secondary current **need not have an individual primary device**, provided that the **primary feeder overcurrent device ≤ 300%** of rated primary current (rule conditions apply).  
- **Inrush withstand guidance (Appendix):** the device should be able to carry **12× FLA for 0.1 s** and **25× FLA for 0.01 s** (verify manufacturer curves).
"""
            )

            st.markdown("### Continuous load and conductor checks (OESC 26-258 and Rule 8-104 intent)")
            st.write(
                "OESC 26-258 ties transformer overcurrent protection and conductor sizing (Rules 26-250 to 26-256) to the **continuous load** connected to the transformer secondary. "
                "In general terms: the continuous load determined from the calculated load connected to the transformer secondary must not exceed the values specified in Rule 8-104 (as applicable)."
            )
            st.write(
                "Appendix intent (plain language): this requirement helps ensure **coordination** between the secondary loads, the rating of transformer protection devices, "
                "and the ampacity of transformer conductors so minimum acceptable conductor size and protection selection are aligned."
            )

            st.markdown("### Worked calculation examples (from the provided doc)")
            st.write("Example A — Oil-cooled > 750 V (2,000 kVA, 27.6 kV / 600 V, 3Φ):")
            eq(r"I_{pri}=\frac{2{,}000{,}000}{\sqrt{3}\cdot 27{,}600}\approx 41.89\ \mathrm{A}")
            eq(r"I_{sec}=\frac{2{,}000{,}000}{\sqrt{3}\cdot 600}\approx 1926.78\ \mathrm{A}")
            st.write("Using OESC 26-250 multipliers:")
            eq(r"I_{fuse,max}=1.50\cdot I_{pri}\approx 62.83\ \mathrm{A}")
            eq(r"I_{brk,max}=3.00\cdot I_{pri}\approx 125.66\ \mathrm{A}")
            st.write("Selected standard sizes: **70 A fuse** or **150 A breaker** (next standard values).")

            st.write("Example B — Oil-cooled ≤ 750 V (75 kVA, 600 V / 208 V):")
            eq(r"I_{pri}=\frac{75{,}000}{\sqrt{3}\cdot 600}\approx 72.17\ \mathrm{A}")
            eq(r"I_{ocpd,max}=1.50\cdot I_{pri}\approx 108.26\ \mathrm{A}")
            st.write("Selected standard size: **110 A** (per standard device values).")

            st.write("Example C — Dry-type ≤ 750 V (75 kVA, 600 V / 208 V):")
            eq(r"I_{pri}\approx 72.17\ \mathrm{A}")
            eq(r"I_{ocpd,max}=1.25\cdot I_{pri}\approx 90.21\ \mathrm{A}")
            st.write("Selected standard size: **100 A**. Inrush checks: 12× and 25× multiples shown below.")
            eq(r"12\times I_{pri}\approx 866.04\ \mathrm{A}")
            eq(r"25\times I_{pri}\approx 1804.25\ \mathrm{A}")

            st.markdown("### Design considerations & coordination")
            st.write(
                "After selecting initial device ratings, perform a coordination study. Consider transformer winding configuration "
                "(Δ–Y, Y–Y, etc.), grounding method (open, solid, NGR), device availability, cost, and selective clearing of faults."
            )

            st.markdown("### Conclusion (example selections)")
            st.write(
                "- For the 2 MVA 27.6k/600V oil-cooled example: **70 A fuse** or **150 A breaker** selected.  \n"
                "- For the 75 kVA 600/208V oil-cooled example: **110 A** selected.  \n"
                "- For the 75 kVA dry-type example: **100 A** selected."
            )

            st.markdown("### Approval block (template)")
            st.write(
                "Prepared by: Michael Hommersen — Self-Check Completed? YES.  \n"
                "Include signature/date fields in your deliverable calculation sheet."
            )

        # NEC Theory (full, corrected + expanded to match document notes)
        else:
            st.subheader("NEC — Transformer Protection (Full Theory, simplified)")

            st.markdown("### Objective")
            st.write(
                "Select transformer overcurrent protection (breaker/fuses) in accordance with **NEC Article 450** "
                "so the device ratings meet the code allowances and protect the transformer."
            )

            st.markdown("### Scope & Key references")
            st.write(
                "Focus on NEC 450.3 and tables 450.3(A) / 450.3(B) depending on voltage class. Also consult NEC 240.6(A) for standard ratings "
                "and device availability rules used when rounding to standard/commercial sizes."
            )

            st.markdown("### Assumptions (example template)")
            st.markdown(
                """
- Ambient temperature: **40°C**  
- Conductors: **75°C copper**, free-air routing  
- Max cable length: **50 m**  
- Transformer impedance: **≤ 6%** (common example used in the template)  
- Installation location classification: **Any location** vs **Supervised location** (affects table choices)
"""
            )

            st.markdown("### Method / Practical approach")
            st.write(
                "1. Use nameplate FLA when available; otherwise compute FLA for primary and secondary using the 3Φ formula below.  \n"
                "2. Determine whether transformer is **over 1000 V nominal** (use **Table 450.3(A)**) or **1000 V nominal or less** (use **Table 450.3(B)**).  \n"
                "3. Determine whether the installation is **Any location** or a **Supervised location** (this can change allowable multipliers/limits).  \n"
                "4. Apply the table-based multipliers/limits to find allowable OCPD ratings (primary-only or primary+secondary schemes, where applicable).  \n"
                "5. Apply the table notes on rounding to standard/commercial device ratings and on how multiple secondary devices may be grouped."
            )

            st.markdown("### Rated current formula (3Φ)")
            eq(r"I_L=\frac{S}{\sqrt{3}\,V_L}")
            st.write(
                "Use consistent units (e.g., **S in VA with V in V**, or **S in kVA with V in kV**) so the result is in amperes."
            )
            eq(r"I_{pri}=\frac{S}{\sqrt{3}\,V_{pri}}")
            eq(r"I_{sec}=\frac{S}{\sqrt{3}\,V_{sec}}")

            st.markdown("### NEC 450.3 structure")
            st.markdown(
                """
**450.3(A)** — Transformers **over 1000 V nominal**: overcurrent protection per Table 450.3(A).  
**450.3(B)** — Transformers **1000 V nominal or less**: overcurrent protection per Table 450.3(B).  
**450.3(C)** — Voltage (potential) transformers: protection requirements depend on application; often primary fusing for indoor/enclosed installations with common small-circuit protections in control/potential circuits (as applicable).
"""
            )

            st.markdown("### Table 450.3 notes that materially affect design (carried into this app)")
            st.markdown(
                """
**Table 450.3 Note 1 — Rounding to standard / commercially available sizes**  
- If the required fuse rating or breaker setting does not correspond to a standard value, a higher rating/setting is permitted provided it does not exceed:  
  - the **next higher standard rating/setting** for devices **1000 V and below**, or  
  - the **next higher commercially available rating/setting** for devices **over 1000 V**.

**Table 450.3 Note 2 — Multiple secondary devices (when secondary OCPD is required)**  
- The secondary OCPD is permitted to consist of **not more than six** circuit breakers, or **six sets of fuses**, **grouped in one location**.  
- Where multiple devices are used, the **sum of device ratings** shall not exceed the allowed value of a **single** overcurrent device.  
- If **both breakers and fuses** are used, the total of the device ratings shall not exceed that allowed for **fuses**.

**Supervised location (definition used in the calculation template)**  
- A supervised location is one where maintenance/supervision ensure **only qualified persons** monitor and service the transformer installation (qualified persons have safety training and are familiar with operation and hazards).
"""
            )

            st.markdown("### Worked NEC examples (from the NEC calc document)")
            st.write("Example 1 — 2 MVA, 27.6 kV / 4.16 kV, Z ≤ 6%, any location:")
            eq(r"I_{pri}=\frac{2{,}000{,}000}{\sqrt{3}\cdot 27{,}600}\approx 41.89\ \mathrm{A}")
            eq(r"I_{sec}=\frac{2{,}000{,}000}{\sqrt{3}\cdot 4{,}160}\approx 277.90\ \mathrm{A}")

            st.markdown("**Document example multipliers (table-driven, Z ≤ 6%, any location):**")
            st.write("Primary limits:")
            eq(r"I_{pri,brk,max}=6.00\cdot I_{pri}\approx 251.34\ \mathrm{A}")
            eq(r"I_{pri,fuse,max}=3.00\cdot I_{pri}\approx 125.67\ \mathrm{A}")
            st.write("Secondary limits:")
            eq(r"I_{sec,brk,max}=3.00\cdot I_{sec}\approx 833.70\ \mathrm{A}")
            eq(r"I_{sec,fuse,max}=2.50\cdot I_{sec}\approx 694.75\ \mathrm{A}")
            st.write(
                "Example document selections (using commercially available sizes where applicable): "
                "**Primary 300 A breaker** or **150 A fuse**; **Secondary 1000 A breaker** or **700 A fuse**."
            )

            st.write("Example 2 — 75 kVA, 600 V / 208 V (currents > 9 A):")
            eq(r"I_{pri}=\frac{75{,}000}{\sqrt{3}\cdot 600}\approx 72.25\ \mathrm{A}")
            eq(r"I_{sec}=\frac{75{,}000}{\sqrt{3}\cdot 208}\approx 208.43\ \mathrm{A}")
            st.write(
                "Two schemes presented in the document (table-driven): primary-only → **100 A**; "
                "primary+secondary → **200 A primary** and **300 A secondary** (example selections)."
            )

            st.markdown("### Practical design notes (NEC)")
            st.write(
                "NEC transformer OCPD sizing focuses on protecting the transformer. Conductor protection still must be checked under Article 240. "
                "Coordination, relay protection for large transformers (e.g., ANSI 50/51 where applicable), and grounding/winding configuration "
                "should all be considered."
            )

    # ----------------------------
    # Calculator tab for Transformer Protection (CORRECT per attached docs)
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
        # OESC calculator (per OESC calc doc)
        # ----------------------------
        if code_mode == "OESC":
            st.subheader("OESC — Rule-based sizing (implemented per the attached OESC calculation)")

            cc1, cc2, cc3 = st.columns([1.2, 1.2, 1.2], gap="large")
            with cc1:
                xfmr_type = st.selectbox("Transformer type", ["Oil-cooled (non-dry)", "Dry-type"], index=0, key="tp_oesc_type")
            with cc2:
                # This matches how the attached document is organized
                voltage_class = st.selectbox("Voltage class selection", ["> 750 V", "≤ 750 V"], index=1 if vpri <= 750 else 0, key="tp_oesc_vclass")
            with cc3:
                round_to_std = st.checkbox("Round up to standard rating (Table 13 style)", value=True, key="tp_oesc_round")

            # Decide which rule path is valid
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

            # 26-250 (>750V) — per doc table: fuse 1.5, breaker 3.0 on primary.
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

            # 26-252 (≤750V non-dry) — per doc: primary allowance depends on Ip (<2A 300%, <9A 167%, else 150%).
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

            # 26-252 secondary pathway — per doc text: secondary device <=125% and primary feeder device <=300%.
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

            # 26-254 direct primary — per doc: primary 125%, next higher standard permitted, plus inrush 12x and 25x.
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

            # 26-254 secondary pathway — per doc: secondary device <=125% and primary feeder device <=300%.
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
        # NEC calculator (per NEC calc doc)
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
                # Note: for >1000V the calc doc uses "next higher commercially available";
                # we still show rounding using the standard list for convenience, with a note.
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
                    # From attached calc table:
                    # Primary breaker 6.00, primary fuse 3.00, secondary breaker 3.00, secondary fuse 2.50
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
                        # From attached calc: multiplier 1.25 on primary only
                        raw_primary = 1.25 * Ip
                        show_nec_result("Max Primary OCPD (1.25×)", raw_primary, over_1000v=False)
                        st.caption("This matches the attached NEC calculation 'Primary Only ≥9A Multiplier: 1.25'.")

                    else:
                        # From attached calc: primary multiplier 2.50, secondary multiplier 1.25
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

        st.markdown("### Purpose")
        st.write(
            "Transformer feeder design ensures conductors supplying the transformer can carry the expected load, "
            "meet continuous loading rules, and coordinate with overcurrent protection."
        )

        st.markdown("### Key points")
        st.markdown(
            """
- Start conductor sizing from transformer **secondary** full-load current.  
- Apply continuous load multipliers (e.g., 125% where applicable).  
- Adjust for ambient temperature, grouping, conductor insulation rating, and installation method.  
- Perform coordination with upstream protection and consider voltage drop and fault clearing.
"""
        )

        st.markdown("### Equations")
        st.write("Secondary FLA (3Φ):")
        eq(r"I_{sec}=\frac{S}{\sqrt{3}\,V_{sec}}")
        st.write("Suggested continuous ampacity target (example):")
        eq(r"I_{target}=1.25\cdot I_{sec}")

        st.markdown("### Example")
        eq(r"I_{sec}=\frac{150{,}000}{\sqrt{3}\cdot 208}\approx 416\ \mathrm{A}")

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

        st.markdown("### Overview")
        st.write(
            "Grounding and bonding conductor sizing is usually table-driven. NEC/OESC specify conductor sizes "
            "based on the largest ungrounded conductor or the OCPD rating. Consider electrode conductors (GEC), equipment grounding conductors (EGC), and bonding jumpers separately."
        )

        st.markdown("### Conceptual equation (placeholder)")
        eq(r"\text{EGC size} = f(\text{OCPD rating})")

        st.markdown("### Practical notes")
        st.write(
            "- Use the specific NEC/OESC tables for exact conductor sizes.  \n"
            "- For transformer-secondary grounding or neutral grounding, follow transformer-specific rules and coordinate with protective devices."
        )

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

        st.markdown("### Overview")
        st.write(
            "Motor protection includes overload protection (thermal overloads) and short-circuit/ground-fault protection. "
            "Settings depend on motor FLA, service factor, and the code requirements for the protection type."
        )

        st.markdown("### Typical equations")
        eq(r"I_{OL}=k\cdot I_{FLA}\quad\text{(overload setting)}")
        eq(r"I_{SC}=m\cdot I_{FLA}\quad\text{(short-circuit device sizing placeholder)}")

        st.markdown("### Notes")
        st.write(
            "- Overload multipliers often in the 1.15–1.25 range depending on motor and service factor.  \n"
            "- Short-circuit device selection needs coordination with conductor ampacity and upstream devices."
        )

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

        st.write(
            "Feeder sizing for motors often starts with a multiplier of the motor FLA (commonly 125% for single motor feeders). "
            "Apply correction factors, conductor ampacity tables, and check protection per code."
        )
        eq(r"I_{target}=1.25\cdot I_{FLA}")

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

        st.write(
            "Tray fill and bend-radius rules depend on cable type, manufacturer recommendations, and local code rules. "
            "The following are geometric approximations to help estimate area and bend radius."
        )
        eq(r"A_{cables}\approx n\cdot \pi\left(\frac{d}{2}\right)^2")
        eq(r"R_{min}=k\cdot d")

        st.markdown("### Notes")
        st.write(
            "- Real tray fill rules use percentage area limits and layering rules—replace these approximations with code tables for final designs."
        )

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

        st.write("Conduit fill is area-based; percent fill limits depend on conductor count and conduit type.")
        eq(r"\text{Fill}=\frac{A_{wires}}{A_{conduit}}")
        eq(r"R_{min}=6\cdot D_{ID}")

        st.markdown("### Notes")
        st.write("- Use manufacturer/conduit tables for exact internal areas and correct fill percentages.")

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

        st.write(
            "Ampacity in trays depends on cable grouping, spacing, ambient temperature, and insulation. "
            "Start from a base ampacity and apply derating factors."
        )
        eq(r"I_{adj}=I_{base}\cdot k_{group}\cdot k_{ambient}")

        st.markdown("### Notes")
        st.write("- Replace the simple model with table-driven derating per code/manufacturer for final designs.")

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

        st.write("Demand (calculated) load is the connected load multiplied by a demand factor that depends on load category.")
        eq(r"P_{demand}=P_{connected}\cdot f_{demand}")

        st.markdown("### Notes")
        st.write("- Add category-specific demand factors (occupancy, appliances, HVAC, etc.) for full implementations.")

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

        st.write("Use resistive or full impedance models; the resistive approximations shown below are quick checks.")
        st.markdown("Single-phase (2-wire) resistive estimate:")
        eq(r"\Delta V \approx 2\,I\,R\,L")
        st.markdown("Three-phase balanced resistive estimate:")
        eq(r"\Delta V \approx \sqrt{3}\,I\,R\,L")
        st.markdown("Percent voltage drop:")
        eq(r"\%\Delta V = 100\cdot\frac{\Delta V}{V_{nom}}")

        st.markdown("### Notes")
        st.write("- For accurate results include conductor reactance, power factor, and tabulated conductor resistance/impedance per length.")

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

# End of app
