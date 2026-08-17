## Overview

Voltage drop must be accounted for in circuit design, especially for long conductor runs. Under the National Electrical Code (NEC) 2026, voltage drop parameters are defined by advisory guidelines rather than rigid branch-circuit rules. 

Specifically, the **Informational Notes to NEC 210.19(A)** (branch circuits) and **NEC 215.2(A)(1)** (feeders) recommend limiting voltage drop to:

- A maximum of **3%** on the branch circuit or the feeder individually.
- A maximum of **5%** combined total from the service point to the final outlet.

These are Informational Notes, which under NEC 90.5(C) are explanatory and **not enforceable as Code requirements**. They are routinely written into project specifications as hard limits, so in practice they are usually treated as such.

To accommodate this, conductors must be upsized when necessary to lower overall circuit impedance.

---

## Finding Voltage Drop

Voltage drop is typically expressed as a percentage of nominal system voltage:

$$
\Delta V \% = \frac{V_D}{V_{nom}} \cdot 100
$$

The single-phase and three-phase voltage drop values can be calculated using either the **Circular Mil (CM) Method** or the **Effective Impedance Method**.

### Method A — Circular Mil (CM) Method

#### Formulas:

$$\text{Single-phase:} \quad V_D = \frac{2 \cdot K \cdot I \cdot L}{CM}$$

$$\text{Three-phase:} \quad V_D = \frac{\sqrt{3} \cdot K \cdot I \cdot L}{CM}$$

**Where**

- **$K$** = Direct current resistance factor of a circular mil-foot conductor: approximately 12.9 Ω-cmil/ft for Copper and 21.2 Ω-cmil/ft for Aluminum at 75°C. These constants are not tabulated in the NEC. They are derived from Chapter 9, Table 8 as $K = R \times CM / 1000$.
- **$I$** = Load current, A.
- **$L$** = One‑way length of the circuit, ft.
- **$CM$** = Cross-sectional area of the conductor in circular mils (from Chapter 9, Table 8).

---

### Method B — Effective Impedance Method (NEC Chapter 9, Table 9)

For larger AC circuits, resistance and inductive reactance combined determine the voltage drop.

#### Formula:

$$ V_D = \frac{2 \cdot I \cdot L \cdot Z_{\text{eff}}}{1000} \quad \text{(Single-Phase)} $$

$$ V_D = \frac{\sqrt{3} \cdot I \cdot L \cdot Z_{\text{eff}}}{1000} \quad \text{(Three-Phase)} $$

**Where**

- **$Z_{\text{eff}}$** = Effective impedance (Ω per 1000 ft) from Chapter 9, Table 9, based on conductor material, conduit type, and power factor.
- **$L$** = One-way length of the circuit, ft.
- **$I$** = Load current, A.

---

## Finding Conductor Size or Maximum Length

If determining the required conductor size (in Circular Mils) or the maximum allowable length for a target voltage drop, the formulas can be rearranged:

### Conductor Sizing (CM)

$$
CM \geq \frac{2 \cdot K \cdot I \cdot L}{V_D} \quad \text{(Single-Phase)}
$$

$$
CM \geq \frac{\sqrt{3} \cdot K \cdot I \cdot L}{V_D} \quad \text{(Three-Phase)}
$$

### Maximum Length (CM)

$$
L \leq \frac{V_D \cdot CM}{2 \cdot K \cdot I} \quad \text{(Single-Phase)}
$$

$$
L \leq \frac{V_D \cdot CM}{\sqrt{3} \cdot K \cdot I} \quad \text{(Three-Phase)}
$$

---

## Appendix

<!-- ### Related Knowledge Files

[Knowledge File — NEC: Article 310 Conductors for General Wiring]<br/>
[Design Basis – Calculations: Voltage Drop and Conductor Impedance] -->

### Related NEC Articles

Section 90.5(C) — Explanatory Material (status of Informational Notes)<br/>
Section 210.19(A) — Branch Circuit Voltage Drop Informational Note<br/>
Section 215.2(A)(1) — Feeder Voltage Drop Informational Note

### Related NEC Tables

Chapter 9, Table 8 — Conductor Properties<br/>
Chapter 9, Table 9 — AC Resistance and Reactance for 600-Volt Cables
