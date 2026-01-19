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
        header("Transformer Protection", "Code-focused summary with a simple step-by-step method.")
        show_code_note(code_mode)

        if code_mode == "OESC":
            st.markdown(
                r"""
## OESC Transformer Protection (Simple Guide)

### Objective
Select transformer overcurrent protection (breaker and/or fuses) to satisfy the **Ontario Electrical Safety Code (OESC)** rules for transformer circuits.

---

## Scope (what this calculation covers)
- Calculate **primary** and **secondary** full-load current (FLA)
- Determine **maximum permitted** OCPD ratings/settings using the correct OESC rule
- Convert calculated values to **standard device ratings** (commonly selected from **OESC Table 13**)
- Note when **secondary protection or manufacturer protection** may allow relaxed primary requirements

---

## Key OESC references (common ones used)
- **26-248** — Disconnecting means for transformers (primary disconnect required)
- **26-250** — Overcurrent protection for power/distribution transformers **over 750 V**
- **26-252** — Overcurrent protection for power/distribution transformers **750 V or less**, other than dry-type
- **26-254** — Overcurrent protection for **dry-type** transformers **750 V or less**
- **26-258** — Transformer continuous load (ties into Rule 8-104)
- **8-104** — Maximum circuit loading (continuous loading limits)

---

## Assumptions (example template)
- Ambient temperature: **40°C**
- Conductor temperature rating: **75°C**
- Copper conductors, free-air (field routed)
- No more than 3 conductors per cable (incl. ground)
- Max cable length: **50 m**
- Natural cooling (no fans/pumps)

---

## Step 1 — Get the transformer full-load currents
**Use nameplate FLA if available.** If not, calculate (3Φ):

\[
I_L=\frac{S}{\sqrt{3}\,V_L}
\]

Compute both:
- **Primary FLA:** \(I_{pri} = \frac{S}{\sqrt{3}\,V_{pri}}\)
- **Secondary FLA:** \(I_{sec} = \frac{S}{\sqrt{3}\,V_{sec}}\)

---

## Step 2 — Choose the correct OESC rule path
Pick the rule based on **voltage** and **transformer type**:

### A) Oil-cooled (or liquid-filled) **> 750 V** → **Rule 26-250**
- **Fuses:** ≤ **150%** of rated primary current  
- **Breakers:** ≤ **300%** of rated primary current  
If 150% does not match a standard fuse size, the **next higher standard** is permitted.

### B) Non-dry-type **≤ 750 V** → **Rule 26-252**
- Primary OCPD generally ≤ **150%** of rated primary current  
Special allowances exist for smaller currents and for some secondary-protection cases.

### C) Dry-type **≤ 750 V** → **Rule 26-254**
- Primary OCPD generally ≤ **125%** of rated primary current  
If 125% doesn’t match a standard rating, **next higher standard** is permitted.
- Appendix guidance: device should be able to carry
  - **12× FLA for 0.1 s**
  - **25× FLA for 0.01 s**

---

## Step 3 — Convert to a standard device rating
After calculating the allowable OCPD value:
- Select the **next appropriate standard size** (commonly from **OESC Table 13**).

---

## Worked Examples (from the template)

### Example 1 — Oil-cooled, **> 750 V** (Rule 26-250)
**2,000 kVA**, **27.6 kV / 600 V**, 3Φ

Primary FLA:
\[
I_{pri}=\frac{2{,}000{,}000}{1.732\cdot 27{,}600}\approx 41.89\text{ A}
\]

- Max fuse (150%): \(41.89\times 1.5 \approx 62.83\text{ A}\) → **select 70 A (standard)**
- Max breaker (300%): \(41.89\times 3.0 \approx 125.66\text{ A}\) → **select 150 A (standard)**

### Example 2 — Non-dry-type, **≤ 750 V** (Rule 26-252)
**75 kVA**, **600 V / 208 V**, 3Φ

Primary FLA:
\[
I_{pri}=\frac{75{,}000}{1.732\cdot 600}\approx 72.17\text{ A}
\]

- Max primary OCPD (150%): \(72.17\times 1.5 \approx 108.26\text{ A}\) → **select 110 A (standard)**

### Example 3 — Dry-type, **≤ 750 V** (Rule 26-254)
**75 kVA**, **600 V / 208 V**, 3Φ

- Max primary OCPD (125%): \(72.17\times 1.25 \approx 90.21\text{ A}\) → **select 100 A (standard)**
- Inrush withstand (Appendix guidance):
  - 12×: \(72.17\times 12 \approx 866\text{ A}\) for 0.1 s
  - 25×: \(72.17\times 25 \approx 1804\text{ A}\) for 0.01 s

---

## Practical design notes (after sizing)
- Confirm **continuous loading** meets **Rule 26-258** and **Rule 8-104**
- Confirm conductor ampacity and installation conditions (separate feeder calculation)
- Perform a **coordination study** where needed (selectivity + equipment protection)
- Consider winding configuration and grounding method (often Δ–Y for distribution)
"""
            )

        else:  # NEC
            st.markdown(
                r"""
## NEC Transformer Protection (Simple Guide)

### Objective
Select transformer overcurrent protection (breaker and/or fuses) that complies with **NEC 450.3** using transformer nameplate data (preferred) or calculated full-load current (FLA).

---

## Scope (what this calculation covers)
- Calculate **primary** and **secondary** full-load currents
- Select which NEC pathway applies:
  - **450.3(A)** — Transformers **over 1000 V nominal**
  - **450.3(B)** — Transformers **1000 V nominal or less**
  - **450.3(C)** — Voltage (potential) transformers
- Use **Table 450.3(A)** or **Table 450.3(B)** to determine the **maximum permitted** OCPD rating/setting
- Select a **standard rating** from **NEC 240.6(A)** (or the next commercially available size where permitted)

---

## Applicable NEC references (as used in the design calc)
- **NEC 450.3** — Transformer overcurrent protection (A), (B), or (C)
- **Table 450.3(A)** — Transformers over 1000 V
- **Table 450.3(B)** — Transformers 1000 V or less
- **NEC 240.6(A)** — Standard ampere ratings

---

## Assumptions (template)
- Ambient temperature: **40°C**
- Conductor temperature rating: **75°C**
- Copper conductors, free-air (field routed)
- No more than 3 conductors per cable (incl. ground)
- Max cable length: **50 m**
- Transformer impedance **≤ 6%**
- Transformer operating in **“any location”** (unsupervised)

---

## Step 1 — Find transformer rated current (FLA)
Use nameplate data when available. If FLA is unknown, calculate for 3Φ:

\[
I_L=\frac{S}{\sqrt{3}\,V_L}
\]

Compute:
- Primary FLA: \(I_{pri} = \frac{S}{\sqrt{3}\,V_{pri}}\)
- Secondary FLA: \(I_{sec} = \frac{S}{\sqrt{3}\,V_{sec}}\)

---

## Step 2 — Apply NEC 450.3 based on transformer class

### A) **450.3(A)** — Transformers **over 1000 V nominal**
- Overcurrent protection is selected using **Table 450.3(A)**.
- Table 450.3(A) depends on:
  - protective device type (fuse / electronic fuse / breaker),
  - transformer-rated current and impedance,
  - primary/secondary voltages,
  - and whether the transformer is in **“any location”** vs **supervised location**.

**Key table notes (simplified):**
1) If the computed rating/setting is not standard:
   - You may select the **next higher standard rating** for devices **1000 V and below**, or
   - the **next higher commercially available** rating/setting for devices **over 1000 V**.
2) Where secondary OCPD is required, it may be **up to six** breakers or **six sets of fuses** grouped in one location,
   and the **sum** of their ratings must not exceed the allowance for a single device.

> The design calc emphasizes that secondary OCPD requirements in 450.3 are for **transformer protection** (not automatically conductor protection).
> Conductor protection is addressed separately under **Article 240**.

### B) **450.3(B)** — Transformers **1000 V nominal or less**
- Overcurrent protection is selected using **Table 450.3(B)**.
- Table 450.3(B) effectively supports two common approaches:
  1) **Primary-only protection**, or
  2) **Primary + secondary protection** (secondary limited per table, with corresponding primary limits).
- If **125%** does not correspond to a standard fuse/nonadjustable breaker size, the **next higher standard** size is permitted (see the table notes and 240.6(A)).

### C) **450.3(C)** — Voltage (potential) transformers
- Voltage (potential) transformers installed **indoors or enclosed** shall be protected with **primary fuses**.
- Certain instruments/pilot lights/PTs with potential coils in switchgear are typically supplied by a circuit protected at **15 A or less**, with listed exceptions.

---

## Step 3 — Choose the standard device size
After applying Table 450.3(A/B):
- Select the **next standard size** using **NEC 240.6(A)** (or next commercially available, where allowed by table notes).

---

## Worked Examples (from the NEC template conclusions)

### Example 1 — **450.3(A)** (Over 1000 V), Z ≤ 6%, **any location**
**2 MVA**, **27.6 kV / 4.16 kV**, 3Φ

Primary FLA:
\[
I_{pri}=\frac{2{,}000{,}000}{1.732\cdot 27{,}600}\approx 41.89\text{ A}
\]

Secondary FLA:
\[
I_{sec}=\frac{2{,}000{,}000}{1.732\cdot 4{,}160}\approx 277.90\text{ A}
\]

Using **Table 450.3(A)** for the selected conditions, the standard OCPD selections shown were:
- **Primary:** 300 A breaker **or** 150 A fuse
- **Secondary:** 1000 A breaker **or** 700 A fuse

### Example 2 — **450.3(B)** (1000 V or less), currents > 9 A
**75 kVA**, **600 V / 208 V**, 3Φ

Two schemes were shown:

**(1) Primary-only protection**
- **Breaker or fuse:** 100 A

**(2) Primary + secondary protection**
- **Primary:** 200 A (breaker or fuse)
- **Secondary:** 300 A (breaker or fuse)

---

## Practical design notes (after sizing)
- **450.3 is transformer protection.** Conductor protection must be checked under **Article 240** where applicable.
- Consider coordination (selectivity), device availability, and what each protective element is protecting.
- Larger transformer applications may use relays (e.g., ANSI 50/51) as part of the overall protection strategy.
- Confirm feeder conductor sizing separately (Transformer Feeders page).
"""
            )

    with calc_tab:
        header("Transformer Protection Calculator", "Compute transformer currents and basic OCPD limits (template).")
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
        st.markdown("### OCPD sizing helpers")

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
                "This calculator currently shows FLA and provides example-style outputs. "
                "Next step (if you want full automation) is implementing Table 450.3(A/B) lookups."
            )

            if nec_path.startswith("450.3(A)"):
                st.markdown("### Example-style outputs (from the NEC calc template conclusions)")
                st.write("For a 2 MVA, 27.6 kV / 4.16 kV transformer (Z ≤ 6%, any location):")
                st.success("Primary: **300 A breaker** or **150 A fuse**")
                st.success("Secondary: **1000 A breaker** or **700 A fuse**")
                st.caption("To automate: add impedance + location inputs and table multipliers from NEC 450.3(A).")

            elif nec_path.startswith("450.3(B)"):
                st.markdown("### Example-style outputs (from the NEC calc template conclusions)")
                st.write("For a 75 kVA, 600 V / 208 V transformer (currents > 9 A):")
                st.success("Method 1 (Primary-only): **100 A**")
                st.success("Method 2 (Primary + Secondary): **200 A primary**, **300 A secondary**")
                st.caption("To automate: add Method 1/2 selection and table logic from NEC 450.3(B).")

            else:
                st.markdown(
                    """
### NEC 450.3(C) quick notes (simplified)
- Indoor/enclosed voltage (potential) transformers: **primary fuses required**
- Potential-coil switchgear devices are commonly supplied from circuits protected at **15 A or less**
- Exceptions exist (hazard interruption, very small ratings, etc.)
"""
                )

