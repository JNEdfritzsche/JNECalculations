## Overview

Transformers are passive devices that can deliver their full rated output continuously, so feeder sizing is based on transformer nameplate kVA and voltage rather than downstream load diversity. For this reason, transformer feeders are generally treated as continuous and must be selected to remain within allowable temperature limits after applying ambient, grouping, installation, and termination corrections. This section will cover the main aspects of sizing transformer feeders as well as cover a general methodology.

Transformers differ fundamentally from utilization equipment such as motors, heaters, or lighting loads:

- A transformer does not "draw" current based on demand in the same way a motor does
- It is capable of delivering its full rated current continuously
- It has no inherent current-limiting capability
- Overloads occur primarily as thermal stress, not immediate functional failure
- Because of this, the OESC treats the transformer feeder as part of the transformer system, not a supply conductor
- The feeder must therefore be sized assuming the transformer can and may operate at its nameplate rating indefinitely

---

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

---

## Appendix

### Related Knowledge Files

[Knowledge File — OESC: Section 4 Conductors](https://jnepeng.sharepoint.com/:b:/s/JNEElectricalPortalTeams/IQBX__AeZwFdTaYRIpekMk53AST1Z1fmbLyJuMdhL2C3csc?e=siODjS)<br/>
[Knowledge File — OESC: Section 26 Installation of Electrical Equipment](https://jnepeng.sharepoint.com/:b:/s/JNEElectricalPortalTeams/IQAr5W2CWdUbQb-26XCqmNYqAfifLPPITzkxySXkq7Q7sGQ?e=ZFTBIb)<br/>
[Design Basis — Calculations: Transformer Feeder Calculation](https://jnepeng.sharepoint.com/:w:/s/JNEElectricalPortalTeams/IQBmWQP7oRhwQJpoUj2syI31ASaPrwBGzyvhWrQlZzT9228?e=XKoJPh)

### Related OESC Rules

Rule 26-256 — Conductor size for transformers

### Related OESC Tables

Table 1/3 — Single Conductor ampacities for Copper/Aluminum<br/>
Table 2/4 — Multi-Conductor ampacities for Copper/Aluminum
