from __future__ import annotations

from typing import Any

from nec_calc.common.report_helper import (
    add_word_equation,
    build_nec_table_row_source,
    build_standard_excel_report,
    build_standard_word_report,
    get_first,
    omml_frac,
    omml_r,
    omml_sqrt,
    omml_sub,
    render_standard_export_report,
    yes_no,
)


REPORT_TITLE = "NEC Voltage Drop Calculation Report"
SHEET_NAME = "Voltage Drop"

METHOD_LABELS = {
    "table8_r": "Resistance Method (NEC Chapter 9, Table 8)",
    "table9_z": "AC Impedance Method (NEC Chapter 9, Table 9)",
    "manual_r": "Manual Resistance",
}

SYSTEM_LABELS = {
    "dc": "DC",
    "single_phase": "1φ AC",
    "three_phase": "3φ AC",
}

CONDUCTOR_LABELS = {
    "cu": "Copper",
    "al": "Aluminum",
    None: "—",
}

COATING_LABELS = {
    "uncoated": "Uncoated",
    "coated": "Coated (Tinned)",
    None: "—",
}

CONDUIT_LABELS = {
    "pvc": "PVC",
    "al": "Aluminum",
    "st": "Steel",
    None: "—",
}

TABLE9_CONDUIT_KEYS = {
    "st": "steel",
    "al": "aluminum",
    "pvc": "pvc",
}

TABLE8_COLUMNS = [
    "size_awg_kcmil",
    "area_mm2",
    "area_circular_mils",
    "stranding_quantity",
    "overall_dia_mm",
    "overall_dia_in",
    "cu_uncoated_ohm_kft",
    "cu_coated_ohm_kft",
    "aluminum_ohm_kft",
]

TABLE8_LABELS = {
    "size_awg_kcmil": "Size",
    "area_mm2": "Area (mm²)",
    "area_circular_mils": "Area (circular mils)",
    "stranding_quantity": "Stranding Qty.",
    "overall_dia_mm": "Overall Dia. (mm)",
    "overall_dia_in": "Overall Dia. (in.)",
    "cu_uncoated_ohm_kft": "Cu Uncoated R (Ω/kft)",
    "cu_coated_ohm_kft": "Cu Coated R (Ω/kft)",
    "aluminum_ohm_kft": "Aluminum R (Ω/kft)",
}


# ============================================================
# Small helpers
# ============================================================
def _enum_key(value: Any) -> str | None:
    if value is None:
        return None
    return getattr(value, "key", value)


def _enum_label(value: Any) -> str | None:
    if value is None:
        return None
    return getattr(value, "label", None)


def _clean_key(value: Any) -> str | None:
    value = _enum_key(value)
    if value is None or value == "":
        return None
    return str(value)


def _mode_key(result: dict[str, Any], vd_mode: Any = None) -> str:
    return _clean_key(vd_mode) or str(get_first(result, "vd_mode", default="manual_r"))


def _system_label(result: dict[str, Any], system_type_label: Any = None) -> str:
    return (
        _enum_label(system_type_label)
        or system_type_label
        or get_first(result, "system_type_label")
        or SYSTEM_LABELS.get(get_first(result, "system_type"), get_first(result, "system_type", default="—"))
    )


def _conduit_key(result: dict[str, Any], conduit_material: Any = None) -> str | None:
    key = _clean_key(conduit_material) or get_first(result, "conduit_material_key")
    if key in CONDUIT_LABELS:
        return key

    label = str(get_first(result, "conduit_material", default="")).lower()
    reverse_labels = {label.lower(): key for key, label in CONDUIT_LABELS.items() if key is not None}
    return reverse_labels.get(label)


def _flag(result: dict[str, Any], key: str, fallback: bool | None) -> bool:
    return bool(get_first(result, key, default=fallback))


def _label_from_result(result: dict[str, Any], value_key: str, label_key: str, labels: dict[Any, str]) -> str:
    value = get_first(result, value_key)
    return get_first(result, label_key, default=None) or labels.get(value, str(value or "—"))


def _method_label(vd_mode: str) -> str:
    return METHOD_LABELS.get(vd_mode, str(vd_mode))


def _conductor_size_text(result: dict[str, Any]) -> str:
    size = get_first(result, "conductor_size")
    unit = get_first(result, "size_unit", default="")
    return "—" if size is None else f"{size} {unit}".strip()


def _uses_temperature_adjustment(vd_mode: str, use_custom_pf: bool = False, use_custom_T_op: bool = False) -> bool:
    return vd_mode == "table8_r" or (vd_mode == "table9_z" and use_custom_pf and use_custom_T_op)


