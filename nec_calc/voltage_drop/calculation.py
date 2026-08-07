from __future__ import annotations

import math
from typing import Any

from lib import nec_tables


# ----------------------------
# result helper functions
# ----------------------------
def _method_result(
    voltage_drop,
    r_base_value=None,
    r_value=None,
    z_value=None,
    xl_value=None,
):
    return {
        "voltage_drop": voltage_drop,
        "r_base_value": r_base_value,
        "r_value": r_value,
        "z_value": z_value,
        "xl_value": xl_value,
    }


def _build_calc_result(calc: dict[str, Any], **inputs) -> dict[str, Any]:
    vd = calc["voltage_drop"]

    r_value = calc.get("r_value")
    z_value = calc.get("z_value")
    xl_value = calc.get("xl_value")

    current = inputs["current"]
    voltage = inputs["voltage"]
    parallel_conductors = inputs["parallel_conductors"]

    return {
        **inputs,
        "v_nom": voltage,
        "r_base_value": calc.get("r_base_value"),
        "r_value": r_value,
        "z_value": z_value,
        "xl_value": xl_value,
        "R": r_value,
        "Z": z_value,
        "XL": xl_value,

        "I_eff": _effective_current(current, parallel_conductors),
        "f": phase_label(inputs["system_type"]),

        "voltage_drop": vd,
        "percent_drop": vd_percent(vd, voltage),
    }


# ----------------------------
# calculator helper functions
# ----------------------------
def phase_F(system_type: str) -> float:
    return math.sqrt(3) if system_type == "three_phase" else 2.0


def phase_label(system_type: str) -> str:
    return r"$\sqrt{3}$" if system_type == "three_phase" else "2"


def vd_percent(V_d, V_nom):
    if V_d is None or V_nom in (None, 0):
        return None

    return (V_d / V_nom) * 100


def _effective_current(current, parallel_conductors):
    if not parallel_conductors:
        raise ValueError("parallel_conductors must be at least 1.")

    return current / parallel_conductors


def _voltage_drop(system_type: str, current: float, length: float, parallel_conductors, R_Z, pf=1.0) -> float:

    if R_Z is None:
        raise ValueError("Voltage-drop resistance/impedance value is missing.")

    I_eff = _effective_current(current, parallel_conductors)
    return pf * phase_F(system_type) * R_Z * I_eff * length / 1000.0


def _table9_key(group: str, conductor_material: str, conduit_material: str) -> str:
    return nec_tables.TABLE_9_LOOKUP_KEYS_kft[group][conductor_material][conduit_material]


def _r_temp_change(r_base_value, temperature, conductor_material):
    return nec_tables.r_t_change(r_base_value, temperature, conductor_material)


def _require_table_value(value, table_name, conductor_size, conductor_material=None, conduit_material=None, column=None):
    if value is not None:
        return value

    details = [
        f"table={table_name}",
        f"conductor_size={conductor_size}",
    ]

    if conductor_material is not None:
        details.append(f"conductor_material={conductor_material}")

    if conduit_material is not None:
        details.append(f"conduit_material={conduit_material}")

    if column is not None:
        details.append(f"column={column}")

    raise ValueError("Missing table value: " + ", ".join(details))


# ----------------------------
# method calculators
# ----------------------------
def voltage_drop_table8(
    system_type,
    temperature,
    current,
    length,
    parallel_conductors,
    conductor_material,
    conductor_size,
    coating_type,
    pf,
):

    table_value = nec_tables.get_r_value_t8(
        conductor_size,
        conductor_material,
        coating_type,
    )

    if table_value is None:
        raise ValueError(
            "No NEC Table 8 resistance value found for "
            f"size={conductor_size}, material={conductor_material}, coating={coating_type}."
        )
    R_1 = table_value["kft"]
    
    R = _r_temp_change(R_1, temperature, conductor_material)

    vd = _voltage_drop(
        system_type=system_type,
        current=current,
        length=length,
        parallel_conductors=parallel_conductors,
        R_Z=R,
        pf=pf,
    )

    return _method_result(
        voltage_drop=vd,
        r_base_value=R_1,
        r_value=R,
    )


