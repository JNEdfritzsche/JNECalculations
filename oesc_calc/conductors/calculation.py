from __future__ import annotations

from typing import Any

from oesc_calc.common import tables

COPPER = "Copper"
ALUMINUM = "Aluminum"

SINGLE = "Single conductor"
MULTI = "Multi-conductor cable"

FREE_AIR = "Free air"
RACEWAY = "Raceway or cable"
UNDERGROUND = "Underground"
INSTALLATIONS = (FREE_AIR, RACEWAY, UNDERGROUND)

SPACING_100 = "≥ 100%"
SPACING_25_100 = "25% to 100%"
SPACING_UNDER_25 = "< 25%"
SPACINGS = (SPACING_100, SPACING_25_100, SPACING_UNDER_25)

SIZE_CLASS_LARGE = "No. 1/0 AWG and larger"
SIZE_CLASS_SMALL = "Smaller than No. 1/0 AWG"
SIZE_CLASSES = (SIZE_CLASS_LARGE, SIZE_CLASS_SMALL)


def _table(material: str, free_air: bool) -> str:
    if material == COPPER:
        return "Table 1" if free_air else "Table 2"
    return "Table 3" if free_air else "Table 4"


def select_subrule(
    material: str,
    conductor_form: str,
    install: str,
    n_conductors: int = 3,
    spacing: str = SPACING_100,
    size_class: str = SIZE_CLASS_LARGE,
    in_diagrams: str = "Yes",
) -> dict[str, Any]:
    is_multi = conductor_form == MULTI

    if install == FREE_AIR:
        if is_multi:
            if n_conductors <= 3:
                return {"subrule": "4-004 (1) & (2) — multiconductor in free air (1–3 CCC)",
                        "amp_table": _table(material, False), "corr_table": None, "corr_count": None}
            return {"subrule": "4-004 (1) & (2) — multiconductor in free air (4+ CCC)",
                    "amp_table": _table(material, False), "corr_table": "5C", "corr_count": n_conductors}

        if spacing == SPACING_100:
            return {"subrule": "4-004 (1) & (2) — single in free air",
                    "amp_table": _table(material, True), "corr_table": None, "corr_count": None}
        if spacing == SPACING_25_100:
            return {"subrule": "4-004 (8) — single in free air",
                    "amp_table": _table(material, True), "corr_table": "5D", "corr_count": None}
        if n_conductors <= 4:
            return {"subrule": "4-004 (9) — ≤4 single in free air",
                    "amp_table": _table(material, True), "corr_table": "5B", "corr_count": n_conductors}
        return {"subrule": "4-004 (11) — ≥5 single in free air",
                "amp_table": _table(material, False), "corr_table": "5C", "corr_count": n_conductors}

    if install == RACEWAY:
        if n_conductors <= 3:
            return {"subrule": "4-004 (1) & (2) — 1 to 3 in raceway/cable",
                    "amp_table": _table(material, False), "corr_table": None, "corr_count": None}
        return {"subrule": "4-004 (1) & (2) — 4 or more in raceway/cable",
                "amp_table": _table(material, False), "corr_table": "5C", "corr_count": n_conductors}

    if size_class == SIZE_CLASS_LARGE and in_diagrams == "Yes":
        return {"subrule": "4-004 (1) & (2)(d) — underground, ≥1/0, config in D8–D11",
                "amp_table": "Tables D8A to D11B (or IEEE 835)", "corr_table": None, "corr_count": None}
    if size_class == SIZE_CLASS_LARGE:
        return {"subrule": "4-004 (1) & (2)(e) — underground, ≥1/0, config NOT in D8–D11",
                "amp_table": "IEEE 835 calculation method", "corr_table": None, "corr_count": None}
    if in_diagrams == "No":
        return {"subrule": "4-004 (1) & (2)(f) — underground, <1/0, config NOT in D8–D11",
                "amp_table": f"{_table(material, False)} (or IEEE 835)", "corr_table": None, "corr_count": None}
    return {"subrule": "Underground case (not explicitly shown in the chart)",
            "amp_table": f"{_table(material, False)} (confirm applicability)",
            "corr_table": None, "corr_count": None}


def ampacity_table_id(amp_table: str) -> str | None:
    for candidate in ("1", "2", "3", "4"):
        if amp_table.startswith(f"Table {candidate}"):
            return candidate
    return None


def calc_conductors(
    i_load: float,
    sf: float,
    n_parallel: int,
    material: str,
    conductor_form: str,
    install: str,
    corr_factor: float,
    temp_factor: float,
    temp_choice: int,
    n_conductors: int = 3,
    spacing: str = SPACING_100,
    size_class: str = SIZE_CLASS_LARGE,
    in_diagrams: str = "Yes",
    corr_factor_source: str = "None",
    temp_factor_source: str = "None",
) -> dict[str, Any]:
    path = select_subrule(material, conductor_form, install, n_conductors, spacing, size_class, in_diagrams)

    i_design_total = i_load * sf
    i_per_set = i_design_total / n_parallel if n_parallel else None

    k_total = corr_factor * temp_factor
    i_table_required = i_per_set / k_total if (i_per_set is not None and k_total) else None

    table_id = ampacity_table_id(path["amp_table"])
    selected_size = base_ampacity = adjusted = None
    if table_id is not None and i_table_required is not None:
        selected_size, base_ampacity = tables.smallest_size_for(table_id, i_table_required, temp_choice)
        if base_ampacity is not None:
            adjusted = base_ampacity * k_total

    source_tables = [t for t in (table_id, path["corr_table"]) if t]
    if temp_factor_source == "Table 5A":
        source_tables.append("5A")

    return {
        "i_load": i_load,
        "sf": sf,
        "n_parallel": n_parallel,
        "material": material,
        "conductor_form": conductor_form,
        "install": install,
        "n_conductors": n_conductors,
        "spacing": spacing if install == FREE_AIR and conductor_form == SINGLE else None,
        "subrule": path["subrule"],
        "amp_table": path["amp_table"],
        "amp_table_id": table_id,
        "corr_table": path["corr_table"],
        "corr_factor": corr_factor,
        "corr_factor_source": corr_factor_source,
        "temp_factor": temp_factor,
        "temp_factor_source": temp_factor_source,
        "temp_choice": temp_choice,
        "k_total": k_total,
        "I_design_total": i_design_total,
        "I_per_set": i_per_set,
        "I_table_required": i_table_required,
        "selected_size": selected_size,
        "base_ampacity": base_ampacity,
        "adjusted_ampacity_per_set": adjusted,
        "adjusted_ampacity_total": adjusted * n_parallel if adjusted is not None else None,
        "primary_table": table_id,
        "source_tables": source_tables,
    }