def _temperature_coefficient(result: dict[str, Any]) -> float | None:
    material = get_first(result, "conductor_material_key")
    if material == "cu":
        return 0.00300
    if material == "al":
        return 0.00323
    return None


# ============================================================
# Equations
# ============================================================
def _temperature_adjustment_equation() -> str:
    return (
        omml_r("R = ")
        + omml_sub("R", "1")
        + omml_r(" × [1 + α × (")
        + omml_sub("T", "op")
        + omml_r(" - 75)]")
    )


def _effective_impedance_equation() -> str:
    return (
        omml_sub("Z", "eff")
        + omml_r(" = R × pf + ")
        + omml_sub("X", "L")
        + omml_r(" × ")
        + omml_sqrt(omml_r("1 - pf²"))
    )


def _voltage_drop_equation(vd_mode: str, use_custom_pf: bool = False) -> str:
    if vd_mode == "table9_z":
        z_term = omml_sub("Z", "eff") if use_custom_pf else omml_r("Z")
        numerator = omml_r("f × ") + z_term + omml_r(" × ") + omml_sub("I", "eff") + omml_r(" × L")
    else:
        r_term = omml_sub("R", "manual") if vd_mode == "manual_r" else omml_r("R")
        numerator = omml_r("pf × f × ") + r_term + omml_r(" × ") + omml_sub("I", "eff") + omml_r(" × L")

    return omml_sub("V", "D") + omml_r(" = ") + omml_frac(numerator, omml_r("1000"))


def add_voltage_drop_equations(doc, context: dict[str, Any]) -> None:
    vd_mode = context["vd_mode"]
    use_custom_pf = context["use_custom_pf"]
    use_custom_T_op = context["use_custom_T_op"]

    doc.add_heading("Equations Used", level=1)
    add_word_equation(
        doc,
        "Effective current",
        omml_sub("I", "eff") + omml_r(" = ") + omml_frac(omml_r("I"), omml_sub("N", "parallel")),
    )

    if _uses_temperature_adjustment(vd_mode, use_custom_pf, use_custom_T_op):
        add_word_equation(doc, "Temperature-adjusted resistance", _temperature_adjustment_equation())

    if vd_mode == "table9_z" and use_custom_pf:
        add_word_equation(doc, "Effective impedance", _effective_impedance_equation())

    add_word_equation(doc, "Voltage drop", _voltage_drop_equation(vd_mode, use_custom_pf))
    add_word_equation(
        doc,
        "Voltage drop percentage",
        omml_r("%ΔV = ") + omml_frac(omml_r("100 × ") + omml_sub("V", "D"), omml_sub("V", "nom")),
    )


def _build_equations_for_excel(context: dict[str, Any]) -> list[tuple[str, str]]:
    vd_mode = context["vd_mode"]
    use_custom_pf = context["use_custom_pf"]
    use_custom_T_op = context["use_custom_T_op"]
    equations = [("Effective current", "I_eff = I / N_parallel")]

    if _uses_temperature_adjustment(vd_mode, use_custom_pf, use_custom_T_op):
        equations.append(("Temperature-adjusted resistance", "R = R_1 × [1 + α × (T_op - 75)]"))

    if vd_mode == "table9_z" and use_custom_pf:
        equations.extend([
            ("Effective impedance", "Z_eff = R × pf + X_L × sqrt(1 - pf^2)"),
            ("Voltage drop", "V_D = f × Z_eff × I_eff × L / 1000"),
        ])
    elif vd_mode == "table9_z":
        equations.append(("Voltage drop", "V_D = f × Z × I_eff × L / 1000"))
    elif vd_mode == "manual_r":
        equations.append(("Voltage drop", "V_D = pf × f × R_manual × I_eff × L / 1000"))
    else:
        equations.append(("Voltage drop", "V_D = pf × f × R × I_eff × L / 1000"))

    equations.append(("Voltage drop percentage", "%ΔV = 100 × V_D / V_nom"))
    return equations


# ============================================================
# Report sections
# ============================================================
def _build_result_pairs(result: dict[str, Any]) -> list[tuple[str, Any]]:
    return [
        ("Estimated voltage drop, VD (V)", get_first(result, "voltage_drop")),
        ("Voltage drop percentage (%)", get_first(result, "percent_drop")),
    ]


