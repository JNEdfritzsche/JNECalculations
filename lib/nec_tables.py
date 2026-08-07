from __future__ import annotations

from typing import Any, List
import re

from nec_calc.common.table_helpers import get_table_row
from lib.nec_table_loader import (
    TABLES,
    nec_group,
    nec_table,
)

# ----------------------------
# Helpers
# ----------------------------
def get_standard_conductor_sizes_unitless(table: dict[str, dict[str, Any]]) -> List[str] | None:
    if not table:
        return None
    
    sizes = []

    for row in table['rows']:
        size = row.get('size_awg_kcmil')
        if size not in sizes:
            sizes.append(size)
    
    if not sizes:
        return None
    
    return sizes

def get_standard_conductor_sizes(table: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    if not table:
        return None

    sizes = {}

    for size in get_standard_conductor_sizes_unitless(table):
        unit = None

        if size.isnumeric() and int(size) >= 250:
            unit = ' kcmil'
        else:
            unit = ' AWG'
        
        sizes[size + unit] = size
    
    return sizes

# --------------------------------------------------------------------------------------
# Table 1: Percent of Cross Section of Conduit and Tubing for Conductors and Cables
# --------------------------------------------------------------------------------------

TABLE_1 = nec_table("table_1")

CONDUCTOR_COUNT_PATTERN = re.compile(r'^(Over\s+)?(\d+)$', re.I)

def get_cross_sectional_area_percent(conductors_cables_n):
    # The table states its own condition in the wording the codebook prints: a bare count
    # means exactly that many conductors, 'Over 2' means more than two.
    for row in TABLE_1['rows']:
        match = CONDUCTOR_COUNT_PATTERN.match(str(row['number_of_conductors_cables']).strip())
        if not match:
            continue

        over, threshold = match.group(1), int(match.group(2))
        is_match = conductors_cables_n > threshold if over else conductors_cables_n == threshold

        if is_match:
            return int(row['cross_sectional_area_percent'])

    return None

# --------------------------------------------------------------------------------------
# Table 2: Radius of Conduit and Tubing Bends
# --------------------------------------------------------------------------------------

TABLE_2 = nec_table("table_2")

# --------------------------------------------------------------------------------------
# Chapter 9: Table 4
# --------------------------------------------------------------------------------------


TABLE_4_EMT                  = nec_table("table_4_emt",                  group="table_4")
TABLE_4_ENT                  = nec_table("table_4_ent",                  group="table_4")
TABLE_4_FMC                  = nec_table("table_4_fmc",                  group="table_4")
TABLE_4_IMC                  = nec_table("table_4_imc",                  group="table_4")
TABLE_4_LFNC_A               = nec_table("table_4_lfnc_a",               group="table_4")
TABLE_4_LFNC_B               = nec_table("table_4_lfnc_b",               group="table_4")
TABLE_4_LFNC_C               = nec_table("table_4_lfnc_c",               group="table_4")
TABLE_4_LFMC                 = nec_table("table_4_lfmc",                 group="table_4")
TABLE_4_RMC                  = nec_table("table_4_rmc",                  group="table_4")
TABLE_4_PVC_SCHEDULE_80      = nec_table("table_4_pvc_schedule_80",      group="table_4")
TABLE_4_PVC_SCHEDULE_40_HDPE = nec_table("table_4_pvc_schedule_40_hdpe", group="table_4")
TABLE_4_PVC_TYPE_A           = nec_table("table_4_pvc_type_a",           group="table_4")
TABLE_4_PVC_TYPE_EB          = nec_table("table_4_pvc_type_eb",          group="table_4")

TABLE_4 = nec_group("table_4", "Table 4 — Dimensions and Percent Area of Conduit and Tubing")
TABLE_4_COLUMNS = TABLE_4["columns"]


# --------------------------------------------------------------------------------------
# Table 8: Conductor Properties (Voltage Drop) — K values for calculating voltage drop (Ω/km)
# --------------------------------------------------------------------------------------

TABLE_8 = nec_table("table_8")

def get_standard_conductor_sizes_t8() -> dict[str, Any] | None:
    return get_standard_conductor_sizes(TABLE_8)

def get_r_value_t8(
    # construction,
    size,
    material,
    coating_type
):
    k_row = next(
        (row for row in TABLE_8['rows'] if row['size_awg_kcmil'] == size),
        None
    )

    if k_row is None:
        return None

    if material == "al":
        ohm_km = k_row['aluminum_ohm_km']
        ohm_kft = k_row['aluminum_ohm_kft']      
    elif coating_type == "uncoated":
        ohm_km = k_row['cu_uncoated_ohm_km']
        ohm_kft = k_row['cu_uncoated_ohm_kft']        
    elif coating_type == "coated":
        ohm_km = k_row['cu_coated_ohm_km']
        ohm_kft = k_row['cu_coated_ohm_kft']     
    else:
        return None  
    
    return {'km': ohm_km, 'kft': ohm_kft}         
    
    
def r_t_change(R_1: float, T_2: float, material: str) -> float | None:    
    if not R_1:
        return None
    
    if not T_2 or T_2 == "":
        T_2 = 75
    
    if material == "al":
        a = 0.00323
    elif material == "cu":
        a = 0.00300
    else:
        return None
    
    return R_1 * (1 + a * (T_2-75))  
    

    

# --------------------------------------------------------------------------------------
# Table 9: Alternating-Current Resistance and Reactance for 600-Volt Cables, 3-Phase, 60 Hz, 75°C — Three Single Conductors in Conduit
# --------------------------------------------------------------------------------------

TABLE_9 = nec_table("table_9")

TABLE_9_LOOKUP_KEYS_kft = {
    "impedance_map": {
        "cu": {
            "pvc": 'cu_uncoated_eff_z_085pf_pvc_conduit_ohm_kft',
            "al": 'cu_uncoated_eff_z_085pf_aluminum_conduit_ohm_kft',
            "st": 'cu_uncoated_eff_z_085pf_steel_conduit_ohm_kft',
        },
        "al": {
            "pvc": 'aluminum_eff_z_085pf_pvc_conduit_ohm_kft',
            "al": 'aluminum_eff_z_085pf_aluminum_conduit_ohm_kft',
            "st": 'aluminum_eff_z_085pf_steel_conduit_ohm_kft',
        }
    },
    "reactance_map": {
        "cu": {
            "pvc": 'xl_pvc_aluminum_conduits_ohm_kft',
            "al": 'xl_pvc_aluminum_conduits_ohm_kft',
            "st": 'xl_steel_conduit_ohm_kft',
        },
        "al": {
            "pvc": 'xl_pvc_aluminum_conduits_ohm_kft',
            "al": 'xl_pvc_aluminum_conduits_ohm_kft',
            "st": 'xl_steel_conduit_ohm_kft',
        },
    },
    "resistance_map": {
        "cu": {
            "pvc": 'cu_uncoated_ac_resistance_pvc_conduit_ohm_kft',
            "al": 'cu_uncoated_ac_resistance_aluminum_conduit_ohm_kft',
            "st": 'cu_uncoated_ac_resistance_steel_conduit_ohm_kft',
        },
        "al": {
            "pvc": 'aluminum_ac_resistance_pvc_conduit_ohm_kft',
            "al": 'aluminum_ac_resistance_aluminum_conduit_ohm_kft',
            "st": 'aluminum_ac_resistance_steel_conduit_ohm_kft',
        },
    },
}

def get_standard_conductor_sizes_t9() -> dict[str, Any] | None:
    return get_standard_conductor_sizes(TABLE_9)

def get_table9_row(
    criteria: dict[str, Any],
) -> dict[str, Any] | None:
    return get_table_row(TABLE_9, criteria)

# --------------------------------------------------------------------------------------
# Motor Feeder Cables
# --------------------------------------------------------------------------------------

TABLE_430_247 = nec_table("table_430_247")

TABLE_430_248 = nec_table("table_430_248")

TABLE_430_250 = nec_table("table_430_250")

TABLE_430_251_A = nec_table("table_430_251_a")

TABLE_430_251_B = nec_table("table_430_251_b")

TABLE_430_251_C = nec_table("table_430_251_c")


# --------------------------------------------------------------------------------------
# TABLE 310.16
# --------------------------------------------------------------------------------------

TABLE_310_16 = nec_table("table_310_16")



# --------------------------------------------------------------------------------------
# TABLE 310.14_1
# --------------------------------------------------------------------------------------
TABLE_310_14_1 = nec_table("table_310_4_1")  # 2026 renumbering: 310.14(1) -> 310.4(1)

TABLE_5 = nec_table("table_5")

TABLE_5A = nec_table("table_5a")

NEC_2406A_STANDARD = [
    10, 15, 20, 25, 30,
    35, 40, 45, 50, 60,
    70, 80, 90, 100, 110,
    125, 150, 175, 200, 225,
    250, 300, 350, 400, 450,
    500, 600, 700, 800, 1000,
    1200, 1600, 2000, 2500, 3000,
    4000, 5000, 6000,
]

TABLE_450_5A = nec_table("table_450_5_a")

TABLE_450_5B = nec_table("table_450_5_b")

# --------------------------------------------------------------------------------------
# Derating & Adjustments (Article 310)
# --------------------------------------------------------------------------------------

TABLE_310_15_B_1_1 = nec_table("table_310_15_b_1_1")

TABLE_310_15_B_1_2 = nec_table("table_310_15_b_1_2")

TABLE_310_15_C_1 = nec_table("table_310_15_c_1")

# --------------------------------------------------------------------------------------
# Additional Ampacity / Sizing (Article 310)
# --------------------------------------------------------------------------------------

TABLE_310_17 = nec_table("table_310_17")

TABLE_310_12_A = nec_table("table_310_12_a")

# --------------------------------------------------------------------------------------
# Grounding & Bonding (Article 250)
# --------------------------------------------------------------------------------------

TABLE_250_122 = nec_table("table_250_122")

TABLE_250_66 = nec_table("table_250_66")

TABLE_430_7_B = nec_table("table_430_7_b")

# --------------------------------------------------------------------------------------
# Table 430.52(C)(1): Maximum Rating or Setting of Motor Branch-Circuit Short-Circuit and Ground-Fault Protective Devices
# --------------------------------------------------------------------------------------

TABLE_430_52_C_1 = nec_table("table_430_52_c_1")

# --------------------------------------------------------------------------------------
# Table 430.22(E): Duty-Cycle Service
# --------------------------------------------------------------------------------------

TABLE_430_22_E = nec_table("table_430_22_e")

# --------------------------------------------------------------------------------------
# Table 430.37: Overload Units
# --------------------------------------------------------------------------------------

TABLE_430_37 = nec_table("table_430_37")

# --------------------------------------------------------------------------------------
# Table 430.72(B): Maximum Rating of Overcurrent Protective Device in Amperes
# --------------------------------------------------------------------------------------

TABLE_430_72_B = nec_table("table_430_72_b_2")

# --------------------------------------------------------------------------------------
# Table 392.22(A)(1): Allowable Cable Fill Area for Multiconductor Cables in Ladder,
# Ventilated Trough, or Solid Bottom Cable Trays for Cables Rated 2000 Volts or Less
# --------------------------------------------------------------------------------------

TABLE_392_22_A_1 = nec_table("table_392_22_a_1")

# --------------------------------------------------------------------------------------
# Table 392.22(A)(5): Allowable Cable Fill Area for Multiconductor Cables in Ventilated
# Channel Cable Trays for Cables Rated 2000 Volts or Less
# --------------------------------------------------------------------------------------

TABLE_392_22_A_5 = nec_table("table_392_22_a_5")

# --------------------------------------------------------------------------------------
# Table 392.22(A)(6): Allowable Cable Fill Area for Multiconductor Cables in Solid
# Channel Cable Trays for Cables Rated 2000 Volts or Less
# --------------------------------------------------------------------------------------

TABLE_392_22_A_6 = nec_table("table_392_22_a_6")

# --------------------------------------------------------------------------------------
# Table 392.22(B)(1): Allowable Cable Fill Area for Single-Conductor Cables in Ladder,
# Ventilated Trough, or Wire Mesh Cable Trays for Cables Rated 2000 Volts or Less
# --------------------------------------------------------------------------------------

TABLE_392_22_B_1 = nec_table("table_392_22_b_1")

# ----------------------------
# Registry + public API
# ----------------------------

def _try_import_pandas():
    try:
        import pandas as pd  # type: ignore
        return pd
    except Exception:
        return None

def _df(rows: list[dict[str, Any]]):
    pd = _try_import_pandas()
    if pd is None:
        return rows
    return pd.DataFrame(rows)

# Metadata carried through to the Table Library page alongside the rows.
_REGISTRY_META = ('units', 'condition', 'notes', 'edition', 'source',
                  'header_tiers', 'column_tiers')


def _registry_entry(table_id: str, table: dict[str, Any], rows: Any) -> dict[str, Any]:
    entry = {
        "id": table_id,
        "title": table.get('title', ''),
        "columns": table.get('columns'),
        "rows": rows,
        "raw": table,
    }
    entry.update({key: table[key] for key in _REGISTRY_META if table.get(key)})
    return entry


def _build_nec_registry(tables_dict: dict[str, Any]) -> dict[str, dict[str, Any]]:
    reg: dict[str, dict[str, Any]] = {}

    for key, table in tables_dict.items():
        if 'tables' in table and isinstance(table['tables'], dict):
            reg[key] = _registry_entry(key, table, None)
            for sub_key, sub_table in table['tables'].items():
                sub_id = f"{key}_{sub_key}"
                reg[sub_id] = _registry_entry(sub_id, sub_table, sub_table.get('rows'))
        else:
            reg[key] = _registry_entry(key, table, table.get('rows'))
    return reg

# cached registry
_TABLE_REGISTRY: dict[str, dict[str, Any]] = _build_nec_registry(TABLES)

def list_table_ids() -> list[str]:
    """Return sorted table IDs available in the library (e.g., ['1','2','5A','6A',...])."""
    def _sort_key(tid: str):
        # Numeric-only IDs first (1, 2, 5A, 6A …), then letter-prefixed (D8A, D9A …)
        import re
        m = re.match(r"^table_(\d+)(.*)$", str(tid).lower())
        if not m:
            return (2, 0, 10**9, str(tid))
        n = int(m.group(1))
        suf = m.group(2) or ""
        return (0, 0, n, suf)
    return sorted(_TABLE_REGISTRY.keys(), key=_sort_key)

def get_table_meta(table_id: str) -> dict[str, Any] | None:
    return _TABLE_REGISTRY.get(str(table_id).lower())

def get_table_rows(table_id: str) -> list[dict[str, Any]] | None:
    meta = get_table_meta(table_id)
    if not meta:
        return None
    return meta.get("rows")

def search_tables(query: str) -> list[str]:
    q = (query or "").strip().lower()
    if not q:
        return list_table_ids()
    out = []
    for tid, meta in _TABLE_REGISTRY.items():
        hay = " ".join([str(tid), str(meta.get("title","")), str(meta.get("id",""))]).lower()
        if q in hay:
            out.append(tid)
    # keep natural ordering
    order = list_table_ids()
    return [t for t in order if t in out]

def get_table_dataframe(table_id: str):
    """Return a pandas DataFrame when possible; otherwise returns list-of-Dicts or None.

    Notes:
    - Most tables are stored as a simple list-of-Dicts in meta['rows'].
    - Some large tables (notably Table 6 and Table 9 families) are stored in structured meta['raw'] formats.
      For those, we generate a display DataFrame here so the Table Library page can render them.
    """
    meta = get_table_meta(table_id)
    if not meta:
        return None

    rows = meta.get("rows")
    if rows is not None:
        return _df(rows)

    return None
