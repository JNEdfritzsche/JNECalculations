# Overview

The Transformer Protection section describes the OESC intent and design principles for overcurrent protection to maintain operability of a typical transformer. The OESC classifies three main groups of transformer circuits, each with its own associated design rules. This section focuses on the sizing of the fuses and breakers used to protect the transformer, cable sizing can be found in the Transformer Feeders section of this website. The general layout of a transformer with primary-side overcurrent protection can be seen below.

<div align="center">

![Figure 1: Example Motor Protection](images/Transformer_Protection.png)

</div>

*Figure 1: Transformer Protection*
<br>

## Transformer Circuit Classifications:
There are 3 main types of transformer tircuits outlined in OESC Section 26-250, 26-252, and 26-254:
- Circuits rated over 750 V
- Circuits rated 750 V or less, other than dry-type transformers
- Dry-type transformer circuits rated 750 V or less

Circuits over 750 V are treated as high-voltage systems; at this level, arc-flash energy, insulation stress, and fault consequences increase significantly. The focus with these systems is on safety rather than equipment convenience. Non-dry transformers at low voltage pose a fire and environmental risk due to the presence of insulating liquid - one must account for leakage, ignition, and heat dissipation. Finally, dry type transformers at low voltages pose the lowest overall risk with risks being primarily electrical rather than fire-related. When considering the application of the transformer and which type of cooling it will use there are two main options:
- 1. Oil-Cooled Transformers (Rules 26-250 & 26-252):
  - Typically used in either outdoor or higher voltage systems due to being fully enclosed alongside better cooling capabilities
  - Higher cost and require additional maintenance
- 2. Dry-type Transformers (Rule 26-254):
  - Common in indoor and lower voltage applications
  - Require less maintenance and are often cheaper
  - Lower capacity due to inferior heat dissipation with respect to oil-cooled systems

### Transformer Circuits Rated Over 750 V
Each ungrounded conductor of the transformer feeder or branch circuit supplying the transformer shall be provided with overcurrent protection:
- a. rated at not more than 150% of the rated primary current of the transformer in the case of fuses; and 
- b. rated or set at not more than 300% of the rated primary current of the transformer in the case of breakers.
The OESC outlines some exceptions to this rule in subrules 2-4 of section 26-250.

### Non-Dry Type Transformer Circuits Rated Under 750 V
Each ungrounded conductor of the transformer feeder or branch circuit supplying the transformer shall be provided with overcurrent protection rated or set at not more than 150% of the rated primary current of the transformer. The OESC outlines some exceptions to this rule in subrules 2-6 of section 26-252.

### Dry Type Transformer Circuits Rated Under 750 V
Each ungrounded conductor of the transformer feeder or branch circuit supplying the transformer shall be provided with overcurrent protection rated or set at not more than 125% of the rated primary current of the transformer, and this primary overcurrent device shall be considered as protecting secondary conductors rated at not less than 125% of the rated secondary current. The OESC outlines an exception to this rule in subrules 2-3 of section 26-254.

## Other Considerations

### Maximum Circuit Loading
OESC Section 8-104 states that the ampere rating of a consumer’s service, feeder, or branch circuit shall be the lesser of the rating of the overcurrent device protecting the circuit or the ampacity of the conductors. It also says that the calculated load in a circuit shall not exceed the ampere rating of the circuit. The calculated load in a consumer's service, feeder, or branch circuit shall be considered a continuous load unless it can be shown that in normal operation it will not persist for:
- a. a total of more than 1 h in any 2 h period if the load does not exceed 225 A; or
- b. a total of more than 3 h in any 6 h if the load exceeds 225 A.

### Fuses vs Breakers
While creating the design, the engineer should consider the cost comparisons, availability of units, the total load size, and what the devices are protecting. Circuit breakers are typically used on higher value assets for tighter regulation and to prevent one phase tripping which may happen with fuses. Fuses are often less expensive and used for lower voltage or remote applications of transformers.

### Transformer Connection Types
Another thing to consider is how the transformer windings are configured. The possible connections are Delta-Delta (Dd), Wye-Wye (Yy), Wye-Delta (Yd), Delta-Wye (Dy). Typically you will see the Delta-Wye connection as it is commonly used in low power distribution; the Delta windings provide a balanced load for the utility company while the Wye connection provides a 4th-wire neutral connection for the secondary side. The designer should also consider how the secondary side will be grounded (Open, Solid Ground, or Neutral Ground Resistor).

# Example

## Assumptions
- The ambient temperature is 40 °C
- The conductor temperature is 75 °C
- The conductor is copper routed in free-air
- No more than 3 conductors per cable, complete with ground
- The maximum cable length is 50m
- Transformer is operating with natural cooling (no fans/pumps)<br/>
<br>

## 1. Oil-Cooled > 750 V

### Transformer Nameplate Data

| Parameter           | Value     |
|---------------------|-----------|
| Rating              | 2000 kVA  |
| Primary Voltage     | 27.6 kV   |
| Secondary Voltage   | 600 V     |
| Phase               | 3         |
| Frequency           | 60 Hz     |

### Full-Load Currents

