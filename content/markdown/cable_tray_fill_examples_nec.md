## Overview

Sizing cable trays under the NEC requires evaluating the type of cables, quantities, and cross-sectional dimensions. Cable tray fill evaluation is based on **NEC 392.22** to ensure proper heat dissipation and mechanical safety.

The general fill calculation is:

$$ \text{Tray Fill (\%)} = \frac{\text{Total Cable Area}}{\text{Usable Tray Area}} \times 100 $$

---

## Example 1 — Single-conductor Power Runs (Ladder Tray)

We are running single-conductor 600V power cables in a horizontal layer in a ladder-type cable tray. We must evaluate compliance under **NEC 392.22(B)**.

| Voltage | Quantity | Gauge   | Conductors | Outside Diameter (OD) |
| ------- | -------- | ------- | ---------- | --------------------- |
| 600 V   | 9        | 1/0 AWG | 1/C THHN   | 0.521 in (13.23 mm)   |

Under **NEC 392.22(B)(1)(c)**, where single-conductor cables are installed in a ladder tray, and all cables are smaller than 1/0 AWG, the sum of the cable diameters must not exceed the cable tray width. (For #1/0 AWG and larger single-conductor cables, they are typically installed in a single layer, and spacing must be maintained to prevent derating per 392.80).

Let's evaluate the required physical width using a single-layer spaced configuration:

$$ \text{Total Width Space} = (\text{Sum of Cable Diameters}) + (\text{Sum of Cable Spacings}) $$

Assuming we maintain a space of one cable diameter ($0.521\text{ in}$) between each cable to maintain free air ampacity rating (per NEC 392.80(B)(2)(b)):

$$ \text{Width Required} = (9 \times 0.521 \text{ in}) + (8 \times 0.521 \text{ in}) = 8.857 \text{ in} \quad (225.0 \text{ mm}) $$

**A 9" wide cable tray is selected.**

The total conductor area calculation:

$$ A_{\text{conductor}} = \pi \times \left(\frac{0.521}{2}\right)^2 \approx 0.213 \text{ in}^2 \quad (137.4 \text{ mm}^2) $$

$$\text{Total Cable Area} = 9 \times 0.213 = 1.917 \text{ in}^2$$

Usable area of a 4" deep, 9" wide ladder tray (assuming nominal inside depth of 3 inches):

$$ A_{\text{usable}} = 3.0 \text{ in} \times 9.0 \text{ in} = 27.0 \text{ in}^2 $$

$$ \text{Tray Fill \%} = \frac{1.917}{27.0} \times 100\% = 7.10\% $$

**Result: Selected 9" wide ladder tray at 7.1% fill.**

---

## Example 2 — Sectioned Runs (Multi-conductor Power and Control)

We are running multi-conductor power and control cables in a 4" × 12" ladder-type cable tray divided into two equal sections using a barrier strip (NEC 392.20(D)).

- **Section 1**: 9 × #2 AWG 3/C power cables (600 V) $\Rightarrow$ Nominal OD = 1.042 in (26.46 mm)
- **Section 2**: 9 × #14 AWG 12/C control cables (24 VDC) $\Rightarrow$ Nominal OD = 1.216 in (30.88 mm)

Each section width is approximately **6 inches** (usable area = 3.0" × 6.0" = 18.0 in²).

**Section 1 Fill (Multi-conductor power cables):**

- Area of one 3/C cable = $\pi \times (1.042 / 2)^2 = 0.8527 \text{ in}^2$
- Total Area (Section 1) = $9 \times 0.8527 = 7.674 \text{ in}^2$
- Usable tray area = $18.0 \text{ in}^2$
- Fill% = $(7.674 / 18.0) \times 100\% = 42.63\%$

Under NEC Table 392.22(A) Column 1, the maximum allowable fill area for multi-conductor cables in a 6" wide tray is **7.0 in²**. Since our calculated area is **7.674 in²**, Section 1 is overfilled. We must adjust the barrier strip to provide **9 inches** for Section 1 (allowable limit = 10.5 in²) and **3 inches** for Section 2.

**Revised Layout (9" Power Section, 3" Control Section):**

- **Section 1 (9" Power Section, Usable Area = 27.0 in²):**
  
  - Allowable fill area per Table 392.22(A) = **10.5 in²**
  - Actual Area = **7.674 in²**
  - Fill% = $(7.674 / 27.0) \times 100\% = 28.42\% \leq 10.5 \text{ in}^2 \text{ limit} \quad \checkmark \text{ PASS}$

- **Section 2 (3" Control Section, Usable Area = 9.0 in²):**
  
  - Area of one 12/C control cable = $\pi \times (1.216 / 2)^2 = 1.161 \text{ in}^2$
  - Total Area (Section 2) = $9 \times 1.161 = 10.45 \text{ in}^2$ (Control cables smaller than 4/0 AWG must not exceed fill limits. A 3" section has an allowable limit of 3.5 in² per Table 392.22(A)).
  - Since Section 2 is overfilled, we must use a larger overall cable tray (such as a 4" × 18" tray) to accommodate both sections safely.

---

## Appendix

<!-- ### Related Knowledge Files

[Knowledge File: Industrial Cable Tray Design Principles]<br/>
[Knowledge File: Cable Tray Fill Sizing and Area Calculations] -->

### Related NEC Articles

Section 392.20 — Cable and Conductor Installation in Trays<br/>
Section 392.22 — Number of Cables or Conductors in Cable Trays<br/>
Section 392.80 — Ampacity of Conductors in Cable Trays

### Related NEC Tables

Table 392.22(A) — Allowable Fill Area for Multi-conductor Cables in Ladder/Ventilated Trays<br/>
Table 392.22(B)(1) — Allowable Fill Area for Single-conductor Cables in Ladder/Ventilated Trays 


