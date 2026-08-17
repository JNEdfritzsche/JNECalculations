## Overview

This section walks through worked examples for conduit fill calculations under the National Electrical Code (NEC) 2026. The goal is to evaluate conductor areas using Chapter 9, Table 5, select the minimum conduit size from Chapter 9, Table 4, and ensure compliance with Chapter 9, Table 1 fill limits.

The core formula is:

$$\text{Fill\%} = \frac{\sum (A_{\text{cable}} \times N_{\text{cond/cable}} \times N_{\text{cables}})}{A_{\text{conduit}}} \times 100\%$$

Where $A_{\text{cable}}$ is the cross-sectional area per conductor (in² or mm²) from Chapter 9, Table 5, and $A_{\text{conduit}}$ is the conduit internal cross-sectional area (in² or mm²) from Chapter 9, Table 4.

**Allowable fill limits (NEC Chapter 9, Table 1):**

| Number of Conductors | Max Fill | Rationale / Reference |
|----------------------|----------|-----------------------|
| 1 conductor          | 53%      | Chapter 9, Table 1    |
| 2 conductors         | 31%      | Chapter 9, Table 1    |
| 3 or more conductors | 40%      | Chapter 9, Table 1    |

---

## Example 1 — Two Valid Conduit Solutions

**600 V | RMC | 3× 250 kcmil – 1/C | Chapter 9, Table 5 | THHN/THWN-2**

This example demonstrates that conduit selection can offer different routing layouts depending on space, cost, and design constraints.

| Parameter | Value |
|-----------|-------|
| Conductor Area (Chapter 9, Table 5, 250 kcmil THHN) | 0.3970 in² (256.13 mm²) per cable |
| Number of conductors | 3 |
| Total conductor area | 3 × 0.3970 in² = **1.191 in²** (768.39 mm²) |

**Option A — One 2" trade size RMC conduit, all 3 conductors**

With 3 conductors, the 40% fill limit applies (Chapter 9, Table 1).

