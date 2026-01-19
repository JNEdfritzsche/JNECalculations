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

        # OESC Theory (full, reintroduced)
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
                "where S = apparent power (VA), V_L = line-to-line voltage (V). Use this to calculate primary and secondary FLA:"
            )
            eq(r"I_{pri}=\frac{S}{\sqrt{3}\,V_{pri}}")
            eq(r"I_{sec}=\frac{S}{\sqrt{3}\,V_{sec}}")

            st.markdown("### Methodology (practical steps)")
            st.write(
                "1. Use nameplate FLA if available; otherwise compute FLA using the equation above.\n"
                "2. Identify transformer type (oil-cooled, dry-type) and voltage class (>750 V or ≤750 V).\n"
                "3. Apply the relevant OESC rule to determine the permitted OCPD multiplier (e.g., 150% for fuses, 300% for breakers for certain rules).\n"
                "4. If the calculated device rating does not match a standard device rating, select the **next higher** standard rating as permitted by the rule.\n"
                "5. Verify continuous loading limits (Rule 26-258 and Rule 8-104) and conductor ampacity separately."
            )

            st.markdown("### OESC Rule highlights (key subrules summarized)")
            st.markdown(
                """
**OESC 26-250 — Overcurrent protection for transformers rated over 750 V (oil-cooled example)**  
- Each ungrounded conductor of the transformer feeder shall have overcurrent protection.  
- **Fuses:** rated at not more than **150%** of rated primary current.  
- **Breakers:** rated/set at not more than **300%** of rated primary current.  
- If 150% doesn't match a standard fuse, the next higher standard rating is permitted.

**OESC 26-252 — Overcurrent protection for transformers 750 V or less (other than dry-type)**  
- Primary OCPD generally ≤ **150%** of rated primary current (with exceptions for small currents and secondary protection cases).  
- If rated primary current is ≥ 9 A and 150% doesn't match a standard rating, next higher standard rating permitted.

**OESC 26-254 — Overcurrent protection for dry-type transformers 750 V or less**  
- Primary OCPD generally ≤ **125%** of rated primary current.  
- If the device must withstand inrush, refer to the appendix guidance: device should be able to carry **12× FLA for 0.1 s** and **25× FLA for 0.01 s**.
"""
            )

            st.markdown("### Continuous load and conductor checks")
            st.write(
                "Refer to OESC 26-258 (Transformer continuous load) and Rule 8-104 for limits on continuous loading and conductor ampacity. "
                "These requirements ensure the transformer protection and conductors are coordinated."
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
            st.write("Selected standard size: **110 A** (per Table 13 standard values).")

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

        # NEC Theory (full, reintroduced)
        else:
            st.subheader("NEC — Transformer Protection (Full Theory, simplified)")

            st.markdown("### Objective")
            st.write(
                "Select transformer overcurrent protection (breaker/fuses) in accordance with **NEC Article 450** "
                "so the device ratings meet the code allowances and protect the transformer."
            )

            st.markdown("### Scope & Key references")
            st.write(
                "Focus on NEC 450.3 and tables 450.3(A) / 450.3(B) depending on voltage class. Also consult NEC 240.6(A) for standard ratings."
            )

            st.markdown("### Assumptions (example template)")
            st.markdown(
                """
- Ambient temperature: **40°C**  
- Conductors: **75°C copper**, free-air routing  
- Max cable length: **50 m**  
- Transformer impedance: **≤ 6%** (common example used in the template)  
- Installation: **any location** vs **supervised** (affects table choices)
"""
            )

            st.markdown("### Method / Practical approach")
            st.write(
                "1. Use nameplate FLA when available; otherwise compute FLA for primary and secondary using the 3Φ formula below.  \n"
                "2. Determine whether transformer is >1000 V (use Table 450.3(A)) or ≤1000 V (use Table 450.3(B)).  \n"
                "3. Apply the table-based multipliers/limits to find allowable OCPD ratings.  \n"
                "4. Round to the next standard/commercial device per NEC 240.6(A) as allowed."
            )

            st.markdown("### Rated current formula (3Φ)")
            eq(r"I_L=\frac{S}{\sqrt{3}\,V_L}")
            eq(r"I_{pri}=\frac{S}{\sqrt{3}\,V_{pri}}")
            eq(r"I_{sec}=\frac{S}{\sqrt{3}\,V_{sec}}")

            st.markdown("### NEC 450.3 highlights")
            st.markdown(
                """
**450.3(A)** — Transformers **over 1000 V nominal**: use Table 450.3(A). Table values depend on device type, impedance, and location.  
**450.3(B)** — Transformers **1000 V nominal or less**: use Table 450.3(B). Commonly permits primary-only or primary+secondary schemes.  
**450.3(C)** — Voltage (potential) transformers: typical requirement is primary fusing for indoor/enclosed installations; small control/potential circuits often protected at 15 A or less with listed exceptions.
"""
            )

            st.markdown("### Worked NEC examples (from the NEC calc document)")
            st.write("Example 1 — 2 MVA, 27.6 kV / 4.16 kV, Z ≤ 6%, any location:")
            eq(r"I_{pri}=\frac{2{,}000{,}000}{\sqrt{3}\cdot 27{,}600}\approx 41.89\ \mathrm{A}")
            eq(r"I_{sec}=\frac{2{,}000{,}000}{\sqrt{3}\cdot 4{,}160}\approx 277.90\ \mathrm{A}")
            st.write(
                "Example table-derived (document example) selections: Primary 300 A breaker or 150 A fuse; Secondary 1000 A breaker or 700 A fuse."
            )

            st.write("Example 2 — 75 kVA, 600 V / 208 V (currents > 9 A):")
            eq(r"I_{pri}=\frac{75{,}000}{\sqrt{3}\cdot 600}\approx 72.25\ \mathrm{A}")
            eq(r"I_{sec}=\frac{75{,}000}{\sqrt{3}\cdot 208}\approx 208.43\ \mathrm{A}")
            st.write(
                "Two schemes presented in the document: primary-only → 100 A; primary+secondary → 200 A primary and 300 A secondary (example selections)."
            )

            st.markdown("### Practical design notes (NEC)")
            st.write(
                "NEC transformer OCPD sizing focuses on protecting the transformer. Conductor protection still must be checked under Article 240. Coordination, relay protection for large transformers (ANSI 50/51), and grounding/winding configuration should all be considered."
            )

    # Calculator tab for Transformer Protection
    with calc_tab:
        header("Transformer Protection Calculator", "Compute transformer currents + suggested OCPD limits (template).")
        show_code_note(code_mode)

        col1, col2, col3 = st.columns(3, gap="large")
        with col1:
            kva = st.number_input("Transformer size (kVA)", min_value=0.1, value=75.0, step=1.0)
        with col2:
            vpri = st.number_input("Primary voltage (V LL)", min_value=1.0, value=600.0, step=1.0)
        with col3:
            vsec = st.number_input("Secondary voltage (V LL)", min_value=1.0, value=208.0, step=1.0)

        st.markdown("### Full-load current (3Φ assumed)")
        Ip = (kva * 1000.0) / (math.sqrt(3) * vpri)
        Is = (kva * 1000.0) / (math.sqrt(3) * vsec)

        c1, c2 = st.columns(2)
        c1.metric("Primary FLA", fmt(Ip, "A"))
        c2.metric("Secondary FLA", fmt(Is, "A"))

        st.divider()
        st.markdown("### OCPD sizing helpers / quick suggestions")

        if code_mode == "OESC":
            oesc_path = st.selectbox(
                "OESC path (simplified)",
                [
                    "26-250 (>750V) — Fuse 150% / Breaker 300%",
                    "26-252 (≤750V non-dry) — Primary 150% (common case)",
                    "26-254 (≤750V dry-type) — Primary 125% + inrush checks",
                ],
                index=1,
            )

            if oesc_path.startswith("26-250"):
                st.success(f"Max Fuse (150%): **{fmt(Ip * 1.50, 'A')}**")
                st.success(f"Max Breaker (300%): **{fmt(Ip * 3.00, 'A')}**")
                st.caption("Pick the next standard rating per your standard device table (e.g., OESC Table 13).")

            elif oesc_path.startswith("26-252"):
                st.success(f"Max Primary OCPD (150%): **{fmt(Ip * 1.50, 'A')}**")
                st.caption("OESC 26-252 includes additional allowances for small currents and certain secondary-protection cases.")

            else:
                st.success(f"Max Primary OCPD (125%): **{fmt(Ip * 1.25, 'A')}**")
                st.markdown("**Inrush withstand checks (Appendix guidance):**")
                st.write(f"12× FLA for 0.1 s: **{fmt(Ip * 12, 'A')}**")
                st.write(f"25× FLA for 0.01 s: **{fmt(Ip * 25, 'A')}**")
                st.caption("Verify device curves / manufacturer data to confirm short-duration withstand capability.")

        else:  # NEC
            nec_path = st.selectbox(
                "NEC path (simplified)",
                [
                    "450.3(A) — Transformers >1000V (table-based)",
                    "450.3(B) — Transformers ≤1000V (table-based)",
                    "450.3(C) — Voltage (Potential) Transformers (notes-based)",
                ],
                index=1,
            )

            st.caption(
                "This calculator shows currents and provides example-style outputs. To fully automate NEC table lookups, add inputs for impedance, location (any vs supervised), and the full Table 450.3 multipliers."
            )

            if nec_path.startswith("450.3(A)"):
                st.markdown("### Example-style outputs (Document example)")
                st.write("For a 2 MVA, 27.6 kV / 4.16 kV transformer (Z ≤ 6%, any location):")
                st.success("Primary: **300 A breaker** or **150 A fuse**")
                st.success("Secondary: **1000 A breaker** or **700 A fuse**")
                st.caption("To automate: add impedance + location inputs and table multipliers from NEC 450.3(A).")

            elif nec_path.startswith("450.3(B)"):
                st.markdown("### Example-style outputs (Document example)")
                st.write("For a 75 kVA, 600 V / 208 V transformer (currents > 9 A):")
                st.success("Method 1 (Primary-only): **100 A**")
                st.success("Method 2 (Primary + Secondary): **200 A primary**, **300 A secondary**")
                st.caption("To automate: add Method 1/2 selection and drive the limits from Table 450.3(B).")

            else:
                st.markdown(
                    """
### NEC 450.3(C) quick notes (simplified)
- Indoor/enclosed voltage (potential) transformers: **primary fuses recommended/required** in many cases
- Certain potential-coil switchgear devices commonly supplied from circuits protected at **15 A or less**
"""
                )

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
