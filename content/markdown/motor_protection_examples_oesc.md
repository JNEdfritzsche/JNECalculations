## Overview

This section walks through worked examples for sizing motor overcurrent protection devices under OESC Rule 28-200 and Table 29. The goal is to demonstrate individual motor branch circuit OCPD selection and feeder OCPD sizing for multiple motors. For theory and device type selection, refer to the theory tab.

The general branch circuit sizing formula is:

$$I_{\text{target}} = I_{\text{FLC}} \times \text{factor (Table 29)}$$

Select the **next lower** standard fuse size from Table 13 if the calculated value does not correspond to a standard size.

For a feeder supplying multiple motors, upsize the largest FLC motor by its Table 29 factor and add the remaining motors at nominal FLC:

$$I_{\text{feeder}} = (I_{\text{largest}} \times \text{factor}) + \sum I_{\text{remaining, nominal}}$$

---

## Example 1 — Three-Motor Branch Circuit and Feeder OCPD Sizing

**3× time-delay fuses | OESC Rule 28-200 & 28-202 | Table 29**

Three motors share a common feeder, each with individual branch circuit overcurrent protection. All three use time-delay fuses (Table 29 factor = 1.75).

| Motor | Fuse Type | FLC |
|-------|-----------|-----|
| $M_1$ | Time-delay | 62 A |
| $M_2$ | Time-delay | 27 A |
| $M_3$ | Time-delay | 11 A |

**Individual branch circuit OCPD sizing (Table 29, time-delay factor = 1.75):**

$$M_1: \quad 62 \times 1.75 = 108.5 \text{ A} \quad \Rightarrow \text{Select } \mathbf{100 \text{ A}} \text{ (next lower standard, Table 13)}$$

$$M_2: \quad 27 \times 1.75 = 47.25 \text{ A} \quad \Rightarrow \text{Select } \mathbf{45 \text{ A}}$$

$$M_3: \quad 11 \times 1.75 = 19.25 \text{ A} \quad \Rightarrow \text{Select } \mathbf{15 \text{ A}}$$

**Feeder OCPD sizing — three device type options (upsize $M_1$, add $M_2$ and $M_3$ at nominal FLC):**

| Device Type | Table 29 Factor | Calculation | Feeder Target | Standard Rating |
|-------------|----------------|-------------|---------------|----------------|
| Non-time-delay fuse | 3.00 | (62 × 3.00) + 27 + 11 | 224 A | **200 A** |
| Time-delay fuse | 1.75 | (62 × 1.75) + 27 + 11 | 146.5 A | **125 A** |
| Circuit breaker | 2.50 | (62 × 2.50) + 27 + 11 | 193 A | **175 A** |

**Result: Branch circuits — M1: 100 A fuse, M2: 45 A fuse, M3: 15 A fuse | Feeder — 200 A (non-TD) / 125 A (TD) / 175 A (CB)**

---

## Appendix

### Related Knowledge Files

[Design Basis — Calculations: Motor Protection](https://jnepeng.sharepoint.com/:w:/s/JNEElectricalPortalTeams/IQCXVHdd4QCvQJZdJh_U0PmVAUMoccLRBfe8SBMf7WTRXpo?e=oWNutN)<br/>
[Knowledge File - OESC: Section 28 Motor and Generators](https://jnepeng.sharepoint.com/:b:/s/JNEElectricalPortalTeams/IQAXnWzLgtMmR61hoesUWqmpAXLI_p34pKUoeB9wE2W_eBs?e=cBCsY6)

### Related OESC Rules

Rule 28-200 — Branch circuit overcurrent protection<br/>
Rule 28-202 — Feeder circuit overcurrent protection<br/>
Rule 28-210 — Instantaneous-trip circuit breakers<br/>
Rule 28-306 — Trip selection of overload devices<br/>
Rule 28-604 — Location of disconnecting means

### Related OESC Tables

Table 13 — Overcurrent devices; conductor protection<br/>
Table 29 — Overcurrent devices; motor branch circuits<br/>
Table 25 — Overcurrent devices; trip coils for motors<br/>
Table D16 — Conductors, fuses, circuit breakers for motor overload and overcurrent protection
