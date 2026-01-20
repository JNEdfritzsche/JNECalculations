## Conductors — Theory
OESC Section 4 (Rule 4-004) workflow + worked example case study.

> **Note (Jurisdiction):** This page is based on an OESC/CEC (Ontario/Canada) conductor sizing workflow summary. If you need NEC-specific conductor sizing, this page would need a separate NEC implementation.

### Keywords
- **Raceway:** any channel designed for holding wires, cables, or busbars, such as conduits, tubing, and ducts.  
- **Spacing:** the separation between cables in a run, given as **% of largest cable diameter**.  
- **Service factor:** a multiplying factor that indicates how much a piece of equipment can be overloaded without significant damage under specified conditions.

### Summary
This summary is intended to familiarize you with calculating cable sizes for different loads and runs, using a CEC Handbook-style workflow and OESC tables (Tables 1–4 plus correction factors). Always consult the full code book for final compliance.

### Ampacity selection chart (ambient temperature ≤ 30°C)
Table-selection logic summarized from OESC Rule 4-004 guidance.

| Subrule | Conductors | Condition | Spacing (% of cable diameter) | Use ampacity from |
|---|---|---|---|---|
| 4-004 (1) & (2) | a) Single | Free air | ≥ 100% | Table **1** (Cu) or **3** (Al) |
| 4-004 (1) & (2) | b) 1 to 3 | Raceway or cable | N/A | Table **2** (Cu) or **4** (Al) |
| 4-004 (1) & (2) | c) 4 or more | Raceway or cable | N/A | Table **2** or **4** × correction factor from Table **5C** |
| 4-004 (1) & (2) | d) Not more than 4 | No. 1/0 AWG and larger underground run — direct buried or in a direct-buried raceway | Configurations in Diagrams D8 to D11 | Tables **D8A to D11B** or IEEE **835** method |
| 4-004 (1) & (2) | e) Not more than 4 | No. 1/0 AWG and larger underground run — direct buried or in a direct-buried raceway | Configuration not described in D8 to D11 | IEEE **835** method |
| 4-004 (1) & (2) | f) Not more than 4 | Smaller than No. 1/0 AWG underground run — direct buried or in a direct-buried raceway | Configuration not described in D8 to D11 | IEEE **835** method or as specified in Tables **2** and **4** |
| 4-004 (8) | Single | Free air | 25% to 100% | Table **1** or **3** × correction factor from Table **5D** |
| 4-004 (9) | Not more than 4 single | Free air | < 25% | Table **1** or **3** × correction factor from Table **5B** |
| 4-004 (11) | 5 or more single | Free air | < 25% | Table **2** or **4** × correction factor from Table **5C** |

### Typical assumptions used in the worked example
- Termination temperature assumption often used for quick checks: **60°C** for equipment **<100A**, and **75°C** for equipment **>100A**  
- Service factor often assumed for equipment: **SF = 1.25**  
- Power factor often assumed: **pf ≈ 0.9**  
- Ambient temperature: **≤ 30°C**

### Common calculation relationships used in the workflow
Service-factor (design multiplier) current:

$$ I_{design} = I_{load}\times SF $$

If using parallel runs (per set current):

$$ I_{per\_set} = \frac{I_{design}}{N_{parallel}} $$

If a correction factor applies (Table 5B / 5C / 5D), the base-table ampacity needed is:

$$ I_{table} = \frac{I_{per\_set}}{k_{corr}} $$

### Worked example case study (steel mill — tasks 1 to 5)

**Case:** steel mill installing new equipment and replacing old cables; a transformer supplies lighting, motors, control panels, heaters, etc.  
**Conditions:** transformer inside electrical room; feeds equipment through free air (tray), raceways, and direct-buried routes.

**Task 1:** 3Φ 500 kVA, 13.8 kV / 600 V transformer; single conductors for secondary connection.  
- Primary/secondary FLA: **20.919 A / 481.139 A**  
- With SF=1.25: **26.15 A / 601.42 A**  
- Example result: **500 MCM** (Table 1, rounded up)

**Task 2 (Free air / ladder tray):** ladder trays considered free-air.  
- 40A 1Φ + GND (3C), plenty of spacing → design 50A → Table 2 → **No. 6 AWG**  
- 100A 3Φ delta + GND (4 singles), spacing 25–100% → apply Table 5D → table current 150A → Table 1 → **No. 2 AWG**  
- 200A 3Φ wye + GND, parallel singles, <25% spacing → per-conductor 100A → apply Table 5C → table current 179A → Table 2 → **No. 3/0 AWG**

**Task 3 (Raceway):**  
- 125A 3Φ 3W delta in its own conduit → 156.25A design → Table 2 → **No. 2/0 AWG**  
- 150A 3Φ 4W wye in its own conduit (Al) → apply Table 5C → table current 234.38A → Table 4 → **350 MCM**

**Task 4 (Direct-bury):** follow Diagrams D8–D11; otherwise IEEE 835 method.  
- 325A 3Φ, 3 singles flat config (Diagram D8 Detail 1) → 406.25A design → Table D8A → **No. 4/0 AWG**  
- 160A 3Φ using parallel 3C cables in underground conduit (Diagram D11 Detail 2) → diagram table shows smallest cable 185A, so example uses Table 2 → **No. 3 AWG**  
*(Spacing often must be calculated and iterated.)*

**Task 5 (Voltage drop / k-value):** 600V / 100A heater, 1.5 km away.  
- Design current 125A; max VD = 5% = 30V  
- Compute **k_max = 0.08 Ω/km**, select from Table D3 → **1000 MCM**

### Voltage drop k-value relationship used in the example

$$ k_{max} = \frac{\Delta V_{allow}}{2\,I\,L_{km}} $$

Compare \(k_{max}\) to manufacturer k-values (Ω/km). Tables 1–4 ampacities do not include voltage drop.

<details>
  <summary><b>Manufacturer spec reminder (why cable spec sheets matter)</b></summary>
  <br/>
  The Knowledge File includes examples of manufacturer spec pages (e.g., TECK90 and armored VFD cable).
  In real projects, you’ll need spec-sheet details such as conductor class/stranding, insulation type, jacket/armor, OD, weight,
  minimum bend radius, pull tension, and resistance/k-values for voltage drop and heat calculations.
</details>
