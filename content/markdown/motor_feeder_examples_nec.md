## Overview

This section walks through worked examples for calculating motor Full-Load Amps (FLA) and conductor sizing targets under the National Electrical Code (NEC) 2026. 

Under **NEC 430.6(A)(1)**, conductor and OCPD sizing must be based on standard FLC values listed in the NEC tables (Table 430.247 for DC, Table 430.248 for 1φ AC, and Table 430.250 for 3φ AC), rather than actual nameplate FLA.

The formulas used to evaluate theoretical performance are:

$$\text{Single-phase AC:} \quad I_{\text{FLA}} = \frac{HP \times 745.7}{V \cdot \cos\theta \cdot \eta}$$

$$\text{Three-phase AC:} \quad I_{\text{FLA}} = \frac{HP \times 745.7}{\sqrt{3} \cdot V \cdot \cos\theta \cdot \eta}$$

$$\text{DC:} \quad I_{\text{FLA}} = \frac{HP \times 745.7}{V \cdot \eta}$$

For continuous duty motor branch circuits, NEC 430.22 requires sizing conductors to carry a **125% continuous rating factor**:

$$I_{\text{target}} = 1.25 \times I_{\text{FLC}}$$

---

## Example 1 — Single-Phase AC Motor

**230 V | 1φ | 10 HP | Continuous Duty**

| Parameter | Value |
|-----------|-------|
| Motor Power | 10 HP |
| Voltage $V$ | 230 V |
| FLC (NEC Table 430.248) | **50 A** |

Under NEC 430.22, we apply the 125% continuous duty factor to the table FLC:

$$I_{\text{target}} = 1.25 \times 50 \text{ A} = 62.5 \text{ A}$$

Conductor Sizing (NEC Table 310.16):
- Sized using the 75°C column per terminal temperature limits (NEC 110.14(C)(1)(a)(2) permits 75°C terminations if listed):
- **Select #6 AWG Copper Conductor** (rated at 65 A under the 75°C column).

**Result: Table I_FLC = 50 A &nbsp;|&nbsp; Conductor Sizing Target = 62.5 A**

---

## Example 2 — Three-Phase AC Motor

**460 V | 3φ | 40 HP | Continuous Duty**

| Parameter | Value |
|-----------|-------|
| Motor Power | 40 HP |
| Voltage $V$ | 460 V |
| FLC (NEC Table 430.250) | **52 A** |

Under NEC 430.22, we apply the 125% continuous duty factor:

$$I_{\text{target}} = 1.25 \times 52 \text{ A} = 65 \text{ A}$$

Conductor Sizing (NEC Table 310.16):
- Sized using 75°C terminations:
- **Select #6 AWG Copper Conductor** (rated at 65 A under the 75°C column).

**Result: Table I_FLC = 52 A &nbsp;|&nbsp; Conductor Sizing Target = 65 A**

---

## Example 3 — DC Motor

**240 V | DC | 5 HP | Continuous Duty**

| Parameter | Value |
|-----------|-------|
| Motor Power | 5 HP |
| Voltage $V$ | 240 V |
| FLC (NEC Table 430.247) | **20 A** |

Under NEC 430.22, we apply the 125% continuous duty factor:

$$I_{\text{target}} = 1.25 \times 20 \text{ A} = 25 \text{ A}$$

Conductor Sizing (NEC Table 310.16):
- Sized using 60°C terminals per NEC 110.14(C)(1) as load is ≤ 100A:
- **Select #10 AWG Copper Conductor** (rated at 30 A under the 60°C column).

**Result: Table I_FLC = 20 A &nbsp;|&nbsp; Conductor Sizing Target = 25 A**

---

## Appendix
<!-- 
### Related Knowledge Files

[Design Basis — Calculations: Motor Feeder Sizing]<br/>
[Knowledge File — NEC: Article 430 Motors, Motor Circuits, and Controllers] -->

### Related NEC Articles

Section 110.14(C) — Temperature Limitations of Terminals<br/>
Section 430.6 — Ampacity and Motor Rating Determination<br/>
Section 430.22 — Single Motor Conductor Sizing

### Related NEC Tables

Table 310.16 — Ampacities of Insulated Conductors in Raceway or Cable<br/>
Table 430.247 — DC Motor Full-Load Current<br/>
Table 430.248 — 1-Phase AC Motor FLC<br/>
Table 430.250 — 3-Phase AC Motor FLC