$$A_{\text{conduit, min}} = \frac{1.191 \text{ in}^2}{0.40} = 2.978 \text{ in}^2 \quad \Rightarrow \text{Select 2" RMC} \quad (100\% \text{ Area} = 3.408 \text{ in}^2)$$

$$\text{Fill\%} = \frac{1.191}{3.408} \times 100\% = 34.95\% \leq 40\% \quad \checkmark \text{ PASS}$$

**Option B — Three 1" trade size RMC conduits, one conductor each**

With 1 conductor per conduit, the 53% fill limit applies (Chapter 9, Table 1).

$$A_{\text{conduit, min}} = \frac{0.3970 \text{ in}^2}{0.53} = 0.749 \text{ in}^2 \quad \Rightarrow \text{Select 1" RMC} \quad (100\% \text{ Area} = 0.887 \text{ in}^2)$$

$$\text{Fill\%} = \frac{0.3970}{0.887} \times 100\% = 44.76\% \leq 53\% \quad \checkmark \text{ PASS (per conduit)}$$

**Result: Fill one 2" RMC at 35.0% — or — three 1" RMC conduits at 44.8% each**

---

## Example 2 — Single Cable Type, Two Conduit Runs

**480 V | RMC | Two runs of 3× #1/0 AWG – 1/C | Chapter 9, Table 5 | THHN/THWN-2**

Two separate 3-conductor runs are required. Each run is sized independently. With 3 conductors per conduit, the 40% fill limit applies.

| Parameter | Value |
|-----------|-------|
| Conductor Area (Chapter 9, Table 5, #1/0 AWG THHN) | 0.1855 in² (119.68 mm²) per conductor |
| Number of conductors per conduit | 3 |
| Total conductor area per conduit | 3 × 0.1855 in² = **0.5565 in²** (359.03 mm²) |

Sizing for 40% fill:

$$A_{\text{conduit, min}} = \frac{0.5565 \text{ in}^2}{0.40} = 1.391 \text{ in}^2 \quad \Rightarrow \text{Select 1¼" RMC} \quad (100\% \text{ Area} = 1.526 \text{ in}^2)$$

$$\text{Fill\%} = \frac{0.5565}{1.526} \times 100\% = 36.47\% \leq 40\% \quad \checkmark \text{ PASS}$$

**Result: Fill two 1¼" RMC conduits, one run per conduit, at 36.5% each**

---

## Example 3 — Mixed Cable Types Requiring Split Conduits

**Mixed 24VDC and 480V cables | RMC**

Three cable groups are present. To prevent signal noise, the 24VDC control cables must be kept separate from the 480V power cables. The 480V group contains one multi-conductor power cable and four single-conductor power cables.

| Conductor Group | Table | Area per Conductor/Cable | Qty | Total Area |
|-----------------|-------|--------------------------|-----|------------|
| 24VDC — #14 AWG THHN (1/C) | Table 5 | 0.0097 in² (6.26 mm²) | 80 | 0.7760 in² (500.6 mm²) |
| 480V — #1/0 AWG (3/C Cable) | Mfg Spec| 0.7735 in² (499.0 mm²) | 1 | 0.7735 in² (499.0 mm²) |
| 480V — #1/0 AWG THHN (1/C) | Table 5 | 0.1855 in² (119.68 mm²) | 4 | 0.7420 in² (478.7 mm²) |

**Conduit 1 — 24VDC control cables (80 conductors, 40% limit):**

$$A_{\text{conduit, min}} = \frac{0.7760 \text{ in}^2}{0.40} = 1.940 \text{ in}^2 \quad \Rightarrow \text{Select 1½" RMC} \quad (100\% \text{ Area} = 2.071 \text{ in}^2)$$

$$\text{Fill\%} = \frac{0.7760}{2.071} \times 100\% = 37.47\% \leq 40\% \quad \checkmark \text{ PASS}$$

**Conduit 2 — 480V power cables (5 conductors/cables, 40% limit):**

$$\text{Total Area} = 0.7735 \text{ in}^2 + 0.7420 \text{ in}^2 = 1.5155 \text{ in}^2$$

$$A_{\text{conduit, min}} = \frac{1.5155 \text{ in}^2}{0.40} = 3.789 \text{ in}^2 \quad \Rightarrow \text{Select 2½" RMC} \quad (100\% \text{ Area} = 4.866 \text{ in}^2)$$

$$\text{Fill\%} = \frac{1.5155}{4.866} \times 100\% = 31.14\% \leq 40\% \quad \checkmark \text{ PASS}$$

**Result: Fill one 1½" RMC conduit (24VDC control) at 37.5% and one 2½" RMC conduit (480V power) at 31.1%**

---

## Example 4 — Complex Multi-Conduit, Mixed Voltage Levels

**Mixed 24VDC, 120V, and 600V cables | RMC**

Four cable groups must be distributed. The 600V feeder cable must be isolated from all LV/signal cables. The two 24VDC groups are split into separate conduits to balance the routing layout.

| Conductor Group | Table | Area per Conductor/Cable | Qty | Total Area |
|-----------------|-------|--------------------------|-----|------------|
| 24VDC — #10 AWG THHN (1/C) | Table 5 | 0.0211 in² (13.61 mm²) | 175 | 3.6925 in² (2,382.2 mm²) |
| 24VDC — #14 AWG THHN (1/C) | Table 5 | 0.0097 in² (6.26 mm²) | 64 | 0.6208 in² (400.5 mm²) |
| 120V — #4/0 AWG THHN (4/C) | Mfg Spec| 1.2803 in² (826.0 mm²) | 1 | 1.2803 in² (826.0 mm²) |
| 600V — 500 kcmil (3/C) | Mfg Spec| 2.7125 in² (1,750.0 mm²) | 1 | 2.7125 in² (1,750.0 mm²) |

For a 4" trade size RMC conduit, total internal area is **12.882 in²** (8,316 mm²). Chapter 9, Table 4 publishes the fill columns directly:
- Allowable at 40% (3+ conductors, Chapter 9, Table 1) = **5.153 in²** (3,326 mm²).
- Allowable at 31% (2 conductors, Chapter 9, Table 1) = **3.994 in²** (2,578 mm²).

**Conduit 1 — 24VDC #10 AWG (175 conductors, 40% limit):**

$$\text{Fill\%} = \frac{3.6925 \text{ in}^2}{12.882 \text{ in}^2} \times 100\% = 28.66\% \leq 40\% \quad \checkmark \text{ PASS}$$

**Conduit 2 — 24VDC #14 AWG (64 conductors, 40% limit):**

$$\text{Fill\%} = \frac{0.6208 \text{ in}^2}{12.882 \text{ in}^2} \times 100\% = 4.82\% \leq 40\% \quad \checkmark \text{ PASS}$$

**Conduit 3 — 120V + 600V power (2 cables → 31% limit applies, Chapter 9, Table 1):**

$$\text{Total Area} = 1.2803 \text{ in}^2 + 2.7125 \text{ in}^2 = 3.9928 \text{ in}^2$$

$$\text{Fill\%} = \frac{3.9928 \text{ in}^2}{12.882 \text{ in}^2} \times 100\% = 31.00\% \leq 31\% \quad \text{(nominally compliant)}$$

With 2 cables, the 31% limit of 3.994 in² leaves only 0.0006 in² of margin, so we upsize Conduit 3 to **5" trade size RMC** (100% Area = 20.212 in², 31% Fill Limit = 6.266 in²).

$$\text{Fill\%} = \frac{3.9928 \text{ in}^2}{20.212 \text{ in}^2} \times 100\% = 19.75\% \leq 31\% \quad \checkmark \text{ PASS}$$

**Result: Fill two 4" RMC conduits (Conduits 1 & 2) for LV control, and one 5" RMC conduit (Conduit 3) for mixed power**

---

## Appendix

<!-- ### Related Knowledge Files

[Knowledge File: Maximum Allowable Conductors/Cables in Conduit and Tubing] -->

### Related NEC Articles

Section 310.15 — Ampacity Correction and Adjustment Factors<br/>
Section 310.16 — Allowable Ampacities of Conductors

### Related NEC Tables

Chapter 9, Table 1 — Percent of Cross Section of Conduit and Tubing for Conductors<br/>
Chapter 9, Table 4 — Dimensions and Percent Area of Conduit and Tubing<br/>
Chapter 9, Table 5 — Dimensions of Insulated Conductors and Fixture Wires