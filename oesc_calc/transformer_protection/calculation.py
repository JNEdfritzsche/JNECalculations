from __future__ import annotations

import math
from typing import Any

from calc_common.formatting import next_standard
from lib import oesc_tables

THREE_PHASE = "3Φ"
SINGLE_PHASE = "1Φ"
PHASES = (THREE_PHASE, SINGLE_PHASE)

OIL = "Oil-cooled (non-dry)"
DRY = "Dry-type"
TRANSFORMER_TYPES = (OIL, DRY)

OVER_750 = "> 750 V"
UPTO_750 = "≤ 750 V"
VOLTAGE_CLASSES = (OVER_750, UPTO_750)

PRIMARY_ONLY = "Primary only"
PRIMARY_AND_SECONDARY = "Primary & Secondary (P&S)"
PROTECTION_CONFIGS = (PRIMARY_ONLY, PRIMARY_AND_SECONDARY)

Z_MAX = 10.0
Z_LOW_BAND = 7.5

INRUSH_CHECKS = ((12, 0.1), (25, 0.01))


def full_load_current(kva: float, volts: float, phase: str) -> float | None:
    s_va = float(kva) * 1000.0
    v = float(volts)
    if v <= 0:
        return None
    return s_va / (math.sqrt(3) * v) if phase == THREE_PHASE else s_va / v


def oil_primary_multiplier(ip: float) -> tuple[float, str, str]:
    if ip < 2.0:
        return 3.00, "Ip < 2A", "Ip < 2 A — up to 300% permitted."
    if ip < 9.0:
        return 1.67, "Ip 2–9A", "Ip < 9 A — up to 167% permitted."
    return 1.50, "Ip > 9A", (
        "Ip ≥ 9 A — up to 150% permitted; if not a standard size, next higher standard permitted."
    )


def _device(label: str, raw: float | None, round_to_std: bool, reference: bool = False) -> dict[str, Any]:
    """reference marks a figure shown for information only, not a device the rule requires."""
    selected = next_standard(raw, oesc_tables.STANDARD_DEVICE_RATINGS) if round_to_std else None
    return {"label": label, "raw": raw, "selected": selected, "reference": reference}


TABLE_50_DEVICES = (
    ("Max Primary Fuse", "Maximum primary fuse rating", "Ip"),
    ("Max Primary Breaker", "Maximum primary breaker setting", "Ip"),
    ("Max Secondary Fuse", "Maximum secondary fuse rating", "Is"),
    ("Max Secondary Breaker", "Maximum secondary breaker setting", "Is"),
)


def _over_750(ip, is_, vsec, prot_config, z_pct, round_to_std):
    if prot_config == PRIMARY_ONLY:
        band, band_label = oesc_tables.TABLE_50_ANY, ""
    elif z_pct > Z_MAX:
        error = (
            f"Z = {z_pct:.2f}% exceeds 10%: Table 50 (Rule 26-250) does not cover this "
            "impedance range for the P&S configuration. Consult OESC Rule 26-250 directly."
        )
        return [], f"26-250 (>750V) — P&S, Z={z_pct:.2f}% (7.5–10%)", error
    elif z_pct <= Z_LOW_BAND:
        band, band_label = oesc_tables.TABLE_50_Z_LOW, f", Z={z_pct:.2f}% (≤ 7.5%)"
    else:
        band, band_label = oesc_tables.TABLE_50_Z_HIGH, f", Z={z_pct:.2f}% (7.5–10%)"

    secondary_class = (
        oesc_tables.TABLE_50_SEC_OVER_750 if vsec > 750 else oesc_tables.TABLE_50_SEC_UPTO_750
    )
    config_label = "Primary only" if prot_config == PRIMARY_ONLY else "P&S"
    rule_path = f"26-250 (>750V) — {config_label}{band_label}"

    row = oesc_tables.get_table_50_row(prot_config, band, secondary_class)
    if row is None:
        return [], rule_path, "Table 50 (Rule 26-250) has no row for this combination."

    devices: list[dict[str, Any]] = []
    for label, column, current_symbol in TABLE_50_DEVICES:
        pct = row.get(column)
        if pct is None:
            continue
        current = ip if current_symbol == "Ip" else is_
        devices.append(_device(
            f"{label} ({pct:g}% × {current_symbol})", pct / 100.0 * current, round_to_std))

    return devices, rule_path, None


def _upto_750(ip, is_, xfmr_type, prot_config, round_to_std):
    is_dry = xfmr_type == DRY
    rule_ref = "26-254" if is_dry else "26-252"
    devices: list[dict[str, Any]] = []

    if prot_config == PRIMARY_ONLY:
        if is_dry:
            devices.append(_device("Max Primary OCPD (125%)", 1.25 * ip, round_to_std))
            devices.append(_device("Secondary @ 125% (reference)", 1.25 * is_, round_to_std, reference=True))
            return devices, f"{rule_ref} (≤750V) — Primary only", None

        multiplier, band, _reason = oil_primary_multiplier(ip)
        devices.append(_device(f"Max Primary OCPD ({multiplier:.2f}×)", multiplier * ip, round_to_std))
        devices.append(_device(f"Secondary @ {multiplier:.2f}× (reference)", multiplier * is_, round_to_std, reference=True))
        return devices, f"{rule_ref} (≤750V) — Primary only ({band})", None

    devices.append(_device("Max Secondary OCPD (125% of secondary FLA)", 1.25 * is_, round_to_std))
    devices.append(_device("Max Primary Feeder OCPD (300% of primary FLA)", 3.00 * ip, round_to_std))
    return devices, f"{rule_ref} (≤750V) — P&S", None


def calc_transformer_protection(
    phase: str,
    kva: float,
    vpri: float,
    vsec: float,
    xfmr_type: str,
    voltage_class: str,
    prot_config: str,
    z_pct: float | None,
    round_to_std: bool,
    use_nameplate: bool = False,
    nameplate_ip: float | None = None,
    nameplate_is: float | None = None,
) -> dict[str, Any]:
    if use_nameplate:
        ip, is_ = nameplate_ip, nameplate_is
    else:
        ip, is_ = full_load_current(kva, vpri, phase), full_load_current(kva, vsec, phase)

    if ip is None or is_ is None:
        devices, rule_path, error = [], "", "Primary/Secondary FLA could not be computed."
    elif voltage_class == OVER_750:
        devices, rule_path, error = _over_750(ip, is_, vsec, prot_config, z_pct, round_to_std)
    else:
        devices, rule_path, error = _upto_750(ip, is_, xfmr_type, prot_config, round_to_std)

    result = {
        "phase": phase,
        "kva": kva,
        "vpri": vpri,
        "vsec": vsec,
        "use_nameplate": use_nameplate,
        "xfmr_type": xfmr_type,
        "voltage_class": voltage_class,
        "prot_config": prot_config,
        "z_pct": z_pct,
        "round_to_std": round_to_std,
        "Ip": ip,
        "Is": is_,
        "devices": devices,
        "rule_path": rule_path,
        "error": error,
        # Rules 26-252 and 26-254 state their multipliers in the rule text, so those
        # rows cite the rule rather than a table.
        "rule_ref": "26-250" if voltage_class == OVER_750 else ("26-254" if xfmr_type == DRY else "26-252"),
        "primary_table": "50" if voltage_class == OVER_750 else None,
        "source_tables": ["50"] if voltage_class == OVER_750 else [],
    }

    if voltage_class == UPTO_750 and xfmr_type == DRY and ip is not None:
        result["inrush_12x"] = ip * 12
        result["inrush_25x"] = ip * 25

    return result
