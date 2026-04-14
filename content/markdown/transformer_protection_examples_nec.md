## Overview

This section walks through worked examples for sizing transformer overcurrent protection devices per **NEC Article 450.3**. The key distinction is whether the transformer voltage is over 1000 V (Table 450.3(A)) or 1000 V and below (Table 450.3(B)), and whether the installation qualifies as a supervised location. For theory and table selection, refer to the theory tab.

Primary and secondary full-load current uses the 3φ formula:

$$I_{\text{pri}} = \frac{S}{\sqrt{3} \cdot V_{\text{pri}}} \qquad I_{\text{sec}} = \frac{S}{\sqrt{3} \cdot V_{\text{sec}}}$$

OCPD ratings are found by multiplying FLA by the applicable Table 450.3 multiplier, then rounding to the next available standard or commercially available device size per NEC 240.6(A).

---

## Example 1 — 2 MVA, High-Voltage Transformer (Over 1000 V)

**2 MVA | 3φ | 27.6 kV primary / 4.16 kV secondary | Z ≤ 6% | Any location**

For transformers over 1000 V, use **Table 450.3(A)**.

| Parameter | Value |
|-----------|-------|
| Apparent power $S$ | 2,000,000 VA |
| Primary voltage $V_{\text{pri}}$ | 27,600 V |
| Secondary voltage $V_{\text{sec}}$ | 4,160 V |
| Impedance | ≤ 6% |
| Installation | Any location |

**Full-load currents:**

$$I_{\text{pri}} = \frac{2{,}000{,}000}{\sqrt{3} \times 27{,}600} \approx 41.89 \text{ A}$$

$$I_{\text{sec}} = \frac{2{,}000{,}000}{\sqrt{3} \times 4{,}160} \approx 277.90 \text{ A}$$

**OCPD sizing per Table 450.3(A) (Z ≤ 6%, any location):**

| Side | Device | Multiplier | Target | Selected (commercially available) |
|------|--------|-----------|--------|----------------------------------|
| Primary | Circuit breaker | 6.00 | 6.00 × 41.89 = 251.3 A | **300 A** |
| Primary | Fuse | 3.00 | 3.00 × 41.89 = 125.7 A | **150 A** |
| Secondary | Circuit breaker | 3.00 | 3.00 × 277.90 = 833.7 A | **1000 A** |
| Secondary | Fuse | 2.50 | 2.50 × 277.90 = 694.8 A | **700 A** |

**Result: Primary — 300 A breaker or 150 A fuse | Secondary — 1000 A breaker or 700 A fuse**

---

## Example 2 — 75 kVA, Low-Voltage Transformer (1000 V and Below)

**75 kVA | 3φ | 600 V primary / 208 V secondary | Currents > 9 A**

For transformers 1000 V and below, use **Table 450.3(B)**. Two protection schemes are evaluated: primary-only and primary+secondary.

| Parameter | Value |
|-----------|-------|
| Apparent power $S$ | 75,000 VA |
| Primary voltage $V_{\text{pri}}$ | 600 V |
| Secondary voltage $V_{\text{sec}}$ | 208 V |

**Full-load currents:**

$$I_{\text{pri}} = \frac{75{,}000}{\sqrt{3} \times 600} \approx 72.25 \text{ A}$$

$$I_{\text{sec}} = \frac{75{,}000}{\sqrt{3} \times 208} \approx 208.43 \text{ A}$$

**Scheme A — Primary-only protection (Table 450.3(B), currents > 9 A):**

$$I_{\text{pri, OCPD}} = 1.25 \times 72.25 = 90.3 \text{ A} \quad \Rightarrow \text{Select } \mathbf{100 \text{ A}}$$

**Scheme B — Primary + secondary protection (Table 450.3(B)):**

| Side | Multiplier | Target | Selected |
|------|-----------|--------|----------|
| Primary | 2.50 | 2.50 × 72.25 = 180.6 A | **200 A** |
| Secondary | 1.25 | 1.25 × 208.43 = 260.5 A | **300 A** |

**Result: Primary-only → 100 A primary OCPD | Primary+secondary → 200 A primary / 300 A secondary**

---

## Appendix

### Related Knowledge Files

### Related NEC Articles

NEC 240.6(A) — Standard ampere ratings for fuses and circuit breakers<br/>
NEC 450.3 — Overcurrent protection for transformers<br/>
NEC 450.3(A) — Transformers over 1000 V nominal<br/>
NEC 450.3(B) — Transformers 1000 V nominal or less

### Related NEC Tables

Table 450.3(A) — Maximum rating or setting of overcurrent protection for transformers over 1000 V<br/>
Table 450.3(B) — Maximum rating or setting of overcurrent protection for transformers 1000 V and below
