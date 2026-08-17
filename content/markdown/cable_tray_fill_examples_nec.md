## Overview

Sizing cable trays under the NEC requires evaluating the type of cables, quantities, and cross-sectional dimensions. Cable tray fill evaluation is based on **NEC 392.22** to ensure proper heat dissipation and mechanical safety.

Depending on the cable sizes present, 392.22 applies one of two tests:

$$ \text{Area test:} \quad \sum A_{\text{cable}} \leq A_{\text{allowable}} \text{ from Table 392.22(A)(1) or 392.22(B)(1)} $$

$$ \text{Width test:} \quad \sum \text{OD}_{\text{cable}} \leq \text{inside width of tray} $$
<br/><br/>

Where the area test applies, utilization is expressed against the *allowable fill area*:

$$ \text{Utilization} = \frac{\sum A_{\text{cable}}}{A_{\text{allowable}}} \times 100\% $$

---

## Example 1 — Single-conductor Power Runs (Ladder Tray)

We are running single-conductor 600V power cables in a horizontal layer in a ladder-type cable tray. We must evaluate compliance under **NEC 392.22(B)**.

| Voltage | Quantity | Gauge   | Conductors | Outside Diameter (OD) |
| ------- | -------- | ------- | ---------- | --------------------- |
| 600 V   | 9        | 1/0 AWG | 1/C THHN   | 0.521 in (13.23 mm)   |

These are 1/0 AWG single conductors, so the governing rule is **NEC 392.22(B)(1)(d)**: where any of the cables installed are 1/0 AWG through 4/0 AWG, the sum of the diameters must not exceed the cable tray width.

$$ \sum \text{OD} = 9 \times 0.521 \text{ in} = 4.689 \text{ in} \quad (119.1 \text{ mm}) $$

$$ 4.689 \text{ in} \leq 6.0 \text{ in} \quad \checkmark $$

**The code minimum is a 6" wide ladder tray.**

### Spacing for Free-Air Ampacity

To rate the conductors on free-air ampacity, **NEC 392.80(A)(2)** requires a single layer with a maintained spacing of not less than one cable diameter:

$$ \text{Width Required} = (9 \times 0.521) + (8 \times 0.521) = 17 \times 0.521 = 8.857 \text{ in} \quad (225.0 \text{ mm}) $$

**Result: a 6" ladder tray meets 392.22(B)(1)(d), and a 9" tray is selected to hold one-diameter spacing per 392.80(A)(2).**

---

## Example 2 — Sectioned Runs (Multi-conductor Power and Control)

We are running multi-conductor power and control cables in a 12" wide ladder-type cable tray divided into two equal sections using a solid fixed barrier.

- **Section 1**: 9 × #2 AWG 3/C power cables (600 V) $\Rightarrow$ Nominal OD = 1.042 in (26.46 mm)
- **Section 2**: 9 × #14 AWG 12/C control cables (24 VDC) $\Rightarrow$ Nominal OD = 1.216 in (30.88 mm)

All cables are smaller than 4/0 AWG, so **392.22(A)(1)(b)** applies to both sections: the sum of the cross-sectional areas must not exceed **Column 1** of Table 392.22(A)(1) for the applicable width.

Each section is evaluated as a tray of its own inside width.

**Cable areas:**

$$ A_{\text{power}} = \pi \times (1.042 / 2)^2 = 0.8528 \text{ in}^2 \quad \Rightarrow \quad 9 \times 0.8528 = 7.675 \text{ in}^2 $$

$$ A_{\text{control}} = \pi \times (1.216 / 2)^2 = 1.1613 \text{ in}^2 \quad \Rightarrow \quad 9 \times 1.1613 = 10.452 \text{ in}^2 $$

**First attempt — 12" tray, two 6" sections (Column 1 allowable = 7.0 in² each):**

| Section | Cable area | Allowable (6") | Utilization | Result |
|---|---|---|---|---|
| 1 — Power | 7.675 in² | 7.0 in² | 109.6% | ✗ FAIL |
| 2 — Control | 10.452 in² | 7.0 in² | 149.3% | ✗ FAIL |

Both sections are overfilled. An 18" tray (8" power, 9" control) would comply, but the control section lands at 99.5% of its 10.5 in² allowable.

**Selected — 24" tray, two 12" sections (Column 1 allowable = 14.0 in² each):**

| Section | Cable area | Allowable (12") | Utilization | Result |
|---|---|---|---|---|
| 1 — Power | 7.675 in² | 14.0 in² | 54.8% | ✓ PASS |
| 2 — Control | 10.452 in² | 14.0 in² | 74.7% | ✓ PASS |

**Result: 24" ladder tray with a centre barrier, power section at 54.8% and control section at 74.7% of their allowable fill areas.**

Table 392.22(A)(1) is tabulated at discrete widths (2, 4, 6, 8, 9, 12, 16, 18, 20, 24, 30 and 36 in.) and is not interpolated.

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

Table 392.22(A)(1) — Allowable Cable Fill Area for Multiconductor Cables in Ladder, Ventilated Trough, or Solid Bottom Cable Trays<br/>
Table 392.22(B)(1) — Allowable Cable Fill Area for Single-Conductor Cables in Ladder, Ventilated Trough, or Wire Mesh Cable Trays