# ============================
# 2) Transformer Feeders
# ============================
elif page == "Transformer Feeders":
    with theory_tab:
        header("Transformer Feeders", "Feeder sizing concepts around transformer loads (template).")
        show_code_note(code_mode)

        st.markdown(
            r"""
### Key ideas (template)
- Feeder ampacity typically starts from transformer secondary full-load current
- Consider continuous loads, ambient/temp correction, conductor ratings, and coordination

### Example (simplified)
A **150 kVA**, **600V–208Y/120V** transformer:
\[
I_{sec} = \frac{150{,}000}{1.732 \cdot 208} \approx 416\text{ A}
\]

Start by sizing conductors ≥ this current (then apply code adjustments).
"""
        )

    with calc_tab:
        header("Transformer Feeder Calculator", "Compute secondary full-load current and a basic feeder ampacity target.")
        show_code_note(code_mode)

        col1, col2 = st.columns(2, gap="large")
        with col1:
            kva = st.number_input("Transformer size (kVA)", min_value=0.1, value=150.0, step=1.0, key="tf_kva")
        with col2:
            vsec = st.number_input("Secondary voltage (V LL)", min_value=1.0, value=208.0, step=1.0, key="tf_vsec")

        continuous = st.checkbox("Treat as continuous load (125%)", value=True)
        Is = (kva * 1000.0) / (math.sqrt(3) * vsec)
        target = Is * (1.25 if continuous else 1.0)

        st.metric("Secondary full-load current (A)", fmt(Is, "A"))
        st.success(f"Feeder ampacity target: **{fmt(target, 'A')}**")

