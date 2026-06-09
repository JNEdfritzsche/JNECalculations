## Overview

This section walks through worked examples for calculating motor overcurrent device currents, including time-delay fuses, non-time-delay fuses, and circuit breakers.<br/>

The overcurrent device setting formula is:<br/>

$$ I_{OCPD} = k \cdot I_{FLA} $$

## Example 1 — DC Motor

A motor has the following nameplate

|Parameter|Value|
|-|-|
|$$V$$|180 V|
|$$I_{FLA}$$|9.5 A|
|Starter or Controller Type|N/A|

According to rule 28-200, noting that our motor is DC, we size for the overcurrent device rating with the following multipliers:

$${k_{TD}}$$ = 1.50

$${k_{NTD}}$$ = 1.50

$${k_{CB}}$$ = 1.50

Rounding up to the next standard overcurrent device rating, our devices would be sized to

$$ I_{OCPD(TD)}=I_{FLA} \cdot k_{TD} = 9.5 \cdot 1.50 =  14.25 A $$ -> <mark> $$15A$$

$$ I_{OCPD(NTD)}=I_{FLA} \cdot k_{NTD} = 9.5 \cdot 1.50 =  14.25 A $$ -> <mark> $$15A$$

$$ I_{OCPD(CB)}=I_{FLA} \cdot k_{CB} = 9.5 \cdot 1.50 =  14.25 A $$ -> <mark> $$15A$$

---

## Example 2 — AC Motor; 1$\phi$

A motor has the following nameplate

|Parameter|Value|
|-|-|
|$$V$$|230 V|
|$$I_{FLA}$$|62 A|
|Phase|1|
|Starter or Controller Type|N/A|

According to rule 28-200, noting that motor is single-phased, we size for the overcurrent device rating with the following multipliers:

$${k_{TD}}$$ = 1.75

$${k_{NTD}}$$ = 3.00

$${k_{CB}}$$ = 2.50

Rounding up to the next standard overcurrent device rating, our devices would be sized to

$$ I_{OCPD(TD)}=I_{FLA} \cdot k_{TD} = 62 \cdot 1.75 =  108.5 A $$ -> <mark> $$110A$$

$$ I_{OCPD(NTD)}=I_{FLA} \cdot k_{NTD} = 62  \cdot 3.00 =  186 A $$ -> <mark> $$200A$$

$$ I_{OCPD(CB)}=I_{FLA} \cdot k_{CB} = 62  \cdot 2.50 =  155 A $$ -> <mark> $$175A$$

---

## Example 3 — AC Motor; 3$\phi$; Squirrel-cage or Synchronous, Auto-TX or Star-Delta

A motor has the following nameplate

|Parameter|Value|
|-|-|
|$$V$$|612 V|
|$$I_{FLA}$$|90 A|
|Phase|3|
|Starter or Controller Type|Auto-TX or Star-Delta|

According to rule 28-200, noting that our motor is 3-phase with a motor type of Squirrel-cage or Synchronous, a starter or controller type of Auto-TX or Star-Delta, and $$I_{FLC}>30 A$$, we size for the overcurrent device rating with the following multipliers:

$${k_{TD}}$$ = 1.75

$${k_{NTD}}$$ = 2.00

$${k_{CB}}$$ = 2.00

Rounding up to the next standard overcurrent device rating, our devices would be sized to

$$ I_{OCPD(TD)}=I_{FLA} \cdot k_{TD} = 90 \cdot 1.75 =  157.5 A $$ -> <mark> $$175A$$

$$ I_{OCPD(NTD)}=I_{FLA} \cdot k_{NTD} = 90 \cdot 2.00 =  180 A $$ -> <mark> $$200A$$

$$ I_{OCPD(CB)}=I_{FLA} \cdot k_{CB} = 90 \cdot 2.00 =  180 A $$ -> <mark> $$200A$$

---

## Example 4 — AC Motor; 3$\phi$, Squirrel-cage or Synchronous, Auto-TX or Star-Delta

A motor has the following nameplate

|Parameter|Value|
|-|-|
|$$V$$|360 V|
|$$I_{FLA}$$|25 A|
|Phase|3|
|Starter or Controller Type|Auto-TX or Star-Delta|

