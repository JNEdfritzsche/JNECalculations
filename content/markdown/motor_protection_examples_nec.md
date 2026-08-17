## Overview

This section walks through worked examples for calculating motor branch-circuit short-circuit and ground-fault protective device (BCSCGFP) sizing under the National Electrical Code (NEC) 2026. Sizing parameters are governed by **NEC Article 430.52 and Table 430.52(C)(1)**.

The overcurrent device setting formula is:

$$ I_{\text{BCSCGFP}} = k \cdot I_{\text{FLC}} $$

Where $k$ is the multiplier from NEC Table 430.52(C)(1), and $I_{\text{FLC}}$ is the standard FLC from standard motor tables (not actual nameplate current). Sizing allows rounding up to the next standard rating per NEC 430.52(C)(1) Exception No. 1.

Standard ratings are as listed in NEC 240.6(A).

---

## Example 1 — DC Motor (Constant Voltage)

A motor has the following nameplate parameters:

| Parameter | Value |
|-----------|-------|
| Motor Power | 1½ HP |
| Voltage   | 180 VDC |
| $I_{\text{FLC}}$ (Table 430.247) | 8.3 A |

According to NEC Table 430.52(C)(1), for DC motors (constant voltage):
- Dual-Element (Time-Delay) Fuse multiplier $k_{\text{TD}}$ = **150%**
- Non-Time-Delay Fuse multiplier $k_{\text{NTD}}$ = **150%**
- Inverse-Time Circuit Breaker multiplier $k_{\text{CB}}$ = **150%**

The DC row also caps an instantaneous-trip breaker at **250%**, well below the 800% allowed for ac motors.

Rounding up to the next standard rating (per Exception 1):

$$ I_{\text{TD}} = 8.3 \text{ A} \times 1.50 = 12.45 \text{ A} \quad \Rightarrow \text{Select standard 15 A fuse} $$

$$ I_{\text{NTD}} = 8.3 \text{ A} \times 1.50 = 12.45 \text{ A} \quad \Rightarrow \text{Select standard 15 A fuse} $$

$$ I_{\text{CB}} = 8.3 \text{ A} \times 1.50 = 12.45 \text{ A} \quad \Rightarrow \text{Select standard 15 A circuit breaker} $$

---

## Example 2 — AC Motor; 1φ

A motor has the following nameplate parameters:

| Parameter | Value |
|-----------|-------|
| Motor Power | 10 HP |
| Voltage   | 230 V |
| $I_{\text{FLC}}$ (Table 430.248) | 50 A |
| Phase     | 1 |

According to NEC Table 430.52(C)(1), for single-phase AC motors:
- $k_{\text{TD}}$ = **175%**
- $k_{\text{NTD}}$ = **300%**
- $k_{\text{CB}}$ = **250%**

Rounding up to the next standard rating:

$$ I_{\text{TD}} = 50 \text{ A} \times 1.75 = 87.5 \text{ A} \quad \Rightarrow \text{Select standard 90 A fuse} $$

$$ I_{\text{NTD}} = 50 \text{ A} \times 3.00 = 150.0 \text{ A} \quad \Rightarrow \text{Select standard 150 A fuse} $$

$$ I_{\text{CB}} = 50 \text{ A} \times 2.50 = 125.0 \text{ A} \quad \Rightarrow \text{Select standard 125 A circuit breaker} $$

---

## Example 3 — AC Motor; 3φ; Squirrel-Cage (Full-Voltage, Autotransformer, or Star-Delta Start)

A motor has the following nameplate parameters:

| Parameter | Value |
|-----------|-------|
| Motor Power | 75 HP |
| Voltage   | 575 V |
| $I_{\text{FLC}}$ (Table 430.250) | 77 A |
| Phase     | 3 |

Table 430.250 publishes no 600 V column, so a 600 V nominal system is read from the **575 V** column.

According to NEC Table 430.52(C)(1), ac polyphase motors other than wound-rotor are sized using the standard maximum limits:
- $k_{\text{TD}}$ = **175%**
- $k_{\text{NTD}}$ = **300%**
- $k_{\text{CB}}$ = **250%**

*(Note: Sizing limits do not decrease for larger starting currents or starter types, unlike other codes).*

Rounding up to the next standard rating:

$$ I_{\text{TD}} = 77 \text{ A} \times 1.75 = 134.75 \text{ A} \quad \Rightarrow \text{Select standard 150 A fuse} $$

$$ I_{\text{NTD}} = 77 \text{ A} \times 3.00 = 231.0 \text{ A} \quad \Rightarrow \text{Select standard 250 A fuse} $$