# ============================
# 3) Grounding/Bonding Conductor Sizing
# ============================
elif page == "Grounding/Bonding Conductor Sizing":
    with theory_tab:
        header("Grounding/Bonding Conductor Sizing", "Conceptual sizing workflow (template).")
        show_code_note(code_mode)

        st.markdown(
            r"""
### Template concepts
- Grounding electrode conductor (GEC) vs equipment grounding conductor (EGC) vs bonding jumper
- Many codes size based on **largest ungrounded conductor** or **OCPD rating**

### Example (placeholder)
If an upstream OCPD is **200 A**, many workflows size the equipment grounding conductor from a table.

> Add your NEC/OESC table references here, and optionally embed a lookup table.
"""
        )

    with calc_tab:
        header("Grounding/Bonding Sizing Helper", "Simple placeholder (replace with real NEC/OESC table logic).")
        show_code_note(code_mode)

        ocpd = st.number_input("Upstream OCPD rating (A)", min_value=1.0, value=200.0, step=1.0)

        # Placeholder "table" logic (NOT code-accurate)
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
        st.caption("Replace this with real table-driven logic for NEC/OESC.")

# ============================
# 4) Motor Protection
# ============================
elif page == "Motor Protection":
    with theory_tab:
        header("Motor Protection", "Overload vs short-circuit/ground-fault protection (template).")
        show_code_note(code_mode)

        st.markdown(
            r"""
### Motor protection types
- **Overload protection**: protects motor from overheating (often based on nameplate/current)
- **Short-circuit / ground-fault**: protects conductors/equipment (often based on tables/multipliers)

### Example (simplified)
A motor with **FLA = 28 A**:
- Overload may be set around **115%–125%** depending on motor/service factor and code.
"""
        )

    with calc_tab:
        header("Motor Protection Calculator", "Overload setting estimate + short-circuit device estimate (simplified).")
        show_code_note(code_mode)

        fla = st.number_input("Motor full-load amps (FLA)", min_value=0.1, value=28.0, step=0.1)
        ol_mult = st.selectbox("Overload multiplier (simplified)", ["115%", "125%"], index=1)
        ol = fla * (1.15 if ol_mult == "115%" else 1.25)

        sc_mult = st.selectbox("Short-circuit device multiplier (placeholder)", ["175%", "250%"], index=0)
        sc = fla * (1.75 if sc_mult == "175%" else 2.50)

        c1, c2 = st.columns(2)
        c1.metric("Overload setting (A)", fmt(ol, "A"))
        c2.metric("Short-circuit device (A)", fmt(sc, "A"))
        st.caption("Multipliers here are placeholders; implement your preferred NEC/OESC rule set.")