def _build_input_pairs(result: dict[str, Any], context: dict[str, Any]) -> list[tuple[str, Any]]:
    vd_mode = context["vd_mode"]
    use_custom_pf = context["use_custom_pf"]
    use_custom_T_op = context["use_custom_T_op"]
    conduit_key = context["conduit_material"]

    pairs: list[tuple[str, Any]] = [
        ("Calculation method", _method_label(vd_mode)),
        ("System type", context["system_type_label"]),
        ("Calculation current, I (A)", get_first(result, "current")),
        ("Nominal voltage, Vnom (V)", get_first(result, "v_nom", "voltage")),
        ("One-way length, L (ft)", get_first(result, "length")),
        ("Parallel conductors per phase/pole", get_first(result, "parallel_conductors")),
        ("Effective current, Ieff (A)", get_first(result, "I_eff")),
        ("Voltage-drop system factor, f", get_first(result, "f")),
        ("Power factor", get_first(result, "pf")),
    ]

    if vd_mode in ("table8_r", "table9_z"):
        pairs.extend([
            ("Conductor size", _conductor_size_text(result)),
            ("Conductor material", _label_from_result(result, "conductor_material_key", "conductor_material", CONDUCTOR_LABELS)),
            ("Operating temperature (°C)", get_first(result, "temperature")),
        ])

    if _uses_temperature_adjustment(vd_mode, use_custom_pf, use_custom_T_op):
        pairs.append(("Temperature coefficient, α (1/°C)", _temperature_coefficient(result)))

    if vd_mode == "table8_r":
        pairs.extend([
            ("NEC source", "Chapter 9, Table 8"),
            ("Coating type", _label_from_result(result, "coating_type_key", "coating_type", COATING_LABELS)),
            ("Raw Table 8 resistance, R1 (Ω/kft)", get_first(result, "r_base_value")),
            ("Final resistance used, R (Ω/kft)", get_first(result, "r_value")),
        ])

    elif vd_mode == "table9_z":
        pairs.extend([
            ("NEC source", "Chapter 9, Table 9"),
            ("Conduit material", CONDUIT_LABELS.get(conduit_key, get_first(result, "conduit_material", default="—"))),
            ("Use custom power factor", yes_no(use_custom_pf)),
            ("Use custom operating temperature", yes_no(use_custom_T_op)),
        ])

        if use_custom_pf:
            pairs.extend([
                ("Raw Table 9 reactance, XL (Ω/kft)", get_first(result, "xl_value")),
                ("Raw Table 9 resistance, R1 (Ω/kft)", get_first(result, "r_base_value")),
                ("Final resistance used, R (Ω/kft)", get_first(result, "r_value")),
                ("Final impedance used, Z (Ω/kft)", get_first(result, "z_value")),
            ])
        else:
            pairs.append(("Table 9 impedance used, Z (Ω/kft)", get_first(result, "z_value")))

    elif vd_mode == "manual_r":
        pairs.extend([
            ("NEC source", "Manual user-entered resistance"),
            ("Manual resistance used, R (Ω/kft)", get_first(result, "manual_r", "r_value")),
            ("Conductor size reference", _conductor_size_text(result)),
            ("Conductor material reference", _label_from_result(result, "conductor_material_key", "conductor_material", CONDUCTOR_LABELS)),
            ("Temperature reference (°C)", get_first(result, "temperature", default="—")),
        ])

    return pairs


def _build_notes(vd_mode: str, use_custom_pf: bool = False, use_custom_T_op: bool = False) -> list[str]:
    notes = [
        "This report is based on the input values entered into the calculator.",
        "Final selections and design decisions should be verified against the NEC, project specifications, equipment data, and engineering judgement.",
        "Voltage drop limits may be imposed by project specifications or authority requirements even where NEC informational notes are not mandatory requirements.",
    ]

    mode_notes = {
        "table8_r": "The resistance method uses NEC Chapter 9, Table 8 resistance values. Reactance is not included in this simplified resistance-based calculation.",
        "table9_z": "The AC impedance method uses NEC Chapter 9, Table 9 values. Confirm the Table 9 assumptions are suitable for the installation.",
        "manual_r": "The manual resistance method uses the user-entered resistance value directly. The entered value should already reflect the intended conductor, material, and temperature basis.",
    }
    notes.append(mode_notes.get(vd_mode, "Confirm the selected voltage-drop method is suitable for the installation."))

    if _uses_temperature_adjustment(vd_mode, use_custom_pf, use_custom_T_op):
        notes.append("Resistance is temperature-adjusted using R = R1 × [1 + α × (Top - 75)], where α = 0.00300 for copper and α = 0.00323 for aluminum.")

    return notes


# ============================================================
# NEC source table row
# ============================================================
def _table9_material_prefix(result: dict[str, Any]) -> str:
    return "aluminum" if get_first(result, "conductor_material_key") == "al" else "cu_uncoated"


def _table9_xl_column(conduit_material: str | None) -> str:
    return "xl_steel_conduit_ohm_kft" if conduit_material == "st" else "xl_pvc_aluminum_conduits_ohm_kft"


