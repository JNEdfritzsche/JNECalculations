## Overview

This section walks through worked examples for voltage drop calculations using the methods defined under the National Electrical Code (NEC) 2026. This includes calculations using direct conductor properties from Chapter 9, Table 8 and AC impedance values from Chapter 9, Table 9.

---

## Example 1 — 1φ AC Cable, Temperature-Adjusted Resistance

**240 V, 1φ | 50 A | Cable | 200 ft | 60 °C Operating Temperature | 90% PF | #1 AWG – 2/C | Copper**

Because the operating temperature is 60°C, the base 75°C DC resistance from Chapter 9, Table 8 must be adjusted downward using the formula:

$$ R_T = R_{75} \times [1 + \alpha (T - 75)] $$

For copper, $\alpha = 0.00323$.

| Symbol | Description | Value |
|--------|-------------|-------|
| $R_{75}$ | Chapter 9, Table 8, #1 AWG Copper Resistance | 0.154 Ω / 1000 ft |
| $R_{60}$ | Temperature Adjusted Resistance (60°C) | 0.1465 Ω / 1000 ft |
| $X_L$ | Chapter 9, Table 9, Reactance in PVC Conduit | 0.046 Ω / 1000 ft |
| $Z_{\text{eff}}$ | Effective Impedance ($R \cos\theta + X \sin\theta$) | 0.1519 Ω / 1000 ft |
| $I$ | Load Current | 50 A |
| $L$ | One-way length | 200 ft |
| $V_{\text{nom}}$ | Nominal Voltage | 240 V |

**Adjusted Resistance calculation:**

$$ R_{60} = 0.154 \times [1 + 0.00323 \times (60 - 75)] = 0.1465 \ \Omega\text{ / 1000 ft} $$

**Effective Impedance calculation ($\cos\theta = 0.9$, $\sin\theta \approx 0.436$):**

$$ Z_{\text{eff}} = (0.1465 \times 0.9) + (0.046 \times 0.436) = 0.1319 + 0.0201 = 0.1519 \ \Omega\text{ / 1000 ft} $$

**Voltage Drop calculation:**

$$ V_D = \frac{2 \cdot I \cdot L \cdot Z_{\text{eff}}}{1000} = \frac{2 \times 50 \times 200 \times 0.1519}{1000} = 3.04 \text{ V} $$

$$ \%\Delta V = \frac{3.04 \text{ V}}{240 \text{ V}} \times 100\% = 1.27\% \leq 3\% \quad \checkmark \text{ PASS} $$

**Result: V_D = 3.04 V &nbsp;|&nbsp; %ΔV = 1.27%**

---

## Example 2 — 3φ AC Raceway, Table 9 Values

**600 V, 3φ | 100 A | Steel Conduit | 400 ft | 75 °C Operating | 80% PF | #3 AWG – 1/C | Copper**

Operating at 75°C, which matches the base temperature rating of Chapter 9, Table 9. No temperature adjustment is required.

| Symbol | Description | Value |
|--------|-------------|-------|
| $R$ | Table 9, #3 AWG Copper Resistance (Steel Conduit) | 0.25 Ω / 1000 ft |
| $X_L$ | Table 9, #3 AWG Reactance (Steel Conduit) | 0.059 Ω / 1000 ft |
| $Z_{\text{eff}}$ | Effective Impedance ($R \cos\theta + X \sin\theta$) | 0.2354 Ω / 1000 ft |
| $I$ | Load Current | 100 A |
| $L$ | One-way length | 400 ft |
| $V_{\text{nom}}$ | Nominal Voltage | 600 V |

**Effective Impedance calculation ($\cos\theta = 0.8$, $\sin\theta = 0.6$):**

$$ Z_{\text{eff}} = (0.25 \times 0.8) + (0.059 \times 0.6) = 0.200 + 0.0354 = 0.2354 \ \Omega\text{ / 1000 ft} $$

**Voltage Drop calculation:**

$$ V_D = \frac{\sqrt{3} \cdot I \cdot L \cdot Z_{\text{eff}}}{1000} = \frac{1.732 \times 100 \times 400 \times 0.2354}{1000} = 16.31 \text{ V} $$

$$ \%\Delta V = \frac{16.31 \text{ V}}{600 \text{ V}} \times 100\% = 2.72\% \leq 3\% \quad \checkmark \text{ PASS} $$

**Result: V_D = 16.31 V &nbsp;|&nbsp; %ΔV = 2.72%**

---

## Example 3 — DC Circuit, Temperature-Adjusted Resistance, Aluminum

**125 V, DC | 80 A | 80 ft | 90 °C Operating Temperature | #3 AWG – 2/C | Aluminum**

DC circuits use direct DC resistance from Chapter 9, Table 8. For aluminum, the temperature coefficient is $\alpha = 0.00330$ (at 75°C).

| Symbol | Description | Value |
|--------|-------------|-------|
| $R_{75}$ | Chapter 9, Table 8, #3 AWG Aluminum DC Resistance | 0.403 Ω / 1000 ft |
| $R_{90}$ | Adjusted Resistance (90°C) | 0.4230 Ω / 1000 ft |
| $I$ | Load Current | 80 A |
| $L$ | One-way length | 80 ft |
| $V_{\text{nom}}$ | Nominal Voltage | 125 V |

**Adjusted Resistance calculation:**

$$ R_{90} = 0.403 \times [1 + 0.00330 \times (90 - 75)] = 0.4230 \ \Omega\text{ / 1000 ft} $$

**Voltage Drop calculation:**

$$ V_D = \frac{2 \cdot I \cdot L \cdot R_{90}}{1000} = \frac{2 \times 80 \times 80 \times 0.4230}{1000} = 5.41 \text{ V} $$

$$ \%\Delta V = \frac{5.41 \text{ V}}{125 \text{ V}} \times 100\% = 4.33\% \leq 5\% \quad \checkmark \text{ PASS (combined feeder/branch)} $$

**Result: V_D = 5.41 V &nbsp;|&nbsp; %ΔV = 4.33%**

---

## Appendix

<!-- ### Related Knowledge Files

[Knowledge File — NEC: Article 310 Conductors for General Wiring]<br/>
[Design Basis – Calculations: Voltage Drop and Conductor Impedance] -->

### Related NEC Articles

Section 210.19(A) — Branch Circuit Voltage Drop Informational Note<br/>
Section 215.2(A)(1) — Feeder Voltage Drop Informational Note

### Related NEC Tables

Chapter 9, Table 8 — Conductor Properties (DC resistance)<br/>
Chapter 9, Table 9 — AC Resistance and Reactance for 600-Volt Cables