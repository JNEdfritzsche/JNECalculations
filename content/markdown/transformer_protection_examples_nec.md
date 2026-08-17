## Overview

This section walks through worked examples for calculating and sizing transformer Overcurrent Protective Devices (OCPDs) under the National Electrical Code (NEC) 2026. Sizing is governed by NEC Article 450.5 and the corresponding Tables 450.5(A) and 450.5(B). Sizing maximums differ based on whether the primary nominal voltage is over 1000V or 1000V and less, and whether secondary protection is provided.

---

## Example 1 — Transformers Over 1000V; Primary-Only Protection

A transformer has the following nameplate parameters:

| Parameter | Value |
|-----------|-------|
| Power     | 2 MVA (2,000 kVA) |
| Phase     | 3 |
| $V_P$     | 12.47 kV |
| $V_S$     | 480 V |
| Impedance | 5.5% |
| Location  | Supervised |

According to NEC Table 450.5(A) for supervised installations:
- The maximum rating for primary fuses is **250%** of primary FLC.
- The maximum rating for primary circuit breakers is **300%** of primary FLC.

**Primary full-load current calculation:**

$$ I_P = \frac{2{,}000{,}000 \text{ VA}}{\sqrt{3} \times 12{,}470 \text{ V}} \approx 92.60 \text{ A} $$

Both devices are above 1000 V, so Note 1 permits rounding up to the next higher **commercially available** rating. The 240.6(A) standard-rating list applies only at 1000 V and below.

**Sizing for Fuses (250%):**

$$ I_{\text{fuse, max}} = 92.60 \text{ A} \times 2.50 = 231.50 \text{ A} \quad \Rightarrow \text{Select a 250 A fuse} $$

**Sizing for Circuit Breakers (300%):**

$$ I_{\text{CB, max}} = 92.60 \text{ A} \times 3.00 = 277.80 \text{ A} \quad \Rightarrow \text{Select a 300 A circuit breaker} $$

---

## Example 2 — Transformers Over 1000V; Primary & Secondary Protection

A transformer has the following nameplate parameters:

| Parameter | Value |
|-----------|-------|
| Power     | 750 kVA |
| Phase     | 3 |
| $V_P$     | 13.8 kV |
| $V_S$     | 4.16 kV |
| Impedance | 5.75% |
| Location  | Supervised |

Since both primary and secondary are over 1000V, we refer to Table 450.5(A) for primary and secondary protection (Supervised). The rated impedance of 5.75% falls in the *Not more than 6%* row, which sets the multipliers:
- Primary circuit breaker max multiplier = **600%**
- Primary fuse max multiplier = **300%**
- Secondary circuit breaker max multiplier = **300%**
- Secondary fuse max multiplier = **250%**

**Primary and Secondary current calculations:**

$$ I_P = \frac{750{,}000 \text{ VA}}{\sqrt{3} \times 13{,}800 \text{ V}} \approx 31.38 \text{ A} $$

$$ I_S = \frac{750{,}000 \text{ VA}}{\sqrt{3} \times 4{,}160 \text{ V}} \approx 104.09 \text{ A} $$

All four devices are above 1000 V, so Note 1 rounds up to the next higher **commercially available** rating.

**Primary Device Sizing:**
- Circuit Breaker: $31.38 \text{ A} \times 6.00 = 188.28 \text{ A} \quad \Rightarrow \text{Select a 200 A CB}$
- Fuse: $31.38 \text{ A} \times 3.00 = 94.14 \text{ A} \quad \Rightarrow \text{Select a 100 A fuse}$

**Secondary Device Sizing:**
- Circuit Breaker: $104.09 \text{ A} \times 3.00 = 312.27 \text{ A} \quad \Rightarrow \text{Select a 350 A CB}$
- Fuse: $104.09 \text{ A} \times 2.50 = 260.23 \text{ A} \quad \Rightarrow \text{Select a 300 A fuse}$

---

## Example 3 — Transformers 1000V and Less; Oil-Type, Primary-Only Protection

A transformer has the following nameplate parameters:

| Parameter | Value |
|-----------|-------|
| Power     | 100 kVA |
| Phase     | 1 |
| $V_P$     | 480 V |
| $V_S$     | 120/240 V |
| Type      | Oil-Insulated |

For transformers rated 1000V or less, we use NEC Table 450.5(B). Sizing is based on current levels, and oil-type transformers follow the same electrical rules as dry-type under 1000V. Sizing for primary-only protection (current is 9A or more) allows a maximum multiplier of **125%**.

**Primary full-load current calculation:**

$$ I_P = \frac{100{,}000 \text{ VA}}{480 \text{ V}} = 208.33 \text{ A} $$

**OCPD Sizing (125%):**

$$ I_{\text{target}} = 208.33 \text{ A} \times 1.25 = 260.41 \text{ A} $$

Using Table 450.5(B) Note 1, we are permitted to round up to the next standard rating because 125% does not align with standard size.
- Standard sizes from 240.6(A): 250 A, then 300 A.
- **Select standard 300 A fuse or circuit breaker**

---

## Example 4 — Transformers 1000V and Less; Dry-Type, Primary & Secondary Protection

A dry-type transformer has the following nameplate parameters:

| Parameter | Value |
|-----------|-------|
| Power     | 15 kVA |
| Phase     | 1 |
| $V_P$     | 480 V |
| $V_S$     | 240 V |
| Type      | Dry-type |

Under Table 450.5(B), when providing secondary protection at not more than 125%, the primary side protection is permitted to be up to **250%** of the primary FLC. Note that under NEC Table 450.5(B) Note 1, rounding up is only permitted for the secondary OCPD (at 125%); for the primary OCPD (at 250%), rounding up is **not** permitted.

**Primary and Secondary current calculations:**

$$ I_P = \frac{15{,}000 \text{ VA}}{480 \text{ V}} = 31.25 \text{ A} $$

$$ I_S = \frac{15{,}000 \text{ VA}}{240 \text{ V}} = 62.5 \text{ A} $$

**Primary OCPD Sizing (250% - No Rounding Up):**

$$ I_{\text{pri, max}} = 31.25 \text{ A} \times 2.50 = 78.13 \text{ A} $$

Since rounding up is not permitted above 250%, we must round down to the next standard rating:
- **Select standard 70 A fuse or circuit breaker**

**Secondary OCPD Sizing (125% - Rounding Up Permitted):**

$$ I_{\text{sec, max}} = 62.5 \text{ A} \times 1.25 = 78.13 \text{ A} $$

Since rounding up is permitted for the 125% secondary limit, we round up to the next standard rating:
- **Select standard 80 A fuse or circuit breaker**

---

## Appendix

<!-- ### Related Knowledge Files

[Knowledge File — NEC: Article 450 Transformers and Transformer Vaults]<br/>
[Design Basis — Calculations: Transformer Protection Calculation] -->

### Related NEC Articles

Section 240.6 — Standard Overcurrent Device Ratings<br/>
Section 450.5 — Overcurrent Protection of Transformers

### Related NEC Tables

Table 450.5(A) — Overcurrent Protection for Transformers Over 1000 Volts<br/>
Table 450.5(B) — Overcurrent Protection for Transformers 1000 Volts and Less