## Overview

This section walks through worked examples for voltage drop calculations using OESC Appendix D. The goal is to demonstrate how to select the correct k-value, temperature multiplier, and system factor for different circuit types. For theory and methodology, refer to the theory tab.

The core formula is the same for every case:

$$V_D = \frac{k \cdot f \cdot I_{\text{eff}} \cdot L}{1000} \qquad \%\Delta V = \frac{V_D}{V_{\text{nom}}} \times 100\%$$

Where $k$ is the adjusted resistance factor (Ω/km), $f$ is the system factor from Appendix D, $I_{\text{eff}}$ is the current per conductor (A), and $L$ is the one-way length (m).

---

## Example 1 — 1φ AC Cable, Temperature-Adjusted k

**240 V, 1φ | 50 A | Cable | 60 m | 60 °C operating | 90% PF | #1 AWG – 2/C | Copper**

Operating at 60 °C, so the base k-value from Table D3 must be adjusted downward. The system factor $f = 2$ applies for a 1φ 3-wire line-to-line circuit.

| Symbol | Description | Value |
|--------|-------------|-------|
| $k_{\text{base}}$ | Table D3, Cable 90% PF column, #1 AWG | 0.512 Ω/km |
| $k_{\text{mult}}$ | Temperature multiplier — 60 °C | 0.95 |
| $k$ | Adjusted k-value | 0.4864 Ω/km |
| $f$ | System factor — 1φ, 3-wire, L-L | 2 |
| $I_{\text{eff}}$ | Current per conductor | 50 A |
| $L$ | One-way length | 60 m |
| $V_{\text{nom}}$ | Nominal voltage | 240 V |

$$k = k_{\text{base}} \times k_{\text{mult}} = 0.512 \times 0.95 = 0.4864 \text{ Ω/km}$$

$$V_D = \frac{0.4864 \times 2 \times 50 \times 60}{1000} = 2.918 \text{ V}$$

$$\%\Delta V = \frac{2.918}{240} \times 100\% = 1.216\%$$

**Result: V_D = 2.92 V &nbsp;|&nbsp; %ΔV = 1.22%**

---

## Example 2 — 3φ AC Raceway, No Temperature Adjustment

**600 V, 3φ | 100 A | Raceway | 120 m | 75 °C operating | 80% PF | #3 AWG – 1/C | Copper**

Operating at 75 °C, which is the Table D3 base temperature, so no temperature adjustment is needed. The system factor $f = \sqrt{3}$ applies for a 3φ 3-wire line-to-line circuit.

| Symbol | Description | Value |
|--------|-------------|-------|
| $k_{\text{base}}$ | Table D3, Raceway 80% PF column, #3 AWG | 0.792 Ω/km |
| $k_{\text{mult}}$ | Temperature multiplier — 75 °C (base) | 1.00 |
| $k$ | Adjusted k-value | 0.792 Ω/km |
| $f$ | System factor — 3φ, 3-wire, L-L | $\sqrt{3}$ = 1.732 |
| $I_{\text{eff}}$ | Current per conductor | 100 A |
| $L$ | One-way length | 120 m |
| $V_{\text{nom}}$ | Nominal voltage | 600 V |

$$k = 0.792 \times 1.00 = 0.792 \text{ Ω/km}$$

$$V_D = \frac{0.792 \times 1.732 \times 100 \times 120}{1000} = 16.46 \text{ V}$$

$$\%\Delta V = \frac{16.46}{600} \times 100\% = 2.74\%$$

**Result: V_D = 16.46 V &nbsp;|&nbsp; %ΔV = 2.74%**

---

## Example 3 — DC Circuit, Temperature-Adjusted k, Aluminum

**125 V, DC | 80 A | DC | 25 m | 90 °C operating | #3 AWG – 2/C | Aluminum**

DC circuits use the DC column from Table D3 — no power factor column applies. Operating at 90 °C, so k is adjusted upward. The system factor $f = 2$ applies for a DC 2-wire positive-to-ground circuit.

| Symbol | Description | Value |
|--------|-------------|-------|
| $k_{\text{base}}$ | Table D3, DC column, #3 AWG, Aluminum | 1.3 Ω/km |
| $k_{\text{mult}}$ | Temperature multiplier — 90 °C | 1.05 |
| $k$ | Adjusted k-value | 1.365 Ω/km |
| $f$ | System factor — DC, 2-wire, positive-to-ground | 2 |
| $I_{\text{eff}}$ | Current per conductor | 80 A |
| $L$ | One-way length | 25 m |
| $V_{\text{nom}}$ | Nominal voltage | 125 V |

$$k = k_{\text{base}} \times k_{\text{mult}} = 1.3 \times 1.05 = 1.365 \text{ Ω/km}$$

$$V_D = \frac{1.365 \times 2 \times 80 \times 25}{1000} = 5.46 \text{ V}$$

$$\%\Delta V = \frac{5.46}{125} \times 100\% = 4.37\%$$

**Result: V_D = 5.46 V &nbsp;|&nbsp; %ΔV = 4.37%**

---

## Appendix

### Related Knowledge Files

[Knowledge File — OESC: Section 4 Conductors](https://jnepeng.sharepoint.com/:b:/s/JNEElectricalPortalTeams/IQBX__AeZwFdTaYRIpekMk53AST1Z1fmbLyJuMdhL2C3csc?e=siODjS) </br>
[Design Basis – Calculations: Motor Feeder](https://jnepeng.sharepoint.com/:w:/s/JNEElectricalPortalTeams/IQAJQj9NgJoFQZ1Cka91W7FrAU1C4cOQc2NbIUe-6dugX7o?e=4OlqCj)

### Related OESC Rules

Rule 8-102 — Voltage drop limitations<br/>

### Related OESC Tables

Table D3 — K-values for calculating voltage drop 
