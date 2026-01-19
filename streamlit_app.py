import math
import streamlit as st

# ----------------------------
# Page config + simple styling
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
    """Nice number formatting with optional unit."""
    if x is None:
        return "—"
    if abs(x) >= 1e6:
        s = f"{x:,.3g}"
    elif abs(x) >= 1:
        s = f"{x:,.4g}"
    else:
        s = f"{x:.6g}"
    return f"{s} {unit}".strip()


def section_header(title: str, subtitle: str = ""):
    st.subheader(title)
    if subtitle:
        st.write(subtitle)


# ----------------------------
# Sidebar navigation
# ----------------------------
with st.sidebar:
    st.header("Navigate")
    page = st.radio(
        "Go to",
        [
            "Home",
            "Theory & Examples",
            "Calculators",
            "Reference Tables",
            "About",
        ],
        index=0,
    )

    st.divider()
    st.write("**Unit Preferences**")
    unit_system = st.selectbox("Units", ["SI (V, A, Ω, W)", "SI + k (kW, kVA)"], index=1)

    st.divider()
    st.write("**Notes**")
    st.info(
        "This is a template. Add topics, calculators, and tables as your site grows.\n\n"
        "Tip: Put long theory text in separate markdown files later."
    )


# ----------------------------
# HOME
# ----------------------------
if page == "Home":
    col1, col2 = st.columns([1.4, 1.0], gap="large")

    with col1:
        section_header("Welcome", "Use the left menu to explore theory or run calculations.")
        st.markdown(
            """
### What you can do here
- Learn fundamentals (Ohm’s Law, power, three-phase, etc.)
- Work through examples step-by-step
- Use calculators for quick engineering checks

### Common calculators to add next
- Voltage drop (single/three-phase)
- Conductor sizing helper
- Motor FLA / overload quick check
- Transformer sizing
- Power factor correction
            """
        )

    with col2:
        st.markdown("### Quick Start")
        st.success("Pick **Calculators → Ohm’s Law & Power** to try the calculator.")
        st.markdown("### Roadmap (editable)")
        st.checkbox("Add voltage drop calculator", value=True)
        st.checkbox("Add three-phase power calculator", value=True)
        st.checkbox("Add PF correction calculator", value=False)
        st.checkbox("Add short-circuit basics page", value=False)


# ----------------------------
# THEORY & EXAMPLES
# ----------------------------
elif page == "Theory & Examples":
    st.header("📚 Theory & Examples")

    topic = st.selectbox(
        "Choose a topic",
        [
            "Ohm’s Law",
            "Power (DC / AC basics)",
            "Series & Parallel Resistors",
            "Three-Phase Basics",
        ],
        index=0,
    )

    st.divider()

    if topic == "Ohm’s Law":
        st.markdown(
            r"""
## Ohm’s Law

**Core relationship:**
- \( V = I \cdot R \)
- \( I = \frac{V}{R} \)
- \( R = \frac{V}{I} \)

Where:
- \(V\) = voltage (V)
- \(I\) = current (A)
- \(R\) = resistance (Ω)

### Example
A resistor is **12 Ω** and the current is **2 A**.  
Find the voltage:

\[
V = I \cdot R = 2 \cdot 12 = 24\ \text{V}
\]
            """
        )

    elif topic == "Power (DC / AC basics)":
        st.markdown(
            r"""
## Power Basics

### DC (or resistive AC)
\[
P = V \cdot I
\]

### Using Ohm’s law substitutions
\[
P = I^2R
\]
\[
P = \frac{V^2}{R}
\]

### AC real power (single-phase)
\[
P = V \cdot I \cdot \text{PF}
\]
Where PF = power factor (0–1)

### Example (AC)
A 120 V load draws 8 A at PF = 0.9:

\[
P = 120 \cdot 8 \cdot 0.9 = 864\ \text{W}
\]
            """
        )

    elif topic == "Series & Parallel Resistors":
        st.markdown(
            r"""
## Series & Parallel Resistors

### Series
\[
R_{eq} = R_1 + R_2 + \dots
\]

### Parallel
\[
\frac{1}{R_{eq}} = \frac{1}{R_1} + \frac{1}{R_2} + \dots
\]

### Example (parallel)
Two resistors: 10 Ω and 20 Ω:

\[
\frac{1}{R_{eq}} = \frac{1}{10} + \frac{1}{20} = 0.1 + 0.05 = 0.15
\]
\[
R_{eq} = \frac{1}{0.15} \approx 6.67\ \Omega
\]
            """
        )

    elif topic == "Three-Phase Basics":
        st.markdown(
            r"""
## Three-Phase Basics

### Line-to-line vs phase
For a balanced system:
- \( V_{LL} = \sqrt{3}\, V_{ph} \)

### Power (real power)
\[
P = \sqrt{3}\, V_{LL}\, I_{L}\, \text{PF}
\]

### Example
A 400 V (LL) system, 10 A line current, PF = 0.85:

\[
P = 1.732 \cdot 400 \cdot 10 \cdot 0.85 \approx 5889\ \text{W}
\]
            """
        )


