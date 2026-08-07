from __future__ import annotations

import streamlit as st

from nec_calc.common.units import MetricPrefix, Voltage, ApparentPower
from nec_calc.common.enums import LabeledEnum, SystemTypes
from nec_calc.common.formatting import fmt, next_standard_size
from lib.nec_tables import NEC_2406A_STANDARD

def header(title: str, subtitle: str = ""):
    st.header(title)
    if subtitle:
        st.write(subtitle)

def show_code_note(selected_code: str):
    st.info(
        f"Code mode: **{selected_code}**. "
        "This site is written to be easy to follow. Always verify final selections against the code, "
        "project specs, equipment data, and a coordination study where required."
    )

def eq(latex: str):
    """Render a LaTeX equation in a consistent display style."""
    st.latex(latex)


def enum_selectbox(container, label: str, options, format_func=lambda m: getattr(m, "label", getattr(m, "name", str(m))), **kwargs):
    return container.selectbox(
        label=label, 
        options=options, 
        format_func=format_func, 
        **kwargs
    )

def enum_radio(container, label: str, options, format_func=lambda m: getattr(m, "label", getattr(m, "name", str(m))), **kwargs):
    return container.radio(
        label=label, 
        options=options, 
        format_func=format_func, 
        **kwargs
    )

def quant_selectbox(container, label: str, options, **kwargs):
    return container.selectbox(
        label=label, 
        options=list(MetricPrefix), 
        format_func=lambda prefix: f"{prefix.prefix}{options.base_symbol}", 
        **kwargs
    )
    

def quant_unit_input(
    label: str, 
    options, 
    value: float = 0.0, 
    min_value: float | None = 0.0, 
    max_value: float | None = None, 
    step: float = 1.0, 
    unit_index: int = 0
):
    c1, c2 = st.columns([4, 1])
    
    unit = quant_selectbox(
        container=c2, 
        label="Unit", 
        options=options, 
        index=unit_index,
        key=f"{label}_unit"
    )
    
    quant = c1.number_input(
        label=f"{label} ({options.unit(unit)})", 
        value=value,
        min_value=min_value, 
        max_value=max_value,
        step=step,
        key=f"{label}_quant"
    )
    
    return options.of(quant, unit)

def transformer_feeder_inputs(
    system_type: SystemTypes | None = None, 
    transformer_rating: ApparentPower | None = None, 
    v_pri: Voltage | None = None, 
    v_sec: Voltage | None = None
):
    c1, _ = st.columns([4, 1])
    
    system_type = system_type or enum_selectbox(c1, "System Type", SystemTypes.exclude(SystemTypes.DC), index=0)
    
    v_pri = v_pri or quant_unit_input("Primary transformer voltage", Voltage, value=480.0, step=1.0, unit_index=1)
    v_sec = v_sec or quant_unit_input("Secondary transformer voltage", Voltage, value=120.0, step=1.0, unit_index=1)
    transformer_rating = transformer_rating or quant_unit_input("Transformer rating", ApparentPower, value=15.0, step=0.1, unit_index=2)
    
    return {
        "phase": system_type.key,
        "current_factor": system_type.current_factor,
        "transformer_rating": transformer_rating.to(),
        "V_data": {
            "V_primary": v_pri.to(),
            "V_secondary": v_sec.to(),
        },
    }
    
def _show_result(
    label: str,
    raw: float | None,
    std_list: list[float] | None = NEC_2406A_STANDARD,
    round_to_std: bool = True,
    direction: str = "up",
    selected_label: str = "Selected standard",
    caption: str | None = None,
) -> float | None:
    if raw is None:
        st.error(f"{label}: no value computed.")
        return None

    if round_to_std and std_list:
        std = next_standard_size(raw, std_list, direction)
        if std is None:
            edge = "exceeds" if direction == "up" else "is below"
            st.error(
                f"{label}: Raw = **{fmt(raw, 'A')}** → {edge} the standard list. "
            )
        else:
            st.success(
                f"{label}: Raw = **{fmt(raw, 'A')}** → {selected_label} = **{fmt(std, 'A')}**"
            )
        result = std
    else:
        st.success(f"{label}: **{fmt(raw, 'A')}**")
        result = raw

    if caption:
        st.caption(caption)

    return result

__all__ = [
    "header", "show_code_note", "eq", "enum_selectbox", "enum_radio",
    "quant_selectbox", "quant_unit_input", "transformer_feeder_inputs", "_show_result",
]
