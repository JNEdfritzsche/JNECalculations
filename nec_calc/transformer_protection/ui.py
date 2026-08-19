import streamlit as st

from calc_common.report_schedule import apply_restore
from calc_common.enums import LocationTypes, ProtectionOptions, SystemTypes, TransformerSourceOptions
from calc_common.formatting import fmt
from calc_common.ui_helpers import enum_radio, enum_selectbox, quant_unit_input, transformer_feeder_inputs, eq
from calc_common.units import Voltage
from content.charts.flowcharts import get_nec_transformer_protection_flowchart
from nec_calc.transformer_protection.calculation import calc_transformer_protection, calc_voltage_class
from calc_common.physics import calc_flas
from nec_calc.transformer_protection.report import (
    TP_SCHEDULE_SPEC,
    render_add_to_schedule,
    render_schedule_section,
)
from lib.nec_tables import TABLES

def _show_device(label, device):
    raw = device.get("size")
    std = device.get("standard")

    if std is None:
        st.success(f"{label}: Maximum = **{fmt(raw, 'A')}**")
    else:
        st.success(
            f"{label}: Maximum = **{fmt(raw, 'A')}** → Selected = **{fmt(std, 'A')}**"
        )
    if device.get("basis"):
        st.caption(device["basis"])


def _show_ocpd(side, cb, fr):
    if cb.get("size") is None and fr.get("size") is None:
        st.info(f"{side} protection: **Not required**")
    elif cb == fr:
        _show_device(rf"Max {side} Breaker/Fuse ({cb.get("mult")}% $\times I_{{flc}}$)", cb)
    else:
        _show_device(rf"Max {side} Breaker ({cb.get("mult")}% $\times I_{{flc}}$)", cb)
        _show_device(rf"Max {side} Fuse ({fr.get("mult")}% $\times I_{{flc}}$)", fr)