# ============================
# 5) Motor Feeder
# ============================
elif page == "Motor Feeder":
    with theory_tab:
        header("Motor Feeder", "Feeder sizing for motor circuits (template).")
        show_code_note(code_mode)

        st.markdown(
            r"""
### Template concepts
- Motor branch-circuit conductors may be sized at a % of FLA (often 125% for single motor)
- Feeders supplying multiple motors add additional allowances

### Example (single motor, simplified)
Motor FLA = 40 A  
Conductor ampacity target:
\[
I_{target} = 1.25 \cdot 40 = 50\text{ A}
\]
"""
        )

    with calc_tab:
        header("Motor Feeder Calculator", "Single-motor conductor ampacity target (simplified).")
        show_code_note(code_mode)

        fla = st.number_input("Motor FLA (A)", min_value=0.1, value=40.0, step=0.1, key="mf_fla")
        cont = st.checkbox("Apply 125% factor", value=True)
        target = fla * (1.25 if cont else 1.0)
        st.success(f"Conductor ampacity target: **{fmt(target, 'A')}**")

# ============================
# 6) Cable Tray Size & Fill & Bend Radius
# ============================
elif page == "Cable Tray Size & Fill & Bend Radius":
    with theory_tab:
        header("Cable Tray Size, Fill & Bend Radius", "Basics for organizing tray layouts (template).")
        show_code_note(code_mode)

        st.markdown(
            r"""
### Tray sizing concepts (template)
- Tray **width/depth** selection depends on cable OD, quantity, and fill rules
- **Bend radius** often based on cable type and overall diameter (OD)

### Example (simplified fill)
If you have 20 cables with OD = 20 mm, a rough area estimate:
\[
A \approx n \cdot \pi(\frac{d}{2})^2
\]
Then compare to allowable tray fill area (your rule set).
"""
        )

    with calc_tab:
        header("Tray Fill & Bend Radius Calculator", "Estimate cable area + suggest a bend radius from OD (rule-of-thumb).")
        show_code_note(code_mode)

        col1, col2, col3 = st.columns(3, gap="large")
        with col1:
            n = st.number_input("Number of cables", min_value=1, value=20, step=1)
        with col2:
            od_mm = st.number_input("Cable OD (mm)", min_value=1.0, value=20.0, step=0.5)
        with col3:
            tray_width_mm = st.number_input("Tray inside width (mm)", min_value=50.0, value=300.0, step=10.0)

        cable_area_mm2 = n * math.pi * (od_mm / 2.0) ** 2
        tray_area_mm2 = tray_width_mm * od_mm  # very rough single-layer estimate

        st.metric("Estimated total cable cross-sectional area", fmt(cable_area_mm2, "mm²"))
        st.metric("Rough single-layer tray area (width × OD)", fmt(tray_area_mm2, "mm²"))
        st.caption("This is a rough geometric estimate. Real tray fill rules vary by code and tray type.")

        br_mult = st.selectbox("Bend radius multiplier (rule-of-thumb)", ["8× OD", "12× OD", "16× OD"], index=1)
        mult = {"8× OD": 8, "12× OD": 12, "16× OD": 16}[br_mult]
        bend_radius_mm = mult * od_mm
        st.success(f"Suggested minimum bend radius (rule-of-thumb): **{fmt(bend_radius_mm, 'mm')}**")

