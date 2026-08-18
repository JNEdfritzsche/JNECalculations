## Overview

Cable trays comprise a large portion of installation pathways in industrial facilities. They offer a highly accessible routing solution to carry multiple power, control, and signal cables. Sizing and filling cable trays is strictly regulated under **NEC Article 392** to prevent overheating and conductor damage.

---

## Cable Tray Characteristics

### Material

Cable trays are typically constructed of galvanized steel, aluminum, or fiberglass. **Galvanized steel** and **aluminum** are the most common metallic options in industrial environments and must be listed and labeled for their physical loading capacity.

### Bottoms

The design configuration determines the fill limits under NEC Article 392:

- **Ladder or Ventilated Trough**: Most common for power distribution because they allow free air circulation.
- **Solid Bottom**: Often used where shielding or additional physical protection is required, but have stricter fill limitations.

### Fittings

Fittings include tees, elbows, crosses, and vertical risers. Sizing horizontal bends must respect the minimum bending radius of the cables being installed (NEC 305.13(C) and Article 392).

### Expansion Joints

Since metallic trays expand and contract with temperature swings, expansion joints must be installed in long outdoor runs as calculated using manufacturer guidelines.

---

## Clearances and Installation Methods

Under NEC 392.18, cable trays must be exposed and accessible. Clearance must be maintained above and around the tray to permit the installation and maintenance of cables without physical obstruction.

---

## Cable Tray Fill Calculations

Unlike other standards that rely on arbitrary fill margins, the **NEC mandates strict mathematical limits** for cable tray fill in **NEC 392.22**:

### Multi-conductor Cables Rated 2000V or Less:

**Ladder, Ventilated Trough or Wire Mesh (NEC 392.22(A)(1))**: which test applies depends on the cable sizes present.

- **392.22(A)(1)(a)** — **all** cables 4/0 AWG or larger: the sum of the cable **diameters** must not exceed the tray width, installed in a single layer. No area limit applies.
- **392.22(A)(1)(b)** — **all** cables smaller than 4/0 AWG: the sum of the cross-sectional **areas** must not exceed **Column 1** of Table 392.22(A)(1) for that tray width.
- **392.22(A)(1)(c)** — 4/0 AWG and larger sharing the tray with smaller cables: the areas of the **smaller** cables are limited by the **Column 2** computation, *(Column 1 value) − (1.2 × Sd)*.

**Solid Bottom (NEC 392.22(A)(3))**: the same three-way structure, using Columns 3 and 4 of the same table. Solid-bottom allowances run about **75% to 80%** of the ladder/ventilated values because of trapped heat.

### Single-conductor Cables Rated 2000V or Less:

Single-conductor cables in tray must be 1/0 AWG or larger, and are sized per **NEC 392.22(B)(1)**, which splits four ways by conductor size:

- **(a)** — all cables 1000 kcmil or larger: sum of **diameters** must not exceed the tray width.
- **(b)** — all cables 250 kcmil through 900 kcmil: sum of **areas** must not exceed Column 1 of Table 392.22(B)(1).
- **(c)** — 1000 kcmil and larger installed with smaller cables: the smaller cables are limited by the Column 2 computation, *(Column 1 value) − (1.1 × Sd)*.
- **(d)** — where any cables **1/0 through 4/0** are installed: sum of **diameters** must not exceed the tray width. This is the common industrial case, and it is a width check.

### Voltage Segregation (Barrier Strips)

Under **NEC 392.20(B)**, cables rated **over 2000 volts** shall not be installed in the same cable tray with cables rated 2000 volts or less unless one of the following applies:

- The cables rated over 2000 volts are Type MC, or
- The two groups are separated by a solid fixed barrier of material compatible with the cable tray.

Note that the threshold here is 2000 V rather than the 600 V often assumed. Below 2000 V no barrier is required between voltage levels, though separating power from instrumentation and control remains good practice for electromagnetic interference.

---

## Appendix

<!-- ### Related Knowledge Files

[Knowledge File: Industrial Cable Tray Design Principles]<br/>
[Knowledge File: Cable Tray Fill Sizing and Area Calculations] -->

### Related NEC Articles

Section 305.13(C) — Conductor Bending Radius<br/>
Section 392.10 — Uses Permitted for Cable Trays<br/>
Section 392.20 — Cable and Conductor Installation in Trays<br/>
Section 392.22 — Number of Cables or Conductors in Cable Trays<br/>
Section 392.60 — Grounding and Bonding of Cable Trays<br/>
Section 392.80 — Ampacity of Conductors in Cable Trays

### Related NEC Tables

Table 392.22(A)(1) — Allowable Cable Fill Area for Multiconductor Cables in Ladder, Ventilated Trough, or Solid Bottom Cable Trays<br/>
Table 392.22(A)(5) — Allowable Cable Fill Area for Multiconductor Cables in Ventilated Channel Cable Trays<br/>
Table 392.22(A)(6) — Allowable Cable Fill Area for Multiconductor Cables in Solid Channel Cable Trays<br/>
Table 392.22(B)(1) — Allowable Cable Fill Area for Single-Conductor Cables in Ladder, Ventilated Trough, or Wire Mesh Cable Trays
