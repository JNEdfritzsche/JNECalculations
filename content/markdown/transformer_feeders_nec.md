## Overview

Transformers are passive devices that can deliver their full rated output continuously, so feeder sizing is based on transformer nameplate kVA and voltage rather than downstream load diversity. For this reason, transformer feeders are treated as continuous loads and must be selected to remain within allowable temperature limits after applying ambient temperature, grouping, and termination corrections. This section covers the main aspects of sizing transformer feeders as well as a general methodology under the National Electrical Code (NEC) 2026.

Transformers differ fundamentally from utilization equipment such as motors, heaters, or lighting loads:

- A transformer does not "draw" current based on demand in the same way a motor does.
- It is capable of delivering its full rated current continuously.
- It has no inherent current-limiting capability.
- Overloads occur primarily as thermal stress, not immediate functional failure.
- Because of this, the NEC treats the transformer feeder as a supply circuit that must be sized assuming the transformer can and may operate at its nameplate rating continuously.
- Under NEC 215.2(A)(1) (for feeders) and NEC 210.19(A)(1) (for branch circuits), the allowable ampacity of the conductors must not be less than 125% of the continuous load.

---

## Design Methodology

### Base Current Determination

Conductor sizing begins with the transformer's nominal full-load current (FLC) on both sides of the transformer, which can be calculated using the following equation:

$$ I_{\text{Pri./Sec.}} = \frac{\text{VA}}{\sqrt{3} \cdot V_{\text{Pri./Sec.}}} $$

### Feeder Ampacity

To protect the feeder conductors supplying the transformer, they must be sized at 125% of the continuous FLC, as required by NEC 215.2(A)(1).

$$ I = 1.25 \cdot I_{\text{Pri./Sec.}} $$

### Ampacity Corrections/Derating

After applying the continuous load multiplier, conductor ampacity can be further corrected as necessary for:

- Ambient temperature (NEC Table 310.15(B)(1) or Table 310.15(B)(2))
- Number of current-carrying conductors in a raceway or cable (NEC Table 310.15(C)(1))
- Conductor insulation temperature rating (NEC Table 310.16 / Table 310.17)
- Termination temperature limits (NEC 110.14(C))

---

## Primary Feeder Sizing Example

Properly size the primary feeder of a transformer with the following information:

### Given Data

- Transformer rating: **75 kVA**
- Primary voltage: **600 V**
- Secondary voltage: **208 V**
- System: **3-phase**
- Ambient temperature: **40 °C**
- Maximum conductor temperature: **75 °C**
- Single Conductors in Free Air (NEC Table 310.17)

### Primary Adjusted Full-Load Current

First, calculate the primary full-load current:

$$  I_{\text{FLC}} = \frac{75{,}000}{\sqrt{3}\cdot 600} \approx 72.17 \text{A}  $$

To account for continuous duty, we apply the 125% factor:

$$ I_{\text{continuous}} = 1.25 \cdot 72.17 \approx 90.21 \text{A} $$

From the NEC Table 310.15(B)(1) ambient temperature correction factors (based on a 30°C reference), the correction factor for a 75°C rated conductor operating in a 40°C ambient is: *0.88*

To find the minimum allowable conductor ampacity before derating is applied, we divide the continuous target by the correction factor:

$$  I_{\text{target}} = \frac{1.25 \cdot I_{\text{FLC}}}{0.88} = \frac{90.21}{0.88} \approx 102.5 \text{A}  $$

### Conductor Size Selection

With our ampacity target of 102.5 A, we check NEC Table 310.17 (Ampacities of Single-Insulated Conductors in Free Air) under the 75°C column. We select **#4 AWG Copper** (rated at 125 A) as our feeder size. (#6 AWG Copper is only rated at 95 A, which is insufficient).

---

## Appendix

<!-- ### Related Knowledge Files

[Knowledge File — NEC: Article 310 Conductors for General Wiring]<br/>
[Knowledge File — NEC: Article 450 Transformers and Transformer Vaults]<br/>
[Design Basis — Calculations: Transformer Feeder Calculation] -->

### Related NEC Articles

Section 215.2 — Feeder Minimum Rating and Size<br/>
Section 240.4 — Protection of Conductors<br/>
Section 310.15 — Ampacity Correction and Adjustment Factors<br/>
Section 450.5 — Overcurrent Protection of Transformers

### Related NEC Tables

Table 310.16 — Ampacities of Insulated Conductors in Raceway, Cable, or Earth (up to 3 Current-Carrying Conductors)<br/>
Table 310.17 — Ampacities of Single-Insulated Conductors in Free Air<br/>
Table 310.15(B)(1) — Ambient Temperature Correction Factors (Celsius)