$$ I_{\text{CB}} = 77 \text{ A} \times 2.50 = 192.5 \text{ A} \quad \Rightarrow \text{Select standard 200 A circuit breaker} $$

---

## Example 4 — AC Motor; 3φ, Squirrel-Cage

A motor has the following nameplate parameters:

| Parameter | Value |
|-----------|-------|
| Motor Power | 20 HP |
| Voltage   | 460 V |
| $I_{\text{FLC}}$ (Table 430.250) | 27 A |
| Phase     | 3 |

According to NEC Table 430.52(C)(1):
- $k_{\text{TD}}$ = **175%**
- $k_{\text{NTD}}$ = **300%**
- $k_{\text{CB}}$ = **250%**

Rounding up to the next standard rating:

$$ I_{\text{TD}} = 27 \text{ A} \times 1.75 = 47.25 \text{ A} \quad \Rightarrow \text{Select standard 50 A fuse} $$

$$ I_{\text{NTD}} = 27 \text{ A} \times 3.00 = 81.0 \text{ A} \quad \Rightarrow \text{Select standard 90 A fuse} $$

$$ I_{\text{CB}} = 27 \text{ A} \times 2.50 = 67.5 \text{ A} \quad \Rightarrow \text{Select standard 70 A circuit breaker} $$

---

## Example 5 — AC Motor; 3φ; Squirrel-Cage; High-Efficiency Option

A motor has the following nameplate parameters:

| Parameter | Value |
|-----------|-------|
| Motor Power | 50 HP |
| Voltage   | 460 V |
| $I_{\text{FLC}}$ (Table 430.250) | 65 A |
| Phase     | 3 |
| Design    | B, energy-efficient |

A Design B energy-efficient motor keeps the same fuse and inverse-time breaker multipliers as any other polyphase motor. The one column that changes is the **instantaneous-trip** limit, which Table 430.52(C)(1) raises from 800% to **1100%**:
- $k_{\text{TD}}$ = **175%**
- $k_{\text{NTD}}$ = **300%**
- $k_{\text{CB}}$ = **250%**
- $k_{\text{inst}}$ = **1100%** (800% for other motors)

Rounding up to the next standard rating:

$$ I_{\text{TD}} = 65 \text{ A} \times 1.75 = 113.75 \text{ A} \quad \Rightarrow \text{Select standard 125 A fuse} $$

$$ I_{\text{NTD}} = 65 \text{ A} \times 3.00 = 195.0 \text{ A} \quad \Rightarrow \text{Select standard 200 A fuse} $$

$$ I_{\text{CB}} = 65 \text{ A} \times 2.50 = 162.5 \text{ A} \quad \Rightarrow \text{Select standard 175 A circuit breaker} $$

Where 1100% will not start the motor, 430.52(C)(3) Exception No. 1 permits up to 1700% of FLC for a Design B energy-efficient motor.

---

## Example 6 — AC Motor; 3φ, Wound Rotor

A motor has the following nameplate parameters:

| Parameter | Value |
|-----------|-------|
| Motor Power | 125 HP |
| Voltage   | 575 V |
| $I_{\text{FLC}}$ (Table 430.250) | 125 A |
| Phase     | 3 |

According to NEC Table 430.52(C)(1), for Wound Rotor motors:
- $k_{\text{TD}}$ = **150%**
- $k_{\text{NTD}}$ = **150%**
- $k_{\text{CB}}$ = **150%**

Rounding up to the next standard rating:

$$ I_{\text{TD}} = 125 \text{ A} \times 1.50 = 187.5 \text{ A} \quad \Rightarrow \text{Select standard 200 A fuse} $$

$$ I_{\text{NTD}} = 125 \text{ A} \times 1.50 = 187.5 \text{ A} \quad \Rightarrow \text{Select standard 200 A fuse} $$

$$ I_{\text{CB}} = 125 \text{ A} \times 1.50 = 187.5 \text{ A} \quad \Rightarrow \text{Select standard 200 A circuit breaker} $$

---

## Appendix

<!-- ### Related Knowledge Files

[Design Basis — Calculations: Motor Protection Sizing]<br/>
[Knowledge File — NEC: Article 430 Motors, Motor Circuits, and Controllers] -->

### Related NEC Articles

Section 240.6 — Standard Overcurrent Device Ratings<br/>
Section 430.52 — Rating or Setting for Individual Motor Circuit

### Related NEC Tables

Table 430.52(C)(1) — Maximum Rating of Motor Branch-Circuit Protective Devices<br/>
Table 430.247 — DC Motor Full-Load Currents<br/>
Table 430.248 — Single-Phase AC Motor Full-Load Currents<br/>
Table 430.250 — Three-Phase AC Motor Full-Load Currents