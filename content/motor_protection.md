Motor Protection

## Overview

Once motor feeder size has been determined, our next consideration is motor protectino devices. Motor protectino consists of three primary functions:

1. Overcurrent protection
2. Overload and overheating protection
3. Disconnecting means

## Overcurrent Devices 200s

When motors start, they pull a large inrush current, typically six times the FLC. Determining the correct fuse size and type can help avoid this nuisance tripping. 
The most common devices used are time-delay fuses, non-time-delay fuses. inverse-time (thermal-magnetic) circuit breakers, and instantaneous (magnetic-only) circuit breakers. As per rule 28-200 & 28-204, we generally size overcurrent device by Table 29 (and Table D16 which is based on Table 29) to a maximum of 300%. For protecting the conductors, the maximum fuse rating per conductor is the max ampacity of the conductor as per Rule 8.

Below is a general flow to follow for sizing overcurrent devices based on inputs. Note that for *any type of motor* that is protected by an instantaneous trip circuit breaker, the size must be circuit breaker must be sized to either the FLC by 13 or LRC by 2.15.

<!-- Flowchart method 28-4: Method to determine max overcurrent device size for an individual motor -->

For sizing the overcurrent device for a feeder supplying multiple motors, the methodology is similar to conductor sizing feeders. You size the largest FLC accordingly by table 29, then sum that adjusted FLC with the other nominal FLCs to size the main feeder. 

For example, say you have three motors, with the following characteristics

| Motor No. | Fuse Type  | FLC |
|-----------|------------|-----|
| $${M_1}$$ | Time-delay | 62  |
| $${M_2}$$ | Time-delay | 27  |
| $${M_3}$$ | Time-delay | 11  |

To size each motor's overcurrent device, we would apply the factor from Table 29 for each line.

| Motor No. | Ampere Target| Closest Fuse Rating |
|-----------|--------------|---------------------|
| $${M_1}$$ | 62 \cdot 1.75 = 108.5 A | 100 A |
| $${M_2}$$ | 27 \cdot 1.75 = 47.25 A | 45 A  |
| $${M_3}$$ | 11 \cdot 1.75 = 19.25 A | 15 A  |

To size the feeder supplying all these motors, we adjust the largest FLC in the circuit, and add the remaining FLCs to size our overcurrent device.

| Device Type | Ampere Target| Closest Fuse Rating |
|-------------|--------------|---------------------|
| Non-time-delay fuse | (62 \cdot 3) + 27 + 11 = 200 A |
| Time-delay fuse | (62 \cdot 1.75) + 27 + 11 = 125 A |
| Circuit Breaker | (62 \cdot 2.5) + 27 + 11 = 150 A |

## overload & overheating protection 300s

Overloading and overheating protection devices are sized according to motor's nameplate current rating. If the service rating is > 1.15 then size by a factor 1.25, other size by factor of 1.15. Consult Table 25 for number of and where to places devices based on system.

## control(/starters?) 500s

All motors require starters/controllers, they must be of the correct rating in HP equal or greater than the motor itself. not required as per 28-500 3)

## Disconnecting Means 600s

Rules generally cover different situations and cases where starters and disconnects are used interchangeably, e.g. using a starter as a the sole  disconnect if the situation meets a certain criteria, but in general it is best to have a proper disconnect for each motor. Location is the main one, when typically placed at the distribution centre they can serve as the main source of de-energizing the circuit when; within sight of and 9m of motor or machinery driven by motor, or be able to be locked in open and is labelled with the loads connected to it.

## Motor not starting

As we saw in the first section, we aim to chose a fuse size as close as we can to the adjusted FLC. Sometimes we are limited to standard fuse sizes which could be well below this target, which might not allow our motor to start. Furthermore, all these calculations are based on the assumption that not all the motors will be starting simultaneously. Though typically in the past 15 years, most industrial motors come with soft starters of VFds, so motor not starting due to nuissance tripping is not as big of a concern anymore.

# General rules
As a general rule of thumb, we can follow Figure 1 below as a quick guide to choosing devices for different motors. 

<div align="center">

![Figure 1: Quick Guide to Choosing Motor Protection Devices](images/MotorProtectDeviceGuide.png)

</div>

<!--
## Special motors
RLC for compressors
-->

# Appendix

## Related OESC Rules

Rule 28-200: Branch circuit overcurrent protection
Rule 28-202: Feeder circuit overcurrent protection
Rule 28-200


## Related OESC Tables

Table 13
Table 29
Table 25
Table D16

