## Overview

This section walks through worked examples for conductor sizing under OESC Rule 4-004. The goal is to demonstrate how to identify which tables and correction factors apply, and how to combine them correctly. For theory and derating methodology, refer to the theory tab.

---

## Example 1 — Free Air, No Derating

**600 V, 3Ø 3W | 60 A | Single conductors | Ladder tray | 30 °C ambient | 60 °C insulation | Spacing ≥100%**

No correction factors apply — ambient is at the 30 °C baseline and spacing is sufficient.

| Item | Selection |
|------|-----------|
| Subrule | 4-004 (1) & (2) — single in free air |
| Ampacity table | Table 1 |
| Correction table | None |
| Temperature correction | None |

$$k_{\text{corr}} = 1.0 \qquad k_{\text{temp}} = 1.0 \qquad k_{\text{total}} = 1.0$$

$$I_{\text{table}} = \frac{I_{\text{per set}}}{k_{\text{total}}} = \frac{60}{1.0} = 60 \text{ A}$$

From **Table 1**, Copper, 60 °C column → **8 AWG** at 60 A.

$$I_{\text{adjusted}} = 60 \times 1.0 = 60 \text{ A} \geq 60 \text{ A} \checkmark$$

**Result: 3× #8 AWG – 1/C**

---

## Example 2 — Free Air, Temperature + Grouping (≤4 Single Conductors)

**600 V, 3Ø 4W | 100 A | Single conductors | Ladder tray | 40 °C ambient | 75 °C insulation | Spacing <25%**

With ≤4 single conductors in free air at close spacing, **Table 5B** applies. Elevated ambient means **Table 5A** also applies.

| Item | Selection |
|------|-----------|
| Subrule | 4-004 (9) — ≤4 single in free air |
| Ampacity table | Table 1 |
| Correction table | Table 5B |
| Temperature correction | Table 5A |

$$k_{\text{corr}} = 0.8 \quad \text{(Table 5B)} \qquad k_{\text{temp}} = 0.88 \quad \text{(Table 5A, 75 °C @ 40 °C)}$$

$$k_{\text{total}} = 0.8 \times 0.88 = 0.704$$

$$I_{\text{table}} = \frac{100}{0.704} \approx 142 \text{ A}$$

From **Table 1**, Copper, 75 °C column → **3 AWG** at 145 A.

$$I_{\text{adjusted}} = 145 \times 0.8 \times 0.88 = 102.1 \text{ A} \geq 100 \text{ A} \checkmark$$

**Result: 4× #3 AWG – 1/C**

---

## Example 3 — Free Air, Temperature + Grouping (≥5 Single Conductors)

**600 V, 3Ø 4W+GND | 75 A | Single conductors | Ladder tray | 40 °C ambient | 60 °C insulation | Spacing <25%**

Five or more single conductors in free air at close spacing is functionally equivalent to conductors in a raceway — **Table 5C** applies instead of 5B. Elevated ambient means **Table 5A** also applies.

| Item | Selection |
|------|-----------|
| Subrule | 4-004 (11) — ≥5 single in free air |
| Ampacity table | Table 2 |
| Correction table | Table 5C |
| Temperature correction | Table 5A |

$$k_{\text{corr}} = 0.8 \quad \text{(Table 5C, 4–6 conductors)} \qquad k_{\text{temp}} = 0.82 \quad \text{(Table 5A, 60 °C @ 40 °C)}$$

$$k_{\text{total}} = 0.8 \times 0.82 = 0.656$$

$$I_{\text{table}} = \frac{75}{0.656} \approx 114.3 \text{ A}$$

From **Table 2**, Copper, 60 °C column → **0 AWG** at 125 A.

$$I_{\text{adjusted}} = 125 \times 0.8 \times 0.82 = 82 \text{ A} \geq 75 \text{ A} \checkmark$$

**Result: 5× #1/0 AWG – 1/C**

---

## Appendix

### Related Knowledge Files

[Knowledge File — OESC: Section 4 Conductors](https://jnepeng.sharepoint.com/:b:/s/JNEElectricalPortalTeams/IQBX__AeZwFdTaYRIpekMk53AST1Z1fmbLyJuMdhL2C3csc?e=siODjS)<br/>
[Knowledge File — Conductor and Cable Derating](https://jnepeng.sharepoint.com/:w:/s/JNEElectricalPortalTeams/IQBMnxSrwpgZQKutZR-IKS8qAeWe8-uExB0Z5BcelGhbldA?e=cjV7bE)

### Related OESC Rules

Rule 4-004 — Ampacity of Wires and Cables<br/>
Rule 4-006 — Temperature Limitations

### Related OESC Tables

Table 1/2 — Single Conductor Ampacities for Copper/Aluminum<br/>
Table 3/4 — Multi-Conductor Ampacities for Copper/Aluminum<br/>
Table 5A — Conductor Ambient Temperature Correction Factors<br/>
Table 5B — Single Conductor Spacing Correction Factors<br/>
Table 5C — Multi-Conductor Group Correction Factors<br/>
Table 5D — Cable Tray Spacing Correction Factors<br/>
