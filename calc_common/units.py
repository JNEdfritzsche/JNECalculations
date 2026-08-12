from __future__ import annotations

from enum import Enum
from dataclasses import dataclass
from typing import ClassVar


class MetricPrefix(Enum):
    MILLI = ("m", 1e-3)
    UNIT  = ("",  1.0)
    KILO  = ("k", 1e3)
    MEGA  = ("M", 1e6)

    def __init__(self, prefix: str, factor: float):
        self.prefix = prefix
        self.factor = factor
        
    
@dataclass(frozen=True) 
class _Quantity:
    value: float
    base_symbol: ClassVar[str] = ""

    @classmethod
    def of(cls, value: float, prefix: MetricPrefix = MetricPrefix.UNIT):
        return cls(value * prefix.factor) 

    def to(self, prefix: MetricPrefix = MetricPrefix.UNIT) -> float:
        return self.value / prefix.factor

    def display(self, prefix: MetricPrefix = MetricPrefix.UNIT) -> str:
        return f"{self.to(prefix):g} {prefix.prefix}{self.base_symbol}"
    
    @classmethod
    def unit(cls, prefix: MetricPrefix = MetricPrefix.UNIT) -> str:
        return f"{prefix.prefix}{cls.base_symbol}"


@dataclass(frozen=True)
class Voltage(_Quantity): base_symbol: ClassVar[str] = "V"
@dataclass(frozen=True)
class Current(_Quantity): base_symbol: ClassVar[str] = "A"
@dataclass(frozen=True)
class ApparentPower(_Quantity): base_symbol: ClassVar[str] = "VA"

__all__ = ["MetricPrefix", "_Quantity", "Voltage", "Current", "ApparentPower"]
