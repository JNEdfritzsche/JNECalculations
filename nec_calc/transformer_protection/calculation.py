from __future__ import annotations

from typing import Any
from lib.nec_tables import NEC_2406A_FUSE, NEC_2406A_STANDARD, get_table_entry
from calc_common.enums import LocationTypes, ProtectionOptions
from calc_common.formatting import next_standard_size
from calc_common.units import Voltage

# How each table's Note 1 lets a calculated maximum be moved to a device rating.
NEXT_HIGHER = "Next higher standard rating (240.6)"
NEXT_LOWER = "Table maximum — no rounding up permitted"
COMMERCIAL = "Next higher commercially available rating"

# ----------------------------
# results helper functions
# ----------------------------
def _build_calc_result(OCPD: dict[str, Any], inputs: Any) -> dict[str, Any]:
    pri = OCPD.get("primary")
    sec = OCPD.get("secondary")

    return {
        "primary_cb": pri.get("cb"),
        "primary_fr": pri.get("fr"),
        "secondary_cb": sec.get("cb"),
        "secondary_fr": sec.get("fr"),
        "table_used": OCPD.get("table"),
        "row_criteria": OCPD.get("criteria"),
        **inputs,
    }


# ----------------------------
# calculator helper functions
# ----------------------------

def calc_voltage_class(V_primary: Voltage, V_secondary: Voltage) -> str:
    if V_primary <= 1000 and V_secondary <= 1000:
        return "low"
    else:
        return "high"

def calc_impedance_class(Z_percent):
    if Z_percent is None:
        return None

    if Z_percent >= 0 and Z_percent <= 6.0:
        return "low"
    elif Z_percent > 6.0 and Z_percent <= 10.0:
        return "high"
    else:
        return None


def _rounding_basis(table: str, mult: int | None, entry_key: str) -> str | None:
    """Which rounding each table's Note 1 actually permits for this cell.

    Table 450.5(B) Note 1 is written against "125 percent of this current", so the
    167%, 250% and 300% cells are hard maximums that may not be rounded up.
    Table 450.5(A) Note 1 permits the next higher rating for every cell, taken from
    240.6 at 1000 V and below and from commercially available ratings above that.
    """
    if mult is None:
        return None
    if table == "table_450_5_b":
        return NEXT_HIGHER if mult == 125 else NEXT_LOWER
    return NEXT_HIGHER if "1000 Volts or Less" in entry_key else COMMERCIAL


def _select_standard(size: float | None, basis: str | None, cb_fr: str) -> float | None:
    """The device rating to specify. None where 240.6 does not supply one."""
    if size is None or basis == COMMERCIAL:
        return None
    ratings = NEC_2406A_FUSE if cb_fr == "fr" else NEC_2406A_STANDARD
    return next_standard_size(size, ratings, "down" if basis == NEXT_LOWER else "up")


def _get_appropriate_table(voltage_class):
    if voltage_class == "low":
        return "table_450_5_b"
    else:
        return "table_450_5_a"


def _get_table_search_criteria(
    pri_sec,
    cb_fr_key,
    flas,
    flc_key,
    location_type,
    protection_method,
    tx_z,
    voltage_class,
    V_secondary,
    **kwargs,
    ) -> tuple[dict[str, Any], str | None]:

    criteria = {}
    entry_key = None
    flc = flas.get(flc_key)

    if voltage_class == "high":
        cb_fr = (
            "Circuit Breaker or Fuse Rating" if pri_sec == "Secondary" and V_secondary <= 1000
            else "Circuit Breaker" if cb_fr_key == "cb"
            else "Fuse Rating"
        )
    else:
        cb_fr = ""

    if voltage_class == "high":
        # PRIMARY FIRST
        if protection_method is not ProtectionOptions.PRIMARY_ONLY:
            if tx_z <= 6:
                criteria['Transformer Rated Impedance'] = "Not more than 6%"
            elif tx_z > 6 and tx_z <= 10:
                criteria['Transformer Rated Impedance'] = "More than 6% and not more than 10%"

        if location_type == LocationTypes.SUPERVISED:
            criteria['Location Limitations'] = "Supervised locations only"

            if protection_method == ProtectionOptions.PRIMARY_ONLY:
                criteria['Transformer Rated Impedance'] = "Any"

        else:
            criteria['Location Limitations'] = "Any location"

        if pri_sec == "Secondary":
            entry_key = " Protection over 1000 Volts - " if V_secondary > 1000 else " Protection 1000 Volts or Less - "
        else:
            entry_key = " Protection over 1000 Volts - "

    elif voltage_class == "low":
        entry_key = (
            " Protection - Currents Less Than 2 Amperes" if flc < 2 else (
                " Protection - Currents Less Than 9 Amperes" if flc < 9 else (
                    " Protection - Currents of 9 Amperes or More"
                )
            )
        )

        if flc_key == "primary_fla":
            criteria['Protection Method'] = "Primary only protection"

        elif flc_key == "secondary_fla":
            criteria['Protection Method'] = "Primary and secondary protection"

        # for table 450.5(B), secondary protection, there is no distinction between currents less than 2 amperes and currents less than 9 amperes
        if pri_sec == "Secondary" and flc < 9:
            entry_key = " Protection - Currents Less Than 9 Amperes"

    return criteria, pri_sec + entry_key + cb_fr


def _calc_protection(inputs: dict[str, Any]):
    OCPD = { "primary": { "cb": {}, "fr": {} }, "secondary": { "cb": {}, "fr": {} } }
    table = _get_appropriate_table(inputs.get("voltage_class"))
    flas = inputs.get("flas")

    for pri_sec in ["primary", "secondary"]:
        for cb_fr in ["cb", "fr"]:
            criteria, entry_key = _get_table_search_criteria(pri_sec.title(), cb_fr, **inputs)
            table_entry = get_table_entry(table, criteria, entry_key)

            if table_entry == "Not required":
                mult = None
                size = None
            else:
                mult = int(table_entry.strip("%"))
                size = flas.get(pri_sec + "_fla") * mult / 100

            basis = _rounding_basis(table, mult, entry_key)

            OCPD[pri_sec][cb_fr]["mult"] = mult
            OCPD[pri_sec][cb_fr]["size"] = size
            OCPD[pri_sec][cb_fr]["standard"] = _select_standard(size, basis, cb_fr)
            OCPD[pri_sec][cb_fr]["basis"] = basis
            OCPD[pri_sec][cb_fr]["column"] = entry_key

    OCPD["table"] = table
    OCPD["criteria"] = criteria
    return OCPD

def calc_transformer_protection(
    V_data,
    flas,
    protection_method,
    flc_key,
    location_type,
    tx_z,
    phase,
    transformer_rating,
    nameplate_used,
) -> dict[str, Any]:

    voltage_class = calc_voltage_class(**V_data)

    common_args = {
        **V_data,
        "flas": flas,
        "protection_method": protection_method,
        "flc_key": flc_key,
        "location_type": location_type,
        "tx_z": tx_z,
        "voltage_class": voltage_class,
        "phase": phase,
        "transformer_rating": transformer_rating,
        "nameplate_used": nameplate_used,
    }

    calc = _calc_protection(
        common_args
    )
    return _build_calc_result(
        calc,
        common_args,
    )