### OESC — Transformer Protection (Full Theory, simplified)

### Document metadata / header (example)
**Associated with WI-8.3-.06 Rev. 0, May 2019**  
**Project #:** XX-XX-XXXX-XX — **Client:** JNE  
**Project Title:** OESC Transformer Protection Design Calculation  
**Calculation #:** EC-XXXX — **Revision:** A — **Date Initiated:** 08/17/2022

### Objective
Determine required overcurrent protection for a transformer (primary breaker/fuse sizing) so the transformer operates safely and the installation meets OESC requirements.

### Scope
This calculation covers selecting primary (and when applicable secondary) overcurrent devices for typical power/distribution transformers using OESC as the reference.

### Technical Criteria / Applicable Codes
Primary reference: Ontario Electrical Safety Code (OESC) — relevant rules include 26-240 through 26-258 and Section 8 (Rule 8-104) for continuous loading.

### Assumptions (example template used in the document)
- Ambient temperature: **40 °C**  
- Conductor temperature rating: **75 °C**  
- Copper conductors routed in free-air (field routed)  
- No more than 3 conductors per cable (including equipment grounding conductor)  
- Maximum cable length: **50 m (~164 ft)**  
- Transformer operating with **natural cooling** (no fans/pumps)

### Input Data
Use transformer nameplate data where available. If using OEM documentation, include document name/number and equipment ID.

### Rated current formula (when FLA is not known)
For three-phase transformers the rated line current is:

$$ I_L=\frac{S}{\sqrt{3}\,V_L} $$

where \(S\) = apparent power, \(V_L\) = line-to-line voltage. Use consistent units (e.g., **S in VA with V in V**, or **S in kVA with V in kV**) so the result is in amperes.

Use this to calculate primary and secondary FLA:

$$ I_{pri}=\frac{S}{\sqrt{3}\,V_{pri}} $$
$$ I_{sec}=\frac{S}{\sqrt{3}\,V_{sec}} $$

### Methodology (practical steps)
1. Use nameplate FLA if available; otherwise compute FLA using the equations above.  
2. Identify transformer type (oil-cooled vs dry-type) and voltage class (>750 V or ≤750 V).  
3. Apply the relevant OESC rule to determine the permitted OCPD multiplier(s) and any conditions/exceptions.  
4. If the calculated device rating does not match a standard device rating, select the **next higher** standard rating as permitted by the rule.  
5. Confirm whether an **individual primary device at the transformer** is required, or whether upstream feeder/branch protection is permitted to serve this role (rule-dependent).  
6. Verify continuous loading limits (Rule 26-258 and Rule 8-104) and conductor ampacity separately.

### OESC Rule highlights (key subrules summarized — corrected)

**OESC 26-250 — Overcurrent protection for power and distribution transformer circuits rated over 750 V (oil-cooled / power & distribution)**  
- Each ungrounded conductor of the transformer feeder shall have overcurrent protection.  
- **Fuses:** rated at not more than **150%** of rated primary current.  
- **Breakers:** rated/set at not more than **300%** of rated primary current.  
- If **150%** does not correspond to a standard fuse rating, the **next higher standard fuse rating** is permitted.  
- **An individual overcurrent device is not required** where the feeder/branch overcurrent device provides the protection specified in this rule.

**OESC 26-252 — Overcurrent protection for transformers 750 V or less (oil-cooled / other than dry-type)**  
- Primary overcurrent protection generally **≤ 150%** of rated primary current.  
- If rated primary current is **9 A or more** and **150%** does not correspond to a standard rating of a fuse or non-adjustable breaker, the **next higher standard rating** is permitted.  
- If rated primary current is **less than 9 A**, an overcurrent device **≤ 167%** is permitted.  
- If rated primary current is **less than 2 A**, an overcurrent device **≤ 300%** is permitted.  
- **An individual overcurrent device is not required** where the feeder/branch overcurrent device provides the protection specified in this rule.  
- **Secondary-protection pathway (common allowance):** A transformer with a **secondary-side device ≤ 125%** of rated secondary current **need not have an individual primary device**, provided that the **primary feeder overcurrent device ≤ 300%** of rated primary current (rule conditions apply).

