## Overview

Sizing motor feeders and branch-circuit conductors is crucial for any industrial application. This section covers key considerations and a practical sizing workflow under the National Electrical Code (NEC) 2026.

<div align="center">

![Figure 1: Example Motor Branch Circuit](../images/SingleMotorFeeder.png)

</div>

The first step when working with any motor is to gather nameplate and design criteria.

<div align="center">

![Figure 2: Motor Nameplate Example](../images/TestPicture.jpg)

</div>

---

## Feeder Sizing

Under NEC 430.6(A)(1), conductor sizing and overcurrent protection calculations must be based on the Full-Load Current (FLC) values listed in the NEC tables (Table 430.247 for DC, Table 430.248 for 1φ AC, and Table 430.250 for 3φ AC), rather than the actual motor nameplate current rating. The motor nameplate FLA is used primarily for sizing motor overload protection (NEC 430.6(A)(2)).

To calculate the theoretical FLC for a 3φ motor for design checking:

$$
I_{\text{FLC}} = \frac{\text{HP} \cdot 745.7}{\sqrt3 \cdot V_{\text{LL}} \cdot \cos\theta \cdot  \eta}
$$

For actual installation compliance, the NEC standard Table FLC values must be used.

For a single motor branch circuit, NEC 430.22 requires that the conductors have an ampacity of not less than 125% of the motor FLC:

$$
I_{\text{conductor}} = 1.25 \cdot I_{\text{FLC}}
$$

For multiple motors on a single feeder, NEC 430.24 requires that feeder conductors have an ampacity of not less than 125% of the highest-rated motor FLC in the group, plus the sum of the FLC ratings of all other motors on the feeder.

---

## Conductor Temperature Ratings

Motors are often installed in hot or confined spaces, which requires ampacity adjustment. Under NEC 110.14(C)(1), conductor selection must respect termination temperature limits:
- Equipment rated 100 A or less, or marked for #14 AWG through #1 AWG, must use the **60°C column** of Table 310.16 unless the terminals are specifically listed and marked for 75°C.
- Equipment rated over 100 A, or marked for conductors larger than #1 AWG, uses the **75°C column** of Table 310.16.
- Class F and H motor windings can withstand high operating temperatures, but the connected supply conductors are still limited by terminal ratings (typically 75°C).

---

## Voltage Drop

NEC 210.19(A) Informational Note recommends sizing branch circuit conductors to limit voltage drop to not more than 3%, and a maximum of 5% total voltage drop for both the feeder and branch circuit combined, to ensure efficient equipment operation.

---

## Duty Cycle and Service Ratings

Not all motors are rated for continuous duty. Under NEC Table 430.22(E), conductors for non-continuous or short-time duty motors must be sized based on the percentages of the nameplate current rating specified for the specific motor operating duration and classification.

---

## Multiple Motors Sizing Example

Sizing conductors for multiple motors on a single feeder is common. Apply the NEC 430.24 methodology to determine feeder conductor size.

Assume the following three motors are fed from a single 460V, 3-phase feeder:

| Motor No. | Service Duty | FLC (from NEC Table 430.250) |
|-----------|--------------|------------------------------|
| $M_1$     | Continuous   | 9 A                          |
| $M_2$     | Continuous   | 12 A                         |
| $M_3$     | Intermittent (15-min rating) | 5 A                          |

Under NEC 430.24 and Table 430.22(E), we apply the continuous 125% multiplier to the highest-rated continuous motor ($M_2$), and we look up the intermittent duty factor for a 15-minute rated motor (which is typically 120% per Table 430.22(E)).

| Motor No. | Adjusted FLC Calculation | Minimum Ampacity Target |
|-----------|--------------------------|-------------------------|
| $M_1$     | Continuous load (at 100%)| 9.0 A                   |
| $M_2$     | Largest Continuous (125%)| 12 A × 1.25 = 15.0 A    |
| $M_3$     | Intermittent load (120%) | 5 A × 1.20 = 6.0 A      |
| **Feeder Total**| **9.0 A + 15.0 A + 6.0 A** | **30.0 A**            |

### Feeder Conductor Selection:
Checking NEC Table 310.16 (under 60°C termination limits per NEC 110.14(C)(1) since target load is ≤100A), we select **#10 AWG Copper** (rated for 30 A).

---

## Appendix

### Related Knowledge Files
<!-- 
[Design Basis — Calculations: Motor Feeder Sizing]<br/>
[Knowledge File — NEC: Article 430 Motors, Motor Circuits, and Controllers] -->

### Related NEC Articles

Section 110.14(C) — Temperature Limitations of Terminals<br/>
Section 210.19(A) — Voltage Drop Informational Note<br/>
Section 430.6 — Ampacity and Motor Rating Determination<br/>
Section 430.22 — Single Motor Conductor Sizing<br/>
Section 430.24 — Several Motors Conductor Sizing<br/>
Section 430.25 — Conductor Sizing for Feeder and Motor Loads

### Related NEC Tables

Table 310.16 — Ampacities of Insulated Conductors in Raceway or Cable<br/>
Table 430.22(E) — Duty Cycle Conductor Percentages<br/>
Table 430.247 — DC Motor Full-Load Current<br/>
Table 430.248 — 1-Phase AC Motor FLC<br/>
Table 430.250 — 3-Phase AC Motor FLC