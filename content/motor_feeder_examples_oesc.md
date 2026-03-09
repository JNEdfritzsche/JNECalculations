## Overview

This section walks through worked examples for calculating motor full-load amps (FLA) from nameplate data. The formula varies by system type — the √3 factor appears for three-phase, and cosθ drops out for DC. For theory and conductor/overcurrent protection sizing from FLA, refer to the theory tab.

The formulas are:

$$\text{Single-phase AC:} \quad I_{\text{FLA}} = \frac{HP \times 745.7}{V \cdot \cos\theta \cdot \eta}$$

$$\text{Three-phase AC:} \quad I_{\text{FLA}} = \frac{HP \times 745.7}{\sqrt{3} \cdot V \cdot \cos\theta \cdot \eta}$$

$$\text{DC:} \quad I_{\text{FLA}} = \frac{HP \times 745.7}{V \cdot \eta}$$

For continuous duty motors, the conductor ampacity target applies a **125% service factor**:

$$I_{\text{target}} = 1.25 \times I_{\text{FLA}}$$

---

## Example 1 — Single-Phase AC Motor

**230 V | 1φ | 10 HP | cosθ = 0.9 | η = 75% | Continuous duty | SF = 1.25**

| Parameter | Value |
|-----------|-------|
| Motor power | 10 HP = 7,457 W |
| Voltage $V$ | 230 V |
| Power factor $\cos\theta$ | 0.9 |
| Efficiency $\eta$ | 0.75 |

$$I_{\text{FLA}} = \frac{7{,}457}{230 \times 0.9 \times 0.75} = \frac{7{,}457}{155.25} = 48.03 \text{ A}$$

$$I_{\text{target}} = 1.25 \times 48.03 = 60.04 \text{ A}$$

**Result: I_FLA = 48.03 A &nbsp;|&nbsp; Conductor ampacity target = 60.04 A**

---

## Example 2 — Three-Phase AC Motor

**460 V | 3φ | 40 HP | cosθ = 0.9 | η = 80% | Continuous duty | SF = 1.25**

For three-phase, the √3 factor is added to the denominator alongside voltage.

| Parameter | Value |
|-----------|-------|
| Motor power | 40 HP = 29,828 W |
| Voltage $V$ | 460 V |
| Power factor $\cos\theta$ | 0.9 |
| Efficiency $\eta$ | 0.80 |

$$I_{\text{FLA}} = \frac{29{,}828}{\sqrt{3} \times 460 \times 0.9 \times 0.80} = \frac{29{,}828}{573.96} = 51.97 \text{ A}$$

$$I_{\text{target}} = 1.25 \times 51.97 = 64.96 \text{ A} \approx 65 \text{ A}$$

**Result: I_FLA = 51.97 A &nbsp;|&nbsp; Conductor ampacity target = 65 A**

---

## Example 3 — DC Motor

**500 V | DC | 100 HP | η = 92% | Continuous duty | SF = 1.25**

For DC, there is no reactive power component, so cosθ = 1 and drops out of the formula entirely.

| Parameter | Value |
|-----------|-------|
| Motor power | 100 HP = 74,570 W |
| Voltage $V$ | 500 V |
| Power factor $\cos\theta$ | N/A (DC) |
| Efficiency $\eta$ | 0.92 |

$$I_{\text{FLA}} = \frac{74{,}570}{500 \times 0.92} = \frac{74{,}570}{460} = 162.1 \text{ A}$$

$$I_{\text{target}} = 1.25 \times 162.1 = 202.6 \text{ A}$$

**Result: I_FLA = 162.1 A &nbsp;|&nbsp; Conductor ampacity target = 202.6 A**

---

## Appendix

### Related Knowledge Files

[Design Basis — Calculations: Motor Feeder](https://jnepeng.sharepoint.com/:w:/s/JNEElectricalPortalTeams/IQAJQj9NgJoFQZ1Cka91W7FrAU1C4cOQc2NbIUe-6dugX7o?e=4OlqCj)<br/>
[Knowledge File — OESC: Section 28 Motor and Generators](https://jnepeng.sharepoint.com/:b:/s/JNEElectricalPortalTeams/IQAXnWzLgtMmR61hoesUWqmpAXLI_p34pKUoeB9wE2W_eBs?e=cBCsY6)<br/>
[Knowledge File — Cable Sizing for a motor](https://jnepeng.sharepoint.com/:w:/s/JNEElectricalPortalTeams/IQAeH5a2w33eToJmvy6SYiWPAb36iBHMkGGKajJcOedagLo?e=5mL84s)

### Related OESC Rules

Rule 4-004 — Conductor ampacity<br/>
Rule 4-006 — Temperature limitations<br/>
Rule 8-102 — Voltage drop <br/>
Rule 28-104 — Motor supply conductor insulation temperature rating & ampacity<br/>
Rule 28-106 — Conductor sizing:  Single motor branch circuit<br/>
Rule 28-108 — Conductor sizing:  Multiple motors branch circuit<br/>
Rule 28-110 — Conductor sizing: Feeder <br/>
Rule 28-400 — Motor Undervoltage

## Related OESC Tables

Tables 27 — Motor Service Duties<br/>
Tables 37 — Motor Insulation Class Rating<br/>
Table D2 — DC motor Full Load Ampacity<br/>
Table 44 — 3Φ Motor FLA at 100% PF<br/>
Table 45 — 1Φ Motor FLA at 100% PF