**OESC 26-254 — Overcurrent protection for dry-type transformers 750 V or less**  
- Primary overcurrent protection generally **≤ 125%** of rated primary current.  
- If the required device rating does not correspond to a standard rating, the **next higher standard rating** may be permitted as allowed by the rule.  
- **An individual overcurrent device is not required** where the feeder/branch overcurrent device provides the protection specified in this rule.  
- **Secondary-protection pathway (common allowance):** A transformer with a **secondary-side device ≤ 125%** of rated secondary current **need not have an individual primary device**, provided that the **primary feeder overcurrent device ≤ 300%** of rated primary current (rule conditions apply).  
- **Inrush withstand guidance (Appendix):** the device should be able to carry **12× FLA for 0.1 s** and **25× FLA for 0.01 s** (verify manufacturer curves).

### Continuous load and conductor checks (OESC 26-258 and Rule 8-104 intent)
OESC 26-258 ties transformer overcurrent protection and conductor sizing (Rules 26-250 to 26-256) to the **continuous load** connected to the transformer secondary. In general terms: the continuous load determined from the calculated load connected to the transformer secondary must not exceed the values specified in Rule 8-104 (as applicable).

Appendix intent (plain language): this requirement helps ensure **coordination** between the secondary loads, transformer protection device ratings, and conductor ampacity.

### Worked calculation examples (from the provided doc)

Example A — Oil-cooled > 750 V (2,000 kVA, 27.6 kV / 600 V, 3Φ):

$$ I_{pri}=\frac{2{,}000{,}000}{\sqrt{3}\cdot 27{,}600}\approx 41.89\ \mathrm{A} $$
$$ I_{sec}=\frac{2{,}000{,}000}{\sqrt{3}\cdot 600}\approx 1926.78\ \mathrm{A} $$

Using OESC 26-250 multipliers:

$$ I_{fuse,max}=1.50\cdot I_{pri}\approx 62.83\ \mathrm{A} $$
$$ I_{brk,max}=3.00\cdot I_{pri}\approx 125.66\ \mathrm{A} $$

Selected standard sizes: **70 A fuse** or **150 A breaker** (next standard values).

Example B — Oil-cooled ≤ 750 V (75 kVA, 600 V / 208 V):

$$ I_{pri}=\frac{75{,}000}{\sqrt{3}\cdot 600}\approx 72.17\ \mathrm{A} $$
$$ I_{ocpd,max}=1.50\cdot I_{pri}\approx 108.26\ \mathrm{A} $$

Selected standard size: **110 A** (per standard device values).

Example C — Dry-type ≤ 750 V (75 kVA, 600 V / 208 V):

$$ I_{pri}\approx 72.17\ \mathrm{A} $$
$$ I_{ocpd,max}=1.25\cdot I_{pri}\approx 90.21\ \mathrm{A} $$

Selected standard size: **100 A**. Inrush checks:

$$ 12\times I_{pri}\approx 866.04\ \mathrm{A} $$
$$ 25\times I_{pri}\approx 1804.25\ \mathrm{A} $$

### Design considerations & coordination
After selecting initial device ratings, perform a coordination study. Consider transformer winding configuration (Δ–Y, Y–Y, etc.), grounding method (open, solid, NGR), device availability, cost, and selective clearing of faults.

### Conclusion (example selections)
- For the 2 MVA 27.6k/600V oil-cooled example: **70 A fuse** or **150 A breaker** selected.  
- For the 75 kVA 600/208V oil-cooled example: **110 A** selected.  
- For the 75 kVA dry-type example: **100 A** selected.

### Approval block (template)
Prepared by: Michael Hommersen — Self-Check Completed? YES.  
Include signature/date fields in your deliverable calculation sheet.