# ----------------------------
# CALCULATORS
# ----------------------------
elif page == "Calculators":
    st.header("🧮 Calculators")

    calc = st.selectbox(
        "Choose a calculator",
        [
            "Ohm’s Law & Power",
            "Series / Parallel Resistance",
            "Single-Phase AC Power",
            "Three-Phase AC Power",
        ],
        index=0,
    )

    st.divider()

    # ---- Ohm's Law & Power ----
    if calc == "Ohm’s Law & Power":
        section_header("Ohm’s Law & Power Calculator", "Enter any two values to compute the rest.")

        colA, colB, colC = st.columns(3, gap="large")
        with colA:
            V = st.number_input("Voltage V (V)", min_value=0.0, value=120.0, step=1.0)
        with colB:
            I = st.number_input("Current I (A)", min_value=0.0, value=10.0, step=0.1)
        with colC:
            R_mode = st.selectbox("Solve for", ["Resistance (Ω)", "Current (A)", "Voltage (V)"], index=0)

        st.markdown("### Results")

        R = None
        P = None

        if R_mode == "Resistance (Ω)":
            if I > 0:
                R = V / I
                P = V * I
            else:
                st.warning("Current must be > 0 to compute resistance.")
        elif R_mode == "Current (A)":
            R = st.number_input("Resistance R (Ω)", min_value=0.0, value=12.0, step=0.1)
            if R > 0:
                I = V / R
                P = V * I
            else:
                st.warning("Resistance must be > 0 to compute current.")
        else:  # Voltage
            R = st.number_input("Resistance R (Ω)", min_value=0.0, value=12.0, step=0.1)
            if R >= 0:
                V = I * R
                P = V * I

        k = 1000.0
        show_kw = (unit_system == "SI + k (kW, kVA)")

        c1, c2, c3 = st.columns(3)
        c1.metric("Voltage (V)", fmt(V, "V"))
        c2.metric("Current (A)", fmt(I, "A"))
        c3.metric("Resistance (Ω)", fmt(R, "Ω") if R is not None else "—")

        if P is not None:
            st.metric("Power", fmt(P / k, "kW") if show_kw else fmt(P, "W"))

        with st.expander("Show formulas"):
            st.markdown(
                r"""
- \(V = I \cdot R\)
- \(I = \frac{V}{R}\)
- \(R = \frac{V}{I}\)
- \(P = V \cdot I\)
                """
            )

    # ---- Series/Parallel Resistance ----
    elif calc == "Series / Parallel Resistance":
        section_header("Equivalent Resistance", "Compute series or parallel resistance for up to 6 resistors.")
        mode = st.radio("Mode", ["Series", "Parallel"], horizontal=True)

        cols = st.columns(3)
        Rs = []
        for idx in range(6):
            with cols[idx % 3]:
                r = st.number_input(f"R{idx+1} (Ω) — set 0 to ignore", min_value=0.0, value=0.0, step=0.5)
                if r > 0:
                    Rs.append(r)

        if not Rs:
            st.info("Enter at least one resistance > 0.")
        else:
            if mode == "Series":
                Req = sum(Rs)
                st.success(f"Equivalent resistance: **{fmt(Req, 'Ω')}**")
            else:
                inv = sum(1.0 / r for r in Rs if r > 0)
                if inv > 0:
                    Req = 1.0 / inv
                    st.success(f"Equivalent resistance: **{fmt(Req, 'Ω')}**")
                else:
                    st.warning("Parallel calculation requires resistances > 0.")

        with st.expander("Show formulas"):
            st.markdown(
                r"""
**Series:** \(R_{eq} = R_1 + R_2 + \dots\)

**Parallel:** \(\frac{1}{R_{eq}} = \frac{1}{R_1} + \frac{1}{R_2} + \dots\)
                """
            )

    # ---- Single-phase AC power ----
    elif calc == "Single-Phase AC Power":
        section_header("Single-Phase AC Power", "Real, apparent, and reactive power from V, I, and PF.")

        col1, col2, col3 = st.columns(3, gap="large")
        with col1:
            V = st.number_input("Voltage (V RMS)", min_value=0.0, value=120.0, step=1.0)
        with col2:
            I = st.number_input("Current (A)", min_value=0.0, value=10.0, step=0.1)
        with col3:
            PF = st.number_input("Power factor (0–1)", min_value=0.0, max_value=1.0, value=0.9, step=0.01)

        S = V * I  # VA
        P = S * PF  # W
        # Q = sqrt(S^2 - P^2)
        Q = math.sqrt(max(S * S - P * P, 0.0))

        show_kw = (unit_system == "SI + k (kW, kVA)")
        k = 1000.0

        c1, c2, c3 = st.columns(3)
        c1.metric("Apparent Power (S)", fmt(S / k, "kVA") if show_kw else fmt(S, "VA"))
        c2.metric("Real Power (P)", fmt(P / k, "kW") if show_kw else fmt(P, "W"))
        c3.metric("Reactive Power (Q)", fmt(Q / k, "kVAr") if show_kw else fmt(Q, "VAr"))

        with st.expander("Show formulas"):
            st.markdown(
                r"""
- \(S = V \cdot I\)
- \(P = V \cdot I \cdot PF\)
- \(Q = \sqrt{S^2 - P^2}\)
                """
            )

    # ---- Three-phase AC power ----
    elif calc == "Three-Phase AC Power":
        section_header("Three-Phase AC Power", "Balanced 3Φ power from V_LL, I_L, and PF.")

        col1, col2, col3 = st.columns(3, gap="large")
        with col1:
            VLL = st.number_input("Line-to-line voltage (V_LL)", min_value=0.0, value=400.0, step=1.0)
        with col2:
            IL = st.number_input("Line current (I_L) (A)", min_value=0.0, value=10.0, step=0.1)
        with col3:
            PF = st.number_input("Power factor (0–1)", min_value=0.0, max_value=1.0, value=0.85, step=0.01)

        S = math.sqrt(3) * VLL * IL  # VA
        P = S * PF  # W
        Q = math.sqrt(max(S * S - P * P, 0.0))

        show_kw = (unit_system == "SI + k (kW, kVA)")
        k = 1000.0

        c1, c2, c3 = st.columns(3)
        c1.metric("Apparent Power (S)", fmt(S / k, "kVA") if show_kw else fmt(S, "VA"))
        c2.metric("Real Power (P)", fmt(P / k, "kW") if show_kw else fmt(P, "W"))
        c3.metric("Reactive Power (Q)", fmt(Q / k, "kVAr") if show_kw else fmt(Q, "VAr"))

        with st.expander("Show formulas"):
            st.markdown(
                r"""
- \(S = \sqrt{3}\, V_{LL}\, I_L\)
- \(P = \sqrt{3}\, V_{LL}\, I_L\, PF\)
- \(Q = \sqrt{S^2 - P^2}\)
                """
            )


