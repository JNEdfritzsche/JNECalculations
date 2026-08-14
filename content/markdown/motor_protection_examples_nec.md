## Overview

This section walks through worked examples for calculating motor branch-circuit short-circuit and ground-fault protective device (BCSCGFP) sizing under the National Electrical Code (NEC) 2026. Sizing parameters are governed by **NEC Article 430.52 and Table 430.52**.

The overcurrent device setting formula is:

$$ I_{\text{BCSCGFP}} = k \cdot I_{\text{FLC}} $$

Where $k$ is the multiplier from NEC Table 430.52, and $I_{\text{FLC}}$ is the standard FLC from standard motor tables (not actual nameplate current). Sizing allows rounding up to the next standard rating per NEC 430.52(C)(1) Exception No. 1.

Standard ratings are as listed in NEC 240.6(A).

---

## Example 1 — DC Motor (Constant Speed)

A motor has the following nameplate parameters:

| Parameter | Value |
|-----------|-------|
| Voltage   | 180 VDC |
| $I_{\text{FLC}}$ (Table 430.247) | 9.5 A |

According to NEC Table 430.52, for DC motors (constant speed):
- Dual-Element (Time-Delay) Fuse multiplier $k_{\text{TD}}$ = **150%**
- Non-Time-Delay Fuse multiplier $k_{\text{NTD}}$ = **150%**
- Inverse-Time Circuit Breaker multiplier $k_{\text{CB}}$ = **150%**

Rounding up to the next standard rating (per Exception 1):

$$ I_{\text{TD}} = 9.5 \text{ A} \times 1.50 = 14.25 \text{ A} \quad \Rightarrow \text{Select standard 15 A fuse} $$

$$ I_{\text{NTD}} = 9.5 \text{ A} \times 1.50 = 14.25 \text{ A} \quad \Rightarrow \text{Select standard 15 A fuse} $$

$$ I_{\text{CB}} = 9.5 \text{ A} \times 1.50 = 14.25 \text{ A} \quad \Rightarrow \text{Select standard 15 A circuit breaker} $$

---

## Example 2 — AC Motor; 1φ

A motor has the following nameplate parameters:

| Parameter | Value |
|-----------|-------|
| Voltage   | 230 V |
| $I_{\text{FLC}}$ (Table 430.248) | 62 A |
| Phase     | 1 |

According to NEC Table 430.52, for single-phase AC motors:
- $k_{\text{TD}}$ = **175%**
- $k_{\text{NTD}}$ = **300%**
- $k_{\text{CB}}$ = **250%**

Rounding up to the next standard rating:

$$ I_{\text{TD}} = 62 \text{ A} \times 1.75 = 108.5 \text{ A} \quad \Rightarrow \text{Select standard 110 A fuse} $$

$$ I_{\text{NTD}} = 62 \text{ A} \times 3.00 = 186.0 \text{ A} \quad \Rightarrow \text{Select standard 200 A fuse} $$

$$ I_{\text{CB}} = 62 \text{ A} \times 2.50 = 155.0 \text{ A} \quad \Rightarrow \text{Select standard 175 A circuit breaker} $$

---

## Example 3 — AC Motor; 3φ; Squirrel-Cage (Full-Voltage, Autotransformer, or Star-Delta Start)

A motor has the following nameplate parameters:

| Parameter | Value |
|-----------|-------|
| Voltage   | 600 V |
| $I_{\text{FLC}}$ (Table 430.250) | 90 A |
| Phase     | 3 |

According to NEC Table 430.52, all standard 3-phase squirrel-cage motors (except Design B, C, or D under specific high-efficiency guidelines) are sized using standard maximum limits:
- $k_{\text{TD}}$ = **175%**
- $k_{\text{NTD}}$ = **300%**
- $k_{\text{CB}}$ = **250%**

*(Note: Sizing limits do not decrease for larger starting currents or starter types, unlike other codes).*

Rounding up to the next standard rating:

$$ I_{\text{TD}} = 90 \text{ A} \times 1.75 = 157.5 \text{ A} \quad \Rightarrow \text{Select standard 175 A fuse} $$

$$ I_{\text{NTD}} = 90 \text{ A} \times 3.00 = 270.0 \text{ A} \quad \Rightarrow \text{Select standard 300 A fuse} $$

