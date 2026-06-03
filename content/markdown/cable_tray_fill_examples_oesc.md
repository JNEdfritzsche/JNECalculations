## Overview

### Example: Single Layer Power Runs

We're running the following cables, evenly spaced in a horizontal layer, in a 4" cable tray. We need to determine the minimum width and fill percentage.

| Voltage | Quantity | Gauge     | Conductors | Approximate OD [mm] |
|---------|----------|-----------|------------|---------------------|
| 600 V   |     9    | # 1/0 AWG |  1/C       |         13.23       |

Since they're being placed in a single layer, we sum the cable diameters and the even spacing between giving us;

$$ \text{Total Cable Width Space} = (\text{Total Cable Diameters}) + (\text{Total Cable Spacing}) $$

$$ = (9 \cdot 13.23 ) + (8 \cdot 13.23) = 224.91 \text{mm} \approx \text{8.85"} $$

A 9" tray will suffice.

<div align="center">

![](../images/CableTrayEx1a.png)

</div>

To determine tray fil, we simply divide total cable area by usable tray area. Practical dimensions can be found from the manufacturer's catalogue as often a 4" height tray will have a smaller usable height due to the rungs (say 3.04").

$$ \text{Tray fill \%} = \frac{\text{Total Cable Area}}{\text{Usable Tray Area}} = \frac{9 \cdot \pi (6.615)^2}{77.22 \cdot 228.6}  = \frac{1237.24}{17652.492} = 7 \% $$

**NOTE**: To save more space, we can run them in a trefoil arrangment, like below. These are the same conductors but in a 6" tray.

<div align="center">

![](../images/CableTrayEx1b.png)

</div>

### Example: Sectioned Runs

We're running the the following cables in a 4"x12" cable tray divided into two section


| Voltage | Quantity | Gauge    | Conductors | Approximate OD [mm] |
|---------|----------|----------|------------|---------------------|
|  347 V  |     9    | # 2 AWG  |  3/C       |       26.46         |
|  24 VDC |     9    | # 14 AWG |  12/C      |       30.88         |

Since these cables have already been derated appropriately for <25% spacing, we can just arrange them in a neat configuration.

<div align="center">

![](../images/CableTrayEx2.png)

</div>

Finding the fill is the same, except we divide them into sections to determine if we can fit more cables in the future.

$$ \text{Section 1} = \frac{\text{Total Cable Area}}{\text{Usable Tray Area}} = \frac{9 \cdot \pi(13.23)^2}{77.22 \cdot 119.38} = \frac{4948.94}{9216.136} = 53.7 \% $$

$$ \text{Section 2} = \frac{\text{Total Cable Area}}{\text{Usable Tray Area}} = \frac{9 \cdot \pi(15.443)^2}{77.22 \cdot 183.92} = \frac{6743.04}{14202.3} = 47.48 \% $$

$$ \text{Total fill} = \frac{\text{Total Cable Area}}{\text{Usable Tray Area}} = \frac{11691.98}{23418.44} = 50 \% $$

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

Tables 15 — Bending Radii: High-Voltage Cables
