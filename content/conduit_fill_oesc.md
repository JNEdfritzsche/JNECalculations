## Overview

Cables running through conduit provide a reliable path, protecting from environmental damages. As covered in the **Conductors** section and in Rules 4-004, cables must be derated accordingly if ran through conduit. Cable size is determined beforehand, based on load, distance, and it's installation path. Each cable size will be given by the manufacturer, as will the conduit's internal cross-sectional area, which determines our conduit fill schedule. This section will briefly cover the limits and methodology of filling conduits with conductors/cables. 

---
## Cables in Conduit

Conduit fill percentage is determined by the number of cables/conductors inside. As per Figure 1 below, we are restricted to the following percentages. For most cases, we deal with a 40% fill limit. Simply put, we give conduit fill as a percentage of the total cable(s) area over internal conduit area.

<div align="center">
  
![Figure 1: Conduit Fill Percentages Table](images/Table8.png)

</div>

There are a few factors to consider, such as pull tension, maximum of two 90° elbows in one run, etc. The larger concerns are maximum number of cables and voltage segregation. 
- As per Rule 12-910, we are limited to a *maximum of 200 cables per conduit* no matter the size. 
- It is best practice to segregate conduits by voltage, **never** mixing low voltage signal runs with high voltage power runs. You can have mixed runs, of 120V~600V in one conduit (usually if of the same circuit), but if feasible, it is best to separate voltages as much as possible. 

---
## General Method

Once cables have been adequately sized, we must determine the best order to fill the conduits. We aim to fill conduits in order of; voltage level, and conductor gauge. Below are two examples.

### Separating by Voltage Level

Consider two runs through 53 mm (2") conduit.

|Param.      |Run 1| Run 2|
|------------|-----|------|
|Voltage:    | 24VDC | 600V |
|Insulation: | TW75  | RW90XLPE jacketed |
|Conductors: | 98 x #14 AWG-1/C | 1 x #2/0 AWG-6/C |

Here we would run the signal through one conduit and the power through the other. The signal conduit having a limit of 40% and the power conduit of 53%.

|     Param.        | Conduit 1                             | Conduit 2                            |
|-------------------|---------------------------------------|--------------------------------------|
Cable Area:         | $$ 8.9 \text{mm}^2 $$                 | $$ 1165 \text{mm}^2$$                |
Total Cable area:   | $$ 98 \cdot 8.9 = 872.2 \text{mm}^2$$ | $$ 1 \cdot 1165 = 1165 \text{mm}^2$$ |
Conduit Area (100%):| $$ 2199 \text{mm}^2 $$                | $$ 2199 \text{mm}^2 $$               |
Conduit Fill %:     | $$ \frac{872.2}{2199} = 39.66 \% $$   | $$ \frac{1165}{2199} =  52.97\% $$   |

As we see, both conduit are able to fit their respective runs within regulation.

### Separating by Gauge

Consider two runs through 78 mm (3") conduit.

|Param.      |Conduit 1|Conduit 2|
|------------|---------|---------|
|Voltage:    | 24VDC | 480V |
|Insulation: | TW75  | RW90XLPE jacketed |
|Conductors: | 75 x #14 AWG-1/C </br> 150 x #10 AWG-1/C | 4 x 250 MCM-1/C |

However, since we see the signal runs comprise of more than 200 cables, we must use another conduit to run these. In this case, we would segregate by conductor gauge. Following the same methodology as before.

|     Param.        |Conduit 1 | Conduit 2 | Conduit 3  |
|-------------------|----------|-----------|------------|
Cable Area:         | $$8.9 \text{mm}^2 $$                 | $$15.7 \text{mm}^2$$                       | $$ 354 \text{mm}^2$$                |
Total Cable area:   | $$75 \cdot 8.9 = 667.5 \text{mm}^2$$ | $$150 \cdot 15.7 = 2355 \text{mm}^2$$      | $$ 4 \cdot 354 = 1416 \text{mm}^2$$ |
Conduit Area (100%):| $$ 4839\text{mm}^2 $$                | $$ 4839 \text{mm}^2 $$                     | $$ 4839\text{mm}^2 $$               |
Conduit Fill %:     | $$ \frac{667.5}{4839} = 13.79 \% $$  | $$ \frac{2355}{4839} = \cancel{48.67\%} $$ | $$ \frac{1416}{4839} = 29.26\% $$   |

Had the conduit been 3½" or bigger, we would have no problem, this forces us fill our remaining cables from conduit 2 into conduit 1.


|     Param.        |Conduit 1 | Conduit 2 | Conduit 3  |
|-------------------|----------|-----------|------------|
Cable Area          |                                                          $$ 8.9 \text{mm}^2 $$                                                           | $$15.7 \text{mm}^2$$                  | $$ 354 \text{mm}^2$$              |
Total Cable area    | $$ 75 \cdot 8.9 = 667.5 \text{mm}^2$$ </br> $$27\cdot 15.7 = \underline{423.9 \text{mm}^2}$$ </br> $$ \hspace{1.5cm} 1091.4\text{mm}^2$$ | $$123 \cdot 15.7 = 1931.1\text{mm}^2$$| $$4 \cdot 354 = 1416 \text{mm}^2$$|
Conduit Area (100%) |                                                         $$ 4839\text{mm}^2 $$                                                            | $$ 4839 \text{mm}^2 $$                | $$ 4839\text{mm}^2 $$             |
Conduit Fill %      |                                                   $$ \frac{1091.4}{4839} = 22.55 \% $$                                                   | $$ \frac{1931.1}{4839} = 39.91\% $$   | $$ \frac{1416}{4839} = 29.26\% $$ |


## Other considerations

Conductors and cables suitable for conduit are listed as raceway cables in Table 19. In an industrial setting, armoured cable is very common. While typically ran in cable trays, they are allowed to be run through conduit. According to Rule 12-902, we can run armoured cable if one of the two cases are true;
- the length of the cable being pulled into the conduit does not exceed the maximum pulling tension or maximum sidewall bearing pressure
- the maximum length between draw-in points is
  - 15m for a three-conductor copper cable;
  - 45m for a single-conductor copper cable;
  - 35m for a three-conductor aluminum cable; or
  - 100m for a single-conductor aluminum cable.

When running high current armoured or metal-sheathed conductors it can induced a voltage across the sheath. Moreover, when metal objects are placed inadvertently nearby or as grounding points, a current can travel in this circuit, posing a safety risk. To reduce this safety risk, it is typically recommended to use non-magnetic or non-magnetic box connectors, locknuts, bushings, and insulating plates that are at least 6mm thick to cover the opening in magnetic material if passing through. 


---
## Appendix

### Related Knowledge File

[Knowledge File: Maximum Allowable Conductors/Cables in Conduit and Tubing]()

### Related OESC Rules

Rule 4-004 — Ampacity of Wires and Cables<br/>
Rule 12-902 — Types of insulated conductors and cables<br/>
Rule 12-904 — Conductors in Raceways<br/>
Rule 12-910 — Conductors in Conduit

### Related OESC Tables

Tables 9A-9G — Conduit areas at various percentages<br/>
Table 8 — Maximum allowable conduit fill percent<br/>
Table 19 — Conditions of use for Conductors and Cables