$$ I_{\text{CB}} = 90 \text{ A} \times 2.50 = 225.0 \text{ A} \quad \Rightarrow \text{Select standard 225 A circuit breaker} $$

---

## Example 4 — AC Motor; 3φ, Squirrel-Cage

A motor has the following nameplate parameters:

| Parameter | Value |
|-----------|-------|
| Voltage   | 460 V |
| $I_{\text{FLC}}$ (Table 430.250) | 25 A |
| Phase     | 3 |

According to NEC Table 430.52:
- $k_{\text{TD}}$ = **175%**
- $k_{\text{NTD}}$ = **300%**
- $k_{\text{CB}}$ = **250%**

Rounding up to the next standard rating:

$$ I_{\text{TD}} = 25 \text{ A} \times 1.75 = 43.75 \text{ A} \quad \Rightarrow \text{Select standard 45 A fuse} $$

$$ I_{\text{NTD}} = 25 \text{ A} \times 3.00 = 75.0 \text{ A} \quad \Rightarrow \text{Select standard 75 A fuse} $$ (which is standard)

$$ I_{\text{CB}} = 25 \text{ A} \times 2.50 = 62.5 \text{ A} \quad \Rightarrow \text{Select standard 70 A circuit breaker} $$

---

## Example 5 — AC Motor; 3φ; Squirrel-Cage; High-Efficiency Option

A motor has the following nameplate parameters:

| Parameter | Value |
|-----------|-------|
| Voltage   | 460 V |
| $I_{\text{FLC}}$ (Table 430.250) | 72 A |
| Phase     | 3 |

According to NEC Table 430.52:
- $k_{\text{TD}}$ = **175%**
- $k_{\text{NTD}}$ = **300%**
- $k_{\text{CB}}$ = **250%**

Rounding up to the next standard rating:

$$ I_{\text{TD}} = 72 \text{ A} \times 1.75 = 126.0 \text{ A} \quad \Rightarrow \text{Select standard 150 A fuse} $$

$$ I_{\text{NTD}} = 72 \text{ A} \times 3.00 = 216.0 \text{ A} \quad \Rightarrow \text{Select standard 225 A fuse} $$

$$ I_{\text{CB}} = 72 \text{ A} \times 2.50 = 180.0 \text{ A} \quad \Rightarrow \text{Select standard 200 A circuit breaker} $$

---

## Example 6 — AC Motor; 3φ, Wound Rotor

A motor has the following nameplate parameters:

| Parameter | Value |
|-----------|-------|
| Voltage   | 575 V |
| $I_{\text{FLC}}$ (Table 430.250) | 127 A |
| Phase     | 3 |

According to NEC Table 430.52, for Wound Rotor motors:
- $k_{\text{TD}}$ = **150%**
- $k_{\text{NTD}}$ = **150%**
- $k_{\text{CB}}$ = **150%**

Rounding up to the next standard rating:

$$ I_{\text{TD}} = 127 \text{ A} \times 1.50 = 190.5 \text{ A} \quad \Rightarrow \text{Select standard 200 A fuse} $$

$$ I_{\text{NTD}} = 127 \text{ A} \times 1.50 = 190.5 \text{ A} \quad \Rightarrow \text{Select standard 200 A fuse} $$

$$ I_{\text{CB}} = 127 \text{ A} \times 1.50 = 190.5 \text{ A} \quad \Rightarrow \text{Select standard 200 A circuit breaker} $$

---

## Appendix

<!-- ### Related Knowledge Files

[Design Basis — Calculations: Motor Protection Sizing]<br/>
[Knowledge File — NEC: Article 430 Motors, Motor Circuits, and Controllers] -->

### Related NEC Articles

Section 240.6 — Standard Overcurrent Device Ratings<br/>
Section 430.52 — Rating or Setting for Individual Motor Circuit

### Related NEC Tables

Table 240.6(A) — Standard Ampere Ratings for Fuses and Circuit Breakers<br/>
Table 430.52 — Maximum Rating of Motor Branch-Circuit Protective Devices<br/>
Table 430.247 — DC Motor Full-Load Currents<br/>
Table 430.248 — Single-Phase AC Motor Full-Load Currents<br/>
Table 430.250 — Three-Phase AC Motor Full-Load Currents