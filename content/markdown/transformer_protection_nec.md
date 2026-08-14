## Overview

The Transformer Protection section outlines the NEC design requirements and overcurrent protection limitations to safeguard transformers and their supply conductors. The NEC classifies transformers into two main voltage levels, each with its own overcurrent protective device (OCPD) sizing limits under **NEC Article 450.3**:

- Circuits rated over 1000 Volts
- Circuits rated 1000 Volts or Less

This section focuses on sizing fuses and circuit breakers to protect the transformer winding. Conductor and feeder sizing requirements are covered in the Transformer Feeders section.

---

## Transformer Circuit Classifications

### 1. Transformer Circuits Rated Over 1000 V

Each ungrounded conductor of a transformer feeder supplying a transformer rated over 1000V must be provided with overcurrent protection. Under **NEC Table 450.3(A)**, the maximum OCPD setting depends on whether the installation is supervised and whether both primary and secondary protection are used:

**Supervised Installations (Primary-Only Protection):**

- Primary Fuses: Maximum **250%** of primary FLC.
- Primary Circuit Breakers: Maximum **300%** of primary FLC.

**Supervised Installations (Primary & Secondary Protection):**

- Primary Fuses: Maximum **300%** of primary FLC.
- Primary Circuit Breakers: Maximum **600%** of primary FLC.
- Secondary Fuses: Maximum **250%** of secondary FLC.
- Secondary Circuit Breakers: Maximum **300%** of secondary FLC.

<div align="center">

![Figure 1: Transformers rated over 1000V layout](../images/TXProtect1.png)

</div>

### 2. Transformer Circuits Rated 1000 V or Less

Under **NEC Table 450.3(B)**, overcurrent protection requirements for low-voltage transformers are based on the nominal full-load current (FLC):

**Primary-Only Protection (No Secondary OCPD):**

- Primary FLC of 9 A or more: Maximum **125%** of FLC. (Note 1 permits rounding up to the next standard OCPD rating per NEC 240.6(A)).
- Primary FLC less than 9 A: Maximum **167%** of FLC (No rounding up permitted).
- Primary FLC less than 2 A: Maximum **300%** of FLC (No rounding up permitted).

**Primary & Secondary Protection:**

- Primary FLC of 9 A or more: Maximum **250%** of FLC. (Rounding up is **not** permitted).
- Secondary FLC of 9 A or more: Maximum **125%** of FLC. (Note 1 permits rounding up to the next standard rating).
- Secondary FLC less than 9 A: Maximum **167%** of FLC (No rounding up permitted).

<div align="center">

![Figure 2: Transformers rated under 1000V primary and secondary layout](../images/TXProtect2.png)

</div>

---

## Key Design Considerations

### Continuous Circuit Loading

Under NEC 215.2(A)(1), transformer supply feeders must be sized for 125% of the continuous load. This thermal margin must be maintained to prevent conductor degradation.

### Fuses vs. Circuit Breakers

Circuit breakers are often specified for high-value industrial assets to prevent single-phase tripping (which can damage downstream three-phase motors). Fuses are cost-effective and offer exceptionally high short-circuit interrupting ratings. Standard ratings are defined in NEC 240.6(A).

---

## Sizing Examples (Supervised Industrial Location)

These examples assume a standard indoor/outdoor industrial environment with copper conductors installed in raceways per Table 310.16.

### 1. Transformer Rated Over 1000 V

Consider an oil-filled transformer in a supervised industrial facility:

| Parameter         | Value             |
| ----------------- | ----------------- |
| Rating            | 2 MVA (2,000 kVA) |
| Primary Voltage   | 27.6 kV           |
| Secondary Voltage | 600 V             |
| Impedance         | 6%                |

**Full-Load Current Calculations:**

- Primary FLC:

$$ I_P = \frac{2{,}000 \times 10^3 \text{ VA}}{\sqrt{3} \times 27.6 \times 10^3 \text{ V}} \approx 41.84 \text{ A} $$

- Secondary FLC:

$$ I_S = \frac{2{,}000 \times 10^3 \text{ VA}}{\sqrt{3} \times 600 \text{ V}} \approx 1924.50 \text{ A} $$

**OCPD Sizing (Supervised, Primary & Secondary Protection, Table 450.3(A)):**

