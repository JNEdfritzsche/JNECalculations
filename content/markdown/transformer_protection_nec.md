## Overview

Select transformer overcurrent protection (breaker/fuses) in accordance with **NEC Article 450** so the device ratings meet the code allowances and protect the transformer.

---

## Scope & Key References

Focus on NEC 450.3 and tables 450.3(A) / 450.3(B) depending on voltage class. Also consult NEC 240.6(A) for standard ratings and device availability rules used when rounding to standard/commercial sizes.

---

## Assumptions

- Ambient temperature: **40°C**
- Conductors: **75°C copper**, free-air routing
- Max cable length: **50 m**
- Transformer impedance: **≤ 6%** (common example used in the template)
- Installation location classification: **Any location** vs **Supervised location** (affects table choices)

---

## Method / Practical approach

1. Use nameplate FLA when available; otherwise compute FLA for primary and secondary using the 3Φ formula below.
2. Determine whether transformer is **over 1000 V nominal** (use **Table 450.3(A)**) or **1000 V nominal or less** (use **Table 450.3(B)**).
3. Determine whether the installation is **Any location** or a **Supervised location** (this can change allowable multipliers/limits).
4. Apply the table-based multipliers/limits to find allowable OCPD ratings (primary-only or primary+secondary schemes, where applicable).
5. Apply the table notes on rounding to standard/commercial device ratings and on how multiple secondary devices may be grouped.

---

## Rated current formula (3Φ)

$$ I_L=\frac{S}{\sqrt{3}\,V_L} $$

Use consistent units (e.g., **S in VA with V in V**, or **S in kVA with V in kV**) so the result is in amperes.

$$ I_{pri}=\frac{S}{\sqrt{3}\,V_{pri}} $$
$$ I_{sec}=\frac{S}{\sqrt{3}\,V_{sec}} $$

---

## NEC 450.3 structure

**450.3(A)** — Transformers **over 1000 V nominal**: overcurrent protection per Table 450.3(A).
**450.3(B)** — Transformers **1000 V nominal or less**: overcurrent protection per Table 450.3(B).
**450.3(C)** — Voltage (potential) transformers: protection requirements depend on application.

---

## Table 450.3 notes that materially affect design

**Table 450.3 Note 1 — Rounding to standard / commercially available sizes**

- If the required fuse rating or breaker setting does not correspond to a standard value, a higher rating/setting is permitted provided it does not exceed:
  - the **next higher standard rating/setting** for devices **1000 V and below**, or
  - the **next higher commercially available rating/setting** for devices **over 1000 V**.

**Table 450.3 Note 2 — Multiple secondary devices (when secondary OCPD is required)**

- The secondary OCPD is permitted to consist of **not more than six** circuit breakers, or **six sets of fuses**, **grouped in one location**.
- Where multiple devices are used, the **sum of device ratings** shall not exceed the allowed value of a **single** overcurrent device.
- If **both breakers and fuses** are used, the total of the device ratings shall not exceed that allowed for **fuses**.

**Supervised location (definition used in the calculation template)**

A supervised location is one where maintenance/supervision ensure **only qualified persons** monitor and service the transformer installation (qualified persons have safety training and are familiar with operation and hazards).

---

## Practical design notes

NEC transformer OCPD sizing focuses on protecting the transformer. Conductor protection still must be checked under Article 240. Coordination, relay protection for large transformers (e.g., ANSI 50/51 where applicable), and grounding/winding configuration should all be considered.