# ============================
# 7) Conduit Size & Fill & Bend Radius
# ============================
elif page == "Conduit Size & Fill & Bend Radius":
    with theory_tab:
        header("Conduit Size, Fill & Bend Radius", "Conduit fill and bending considerations (template).")
        show_code_note(code_mode)

        st.markdown(
            r"""
### Template concepts
- Conduit fill is typically limited by % cross-sectional area (depends on number of conductors)
- Bend radius depends on conduit type and trade size; also watch pull tension

### Example (simplified)
If conduit inner area is \(A_c\) and conductors total area \(A_w\):
\[
\text{Fill} = \frac{A_w}{A_c}
\]
Compare to your allowed % fill.
"""
        )

    with calc_tab:
        header("Conduit Fill Calculator", "Compute fill % using areas (you supply areas).")
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
            st.metric("Fill ratio", fmt(fill * 100.0, "%"))
            st.caption("Compare this against your NEC/OESC fill limits for conductor count/type.")

        st.markdown("### Bend radius (rule-of-thumb)")
        conduit_id_mm = st.number_input("Conduit ID (mm) (optional)", min_value=0.0, value=25.0, step=1.0)
        br = 6 * conduit_id_mm
        st.success(f"Rule-of-thumb bend radius: **{fmt(br, 'mm')}**")
        st.caption("Replace with your preferred conduit-type-based rule set.")