def voltage_drop_table9(
    system_type: str,
    temperature,
    current,
    length,
    parallel_conductors,
    conductor_material,
    conductor_size,
    conduit_material,
    pf,
    use_custom_pf,
    use_custom_T_op,
):
    row = nec_tables.get_table9_row({"size_awg_kcmil": conductor_size})

    if row is None:
        raise ValueError(f"No NEC Table 9 row found for conductor size={conductor_size}.")

    R_1 = None
    R = None
    XL = None
    
    if use_custom_pf:
        xl_col = _table9_key("reactance_map", conductor_material, conduit_material)
        r_col = _table9_key("resistance_map", conductor_material, conduit_material)

        XL = _require_table_value(
            row.get(xl_col),
            table_name="NEC Table 9",
            conductor_size=conductor_size,
            conductor_material=conductor_material,
            conduit_material=conduit_material,
            column=xl_col,
        )
        R_1 = _require_table_value(
            row.get(r_col),
            table_name="NEC Table 9",
            conductor_size=conductor_size,
            conductor_material=conductor_material,
            conduit_material=conduit_material,
            column=r_col,
        )
        
        R = (
            _r_temp_change(R_1, temperature, conductor_material)
            if use_custom_T_op
            else R_1
        )

        Z = R * pf + XL * math.sqrt(max(0.0, 1 - pf**2))

    else:
        z_col = _table9_key("impedance_map", conductor_material, conduit_material)
        Z = _require_table_value(
            row.get(z_col),
            table_name="NEC Table 9",
            conductor_size=conductor_size,
            conductor_material=conductor_material,
            conduit_material=conduit_material,
            column=z_col,
        )

    vd = _voltage_drop(
        system_type=system_type,
        current=current,
        length=length,
        parallel_conductors=parallel_conductors,
        R_Z=Z,
        pf=1.0,
    )

    return _method_result(
        voltage_drop=vd,
        r_base_value=R_1,
        r_value=R,
        z_value=Z,
        xl_value=XL,
    )


def voltage_drop_manual_r(
    system_type: str,
    current,
    length,
    parallel_conductors,
    manual_r,
    pf,
):
    if manual_r is None:
        raise ValueError("Manual R-value is required when using Manual Resistance mode.")

    vd = _voltage_drop(
        system_type=system_type,
        current=current,
        length=length,
        parallel_conductors=parallel_conductors,
        R_Z=manual_r,
        pf=pf,
    )

    return _method_result(
        voltage_drop=vd,
        r_value=manual_r,
    )


# ----------------------------
# main calculator function
# ----------------------------
def calc_voltage_drop(
    vd_mode: str,
    system_type: str,
    system_type_label: str,
    temperature,
    current,
    length,
    voltage,
    parallel_conductors,
    manual_r,
    conductor_material,
    conductor_material_label,
    conductor_size,
    size_unit,
    coating_type,
    coating_type_label,
    conduit_material,
    conduit_material_label,
    pf,
    use_custom_pf,
    use_custom_T_op,
):
        
    common_args = {
        "system_type": system_type,
        "current": float(current),
        "length": float(length),
        "parallel_conductors": int(parallel_conductors),
    }

    if vd_mode == "table8_r":
        calc = voltage_drop_table8(
            **common_args,
            temperature=float(temperature),
            conductor_material=conductor_material,
            conductor_size=conductor_size,
            coating_type=coating_type,
            pf=float(pf),
        )

    elif vd_mode == "table9_z":
        calc = voltage_drop_table9(
            **common_args,
            temperature=float(temperature),
            conductor_material=conductor_material,
            conductor_size=conductor_size,
            conduit_material=conduit_material,
            pf=float(pf),
            use_custom_pf=use_custom_pf,
            use_custom_T_op=use_custom_T_op,
        )

    elif vd_mode == "manual_r":
        calc = voltage_drop_manual_r(
            **common_args,
            manual_r=manual_r,
            pf=float(pf),
        )

    else:
        raise ValueError(f"Unknown voltage-drop calculation mode: {vd_mode!r}")

    return _build_calc_result(
        calc=calc,
        vd_mode=vd_mode,
        system_type=system_type,
        system_type_label=system_type_label,
        temperature=float(temperature),
        current=float(current),
        length=float(length),
        voltage=float(voltage),
        parallel_conductors=int(parallel_conductors),
        conductor_material=conductor_material_label,
        conductor_material_key=conductor_material,
        conductor_size=conductor_size,
        size_unit=size_unit,
        coating_type=coating_type_label,
        coating_type_key=coating_type,
        conduit_material=conduit_material_label,
        conduit_material_key=conduit_material,
        pf=float(pf),
        manual_r=manual_r,
        use_custom_pf=use_custom_pf,
        use_custom_T_op=use_custom_T_op,
    )
