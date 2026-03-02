
Cable Trays

## Overview

Cable trays comprise a large portion of installation paths in industrial projects. They provide a large area to carry multiple conductors/cables while being less labour-intensive than conduit. This section will cover general characteristics, considerations, and some basic examples of filling/bending cable trays.

---
## Cable Tray Characteristics

There are multiple different configurations and types of cable trays, and plenty of components to go along with them,

### Material

Cable Trays can be made of; steel, aluminum, or fibreglass. Each have their on strengths and use cases. Typically, we focus on **galvanized steel** cable trays as they are the most common material type we deal with. 

### Bottoms

The bottom of a cable tray decides the kind of installation path it is considered to be. There are; ladder (rung), solid, ventialted, wire mesh, etc., bottoms. We most often see **ladder trays** and they are considered *free-air* path of installation with no cover. 

### Fittings

Fittings are the different kinds of trays that are used in project  such as straights, side 45s, vertical 90s, tees, etc. There are many different kinds, some of which are not common at all. During the routing phase, the design team will become familiar for choosing what to use, creating a BOM of all fittings used.

### Expansion

Like all metal materials, cable trays experience expansion and contraction during temperature fluctuations. Between two sections of cable tray an expansion joints/guides is used to handle this. Its calculation is dependant on the maximum temperature difference the sections and expected to experience. 

### Typical Dimensions

Trays come in many different manufactured size. Heights, lengths, useable lengths, below is a typical [catalogue](https://tnb.ca/en/pdf-catalogues/cable-tray-systems/tnb-cable-tray/Aluminum_cable_tray.pdf) number for a straight piece. 

<div align="center">
  
![Figure 1: Typical Cable Tray Catalogue](images/CableTrayCatalogueNumber.png)
</div>

## Clearances



## Bending



---
## Cable Tray fill

There is no regulation explicitly stating the allowable limit of a cable tray fill. A general rule of thumb is to allow for 40% at the start of the detailed design phase and 80% at the end, to accommodate unaccounted for loads, and changes during installation. 

<div align="center">

![Figure 2: Typical Cable Tray Run](images/CableTrayRun.jpg)

</div>

Cables Trays can be fitted with dividers, effectively dividing the area into smaller sections for multiple runs. This division **does not allow** us to mix HV and LV runs in the same tray. We usually lay cables at 100% spacing or 0% spacing for the duration of the run as either; single layer spaced or trefoil configuration. 

Below are examples of cable tray filling. 

### Example: Single Layer Power Runs

We're running the following cables, evenly spaced in a single layer, in a 4" cable tray. We need to determine the minimum width and fill percentage.

| Quantity | Gauge     | Conductors | Approximate OD [mm] |
|----------|-----------|------------|---------------------|
|     9    | # 1/0 AWG |  1/C       |         13.23       |

Since they're being placed in a single layer, we sum the cable diameters and the even spacing between giving us;

$$ \text{Total Cable Width Space} = (\text{Total Cable Diameters}) + (\text{Total Cable Spacing}) $$

$$ = (9 \cdot 13.23 ) + (8 \cdot 13.23) = 224.91 \text{mm} \approx \text{8.85"} $$
 
A 9" tray will suffice. 

<div align="center">

![](images/CableTrayEx1a.png)

</div>

To determine tray we simply divide total cable area by usable tray area. Practical dimensions can be found from the manufacturer's catalogue as often a 4" height tray will have a smaller usable area due to the rails (say 3.04").

$$ \text{Tray fill %} = \frac{\text{Total Cable Area}}{\text{Usable Tray Area}} = \frac{9 \cdot \pi (6.615)^2}{77.22 \cdot 228.6}  = \frac{1237.24}{17652.492} = 7 \% $$

*NOTE*: To save more space, we can run them in a trefoil arrangment, like below. These are the same conductors but in a 6" tray.

<div align="center">

![Same nine conductors, in a trefoil configuration, in a 6" Tray](images/CableTrayEx1b.png)

</div>

### Example: Sectioned Runs

Were running the the following cables in a 12" cable tray divided into two section


| Quantity | Gauge   | Conductors | Approximate OD [mm] |
|----------|---------|------------|---------------------|
|     9    | # 2 AWG |  3/C       |       26.46         |
|     9    | #14 AWG |  12/C      |       30.88         |

Since these cables have already been derated accordingyl for <25% spacing, we can just arrange them in a neat configuration. 

<div align="center">

![](images/CableTrayEx2.png)

</div>

Finding the fill is the same, except we divide them into sections to determine if we can fit more cables in the future.

$$ \text{Section 1} = \frac{\text{Total Cable Area}}{\text{Usable Tray Area}} = \frac{9 \cdot \pi(13.23)^2}{77.22 \cdot 119.38} = \frac{4948.94}{9216.136} = 53.7 \% $$ <br/>
$$ \text{Section 2} = \frac{\text{Total Cable Area}}{\text{Usable Tray Area}} = \frac{9 \cdot \pi(15.443)^2}{77.22 \cdot 183.92} = \frac{6743.04}{14202.3} = 47.48 \% $$ <br/>
$$ \text{Total fill} = \frac{\text{Total Cable Area}}{\text{Usable Tray Area}} = \frac{11691.98}{23418.44} = 50 \% $$ <br/>

---
## Appendix

### Related Knowledge File 

<mark>[Knowledge File: Electrical Cable Tray Basics]()</mark> <br/>
[Knowledge File: Cable Tray Fill Calculations]()
[Design Basis — Calculations: Cable Tray]() <br/>
[Knowledge File Sharing Session: Cable Tray Supports]()

### Related OESC Rules

Rule 4-004 — Ampacity of Wires and Cables<br/>
12-2200
12-904

### Related OESC Tables

Tables 9A-9G — Conduit areas at various percentages<br/>
