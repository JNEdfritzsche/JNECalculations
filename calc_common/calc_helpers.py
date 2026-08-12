from __future__ import annotations
from typing import Any, overload

from lib.nec_tables import TABLES

def _rated_current(S, V_L, phase_factor):
    return abs(S / (V_L * phase_factor))

def calc_fla(S, phase_factor, voltage):
    return _rated_current(S, voltage, phase_factor)

# def calc_flas(S, phase_factor, voltages: dict[str, float]):
#     fla = {}
#     for v in voltages.keys():
#         fla[str(v)] = calc_fla(S, phase_factor, voltages.get(v))
#     return fla

def calc_flas(inputs: dict[str, Any]) -> dict[str, float]:
    fla = {} 
    for v_key, v_val in inputs["V_data"].items():
        key = "primary_fla" if "primary" in v_key else "secondary_fla" if "secondary" in v_key else "fla"
        
        fla[key] = calc_fla(
            inputs["transformer_rating"],
            inputs["current_factor"],
            v_val,
        )
        
    return fla


# ----------------------------
# Table Helpers
# ----------------------------

def get_table_entry(
    table: str,
    criteria: dict[str, Any],
    entry_key: str
) -> Any | None:
    """One cell out of a table, found by matching criteria against its rows.

    The table id, the criteria columns and the wanted column are all named as strings, and
    several of them are assembled at runtime, so each one is checked and reported by name.
    Returning None for a typo would leave the calculator showing a blank with no clue why.
    """
    table_id = table
    table = TABLES.get(table_id)
    if table is None:
        raise KeyError(
            f"no NEC table '{table_id}'. Tables are: {sorted(TABLES)}"
        )

    columns = table.get("columns") or []
    unknown = [key for key in list(criteria) + [entry_key] if key not in columns]
    if unknown:
        raise KeyError(
            f"{table.get('title', table_id)}: no column {unknown}. "
            f"Columns are: {columns}"
        )

    row = None
    for r in table["rows"]:
        if all(r.get(key) == value for key, value in criteria.items()):
            row = r
    return row[entry_key] if row else None
        

  