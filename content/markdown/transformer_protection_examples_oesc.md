## Overview

Below we size overcurrent protection devices for the three types of transformer circuits. We assume the following:

- Ambient temperature: 40 °C
- Conductor temperature: 75 °C
- Copper conductor routed in free air, evenly spaced
- No more than 3 conductors per cable, complete with ground
- Maximum cable length: 50 m
- Transformer operating with natural cooling (no fans/pumps)

---

## Example 1 — Transformer Rated Over 750 V

Consider an oil-filled transformer with the following nameplate. Calculate the fuse and circuit breaker sizes for primary overcurrent protection.

| Parameter       | Value   |
|-----------------|---------|
| Rating          | 2 MVA   |
| Primary Voltage | 27.6 kV |
| Secondary Voltage | 600 V |
| Phase           | 3       |
| Frequency       | 60 Hz   |
| Impedance       | 6 %     |

The FLCs can be calculated as:

| Side      | Calculation | FLA (A) |
|-----------|-------------|---------|
| Primary   | $$ \frac{2000 \times 10^3}{\sqrt{3} \times 27.6 \times 10^3} $$ | 41.84 |
| Secondary | $$ \frac{2000 \times 10^3}{\sqrt{3} \times 600} $$ | 1924.5 |

According to Table 50, the OCPDs can be sized to:

| Protection Type | Primary OCPD Size | Secondary OCPD Size |
|-----------------|-------------------|---------------------|
| Fuses           | 41.84 $$\cdot$$ 3.00 = 125.5 A | 1924.5 $$\cdot$$ 2.50 = 4811.25 A |
| Circuit Breaker | 41.84 $$\cdot$$ 6.00 = 251.02 A | 1924.5 $$\cdot$$ 2.50 = 4811.25 A |

**Result:** 125 A rated fuse or 250 A rated circuit breaker (rounded to standard per Table 13).

---

## Example 2 — Transformer Rated Under 750 V, Non Dry-Type

Consider an oil-filled transformer with the following nameplate. Calculate the fuse and circuit breaker sizes for primary overcurrent protection.

| Parameter         | Value  |
|-------------------|--------|
| Rating            | 75 kVA |
| Primary Voltage   | 600 V  |
| Secondary Voltage | 208 V  |
| Phase             | 3      |
| Frequency         | 60 Hz  |

The FLCs can be calculated as:

| Side      | Calculation | FLA (A) |
|-----------|-------------|---------|
| Primary   | $$ \frac{75 \times 10^3}{\sqrt{3} \times 600} $$ | 72.17 |
| Secondary | $$ \frac{75 \times 10^3}{\sqrt{3} \times 208} $$ | 208.18 |

As per Rule 26-252, the primary OCPD can be sized to:

| Protection Type      | OESC Multiplier | Primary OCPD Size | Secondary OCPD Size |
|----------------------|-----------------|-------------------|---------------------|
| Fuse/Circuit Breaker | 1.50 | 72.17 $$\cdot$$ 1.50 = 108.25 A | 208.18 $$\cdot$$ 1.50 = 312.27 A |

**Result:** 100 A rated fuse or circuit breaker (rounded to standard per Table 13).

---

## Example 3 — Transformer Rated Under 750 V, Dry-Type

Consider a dry-type transformer with the following nameplate. Calculate the fuse and circuit breaker sizes for the overcurrent protection devices.

| Parameter         | Value  |
|-------------------|--------|
| Rating            | 75 kVA |
| Primary Voltage   | 600 V  |
| Secondary Voltage | 208 V  |
| Phase             | 3      |
| Frequency         | 60 Hz  |

The FLCs can be calculated as:

| Side          | Calculation | Result (A) |
|---------------|-------------|------------|
| Primary FLA   | $$ \frac{75 \times 10^3}{\sqrt{3} \times 600} $$ | 72.17 |
| Secondary FLA | $$ \frac{75 \times 10^3}{\sqrt{3} \times 208} $$ | 208.18 |

As per Rule 26-254, the primary OCPD can be sized to:

| Protection Type        | OESC Multiplier | Primary OCPD Size | Secondary OCPD Size |
|------------------------|-----------------|-------------------|---------------------|
| Overcurrent Protection | 1.25 | 72.17 $$\cdot$$ 1.25 = 90.21 A | 208.18 $$\cdot$$ 1.25 = 260.22 A |

**Result:** 90 A rated fuse or circuit breaker (rounded to standard per Table 13).

---

## Appendix

### Related Knowledge Files

[Knowledge File — OESC: Section 26 Installation of Electrical Equipment](https://jnepeng.sharepoint.com/:b:/s/JNEElectricalPortalTeams/IQAr5W2CWdUbQb-26XCqmNYqAfifLPPITzkxySXkq7Q7sGQ?e=ZFTBIb)<br/>
[Design Basis — Calculations: Transformer Protection Calculation](https://jnepeng.sharepoint.com/:w:/s/JNEElectricalPortalTeams/IQDKl-wkmkujQb_ZfZKZZwfDAXYYVGNWrV_TkJmXlw8w2Ac?e=BAApqB)

### Related OESC Rules

Rule 8-104 — Maximum circuit loading<br/>
Rule 26-250 — Overcurrent protection, transformers rated >750 V<br/>
Rule 26-252 — Overcurrent protection, transformers rated <750 V, other than dry type<br/>
Rule 26-254 — Overcurrent protection, dry-type transformers rated <750 V

### Related OESC Tables

Table 13 — Standard Overcurrent Device Ratings<br/>
Table 50 — Overcurrent protection, transformers rated > 750V