According to rule 28-200, noting that our motor is 3-phase with a motor type of Squirrel-cage or Synchronous, a starter or controller type of Auto-TX or Star-Delta, and $$I_{FLC}<30 A$$, we size for the overcurrent device rating with the following multipliers:

$${k_{TD}}$$ = 1.75

$${k_{NTD}}$$ = 2.50

$${k_{CB}}$$ = 2.00

Rounding up to the next standard overcurrent device rating, our devices would be sized to

$$ I_{OCPD(TD)}=I_{FLA} \cdot k_{TD} = 25 \cdot 1.75 =  43.75 A $$ -> <mark> $$45A$$

$$ I_{OCPD(NTD)}=I_{FLA} \cdot k_{NTD} = 25 \cdot 2.50 =  62.5 A $$ -> <mark> $$70A$$

$$ I_{OCPD(CB)}=I_{FLA} \cdot k_{CB} = 25 \cdot 2.00 =  50 A $$ -> <mark> $$50A$$

---



## Example 5 — AC Motor; 3$\phi$; Squirrel-cage or Synchronous; FV&R

A motor has the following nameplate

|Parameter|Value|
|-|-|
|$$V$$|230/460 V|
|$$I_{FLA}$$|144/72 A|
|Phase|3|
|Starter or Controller Type|FV&R|

According to rule 28-200, noting that our motor is 3-phase with a motor type of Squirrel-cage or Synchronous and a starter or controller type of FV&R, we size for the overcurrent device rating with the following multipliers:

$${k_{TD}}$$ = 1.75

$${k_{NTD}}$$ = 3.00

$${k_{CB}}$$ = 2.50

Rounding up to the next standard overcurrent device rating, our devices would be sized to

$$ I_{OCPD(TD)}=I_{FLA} \cdot k_{TD} = 1.75 \cdot 144 = 252 A $$ -> <mark> $$300A$$

$$ I_{OCPD(NTD)}=I_{FLA} \cdot k_{NTD} = 3.00 \cdot 144 = 432  A $$ -> <mark> $$450A$$

$$ I_{OCPD(CB)}=I_{FLA} \cdot k_{CB} = 2.50 \cdot 144 =  360 A $$ -> <mark> $$400A$$

---

## Example 6 — AC Motor; 3$\phi$, Wound Rotor

A motor has the following nameplate

|Parameter|Value|
|-|-|
|$$V$$|430 V|
|$$I_{FLA}$$|127 A|
|Phase|3|
|Starter or Controller Type|Wound Rotor|

According to rule 28-200, noting that our motor is 3-phase with a motor type of wound rotor, we size for the overcurrent device rating with the following multipliers:

$${k_{TD}}$$ = 1.50

$${k_{NTD}}$$ = 1.50

$${k_{CB}}$$ = 1.50

Rounding up to the next standard overcurrent device rating, our devices would be sized to

$$ I_{OCPD(TD)}=I_{FLA} \cdot k_{TD} = 127 \cdot 1.50 =  190.5 A $$ -> <mark> $$200A$$

$$ I_{OCPD(NTD)}=I_{FLA} \cdot k_{NTD} = 127 \cdot 1.50 =  190.5 A $$ -> <mark> $$200A$$

$$ I_{OCPD(CB)}=I_{FLA} \cdot k_{CB} = 127 \cdot 1.50 =  190.5 A $$ -> <mark> $$200A$$

---

## Appendix

### Related Knowledge Files

[Design Basis — Calculations: Motor Protection](https://jnepeng.sharepoint.com/:w:/s/JNEElectricalPortalTeams/IQCXVHdd4QCvQJZdJh_U0PmVAUMoccLRBfe8SBMf7WTRXpo?e=oWNutN)<br/>
[Knowledge File - OESC: Section 28 Motor and Generators](https://jnepeng.sharepoint.com/sites/JNEElectricalPortalTeams/Shared%20Documents/Forms/AllItems.aspx?id=/sites/JNEElectricalPortalTeams/Shared%20Documents/Knowledge%20File%20—%20OESC%20Section%2028%20Motor%20and%20Generators.pdf&parent=/sites/JNEElectricalPortalTeams/Shared%20Documents&p=true&ga=1)

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

