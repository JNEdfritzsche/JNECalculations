## Overview

This section walks through worked examples for cable tray fill calculations under OESC Rule 12-2202. The goal is to demonstrate how to determine minimum tray width and fill percentage for single-layer and sectioned cable tray runs. For theory and cable tray characteristics, refer to the theory tab.

The core formula for tray fill percentage is:

$$\text{Fill\%} = \frac{\text{Total Cable Area}}{\text{Usable Tray Area}} \times 100\%$$

For single-layer spaced runs, minimum tray width sums the cable diameters plus the spacing between each cable (spacing = one cable diameter for even spacing):

$$W_{\text{min}} = (N \cdot d) + (N - 1) \cdot d = (2N - 1) \cdot d$$

---

## Example 1 — Single Layer Power Runs

**9× #1/0 AWG – 1/C | 600 V | 4" tray | Single layer, evenly spaced**

| Parameter | Value |
|-----------|-------|
| Quantity | 9 cables |
| Gauge | #1/0 AWG – 1/C |
| Approximate OD | 13.23 mm (radius = 6.615 mm) |
| Tray height (usable) | 4" (usable ≈ 3.04" = 77.22 mm) |

**Minimum tray width:**

Cables are spaced with one cable-diameter gap between each, so total space = cable diameters + equal spacing:

$$W_{\text{min}} = (9 \times 13.23) + (8 \times 13.23) = 119.07 + 105.84 = 224.91 \text{ mm} \approx 8.85\text{"} \quad \Rightarrow \text{Select 9" tray (228.6 mm usable width)}$$

**Tray fill percentage:**

$$\text{Fill\%} = \frac{9 \cdot \pi (6.615)^2}{77.22 \times 228.6} = \frac{1{,}237.24}{17{,}652.49} = 7\%$$

<div align="center">

![](../images/CableTrayEx1a.png)

</div>

An alternative arrangement is trefoil configuration, which reduces required tray width. The cables below are the same conductors arranged in trefoil in a 6" tray.

<div align="center">

![](../images/CableTrayEx1b.png)

</div>

**Result: Minimum tray width = 9" | Tray fill = 7%**

---

## Example 2 — Sectioned Runs

**Two cable groups | 4"×12" tray | Divided into two sections**

| Voltage | Quantity | Gauge | Conductors | Approximate OD |
|---------|----------|-------|------------|----------------|
| 347 V | 9 | #2 AWG | 3/C | 26.46 mm (radius = 13.23 mm) |
| 24 VDC | 9 | #14 AWG | 12/C | 30.88 mm (radius = 15.44 mm) |

Cables have been derated for <25% spacing. The tray is divided into two sections with each group filling one section.

<div align="center">

![](../images/CableTrayEx2.png)

</div>

**Section 1 — 347 V cables (usable width = 119.38 mm):**

$$\text{Fill\%} = \frac{9 \cdot \pi (13.23)^2}{77.22 \times 119.38} = \frac{4{,}948.94}{9{,}216.14} = 53.7\%$$

**Section 2 — 24 VDC cables (usable width = 183.92 mm):**

$$\text{Fill\%} = \frac{9 \cdot \pi (15.44)^2}{77.22 \times 183.92} = \frac{6{,}743.04}{14{,}202.30} = 47.5\%$$

**Total tray fill:**

$$\text{Fill\%}_{\text{total}} = \frac{4{,}948.94 + 6{,}743.04}{9{,}216.14 + 14{,}202.30} = \frac{11{,}691.98}{23{,}418.44} = 50\%$$

**Result: Section 1 = 53.7% | Section 2 = 47.5% | Total tray fill = 50%**

---

## Appendix

### Related Knowledge Files

[Knowledge File: Electrical Cable Tray Basics](https://jnepeng.sharepoint.com/:b:/s/JNEElectricalPortalTeams/IQBtTHP_lg3JQJIxvLmY4aO0ASu8wD0xU1vlKVAghLyceGM?e=4hsiZl)<br/>
[Knowledge File: Cable Tray Fill Calculations](https://jnepeng.sharepoint.com/:w:/s/JNEElectricalPortalTeams/IQDv0upg_n7VR6T_52A_DDI4Ae_oKjCl7_EWnXslImvY5HA?e=LyVdMO)<br/>
Knowledge File Sharing Session: Cable Tray Supports

### Related OESC Rules

Rule 4-004 — Ampacity of Wires and Cables<br/>
Rule 12-904 — Conductors in Raceway (Barrier Strips)<br/>
Rule 12-2200 — Conductors/Cables installation methods (Clearances)<br/>
Rule 12-2202 — Insulated Conductors/Cables in Cable trays<br/>
Rule 12-2208 — Cable tray Bonding

### Related OESC Tables

Table 15 — Bending Radii: High-Voltage Cables
