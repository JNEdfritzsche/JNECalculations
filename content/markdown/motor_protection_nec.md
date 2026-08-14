## Overview

Once the motor feeder and branch conductors have been sized, the next step is the selection of motor protection devices. Motor circuit protection consists of three primary functions:

- Branch-circuit short-circuit and ground-fault protection (NEC 430 Part IV)
- Motor overload protection (NEC 430 Part III)
- Motor disconnecting means (NEC 430 Part IX)

---

## Branch-Circuit Short-Circuit and Ground-Fault Protection

Motor branch circuits pull a large inrush current during startup. Sizing overcurrent protective devices (OCPDs) is governed by **NEC Table 430.52** to prevent nuisance tripping while providing short-circuit protection. Sizing limits represent a maximum percentage of motor Table FLC:

- **Dual-Element (Time-Delay) Fuses**: Max **175%** of FLC
- **Non-Time-Delay Fuses**: Max **300%** of FLC
- **Inverse-Time Circuit Breakers**: Max **250%** of FLC
- **Instantaneous Trip Breakers**: Sized up to **800%** (and up to 1300% or 1700% for high-efficiency Design B/C/D motors per 430.52(C)(3)).

If the calculated maximum protective rating does not correspond to a standard rating, NEC 430.52(C)(1) Exception No. 1 permits rounding up to the next standard rating as listed in NEC 240.6(A).

### Feeder Overcurrent Protection (Multiple Motors)

Under **NEC 430.62(A)**, feeder short-circuit and ground-fault protection must protect the feeder conductors. The feeder protective device rating is calculated by taking the **maximum branch-circuit OCPD rating** of the largest motor in the group, and adding the FLCs of all other motors on the feeder. Note that under NEC rules, we **cannot** round up above this calculated maximum limit; we must select the next lower standard rating if the sum does not match standard OCPD sizes.

#### Sizing Example for Multiple Motors on a Single Feeder:

Assume the following three motors are connected to a single feeder:

| Motor No. | FLC (Table 430.250) | OCPD Type  | Table 430.52 Limit | Calculated Target | Standard OCPD Size (Round Up) |
| --------- | ------------------- | ---------- | ------------------ | ----------------- | ----------------------------- |
| $M_1$     | 62 A                | Time-Delay | 62 A × 1.75        | 108.5 A           | **110 A** (Standard Size)     |
| $M_2$     | 27 A                | Time-Delay | 27 A × 1.75        | 47.25 A           | **50 A** (Standard Size)      |
| $M_3$     | 11 A                | Time-Delay | 11 A × 1.75        | 19.25 A           | **20 A** (Standard Size)      |

To size the feeder OCPD supplying all three motors using Dual-Element Time-Delay Fuses (NEC 430.62(A)):

- Step 1: Identify the largest individual branch OCPD rating = **110 A** (for $M_1$).
- Step 2: Sum the remaining motor FLCs = 27 A + 11 A = **38 A**.
- Step 3: Feeder OCPD Limit = $110\text{ A} + 38\text{ A} = 148\text{ A}$.
- Step 4: Round **down** to the next standard fuse rating to remain below the 148A ceiling: **Select standard 125 A fuses** for the feeder disconnect.

To size the same feeder using an Inverse-Time Circuit Breaker:

- Step 1: Max branch CB for $M_1$ = $62\text{ A} \times 2.50 = 155\text{ A} \quad \Rightarrow \text{Select standard 175 A CB}$ (rounded up per Exception 1).
- Step 2: Sum remaining FLCs = 27 A + 11 A = **38 A**.
- Step 3: Feeder CB Limit = $175\text{ A} + 38\text{ A} = 213\text{ A}$.
- Step 4: Round **down** to the next standard circuit breaker rating: **Select standard 200 A CB** for the feeder.

---

## Overload Protection

Motor overload protection is intended to protect the motor windings from sustained overload and excessive heating. Overloads are sized based on the actual motor nameplate current rating (FLA), not Table FLC, per NEC 430.6(A)(2).

Under **NEC 430.32(A)(1)**, motors marked with a Service Factor (SF) of 1.15 or greater, or a Temperature Rise of 40°C or less, must have overload devices sized at a maximum of:

$$ I_{\text{overload, max}} = 1.25 \times I_{\text{nameplate FLA}} $$

For all other motors (such as those with SF 1.0 or SF 1.10), the limit is:

$$ I_{\text{overload, max}} = 1.15 \times I_{\text{nameplate FLA}} $$

---

## Disconnecting Means

Under NEC 430 Part IX, a disconnecting means must be provided for each motor controller and motor. The disconnecting means must be horse-power rated (equal to or greater than the motor rating) and located:

- **Within sight** from the controller and the motor, and the driven machinery. "Within sight" is defined in Article 100 as being visible and not more than 50 feet (15 meters) from each other.
- Or, if not within sight, the disconnecting means must be capable of being locked in the open position per NEC 110.25.

---

## Appendix

<!-- ### Related Knowledge Files

[Design Basis — Calculations: Motor Protection Sizing]<br/>
[Knowledge File — NEC: Article 430 Motors, Motor Circuits, and Controllers] -->

### Related NEC Articles

Section 240.6 — Standard Overcurrent Device Ratings<br/>
Section 430.32 — Continuous-Duty Motor Overload Protection<br/>
Section 430.52 — Rating or Setting for Individual Motor Circuit<br/>
Section 430.62 — Rating or Setting for Motor Feeder Protection<br/>
Section 430.102 — Location of Disconnecting Means

### Related NEC Tables

Table 240.6(A) — Standard Ampere Ratings for Fuses and Circuit Breakers<br/>
Table 430.52 — Maximum Rating of Motor Branch-Circuit Protective Devices<br/>
Table 430.250 — Three-Phase AC Motor Full-Load Currents
