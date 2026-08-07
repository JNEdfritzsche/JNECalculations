from __future__ import annotations

from typing import Any
from lib import nec_tables
from nec_calc.common.table_helpers import get_table_row


def format_conductor_size_display(size: str | None) -> str:
    if not size:
        return "—"
    s = str(size).strip()
    if s.isnumeric() and int(s) >= 250:
        return f"{s} kcmil"
    if s in ("250", "300", "350", "400", "500", "600", "700", "750", "800", "900", "1000", "1250", "1500", "1750", "2000"):
        return f"{s} kcmil"
    if s.endswith("AWG") or s.endswith("kcmil"):
        return s
    return f"{s} AWG"


def _method_result(
    calculated_value: float | None,
    intermediate_value: float | None = None,
    **extra: Any,
) -> dict[str, Any]:
    return {
        "calculated_value": calculated_value,
        "intermediate_value": intermediate_value,
        **extra,
    }


def _build_calc_result(calc: dict[str, Any], **inputs: Any) -> dict[str, Any]:
    mat_map = {"cu": "Copper", "al": "Aluminum / Copper-Clad Aluminum"}
    amb_base_map = {
        "30c": "30°C (86°F) Base — Table 310.15(B)(1)(1)",
        "40c": "40°C (104°F) Base — Table 310.15(B)(1)(2)",
    }
    sel_size = calc.get("selected_size") or inputs.get("conductor_size")
    min_size = calc.get("min_recommended_size")
    return {
        **inputs,
        **calc,
        "material_label": mat_map.get(inputs.get("material", ""), str(inputs.get("material", ""))),
        "ambient_base_label": amb_base_map.get(inputs.get("ambient_base", ""), str(inputs.get("ambient_base", ""))),
        "selected_size_display": format_conductor_size_display(sel_size),
        "conductor_size_display": format_conductor_size_display(inputs.get("conductor_size")),
        "min_recommended_size_display": format_conductor_size_display(min_size) if min_size else "—",
    }


def get_table310_16_ampacity(conductor_size: str, material: str, temp_rating: str) -> float | None:
    mat_prefix = "copper" if material in ("cu", "copper") else "aluminum_or_copper_clad_aluminum"
    col_name = f"{mat_prefix}_{temp_rating}c_ampacity"
    row = get_table_row(nec_tables.TABLE_310_16, {"size_awg_kcmil": str(conductor_size)})
    if row and col_name in row:
        val = row.get(col_name)
        if val is not None:
            try:
                return float(val)
            except Exception:
                return None
    return None


def get_ambient_correction(ambient_base: str, ambient_temp_c: str, temp_rating: str) -> float | None:
    table = (
        nec_tables.TABLE_310_15_B_1_2
        if ambient_base == "40c"
        else nec_tables.TABLE_310_15_B_1_1
    )
    col_name = f"temp_rating_{temp_rating}c"
    row = get_table_row(table, {"ambient_temp_c": ambient_temp_c})
    if row and col_name in row:
        val = row.get(col_name)
        if val is not None:
            try:
                return float(val)
            except Exception:
                return None
    return None


def get_conductor_adjustment(number_of_conductors: str) -> float:
    if number_of_conductors in ("1-3", "1", "2", "3"):
        return 1.0
    row = get_table_row(nec_tables.TABLE_310_15_C_1, {"number_of_conductors": number_of_conductors})
    if row and "adjustment_factor_percent" in row:
        val = row.get("adjustment_factor_percent")
        if val is not None:
            try:
                return float(val) / 100.0
            except Exception:
                return 1.0
    return 1.0


