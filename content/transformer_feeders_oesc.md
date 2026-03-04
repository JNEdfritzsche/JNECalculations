## Overview

Transformers are passive devices that can deliver their full rated output continuously, so feeder sizing is based on transformer nameplate kVA and voltage rather than downstream load diversity. For this reason, transformer feeders are generally treated as continuous and must be selected to remain within allowable temperature limits after applying ambient, grouping, installation, and termination corrections. This section will cover the main aspects of sizing transformer feeders as well as cover a general methodology.


<!-- Can just take this out
This section also highlights the role of the transformer feeder in overall system performance. Because the feeder sits at the interface between primary and secondary systems, its sizing and configuration affect grounding, fault behavior, and overcurrent protection coordination. The intent is to ensure that transformers are supplied in a conservative and predictable manner that supports long-term reliability and safe operation of the electrical system. -->

Transformers differ fundamentally from utilization equipment such as motors, heaters, or lighting loads:

- A transformer does not “draw” current based on demand in the same way a motor does
- It is capable of delivering its full rated current continuously
- It has no inherent current-limiting capability
- Overloads occur primarily as thermal stress, not immediate functional failure
- Because of this, the OESC treats the transformer feeder as part of the transformer system, not a supply conductor
- The feeder must therefore be sized assuming the transformer can and may operate at its nameplate rating indefinitely

## Design Methodology

### Base Current Determination
Conductor sizing begins with the transformer's nominal full-load current (FLC) on both sides of the transformer, it can be calculated using the following equation:

$$ I_{\text{Pri./Sec.}} = \frac{\text{VA}}{\sqrt{3} \cdot V_{\text{Pri./Sec.}}} $$

### Feeder Ampacity
To protect the feeder conductors supplying the transformer, they shall be sized at 125% of the FLA, as required by Rule 26-256.

$$ I = 1.25 \cdot I_{\text{Pri./Sec.}} $$

### Ampacity Corrections/Derating
After applying the above correction, conductor ampacity can be further corrected as neccesary, for:

- Ambient temperature  
- Number of current-carrying conductors  
- Conductor insulation temperature rating  
- Installation path (conduit, tray, free air, etc.)

<!--
### Protection and Performance Verification

Final design checks shall include:

- Coordination with upstream overcurrent protective devices  
- Voltage drop compliance  
- Adequate fault-clearing capability
-->

## Primary Feeder Sizing Example

Properly size the primary feeder of a transformer with the following information:

### Given Data

- Transformer rating: **75 kVA**  
- Primary voltage: **600 V**  
- Secondary voltage: **208 V**  
- System: **3-phase**  
- Ambient temperature: **40 °C**  
- Maximum conductor temperature: **75 °C**  
<!-- Not used
- Cable length: **50 m**-->
- Single Conductors

### Primary Adjusted Full-Load Current
From the information given, only the temperature correction can be applied.

$$  I_{\text{FLC}} = \frac{75{,}000}{\sqrt{3}\cdot 600} \approx 73.169 \text{A}  $$

From Table 5A, for 75°C Insulation @ 40°C Ambient, temperature correction factor is: *0.88*

$$  I_{\text{FLC}}' = \frac{1.25 \cdot I_{\text{prim}}}{0.88} = \frac{1.25 \cdot 73.169}{0.88} \approx 102.5 \text{A}  $$

### Conductor Size Selection

With out amapacity target of 102.5 A, we check Table 1 @ 75°C, and select **#4 AWG** as our feeder size.

---
## Appendix

### Related Knowledge Files:
[Knowledge File — OESC: Section 4 Conductors]() <br/>
[Knowledge File — OESC: Section 26 Installation of Electrical Equipment]()Knowledge File 26 <br/>
[Design Basis — Calculations: Transformer Feeder Calculation]()

### Related OESC Rules
Rule 26-256 — Conductor size for transformers <br/>

### Related OESC Tables
Table 1/2 — Single Conductor ampacities for Copper/Aluminum<br/>
Table 3/4 — Multi-Conductor ampacities for Copper/Aluminum <br/>