def _build_source_table_from_result(result: dict[str, Any], vd_mode: str, conduit_material: str | None = None):
    if vd_mode == "table8_r":
        return build_nec_table_row_source(
            table_name="TABLE_8",
            criteria={"size_awg_kcmil": str(get_first(result, "conductor_size"))},
            columns=TABLE8_COLUMNS,
            column_labels=TABLE8_LABELS,
            title="Selected NEC Chapter 9 Table 8 Row",
        )

    if vd_mode == "table9_z":
        conduit_key = TABLE9_CONDUIT_KEYS.get(conduit_material, "pvc")
        material_prefix = _table9_material_prefix(result)
        xl_col = _table9_xl_column(conduit_material)
        r_col = f"{material_prefix}_ac_resistance_{conduit_key}_conduit_ohm_kft"
        z_col = f"{material_prefix}_eff_z_085pf_{conduit_key}_conduit_ohm_kft"

        return build_nec_table_row_source(
            table_name="TABLE_9",
            criteria={"size_awg_kcmil": str(get_first(result, "conductor_size"))},
            columns=["size_awg_kcmil", xl_col, r_col, z_col],
            column_labels={
                "size_awg_kcmil": "Size",
                xl_col: "Reactance XL (Ω/kft)",
                r_col: "AC Resistance R (Ω/kft)",
                z_col: "Effective Z at 0.85 PF (Ω/kft)",
            },
            title="Selected NEC Chapter 9 Table 9 Row",
        )

    return None


def _build_report_context(
    result: dict[str, Any],
    vd_mode: Any = None,
    system_type_label: Any = None,
    conduit_material: Any = None,
    use_custom_pf: bool | None = None,
    use_custom_T_op: bool | None = None,
) -> dict[str, Any]:
    vd_mode_key = _mode_key(result, vd_mode)
    conduit_key = _conduit_key(result, conduit_material)
    custom_pf = _flag(result, "use_custom_pf", use_custom_pf)
    custom_T = _flag(result, "use_custom_T_op", use_custom_T_op)

    context = {
        "vd_mode": vd_mode_key,
        "system_type_label": _system_label(result, system_type_label),
        "conduit_material": conduit_key,
        "use_custom_pf": custom_pf,
        "use_custom_T_op": custom_T,
        "notes": _build_notes(vd_mode_key, custom_pf, custom_T),
        "result_pairs": _build_result_pairs(result),
        "source_table": _build_source_table_from_result(result, vd_mode_key, conduit_key),
    }
    context["input_pairs"] = _build_input_pairs(result, context)
    return context


# ============================================================
# Builders
# ============================================================
def build_word_report(
    result: dict[str, Any],
    vd_mode: Any = None,
    system_type_label: Any = None,
    conduit_material: Any = None,
    use_custom_pf: bool | None = None,
    use_custom_T_op: bool | None = None,
) -> bytes:
    return build_standard_word_report(
        report_title=REPORT_TITLE,
        result=result,
        context_builder=lambda r: _build_report_context(r, vd_mode, system_type_label, conduit_material, use_custom_pf, use_custom_T_op),
        word_equation_builder=add_voltage_drop_equations,
    )


def build_excel_report(
    result: dict[str, Any],
    vd_mode: Any = None,
    system_type_label: Any = None,
    conduit_material: Any = None,
    use_custom_pf: bool | None = None,
    use_custom_T_op: bool | None = None,
) -> bytes:
    return build_standard_excel_report(
        report_title=REPORT_TITLE,
        sheet_name=SHEET_NAME,
        result=result,
        context_builder=lambda r: _build_report_context(r, vd_mode, system_type_label, conduit_material, use_custom_pf, use_custom_T_op),
        excel_equation_builder=_build_equations_for_excel,
    )


def render_export_report(
    result: dict[str, Any] | None,
    vd_mode: Any = None,
    system_type_label: Any = None,
    conduit_material: Any = None,
    use_custom_pf: bool | None = None,
    use_custom_T_op: bool | None = None,
) -> None:
    render_standard_export_report(
        prefix="nec_voltage_drop",
        docx_file="nec_voltage_drop_report.docx",
        xlsx_file="nec_voltage_drop_report.xlsx",
        result=result,
        required_keys=("voltage_drop", "percent_drop"),
        word_builder=lambda r: build_word_report(r, vd_mode, system_type_label, conduit_material, use_custom_pf, use_custom_T_op),
        excel_builder=lambda r: build_excel_report(r, vd_mode, system_type_label, conduit_material, use_custom_pf, use_custom_T_op),
    )
