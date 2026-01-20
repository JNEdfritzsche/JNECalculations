### NEC — Transformer Protection (Full Theory, simplified)

### Objective
Select transformer overcurrent protection (breaker/fuses) in accordance with **NEC Article 450** so the device ratings meet the code allowances and protect the transformer.

### Scope & Key references
Focus on NEC 450.3 and tables 450.3(A) / 450.3(B) depending on voltage class. Also consult NEC 240.6(A) for standard ratings and device availability rules used when rounding to standard/commercial sizes.

### Assumptions (example template)
- Ambient temperature: **40°C**  
- Conductors: **75°C copper**, free-air routing  
- Max cable length: **50 m**  
- Transformer impedance: **≤ 6%** (common example used in the template)  
- Installation location classification: **Any location** vs **Supervised location** (affects table choices)

### Method / Practical approach
1. Use nameplate FLA when available; otherwise compute FLA for primary and secondary using the 3Φ formula below.  
2. Determine whether transformer is **over 1000 V nominal** (use **Table 450.3(A)**) or **1000 V nominal or less** (use **Table 450.3(B)**).  
3. Determine whether the installation is **Any location** or a **Supervised location** (this can change allowable multipliers/limits).  
4. Apply the table-based multipliers/limits to find allowable OCPD ratings (primary-only or primary+secondary schemes, where applicable).  
5. Apply the table notes on rounding to standard/commercial device ratings and on how multiple secondary devices may be grouped.

### Rated current formula (3Φ)
$$ I_L=\frac{S}{\sqrt{3}\,V_L} $$

Use consistent units (e.g., **S in VA with V in V**, or **S in kVA with V in kV**) so the result is in amperes.

$$ I_{pri}=\frac{S}{\sqrt{3}\,V_{pri}} $$
$$ I_{sec}=\frac{S}{\sqrt{3}\,V_{sec}} $$

### NEC 450.3 structure
**450.3(A)** — Transformers **over 1000 V nominal**: overcurrent protection per Table 450.3(A).  
**450.3(B)** — Transformers **1000 V nominal or less**: overcurrent protection per Table 450.3(B).  
**450.3(C)** — Voltage (potential) transformers: protection requirements depend on application.

### Table 450.3 notes that materially affect design (carried into this app)

**Table 450.3 Note 1 — Rounding to standard / commercially available sizes**  
- If the required fuse rating or breaker setting does not correspond to a standard value, a higher rating/setting is permitted provided it does not exceed:  
  - the **next higher standard rating/setting** for devices **1000 V and below**, or  
  - the **next higher commercially available rating/setting** for devices **over 1000 V**.

**Table 450.3 Note 2 — Multiple secondary devices (when secondary OCPD is required)**  
- The secondary OCPD is permitted to consist of **not more than six** circuit breakers, or **six sets of fuses**, **grouped in one location**.  
- Where multiple devices are used, the **sum of device ratings** shall not exceed the allowed value of a **single** overcurrent device.  
- If **both breakers and fuses** are used, the total of the device ratings shall not exceed that allowed for **fuses**.

**Supervised location (definition used in the calculation template)**  
A supervised location is one where maintenance/supervision ensure **only qualified persons** monitor and service the transformer installation (qualified persons have safety training and are familiar with operation and hazards).

### Worked NEC examples (from the NEC calc document)

Example 1 — 2 MVA, 27.6 kV / 4.16 kV, Z ≤ 6%, any location:

$$ I_{pri}=\frac{2{,}000{,}000}{\sqrt{3}\cdot 27{,}600}\approx 41.89\ \mathrm{A} $$
$$ I_{sec}=\frac{2{,}000{,}000}{\sqrt{3}\cdot 4{,}160}\approx 277.90\ \mathrm{A} $$

**Document example multipliers (table-driven, Z ≤ 6%, any location):**

Primary limits:

$$ I_{pri,brk,max}=6.00\cdot I_{pri}\approx 251.34\ \mathrm{A} $$
$$ I_{pri,fuse,max}=3.00\cdot I_{pri}\approx 125.67\ \mathrm{A} $$

Secondary limits:

$$ I_{sec,brk,max}=3.00\cdot I_{sec}\approx 833.70\ \mathrm{A} $$
$$ I_{sec,fuse,max}=2.50\cdot I_{sec}\approx 694.75\ \mathrm{A} $$

Example document selections (using commercially available sizes where applicable):  
**Primary 300 A breaker** or **150 A fuse**; **Secondary 1000 A breaker** or **700 A fuse**.

Example 2 — 75 kVA, 600 V / 208 V (currents > 9 A):

$$ I_{pri}=\frac{75{,}000}{\sqrt{3}\cdot 600}\approx 72.25\ \mathrm{A} $$
$$ I_{sec}=\frac{75{,}000}{\sqrt{3}\cdot 208}\approx 208.43\ \mathrm{A} $$

Two schemes presented in the document (table-driven):  
- primary-only → **100 A**  
- primary+secondary → **200 A primary** and **300 A secondary** (example selections)

### Practical design notes (NEC)
NEC transformer OCPD sizing focuses on protecting the transformer. Conductor protection still must be checked under Article 240. Coordination, relay protection for large transformers (e.g., ANSI 50/51 where applicable), and grounding/winding configuration should all be considered.
