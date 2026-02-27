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

Conductor sizing begins with the transformer's nominal full-load current (FLC) on both sides of the transformer, it can be calcualted using the following equation:

$$ I_{\text{Pri./Sec.}} = \frac{VA}{\sqrt{3} \cdot V_{\text{Pri./Sec.}}} $$

### Continuous Load Adjustment

Where the transformer supplies a continuous load, conductors shall be sized at **125% of the calculated FLA**, as required by **OESC Rule 26-256**.

$$ I = 1.25 \cdot I_{\text{Pri./Sec.}} $$

### Ampacity Corrections/Derating

After applying the continuous load factor, conductor ampacity shall be corrected for:

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

## Worked Example (High-Voltage Side)

Consider a transformer with the following nameplate

### Given Data

- Transformer rating: **75 kVA**  
- Primary voltage: **600 V**  
- Secondary voltage: **208 V**  
- System: **3-phase**  
- Ambient temperature: **40 °C**  
- Maximum conductor temperature: **75 °C**  
- Cable length: **50 m**
- 3 conductors per cable

### Primary Full-Load Current

$$ \begin{aligned} I_{\text{prim}} &= \frac{75{,}000}{\sqrt{3}\cdot 600} &\approx\; 73.3\ \text{A} \end{aligned} $$

#### Continuous Load Ampacity Target

$$ \begin{aligned} I_{\text{prim}}' &= 1.25\, I_{\text{prim}} &\approx\; 90.32\ \text{A} \end{aligned} $$

### Correction / Derating Summary

| Symbol | Meaning | Source / Note | Value |
|---:|---|---|---:|
| $U$ | Grouping / number of conductors correction (3 conductors) | OESC Table 5B | 0.85 |
| $A$ | Ambient temperature derating (40 °C) for 90 °C conductor column | OESC Table 5A (applied to Table 1, 90 °C column) | 0.91 |
| $B$ | Base allowable ampacity from 90 °C column | OESC Table 1, 90 °C column (for selected conductor, e.g. \#4 AWG) | 140 A |
| $C$ | Corrected ampacity using 90 °C base | $C=A\cdot B\cdot U$ | 108.3 A |
| $D$ | Base allowable ampacity from 75 °C column | OESC Table 1, 75 °C column (for selected conductor, e.g. \#4 AWG) | 125 A |
| $F$ | Corrected ampacity limited by 75 °C termination column | $F=D\cdot U$ | 106.3 A |

### Calculations

$$ \begin{aligned} C &= A\cdot B\cdot U = (0.91)(140)(0.85) \\ &\approx 108.3\ \text{A} \end{aligned} $$

$$ \begin{aligned} F &= D\cdot U = (125)(0.85) \\ &\approx 106.3\ \text{A} \end{aligned} $$

**Apply the lesser corrected ampacity**:

$$ I_{\text{min}} = \min(C,F) = 106.3\ \text{A} $$

<!-- Voltage drop covered in seperate section
## Voltage Drop

Use the 3-phase voltage drop check to confirm the feeder run meets the allowable voltage drop for the used distance.

$$ VD = \frac{K\cdot f \cdot I \cdot L}{1000} $$

$$ VD\% = \frac{VD}{V_n}\cdot 100\% $$

Where:
- $VD$ = voltage drop (V)  
- $VD\%$ = percent voltage drop (%)  
- $K$ = Table voltage drop factor in ohms per circuit kilometre found in OESC Table D3
- $f$ = Voltage drop factor based on the electrical system and circuit identifies in the Voltage Drop Factor Table found in OESC Table D3 - Continued 
- $I$ = Line Current (A) – use minimum ampacity above 
- $L$ = one-way length of run (m)  
- $V_n$ = nominal system voltage (V)  

| Cable Size Selected (AWG) | L (m) | K (assuming 90%) | I (A) | f (3-wire L-L, with ground) | VD% Calculated |
|---:|---:|---:|---:|---:|---:|
| 4 | 50 | 1.01 | 90.32 | 2 | **1.52** |

**Since the voltage drop is less than 3% and near our target of 1% this size is feasible. If $VD\%$ is larger than 3%, increase cable size and recalculate.**
-->
## Appendix

### Related Knowledge Files:
Knowlede File 4 <br/>
Knowledge File 26 <br/>
Transformer Feeder Calculations

### Related OESC Tables
Table 1<br/>
Table 2<br/>
Table 5A<br/>
Table 5B<br/>
