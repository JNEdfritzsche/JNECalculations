## Overview

This section walks through worked examples for conduit fill calculations under OESC Rule 12-904 and Table 9. The goal is to demonstrate how to sum cable areas, select conduit size, and check against the allowable fill limit. For theory and table selection, refer to the theory tab.

The core formula is:

$$\text{Fill\%} = \frac{\sum (A_{\text{cable}} \times N_{\text{cond/cable}} \times N_{\text{cables}})}{A_{\text{conduit}}} \times 100\%$$

Where $A_{\text{cable}}$ is the cross-sectional area per conductor (mm²) from Table 6, and $A_{\text{conduit}}$ is the conduit internal area (mm²) from Table 9.

**Allowable fill limits (OESC Table 9):**

| Number of cables | Max fill | Table reference |
|-----------------|---------|----------------|
| 1 cable | 53% | Table 9C |
| 2 cables | 31% | Table 9E |
| 3+ cables | 40% | Table 9G |

---

## Example 1 — Two Valid Conduit Solutions

**600 V | RMC | 3× #250 MCM – 1/C | Table 6C | RW90XLPE jacketed**

This example demonstrates that conduit selection is not always unique — the designer must evaluate multiple valid options and choose based on project constraints (space, cost, routing).

| Parameter | Value |
|-----------|-------|
| Cable area (Table 6C, #250 MCM, 1/C) | 354 mm² per cable |
| Number of cables | 3 |
| Total cable area | 3 × 354 = **1,062 mm²** |

**Option A — One 63 mm (2½") conduit, all 3 cables**

With 3 cables, the 40% fill limit applies (Table 9G).

$$A_{\text{conduit, min}} = \frac{1{,}062}{0.40} = 2{,}655 \text{ mm}^2 \quad \Rightarrow \text{Select } 63 \text{ mm RMC} = 3{,}139 \text{ mm}^2$$

$$\text{Fill\%} = \frac{1{,}062}{3{,}139} \times 100\% = 33.83\% \leq 40\% \quad \checkmark \text{ PASS}$$

**Option B — Three 35 mm (1¾") conduits, one cable each**

With 1 cable per conduit, the 53% fill limit applies (Table 9C).

$$A_{\text{conduit, min}} = \frac{354}{0.53} = 667.9 \text{ mm}^2 \quad \Rightarrow \text{Select } 35 \text{ mm RMC} = 985 \text{ mm}^2$$

$$\text{Fill\%} = \frac{354}{985} \times 100\% = 35.94\% \leq 53\% \quad \checkmark \text{ PASS (per conduit)}$$

**Result: Fill one 63 mm (2½") RMC at 33.8% — or — three 35 mm (1¾") RMC conduits at 35.9% each**

---

## Example 2 — Single Cable Type, Two Conduit Runs

**480 V | RMC | Two runs of 3× #1/0 AWG – 1/C | Table 6A | RPV90 unjacketed**

Two separate 3-conductor runs are required. Each run is sized independently. With 3 cables per conduit, the 40% fill limit applies.

| Parameter | Value |
|-----------|-------|
| Cable area (Table 6A, #1/0 AWG, 1/C) | 119 mm² per cable |
| Number of cables per conduit | 3 |
| Total cable area per conduit | 3 × 119 = **357 mm²** |

$$A_{\text{conduit, min}} = \frac{357}{0.40} = 892.5 \text{ mm}^2 \quad \Rightarrow \text{Select } 35 \text{ mm RMC} = 985 \text{ mm}^2$$

$$\text{Fill\%} = \frac{357}{985} \times 100\% = 36.24\% \leq 40\% \quad \checkmark \text{ PASS}$$

**Result: Fill two 35 mm (1¾") RMC conduits, one run per conduit, at 36.2% each**

---

## Example 3 — Mixed Cable Types Requiring Split Conduits

**Mixed 24VDC and 480V cables | RMC**

Three cable groups are present. The 24VDC control cables must be kept separate from the 480V power cables. The 480V group contains one 3/C cable and four 1/C cables.

| Cable group | Table | Area/cable | Qty | Total area |
|-------------|-------|-----------|-----|------------|
| 24VDC — #14 AWG – 1/C | 6J | 8.9 mm² | 80 | 712 mm² |
| 480V — #1/0 AWG – 3/C | 6C | 499 mm² | 1 | 499 mm² |
| 480V — #1/0 AWG – 1/C | 6C | 167 mm² | 4 | 668 mm² |

**Conduit 1 — 24VDC control cables (80 cables, 40% limit):**

$$A_{\text{conduit, min}} = \frac{712}{0.40} = 1{,}780 \text{ mm}^2 \quad \Rightarrow \text{Select } 63 \text{ mm RMC} = 3{,}139 \text{ mm}^2$$

$$\text{Fill\%} = \frac{712}{3{,}139} \times 100\% = 22.68\% \leq 40\% \quad \checkmark \text{ PASS}$$

**Conduit 2 — 480V power cables (5 cables, 40% limit):**

$$\text{Total} = 499 + (4 \times 167) = 1{,}167 \text{ mm}^2$$

$$A_{\text{conduit, min}} = \frac{1{,}167}{0.40} = 2{,}917.5 \text{ mm}^2 \quad \Rightarrow \text{Select } 63 \text{ mm RMC} = 3{,}139 \text{ mm}^2$$

$$\text{Fill\%} = \frac{1{,}167}{3{,}139} \times 100\% = 37.18\% \leq 40\% \quad \checkmark \text{ PASS}$$

**Result: Fill two 63 mm (2½") RMC conduits — Conduit 1 (24VDC control) at 22.7%, Conduit 2 (480V power) at 37.2%**

---

## Example 4 — Complex Multi-Conduit, Mixed Voltage Levels

**Mixed 24VDC, 120V, and 600V cables | RMC**

Four cable groups must be distributed across three conduits. The 600V HV cable must be isolated from all LV cables. The two 24VDC groups are separated because combining them would exceed 200 conductors in a single raceway (175 + 64 = 239 conductors; note: combining with other groups pushes total above the threshold).

| Cable group | Table | Area/cable | Qty | Total area |
|-------------|-------|-----------|-----|------------|
| 24VDC — #10 AWG – 1/C | 6J | 15.70 mm² | 175 | 2,747.5 mm² |
| 24VDC — #14 AWG – 1/C | 6J | 8.90 mm² | 64 | 569.6 mm² |
| 120V — #4/0 AWG – 4/C | 6A | 826 mm² | 1 | 826 mm² |
| 600V — #500 MCM – 3/C | 6C | 1,750 mm² | 1 | 1,750 mm² |

For 103mm RMC: internal area = 8,311 mm². Allowable at 40% (3+ cables, Table 9G) = **3,325 mm²**. Allowable at 31% (2 cables, Table 9E) = **2,576 mm²**.

**Conduit 1 — 24VDC #10 AWG (175 cables, 40% limit):**

$$\text{Fill\%} = \frac{175 \times 15.70}{8{,}311} \times 100\% = \frac{2{,}747.5}{8{,}311} = 33.06\% \leq 40\% \quad \checkmark \text{ PASS}$$

**Conduit 2 — 24VDC #14 AWG (64 cables, 40% limit):**

$$\text{Fill\%} = \frac{64 \times 8.90}{8{,}311} \times 100\% = \frac{569.6}{8{,}311} = 6.85\% \leq 40\% \quad \checkmark \text{ PASS}$$

**Conduit 3 — 120V + 600V power (2 cables → 31% limit applies, Table 9E):**

$$\text{Fill\%} = \frac{826 + 1{,}750}{8{,}311} \times 100\% = \frac{2{,}576}{8{,}311} = 30.99\% \leq 31\% \quad \checkmark \text{ PASS (barely)}$$

**Result: Fill three 103 mm (4") RMC conduits — Conduits 1 & 2 for LV control, Conduit 3 for LV/HV power at 31.0%**

---

## Example 5 — Voltage Segregation, Two Runs in Separate Conduits

**Mixed 24VDC and 600V | RMC | 53 mm (2")**

Two cable runs must be kept in separate conduits due to voltage segregation. The 24VDC signal run uses 40% fill (3+ cables per conduit). The 600V power run is a single 6/C cable and uses 53% fill (1 cable).

| Cable group | Insulation | Conductors | Area/cable | Qty | Total area |
|-------------|------------|------------|-----------|-----|------------|
| 24VDC — #14 AWG – 1/C | TW75 | 98 × 1/C | 8.9 mm² | 98 | 872.2 mm² |
| 600V — #2/0 AWG – 6/C | RW90XLPE jacketed | 1 × 6/C | 1,165 mm² | 1 | 1,165 mm² |

For 53 mm (2") RMC: internal area = 2,199 mm².

**Conduit 1 — 24VDC signal (98 cables, 40% limit):**

$$\text{Fill\%} = \frac{872.2}{2{,}199} \times 100\% = 39.66\% \leq 40\% \quad \checkmark \text{ PASS}$$

**Conduit 2 — 600V power (1 cable, 53% limit):**

$$\text{Fill\%} = \frac{1{,}165}{2{,}199} \times 100\% = 52.97\% \leq 53\% \quad \checkmark \text{ PASS}$$

**Result: Fill two 53 mm (2") RMC conduits — Conduit 1 (24VDC signal) at 39.7%, Conduit 2 (600V power) at 53.0%**

---

## Example 6 — Gauge Segregation Due to 200-Conductor Limit

**Mixed 24VDC and 480V | RMC | 78 mm (3")**

The 24VDC signal group contains 225 conductors total (75× #14 + 150× #10), exceeding the 200-conductor per conduit limit per Rule 12-910. The two gauges must be split into separate conduits. The 480V power run is kept in a third conduit.

| Cable group | Conductors | Area/cable | Qty | Total area |
|-------------|------------|-----------|-----|------------|
| 24VDC — #14 AWG – 1/C | 75 × 1/C | 8.9 mm² | 75 | 667.5 mm² |
| 24VDC — #10 AWG – 1/C | 150 × 1/C | 15.7 mm² | 150 | 2,355 mm² |
| 480V — #250 MCM – 1/C | 4 × 1/C | 354 mm² | 4 | 1,416 mm² |

For 78 mm (3") RMC: internal area = 4,839 mm². With 3+ cables, 40% fill limit applies.

**Initial check — Conduit 2 (#10 AWG, 150 cables, 40% limit):**

$$\text{Fill\%} = \frac{150 \times 15.7}{4{,}839} \times 100\% = \frac{2{,}355}{4{,}839} = 48.67\% > 40\% \quad \times \text{ FAIL}$$

150× #10 AWG exceeds 40% fill. Move 27 cables from Conduit 2 into Conduit 1 to bring both within limits.

**Revised — Conduit 1 (75× #14 AWG + 27× #10 AWG, 40% limit):**

$$\text{Fill\%} = \frac{(75 \times 8.9) + (27 \times 15.7)}{4{,}839} \times 100\% = \frac{667.5 + 423.9}{4{,}839} = \frac{1{,}091.4}{4{,}839} = 22.55\% \leq 40\% \quad \checkmark \text{ PASS}$$

**Revised — Conduit 2 (remaining 123× #10 AWG, 40% limit):**

$$\text{Fill\%} = \frac{123 \times 15.7}{4{,}839} \times 100\% = \frac{1{,}931.1}{4{,}839} = 39.91\% \leq 40\% \quad \checkmark \text{ PASS}$$

**Conduit 3 — 480V power (4 cables, 40% limit):**

$$\text{Fill\%} = \frac{4 \times 354}{4{,}839} \times 100\% = \frac{1{,}416}{4{,}839} = 29.26\% \leq 40\% \quad \checkmark \text{ PASS}$$

**Result: Fill three 78 mm (3") RMC conduits — Conduit 1 (#14 + partial #10) at 22.6%, Conduit 2 (remaining #10) at 39.9%, Conduit 3 (480V power) at 29.3%**

---

## Appendix

### Related Knowledge Files

[Knowledge File: Maximum Allowable Conductors/Cables in Conduit and Tubing](https://jnepeng.sharepoint.com/:w:/s/JNEElectricalPortalTeams/IQD_dpZ_f5oHQ6fAWxmiT_CjAb57hCu7AJd_lmC_tLEvPTM?e=bzHXAI)

### Related OESC Rules

Rule 4-004 — Ampacity of Wires and Cables<br/>
Rule 12-902 — Types of insulated conductors and cables<br/>
Rule 12-904 — Conductors in Raceways<br/>
Rule 12-910 — Conductors in Conduit

### Related OESC Tables

Table 7 — Minimum conduit bending radius<br/>
Table 8 — Maximum allowable conduit fill percent<br/>
Tables 9A-9G — Conduit areas at various percentages<br/>
Table 19 — Conditions of use for Conductors and Cables