# ----------------------------
# REFERENCE TABLES
# ----------------------------
elif page == "Reference Tables":
    st.header("📌 Reference Tables")

    st.markdown("Use this section for quick lookup tables you frequently reference.")

    tab1, tab2 = st.tabs(["Common Wire Resistivity", "Common Conversions"])

    with tab1:
        st.markdown("### Copper & Aluminum (approx, 20°C)")
        st.write("Add your preferred source and values here (template table below).")
        st.table(
            [
                {"Material": "Copper", "Resistivity (Ω·m)": "1.68e-8"},
                {"Material": "Aluminum", "Resistivity (Ω·m)": "2.82e-8"},
            ]
        )

    with tab2:
        st.markdown("### Conversions")
        st.table(
            [
                {"From": "kW", "To": "W", "Multiply by": "1000"},
                {"From": "kVA", "To": "VA", "Multiply by": "1000"},
                {"From": "hp", "To": "W", "Multiply by": "746 (approx)"},
            ]
        )


# ----------------------------
# ABOUT
# ----------------------------
elif page == "About":
    st.header("ℹ️ About")
    st.markdown(
        """
This is a starter template for an electrical calculations site built with Streamlit.

**How to expand it:**
- Add new topics under **Theory & Examples**
- Add calculators under **Calculators**
- Move long theory into external `.md` files later (optional)
- Add citations/standards references in your theory pages (e.g., NEC/CEC notes)
        """
    )