$$
I = \frac{S}{\sqrt{3}\,V}
$$

| Side           | Calculation | Result (A) |
|----------------|-------------|------------|
| Primary FLA    | $$ \frac{2000 \times 10^3}{\sqrt{3} \times 27.6 \times 10^3} $$ | 41.89 |
| Secondary FLA  | $$ \frac{2000 \times 10^3}{\sqrt{3} \times 600} $$ | 1926.78 |

### Overcurrent Protection Sizing

| Protection Type | OESC Multiplier | Primary Calculation | Primary (A) | Secondary Calculation | Secondary (A) |
|-----------------|-----------------|---------------------|-------------|-----------------------|---------------|
| Fuses           | 1.50 | $$ 41.89 \times 1.50 $$ | 62.83 | $$ 1926.78 \times 1.50 $$ | 2890.17 |
| Circuit Breaker | 3.00 | $$ 41.89 \times 3.00 $$ | 125.66 | $$ 1926.78 \times 3.00 $$ | 5780.35 |

## 5. Oil-Cooled < 750 V

### Transformer Nameplate Data

| Parameter           | Value     |
|---------------------|-----------|
| Rating              | 75 kVA    |
| Primary Voltage     | 600 V     |
| Secondary Voltage   | 208 V     |
| Phase               | 3         |
| Frequency           | 60 Hz     |

### Full-Load Currents

$$
I = \frac{S}{\sqrt{3}\,V}
$$

| Side           | Calculation | Result (A) |
|----------------|-------------|------------|
| Primary FLA    | $$ \frac{75 \times 10^3}{\sqrt{3} \times 600} $$ | 72.17 |
| Secondary FLA  | $$ \frac{75 \times 10^3}{\sqrt{3} \times 208} $$ | 208.43 |

### Overcurrent Protection Sizing  
*(OESC Rule 26-252-1)*

| Protection Type | OESC Multiplier | Primary Calculation | Primary (A) | Secondary Calculation | Secondary (A) |
|-----------------|-----------------|---------------------|-------------|-----------------------|---------------|
| Overcurrent Protection | 1.50 | $$ 72.17 \times 1.50 $$ | 108.26 | $$ 208.43 \times 1.50 $$ | 312.65 |

## 6. Dry-Type < 750 V

### Transformer Nameplate Data

| Parameter           | Value     |
|---------------------|-----------|
| Rating              | 75 kVA    |
| Primary Voltage     | 600 V     |
| Secondary Voltage   | 208 V     |
| Phase               | 3         |
| Frequency           | 60 Hz     |

### Full-Load Currents

$$
I = \frac{S}{\sqrt{3}\,V}
$$

| Side           | Calculation | Result (A) |
|----------------|-------------|------------|
| Primary FLA    | $$ \frac{75 \times 10^3}{\sqrt{3} \times 600} $$ | 72.17 |
| Secondary FLA  | $$ \frac{75 \times 10^3}{\sqrt{3} \times 208} $$ | 208.43 |

### Overcurrent Protection Sizing  
*(OESC Rule 26-254-1)*

| Protection Type | OESC Multiplier | Primary Calculation | Primary (A) | Secondary Calculation | Secondary (A) |
|-----------------|-----------------|---------------------|-------------|-----------------------|---------------|
| Overcurrent Protection | 1.25 | $$ 72.17 \times 1.25 $$ | 90.21 | $$ 208.43 \times 1.25 $$ | 260.54 |

### Timed Overcurrent Requirement  
*(OESC Rule 26-254 — Additional Performance Criteria)*

This overcurrent device must also satisfy **both** of the following conditions:

a) Carry **12 × transformer rated primary full-load current** for **0.1 s**  
b) Carry **25 × transformer rated primary full-load current** for **0.01 s**

#### Timed Trip Current Calculations

| Parameter | Description                                              | Value   |
|----------|----------------------------------------------------------|---------|
| Primary FLA | Transformer Primary Full-Load Current (A)             | 72.17   |
| Multiplier (0.1 s) | OESC Rule 26-254 Requirement (×)               | 12      |
| Multiplier (0.01 s) | OESC Rule 26-254 Requirement (×)              | 25      |

| Condition | Calculation | Result (A) |
|----------|-------------|------------|
| 12× FLA @ 0.1 s | $$ 72.17 \times 12 $$ | 866.04 |
| 25× FLA @ 0.01 s | $$ 72.17 \times 25 $$ | 1804.25 |

## Conclusion

Based on the calculated primary full-load currents and applicable OESC rules, the required primary overcurrent protection device sizes are as follows:

**2 MVA, 27.6 kV / 600 V, Oil-Cooled, Direct Primary Protected Transformer**
- 70 A rated fuse  
- 150 A rated circuit breaker  

**75 kVA, 600 V / 208 V, Oil-Cooled, Direct Primary Protected Transformer**
- 110 A rated circuit breaker or fuse  

**75 kVA, 600 V / 208 V, Dry-Type, Direct Primary Protected Transformer**
- 100 A rated circuit breaker or fuse

# Appendix

## Related OESC Rules
Rule 8-104

## Related OESC Tables
Table 13
