## Overview

Voltage drop must be taken into consideration, especially for long runs.  
In Ontario, the limit is 3% for feeder or branch circuits and 5% from the customer’s point of utilization, according to **OESC Rule 8-102**.

To accommodate this, conductor sizing must be large enough for the given distance, since voltage loss is proportional to conductor impedance and length.

For the following calculations, **Table D3 and Table F** are referenced.

> _Insert Table D3 & F here_

---

## Finding Voltage Drop

Voltage drop is typically expressed as a percentage.

$$
\Delta V \% = \frac{V_D}{V_{nom}} \cdot 100
$$

The voltage drop value is calculated using the following equation:
### Formula

$$
V_D = \frac{k \cdot f \cdot I \cdot L}{1000} 
$$

##### Where

- **k** = Table D3 voltage drop factor, Ω/km 
- **f** = system/connection factor  
- **I** = load current, A 
- **L** = one‑way length, m

This equation assumes you already selected a conductor size and are verifying that the resulting voltage drop meets code limits.

---

## Finding Conductor Size and/or Length

If determining the required conductor size or maximum allowable length for a specified voltage drop, rearranged as needed:

### Conductor sizing (solve for k)

$$
k \leq \frac{V_D \cdot 1000}{I \cdot L \cdot f}
$$

### Maximum length (solve for L)

$$
L \leq \frac{V_D \cdot 1000}{I \cdot K \cdot f}
$$

---

## References

- [Design Basis – Calculations: Motor Feeder](file://jnecon.jnepeng.com/data/Common/Electrical/Electrical%20Calculations/REV%20B/)
- [Knowledge File – OESC: Section 4 Conductors](file:///H:/Electrical/OESC%20Introduction%20Manual/SECTION%204%20-%20CONDUCTORS%20-%20Nikola/)