- **Primary Fuses (300% max limit)**: $41.84\text{ A} \times 3.00 = 125.52\text{ A}$. Using Note 1 (rounding up to next standard rating): **Select standard 150 A fuses**.
- **Primary Circuit Breaker (600% max limit)**: $41.84\text{ A} \times 6.00 = 251.04\text{ A}$. Using Note 1 (rounding up): **Select standard 300 A circuit breaker**.
- **Secondary Circuit Breaker (300% max limit)**: $1924.50\text{ A} \times 3.00 = 5773.50\text{ A}$. Using Note 1 (rounding up): **Select standard 6000 A circuit breaker**.

---

### 2. Transformer Rated 1000 V or Less (Primary-Only Protection)

Consider a transformer with the following nameplate parameters:

| Parameter         | Value  |
| ----------------- | ------ |
| Rating            | 75 kVA |
| Primary Voltage   | 600 V  |
| Secondary Voltage | 208 V  |

**Full-Load Current Calculations:**

- Primary FLC:

$$ I_P = \frac{75{,}000 \text{ VA}}{\sqrt{3} \times 600 \text{ V}} \approx 72.17 \text{ A} $$

**Primary OCPD Sizing (Table 450.3(B) — Primary-Only, 125%):**

$$ I_{\text{target}} = 72.17 \text{ A} \times 1.25 = 90.21 \text{ A} $$

Under Table 450.3(B) Note 1, we round up to the next standard OCPD rating:

- **Select standard 100 A fuse or circuit breaker**

---

### 3. Transformer Rated 1000 V or Less (Primary & Secondary Protection)

Consider a dry-type transformer with the following nameplate parameters:

| Parameter         | Value  |
| ----------------- | ------ |
| Rating            | 75 kVA |
| Primary Voltage   | 600 V  |
| Secondary Voltage | 208 V  |

**Full-Load Current Calculations:**

- Primary FLC: $I_P \approx 72.17\text{ A}$
- Secondary FLC:

$$ I_S = \frac{75{,}000 \text{ VA}}{\sqrt{3} \times 208 \text{ V}} \approx 208.18 \text{ A} $$

**OCPD Sizing (Table 450.3(B) — Primary and Secondary Protection):**

- **Primary OCPD (250% limit - Rounding Up NOT Permitted)**: 

$$ I_{\text{pri, max}} = 72.17 \text{ A} \times 2.50 = 180.43 \text{ A} $$

Since rounding up is not permitted above 250%, we must round down to the next standard rating:

- **Select standard 175 A fuse or circuit breaker**

- **Secondary OCPD (125% limit - Rounding Up Permitted)**:

$$ I_{\text{sec, max}} = 208.18 \text{ A} \times 1.25 = 260.23 \text{ A} $$

Since rounding up is permitted for the 125% secondary limit, we round up to the next standard rating:

- **Select standard 300 A fuse or circuit breaker**

---

## Conclusion

Based on the calculated nominal FLCs and standard NEC rules, the required overcurrent protection device sizes are:

**2 MVA, 27.6 kV / 600 V, Supervised, Both Sides Protected Transformer**

- Primary: 150 A fuses or 300 A circuit breaker
- Secondary: 6000 A circuit breaker

**75 kVA, 600 V / 208 V, Low-Voltage Primary-Only Protected Transformer**

- Primary: 100 A rated fuse or circuit breaker

**75 kVA, 600 V / 208 V, Dry-Type, Both Sides Protected Transformer**

- Primary: 175 A rated fuse or circuit breaker
- Secondary: 300 A rated fuse or circuit breaker

---

## Appendix

<!-- ### Related Knowledge Files

[Knowledge File — NEC: Article 450 Transformers and Transformer Vaults]<br/>
[Design Basis — Calculations: Transformer Protection Calculation] -->

### Related NEC Articles

Section 240.6 — Standard Overcurrent Device Ratings<br/>
Section 450.3 — Overcurrent Protection of Transformers

### Related NEC Tables

Table 240.6(A) — Standard Ampere Ratings for Fuses and Circuit Breakers<br/>
Table 450.3(A) — Overcurrent Protection for Transformers Over 1000 Volts<br/>
Table 450.3(B) — Overcurrent Protection for Transformers 1000 Volts and Less