@st.fragment
def render_calc():
    apply_restore(TP_SCHEDULE_SPEC)

    st.markdown("### Transformer Protection Flowchart")
    st.graphviz_chart(get_nec_transformer_protection_flowchart())
    st.caption("NOTE: P&S denotes direct secondary protection and **upstream** primary protection.")
    
    inputs_pane, result_pane = st.columns([1.45,1], gap="large")
    
    with inputs_pane, st.container(border=True):
        st.markdown("### Inputs")

        calc_method = enum_radio(
            st, "Calculation method", TransformerSourceOptions, horizontal=False,
            key="tp_calc_method",
        )
        
        if calc_method == TransformerSourceOptions.CALCULATED:
            inputs = transformer_feeder_inputs(key_prefix="tp_calc")
            flas = calc_flas(inputs)
        else:
            v_pri = quant_unit_input("Primary transformer voltage", step=1.0, value=480.0, options=Voltage, min_value=0.0, index=1, key_prefix="tp_np")
            v_sec = quant_unit_input("Secondary transformer voltage", step=1.0, value=120.0, options=Voltage, min_value=0.0, index=1, key_prefix="tp_np")
            
            inputs = {
                "phase": None,
                "transformer_rating": None,
                "V_data": 
                    {
                        "V_primary": v_pri.to(),
                        "V_secondary": v_sec.to(),
                    },
            }
            
            c1, c2, _ = st.columns([2, 2, 1])
            flas = {
                "primary_fla": c1.number_input(
                    "Nameplate primary FLA (A)", min_value=0.01, step=0.01, value=72.0, key="tp_np_pri_fla"
                ),
                "secondary_fla": c2.number_input(
                    "Nameplate secondary FLA (A)", min_value=0.01, step=0.01, value=208.0, key="tp_np_sec_fla"
                ),
            }

        V_data = inputs.get("V_data")

        st.divider()

        st.markdown("### Code-based OCPD limits")
        st.markdown("#### NEC — Rule-based sizing (implemented per the attached NEC calculation)")
        
        calc_inputs = {
            "protection_method": None,
            "flc_key": None,
            "location_type": None,
            "tx_z": None,
            "phase": inputs.get("phase"),
            "transformer_rating": inputs.get("transformer_rating"),
            "nameplate_used": calc_method == TransformerSourceOptions.NAMEPLATE,
        }
        
        if calc_voltage_class(**V_data) == "low":
            c1, _ = st.columns([1, 4])
            
            calc_inputs["protection_method"] = enum_radio(c1, "Protection configuration", ProtectionOptions, horizontal=True, index=0, key="tp_prot_low")

            calc_inputs["flc_key"] = "primary_fla" if calc_inputs.get("protection_method") == ProtectionOptions.PRIMARY_ONLY else "secondary_fla"
        else:
            c1, c2 = st.columns(2)
            
            calc_inputs["location_type"] = enum_selectbox(c1, "Location type", LocationTypes, key="tp_location")
            
            calc_inputs["protection_method"] = enum_radio(c2, "Protection configuration", ProtectionOptions, horizontal=True, index=0, key="tp_prot_sup") if calc_inputs.get("location_type") == LocationTypes.SUPERVISED else None
            
            c1, _ = st.columns([4,1])
            if not calc_inputs.get("protection_method") == ProtectionOptions.PRIMARY_ONLY:
                calc_inputs["tx_z"] = c1.number_input("Transformer impedance (%Z)", min_value=0.01, max_value= 100.00, value=2.75, step=0.01, key="tp_tx_z")
                
        result = calc_transformer_protection(
            V_data,
            flas,
            **calc_inputs,
        ) 
        
    with result_pane, st.container(border=True):
        
        st.markdown("### Results")
        m1, m2 = st.columns(2)
        m1.metric("Primary Full-Load Current", fmt(flas.get("primary_fla")) + " A")
        m2.metric("Secondary Full-Load Current", fmt(flas.get("secondary_fla")) + " A")
        
        pri_cb = result.get("primary_cb")
        pri_fr = result.get("primary_fr")    
        sec_cb = result.get("secondary_cb")
        sec_fr = result.get("secondary_fr")  
        
        pri_sym = ">" if V_data.get("V_primary") > 1000 else r"$\leq$"
        sec_sym = ">" if V_data.get("V_secondary") > 1000 else r"$\leq$"
        
        st.markdown(rf"**Primary OCPD (Vpri {pri_sym} 1000 V):**")
        _show_ocpd("Primary", pri_cb, pri_fr)
        
        st.markdown(rf"**Secondary OCPD (Vsec {sec_sym} 1000 V):**")
        _show_ocpd("Secondary", sec_cb, sec_fr)
        
        st.divider()
        render_add_to_schedule(result)  

        with st.expander("Code reference - how the multipliers were selected"):
            st.markdown(f"**{TABLES.get(result.get("table_used")).get("title")}**")
            
            st.markdown("**Row matched:**")
            for key, value in result.get("row_criteria").items():
                st.write(f"- {key}: **{value}**")
            
            st.markdown("**Columns used:**")
            # Cells the table marks "Not required" were never applied, so listing their
            # column would imply a reference this calculation does not rely on.
            columns = []
            for entry in [pri_cb, pri_fr, sec_cb, sec_fr]:
                if entry.get("mult") is None:
                    continue
                if (entry.get("column"), entry.get("mult")) not in columns:
                    columns.append((entry.get("column"), entry.get("mult")))
            for column, mult in columns:
                st.write(f"- {column}: **{mult}%**")

            not_required = [
                side for side, entries in (("Primary", (pri_cb, pri_fr)), ("Secondary", (sec_cb, sec_fr)))
                if all(e.get("mult") is None for e in entries)
            ]
            for side in not_required:
                st.write(f"- {side} protection: **Not required** by this row")
                
        with st.expander("Parameters & equations used"):
            st.markdown("### Equations used")

            if calc_method == TransformerSourceOptions.CALCULATED:
                if result["phase"] == SystemTypes.THREE_PHASE.key:
                    eq(r"I=\frac{S}{\sqrt{3}\,V}")
                else:
                    eq(r"I=\frac{S}{V}")

            eq(r"I_{OCPD,max}=\text{mult}\%\times I_{flc}")
    
    st.divider()
    render_schedule_section()