def calc_single_conductor(
    conductor_size: str,
    material: str,
    temp_rating: str,
    ambient_base: str,
    ambient_temp_c: str,
    number_of_conductors: str,
    terminal_temp_rating: str | None = None,
    load_current: float | None = None,
    n_parallel: int = 1,
) -> dict[str, Any]:
    n_par = max(1, int(n_parallel))
    table_amp = get_table310_16_ampacity(conductor_size, material, temp_rating)
    if table_amp is None:
        return _method_result(
            calculated_value=None,
            intermediate_value=None,
            table_ampacity=None,
            ambient_correction=None,
            conductor_adjustment=None,
            derated_ampacity=None,
            terminal_limit_ampacity=None,
            allowable_single=None,
            is_adequate=False,
            selected_size=conductor_size,
            total_allowable_ampacity=None,
            n_parallel=n_par,
        )

    cf_temp = get_ambient_correction(ambient_base, ambient_temp_c, temp_rating)
    if cf_temp is None:
        return _method_result(
            calculated_value=None,
            intermediate_value=None,
            table_ampacity=table_amp,
            ambient_correction=None,
            conductor_adjustment=None,
            derated_ampacity=None,
            terminal_limit_ampacity=None,
            allowable_single=None,
            is_adequate=False,
            selected_size=conductor_size,
            total_allowable_ampacity=None,
            n_parallel=n_par,
        )

    af_cond = get_conductor_adjustment(number_of_conductors)

    derated = table_amp * cf_temp * af_cond

    term_limit = None
    if terminal_temp_rating and terminal_temp_rating in ("60", "75", "90"):
        term_limit = get_table310_16_ampacity(conductor_size, material, terminal_temp_rating)

    if term_limit is not None and term_limit < derated:
        final_amp = term_limit
    else:
        final_amp = derated

    total_allowable = final_amp * n_par
    is_adequate = (load_current is None) or (total_allowable >= load_current)

    return _method_result(
        calculated_value=total_allowable,
        intermediate_value=derated * n_par,
        table_ampacity=table_amp,
        ambient_correction=cf_temp,
        conductor_adjustment=af_cond,
        derated_ampacity=derated,
        terminal_limit_ampacity=term_limit,
        allowable_single=final_amp,
        is_adequate=is_adequate,
        selected_size=conductor_size,
        total_allowable_ampacity=total_allowable,
        n_parallel=n_par,
    )


def calc_min_conductor_size(
    material: str,
    temp_rating: str,
    ambient_base: str,
    ambient_temp_c: str,
    number_of_conductors: str,
    terminal_temp_rating: str | None = None,
    load_current: float = 0.0,
    n_parallel: int = 1,
) -> str | None:
    sizes = nec_tables.get_standard_conductor_sizes_unitless(nec_tables.TABLE_310_16) or []
    n_par = max(1, int(n_parallel))
    for size in sizes:
        res = calc_single_conductor(
            conductor_size=size,
            material=material,
            temp_rating=temp_rating,
            ambient_base=ambient_base,
            ambient_temp_c=ambient_temp_c,
            number_of_conductors=number_of_conductors,
            terminal_temp_rating=terminal_temp_rating,
            load_current=load_current,
            n_parallel=n_par,
        )
        if res["calculated_value"] is not None and res["is_adequate"]:
            return size
    return sizes[-1] if sizes else None


def calc_conductors(
    conductor_size: str,
    material: str,
    temp_rating: str,
    ambient_base: str,
    ambient_temp_c: str,
    number_of_conductors: str,
    terminal_temp_rating: str | None = None,
    load_current: float | None = None,
    n_parallel: int = 1,
    wire_type: str | None = None,
    temp_unit: str = "C",
    **kwargs: Any,
) -> dict[str, Any]:
    inputs = {
        "conductor_size": conductor_size,
        "material": material,
        "temp_rating": temp_rating,
        "ambient_base": ambient_base,
        "ambient_temp_c": ambient_temp_c,
        "number_of_conductors": number_of_conductors,
        "terminal_temp_rating": terminal_temp_rating,
        "load_current": load_current,
        "n_parallel": max(1, int(n_parallel)),
        "wire_type": wire_type or "Not specified",
        "temp_unit": temp_unit,
    }

    #calculate for the user's selected conductor size across N parallel runs
    calc = calc_single_conductor(
        conductor_size=conductor_size,
        material=material,
        temp_rating=temp_rating,
        ambient_base=ambient_base,
        ambient_temp_c=ambient_temp_c,
        number_of_conductors=number_of_conductors,
        terminal_temp_rating=terminal_temp_rating,
        load_current=load_current,
        n_parallel=inputs["n_parallel"],
    )

    # f load current is specified, also find what the minimum recommended wire size is
    if load_current is not None and load_current > 0:
        min_rec = calc_min_conductor_size(
            material=material,
            temp_rating=temp_rating,
            ambient_base=ambient_base,
            ambient_temp_c=ambient_temp_c,
            number_of_conductors=number_of_conductors,
            terminal_temp_rating=terminal_temp_rating,
            load_current=load_current,
            n_parallel=inputs["n_parallel"],
        )
        calc["min_recommended_size"] = min_rec
    else:
        calc["min_recommended_size"] = None

    return _build_calc_result(calc=calc, **inputs)
