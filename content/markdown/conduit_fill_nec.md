## Overview

Cables installed in conduit are protected from physical and environmental damage. Under the NEC, conductors must be derated according to the quantity installed in a single raceway (NEC Table 310.15(C)(1)). Conductor cross-sectional areas are determined from Chapter 9, Table 5, and compared to internal conduit fill areas from Chapter 9, Table 4. Sizing and fill rules are governed by **NEC Chapter 9, Table 1**.

---

## Conductors in Conduit

Conduit fill limits are based on the number of conductors to ensure proper heat dissipation and prevent physical damage during wire pulls.

**NEC Chapter 9, Table 1 limits:**

- **1 conductor**: Maximum **53%** fill
- **2 conductors**: Maximum **31%** fill
- **3 or more conductors**: Maximum **40%** fill

**Nipple Exception (Chapter 9, Note 4):**
- Where conduit nipples do not exceed 24 inches (600 mm) in length, they are permitted to be filled up to **60%** of their cross-sectional area, and ampacity adjustment factors of Table 310.15(C)(1) do not apply.

**Voltage Segregation:**
- Under NEC 300.5(C)(1), conductors of different systems (such as 120V and 480V) can occupy the same conduit, provided all conductors are insulated for the maximum system voltage of any conductor in the enclosure. However, low-voltage instrumentation/control signals should be isolated from power runs to prevent electromagnetic interference.

---

## General Method

Once conductors have been sized, they are routed through conduit runs based on voltage level and conductor size. Below are two examples.

### Example A — Separating by Voltage Level

Consider two separate runs through 2" trade size RMC conduit (100% internal area = 3.408 in² / 2199 mm²).

| Parameter | Run 1 | Run 2 |
|-----------|-------|-------|
| Voltage   | 24VDC | 600V |
| Insulation Type | THHN | THHN |
| Conductors | 98 × #14 AWG (1/C) | 1 × #2/0 AWG (6/C Cable) |

Run 1 contains control signals (40% fill limit applies). Run 2 contains a single multi-conductor power cable (treated as 1 conductor, 53% fill limit applies).

- Conductor areas from Table 5:
  - #14 AWG THHN = 0.0097 in² (6.26 mm²)
  - #2/0 AWG 6/C Cable (nominal) = 1.8058 in² (1165.0 mm²)

| Parameter | Conduit 1 (Run 1) | Conduit 2 (Run 2) |
|-----------|-------------------|-------------------|
| Conductor Area | 0.0097 in² | 1.8058 in² |
| Total Area Used | 98 × 0.0097 = 0.9506 in² | 1.8058 in² |
| Conduit 100% Area | 3.408 in² (2199 mm²) | 3.408 in² (2199 mm²) |
| Allowable Fill Limit | 40% (1.363 in²) | 53% (1.806 in²) |
| **Conduit Fill %** | **27.89%** $\leq$ 40% $\quad \checkmark$ | **52.99%** $\leq$ 53% $\quad \checkmark$ |

Both conduit runs comply with Chapter 9, Table 1.

---

### Example B — Separating by Gauge

Consider running 225 conductors through 3" trade size RMC conduits (100% Area = 7.500 in² / 4839 mm²).
- Group 1: 75 × #14 AWG THHN (1/C) $\Rightarrow$ Area per wire = 0.0097 in²
- Group 2: 150 × #10 AWG THHN (1/C) $\Rightarrow$ Area per wire = 0.0211 in²

To simplify routing, we attempt to run them in two conduits. However, the #10 AWG run yields:

$$ \text{Total Area} = 150 \times 0.0211 \text{ in}^2 = 3.165 \text{ in}^2 $$

At 40% fill, a 3" RMC can only carry 3.000 in². Thus, the #10 AWG run will overfill a single 3" conduit. We can resolve this by redistributing some of the #10 AWG conductors into Conduit 1 with the #14 AWG conductors.

**Revised Redistribution across two 3" RMC conduits:**

- **Conduit 1**: 75 × #14 AWG THHN + 27 × #10 AWG THHN:
  - Total Conductor Area = $(75 × 0.0097) + (27 × 0.0211) = 0.7275 + 0.5697 = 1.2972 \text{ in}^2$
  - Fill% = $(1.2972 / 7.500) \times 100\% = 17.30\% \leq 40\% \quad \checkmark$

- **Conduit 2**: 123 × #10 AWG THHN:
  - Total Conductor Area = $123 × 0.0211 = 2.5953 \text{ in}^2$
  - Fill% = $(2.5953 / 7.500) \times 100\% = 34.60\% \leq 40\% \quad \checkmark$

---

## Bend Radii

To prevent physical stress on the conductor insulation during installation, the conduit bend radius must comply with NEC Chapter 9, Table 2 (or standard bending requirements defined in specific raceway Articles, such as NEC 344.24 for RMC and NEC 358.24 for EMT).

---

## Appendix

<!-- ### Related Knowledge Files

[Knowledge File: Maximum Allowable Conductors/Cables in Conduit and Tubing] -->

### Related NEC Articles

Section 300.5 — Conductors of Different Systems<br/>
Section 310.15 — Ampacity Correction and Adjustment Factors

### Related NEC Tables

Chapter 9, Table 1 — Percent of Cross Section of Conduit and Tubing for Conductors<br/>
Chapter 9, Table 2 — Radius of Conduit Bends<br/>
Chapter 9, Table 4 — Dimensions and Percent Area of Conduit and Tubing<br/>
Chapter 9, Table 5 — Dimensions of Insulated Conductors and Fixture Wires