## Overview

These examples walk through the few different examples of sizing OCPDs for various transformers. The main three are 

<!--

---

## Example 1 — Transformers > 750V; Primary side Protection

A Transformer has the following nameplate

| Parametre | Value |
|-|-|
| Power | 2 MVA |
| $${V_P}$$ | 10.2 kV |
| $${V_S}$$ | 415 V |
| Impedance | 3.5% |

According to rule 26-250, we size for the primary protection with the following multipliers:

$${k_{CB}}$$ = 3.0

$${k_{F}}$$ = 1.5

Rounding up to the next standard size, our devices would be be sized to

$$ I_{CB,pri.}=I_P \cdot k_{CB} = 113.21 \cdot 3 =  339.63 A $$ -> <mark> $$350A$$

$$ I_{F,pri.}=I_P \cdot k_{F} = 113.21 \cdot 1.5 =  169.82 A $$ -> <mark> $$175A$$

---
## Example 2 — Transformers > 750V; P&S Side Protection

A Transformer has the following nameplate

| Parametre | Value |
|-|-|
| Power | 750 kVA |
| $${V_P}$$ | 33 kV |
| $${V_S}$$ | 11 kV |
| Impedance | 3.6% |

According to rule 26-250, differentiating that our secondary is also > 750V, we size for the primary & secondary protection with the following multipliers:

$${k_{CB,pri.}}$$ = 6.0

$${k_{F,pri.}}$$ = 3.0

$${k_{CB,sec.}}$$ = 3.0

$${k_{F,sec.}}$$ = 1.5

Rounding up to the next standard size, our devices would be be sized to

$$ I_{CB,pri.}=I_P \cdot k_{CB} = 13.12 \cdot 6 =  39.36 A $$ -> <mark> $$40A$$

$$ I_{F,pri.}=I_P \cdot k_{F} = 13.12 \cdot 3 =  78.73 A $$ -> <mark> $$80A$$

$$ I_{CB,sec.}=I_P \cdot k_{CB} = 39.36 \cdot 3 =  59.05 A $$ -> <mark> $$60A$$

$$ I_{F,sec.}=I_P \cdot k_{F} = 39.36 \cdot 1.5 =  118.09 A $$ -> <mark> $$125A$$ 

---
## Example 3 — Transformers < 750V; Oil type, Primary Side Protection

number 6

---
## Example 4 — Transformers < 750V; Dry-type, P&S Side Protection

number 11


---
## Appendix

### Related Knowledge Files

[Knowledge File — OESC: Section 26 Installation of Electrical Equipment](https://jnepeng.sharepoint.com/:b:/s/JNEElectricalPortalTeams/IQAr5W2CWdUbQb-26XCqmNYqAfifLPPITzkxySXkq7Q7sGQ?e=ZFTBIb)<br/>
[Design Basis — Calculations: Transformer Protection Calculation](https://jnepeng.sharepoint.com/:w:/s/JNEElectricalPortalTeams/IQDKl-wkmkujQb_ZfZKZZwfDAXYYVGNWrV_TkJmXlw8w2Ac?e=BAApqB)

### Related OESC Rules

Rule 8-104 — Maximum circuit loading<br/>
Rule 26-250 — Overcurrent protection, transformers rated >750 V<br/>
Rule 26-252 — Overcurrent protection, transformers rated <750 V, other than dry type<br/>
Rule 26-254 — Overcurrent protection. dry-type transformers rated <750 V

### Related OESC Tables

Table 13 — Standard Overcurrent Device Ratings<br/>
Table 50 — Overcurrent protection, transformers rated > 750V