# ============================
# 8) Cable Tray Ampacity
# ============================
elif page == "Cable Tray Ampacity":
    with theory_tab:
        header("Cable Tray Ampacity", "Ampacity depends on installation method, spacing, and insulation (template).")
        show_code_note(code_mode)

        st.markdown(
            r"""
### Template concepts
- Tray ampacity depends on cable type, quantity, spacing, ambient temperature, and grouping
- Many designs start with base ampacity then apply derating factors

### Example (simplified)
If base ampacity is 200 A and grouping factor is 0.8:
\[
I_{adj} = 200 \cdot 0.8 = 160\text{ A}
\]
"""
        )

    with calc_tab:
        header("Ampacity Derating Calculator", "Apply a base ampacity and derating factors (template).")
        show_code_note(code_mode)

        base = st.number_input("Base ampacity (A)", min_value=0.1, value=200.0, step=1.0)
        grouping = st.number_input("Grouping factor", min_value=0.0, max_value=1.0, value=0.80, step=0.01)
        ambient = st.number_input("Ambient factor", min_value=0.0, max_value=1.5, value=1.00, step=0.01)

        adj = base * grouping * ambient
        st.success(f"Adjusted ampacity: **{fmt(adj, 'A')}**")
        st.caption("Replace factors/inputs with NEC/OESC tables and tray-specific rules.")

# ============================
# 9) Demand Load
# ============================
elif page == "Demand Load":
    with theory_tab:
        header("Demand Load", "Apply demand factors to connected load (template).")
        show_code_note(code_mode)

        st.markdown(
            r"""
### Template concepts
- Connected load vs calculated (demand) load
- Demand factor depends on occupancy type and load category

### Example (simplified)
Connected load = 120 kW  
Demand factor = 0.65  
\[
P_{demand} = 120 \cdot 0.65 = 78\text{ kW}
\]
"""
        )

    with calc_tab:
        header("Demand Load Calculator", "Compute demand load from connected load and factor.")
        show_code_note(code_mode)

        connected = st.number_input("Connected load (kW)", min_value=0.0, value=120.0, step=1.0)
        factor = st.number_input("Demand factor (0–1)", min_value=0.0, max_value=1.0, value=0.65, step=0.01)

        demand = connected * factor
        st.success(f"Demand load: **{fmt(demand, 'kW')}**")
        st.caption("For a real implementation, add category-based factors and NEC/OESC references.")

# ============================
# 10) Voltage Drop
# ============================
elif page == "Voltage Drop":
    with theory_tab:
        header("Voltage Drop", "Basic voltage drop estimation (template).")
        show_code_note(code_mode)

        st.markdown(
            r"""
### Template concepts
- Voltage drop depends on conductor resistance, length, current, and system type
- Quick resistive estimates:
  - Single-phase: \(V_d \approx 2 \cdot I \cdot R \cdot L\)
  - Three-phase: \(V_d \approx \sqrt{3} \cdot I \cdot R \cdot L\)

### Example (simplified 3Φ)
- \(I = 50\text{ A}\)
- \(R = 0.0004\ \Omega/\text{m}\)
- \(L = 80\text{ m}\)

\[
V_d \approx 1.732 \cdot 50 \cdot 0.0004 \cdot 80 \approx 2.77\text{ V}
\]
"""
        )

    with calc_tab:
        header("Voltage Drop Calculator", "Estimate V-drop (resistive model) for 1Φ or 3Φ.")
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
        else:
            Vd = math.sqrt(3) * I * R_per_m * L

        pct = (Vd / V_nom) * 100.0 if V_nom > 0 else 0.0

        c1, c2 = st.columns(2)
        c1.metric("Estimated voltage drop", fmt(Vd, "V"))
        c2.metric("Voltage drop (%)", fmt(pct, "%"))

        st.caption("This is a resistive-only estimate. For better accuracy, add reactance, PF, and conductor data tables.")
