## Overview

This section walks through worked examples for calculating transformer primary and secondary full-load currents. The key distinction is the formula used; single-phase and three-phase transformers differ by a factor of √3. For theory, refer to the theory tab.

The formulas are:

$$\text{Single-phase:} \quad I = \frac{S}{V} \qquad \text{Three-phase:} \quad I = \frac{S}{\sqrt{3} \cdot V}$$

Where $S$ is the apparent power (VA) and $V$ is the line-to-line voltage (V).

---

## Example 1 — Single-Phase Step-Down Transformer

**50 kVA | 1φ | 600 V primary / 240 V secondary**

For single-phase, current is simply apparent power divided by voltage — no √3 factor.

| Parameter | Value |
|-----------|-------|
| Apparent power $S$ | 50 kVA = 50,000 VA |
| Phases | 1φ |
| Primary voltage $V_{\text{pri}}$ | 600 V |
| Secondary voltage $V_{\text{sec}}$ | 240 V |

**Primary full-load current:**

$$I_{\text{pri}} = \frac{S}{V_{\text{pri}}} = \frac{50{,}000}{600} = 83.33 \text{ A}$$

**Secondary full-load current:**

$$I_{\text{sec}} = \frac{S}{V_{\text{sec}}} = \frac{50{,}000}{240} = 208.33 \text{ A}$$

**Turns ratio:**

$$\frac{V_1}{V_2} = \frac{600}{240} = 2.5$$

**Result: I_pri = 83.33 A &nbsp;|&nbsp; I_sec = 208.33 A &nbsp;|&nbsp; Turns ratio = 2.5**

---

## Example 2 — Three-Phase Step-Down Transformer

**300 kVA | 3φ | 13.8 kV primary / 600 V secondary**

For three-phase, the √3 factor appears in the denominator because power is distributed across three phases. Note that voltages used are always **line-to-line**.

| Parameter | Value |
|-----------|-------|
| Apparent power $S$ | 300 kVA = 300,000 VA |
| Phases | 3φ |
| Primary voltage $V_{\text{pri}}$ | 13,800 V |
| Secondary voltage $V_{\text{sec}}$ | 600 V |

**Primary full-load current:**

$$I_{\text{pri}} = \frac{S}{\sqrt{3} \cdot V_{\text{pri}}} = \frac{300{,}000}{\sqrt{3} \times 13{,}800} = \frac{300{,}000}{23{,}899} = 12.55 \text{ A}$$

**Secondary full-load current:**

$$I_{\text{sec}} = \frac{S}{\sqrt{3} \cdot V_{\text{sec}}} = \frac{300{,}000}{\sqrt{3} \times 600} = \frac{300{,}000}{1{,}039.2} = 288.68 \text{ A}$$

**Turns ratio:**

$$\frac{V_1}{V_2} = \frac{13{,}800}{600} = 23$$

**Result: I_pri = 12.55 A &nbsp;|&nbsp; I_sec = 288.68 A &nbsp;|&nbsp; Turns ratio = 23**

---

## Appendix

### Related OESC Rules

Rule 26-250 — Transformer Feeder Overcurrent Protection<br/>
Rule 26-256 — Transformer Secondary Overcurrent Protection<br/>
