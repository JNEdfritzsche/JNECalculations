from __future__ import annotations

import math
from enum import Enum


class LabeledEnum(Enum):
    @classmethod
    def exclude(cls, members=()):
        if isinstance(members, cls):
            members = (members,)
        return [m for m in cls if m not in members]
    
    def __init__(self, label: str, key: str):
        self.label = label
        self.key = key


class SystemTypes(LabeledEnum):
    DC = ("DC", "dc", 1.0, 2.0)
    SINGLE_PHASE = ("1φ AC", "single_phase", 1.0, 2.0)
    THREE_PHASE = ("3φ AC", "three_phase", math.sqrt(3), math.sqrt(3))
    
    def __init__(self, label, key, current_factor, vd_factor):
        super().__init__(label, key)
        self.current_factor = current_factor
        self.vd_factor = vd_factor
        
    def get_latex_factor(self, attr: str = "vd_factor") -> str:
        value = getattr(self, attr)
        if abs(value - math.sqrt(3)) < 1e-9:
            return r"$\sqrt{3}$"
        return f"{value:g}"


class VDMode(LabeledEnum):
    TABLE8_R = ("Resistance Method (NEC: Chapter 9, Table 8)", "table8_r")
    TABLE9_Z = ("AC Impedance Method (NEC: Chapter 9, Table 9)", "table9_z")
    MANUAL_R = ("Manual Resistance", "manual_r")
    
class ConduitMaterial(LabeledEnum):
    PVC   = ("PVC", "pvc")
    AL    = ("Aluminum", "al")
    STEEL = ("Steel", "st")

class CopperCoating(LabeledEnum):
    UNCOATED = ("Uncoated", "uncoated")
    COATED   = ("Coated (Tinned)", "coated")

class ConductorMaterial(LabeledEnum):
    AL  = ("Aluminum", "al")
    CU  = ("Copper", "cu")
    NA  = ("Not specified", None)

class TransformerSourceOptions(LabeledEnum):
    CALCULATED = ("Calculate FLCs", "use_calc")
    NAMEPLATE = ("Use nameplate FLAs", "use_nameplate")

class ProtectionOptions(LabeledEnum):
    PRIMARY_ONLY = ("Primary only", "pri")
    PRIMARY_SECONDARY = ("Primary & Secondary", "p&s")
    
class LocationTypes(LabeledEnum):
    ANY = ("Any", "any")
    SUPERVISED = ("Supervised", "supervised")
    
class ServiceFactors(LabeledEnum):
   HIGH = ("1.25 (High SF)", 1.25)
   STANDARD = ("1.15 (Standard)", 1.15)
   UNITY = ("1.0 (Unity / Low SF)", 1.0) 

__all__ = [
    "LabeledEnum", "SystemTypes", "VDMode", "ConduitMaterial",
    "CopperCoating", "ConductorMaterial", "TransformerSourceOptions",
    "ProtectionOptions", "LocationTypes", "ServiceFactors"
]