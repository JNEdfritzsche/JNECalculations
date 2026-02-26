# Standard library
import io
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

# Third-party
import streamlit as st
from docx import Document
from docx.shared import Pt
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

# Optional pandas (used for table processing on Conduit page)
try:
    import pandas as pd  # type: ignore
except ImportError:
    pd = None  # type: ignore

# Local application imports
try:
    from lib.theory import render_md  # type: ignore
    _THEORY_IMPORT_ERROR = None
except Exception as e:
    render_md = None  # type: ignore
    _THEORY_IMPORT_ERROR = str(e)

try:
    from lib import oesc_tables  # type: ignore
    _TABLES_IMPORT_ERROR = None
except Exception as e:
    oesc_tables = None  # type: ignore
    _TABLES_IMPORT_ERROR = str(e)

# Set to False during development to disable password protection
ENABLE_PASSWORD_PROTECTION = False

# ----------------------------
# Global Variables
# ----------------------------
PROJECT_NUMBER = ""
DESIGNER_NAME = ""

# ----------------------------
# Report Export Helpers
# ----------------------------
def append_to_value_line(cell, value: str, paragraph_index: int = 1):
# Ensure the paragraph exists
    while len(cell.paragraphs) <= paragraph_index:
        cell.add_paragraph("")

    p = cell.paragraphs[paragraph_index]

    # Append text to existing formatting
    p.add_run(value)


def add_omml_equation_to_paragraph(p, omml_inner: str) -> None:
    """
    Appends an inline Word equation (<m:oMath>) to an existing paragraph.
    `omml_inner` is the content inside <m:oMath>...</m:oMath>.
    """
    xml = f'<m:oMath {nsdecls("m")}>{omml_inner}</m:oMath>'
    p._p.append(parse_xml(xml))


def set_table_borders(table):
    tbl = table._tbl
    tblPr = tbl.tblPr

    borders = OxmlElement('w:tblBorders')

    for border_name in (
        'top', 'left', 'bottom', 'right',
        'insideH', 'insideV'
    ):
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'single')   # line style
        border.set(qn('w:sz'), '8')         # thickness (8 = 1pt)
        border.set(qn('w:space'), '0')
        border.set(qn('w:color'), '000000') # black
        borders.append(border)

    tblPr.append(borders)


def _delete_paragraph(p):
    # python-docx has no public delete API; remove the underlying XML element
    p._element.getparent().remove(p._element)
    p._p = p._element = None


def remove_leading_blank_paragraphs(doc: Document):
    # Remove any completely empty paragraphs at the very start of the document body
    while doc.paragraphs and doc.paragraphs[0].text.strip() == "":
        _delete_paragraph(doc.paragraphs[0])


st.set_page_config(
    page_title="Electrical Calculations Hub",
    page_icon="⚡",
    layout="wide",
)


# Center all images (both st.image and markdown-rendered images)
st.markdown(
    """
<style>
img { display: block; margin-left: auto; margin-right: auto; }
.stImage { text-align: center; }
/* Hide horizontal scrollbars on LaTeX blocks (keeps content scrollable if needed) */
.katex-display { scrollbar-width: none; -ms-overflow-style: none; }
.katex-display::-webkit-scrollbar { display: none; }
</style>
""",
    unsafe_allow_html=True,
)

# ----------------------------
# Password Protection
# ----------------------------
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        try:
            correct_password = st.secrets["app_password"]
        except (KeyError, FileNotFoundError):
            correct_password = "admin"  # fallback default
        
        if st.session_state["password"] == correct_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.text_input(
        "Enter password to access the site:",
        type="password",
        on_change=password_entered,
        key="password",
    )

    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("❌ Incorrect password")

    return False


if ENABLE_PASSWORD_PROTECTION and not check_password():
    st.stop()

st.title("⚡ Electrical Calculations Hub")
st.caption("Theory • Examples • Calculators")

# ----------------------------
# Helpers
# ----------------------------
# ----------------------------
# Conduit fill rule selector (CEC / OESC Table 9 logic)
# ----------------------------
def select_table9_fill_rule(num_cables: int):
    """
    Returns which Table 9 group to use based on number of cables.
    1 cable  -> 53% (Tables C/D)
    2 cables -> 31% (Tables E/F)
    >=3      -> 40% (Tables G/H)
    """
    if num_cables <= 1:
        return {
            "percent": 53,
            "tables": ["C", "D"],
            "label": "53% fill (1 cable – Tables C/D)"
        }
    elif num_cables == 2:
        return {
            "percent": 31,
            "tables": ["E", "F"],
            "label": "31% fill (2 cables – Tables E/F)"
        }
    else:
        return {
            "percent": 40,
            "tables": ["G", "H"],
            "label": "40% fill (3+ cables – Tables G/H)"
        }


def fmt(x, unit=""):
    if x is None:
        return "—"
    try:
        x = float(x)
    except Exception:
        return str(x)
    if abs(x) >= 1e6:
        s = f"{x:,.3g}"
    elif abs(x) >= 1:
        s = f"{x:,.4g}"
    else:
        s = f"{x:.6g}"
    return f"{s} {unit}".strip()


def safe_div(a, b):
    return None if b == 0 else a / b


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


def _numeric_sort_key(s):
    """
    Generate a sort key that handles numeric strings properly.
    Converts strings like '12', '103', '1/0' to sortable tuples.
    '1/0' and fractions are treated as having a fractional part for sorting.
    """
    s = str(s).strip()
    try:
        # Try simple float conversion first (handles "12", "103", etc.)
        return (0, float(s))
    except ValueError:
        # Handle fractions like "1/0", "2/0", etc.
        if "/" in s:
            try:
                parts = s.split("/")
                numerator = float(parts[0])
                denominator = float(parts[1])
                value = numerator / denominator
                return (0, value)
            except Exception:
                pass
        # Fallback to string sort for non-numeric values
        return (1, s)


def _numeric_sort(items):
    """Sort items numerically, handling strings with fractions and regular numbers."""
    return sorted(items, key=_numeric_sort_key)

def format_cond_size(size_value):
    """Format conductor size with AWG/kcmil suffix based on numeric value."""
    s = str(size_value).strip()
    if not s or s == "(size not found)":
        return s
    s_lower = s.lower()
    if "kcmil" in s_lower or "mcm" in s_lower:
        return re.sub(r"\s*(kcmil|mcm)\s*", " kcmil", s, flags=re.IGNORECASE).strip()
    if "awg" in s_lower:
        return re.sub(r"\s*awg\s*", " AWG", s, flags=re.IGNORECASE).strip()
    if "/" in s:
        return f"{s} AWG"
    try:
        val = float(s)
        return f"{s} kcmil" if val >= 250 else f"{s} AWG"
    except Exception:
        return s


def eq(latex: str):
    """Render a LaTeX equation in a consistent display style."""
    st.latex(latex)


# ----------------------------
# Content paths (reliable on Streamlit Cloud)
# ----------------------------
APP_DIR = Path(__file__).parent
CONTENT_DIR = APP_DIR / "content"


def render_md_safe(rel_path: str):
    """
    Render markdown from /content safely.
    - Uses lib.theory.render_md if available
    - Otherwise shows a friendly error instead of crashing the app
    """
    md_path = CONTENT_DIR / rel_path

    if render_md is None:
        st.error(
            "Theory renderer failed to import. This usually means the `lib/` package is missing in your repo. "
            "Make sure you have:\n\n"
            "- `lib/__init__.py`\n"
            "- `lib/theory.py`\n"
        )
        if _THEORY_IMPORT_ERROR is not None:
            with st.expander("Import error details"):
                st.exception(_THEORY_IMPORT_ERROR)
        st.info(f"Expected markdown path: `{md_path}`")
        if md_path.exists():
            st.warning("Markdown file exists, but renderer is unavailable due to the import error above.")
        else:
            st.warning("Markdown file not found at the expected path.")
        return

    # renderer exists
    render_md(str(md_path))


# Standard device rating helpers
NEC_2406A_STANDARD = [
    15, 20, 25, 30, 35, 40, 45, 50,
    60, 70, 80, 90, 100, 110, 125, 150,
    175, 200, 225, 250, 300, 350, 400, 450,
    500, 600, 700, 800, 1000, 1200, 1600, 2000,
    2500, 3000, 4000, 5000, 6000
]

# Practical "standard" list used by the attached OESC calc (Table 13 style). This list is commonly aligned with the NEC list.
OESC_TABLE13_STANDARD = NEC_2406A_STANDARD[:]


def next_standard(value, standard_list):
    """Return the next standard value >= value. If value exceeds list, return None."""
    try:
        v = float(value)
    except Exception:
        return None
    for s in standard_list:
        if s >= v - 1e-12:
            return s
    return None


def calc_fla(kva, volts, phase):
    """
    FLA from kVA and voltage.
    - 3Φ: I = S / (sqrt(3)*V_LL)
    - 1Φ: I = S / V
    """
    s_va = float(kva) * 1000.0
    v = float(volts)
    if phase == "3Φ":
        return s_va / (math.sqrt(3) * v) if v > 0 else None
    return s_va / v if v > 0 else None


# ----------------------------
# Sidebar navigation
# ----------------------------
PAGES = [
    "Home",
    "Transformer Protection",
    "Transformer Feeders",
    "Grounding/Bonding Conductor Sizing",
    "Motor Protection",
    "Motor Feeder",
    "Cable Tray Size & Fill & Bend Radius",
    "Conduit Size & Fill & Bend Radius",
    "Cable Tray Ampacity",
    "Demand Load",
    "Power Factor Correction",
    "Voltage Drop",
    "Conductors",
    "Table Library",
]

with st.sidebar:
    st.header("Navigate")
    page = st.radio("Go to", PAGES, index=0)

    st.divider()
    st.header("Jurisdiction")
    code_mode = st.selectbox("Select electrical code", ["NEC", "OESC"], index=1)

    st.divider()
    st.header("Report Information")
    PROJECT_NUMBER = st.text_input("Project number", value=PROJECT_NUMBER, key="project_number")
    DESIGNER_NAME = st.text_input("Designer name", value=DESIGNER_NAME, key="designer_name")    

    st.divider()
    st.caption("This portal is provided for educational purposes only and is intended to support the understanding of engineering concepts. The tutorials, examples, and tools are not a substitute for professional judgment. Always consult applicable codes, regulations, and qualified engineers before making design or compliance decisions.")


# ----------------------------
# Page shell with Theory/Calculator tabs
# (Tabs are disabled ONLY on Table Library)
# ----------------------------
if page not in ("Table Library", "Home"):
    theory_tab, calc_tab = st.tabs(["📚 Theory", "🧮 Calculator"])
else:
    theory_tab = None
    calc_tab = None


# ============================
# 0) Home
# ============================
if page == "Home":
    header("Welcome", "Start here for quick context and how to use this hub.")
    show_code_note(code_mode)

    st.markdown("### What you can do")
    st.markdown("- Find code-aligned theory notes with worked examples.")
    st.markdown("- Run calculators for sizing, protection, and voltage drop.")
    st.markdown("- Compare NEC vs OESC assumptions using the sidebar selector.")

    st.markdown("### Popular tools")
    st.markdown("- Transformer Protection")
    st.markdown("- Voltage Drop")
    st.markdown("- Conduit Size & Fill & Bend Radius")
    st.markdown("- Cable Tray Size & Fill & Bend Radius")

    st.markdown("### Quick start")
    st.markdown("1. Pick a topic from the sidebar.")
    st.markdown("2. Use the `Theory` tab for context and code references.")
    st.markdown("3. Switch to `Calculator` for inputs and results.")
    st.markdown("4. Change `Jurisdiction` to see NEC vs OESC logic.")


# ============================
# 1) Transformer Protection
# ============================
if page == "Transformer Protection":
    with theory_tab:
        header("Transformer Protection", "Code-focused theory and worked examples (moved to Markdown).")
        show_code_note(code_mode)

        if code_mode == "OESC":
            render_md_safe("transformer_protection_oesc.md")
        else:
            render_md_safe("transformer_protection_nec.md")

    # ----------------------------
    # Calculator tab for Transformer Protection
    # ----------------------------
    with calc_tab:
        header("Transformer Protection Calculator", "Compute transformer currents + code-based OCPD limits (per attached calc documents).")
        show_code_note(code_mode)

        st.markdown("### Inputs")
        c1, c2, c3, c4 = st.columns([1, 1, 1, 1], gap="large")
        with c1:
            phase = st.selectbox("System", ["3Φ", "1Φ"], index=0, key="tp_phase")
        with c2:
            kva = st.number_input("Transformer size (kVA)", min_value=0.1, value=75.0, step=1.0, key="tp_kva")
        with c3:
            vpri = st.number_input("Primary voltage (V)", min_value=1.0, value=600.0, step=1.0, key="tp_vpri")
        with c4:
            vsec = st.number_input("Secondary voltage (V)", min_value=1.0, value=208.0, step=1.0, key="tp_vsec")

        st.caption(
            "Units note: This calculator assumes kVA and volts. For 3Φ, it uses line-to-line voltage. "
            "Use nameplate FLA when available."
        )

        st.markdown("### Full-load current (nameplate optional)")
        use_nameplate = st.checkbox("Use nameplate FLA inputs instead of calculating from kVA/V", value=False, key="tp_use_nameplate")

        if use_nameplate:
            n1, n2 = st.columns(2, gap="large")
            with n1:
                Ip = st.number_input("Nameplate Primary FLA (A)", min_value=0.01, value=72.0, step=0.01, key="tp_Ip_nameplate")
            with n2:
                Is = st.number_input("Nameplate Secondary FLA (A)", min_value=0.01, value=208.0, step=0.01, key="tp_Is_nameplate")
        else:
            Ip = calc_fla(kva, vpri, phase)
            Is = calc_fla(kva, vsec, phase)

        m1, m2 = st.columns(2)
        m1.metric("Primary FLA", fmt(Ip, "A"))
        m2.metric("Secondary FLA", fmt(Is, "A"))

        st.divider()
        st.markdown("### Code-based OCPD limits")

        # ----------------------------
        # OESC calculator
        # ----------------------------
        if code_mode == "OESC":
            st.subheader("OESC — Rule-based sizing (implemented per the attached OESC calculation)")

            cc1, cc2, cc3 = st.columns([1.2, 1.2, 1.2], gap="large")
            with cc1:
                xfmr_type = st.selectbox("Transformer type", ["Oil-cooled (non-dry)", "Dry-type"], index=0, key="tp_oesc_type")
            with cc2:
                voltage_class = st.selectbox("Voltage class selection", ["> 750 V", "≤ 750 V"], index=1 if vpri <= 750 else 0, key="tp_oesc_vclass")
            with cc3:
                round_to_std = st.checkbox("Round up to standard rating (Table 13 style)", value=True, key="tp_oesc_round")

            rule_options = []
            if voltage_class == "> 750 V":
                rule_options = ["26-250 (>750V) — Primary fuses 150% / breakers 300% (direct primary protection)"]
            else:
                if xfmr_type == "Dry-type":
                    rule_options = [
                        "26-254 (≤750V dry-type) — Primary 125% (direct primary protection)",
                        "26-254 (≤750V dry-type) — Secondary device 125% + Primary feeder device 300% (no individual primary at transformer)",
                    ]
                else:
                    rule_options = [
                        "26-252 (≤750V non-dry) — Primary per 150% / 167% / 300% allowances (direct primary protection)",
                        "26-252 (≤750V non-dry) — Secondary device 125% + Primary feeder device 300% (no individual primary at transformer)",
                    ]

            rule_path = st.selectbox("OESC rule path", rule_options, index=0, key="tp_oesc_rule_path")
            std_list = OESC_TABLE13_STANDARD

            def show_oesc_result(label, raw):
                std = next_standard(raw, std_list) if round_to_std else None
                if round_to_std:
                    if std is None:
                        st.error(f"{label}: Raw = **{fmt(raw,'A')}** → exceeds standard list. Enter final device manually.")
                    else:
                        st.success(f"{label}: Raw = **{fmt(raw,'A')}** → Selected standard = **{fmt(std,'A')}**")
                else:
                    st.success(f"{label}: **{fmt(raw,'A')}**")

            if rule_path.startswith("26-250"):
                st.markdown("#### 26-250 (>750 V) — Direct primary protection (per calc document)")
                if Ip is None:
                    st.error("Primary FLA could not be computed. Check inputs.")
                else:
                    raw_fuse = 1.50 * Ip
                    raw_brk = 3.00 * Ip
                    show_oesc_result("Max Primary Fuse (150%)", raw_fuse)
                    show_oesc_result("Max Primary Breaker (300%)", raw_brk)

                    with st.expander("Optional: show secondary reference values (not a required selection in this direct-primary example)", expanded=False):
                        if Is is None:
                            st.warning("Secondary FLA unavailable.")
                        else:
                            st.info("The attached calculation worksheet also shows secondary-side reference values using the same multipliers.")
                            show_oesc_result("Secondary @ 150% (reference)", 1.50 * Is)
                            show_oesc_result("Secondary @ 300% (reference)", 3.00 * Is)

            elif rule_path.startswith("26-252") and "direct primary" in rule_path.lower():
                st.markdown("#### 26-252 (≤750 V, non-dry) — Direct primary protection (per calc document)")
                if Ip is None:
                    st.error("Primary FLA could not be computed. Check inputs.")
                else:
                    if Ip < 2.0:
                        mult = 3.00
                        reason = "Ip < 2 A — up to 300% permitted."
                    elif Ip < 9.0:
                        mult = 1.67
                        reason = "Ip < 9 A — up to 167% permitted."
                    else:
                        mult = 1.50
                        reason = "Ip ≥ 9 A — up to 150% permitted; if not a standard size, next higher standard permitted."

                    raw_primary = mult * Ip
                    st.caption(reason)
                    show_oesc_result(f"Max Primary OCPD ({mult:.2f}×)", raw_primary)

                    with st.expander("Optional: show secondary reference value from worksheet style", expanded=False):
                        if Is is None:
                            st.warning("Secondary FLA unavailable.")
                        else:
                            st.info("The attached worksheet also shows a secondary reference value using the same multiplier for this example format.")
                            show_oesc_result(f"Secondary @ {mult:.2f}× (reference)", mult * Is)

            elif rule_path.startswith("26-252") and "secondary device" in rule_path.lower():
                st.markdown("#### 26-252 (≤750 V, non-dry) — Secondary device + primary feeder allowance (per calc document)")
                if (Ip is None) or (Is is None):
                    st.error("Primary/Secondary FLA could not be computed. Check inputs.")
                else:
                    raw_sec_dev = 1.25 * Is
                    raw_pri_feeder = 3.00 * Ip
                    show_oesc_result("Max Secondary OCPD (125% of secondary FLA)", raw_sec_dev)
                    show_oesc_result("Max Primary Feeder OCPD (300% of primary FLA)", raw_pri_feeder)
                    st.caption(
                        "This path reflects the allowance summarized in the attached OESC calculation: "
                        "secondary-side device ≤125% and upstream primary feeder device ≤300% (verify rule conditions for your installation)."
                    )

            elif rule_path.startswith("26-254") and "direct primary" in rule_path.lower():
                st.markdown("#### 26-254 (≤750 V, dry-type) — Direct primary protection (per calc document)")
                if Ip is None:
                    st.error("Primary FLA could not be computed. Check inputs.")
                else:
                    raw_primary = 1.25 * Ip
                    show_oesc_result("Max Primary OCPD (125%)", raw_primary)

                    st.markdown("**Inrush withstand checks (Appendix guidance in calc):**")
                    st.write(f"12× FLA for 0.1 s: **{fmt(Ip * 12, 'A')}**")
                    st.write(f"25× FLA for 0.01 s: **{fmt(Ip * 25, 'A')}**")
                    st.caption("Verify manufacturer curves to confirm withstand/ride-through capability.")

                    with st.expander("Optional: show secondary reference value from worksheet style", expanded=False):
                        if Is is None:
                            st.warning("Secondary FLA unavailable.")
                        else:
                            show_oesc_result("Secondary @ 125% (reference)", 1.25 * Is)

            elif rule_path.startswith("26-254") and "secondary device" in rule_path.lower():
                st.markdown("#### 26-254 (≤750 V, dry-type) — Secondary device + primary feeder allowance (per calc document)")
                if (Ip is None) or (Is is None):
                    st.error("Primary/Secondary FLA could not be computed. Check inputs.")
                else:
                    raw_sec_dev = 1.25 * Is
                    raw_pri_feeder = 3.00 * Ip
                    show_oesc_result("Max Secondary OCPD (125% of secondary FLA)", raw_sec_dev)
                    show_oesc_result("Max Primary Feeder OCPD (300% of primary FLA)", raw_pri_feeder)

                    st.markdown("**Inrush withstand checks (Appendix guidance in calc):**")
                    st.write(f"12× FLA for 0.1 s: **{fmt(Ip * 12, 'A')}**")
                    st.write(f"25× FLA for 0.01 s: **{fmt(Ip * 25, 'A')}**")

                    st.caption(
                        "This path reflects the allowance summarized in the attached OESC calculation: "
                        "secondary-side device ≤125% and upstream primary feeder device ≤300% (verify rule conditions for your installation)."
                    )

            else:
                st.warning("Selected OESC path not recognized. Check selections.")

        # ----------------------------
        # NEC calculator
        # ----------------------------
        else:
            st.subheader("NEC — Table-based sizing (implemented per the attached NEC calculation)")

            nc1, nc2, nc3 = st.columns([1.1, 1.1, 1.1], gap="large")
            with nc1:
                nec_case = st.selectbox(
                    "NEC case",
                    [
                        "450.3(A) — Transformers >1000V (Z ≤ 6%, Any location) — multipliers per attached calc",
                        "450.3(B) — Transformers ≤1000V (currents ≥ 9A) — multipliers per attached calc",
                    ],
                    index=1 if vpri <= 1000 else 0,
                    key="tp_nec_case",
                )
            with nc2:
                round_to_std = st.checkbox("Round up to standard rating (NEC 240.6(A) list)", value=True, key="tp_nec_round")
            with nc3:
                show_notes = st.checkbox("Show table-note reminders (Note 1 / Note 2)", value=True, key="tp_nec_notes")

            std_list = NEC_2406A_STANDARD

            def show_nec_result(label, raw, over_1000v=False):
                std = next_standard(raw, std_list) if round_to_std else None
                if round_to_std:
                    if std is None:
                        st.error(f"{label}: Raw = **{fmt(raw,'A')}** → exceeds standard list. Enter final device manually.")
                    else:
                        st.success(f"{label}: Raw = **{fmt(raw,'A')}** → Selected = **{fmt(std,'A')}**")
                else:
                    st.success(f"{label}: **{fmt(raw,'A')}**")

                if over_1000v:
                    st.caption("For >1000 V cases, Table 450.3 Note 1 allows next higher **commercially available** rating/setting (not strictly the 240.6(A) list).")

            if show_notes:
                st.markdown(
                    """
**Table-note reminders (from the attached NEC calc narrative):**  
- **Note 1:** If the calculated rating/setting is not standard, the next higher is permitted (standard for ≤1000 V; commercially available for >1000 V).  
- **Note 2:** If secondary protection is required, up to **six** breakers or **six** fuse sets may be grouped; the **sum** of device ratings must not exceed the allowed single-device value.
"""
                )

            if nec_case.startswith("450.3(A)"):
                st.markdown("#### 450.3(A) (>1000 V) — Implemented multipliers (Z ≤ 6%, Any location) per attached calc")
                if (Ip is None) or (Is is None):
                    st.error("Primary/Secondary FLA could not be computed. Check inputs.")
                else:
                    raw_pri_brk = 6.00 * Ip
                    raw_pri_fuse = 3.00 * Ip
                    raw_sec_brk = 3.00 * Is
                    raw_sec_fuse = 2.50 * Is

                    show_nec_result("Max Primary Breaker (6.00×)", raw_pri_brk, over_1000v=True)
                    show_nec_result("Max Primary Fuse (3.00×)", raw_pri_fuse, over_1000v=True)
                    show_nec_result("Max Secondary Breaker (3.00×)", raw_sec_brk, over_1000v=True)
                    show_nec_result("Max Secondary Fuse (2.50×)", raw_sec_fuse, over_1000v=True)

                    st.caption(
                        "These multipliers match the attached NEC calculation example for a >1000 V transformer with impedance ≤ 6% in an 'any location' installation."
                    )

            else:
                st.markdown("#### 450.3(B) (≤1000 V) — Implemented multipliers (currents ≥ 9A) per attached calc")
                scheme = st.radio(
                    "Protection scheme",
                    ["Primary-only protection", "Primary + Secondary protection"],
                    horizontal=True,
                    key="tp_nec_4503b_scheme",
                )

                if (Ip is None) or (Is is None):
                    st.error("Primary/Secondary FLA could not be computed. Check inputs.")
                else:
                    if Ip < 9.0:
                        st.warning(
                            "The attached NEC worksheet implements the ≥9A case. Your primary FLA is < 9A. "
                            "Refer directly to NEC Table 450.3(B) for the correct small-current conditions."
                        )

                    if scheme == "Primary-only protection":
                        raw_primary = 1.25 * Ip
                        show_nec_result("Max Primary OCPD (1.25×)", raw_primary, over_1000v=False)
                        st.caption("This matches the attached NEC calculation 'Primary Only ≥9A Multiplier: 1.25'.")
                    else:
                        raw_primary = 2.50 * Ip
                        raw_secondary = 1.25 * Is
                        show_nec_result("Max Primary OCPD (2.50×)", raw_primary, over_1000v=False)
                        show_nec_result("Max Secondary OCPD (1.25×)", raw_secondary, over_1000v=False)
                        st.caption(
                            "These multipliers match the attached NEC calculation 'Primary + Secondary' scheme for ≤1000 V with currents ≥ 9A."
                        )

        st.divider()
        st.markdown("### Equations used")
        if phase == "3Φ":
            eq(r"I=\frac{S}{\sqrt{3}\,V}")
        else:
            eq(r"I=\frac{S}{V}")
        st.caption("Where S is in VA and V is in volts (or kVA with kV).")


# ============================
# 2) Transformer Feeders
# ============================
elif page == "Transformer Feeders":
    with theory_tab:
        header("Transformer Feeders — Theory")
        show_code_note(code_mode)
        if code_mode == "OESC":
            render_md_safe("transformer_feeders_oesc.md")
        else:
            render_md_safe("transformer_feeders_nec.md")

    with calc_tab:
        header("Transformer Feeder Calculator", "Compute primary/secondary FLA, turns ratio, and transformer type.")
        show_code_note(code_mode)

        st.markdown("### Inputs")
        row1 = st.columns([3, 1], gap="large")
        with row1[0]:
            phase = st.selectbox("Number of phases", ["Single-phase", "Three-phase"], index=0, key="tf_phase")
        with row1[1]:
            st.write("")

        row2 = st.columns([3, 1], gap="large")
        with row2[0]:
            rating_value = st.number_input("Transformer rating", min_value=0.1, value=15.0, step=0.1, key="tf_rating")
        with row2[1]:
            rating_unit = st.selectbox("Rating unit", ["kVA", "MVA", "VA"], index=0, key="tf_rating_unit")

        row3 = st.columns([3, 1], gap="large")
        with row3[0]:
            vpri_value = st.number_input(
                "Primary transformer voltage",
                min_value=1.0,
                value=480.0,
                step=1.0,
                key="tf_vpri",
            )
        with row3[1]:
            vpri_unit = st.selectbox("Unit", ["V", "kV", "MV"], index=0, key="tf_vpri_unit")

        row4 = st.columns([3, 1], gap="large")
        with row4[0]:
            vsec_value = st.number_input(
                "Secondary transformer voltage",
                min_value=1.0,
                value=120.0,
                step=1.0,
                key="tf_vsec",
            )
        with row4[1]:
            vsec_unit = st.selectbox("Unit", ["V", "kV", "MV"], index=0, key="tf_vsec_unit")

        st.caption("Use line-to-line voltage for three-phase transformers. Example: 15 kVA, 480 V to 120 V.")

        def _volts_from(value, unit):
            if unit == "MV":
                return value * 1_000_000.0
            if unit == "kV":
                return value * 1_000.0
            return value

        vpri = _volts_from(vpri_value, vpri_unit)
        vsec = _volts_from(vsec_value, vsec_unit)

        # Convert rating to VA
        if rating_unit == "MVA":
            s_va = rating_value * 1_000_000.0
        elif rating_unit == "kVA":
            s_va = rating_value * 1_000.0
        else:
            s_va = rating_value

        if phase == "Three-phase":
            I1 = s_va / (math.sqrt(3) * vpri) if vpri > 0 else None
            I2 = s_va / (math.sqrt(3) * vsec) if vsec > 0 else None
        else:
            I1 = s_va / vpri if vpri > 0 else None
            I2 = s_va / vsec if vsec > 0 else None

        turns_ratio = safe_div(vpri, vsec) if vpri and vsec else None
        if vpri > vsec:
            xform_dir = "Step-down"
        elif vpri < vsec:
            xform_dir = "Step-up"
        else:
            xform_dir = "Isolation (1:1)"
        xform_type = f"{phase} {xform_dir} Transformer"

        def _fmt_no_sci(x, unit=""):
            if x is None:
                return "—"
            try:
                v = float(x)
            except Exception:
                return str(x)
            s = f"{v:,.3f}".rstrip("0").rstrip(".")
            return f"{s} {unit}".strip()

        r1, r2, r3 = st.columns([1, 1, 1], gap="large")
        r1.metric("Primary Full-Load Current", _fmt_no_sci(I1, "A"))
        r2.metric("Secondary Full-Load Current", _fmt_no_sci(I2, "A"))
        r3.metric("Turns Ratio (V1/V2)", _fmt_no_sci(turns_ratio, ""))
        st.write(f"**Transformer Type:** {xform_type}")

        st.markdown("### Transformer formulas")
        if phase == "Three-phase":
            eq(r"I=\frac{S}{\sqrt{3}\,V}")
        else:
            eq(r"I=\frac{S}{V}")
        eq(r"\text{Turns Ratio}=\frac{V_1}{V_2}=\frac{N_1}{N_2}=\frac{I_2}{I_1}")


# ============================
# 3) Grounding/Bonding Conductor Sizing
# ============================
elif page == "Grounding/Bonding Conductor Sizing":
    with theory_tab:
        header("Grounding & Bonding — Theory")
        show_code_note(code_mode)
        if code_mode == "OESC":
            render_md_safe("grounding_bonding_oesc.md")
        else:
            render_md_safe("grounding_bonding_nec.md")

    with calc_tab:
        header("Grounding/Bonding Helper", "Simple placeholder — replace with real NEC/OESC table logic.")
        show_code_note(code_mode)

        ocpd = st.number_input("Upstream OCPD rating (A)", min_value=1.0, value=200.0, step=1.0)

        if ocpd <= 60:
            egc = "10 AWG Cu (placeholder)"
        elif ocpd <= 100:
            egc = "8 AWG Cu (placeholder)"
        elif ocpd <= 200:
            egc = "6 AWG Cu (placeholder)"
        elif ocpd <= 400:
            egc = "3 AWG Cu (placeholder)"
        else:
            egc = "See table / engineer (placeholder)"

        st.success(f"Equipment grounding conductor (example placeholder): **{egc}**")
        st.markdown("### Equation used")
        eq(r"\text{EGC size} = f(\text{OCPD rating})")


# ============================
# 4) Motor Protection
# ============================
elif page == "Motor Protection":
    with theory_tab:
        header("Motor Protection — Theory")
        show_code_note(code_mode)
        if code_mode == "OESC":
            render_md_safe("motor_protection_oesc.md")
        else:
            render_md_safe("motor_protection_nec.md")

    with calc_tab:
        header("Motor Protection Calculator", "Estimate overload and short-circuit device settings.")
        show_code_note(code_mode)

        fla = st.number_input("Motor full-load amps (FLA)", min_value=0.1, value=28.0, step=0.1)
        ol_mult = st.selectbox("Overload multiplier (k)", ["1.15", "1.25"], index=1)
        sc_mult = st.selectbox("Short-circuit multiplier (m)", ["1.75", "2.50"], index=0)

        ol = fla * float(ol_mult)
        sc = fla * float(sc_mult)

        c1, c2 = st.columns(2)
        c1.metric("Overload setting (A)", fmt(ol, "A"))
        c2.metric("Short-circuit device (A)", fmt(sc, "A"))

        st.markdown("### Equations used")
        eq(r"I_{OL}=k\cdot I_{FLA}")
        eq(r"I_{SC}=m\cdot I_{FLA}")


# ============================
# 5) Motor Feeder
# ============================
elif page == "Motor Feeder":
    with theory_tab:
        header("Motor Feeder — Theory")
        show_code_note(code_mode)
        if code_mode == "OESC":
            render_md_safe("motor_feeder_oesc.md")
        else:
            render_md_safe("motor_feeder_nec.md")

    with calc_tab:
        header("Motor Feeder Calculator", "Estimate motor I_FLA from nameplate data, then apply feeder factor.")
        show_code_note(code_mode)

        c1, c2, c3, c4 = st.columns(4, gap="large")
        with c1:
            phase = st.selectbox("System", ["3-phase", "1-phase", "DC motor"], index=0, key="mf_phase")
        with c2:
            hp = st.number_input("Motor power (HP)", min_value=0.1, value=25.0, step=0.1, key="mf_hp")
        with c3:
            volts = st.number_input(
                "Voltage (V)",
                min_value=1.0,
                value=600.0,
                step=1.0,
                help="Use line-to-line voltage for 3-phase motors.",
                key="mf_volts",
            )
        with c4:
            if phase == "DC motor":
                pf = 1.0
                st.text_input("Power factor (cosθ)", value="N/A (DC)", disabled=True, key="mf_pf_dc")
            else:
                pf = st.number_input(
                    "Power factor (cosθ)",
                    min_value=0.10,
                    max_value=1.00,
                    value=0.90,
                    step=0.01,
                    key="mf_pf",
                )

        eff = st.number_input(
            "Efficiency (%)",
            min_value=1.0,
            max_value=100.0,
            value=92.0,
            step=0.1,
            key="mf_eff",
        )

        if phase == "DC motor":
            denom = volts * (eff / 100.0)
        else:
            denom = (math.sqrt(3) if phase == "3-phase" else 1.0) * volts * pf * (eff / 100.0)
        ifla = (hp * 745.7) / denom if denom > 0 else None

        sizing_mult = st.selectbox(
            "Conductor sizing factor",
            ["1.00", "1.15", "1.25"],
            index=2,
            key="mf_mult",
        )
        target = ifla * float(sizing_mult) if ifla is not None else None

        c1, c2 = st.columns(2)
        c1.metric("Calculated I_FLA (A)", fmt(ifla, "A"))
        c2.metric("Conductor ampacity target (A)", fmt(target, "A"))

        st.markdown("### Equation used")
        if phase == "3-phase":
            eq(r"I_{FLA}=\frac{HP\cdot 745.7}{\sqrt{3}\cdot V_{LL}\cdot \cos\theta\cdot \eta}")
        elif phase == "1-phase":
            eq(r"I_{FLA}=\frac{HP\cdot 745.7}{V\cdot \cos\theta\cdot \eta}")
        else:
            eq(r"I_{FLA}=\frac{HP\cdot 745.7}{V\cdot \eta}")
        eq(r"I_{target}=k\cdot I_{FLA}")


# ============================
# 6) Cable Tray Size & Fill & Bend Radius
# ============================
elif page == "Cable Tray Size & Fill & Bend Radius":
    with theory_tab:
        header("Cable Tray Size, Fill & Bend Radius — Theory")
        show_code_note(code_mode)
        if code_mode == "OESC":
            render_md_safe("cable_tray_fill_oesc.md")
        else:
            render_md_safe("cable_tray_fill_nec.md")

    with calc_tab:
        header("Tray Fill & Bend Radius Calculator", "Estimate cable area + bend radius.")
        show_code_note(code_mode)

        col1, col2, col3 = st.columns(3, gap="large")
        with col1:
            n = st.number_input("Number of cables", min_value=1, value=20, step=1)
        with col2:
            od_mm = st.number_input("Cable OD (mm)", min_value=1.0, value=20.0, step=0.5)
        with col3:
            br_mult = st.selectbox("Bend radius multiplier (k)", ["8", "12", "16"], index=1)

        cable_area_mm2 = n * math.pi * (od_mm / 2.0) ** 2
        bend_radius_mm = float(br_mult) * od_mm

        st.metric("Estimated total cable area", fmt(cable_area_mm2, "mm²"))
        st.success(f"Suggested bend radius (rule-of-thumb): **{fmt(bend_radius_mm, 'mm')}**")

        st.markdown("### Equations used")
        eq(r"A_{cables}\approx n\cdot \pi\left(\frac{d}{2}\right)^2")
        eq(r"R_{min}=k\cdot d")


# ============================
# 7) Conduit Size & Fill & Bend Radius
# ============================
elif page == "Conduit Size & Fill & Bend Radius":
    with theory_tab:
        header("Conduit Size, Fill & Bend Radius — Theory")
        show_code_note(code_mode)
        if code_mode == "OESC":
            render_md_safe("conduit_fill_oesc.md")
        else:
            render_md_safe("conduit_fill_nec.md")

    with calc_tab:
        header("Conduit Fill Calculator — OESC Table 6 + Table 9 (dynamic cables)", "Select a conduit, add any number of cable groups, and the app computes conduit fill.")
        show_code_note(code_mode)

        st.markdown(
            "This tool is designed to behave like common conduit-fill calculators:\n"
            "- Pick a **conduit type** and **trade size** (Table 9)\n"
            "- Add one or more **cable groups** (Table 6)\n"
            "- The calculator totals cable areas and compares against **Table 9 allowable fill**\n\n"
            "If the embedded OESC Table Library is unavailable in your deployment, a **manual fallback** is provided."
        )

        # ----------------------------
        # Table helpers (Table 6 + Table 9)
        # ----------------------------
        def _norm(s):
            return str(s).strip()

        def _lower(s):
            return _norm(s).lower()

        def _to_float(x):
            try:
                if x is None:
                    return None
                if isinstance(x, (int, float)):
                    return float(x)
                s = str(x).strip()
                if s in ("", "—", "-", "–", "None"):
                    return None
                # remove commas
                s = s.replace(",", "")
                return float(s)
            except Exception:
                return None

        def _best_col(cols, include=(), exclude=()):
            """Return first column name that contains ALL include tokens and NONE of exclude tokens (case-insensitive)."""
            for c in cols:
                lc = _lower(c)
                ok = True
                for t in include:
                    if t not in lc:
                        ok = False
                        break
                if not ok:
                    continue
                for t in exclude:
                    if t in lc:
                        ok = False
                        break
                if ok:
                    return c
            return None

        @st.cache_data(show_spinner=False)
        def _load_table_df(table_id: str):
            if oesc_tables is None:
                return None
            try:
                return oesc_tables.get_table_dataframe(table_id)
            except Exception:
                return None

        def _table6_to_maps(df):
            """
            Convert Table 6 into:
              - types: list[str]
              - sizes_by_type: dict[type -> list[size]]
              - area_lookup: dict[type -> dict[size -> area_mm2]]
            Works with both "wide" and "long" table layouts.
            """
            if df is None:
                return [], {}, {}

            # Normalize to DataFrame if possible
            if pd is not None and not isinstance(df, pd.DataFrame):
                try:
                    df = pd.DataFrame(df)
                except Exception:
                    return [], {}, {}

            if pd is None or not hasattr(df, "columns"):
                return [], {}, {}

            cols = list(df.columns)

            # Guess a "size" column
            size_col = _best_col(cols, include=("size",)) or cols[0]

            # LONG format candidates: has columns like Type/Insulation, Size, Area
            type_col = _best_col(cols, include=("type",)) or _best_col(cols, include=("cable",)) or _best_col(cols, include=("insul",))
            area_col = _best_col(cols, include=("area",)) or _best_col(cols, include=("mm",)) or _best_col(cols, include=("mm2",)) or _best_col(cols, include=("mm²",))

            # If we can confidently interpret as long format, do it
            if type_col and area_col:
                area_lookup = {}
                for _, r in df.iterrows():
                    t = _norm(r.get(type_col, ""))
                    s = _norm(r.get(size_col, ""))
                    a = _to_float(r.get(area_col, None))
                    if not t or not s or a is None:
                        continue
                    area_lookup.setdefault(t, {})[s] = a
                types = sorted(area_lookup.keys())
                sizes_by_type = {t: list(area_lookup[t].keys()) for t in types}
                # Keep a stable (human-ish) order if possible
                for t in types:
                    sizes_by_type[t] = sorted(sizes_by_type[t], key=lambda x: (len(x), x))
                return types, sizes_by_type, area_lookup

            # Otherwise, treat as WIDE:
            # - First column is size, other columns are cable types holding areas
            other_cols = [c for c in cols if c != size_col]
            area_lookup = {}
            for c in other_cols:
                t = _norm(c)
                for _, r in df.iterrows():
                    s = _norm(r.get(size_col, ""))
                    a = _to_float(r.get(c, None))
                    if not s or a is None:
                        continue
                    area_lookup.setdefault(t, {})[s] = a
            types = [t for t in other_cols if t in area_lookup]
            sizes_by_type = {t: list(area_lookup[t].keys()) for t in types}
            for t in types:
                sizes_by_type[t] = sorted(sizes_by_type[t], key=lambda x: (len(x), x))
            return types, sizes_by_type, area_lookup

        def _table9_to_index(df):
            """
            Convert Table 9 into a normalized index:
              rows[(conduit_type, trade_size)] = dict of the original row values
            Attempts to find the conduit type and size columns.
            """
            if df is None:
                return None, None, {}

            if pd is not None and not isinstance(df, pd.DataFrame):
                try:
                    df = pd.DataFrame(df)
                except Exception:
                    return None, None, {}

            cols = list(df.columns) if hasattr(df, "columns") else []
            if not cols:
                return None, None, {}

            type_col = (
                _best_col(cols, include=("type",), exclude=("cable",))
                or _best_col(cols, include=("conduit",), exclude=("area", "id", "internal"))
                or cols[0]
            )
            size_col = (
                _best_col(cols, include=("trade", "size"))
                or _best_col(cols, include=("size",), exclude=("internal", "area", "mm"))
                or (cols[1] if len(cols) > 1 else cols[0])
            )

            idx = {}
            try:
                for _, r in df.iterrows():
                    t = _norm(r.get(type_col, ""))
                    s = _norm(r.get(size_col, ""))
                    if not t or not s:
                        continue
                    idx[(t, s)] = {c: r.get(c, None) for c in cols}
            except Exception:
                pass

            return type_col, size_col, idx

        def _infer_internal_area(row_dict):
            """Try to find an internal area field (mm²)."""
            cols = list(row_dict.keys())
            # Strong signals first
            c = _best_col(cols, include=("internal", "area")) or _best_col(cols, include=("area",), exclude=("allow", "max", "fill", "cable", "cond"))
            if c:
                return _to_float(row_dict.get(c))
            # Next: any numeric-looking column with 'mm' and '2'
            for cc in cols:
                lc = _lower(cc)
                if ("mm" in lc and ("2" in lc or "²" in lc)) and ("allow" not in lc and "fill" not in lc and "max" not in lc):
                    v = _to_float(row_dict.get(cc))
                    if v:
                        return v
            return None

        def _infer_allowed_area_and_pct(row_dict, n_cables_total, internal_area):
            """
            Try to infer allowed area and allowed percent from Table 9 row.
            Returns (allowed_area_mm2, allowed_pct_fraction, source_label)
            """
            cols = list(row_dict.keys())

            # Candidate columns by count bucket
            if n_cables_total <= 1:
                tokens = ("1",)
            elif n_cables_total == 2:
                tokens = ("2",)
            else:
                tokens = ("3",)  # could be "3+", "3 or more"
            # Area-first lookup
            area_candidates = []
            for c in cols:
                lc = _lower(c)
                if all(t in lc for t in tokens) and ("area" in lc or "mm" in lc or "mm2" in lc or "mm²" in lc) and ("%" not in lc):
                    area_candidates.append(c)
            # Also accept "3+" written forms
            if n_cables_total >= 3:
                for c in cols:
                    lc = _lower(c)
                    if (("3+" in lc) or ("3 or" in lc) or ("3 or more" in lc) or ("more" in lc)) and ("area" in lc or "mm" in lc) and ("%" not in lc):
                        if c not in area_candidates:
                            area_candidates.append(c)

            for c in area_candidates:
                a = _to_float(row_dict.get(c))
                if a is not None:
                    pct = (a / internal_area) if (a is not None and internal_area) else None
                    return a, pct, f"Table 9 column: {c}"

            # Percent columns (if table stores % directly)
            pct_candidates = []
            for c in cols:
                lc = _lower(c)
                if all(t in lc for t in tokens) and ("%" in lc or "percent" in lc or "fill" in lc or "max" in lc):
                    pct_candidates.append(c)
            if n_cables_total >= 3:
                for c in cols:
                    lc = _lower(c)
                    if (("3+" in lc) or ("3 or" in lc) or ("more" in lc)) and ("%" in lc or "percent" in lc or "fill" in lc or "max" in lc):
                        if c not in pct_candidates:
                            pct_candidates.append(c)

            for c in pct_candidates:
                p = _to_float(row_dict.get(c))
                if p is None:
                    continue
                # If stored like 40 (meaning %), convert to fraction
                pct_fraction = p / 100.0 if p > 1.0 else p
                a = internal_area * pct_fraction if internal_area else None
                return a, pct_fraction, f"Table 9 column: {c}"

            # Fallback: standard conduit-fill rules (common convention)
            if internal_area:
                if n_cables_total <= 1:
                    pct_fraction = 0.53
                elif n_cables_total == 2:
                    pct_fraction = 0.31
                else:
                    pct_fraction = 0.40
                return internal_area * pct_fraction, pct_fraction, "Fallback: 53%/31%/40% rule (no Table 9 match found)"

            return None, None, "No allowable fill available"

        def _try_int(x):
            try:
                return int(str(x).strip())
            except Exception:
                return None

        def _get_conduit_type_options():
            """
            Prefer the embedded Table 9 helpers in lib.oesc_tables when available.
            Returns (display_names, display_to_key) or (None, {}) when unavailable.
            """
            if oesc_tables is None:
                return None, {}
            if not hasattr(oesc_tables, "CONDUIT_TYPE_LABELS"):
                return None, {}
            labels = list(oesc_tables.CONDUIT_TYPE_LABELS.keys())
            return labels, dict(oesc_tables.CONDUIT_TYPE_LABELS)

        def _get_trade_sizes_for_type(conduit_key: str):
            if oesc_tables is None:
                return []
            if not hasattr(oesc_tables, "TABLE_9A_TYPES") or not hasattr(oesc_tables, "TABLE_9B_TYPES"):
                return []
            if conduit_key in oesc_tables.TABLE_9A_TYPES:
                table = getattr(oesc_tables, "TABLE_9A", {})
            else:
                table = getattr(oesc_tables, "TABLE_9B", {})
            return _numeric_sort([str(k) for k in (table.keys() if isinstance(table, dict) else [])])

        def _get_conduit_entry(conduit_key: str, trade_size):
            if oesc_tables is None or not hasattr(oesc_tables, "get_conduit_9a9b"):
                return None
            ts = _try_int(trade_size)
            if ts is None:
                return None
            return oesc_tables.get_conduit_9a9b(conduit_key, ts)

        # ----------------------------
        # Load tables (best effort)
        # ----------------------------
        t6_df = None
        t9_df = None
        if _TABLES_IMPORT_ERROR:
            st.warning(f"Embedded table library unavailable: `{_TABLES_IMPORT_ERROR}`")
        else:
            # Table IDs are typically "6" and "9" in the library; if your library uses variants like "6A"/"9H",
            # the manual fallback below still works and you can adjust IDs in lib/oesc_tables.py later.
            t6_df = _load_table_df("6")
            t9_df = _load_table_df("9")

        t6_types, t6_sizes_by_type, t6_area = _table6_to_maps(t6_df)
        t9_type_col, t9_size_col, t9_index = _table9_to_index(t9_df)

        # Shared palette for cable group coloring (matches conduit diagram)
        CF_PALETTE = ["#5B8FF9", "#61DDAA", "#F6BD16", "#E8684A", "#9270CA", "#6DC8EC", "#FF9D4D"]

        def _area_to_radius(area_mm2):
            try:
                a = float(area_mm2)
            except Exception:
                return None
            return math.sqrt(a / math.pi) if a > 0 else None

        def _pack_circles_in_circle(n, r, R):
            """Pack n equal circles of radius r inside radius R using tangent candidates."""
            if not n or not r or not R or r <= 0 or R <= 0:
                return []
            if r > R:
                return []
            if n == 1:
                return [(0.0, 0.0)]

            placed = []
            spacing_options = [0.2, 0.0]
            angles = [i * (math.pi / 18.0) for i in range(36)]

            def fits(x, y, rr, spacing):
                if math.hypot(x, y) + rr > R:
                    return False
                for ox, oy in placed:
                    dx = x - ox
                    dy = y - oy
                    if (dx * dx + dy * dy) < (2 * rr + spacing) ** 2:
                        return False
                return True

            def circle_intersections(x0, y0, r0, x1, y1, r1):
                dx = x1 - x0
                dy = y1 - y0
                d = math.hypot(dx, dy)
                if d == 0 or d > (r0 + r1) or d < abs(r0 - r1):
                    return []
                a = (r0 * r0 - r1 * r1 + d * d) / (2 * d)
                h_sq = r0 * r0 - a * a
                if h_sq < 0:
                    return []
                h = math.sqrt(h_sq)
                xm = x0 + a * dx / d
                ym = y0 + a * dy / d
                rx = -dy * (h / d)
                ry = dx * (h / d)
                return [(xm + rx, ym + ry), (xm - rx, ym - ry)]

            placed.append((0.0, 0.0))
            while len(placed) < n:
                placed_flag = False
                for spacing in spacing_options:
                    best = None
                    best_score = None
                    candidates = []

                    for (ox, oy) in placed:
                        base_dist = 2 * r + spacing
                        for a in angles:
                            candidates.append((ox + base_dist * math.cos(a), oy + base_dist * math.sin(a)))

                    for i in range(len(placed)):
                        for j in range(i + 1, len(placed)):
                            (x1, y1) = placed[i]
                            (x2, y2) = placed[j]
                            d1 = 2 * r + spacing
                            d2 = 2 * r + spacing
                            candidates.extend(circle_intersections(x1, y1, d1, x2, y2, d2))

                    for (x, y) in candidates:
                        if not fits(x, y, r, spacing):
                            continue
                        score = x * x + y * y
                        if best_score is None or score < best_score:
                            best_score = score
                            best = (x, y)

                    if best is None:
                        # ring fallback
                        for ring in range(1, 12):
                            ring_r = ring * (r * 1.1)
                            if ring_r + r > R:
                                break
                            for a in angles:
                                x = ring_r * math.cos(a)
                                y = ring_r * math.sin(a)
                                if fits(x, y, r, spacing):
                                    score = x * x + y * y
                                    if best_score is None or score < best_score:
                                        best_score = score
                                        best = (x, y)
                            if best is not None:
                                break

                    if best is not None:
                        placed.append(best)
                        placed_flag = True
                        break

                if not placed_flag:
                    break

            return placed

        def _build_cable_group_swatch_svg(area_per_cable, n_cond, area_per_conductor, group_idx):
            """Render a small SVG swatch showing this cable group's color and conductor layout."""
            r_cable = _area_to_radius(area_per_cable)
            if r_cable is None or r_cable <= 0:
                return None

            r_cond = _area_to_radius(area_per_conductor) if area_per_conductor else None

            canvas = 90
            margin = 6
            scale = (canvas - 2 * margin) / (2 * r_cable)
            cx = canvas / 2
            cy = canvas / 2

            def to_px(val_mm):
                return val_mm * scale

            color = CF_PALETTE[group_idx % len(CF_PALETTE)]

            svg_parts = []
            svg_parts.append(
                f'<svg width="{canvas}" height="{canvas}" viewBox="0 0 {canvas} {canvas}" '
                f'xmlns="http://www.w3.org/2000/svg">'
            )
            svg_parts.append(
                f'<circle cx="{cx}" cy="{cy}" r="{to_px(r_cable):.2f}" '
                f'stroke="#333" stroke-width="1" fill="{color}" fill-opacity="0.55"/>'
            )

            if n_cond:
                inner_margin = 0.6
                R_inner = r_cable - inner_margin
                if R_inner > 0:
                    if r_cond is None or r_cond <= 0:
                        r_cond_use = R_inner / max(1.6 * math.sqrt(int(n_cond)), 1.6)
                    else:
                        r_cond_use = min(r_cond, R_inner)

                    conductor_positions = []
                    for _ in range(15):
                        conductor_positions = _pack_circles_in_circle(int(n_cond), r_cond_use, R_inner)
                        if len(conductor_positions) >= int(n_cond):
                            break
                        r_cond_use *= 0.9

                    for (dx, dy) in conductor_positions[: int(n_cond)]:
                        svg_parts.append(
                            f'<circle cx="{cx + to_px(dx):.2f}" cy="{cy + to_px(dy):.2f}" '
                            f'r="{to_px(r_cond_use):.2f}" stroke="#111" stroke-width="0.6" '
                            f'fill="#000000"/>'
                        )

            svg_parts.append("</svg>")
            return "".join(svg_parts)

        # ----------------------------
        # Conduit selection (Table 9 or manual fallback)
        # ----------------------------
        st.markdown("## 1) Conduit selection (Table 9)")

        use_manual_conduit = st.checkbox(
            "Use manual conduit data (if Table 9 is missing or you want to override it)",
            value=False if t9_index else True,
            key="cf_use_manual_conduit",
        )

        conduit_internal_area = None
        conduit_allowed_area = None
        conduit_allowed_pct = None
        conduit_type_key = None
        allowed_source = "—"

        if use_manual_conduit:
            c1, c2, c3 = st.columns([1, 1, 1], gap="large")
            with c1:
                conduit_type = st.text_input("Conduit type (label)", value="(Manual)", key="cf_manual_type")
            with c2:
                conduit_trade = st.text_input("Trade size (label)", value="(Manual)", key="cf_manual_size")
            with c3:
                conduit_internal_area = st.number_input("Conduit internal area (mm²)", min_value=0.01, value=500.0, step=10.0, key="cf_manual_area")

            st.caption("Manual mode: allowable fill uses 53%/31%/40% convention (unless you override below).")
            n_cables_dummy = st.number_input("Cables in raceway (for allowable fill selection)", min_value=1, value=3, step=1, key="cf_manual_n_cables")
            conduit_allowed_area, conduit_allowed_pct, allowed_source = _infer_allowed_area_and_pct(
                {}, int(n_cables_dummy), conduit_internal_area
            )
        else:
            # Prefer using the embedded Table 9 helpers in lib/oesc_tables.py.
            conduit_display_names, display_to_key = _get_conduit_type_options()
            if conduit_display_names:
                c1, c2 = st.columns([1, 1], gap="large")
                with c1:
                    conduit_choice_display = st.selectbox("Conduit type", conduit_display_names, index=0, key="cf_conduit_type")
                conduit_type_key = display_to_key.get(conduit_choice_display)
                sizes_for_type = _get_trade_sizes_for_type(conduit_type_key) if conduit_type_key else []
                if not sizes_for_type:
                    st.error("Table 9 could not be loaded/parsed. Enable manual conduit mode above.")
                    conduit_type = "(Unknown)"
                    conduit_trade = "(Unknown)"
                else:
                    with c2:
                        conduit_trade = st.selectbox("Conduit trade size", sizes_for_type, index=0, key="cf_conduit_size")
                    conduit_type = conduit_choice_display
                    entry = _get_conduit_entry(conduit_type_key, conduit_trade)
                    conduit_internal_area = _to_float(entry.get("area_mm2") if entry else None)
                    if conduit_internal_area is None:
                        st.warning("Could not infer internal area from Table 9 row — using manual entry for internal area.")
                        conduit_internal_area = st.number_input("Conduit internal area override (mm²)", min_value=0.01, value=500.0, step=10.0, key="cf_area_override")
            else:
                # Fallback to parsing the combined Table 9 dataframe if helpers are unavailable.
                # ======= OESC Table 9 column -> OESC trimmed header mapping =======
                OESC_COLUMN_TO_HEADER = {
                    "Rigid Metal": "Rigid metal conduit",
                    "Flexible Metal": "Flexible metal conduit",
                    "Rigid Pvc": "Rigid PVC conduit",
                    "Rigid Pvc Db2 Es2": "Rigid Type EB1/DB2/ES2 PVC conduit",
                    "Metallic Liquid Tight Flex": "metallic liquid-tight flexible conduit",
                    "Nonmetallic Liquid Tight Flex": "non-metallic liquid-tight flexible conduit",
                    "Emt": "electrical metallic tubing",
                    "Ent": "electrical non-metallic tubing",
                    "Rtrc Ips": "rigid RTRC conduit marked IPS",
                    "Rtrc Id": "rigid RTRC conduit marked ID",
                    "Hdpe Sch40": "HDPE conduit Schedule 40",
                    "Hdpe Sch80": "HDPE conduit Schedule 80",
                    "Hdpe Dr9": "HDPE DR9 conduit",
                    "Hdpe Dr11": "HDPE DR11 conduit",
                    "Hdpe Dr13 5": "HDPE DR13.5 conduit",
                    "Hdpe Dr15 5": "HDPE DR15.5 conduit",
                }

                if t9_df is not None and hasattr(t9_df, "columns") and len(t9_df.columns) > 0:
                    available_cols = list(t9_df.columns)
                    base_tokens = []
                    for col in available_cols:
                        token = re.sub(r"\s+ID\s*\(mm\)$", "", col)
                        token = re.sub(r"\s+Area\s*\(mm²\)$", "", token)
                        token = token.strip()
                        base_tokens.append(token)

                    seen = set()
                    base_order = []
                    for b in base_tokens:
                        if b not in seen:
                            seen.add(b)
                            base_order.append(b)

                    filtered_base_order = [x for x in base_order if not re.search(r"subtable|trade\s*size", x, flags=re.IGNORECASE)]

                    conduit_display_names = []
                    display_to_colbase = {}
                    for base in filtered_base_order:
                        display = OESC_COLUMN_TO_HEADER.get(base, base)
                        conduit_display_names.append(display)
                        display_to_colbase[display] = base
                else:
                    conduit_display_names = None
                    display_to_colbase = {}
                conduit_types = sorted({k[0] for k in t9_index.keys()}) if t9_index else []
                if not conduit_types:
                    st.error("Table 9 could not be loaded/parsed. Enable manual conduit mode above.")
                    conduit_type = "(Unknown)"
                    conduit_trade = "(Unknown)"
                else:
                    c1, c2 = st.columns([1, 1], gap="large")
                    with c1:
                        if conduit_display_names:
                            conduit_choice_display = st.selectbox("Conduit type", conduit_display_names, index=0, key="cf_conduit_type")
                            chosen_base = display_to_colbase.get(conduit_choice_display)
                            conduit_type = chosen_base if chosen_base else conduit_choice_display
                        else:
                            conduit_type = st.selectbox("Conduit type", conduit_types, index=0, key="cf_conduit_type")
                            chosen_base = None
                    sizes_for_type = []
                    try:
                        if t9_df is not None and hasattr(t9_df, 'columns') and 't9_size_col' in globals() and t9_size_col:
                            if chosen_base:
                                possible_area = f"{chosen_base} Area (mm²)"
                                chosen_area_col_local = possible_area if possible_area in t9_df.columns else None
                                if chosen_area_col_local:
                                    sizes_for_type = _numeric_sort([str(x) for x in pd.Series(t9_df.loc[t9_df[chosen_area_col_local].notna(), t9_size_col]).dropna().astype(str).unique()])
                        if not sizes_for_type:
                            key_token = chosen_base if chosen_base else conduit_type
                            sizes_for_type = _numeric_sort({k[1] for k in t9_index.keys() if key_token and key_token in k[0]})
                            if not sizes_for_type:
                                sizes_for_type = _numeric_sort({k[1] for k in t9_index.keys() if k[0] == conduit_type})
                    except Exception:
                        sizes_for_type = _numeric_sort({k[1] for k in t9_index.keys() if k[0] == conduit_type})
                    with c2:
                        conduit_trade = st.selectbox("Conduit trade size", sizes_for_type, index=0, key="cf_conduit_size")

                    row = {}
                    if t9_df is not None and hasattr(t9_df, 'columns') and 't9_size_col' in globals() and t9_size_col:
                        try:
                            mask = t9_df[t9_size_col].astype(str).str.strip() == str(conduit_trade).strip()
                            df_rows = t9_df.loc[mask]
                            if not df_rows.empty:
                                sel = df_rows.iloc[0]
                                row = {c: sel.get(c, None) for c in list(t9_df.columns)}
                        except Exception:
                            row = {}
                    if not row:
                        row = t9_index.get((conduit_type, conduit_trade), {})

                    conduit_internal_area = _infer_internal_area(row)

                    if conduit_internal_area is None:
                        st.warning("Could not infer internal area from Table 9 row — using manual entry for internal area.")
                        conduit_internal_area = st.number_input("Conduit internal area override (mm²)", min_value=0.01, value=500.0, step=10.0, key="cf_area_override")

        # ----------------------------
        # Cable groups (Table 6)
        # ----------------------------
        st.markdown("## 2) Cable groups (Table 6)")

        if pd is None:
            st.error("pandas is required for the dynamic cable table UI. Please add pandas to your environment.")
            st.stop()

        # Build cable table mapping with Table 6A-K structure
        # Maps: table_key -> (title, table_data_dict)
        cable_tables = {
            "6A": ("Table 6A — 600V unjacketed (R90XLPE, RW75XLPE, RW90XLPE, RPV90)", oesc_tables.TABLE_6A if hasattr(oesc_tables, 'TABLE_6A') else None),
            "6B": ("Table 6B — 1000V unjacketed (R90XLPE, RW75XLPE, RW90XLPE, RPV90)", oesc_tables.TABLE_6B if hasattr(oesc_tables, 'TABLE_6B') else None),
            "6C": ("Table 6C — 600V jacketed (R90XLPE, RW75XLPE, R90EP, RW75EP, RW90XLPE, RW90EP, RPV90)", oesc_tables.TABLE_6C if hasattr(oesc_tables, 'TABLE_6C') else None),
            "6D": ("Table 6D — 1000V cables (TWU, TWU75, RWU90XLPE, RPVU90)", oesc_tables.TABLE_6D if hasattr(oesc_tables, 'TABLE_6D') else None),
            "6E": ("Table 6E — 1000V/2000V cables (RPVU90 unjacketed)", oesc_tables.TABLE_6E if hasattr(oesc_tables, 'TABLE_6E') else None),
            "6F": ("Table 6F — 1000V/2000V cables (RPVU90 jacketed)", oesc_tables.TABLE_6F if hasattr(oesc_tables, 'TABLE_6F') else None),
            "6G": ("Table 6G — 2000V unjacketed (RPV90)", oesc_tables.TABLE_6G if hasattr(oesc_tables, 'TABLE_6G') else None),
            "6H": ("Table 6H — 1000V jacketed (RPV90)", oesc_tables.TABLE_6H if hasattr(oesc_tables, 'TABLE_6H') else None),
            "6I": ("Table 6I — 2000V jacketed (RPV90)", oesc_tables.TABLE_6I if hasattr(oesc_tables, 'TABLE_6I') else None),
            "6J": ("Table 6J — TW, TW75 insulated conductors", oesc_tables.TABLE_6J if hasattr(oesc_tables, 'TABLE_6J') else None),
            "6K": ("Table 6K — TWN75, T90 NYLON insulated conductors", oesc_tables.TABLE_6K if hasattr(oesc_tables, 'TABLE_6K') else None),
        }
        # Filter to only tables with data
        cable_tables = {k: v for k, v in cable_tables.items() if v[1] is not None}

        # Base row template
        if not cable_tables:
            st.warning("Table 6 could not be loaded/parsed. You can still proceed by entering cable area manually per cable.")
            default_rows = [
                {"Cable description": "(Manual)", "Conductors per cable": 3, "Qty (cables)": 1, "Area per cable (mm²)": 150.0},
            ]
        else:
            # Initialize with first table, first construction type, first size
            first_table_key = list(cable_tables.keys())[0]
            first_table = cable_tables[first_table_key][1]
            first_construction = list(first_table.keys())[0] if first_table else "stranded"
            first_size = list(first_table.get(first_construction, {}).keys())[0] if first_table else ""
            default_rows = [
                {
                    "Name": "",
                    "Table": first_table_key,
                    "Construction": first_construction,
                    "Conductor size": first_size,
                    "Conductors per cable": 1,
                    "Qty (cables)": 1,
                    "Use custom conductors": False,
                    "Custom conductors": None,
                    "Custom area per cable": None
                },
            ]

        if "cf_cable_df" not in st.session_state:
            st.session_state["cf_cable_df"] = pd.DataFrame(default_rows)
        
        # Ensure each row has a unique ID for reliable deletion
        df_in = st.session_state["cf_cable_df"].copy()
        if "_row_id" not in df_in.columns:
            df_in["_row_id"] = range(len(df_in))
            st.session_state["cf_cable_df"]["_row_id"] = df_in["_row_id"]
        
        # Make sure all rows have IDs (in case of dataframe operations)
        if "_row_id" not in st.session_state["cf_cable_df"].columns:
            st.session_state["cf_cable_df"]["_row_id"] = range(len(st.session_state["cf_cable_df"]))
        
        # Ensure each row has a Name column
        if "Name" not in st.session_state["cf_cable_df"].columns:
            st.session_state["cf_cable_df"]["Name"] = ""
        
        # Ensure custom conductors columns exist
        if "Use custom conductors" not in st.session_state["cf_cable_df"].columns:
            st.session_state["cf_cable_df"]["Use custom conductors"] = False
        if "Custom conductors" not in st.session_state["cf_cable_df"].columns:
            st.session_state["cf_cable_df"]["Custom conductors"] = None
        if "Custom area per cable" not in st.session_state["cf_cable_df"].columns:
            st.session_state["cf_cable_df"]["Custom area per cable"] = None
        
        df_in = st.session_state["cf_cable_df"].copy()

        # Helper function to get area per conductor from table
        def _get_area_for_cable(table_key, construction, cond_size, n_conductors):
            """Get area for a specific cable configuration"""
            if table_key not in cable_tables or cable_tables[table_key][1] is None:
                return None
            table_data = cable_tables[table_key][1]
            if construction not in table_data:
                return None
            size_data = table_data.get(construction, {}).get(cond_size, {})
            if not size_data:
                return None
            areas_by_count = size_data.get("areas_by_count", {})
            return areas_by_count.get(int(n_conductors), None)

        # Initialize edited list to track changes
        edited_list = []

        if cable_tables:
            # Table 6 mode: use hierarchical dropdown selections
            num_rows = len(df_in)
            
            for display_num, (idx, row) in enumerate(df_in.iterrows(), 1):
                row_id = row.get("_row_id", idx)  # Get the unique row ID
                cable_name = row.get("Name", "")
                use_custom = row.get("Use custom conductors", False)
                custom_cond_count = row.get("Custom conductors", None)
                custom_area = row.get("Custom area per cable", None)
                table_key = row.get("Table", list(cable_tables.keys())[0])
                construction = row.get("Construction", "stranded")
                cond_size = row.get("Conductor size", "")
                n_cond = row.get("Conductors per cable", 1)
                qty = row.get("Qty (cables)", 1)
                
                # Get available options for dropdowns
                table_data = cable_tables.get(table_key, (None, {}))[1] or {}
                available_constructions = list(table_data.keys())
                if construction not in available_constructions and available_constructions:
                    construction = available_constructions[0]
                
                available_sizes = list(table_data.get(construction, {}).keys()) if construction in table_data else []
                if cond_size not in available_sizes and available_sizes:
                    cond_size = available_sizes[0]
                
                # Get available conductor counts
                size_data = table_data.get(construction, {}).get(cond_size, {})
                available_counts = sorted(size_data.get("areas_by_count", {}).keys()) if size_data else []
                if int(n_cond) not in available_counts and available_counts:
                    n_cond = available_counts[0]
                
                # Calculate area per cable
                area_per_cable = _get_area_for_cable(table_key, construction, cond_size, int(n_cond))
                
                # Create columns for row: [container with content] [minus button]
                box_col, minus_col = st.columns([0.95, 0.05], gap="small")
                
                # Cable entry in bordered box
                with box_col:
                    row_container = st.container(border=True)
                    with row_container:
                        col1, col2, col3 = st.columns([0.05, 0.25, 0.70], gap="small")
                        
                        # Row number label
                        with col1:
                            st.markdown(f"**{display_num}**")
                        
                        # Cable group name
                        with col2:
                            cable_name = st.text_input(
                                "Name",
                                value=cable_name,
                                placeholder="e.g., 'Main feeder'",
                                key=f"cf_cable_name_{row_id}"
                            )
                        
                        # Cable selection controls - vertical stack
                        with col3:
                            # Row 1: Cable Type
                            st.selectbox(
                                "Cable type",
                                options=list(cable_tables.keys()),
                                index=list(cable_tables.keys()).index(table_key) if table_key in cable_tables else 0,
                                key=f"cf_cable_table_{row_id}",
                                format_func=lambda k: cable_tables[k][0]
                            )
                            table_key = st.session_state[f"cf_cable_table_{row_id}"]
                            table_data = cable_tables.get(table_key, (None, {}))[1] or {}
                            available_constructions = list(table_data.keys())
                            
                            # Row 2: Construction (if multiple available)
                            if len(available_constructions) > 1:
                                construction = st.selectbox(
                                    "Construction",
                                    options=available_constructions,
                                    index=available_constructions.index(construction) if construction in available_constructions else 0,
                                    key=f"cf_cable_construction_{row_id}"
                                )
                            else:
                                construction = available_constructions[0] if available_constructions else "stranded"
                                st.write(f"**Construction:** {construction}")
                            
                            # Row 3: Conductor Size
                            available_sizes = list(table_data.get(construction, {}).keys()) if construction in table_data else []
                            cond_size = st.selectbox(
                                "Conductor size",
                                options=available_sizes,
                                index=available_sizes.index(cond_size) if cond_size in available_sizes else 0,
                                key=f"cf_cable_size_{row_id}"
                            )
                            
                            # Row 4: Number of Conductors
                            use_custom = st.checkbox(
                                "Custom conductors",
                                value=use_custom,
                                key=f"cf_cable_use_custom_{row_id}"
                            )
                            
                            if use_custom:
                                # Custom mode: input custom conductor count and area
                                custom_cond_count = st.number_input(
                                    "Number of conductors",
                                    min_value=1,
                                    value=int(custom_cond_count) if custom_cond_count else 1,
                                    step=1,
                                    key=f"cf_cable_custom_cond_{row_id}"
                                )
                                custom_area = st.number_input(
                                    "Area per cable (mm²)",
                                    min_value=0.0,
                                    value=float(custom_area) if custom_area else 0.0,
                                    step=0.01,
                                    format="%.2f",
                                    key=f"cf_cable_custom_area_{row_id}"
                                )
                                n_cond = custom_cond_count
                                area_per_cable = custom_area
                            else:
                                # Table mode: select from available options
                                size_data = table_data.get(construction, {}).get(cond_size, {})
                                available_counts = sorted(size_data.get("areas_by_count", {}).keys()) if size_data else []
                                n_cond = st.selectbox(
                                    "Number of conductors in cable",
                                    options=available_counts,
                                    index=available_counts.index(int(n_cond)) if int(n_cond) in available_counts else 0,
                                    key=f"cf_cable_ncond_{row_id}"
                                )
                                area_per_cable = _get_area_for_cable(table_key, construction, cond_size, int(n_cond))
                            
                            # Row 5: Quantity of Cables
                            qty = st.number_input(
                                "Qty (cables)",
                                min_value=1,
                                value=int(qty) if qty else 1,
                                step=1,
                                key=f"cf_cable_qty_{row_id}"
                            )
                        
                        # Display area information
                        if area_per_cable is not None:
                            area_display_col1, area_display_col2 = st.columns([1, 1])
                            with area_display_col1:
                                st.caption(f"Area per cable: {area_per_cable:.2f} mm²")
                            with area_display_col2:
                                total_area = area_per_cable * qty
                                st.caption(f"Total area: {total_area:.2f} mm²")

                        # Cable group color swatch (matches conduit diagram palette/layout)
                        area_per_conductor = None
                        if t6_area:
                            t = _norm(table_key)
                            s = _norm(cond_size)
                            area_per_conductor = _to_float(t6_area.get(t, {}).get(s, None))
                        if area_per_conductor is None and area_per_cable and n_cond:
                            area_per_conductor = float(area_per_cable) / float(n_cond)

                        with col2:
                            swatch_svg = _build_cable_group_swatch_svg(
                                area_per_cable=area_per_cable,
                                n_cond=int(n_cond) if n_cond else 0,
                                area_per_conductor=area_per_conductor,
                                group_idx=display_num - 1,
                            )
                            if swatch_svg:
                                st.markdown(swatch_svg, unsafe_allow_html=True)
                                st.caption("Group color preview (matches conduit diagram)")
                
                # Minus button outside the box (on every row)
                with minus_col:
                    st.write("")  # Spacer
                    if st.button("➖", key=f"cf_cable_minus_{row_id}", help="Remove this cable group", width="stretch"):
                        st.session_state["cf_cable_df"] = st.session_state["cf_cable_df"][st.session_state["cf_cable_df"]["_row_id"] != row_id].reset_index(drop=True)
                        st.rerun()
                
                # Append to edited list
                edited_list.append({
                    "Name": cable_name,
                    "Table": table_key,
                    "Construction": construction,
                    "Conductor size": cond_size,
                    "Conductors per cable": int(n_cond),
                    "Qty (cables)": int(qty),
                    "Area per cable (mm²)": area_per_cable,
                    "Use custom conductors": use_custom,
                    "Custom conductors": custom_cond_count,
                    "Custom area per cable": custom_area
                })
            
            # Plus button after the last cable group
            plus_col1, plus_col2 = st.columns([0.95, 0.05], gap="small")
            with plus_col2:
                st.write("")  # Spacer
                if st.button("➕", key=f"cf_cable_plus_new", help="Add new cable group", width="stretch"):
                    first_table_key = list(cable_tables.keys())[0]
                    first_table = cable_tables[first_table_key][1]
                    first_construction = list(first_table.keys())[0] if first_table else "stranded"
                    first_size = list(first_table.get(first_construction, {}).keys())[0] if first_table else ""
                    # Generate a new unique row ID
                    max_id = st.session_state["cf_cable_df"]["_row_id"].max() if len(st.session_state["cf_cable_df"]) > 0 else -1
                    new_row_id = int(max_id) + 1 if max_id >= 0 else 0
                    new_row = {
                        "Name": "",
                        "Table": first_table_key,
                        "Construction": first_construction,
                        "Conductor size": first_size,
                        "Conductors per cable": 1,
                        "Qty (cables)": 1,
                        "Use custom conductors": False,
                        "Custom conductors": None,
                        "Custom area per cable": None,
                        "_row_id": new_row_id
                    }
                    new_df = pd.concat([st.session_state["cf_cable_df"], pd.DataFrame([new_row])], ignore_index=True)
                    st.session_state["cf_cable_df"] = new_df
                    st.rerun()
            
            # Convert edited list back to dataframe for downstream calculations
            edited = pd.DataFrame(edited_list)
            
            # Sync widget states back to session state dataframe
            for display_num, (idx, row) in enumerate(df_in.iterrows(), 1):
                row_id = row.get("_row_id", idx)
                # Update Name if it exists in session state
                if f"cf_cable_name_{row_id}" in st.session_state:
                    st.session_state["cf_cable_df"].loc[st.session_state["cf_cable_df"]["_row_id"] == row_id, "Name"] = st.session_state[f"cf_cable_name_{row_id}"]
                # Update Table
                if f"cf_cable_table_{row_id}" in st.session_state:
                    st.session_state["cf_cable_df"].loc[st.session_state["cf_cable_df"]["_row_id"] == row_id, "Table"] = st.session_state[f"cf_cable_table_{row_id}"]
                # Update Construction
                if f"cf_cable_construction_{row_id}" in st.session_state:
                    st.session_state["cf_cable_df"].loc[st.session_state["cf_cable_df"]["_row_id"] == row_id, "Construction"] = st.session_state[f"cf_cable_construction_{row_id}"]
                # Update Conductor size
                if f"cf_cable_size_{row_id}" in st.session_state:
                    st.session_state["cf_cable_df"].loc[st.session_state["cf_cable_df"]["_row_id"] == row_id, "Conductor size"] = st.session_state[f"cf_cable_size_{row_id}"]
                # Update Conductors per cable
                if f"cf_cable_ncond_{row_id}" in st.session_state:
                    st.session_state["cf_cable_df"].loc[st.session_state["cf_cable_df"]["_row_id"] == row_id, "Conductors per cable"] = st.session_state[f"cf_cable_ncond_{row_id}"]
                # Update Qty
                if f"cf_cable_qty_{row_id}" in st.session_state:
                    st.session_state["cf_cable_df"].loc[st.session_state["cf_cable_df"]["_row_id"] == row_id, "Qty (cables)"] = st.session_state[f"cf_cable_qty_{row_id}"]
                # Update Use custom conductors
                if f"cf_cable_use_custom_{row_id}" in st.session_state:
                    st.session_state["cf_cable_df"].loc[st.session_state["cf_cable_df"]["_row_id"] == row_id, "Use custom conductors"] = st.session_state[f"cf_cable_use_custom_{row_id}"]
                # Update Custom conductors
                if f"cf_cable_custom_cond_{row_id}" in st.session_state:
                    st.session_state["cf_cable_df"].loc[st.session_state["cf_cable_df"]["_row_id"] == row_id, "Custom conductors"] = st.session_state[f"cf_cable_custom_cond_{row_id}"]
                # Update Custom area per cable
                if f"cf_cable_custom_area_{row_id}" in st.session_state:
                    st.session_state["cf_cable_df"].loc[st.session_state["cf_cable_df"]["_row_id"] == row_id, "Custom area per cable"] = st.session_state[f"cf_cable_custom_area_{row_id}"]

        else:
            # Manual mode: allow entering area per cable directly
            for idx, row in df_in.iterrows():
                cable_desc = row.get("Cable description", "(Manual)")
                n_cond = row.get("Conductors per cable", 3)
                qty = row.get("Qty (cables)", 1)
                area_per_cable = row.get("Area per cable (mm²)", 150.0)
                
                # Create row container with label
                row_container = st.container(border=True)
                with row_container:
                    col1, col2 = st.columns([0.05, 0.95], gap="small")
                    
                    # Row number label
                    with col1:
                        st.markdown(f"**{idx + 1}**")
                    
                    # Cable entry controls
                    with col2:
                        cable_desc = st.text_input(
                            "Cable description",
                            value=cable_desc,
                            key=f"cf_cable_desc_{idx}"
                        )
                        
                        n_cond = st.number_input(
                            "Conductors per cable",
                            min_value=1,
                            value=int(n_cond) if n_cond else 3,
                            step=1,
                            key=f"cf_cable_ncond_{idx}"
                        )
                        
                        qty_col1, qty_col2, qty_col3 = st.columns([2, 1, 1], gap="small")
                        with qty_col1:
                            qty = st.number_input(
                                "Qty (cables)",
                                min_value=1,
                                value=int(qty) if qty else 1,
                                step=1,
                                key=f"cf_cable_qty_{idx}"
                            )
                        
                        with qty_col2:
                            if st.button("➕", key=f"cf_cable_plus_{idx}", help="Add new cable group"):
                                new_row = {
                                    "Cable description": "(Manual)",
                                    "Conductors per cable": 3,
                                    "Qty (cables)": 1,
                                    "Area per cable (mm²)": 150.0
                                }
                                new_df = pd.concat([st.session_state["cf_cable_df"], pd.DataFrame([new_row])], ignore_index=True)
                                st.session_state["cf_cable_df"] = new_df
                                st.rerun()
                        
                        with qty_col3:
                            if st.button("➖", key=f"cf_cable_minus_{idx}", help="Remove this cable group"):
                                st.session_state["cf_cable_df"] = st.session_state["cf_cable_df"].drop(idx).reset_index(drop=True)
                                st.rerun()
                        
                        area_per_cable = st.number_input(
                            "Area per cable (mm²)",
                            min_value=0.0,
                            value=float(area_per_cable) if area_per_cable else 150.0,
                            step=0.01,
                            key=f"cf_cable_area_{idx}"
                        )
                    
                    # Display total area
                    total_area = area_per_cable * qty if area_per_cable and qty else None
                    st.caption(f"Total area: {fmt(total_area, 'mm²')}")
                
                # Append to edited list
                edited_list.append({
                    "Cable description": cable_desc,
                    "Conductors per cable": n_cond,
                    "Qty (cables)": qty,
                    "Area per cable (mm²)": area_per_cable
                })
            
            # Convert edited list back to dataframe for downstream calculations
            edited = pd.DataFrame(edited_list)

        # ----------------------------
        # Calculations
        # ----------------------------
        st.markdown("## 3) Results")


        # total # of cables (for Table 9 allowable selection)
        try:
            n_cables_total = int(pd.to_numeric(edited["Qty (cables)"], errors="coerce").fillna(0).sum())
        except Exception:
            n_cables_total = 0

        # total conductor area
        def _row_total_area(r):
            qty = _to_float(r.get("Qty (cables)"))

            # Preferred: use Area per cable (mm²) if present (auto-filled or manual)
            area_per_cable = _to_float(r.get("Area per cable (mm²)"))

            # If not present (or blank), attempt to compute from Table 6:
            # area_per_conductor × conductors_per_cable
            if area_per_cable is None and t6_area:
                ncond = _to_float(r.get("Conductors per cable"))
                t = _norm(r.get("Cable type", ""))
                s = _norm(r.get("Conductor size", ""))
                a_cond = _to_float(t6_area.get(t, {}).get(s, None))
                if (ncond is not None) and (a_cond is not None):
                    area_per_cable = float(ncond) * float(a_cond)

            if qty is None or area_per_cable is None:
                return 0.0
            return float(qty) * float(area_per_cable)

        try:
            total_cable_area = float(edited.apply(_row_total_area, axis=1).sum())
        except Exception:
            total_cable_area = 0.0

        # Determine allowable based on conduit selection + n_cables_total
        if not use_manual_conduit:
            used_oesc = False
            if conduit_type_key and oesc_tables is not None and hasattr(oesc_tables, "get_allowable_conduit_area_mm2"):
                ts = _try_int(conduit_trade)
                if ts is not None:
                    conduit_allowed_area = oesc_tables.get_allowable_conduit_area_mm2(conduit_type_key, ts, max(1, n_cables_total))
                    if conduit_allowed_area is not None:
                        used_oesc = True
                        if conduit_internal_area:
                            conduit_allowed_pct = conduit_allowed_area / conduit_internal_area
                        if hasattr(oesc_tables, "TABLE_9A_TYPES") and conduit_type_key in oesc_tables.TABLE_9A_TYPES:
                            sub = "9C" if n_cables_total <= 1 else ("9E" if n_cables_total == 2 else "9G")
                        else:
                            sub = "9D" if n_cables_total <= 1 else ("9F" if n_cables_total == 2 else "9H")
                        allowed_source = f"OESC Table {sub}"
            if not used_oesc and t9_index:
                row = t9_index.get((conduit_type, conduit_trade), {})
                conduit_allowed_area, conduit_allowed_pct, allowed_source = _infer_allowed_area_and_pct(
                    row, max(1, n_cables_total), conduit_internal_area
                )
        else:
            # manual conduit mode already handled earlier
            if conduit_allowed_area is None and conduit_internal_area:
                conduit_allowed_area, conduit_allowed_pct, allowed_source = _infer_allowed_area_and_pct(
                    {}, max(1, n_cables_total), conduit_internal_area
                )

        fill_pct = safe_div(total_cable_area, conduit_internal_area) if conduit_internal_area else None

        m1, m2, m3, m4, m5 = st.columns([1, 1, 1, 1, 1], gap="large")
        m1.metric("Total cables in raceway", fmt(n_cables_total, ""))
        m2.metric("Total cable area", fmt(total_cable_area, "mm²"))
        # Format conduit internal area in full form without scientific notation
        if conduit_internal_area:
            m3.metric("Conduit internal area", f"{conduit_internal_area:,.2f} mm²")
        else:
            m3.metric("Conduit internal area", "—")

        total_allowable_area = conduit_allowed_area if conduit_allowed_area is not None else None
        remaining_allowable_area = (conduit_allowed_area - total_cable_area) if (conduit_allowed_area is not None) else None

        m4.metric("Total allowable area", fmt(total_allowable_area, "mm²"))
        m5.metric("Remaining allowable area", fmt(remaining_allowable_area, "mm²"))

        if fill_pct is None:
            st.warning("Provide a conduit internal area to compute fill.")
        else:
            # Format fill percentage to 4 decimals
            st.metric("Actual fill (%)", f"{fill_pct * 100.0:.4f}%")

        if conduit_allowed_area is not None and conduit_internal_area:
            allowed_pct_disp = (conduit_allowed_area / conduit_internal_area) * 100.0
            st.info(f"Allowable fill: **{fmt(allowed_pct_disp, '%')}**  (allowable area: **{fmt(conduit_allowed_area, 'mm²')}**)  — {allowed_source}")
            ok = total_cable_area <= conduit_allowed_area + 1e-9
            if ok:
                st.success("✅ Fill is within the allowable limit for the selected conduit.")
            else:
                st.error("❌ Fill exceeds the allowable limit for the selected conduit.")

            # Suggest next trade size (same type) if we have Table 9
            if (not use_manual_conduit) and t9_index and not ok:
                # Build candidate sizes for same type and pick smallest allowed_area >= total_cable_area
                candidates = []
                for (t, s), r in t9_index.items():
                    if t != conduit_type:
                        continue
                    ia = _infer_internal_area(r)
                    if ia is None:
                        continue
                    a_allow, _, _ = _infer_allowed_area_and_pct(r, max(1, n_cables_total), ia)
                    if a_allow is None:
                        continue
                    candidates.append((s, a_allow, ia))
                # sort candidates by allowed area, then label
                candidates.sort(key=lambda x: (x[1], x[0]))
                suggestion = None
                for s, a_allow, ia in candidates:
                    if a_allow >= total_cable_area - 1e-9:
                        suggestion = (s, a_allow, ia)
                        break
                if suggestion:
                    s, a_allow, ia = suggestion
                    st.success(
                        f"Suggested next size (same conduit type) that meets fill: **{conduit_type} — {s}** "
                        f"(allowable area ≈ {fmt(a_allow,'mm²')}, internal area ≈ {fmt(ia,'mm²')})."
                    )
                else:
                    st.warning("No larger trade size found in Table 9 that meets fill (based on parsed data).")

        else:
            st.warning("Allowable fill could not be determined (Table 9 not available or columns not recognized).")

        st.divider()
        st.markdown("### Equation used")
        eq(r"\text{Fill}=\frac{\sum\left(A_{cond}\cdot N_{cond/cable}\cdot N_{cables}\right)}{A_{conduit}}")

        st.divider()
        st.markdown("### Conduit layout (visual)")

        def _layout_in_circle(n, r, R):
            """Simple concentric-ring layout for n equal circles of radius r inside radius R."""
            if not n or not r or not R or r <= 0 or R <= 0:
                return []
            if r > R:
                return []
            if n == 1:
                return [(0.0, 0.0)]
            positions = [(0.0, 0.0)]
            remaining = n - 1
            ring = 1
            while remaining > 0:
                ring_radius = ring * (2.2 * r)
                if ring_radius + r > R:
                    break
                circumference = 2 * math.pi * ring_radius
                count = max(1, int(circumference / (2.2 * r)))
                count = min(count, remaining)
                for i in range(count):
                    angle = 2 * math.pi * i / count
                    positions.append((ring_radius * math.cos(angle), ring_radius * math.sin(angle)))
                remaining -= count
                ring += 1
            return positions[:n]

        def _place_cables(cables, conduit_radius, angle_offset=0.0, angle_count=36, seed_mode="center"):
            """Greedy circle packing using tangent candidates (deterministic)."""
            placed = []
            unplaced = 0
            spacing_options = [0.5, 0.2, 0.0]  # progressively relax spacing if needed

            def fits(x, y, r, spacing):
                if (x * x + y * y) ** 0.5 + r > conduit_radius:
                    return False
                for other in placed:
                    dx = x - other["x"]
                    dy = y - other["y"]
                    min_sep = r + other["r"] + spacing
                    if (dx * dx + dy * dy) < (min_sep * min_sep):
                        return False
                return True

            def circle_intersections(x0, y0, r0, x1, y1, r1):
                dx = x1 - x0
                dy = y1 - y0
                d = math.hypot(dx, dy)
                if d == 0 or d > (r0 + r1) or d < abs(r0 - r1):
                    return []
                a = (r0 * r0 - r1 * r1 + d * d) / (2 * d)
                h_sq = r0 * r0 - a * a
                if h_sq < 0:
                    return []
                h = math.sqrt(h_sq)
                xm = x0 + a * dx / d
                ym = y0 + a * dy / d
                rx = -dy * (h / d)
                ry = dx * (h / d)
                return [(xm + rx, ym + ry), (xm - rx, ym - ry)]

            # Place larger cables first to improve packing
            cables_sorted = sorted(cables, key=lambda c: (c.get("r") or 0.0), reverse=True)
            angles = [angle_offset + i * (math.pi / max(1.0, angle_count / 2.0)) for i in range(angle_count)]

            for cable in cables_sorted:
                r = cable.get("r")
                if r is None or r <= 0:
                    unplaced += 1
                    continue
                if r > conduit_radius:
                    unplaced += 1
                    continue
                if not placed:
                    if seed_mode == "boundary":
                        seed_r = max(0.0, conduit_radius - r)
                        cable["x"], cable["y"] = seed_r * math.cos(angle_offset), seed_r * math.sin(angle_offset)
                    else:
                        cable["x"], cable["y"] = 0.0, 0.0
                    placed.append(cable)
                    continue

                placed_flag = False

                for spacing in spacing_options:
                    best = None
                    best_score = None
                    current_max = 0.0
                    for o in placed:
                        current_max = max(current_max, math.hypot(o["x"], o["y"]) + o["r"])
                    candidates = []

                    # Tangent to one circle (angle sweep)
                    for other in placed:
                        base_dist = other["r"] + r + spacing
                        for a in angles:
                            candidates.append(
                                (other["x"] + base_dist * math.cos(a), other["y"] + base_dist * math.sin(a))
                            )

                    # Tangent to two circles (circle intersections)
                    for i in range(len(placed)):
                        for j in range(i + 1, len(placed)):
                            o1 = placed[i]
                            o2 = placed[j]
                            d1 = o1["r"] + r + spacing
                            d2 = o2["r"] + r + spacing
                            candidates.extend(
                                circle_intersections(o1["x"], o1["y"], d1, o2["x"], o2["y"], d2)
                            )

                    # Boundary candidates (tangent to conduit wall)
                    boundary_r = conduit_radius - r
                    if boundary_r > 0:
                        for a in angles:
                            candidates.append((boundary_r * math.cos(a), boundary_r * math.sin(a)))

                    # Rank candidates by distance to center
                    for (x, y) in candidates:
                        if not fits(x, y, r, spacing):
                            continue
                        extent = math.hypot(x, y) + r
                        max_extent = max(current_max, extent)
                        score = (max_extent, extent, (x * x + y * y))
                        if best_score is None or score < best_score:
                            best_score = score
                            best = (x, y)

                    # Fallback: a few concentric rings
                    if best is None:
                        for ring in range(1, 16):
                            ring_r = ring * (r * 1.1)
                            if ring_r + r > conduit_radius:
                                break
                            for a in angles:
                                x = ring_r * math.cos(a)
                                y = ring_r * math.sin(a)
                                if fits(x, y, r, spacing):
                                    extent = math.hypot(x, y) + r
                                    max_extent = max(current_max, extent)
                                    score = (max_extent, extent, (x * x + y * y))
                                    if best_score is None or score < best_score:
                                        best_score = score
                                        best = (x, y)
                            if best is not None:
                                break

                    if best is not None:
                        cable["x"], cable["y"] = best[0], best[1]
                        placed.append(cable)
                        placed_flag = True
                        break

                if not placed_flag:
                    unplaced += 1

            return placed, unplaced

        def _place_cables_allow_overlap(cables, conduit_radius):
            """Fallback placement that allows overlap (keeps all circles inside the conduit)."""
            placed = []
            for i, cable in enumerate(cables):
                r = cable.get("r")
                if r is None or r <= 0 or r > conduit_radius:
                    continue
                if i == 0:
                    cable["x"], cable["y"] = 0.0, 0.0
                    placed.append(cable)
                    continue
                # place along expanding spiral without collision checks
                angle = i * 0.7
                dist = min(conduit_radius - r, (0.7 * r) * math.sqrt(i))
                x = dist * math.cos(angle)
                y = dist * math.sin(angle)
                cable["x"], cable["y"] = x, y
                placed.append(cable)
            return placed

        def _build_conduit_svg(conduit_radius, cables, overpacked=False):
            canvas = 360
            margin = 12
            scale = (canvas - 2 * margin) / (2 * conduit_radius) if conduit_radius else 1.0
            cx = canvas / 2
            cy = canvas / 2

            def to_px(val_mm):
                return val_mm * scale

            svg_parts = []
            svg_parts.append(
                f'<svg width="{canvas}" height="{canvas}" viewBox="0 0 {canvas} {canvas}" '
                f'xmlns="http://www.w3.org/2000/svg">'
            )
            svg_parts.append(
                f'<circle cx="{cx}" cy="{cy}" r="{to_px(conduit_radius):.2f}" '
                f'stroke="#222" stroke-width="2" fill="#f8f8f8"/>'
            )

            for cable in cables:
                x = cable.get("x")
                y = cable.get("y")
                r = cable.get("r")
                if x is None or y is None or r is None:
                    continue
                color = CF_PALETTE[cable.get("group_idx", 0) % len(CF_PALETTE)]
                svg_parts.append(
                    f'<circle cx="{cx + to_px(x):.2f}" cy="{cy + to_px(y):.2f}" r="{to_px(r):.2f}" '
                    f'stroke="#333" stroke-width="1" fill="{color}" fill-opacity="0.55"/>'
                )

                n_cond = cable.get("n_cond")
                r_cond = cable.get("r_cond")
                if n_cond:
                    margin = 0.6
                    R_inner = r - margin
                    if R_inner > 0:
                        if r_cond is None or r_cond <= 0:
                            r_cond_use = R_inner / max(1.6 * math.sqrt(int(n_cond)), 1.6)
                        else:
                            r_cond_use = min(r_cond, R_inner)

                        # Shrink conductors if they don't fit
                        conductor_positions = []
                        for _ in range(15):
                            conductor_positions = _pack_circles_in_circle(int(n_cond), r_cond_use, R_inner)
                            if len(conductor_positions) >= int(n_cond):
                                break
                            r_cond_use *= 0.9

                        for (dx, dy) in conductor_positions[: int(n_cond)]:
                            svg_parts.append(
                                f'<circle cx="{cx + to_px(x + dx):.2f}" cy="{cy + to_px(y + dy):.2f}" '
                                f'r="{to_px(r_cond_use):.2f}" stroke="#111" stroke-width="0.6" '
                                f'fill="#000000"/>'
                            )

            if overpacked:
                # Diagonal red hatch clipped to conduit circle
                svg_parts.append(
                    f'<defs><clipPath id="conduitClip"><circle cx="{cx}" cy="{cy}" '
                    f'r="{to_px(conduit_radius):.2f}"/></clipPath></defs>'
                )
                svg_parts.append(f'<g clip-path="url(#conduitClip)" opacity="0.35">')
                step = 14
                for x in range(-canvas, canvas * 2, step):
                    x1 = x
                    y1 = -canvas
                    x2 = x + canvas
                    y2 = canvas
                    svg_parts.append(
                        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                        f'stroke="#cc0000" stroke-width="6"/>'
                    )
                svg_parts.append("</g>")

            svg_parts.append("</svg>")
            return "".join(svg_parts)

        show_viz = st.checkbox("Show conduit cross-section diagram", value=True, key="cf_show_viz")
        if show_viz:
            conduit_radius = _area_to_radius(conduit_internal_area) if conduit_internal_area else None
            if not conduit_radius:
                st.warning("Provide a conduit internal area to render the cross-section.")
            else:
                cable_instances = []
                approx_notes = []
                render_issues = []
                expected_cable_count = 0

                try:
                    for group_idx, (_, r) in enumerate(edited.iterrows()):
                        qty = int(_to_float(r.get("Qty (cables)")) or 0)
                        n_cond = int(_to_float(r.get("Conductors per cable")) or 0)
                        expected_cable_count += max(qty, 0)

                        area_per_cable = _to_float(r.get("Area per cable (mm²)"))
                        if area_per_cable is None and t6_area:
                            t = _norm(r.get("Cable type", ""))
                            s = _norm(r.get("Conductor size", ""))
                            a_cond_table = _to_float(t6_area.get(t, {}).get(s, None))
                            if a_cond_table is not None and n_cond:
                                area_per_cable = float(n_cond) * float(a_cond_table)
                        if area_per_cable is None:
                            render_issues.append("One or more cable groups are missing an area per cable.")

                        area_per_conductor = None
                        if t6_area:
                            t = _norm(r.get("Cable type", ""))
                            s = _norm(r.get("Conductor size", ""))
                            area_per_conductor = _to_float(t6_area.get(t, {}).get(s, None))

                        if area_per_conductor is None and area_per_cable and n_cond:
                            area_per_conductor = area_per_cable / n_cond
                            approx_notes.append("Conductor areas were approximated from cable area for custom entries.")

                        r_cable = _area_to_radius(area_per_cable) if area_per_cable else None
                        r_cond = _area_to_radius(area_per_conductor) if area_per_conductor else None

                        for _ in range(qty):
                            cable_instances.append(
                                {
                                    "r": r_cable,
                                    "n_cond": n_cond,
                                    "r_cond": r_cond,
                                    "group_idx": group_idx,
                                }
                            )
                except Exception:
                    cable_instances = []
                    render_issues.append("Unexpected error while building cable instances for rendering.")

                if not cable_instances:
                    st.info("Add at least one cable group with an area to render the layout.")
                    if render_issues:
                        st.caption(" ".join(sorted(set(render_issues))))
                else:
                    placed, unplaced = _place_cables(cable_instances, conduit_radius)
                    # Retry with different seeds/angles to improve packing (non-overlapping)
                    if unplaced > 0:
                        best_placed = placed
                        best_unplaced = unplaced
                        best_extent = None
                        seed_modes = ["center", "boundary"]
                        offsets = [0.0, math.pi / 36.0, math.pi / 18.0, math.pi / 12.0, math.pi / 9.0]
                        for mode in seed_modes:
                            for off in offsets:
                                p2, u2 = _place_cables(
                                    cable_instances,
                                    conduit_radius,
                                    angle_offset=off,
                                    angle_count=48,
                                    seed_mode=mode,
                                )
                                if u2 == 0:
                                    # Choose the tightest layout
                                    extent = 0.0
                                    for c in p2:
                                        extent = max(extent, math.hypot(c["x"], c["y"]) + c["r"])
                                    if best_extent is None or extent < best_extent:
                                        best_extent = extent
                                        best_placed = p2
                                        best_unplaced = u2
                                elif u2 < best_unplaced:
                                    best_unplaced = u2
                                    best_placed = p2
                            if best_unplaced == 0:
                                # keep looking for tighter layouts
                                continue
                        placed, unplaced = best_placed, best_unplaced
                    overpacked = (
                        conduit_allowed_area is not None
                        and total_cable_area is not None
                        and total_cable_area > conduit_allowed_area + 1e-9
                    )
                    if unplaced > 0 and overpacked:
                        placed = _place_cables_allow_overlap(cable_instances, conduit_radius)
                    svg = _build_conduit_svg(conduit_radius, placed, overpacked=overpacked)
                    st.markdown(svg, unsafe_allow_html=True)

                    notes = []
                    rendered_count = len(placed)
                    if rendered_count != expected_cable_count:
                        notes.append(
                            f"Rendered {rendered_count} of {expected_cable_count} cables. "
                            "Missing items may be due to unavailable cable area."
                        )
                    if unplaced > 0 and overpacked:
                        notes.append("Cables overlap in the diagram because fill exceeds the allowable space.")
                    if unplaced > 0 and not overpacked:
                        notes.append(
                            "A non-overlapping layout could not be found even though fill is within allowable. "
                            "Try adjusting cable grouping or quantities to help the packer."
                        )
                    if approx_notes:
                        notes.append("Conductor circles may be approximate when per-conductor area is unavailable.")
                    if overpacked:
                        notes.append("Red hatching indicates the conduit is over-packed.")
                    if render_issues:
                        notes.append(" ".join(sorted(set(render_issues))))
                    if notes:
                        st.caption(" ".join(notes))

        with st.expander("Show calculation details", expanded=False):
            st.write(f"- Conduit: **{conduit_type}** — **{conduit_trade}**")
            st.write(f"- Conduit internal area: **{fmt(conduit_internal_area, 'mm²')}**")
            st.write(f"- Total cables: **{n_cables_total}**")
            st.write(f"- Total cable area: **{fmt(total_cable_area, 'mm²')}**")
            if conduit_allowed_area is not None:
                st.write(f"- Allowable area: **{fmt(conduit_allowed_area, 'mm²')}**  ({allowed_source})")

            st.markdown("#### Cable group breakdown")
            try:
                show_df = edited.copy()
                show_df["Area per conductor (mm²) (used)"] = show_df.apply(
                    lambda r: _to_float(t6_area.get(_norm(r.get("Cable type","")), {}).get(_norm(r.get("Conductor size","")), None)) if t6_area else None,
                    axis=1,
                )

                # Compute/attach Area per cable used
                if "Area per cable (mm²)" not in show_df.columns:
                    show_df["Area per cable (mm²) (used)"] = show_df.apply(
                        lambda r: (
                            (_to_float(r.get("Conductors per cable")) or 0.0)
                            * (_to_float(t6_area.get(_norm(r.get("Cable type","")), {}).get(_norm(r.get("Conductor size","")), None)) or 0.0)
                        )
                        if t6_area
                        else None,
                        axis=1,
                    )
                else:
                    show_df["Area per cable (mm²) (used)"] = show_df["Area per cable (mm²)"].apply(_to_float)

                show_df["Total group area (mm²)"] = show_df.apply(_row_total_area, axis=1)

                st.dataframe(show_df, width="stretch", hide_index=True)
            except Exception:
                st.write("(Unable to render breakdown table in this environment.)")

        st.caption(
            "Important: Always verify Table 6/Table 9 interpretations against the current OESC edition and project specs. "
            "Different table layouts may exist depending on how the table library is encoded."
        )

        # =====================================================================
        # Export Conduit Fill Report
        # =====================================================================
        st.divider()
        st.markdown("### 📄 Export calculation report")


        omml_fill = r"""
        <m:r><m:t>Fill</m:t></m:r>
        <m:r><m:t xml:space="preserve"> = </m:t></m:r>
        <m:f>
            <m:num>
                <m:e>
                    <m:r><m:t>∑</m:t></m:r>

                    <m:r><m:t>(</m:t></m:r>
                    
                    <m:sSub>
                        <m:e><m:r><m:t>A</m:t></m:r></m:e>
                        <m:sub><m:r><m:t>cond</m:t></m:r></m:sub>
                    </m:sSub>

                    <m:r><m:t xml:space="preserve"> × </m:t></m:r>
                    
                    <m:sSub>
                        <m:e><m:r><m:t>N</m:t></m:r></m:e>
                        <m:sub><m:r><m:t>cond/cable</m:t></m:r></m:sub>
                    </m:sSub>

                    <m:r><m:t xml:space="preserve"> × </m:t></m:r>

                    <m:sSub>
                        <m:e><m:r><m:t>N</m:t></m:r></m:e>
                        <m:sub><m:r><m:t>cables</m:t></m:r></m:sub>
                    </m:sSub>

                    <m:r><m:t>)</m:t></m:r>
                </m:e>
            </m:num>

            <m:den>
                <m:sSub>
                    <m:e><m:r><m:t>A</m:t></m:r></m:e>
                    <m:sub><m:r><m:t>conduit</m:t></m:r></m:sub>
                </m:sSub>
            </m:den>
        </m:f>
        """


        def build_conduit_word_report():

            doc = Document("content/files/Template.docx")
            remove_leading_blank_paragraphs(doc)

            table = doc.sections[0].header.tables[0]

            append_to_value_line(table.cell(0, 3), PROJECT_NUMBER)
            append_to_value_line(table.cell(0, 4), "#")
            append_to_value_line(table.cell(2, 3), DESIGNER_NAME)
            append_to_value_line(table.cell(2, 4), datetime.now().strftime("%m/%d/%Y"))
            append_to_value_line(table.cell(3, 3), "")
            append_to_value_line(table.cell(3, 4), "")
            append_to_value_line(table.cell(3, 2), "Conduit Fill Calculation Report")

            doc.add_heading("Equations", level=1)
            p = doc.add_paragraph()
            p.add_run("Conduit fill calculation: ").bold = True
            add_omml_equation_to_paragraph(p, omml_fill)

            doc.add_heading("Assumptions", level=1)
            assumptions_cf = [
                "Conduit internal area retrieved from OESC Table 9 or manually entered.",
                "Cable areas calculated from Table 6 data based on conductor size and count.",
                "Custom cable groups with custom conductor counts and areas are entered manually.",
                "Fill percentage is calculated as total cable area divided by conduit internal area.",
                "Allowable fill follows the OESC standard for the selected number of cables.",
            ]
            for a in assumptions_cf:
                doc.add_paragraph(a, style="CalcBullet")

            doc.add_heading("Input Summary", level=1)
            summary_data = [
                ("Conduit Type", conduit_type),
                ("Trade Size", conduit_trade),
                ("Conduit Internal Area (mm²)", fmt(conduit_internal_area, "mm²")),
                ("Number of Cables", str(n_cables_total)),
                ("Total Cable Area (mm²)", fmt(total_cable_area, "mm²")),
                ("Total Allowable Area (mm²)", fmt(conduit_allowed_area, "mm²")),
                ("Actual Fill (%)", f"{fill_pct * 100.0:.4f}%" if fill_pct else "—"),
            ]
            
            t = doc.add_table(rows=1, cols=2)
            hdr = t.rows[0].cells
            p = hdr[0].paragraphs[0]
            p.clear()
            r = p.add_run("Parameter")
            r.bold = True
            p = hdr[1].paragraphs[0]
            p.clear()
            r = p.add_run("Value")
            r.bold = True
            for param, val in summary_data:
                row = t.add_row().cells
                row[0].text = str(param)
                row[1].text = str(val)
            
            set_table_borders(t)

            doc.add_heading("Cable Group Breakdown", level=1)
            try:
                show_df = edited.copy()
                cols_to_show = ["Name", "Table", "Construction", "Conductor size", "Conductors per cable", "Qty (cables)", "Area per cable (mm²)"]
                available_cols = [c for c in cols_to_show if c in show_df.columns]
                
                t_cables = doc.add_table(rows=1, cols=len(available_cols))
                for j, col in enumerate(available_cols):
                    cell = t_cables.rows[0].cells[j]
                    p = cell.paragraphs[0]
                    p.clear()
                    r = p.add_run(col)
                    r.bold = True
                
                for _, row_data in show_df.iterrows():
                    rr = t_cables.add_row().cells
                    for j, col in enumerate(available_cols):
                        val = row_data.get(col, None)
                        if isinstance(val, float):
                            rr[j].text = f"{val:.2f}"
                        else:
                            rr[j].text = str(val) if val is not None else "—"
            except Exception as e:
                doc.add_paragraph(f"(Unable to render cable breakdown: {str(e)})")

            set_table_borders(t_cables)

            if conduit_allowed_area is not None and conduit_internal_area:
                doc.add_heading("Compliance Status", level=1)
                ok = total_cable_area <= conduit_allowed_area + 1e-9
                status_text = "✓ PASS: Fill is within the allowable limit" if ok else "✗ FAIL: Fill exceeds the allowable limit"
                doc.add_paragraph(status_text)

            style = doc.styles["Normal"]
            style.font.name = "Calibri"
            style.font.size = Pt(11)

            bio = io.BytesIO()
            doc.save(bio)
            return bio.getvalue()

        def build_conduit_excel_report():

            def _safe_float(x):
                try:
                    return None if x is None else float(x)
                except Exception:
                    return None

            wb = Workbook()

            def autosize_ws(ws):
                for col in ws.columns:
                    max_len = 0
                    col_letter = get_column_letter(col[0].column)
                    for cell in col:
                        try:
                            v = "" if cell.value is None else str(cell.value)
                            max_len = max(max_len, len(v))
                        except Exception:
                            pass
                    ws.column_dimensions[col_letter].width = min(60, max(10, max_len + 2))

            # --- Summary
            ws = wb.active
            ws.title = "Summary"
            ws["A1"] = "Conduit Fill Calculation Report"
            ws["A1"].font = Font(bold=True, size=14)
            ws["A3"] = "Generated"
            ws["B3"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            row = 5
            summary_data = [
                ("Conduit Type", conduit_type),
                ("Trade Size", conduit_trade),
                ("Conduit Internal Area (mm²)", _safe_float(conduit_internal_area)),
                ("Number of Cables", n_cables_total),
                ("Total Cable Area (mm²)", _safe_float(total_cable_area)),
                ("Total Allowable Area (mm²)", _safe_float(conduit_allowed_area)),
                ("Actual Fill (%)", _safe_float(fill_pct * 100.0) if fill_pct else None),
            ]
            
            for param, val in summary_data:
                ws[f"A{row}"] = param
                ws[f"B{row}"] = val
                row += 1

            row += 1
            ok = total_cable_area <= conduit_allowed_area + 1e-9 if conduit_allowed_area else False
            ws[f"A{row}"] = "Compliance Status"
            ws[f"B{row}"] = "PASS: Within allowable fill" if ok else "FAIL: Exceeds allowable fill"
            autosize_ws(ws)

            # --- Cable Groups
            ws = wb.create_sheet("Cable Groups")
            try:
                show_df = edited.copy()
                cols_to_show = ["Name", "Table", "Construction", "Conductor size", "Conductors per cable", "Qty (cables)", "Area per cable (mm²)"]
                available_cols = [c for c in cols_to_show if c in show_df.columns]
                
                ws.append(available_cols)
                for cell in ws[1]:
                    cell.font = Font(bold=True)
                
                for _, row_data in show_df.iterrows():
                    row_vals = []
                    for col in available_cols:
                        val = row_data.get(col, None)
                        if isinstance(val, float):
                            row_vals.append(round(val, 2))
                        else:
                            row_vals.append(val)
                    ws.append(row_vals)
            except Exception:
                ws["A1"] = "Unable to load cable groups"

            autosize_ws(ws)

            bio = io.BytesIO()
            wb.save(bio)
            return bio.getvalue()

        # Export buttons
        can_export_cf = (
            conduit_internal_area is not None
            and total_cable_area is not None
            and n_cables_total > 0
        )

        exp_c1, exp_c2 = st.columns([1, 1], gap="large")
        with exp_c1:
            if st.button("Prepare Word report (.docx)", key="cf_build_docx"):
                try:
                    st.session_state["cf_docx_bytes"] = build_conduit_word_report()
                    st.success("Word report prepared. Use the download button below.")
                except Exception as e:
                    st.error(f"Failed to build Word report: {e}")

            docx_bytes_cf = st.session_state.get("cf_docx_bytes", None)
            st.download_button(
                "⬇️ Download Word report (.docx)",
                data=docx_bytes_cf if docx_bytes_cf else b"",
                file_name="Conduit_Fill_Report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                disabled=(not can_export_cf) or (docx_bytes_cf is None),
                key="cf_download_docx",
            )

        with exp_c2:
            if st.button("Prepare Excel report (.xlsx)", key="cf_build_xlsx"):
                try:
                    st.session_state["cf_xlsx_bytes"] = build_conduit_excel_report()
                    st.success("Excel report prepared. Use the download button below.")
                except Exception as e:
                    st.error(f"Failed to build Excel report: {e}")

            xlsx_bytes_cf = st.session_state.get("cf_xlsx_bytes", None)
            st.download_button(
                "⬇️ Download Excel report (.xlsx)",
                data=xlsx_bytes_cf if xlsx_bytes_cf else b"",
                file_name="Conduit_Fill_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                disabled=(not can_export_cf) or (xlsx_bytes_cf is None),
                key="cf_download_xlsx",
            )


# ============================
# 8) Cable Tray Ampacity
# ============================
elif page == "Cable Tray Ampacity":
    with theory_tab:
        header("Cable Tray Ampacity — Theory")
        show_code_note(code_mode)
        if code_mode == "OESC":
            render_md_safe("cable_tray_ampacity_oesc.md")
        else:
            render_md_safe("cable_tray_ampacity_nec.md")

    with calc_tab:
        header("Ampacity Derating Calculator", "Apply base ampacity and derating factors.")
        show_code_note(code_mode)

        base = st.number_input("Base ampacity (A)", min_value=0.1, value=200.0, step=1.0)
        grouping = st.number_input("Grouping factor", min_value=0.0, max_value=1.0, value=0.80, step=0.01)
        ambient = st.number_input("Ambient factor", min_value=0.0, max_value=1.50, value=1.00, step=0.01)

        adj = base * grouping * ambient
        st.success(f"Adjusted ampacity: **{fmt(adj, 'A')}**")

        st.markdown("### Equation used")
        eq(r"I_{adj}=I_{base}\cdot k_{group}\cdot k_{ambient}")


# ============================
# 9) Demand Load
# ============================
elif page == "Demand Load":
    with theory_tab:
        header("Demand Load — Theory")
        show_code_note(code_mode)
        if code_mode == "OESC":
            render_md_safe("demand_load_oesc.md")
        else:
            render_md_safe("demand_load_nec.md")

    with calc_tab:
        header("Demand Load Calculator", "Compute demand load from connected load and factor.")
        show_code_note(code_mode)

        connected = st.number_input("Connected load (kW)", min_value=0.0, value=120.0, step=1.0)
        factor = st.number_input("Demand factor (0–1)", min_value=0.0, max_value=1.0, value=0.65, step=0.01)
        demand = connected * factor
        st.success(f"Demand load: **{fmt(demand, 'kW')}**")

        st.markdown("### Equation used")
        eq(r"P_{demand}=P_{connected}\cdot f_{demand}")


# ============================
# 10) Power Factor Correction
# ============================
elif page == "Power Factor Correction":
    with theory_tab:
        header("Power Factor Correction — Theory")
        show_code_note(code_mode)
        if code_mode == "OESC":
            render_md_safe("power_factor_correction_oesc.md")
        else:
            render_md_safe("power_factor_correction_nec.md")

    with calc_tab:
        header("Power Factor Correction — Calculator")
        show_code_note(code_mode)
        st.info("Placeholder — content coming soon.")


# ============================
# Table Library (browse/search embedded OESC tables)
# ============================
elif page == "Table Library":

    # ---- NO TABS ON THIS PAGE ----
    header("Table Library — OESC Tables")
    show_code_note(code_mode)

    st.markdown(
        "Browse and search the embedded OESC tables included with this app. "
        "Tables are stored in **lib/oesc_tables.py** and exposed through a small registry API."
    )
    st.markdown(
        "- Use the search box to quickly filter by table number (e.g., `5A`) or keywords (e.g., `ampacity`, `conduit`).\n"
        "- A dash/blank entry in the source tables is shown as `—` (stored internally as `None`)."
    )

    st.divider()

    header("Table Lookup")

    if _TABLES_IMPORT_ERROR:
        st.error(
            "Table library failed to import. Confirm your repo has `lib/oesc_tables.py` and `lib/__init__.py`.\n\n"
            f"Import error: `{_TABLES_IMPORT_ERROR}`"
        )
    else:
        q = st.text_input(
            "Search tables",
            value="",
            placeholder="Examples: 1, 2, 5A, 9H, ampacity, conduit fill …",
        )

        table_ids = oesc_tables.search_tables(q)

        if not table_ids:
            st.warning("No tables match your search.")
        else:
            def _label(tid: str) -> str:
                meta = oesc_tables.get_table_meta(tid)
                title = meta.get("title") if meta else ""
                if title and title.lower().startswith("table"):
                    return title
                return f"Table {tid} — {title}" if title else f"Table {tid}"

            selected = st.selectbox(
                "Select a table",
                table_ids,
                format_func=_label,
            )

            meta = oesc_tables.get_table_meta(selected) or {}
            st.markdown(f"### {_label(selected)}")

            if meta.get("units"):
                st.caption(f"Units: **{meta['units']}**")

            df = oesc_tables.get_table_dataframe(selected)

            if df is None:
                st.info(
                    "This table is available in the library, but it is stored in a specialized structure "
                    "(raw format). Showing the raw object below."
                )
                st.json(meta.get("raw", {}))
            else:
                try:
                    st.dataframe(df, width="stretch", hide_index=True)
                except TypeError:
                    st.dataframe(df, width="stretch")

                # Download CSV
                if pd is not None and isinstance(df, pd.DataFrame):
                    csv_bytes = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "Download table as CSV",
                        data=csv_bytes,
                        file_name=f"oesc_table_{str(selected).lower()}.csv",
                        mime="text/csv",
                    )
                elif pd is not None:
                    csv_bytes = pd.DataFrame(df).to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "Download table as CSV",
                        data=csv_bytes,
                        file_name=f"oesc_table_{str(selected).lower()}.csv",
                        mime="text/csv",
                    )


# ============================
# 11) Voltage Drop  (FULL BLOCK — Table D3 expander always shown; f-list filtered for DC; size order matches Table D3)
# ============================
elif page == "Voltage Drop":
    with theory_tab:
        header("Voltage Drop — Theory")
        show_code_note(code_mode)
        if code_mode == "OESC":
            render_md_safe("voltage_drop_oesc.md")
        else:
            render_md_safe("voltage_drop_nec.md")

        # -------------------------------------------------
        # Display Table D3 reference tables
        # -------------------------------------------------
        with st.expander("📋 Show Table D3 reference values", expanded=False):
            st.markdown("### Copper Conductors — Table D3 (Ω/km)")

            display_cols = [
                "Size",
                "DC",
                "Cable 100%",
                "Cable 90%",
                "Cable 80%",
                "Raceway 100%",
                "Raceway 90%",
                "Raceway 80%",
            ]

            # Import from lib.oesc_tables
            from lib.oesc_tables import get_table_meta
            table_d3_meta = get_table_meta("D3")
            
            cu_rows_display = []
            al_rows_display = []
            
            if table_d3_meta:
                for row in table_d3_meta.get("rows", []):
                    size = row.get("size_awg_kcmil")
                    if size and size not in ["14"]:  # Skip non-copper sizes initially
                        cu_row = {
                            "Size": size,
                            "DC": row.get("copper_dc"),
                            "Cable 100%": row.get("copper_cable_100pf"),
                            "Cable 90%": row.get("copper_cable_90pf"),
                            "Cable 80%": row.get("copper_cable_80pf"),
                            "Raceway 100%": row.get("copper_raceway_100pf"),
                            "Raceway 90%": row.get("copper_raceway_90pf"),
                            "Raceway 80%": row.get("copper_raceway_80pf"),
                        }
                        cu_rows_display.append(cu_row)
                        
                        al_row = {
                            "Size": size,
                            "DC": row.get("aluminum_dc"),
                            "Cable 100%": row.get("aluminum_cable_100pf"),
                            "Cable 90%": row.get("aluminum_cable_90pf"),
                            "Cable 80%": row.get("aluminum_cable_80pf"),
                            "Raceway 100%": row.get("aluminum_raceway_100pf"),
                            "Raceway 90%": row.get("aluminum_raceway_90pf"),
                            "Raceway 80%": row.get("aluminum_raceway_80pf"),
                        }
                        al_rows_display.append(al_row)
                    elif size == "14":  # Don't add non-aluminum row
                        cu_row = {
                            "Size": size,
                            "DC": row.get("copper_dc"),
                            "Cable 100%": row.get("copper_cable_100pf"),
                            "Cable 90%": row.get("copper_cable_90pf"),
                            "Cable 80%": row.get("copper_cable_80pf"),
                            "Raceway 100%": row.get("copper_raceway_100pf"),
                            "Raceway 90%": row.get("copper_raceway_90pf"),
                            "Raceway 80%": row.get("copper_raceway_80pf"),
                        }
                        cu_rows_display.append(cu_row)

            if pd is not None:
                df_cu = pd.DataFrame(cu_rows_display, columns=display_cols)
                st.dataframe(df_cu, width="stretch", hide_index=True)
            else:
                st.dataframe(cu_rows_display, width="stretch", hide_index=True)

            st.markdown("### Aluminum Conductors — Table D3 (Ω/km)")
            
            if pd is not None:
                df_al = pd.DataFrame(al_rows_display, columns=display_cols)
                st.dataframe(df_al, width="stretch", hide_index=True)
            else:
                st.dataframe(al_rows_display, width="stretch", hide_index=True)

            st.caption(
                "These tables are from OESC Appendix D – Table D3 "
                "(75 °C conductors). Values are in Ω per circuit kilometre."
            )

        # -------------------------------------------------
        # Display the System Factor (f) lookup table
        # -------------------------------------------------
        with st.expander("📐 Show system factor (f) reference table", expanded=False):
            st.markdown("### System factor (f) — reference table (from Appendix D)")
            
            system_factor_data = [
                {"System / Connection": "DC — 2-wire (positive-to-negative)", "f (used in formula)": 2.0, "Voltage reference": "Positive-to-negative"},
                {"System / Connection": "DC — 2-wire (positive-to-ground)", "f (used in formula)": 2.0, "Voltage reference": "Positive-to-ground"},
                {"System / Connection": "DC — 2-wire (negative-to-ground)", "f (used in formula)": 2.0, "Voltage reference": "Negative-to-ground"},
                {"System / Connection": "DC — 3-wire, line-to-line with grounded conductor", "f (used in formula)": 2.0, "Voltage reference": "Line-to-line"},
                {"System / Connection": "1-φ AC — 2-wire, line-to-grounded conductor", "f (used in formula)": 2.0, "Voltage reference": "Line-to-ground"},
                {"System / Connection": "1-φ AC — 2-wire, line-to-line", "f (used in formula)": 2.0, "Voltage reference": "Line-to-line"},
                {"System / Connection": "1-φ AC — 3-wire, line-to-line, with grounded conductor", "f (used in formula)": 2.0, "Voltage reference": "Line-to-line"},
                {"System / Connection": "3-φ AC — 2-wire, line-to-grounded conductor", "f (used in formula)": 2.0, "Voltage reference": "Line-to-ground"},
                {"System / Connection": "3-φ AC — 2-wire, line-to-line, no grounded conductor", "f (used in formula)": 2.0, "Voltage reference": "Line-to-line"},
                {"System / Connection": "3-φ AC — 3-wire, line-to-line with grounded conductor", "f (used in formula)": 2.0, "Voltage reference": "Line-to-line"},
                {"System / Connection": "3-φ AC — 3-wire, line-to-grounded conductor", "f (used in formula)": 2.0, "Voltage reference": "Line-to-ground"},
                {"System / Connection": "3-φ AC — 3-wire, line-to-line, no grounded conductor", "f (used in formula)": math.sqrt(3), "Voltage reference": "Line-to-line"},
                {"System / Connection": "3-φ AC — 4-wire, line-to-line, with grounded conductor", "f (used in formula)": math.sqrt(3), "Voltage reference": "Line-to-line"},
            ]
            
            if pd is not None:
                df_f = pd.DataFrame(system_factor_data)
                st.dataframe(df_f, width="stretch", hide_index=True)
            else:
                for r in system_factor_data:
                    st.write(f"- **{r['System / Connection']}** — f = {r['f (used in formula)']} — {r['Voltage reference']}")

            st.caption(
                "Notes: The 'Voltage reference' column shows whether the VD is line-to-line or line-to-ground for that circuit type. "
                "f = √3 ≈ 1.732 for 3-phase line-to-line measurements."
            )

    with calc_tab:
        header("Voltage Drop Calculator — Table D3 (OESC) + k-value helper")
        show_code_note(code_mode)

        # --------------------------
        # Exact Table D3 embedded (from supplied images)
        # --------------------------
        TABLE_D3 = {
            "Copper": {
                "14":  {"DC":10.2,"Cable 100%":10.2,"Cable 90%":9.92,"Cable 80%":9.67,"Raceway 90%":10.0,"Raceway 80%":9.67},
                "12":  {"DC":6.38,"Cable 100%":6.38,"Cable 90%":6.25,"Cable 80%":6.10,"Raceway 90%":6.26,"Raceway 80%":6.11},
                "10":  {"DC":4.03,"Cable 100%":4.03,"Cable 90%":3.96,"Cable 80%":3.87,"Raceway 90%":3.96,"Raceway 80%":3.87},
                "8":   {"DC":2.54,"Cable 100%":2.54,"Cable 90%":2.50,"Cable 80%":2.45,"Raceway 90%":2.51,"Raceway 80%":2.45},
                "6":   {"DC":1.59,"Cable 100%":1.59,"Cable 90%":1.58,"Cable 80%":1.55,"Raceway 90%":1.58,"Raceway 80%":1.55},
                "4":   {"DC":1.01,"Cable 100%":1.01,"Cable 90%":1.01,"Cable 80%":0.987,"Raceway 90%":1.01,"Raceway 80%":1.00},
                "3":   {"DC":0.792,"Cable 100%":0.792,"Cable 90%":0.797,"Cable 80%":0.787,"Raceway 90%":0.801,"Raceway 80%":0.792},
                "2":   {"DC":0.626,"Cable 100%":0.627,"Cable 90%":0.636,"Cable 80%":0.629,"Raceway 90%":0.639,"Raceway 80%":0.635},
                "1":   {"DC":0.50,"Cable 100%":0.50,"Cable 90%":0.512,"Cable 80%":0.509,"Raceway 90%":0.516,"Raceway 80%":0.515},
                "1/0": {"DC":0.395,"Cable 100%":0.396,"Cable 90%":0.410,"Cable 80%":0.409,"Raceway 90%":0.414,"Raceway 80%":0.415},
                "2/0": {"DC":0.314,"Cable 100%":0.316,"Cable 90%":0.331,"Cable 80%":0.332,"Raceway 90%":0.335,"Raceway 80%":0.338},
                "3/0": {"DC":0.249,"Cable 100%":0.251,"Cable 90%":0.267,"Cable 80%":0.270,"Raceway 90%":0.271,"Raceway 80%":0.275},
                "4/0": {"DC":0.197,"Cable 100%":0.200,"Cable 90%":0.217,"Cable 80%":0.221,"Raceway 90%":0.221,"Raceway 80%":0.226},
                "250": {"DC":0.167,"Cable 100%":0.171,"Cable 90%":0.188,"Cable 80%":0.193,"Raceway 90%":0.192,"Raceway 80%":0.198},
                "300": {"DC":0.140,"Cable 100%":0.144,"Cable 90%":0.162,"Cable 80%":0.167,"Raceway 90%":0.166,"Raceway 80%":0.172},
                "350": {"DC":0.120,"Cable 100%":0.125,"Cable 90%":0.143,"Cable 80%":0.148,"Raceway 90%":0.147,"Raceway 80%":0.154},
                "400": {"DC":0.105,"Cable 100%":0.111,"Cable 90%":0.129,"Cable 80%":0.135,"Raceway 90%":0.133,"Raceway 80%":0.140},
                "500": {"DC":0.0836,"Cable 100%":0.0912,"Cable 90%":0.110,"Cable 80%":0.116,"Raceway 90%":0.114,"Raceway 80%":0.121},
                "600": {"DC":0.0697,"Cable 100%":0.0785,"Cable 90%":0.0969,"Cable 80%":0.104,"Raceway 90%":0.101,"Raceway 80%":0.109},
                "750": {"DC":0.0558,"Cable 100%":0.0668,"Cable 90%":0.0850,"Cable 80%":0.0915,"Raceway 90%":0.0889,"Raceway 80%":0.097},
                "1000":{"DC":0.0417,"Cable 100%":0.0558,"Cable 90%":0.0739,"Cable 80%":0.0805,"Raceway 90%":0.0778,"Raceway 80%":0.086},
            },
            "Aluminum": {
                "12":  {"DC":10.5,"Cable 100%":10.5,"Cable 90%":10.3,"Cable 80%":10.0,"Raceway 90%":10.3,"Raceway 80%":9.99},
                "10":  {"DC":6.58,"Cable 100%":6.58,"Cable 90%":6.44,"Cable 80%":6.28,"Raceway 90%":6.45,"Raceway 80%":6.29},
                "8":   {"DC":4.14,"Cable 100%":4.14,"Cable 90%":4.07,"Cable 80%":3.97,"Raceway 90%":4.07,"Raceway 80%":3.98},
                "6":   {"DC":2.62,"Cable 100%":2.62,"Cable 90%":2.58,"Cable 80%":2.52,"Raceway 90%":2.58,"Raceway 80%":2.53},
                "4":   {"DC":1.65,"Cable 100%":1.65,"Cable 90%":1.63,"Cable 80%":1.60,"Raceway 90%":1.64,"Raceway 80%":1.61},
                "3":   {"DC":1.30,"Cable 100%":1.31,"Cable 90%":1.30,"Cable 80%":1.27,"Raceway 90%":1.30,"Raceway 80%":1.28},
                "2":   {"DC":1.04,"Cable 100%":1.04,"Cable 90%":1.04,"Cable 80%":1.02,"Raceway 90%":1.04,"Raceway 80%":1.03},
                "1":   {"DC":0.82,"Cable 100%":0.82,"Cable 90%":0.823,"Cable 80%":0.812,"Raceway 90%":0.827,"Raceway 80%":0.818},
                "1/0": {"DC":0.651,"Cable 100%":0.652,"Cable 90%":0.659,"Cable 80%":0.652,"Raceway 90%":0.663,"Raceway 80%":0.657},
                "2/0": {"DC":0.516,"Cable 100%":0.517,"Cable 90%":0.526,"Cable 80%":0.522,"Raceway 90%":0.530,"Raceway 80%":0.528},
                "3/0": {"DC":0.408,"Cable 100%":0.409,"Cable 90%":0.420,"Cable 80%":0.419,"Raceway 90%":0.424,"Raceway 80%":0.425},
                "4/0": {"DC":0.326,"Cable 100%":0.327,"Cable 90%":0.341,"Cable 80%":0.341,"Raceway 90%":0.345,"Raceway 80%":0.347},
                "250": {"DC":0.275,"Cable 100%":0.277,"Cable 90%":0.291,"Cable 80%":0.293,"Raceway 90%":0.295,"Raceway 80%":0.299},
                "300": {"DC":0.229,"Cable 100%":0.231,"Cable 90%":0.247,"Cable 80%":0.249,"Raceway 90%":0.250,"Raceway 80%":0.255},
                "350": {"DC":0.196,"Cable 100%":0.199,"Cable 90%":0.215,"Cable 80%":0.218,"Raceway 90%":0.219,"Raceway 80%":0.224},
                "400": {"DC":0.172,"Cable 100%":0.175,"Cable 90%":0.191,"Cable 80%":0.195,"Raceway 90%":0.195,"Raceway 80%":0.201},
                "500": {"DC":0.138,"Cable 100%":0.141,"Cable 90%":0.158,"Cable 80%":0.163,"Raceway 90%":0.162,"Raceway 80%":0.168},
                "600": {"DC":0.115,"Cable 100%":0.119,"Cable 90%":0.136,"Cable 80%":0.142,"Raceway 90%":0.140,"Raceway 80%":0.147},
                "750": {"DC":0.0916,"Cable 100%":0.0968,"Cable 90%":0.115,"Cable 80%":0.121,"Raceway 90%":0.119,"Raceway 80%":0.126},
                "1000":{"DC":0.0686,"Cable 100%":0.0758,"Cable 90%":0.0933,"Cable 80%":0.0994,"Raceway 90%":0.0973,"Raceway 80%":0.105},
            },
        }

        # --------------------------
        # Ensure "Raceway 100%" exists and equals "Cable 100%" where appropriate
        # --------------------------
        for mat_key, sizes_dict in TABLE_D3.items():
            for size_key, cols in sizes_dict.items():
                if "Cable 100%" in cols and "Raceway 100%" not in cols:
                    cols["Raceway 100%"] = cols["Cable 100%"]

        # ---------------- Inputs
        k_mode = st.radio(
            "k-value input mode",
            ("Lookup k-value from Table D3 (recommended)", "Manual k-value (enter value)"),
            index=0,
            key="vd_k_mode",
        )
        use_table = k_mode.startswith("Lookup")

        c1, c2, c3, c4 = st.columns([1,1,1,1], gap="large")
        with c1:
            I = st.number_input("Load current (A)", min_value=0.0, value=50.0, step=0.1, key="vd_I")
        with c2:
            L_m = st.number_input("One-way length (m)", min_value=0.0, value=80.0, step=1.0, key="vd_Lm")
        with c3:
            V_nom = st.number_input("Nominal voltage (V)", min_value=1.0, value=600.0, step=1.0, key="vd_Vnom")
        with c4:
            n_parallel_vd = st.number_input(
                "Parallel conductors per phase/pole",
                min_value=1,
                value=1,
                step=1,
                key="vd_n_parallel",
            )

        if use_table:
            mat = st.selectbox("Conductor material (table to use)", ["Copper", "Aluminum"], index=0, key="vd_mat")
            location = st.selectbox("Installation (table column family)", ["Cable", "Raceway", "DC"], index=0, key="vd_location")

            if location != "DC":
                pf_choice = st.selectbox("Power-factor column (for Cable/Raceway)", ["100% pf", "90% pf", "80% pf"], index=0, key="vd_pf")
            else:
                pf_choice = "100% pf"
                st.caption("Power-factor selection hidden for DC — DC uses the 'DC' column in Table D3.")

            # ✅ keep conductor sizes in the same order as Table D3 (dict insertion order)
            sizes = list(TABLE_D3[mat].keys())

            # pick a stable default index (prefer 1000 if present for Copper, else first entry)
            default_size_index = 0
            try:
                if mat == "Copper" and "1000" in sizes:
                    default_size_index = sizes.index("1000")
            except Exception:
                default_size_index = 0

            size = st.selectbox(
                "Select conductor size (Table D3)",
                sizes,
                index=default_size_index,
                key="vd_size",
            )
        else:
            st.caption("Manual k-value mode: table lookup controls are hidden. Enter k directly in Ω/km below.")
            mat = None
            location = None
            pf_choice = "100% pf"
            size = None

        operating_temp_c = st.selectbox(
            "Conductor operating temperature (°C)",
            [60, 75, 90],
            index=1,
            format_func=lambda t: f"{t}°C",
            key="vd_operating_temp_c",
        )
        temp_multiplier_map = {60: 0.95, 75: 1.00, 90: 1.05}
        k_temp_multiplier = temp_multiplier_map.get(int(operating_temp_c), 1.00)

        if not use_table:
            k_base = st.number_input(
                "Manual k-value (Ω/km)",
                min_value=0.0,
                value=0.10,
                step=0.00001,
                format="%.6f",
                key="vd_k_manual_only",
            )
            selected_col_suffix = "Manual"
        else:
            pf_short = pf_choice.split()[0] if isinstance(pf_choice, str) else str(pf_choice)

            if location == "DC":
                candidates = ["DC"]
            else:
                primary = f"{location} {pf_short}"
                alt1 = f"{location} {pf_short} pf"
                alt2 = f"{location} {pf_short.replace('%','')}"
                candidates = [primary, alt1, alt2]

            table_entry = TABLE_D3[mat].get(size, {}) if mat is not None and size is not None else {}
            k_found = None
            found_key = None

            for c in candidates:
                if c in table_entry:
                    k_found = table_entry[c]
                    found_key = c
                    break

            if k_found is None and table_entry:
                pf_numeric = pf_short.replace('%','')
                for colname in table_entry.keys():
                    low = colname.lower()
                    if location is not None and location.lower() in low and pf_numeric in low:
                        k_found = table_entry[colname]
                        found_key = colname
                        break

            if k_found is None:
                available = ", ".join(list(table_entry.keys())) if table_entry else "(no table available)"
                st.error(
                    f"Table value not found for {mat} {size} / {location} {pf_short}. "
                    f"Available columns for this size: {available}"
                )
                k_base = None
                selected_col_suffix = None
            else:
                k_base = float(k_found)
                selected_col_suffix = found_key
                st.caption(
                    f"Table D3 base k-value selected for {mat} {size} ({selected_col_suffix}): "
                    f"**{k_base} Ω/km** at 75°C reference."
                )

        k_used = (k_base * k_temp_multiplier) if k_base is not None else None
        if k_base is not None:
            st.caption(
                f"Temperature-adjusted k-value: **{k_used:.6g} Ω/km** "
                f"(base {k_base:.6g} x {k_temp_multiplier:.2f} for {operating_temp_c}°C)."
            )

        # --------------------------
        # f-factor options (used in both table + manual modes)
        # NOTE: filter to DC-only list ONLY when installation is DC.
        # --------------------------
        # When manual k-value mode is active, "location" is None, so we show the full list (as before).
        if I <= 0 or L_m <= 0 or V_nom <= 0 or k_used is None:
            st.warning("Enter positive values and ensure a k-value is selected to compute voltage drop.")
            f_choice = None
            f = None
            f_label = None
            I_eff = None
            Vd = None
            pct = None
        else:
            if location == "DC":
                f_options = [
                    ("DC — 2-wire, positive-to-negative (VD line-to-line)", 2.0),
                    ("DC — 2-wire, positive-to-ground (VD line-to-ground)", 2.0),
                    ("DC — 2-wire, negative-to-ground (VD line-to-ground)", 2.0),
                    ("DC — 3-wire, line-to-line with grounded conductor (VD line-to-line)", 2.0),
                ]
                default_f_index = 0
            else:
                f_options = [
                    ("DC — 2-wire, positive-to-negative (VD line-to-line)", 2.0),
                    ("DC — 2-wire, positive-to-ground (VD line-to-ground)", 2.0),
                    ("DC — 2-wire, negative-to-ground (VD line-to-ground)", 2.0),
                    ("DC — 3-wire, line-to-line with grounded conductor (VD line-to-line)", 2.0),
                    ("1-φ AC — 2-wire, line-to-grounded conductor (VD line-to-ground)", 2.0),
                    ("1-φ AC — 2-wire, line-to-line (VD line-to-line)", 2.0),
                    ("1-φ AC — 3-wire, line-to-line, with grounded conductor (VD line-to-line)", 2.0),
                    ("3-φ AC — 2-wire, line-to-grounded conductor (VD line-to-ground)", 2.0),
                    ("3-φ AC — 2-wire, line-to-line, no grounded conductor (VD line-to-line)", 2.0),
                    ("3-φ AC — 3-wire, line-to-line, with grounded conductor (VD line-to-line)", 2.0),
                    ("3-φ AC — 3-wire, line-to-grounded conductor (VD line-to-ground)", 2.0),
                    ("3-φ AC — 3-wire, line-to-line, no grounded conductor (VD line-to-line)", math.sqrt(3)),
                    ("3-φ AC — 4-wire, line-to-line, with grounded conductor (VD line-to-line)", math.sqrt(3)),
                ]
                default_f_index = 4 if len(f_options) > 4 else 0

            f_choice = st.selectbox(
                "Voltage-drop factor (f) — select circuit type",
                f_options,
                format_func=lambda x: x[0],
                index=default_f_index,
                key="vd_f_choice_full",
            )
            f = float(f_choice[1])
            f_label = f_choice[0]
            st.caption(f"Selected circuit type: **{f_label}** → f = **{f:.6g}** (used in formula \\(V_D = k f I_{{eff}} L / 1000\\)).")

            I_eff = safe_div(I, n_parallel_vd) if n_parallel_vd else None
            Vd = (k_used * f * I_eff * L_m) / 1000.0 if I_eff is not None else None
            pct = (Vd / V_nom) * 100.0

            m1, m2 = st.columns(2)
            m1.metric("Estimated voltage drop", fmt(Vd, "V"))
            m2.metric("Voltage drop (%)", fmt(pct, "%"))

            st.markdown("### Parameters used")
            if use_table:
                st.write(
                    f"- k-value base (75°C Table D3): **{k_base:.6g} Ω/km** "
                    f"(column **{selected_col_suffix}**)"
                )
            else:
                st.write(f"- k-value base (manual): **{k_base:.6g} Ω/km**")
            st.write(
                f"- Operating temperature = **{operating_temp_c}°C** "
                f"→ k multiplier = **{k_temp_multiplier:.2f}**"
            )
            st.write(f"- k-value used in calc: **{k_used:.6g} Ω/km**")
            st.write(f"- factor f: **{f:.6g}** (selected: {f_label})")
            st.write(f"- I (load) = **{fmt(I, 'A')}**, L = **{fmt(L_m, 'm')}**, V_nom = **{fmt(V_nom, 'V')}**")
            st.write(f"- Parallel conductors = **{n_parallel_vd}** → I per conductor = **{fmt(I_eff, 'A')}**")

            st.markdown("### Equation used")
            eq(r"I_{eff}=\frac{I}{N_{parallel}}")
            eq(r"V_D=\frac{k\cdot f\cdot I_{eff}\cdot L}{1000}")
            eq(r"\%\Delta V = 100\cdot\frac{V_D}{V_{nom}}")

        st.caption(
            "Notes: Table D3 values are transcribed exactly from the supplied images (cable vs raceway and pf columns). "
            "Manual mode uses your entered k as the 75°C base value before the operating-temperature multiplier is applied."
        )

        # -------------------------------------------------
        # NEW FEATURE: Download a Word report or Excel report
        # Includes: equations, assumptions, variables, constants, selected inputs, results, and full used tables.
        # -------------------------------------------------
        st.markdown("### 📄 Export calculation report")

        assumptions = [
            "Uses OESC Table D3 k-values in Ω per circuit kilometre as 75°C base values when Table mode is selected.",
            "Applies an operating-temperature multiplier to k: 60°C → 0.95, 75°C → 1.00, 90°C → 1.05.",
            "Uses voltage-drop factor f from the Appendix D system factor list.",
            "Uses one-way length L (m) directly in the formula; table equation divides by 1000 to convert m → km.",
            "If parallel conductors are used, current is divided by N_parallel (per conductor) for the VD calc.",
            "Percent voltage drop is computed against nominal voltage V_nom.",
        ]

        constants = [
            {"Name": "1000", "Meaning": "m per km (unit conversion for L)", "Value": 1000},
            {"Name": "√3", "Meaning": "Three-phase factor for specific circuit types per table note", "Value": float(math.sqrt(3))},
        ]

        inputs = [
            {"Name": "Conductor material", "Value": mat},
            {"Name": "Installation type", "Value": location},
            {"Name": "Operating temperature (°C)", "Value": operating_temp_c},
            {"Name": "Load current (A)", "Value": I},
            {"Name": "One way length (m)", "Value": L_m},
            {"Name": "Nominal Voltage (V)", "Value": V_nom},
            {"Name": "Parallel conductors per phase/pole", "Value": n_parallel_vd},
            {"Name": "Power Factor Column", "Value": pf_choice},
            {"Name": "Conductor size (Table D3)", "Value": size},
            {"Name": "Selected Table D3 Column", "Value": selected_col_suffix},
        ]

        variables = [
            {"Symbol": "k_base", "Description": "Base voltage-drop factor at 75°C (Ω/km)", "Value": k_base},
            {"Symbol": "k_mult", "Description": "Operating-temperature multiplier applied to k_base", "Value": k_temp_multiplier},
            {"Symbol": "f-factor option", "Description": "System/connection factor from Appendix D", "Value": f_label},
            {"Symbol": "k", "Description": "Adjusted voltage-drop factor used in calculation (Ω/km)", "Value": k_used},
            {"Symbol": "f", "Description": "System/connection factor from Appendix D", "Value": f},
            {"Symbol": "I_eff", "Description": "Current per conductor used in VD calc (A)", "Value": I_eff},
            {"Symbol": "V_D", "Description": "Estimated voltage drop (V)", "Value": Vd},
            {"Symbol": "%ΔV", "Description": "Voltage drop percent (%)", "Value": pct},
        ]

        equations_text = [
            ("Effective current", r"I_{eff}=\frac{I}{N_{parallel}}"),
            ("Voltage drop", r"V_D=\frac{k\cdot f\cdot I_{eff}\cdot L}{1000}"),
            ("Percent drop", r"\%\Delta V = 100\cdot\frac{V_D}{V_{nom}}"),
        ]

        # f-factor reference (full) used in expander below; also exported
        f_table_rows = [
            {"System / Connection": "DC — 2-wire (positive-to-negative)", "f (used in formula)": 2.0, "Voltage reference": "Positive-to-negative"},
            {"System / Connection": "DC — 2-wire (positive-to-ground)", "f (used in formula)": 2.0, "Voltage reference": "Positive-to-ground"},
            {"System / Connection": "DC — 2-wire (negative-to-ground)", "f (used in formula)": 2.0, "Voltage reference": "Negative-to-ground"},
            {"System / Connection": "DC — 3-wire, line-to-line with grounded conductor", "f (used in formula)": 2.0, "Voltage reference": "Line-to-line"},
            {"System / Connection": "1-φ AC — 2-wire, line-to-grounded conductor", "f (used in formula)": 2.0, "Voltage reference": "Line-to-ground"},
            {"System / Connection": "1-φ AC — 2-wire, line-to-line", "f (used in formula)": 2.0, "Voltage reference": "Line-to-line"},
            {"System / Connection": "1-φ AC — 3-wire, line-to-line, with grounded conductor", "f (used in formula)": 2.0, "Voltage reference": "Line-to-line"},
            {"System / Connection": "3-φ AC — 2-wire, line-to-grounded conductor", "f (used in formula)": 2.0, "Voltage reference": "Line-to-ground"},
            {"System / Connection": "3-φ AC — 2-wire, line-to-line, no grounded conductor", "f (used in formula)": 2.0, "Voltage reference": "Line-to-line"},
            {"System / Connection": "3-φ AC — 3-wire, line-to-line with grounded conductor", "f (used in formula)": 2.0, "Voltage reference": "Line-to-line"},
            {"System / Connection": "3-φ AC — 3-wire, line-to-grounded conductor", "f (used in formula)": 2.0, "Voltage reference": "Line-to-ground"},
            {"System / Connection": "3-φ AC — 3-wire, line-to-line, no grounded conductor", "f (used in formula)": math.sqrt(3), "Voltage reference": "Line-to-line"},
            {"System / Connection": "3-φ AC — 4-wire, line-to-line, with grounded conductor", "f (used in formula)": math.sqrt(3), "Voltage reference": "Line-to-line"},
        ]

        # Build the DataFrame-ish rows for export (same columns you display)
        display_cols = [
            "Size",
            "DC",
            "Cable 100%",
            "Cable 90%",
            "Cable 80%",
            "Raceway 100%",
            "Raceway 90%",
            "Raceway 80%",
        ]
        cu_rows = []
        for size_key, cols in TABLE_D3["Copper"].items():
            cu_rows.append({
                "Size": size_key,
                "DC": cols.get("DC", None),
                "Cable 100%": cols.get("Cable 100%", None),
                "Cable 90%": cols.get("Cable 90%", None),
                "Cable 80%": cols.get("Cable 80%", None),
                "Raceway 100%": cols.get("Raceway 100%", None),
                "Raceway 90%": cols.get("Raceway 90%", None),
                "Raceway 80%": cols.get("Raceway 80%", None),
            })
        al_rows = []
        for size_key, cols in TABLE_D3["Aluminum"].items():
            al_rows.append({
                "Size": size_key,
                "DC": cols.get("DC", None),
                "Cable 100%": cols.get("Cable 100%", None),
                "Cable 90%": cols.get("Cable 90%", None),
                "Cable 80%": cols.get("Cable 80%", None),
                "Raceway 100%": cols.get("Raceway 100%", None),
                "Raceway 90%": cols.get("Raceway 90%", None),
                "Raceway 80%": cols.get("Raceway 80%", None),
            })

        def _safe_float(x):
            try:
                return None if x is None else float(x)
            except Exception:
                return None

        # ✅ FIX: safe formatter for Word tables (prevents "Unknown format code 'g' for object of type 'str'")
        def _cell_text(val):
            """Safe text for Word/Excel cells: format numbers, otherwise stringify."""
            if val is None:
                return "—"
            if isinstance(val, (int, float)):
                return f"{val:g}"
            # try numeric conversion for numeric-looking strings
            try:
                fval = float(val)
                return f"{fval:g}"
            except Exception:
                return str(val)
            
        # ----------------------------
        # Voltage drop report generation
        # ----------------------------
        OMML_EQUATIONS = {
            r"I_{eff}=\frac{I}{N_{parallel}}": r"""
        <m:sSub>
            <m:e><m:r><m:t>I</m:t></m:r></m:e>
            <m:sub><m:r><m:t>eff</m:t></m:r></m:sub>
        </m:sSub>
        <m:r><m:t xml:space="preserve"> = </m:t></m:r>
        <m:f>
            <m:num><m:r><m:t>I</m:t></m:r></m:num>
            <m:den>
                <m:sSub>
                    <m:e><m:r><m:t>N</m:t></m:r></m:e>
                    <m:sub><m:r><m:t>parallel</m:t></m:r></m:sub>
                </m:sSub>
            </m:den>
        </m:f>
        """,
            r"V_D=\frac{k\cdot f\cdot I_{eff}\cdot L}{1000}": r"""
        <m:sSub>
            <m:e><m:r><m:t>V</m:t></m:r></m:e>
            <m:sub><m:r><m:t>D</m:t></m:r></m:sub>
        </m:sSub>
        <m:r><m:t xml:space="preserve"> = </m:t></m:r>
        <m:f>
            <m:num>
                <m:r><m:t>k</m:t></m:r>
                <m:r><m:t xml:space="preserve"> · </m:t></m:r>
                <m:r><m:t>f</m:t></m:r>
                <m:r><m:t xml:space="preserve"> · </m:t></m:r>
                <m:sSub>
                    <m:e><m:r><m:t>I</m:t></m:r></m:e>
                    <m:sub><m:r><m:t>eff</m:t></m:r></m:sub>
                </m:sSub>
                <m:r><m:t xml:space="preserve"> · </m:t></m:r>
                <m:r><m:t>L</m:t></m:r>
            </m:num>
        <m:den><m:r><m:t>1000</m:t></m:r></m:den>
        </m:f>
        """,
            r"\%\Delta V = 100\cdot\frac{V_D}{V_{nom}}": r"""
        <m:r><m:t>%ΔV</m:t></m:r>
        <m:r><m:t xml:space="preserve"> = </m:t></m:r>
        <m:r><m:t>100</m:t></m:r>
        <m:r><m:t xml:space="preserve"> · </m:t></m:r>
        <m:f>
            <m:num>
                <m:sSub>
                    <m:e><m:r><m:t>V</m:t></m:r></m:e>
                    <m:sub><m:r><m:t>D</m:t></m:r></m:sub>
                </m:sSub>
            </m:num>
            <m:den>
                <m:sSub>
                    <m:e><m:r><m:t>V</m:t></m:r></m:e>
                    <m:sub><m:r><m:t>nom</m:t></m:r></m:sub>
                </m:sSub>
            </m:den>
        </m:f>
        """,
        }


        def build_vd_word_report():

            doc = Document("content/files/Template.docx")

            remove_leading_blank_paragraphs(doc)

            table = doc.sections[0].header.tables[0]

            append_to_value_line(table.cell(0, 3), PROJECT_NUMBER)
            append_to_value_line(table.cell(0, 4), "#")
            append_to_value_line(table.cell(2, 3), DESIGNER_NAME)
            append_to_value_line(table.cell(2, 4), datetime.now().strftime("%m/%d/%Y"))
            append_to_value_line(table.cell(3, 3), "")
            append_to_value_line(table.cell(3, 4), "")
            append_to_value_line(table.cell(3, 2), "Voltage Drop Calculation Report")


            # -------------------------
            # Equations
            # -------------------------
            doc.add_heading("Equations", level=1)

            for title, equation in equations_text:
                p = doc.add_paragraph()
                p.add_run(f"{title}: ").bold = True

                omml = OMML_EQUATIONS.get(equation)
                if omml is not None:
                    add_omml_equation_to_paragraph(p, omml)
                else:
                    # fallback if you add more equations later
                    p.add_run(equation)


            # -------------------------
            # Assumptions
            # -------------------------
            doc.add_heading("Assumptions", level=1)

            for a in assumptions:
                doc.add_paragraph(a, style="CalcBullet")


            # -------------------------
            # Inputs
            # -------------------------
            doc.add_heading("Inputs", level=1)

            t_inputs = doc.add_table(rows=1, cols=2)
            hdr = t_inputs.rows[0].cells
            p = hdr[0].paragraphs[0]
            p.clear()
            r = p.add_run("Parameter")
            r.bold = True
            p = hdr[1].paragraphs[0]
            p.clear()
            r = p.add_run("Value")
            r.bold = True

            for inp in inputs:
                row = t_inputs.add_row().cells
                row[0].text = str(inp["Name"])
                row[1].text = _cell_text(inp["Value"])

            set_table_borders(t_inputs)

            # -------------------------
            # Variables
            # -------------------------
            doc.add_heading("Variables", level=1)

            t = doc.add_table(rows=1, cols=3)
            hdr = t.rows[0].cells
            p = hdr[0].paragraphs[0]
            p.clear()
            r = p.add_run("Symbol")
            r.bold = True
            p = hdr[1].paragraphs[0]
            p.clear()
            r = p.add_run("Description")
            r.bold = True
            p = hdr[2].paragraphs[0]
            p.clear()
            r = p.add_run("Value")
            r.bold = True

            for v in variables:
                row = t.add_row().cells
                row[0].text = str(v["Symbol"])
                row[1].text = str(v["Description"])
                val = v["Value"]
                try:
                    row[2].text = "—" if val is None else f"{float(val):.6g}"
                except Exception:
                    row[2].text = "—" if val is None else str(val)

            set_table_borders(t)

            # -------------------------
            # Constants
            # -------------------------
            doc.add_heading("Constants", level=1)

            tc = doc.add_table(rows=1, cols=3)
            hdr = tc.rows[0].cells
            p = hdr[0].paragraphs[0]
            p.clear()
            r = p.add_run("Name")
            r.bold = True
            p = hdr[1].paragraphs[0]
            p.clear()
            r = p.add_run("Meaning")
            r.bold = True
            p = hdr[2].paragraphs[0]
            p.clear()
            r = p.add_run("Value")
            r.bold = True

            for c in constants:
                row = tc.add_row().cells
                row[0].text = str(c["Name"])
                row[1].text = str(c["Meaning"])
                try:
                    row[2].text = f'{float(c["Value"]):.6g}'
                except Exception:
                    row[2].text = str(c["Value"])
            
            set_table_borders(tc)

            # -------------------------
            # Return Bytes
            # -------------------------
            bio = io.BytesIO()
            doc.save(bio)
            return bio.getvalue()


        def build_vd_excel_report():

            wb = Workbook()

            def autosize(ws):
                for col in ws.columns:
                    max_len = 0
                    col_letter = get_column_letter(col[0].column)
                    for cell in col:
                        try:
                            v = "" if cell.value is None else str(cell.value)
                            max_len = max(max_len, len(v))
                        except Exception:
                            pass
                    ws.column_dimensions[col_letter].width = min(60, max(10, max_len + 2))

            # --- Summary
            ws = wb.active
            ws.title = "Summary"
            ws["A1"] = "Voltage Drop Calculation Report"
            ws["A1"].font = Font(bold=True, size=14)
            ws["A3"] = "Generated"
            ws["B3"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ws["A4"] = "k-mode"
            ws["B4"] = k_mode

            row = 6
            if use_table:
                summary_pairs = [
                    ("Conductor operating temperature (°C)", operating_temp_c),
                    ("k multiplier", f"{k_temp_multiplier:.2f}"),
                    ("Parallel conductors per phase/pole", n_parallel_vd),
                    ("Material", mat),
                    ("Installation", location),
                    ("Power factor column", pf_choice if location != "DC" else "(N/A — DC)"),
                    ("Conductor size", size),
                    ("Selected Table D3 column", selected_col_suffix),
                    ("Base k-value (75°C) (Ω/km)", f"{k_base:.6g}"),
                    ("Adjusted k-value used (Ω/km)", f"{k_used:.6g}"),
                ]
            else:
                summary_pairs = [
                    ("Conductor operating temperature (°C)", operating_temp_c),
                    ("k multiplier", f"{k_temp_multiplier:.2f}"),
                    ("Parallel conductors per phase/pole", n_parallel_vd),
                    ("Material", "(N/A — manual k)"),
                    ("Installation", "(N/A — manual k)"),
                    ("Power factor column", "(N/A — manual k)"),
                    ("Conductor size", "(N/A — manual k)"),
                    ("k source", "Manual entry"),
                    ("Base k-value (75°C) (Ω/km)", f"{k_base:.6g}"),
                    ("Adjusted k-value used (Ω/km)", f"{k_used:.6g}"),
                ]

            for kname, kval in summary_pairs:
                ws[f"A{row}"] = kname
                ws[f"B{row}"] = "" if kval is None else str(kval)
                row += 1

            row += 1
            ws[f"A{row}"] = "Results"
            ws[f"A{row}"].font = Font(bold=True)
            row += 1
            ws[f"A{row}"] = "V_D (V)"
            ws[f"B{row}"] = _safe_float(Vd)
            row += 1
            ws[f"A{row}"] = "%ΔV (%)"
            ws[f"B{row}"] = _safe_float(pct)
            autosize(ws)

            # --- Variables
            ws = wb.create_sheet("Variables")
            ws.append(["Symbol", "Description", "Value"])
            for cell in ws[1]:
                cell.font = Font(bold=True)
            for v in variables:
                val = v["Value"]
                ws.append([v["Symbol"], v["Description"], None if val is None else float(val)])
            autosize(ws)

            # --- Assumptions
            ws = wb.create_sheet("Assumptions")
            ws.append(["Assumptions"])
            ws["A1"].font = Font(bold=True)
            for a in assumptions:
                ws.append([a])
            ws.column_dimensions["A"].width = 110
            for r in range(2, 2 + len(assumptions)):
                ws[f"A{r}"].alignment = Alignment(wrap_text=True, vertical="top")

            # --- Equations
            ws = wb.create_sheet("Equations")
            ws.append(["Name", "Equation (LaTeX)"])
            for cell in ws[1]:
                cell.font = Font(bold=True)
            for title, latex in equations_text:
                ws.append([title, latex])
            ws.column_dimensions["A"].width = 22
            ws.column_dimensions["B"].width = 70

            # --- Constants
            ws = wb.create_sheet("Constants")
            ws.append(["Name", "Meaning", "Value"])
            for cell in ws[1]:
                cell.font = Font(bold=True)
            for c in constants:
                ws.append([c["Name"], c["Meaning"], c["Value"]])
            autosize(ws)

            bio = io.BytesIO()
            wb.save(bio)
            return bio.getvalue()

        # Only enable downloads when we have enough info to populate the report meaningfully
        can_export = (k_used is not None) and (I is not None) and (L_m is not None) and (V_nom is not None)

        exp_c1, exp_c2 = st.columns([1, 1], gap="large")
        with exp_c1:
            if st.button("Prepare Word report (.docx)", key="vd_build_docx"):
                try:
                    st.session_state["vd_docx_bytes"] = build_vd_word_report()
                    st.success("Word report prepared. Use the download button below.")
                except Exception as e:
                    st.error(f"Failed to build Word report: {e}")

            docx_bytes = st.session_state.get("vd_docx_bytes", None)
            st.download_button(
                "⬇️ Download Word report (.docx)",
                data=docx_bytes if docx_bytes else b"",
                file_name="Voltage_Drop_Report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                disabled=(not can_export) or (docx_bytes is None),
                key="vd_download_docx",
            )

        with exp_c2:
            if st.button("Prepare Excel report (.xlsx)", key="vd_build_xlsx"):
                try:
                    st.session_state["vd_xlsx_bytes"] = build_vd_excel_report()
                    st.success("Excel report prepared. Use the download button below.")
                except Exception as e:
                    st.error(f"Failed to build Excel report: {e}")

            xlsx_bytes = st.session_state.get("vd_xlsx_bytes", None)
            st.download_button(
                "⬇️ Download Excel report (.xlsx)",
                data=xlsx_bytes if xlsx_bytes else b"",
                file_name="Voltage_Drop_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                disabled=(not can_export) or (xlsx_bytes is None),
                key="vd_download_xlsx",
            )

        st.caption(
            "Export includes: equations, assumptions, variables/inputs/results, constants, "
        )

        # -------------------------------------------------
        # Display exact Table D3 data used by the calculator (always shown)
        # (Raceway columns ordered: 100% -> 90% -> 80%)
        # -------------------------------------------------
        with st.expander("📋 Show Table D3 values used in this calculator", expanded=False):
            if not use_table:
                st.info("Table D3 shown for reference only while in Manual k-value mode — it does not affect the calculation unless you switch to 'Lookup' mode.")

            st.markdown("### Copper Conductors — Table D3 (Ω/km)")

            display_cols = [
                "Size",
                "DC",
                "Cable 100%",
                "Cable 90%",
                "Cable 80%",
                "Raceway 100%",
                "Raceway 90%",
                "Raceway 80%",
            ]

            cu_rows_display = []
            for size_key, cols in TABLE_D3["Copper"].items():
                row = {
                    "Size": size_key,
                    "DC": cols.get("DC", None),
                    "Cable 100%": cols.get("Cable 100%", None),
                    "Cable 90%": cols.get("Cable 90%", None),
                    "Cable 80%": cols.get("Cable 80%", None),
                    "Raceway 100%": cols.get("Raceway 100%", None),
                    "Raceway 90%": cols.get("Raceway 90%", None),
                    "Raceway 80%": cols.get("Raceway 80%", None),
                }
                cu_rows_display.append(row)

            if pd is not None:
                df_cu = pd.DataFrame(cu_rows_display, columns=display_cols)
                st.dataframe(df_cu, width="stretch", hide_index=True)
            else:
                st.dataframe(cu_rows_display, width="stretch", hide_index=True)

            st.markdown("### Aluminum Conductors — Table D3 (Ω/km)")
            al_rows_display = []
            for size_key, cols in TABLE_D3["Aluminum"].items():
                row = {
                    "Size": size_key,
                    "DC": cols.get("DC", None),
                    "Cable 100%": cols.get("Cable 100%", None),
                    "Cable 90%": cols.get("Cable 90%", None),
                    "Cable 80%": cols.get("Cable 80%", None),
                    "Raceway 100%": cols.get("Raceway 100%", None),
                    "Raceway 90%": cols.get("Raceway 90%", None),
                    "Raceway 80%": cols.get("Raceway 80%", None),
                }
                al_rows_display.append(row)

            if pd is not None:
                df_al = pd.DataFrame(al_rows_display, columns=display_cols)
                st.dataframe(df_al, width="stretch", hide_index=True)
            else:
                st.dataframe(al_rows_display, width="stretch", hide_index=True)

            st.caption(
                "These tables are transcribed **exactly** from OESC Appendix D – Table D3 "
                "(75 °C conductors). Values are in Ω per circuit kilometre and are the "
                "same values used internally by the calculator above."
            )

        # -------------------------------------------------
        # Display the F-factor lookup table used by the calculator
        # -------------------------------------------------
        with st.expander("📐 Show system factor (f) table used in calculations", expanded=False):
            if pd is not None:
                df_f = pd.DataFrame(f_table_rows)
                st.markdown("### System factor (f) — reference table (from Appendix D)")
                st.dataframe(df_f, width="stretch", hide_index=True)

                try:
                    current_label = f_choice[0] if isinstance(f_choice, tuple) else str(f_choice)
                    current_f = f_choice[1] if isinstance(f_choice, tuple) else float(f_choice)
                    st.markdown(f"**Current selection:** `{current_label}` → f = **{current_f:.6g}**")
                except Exception:
                    st.info("Current f selection shown in the calculator inputs above.")

                st.caption(
                    "Notes: The 'Voltage reference' column shows whether the VD is line-to-line or line-to-ground for that circuit type."
                )
            else:
                st.markdown("### System factor (f) — reference (plain)")
                for r in f_table_rows:
                    st.write(f"- **{r['System / Connection']}** — f = {r['f (used in formula)']} — {r['Voltage reference']}")
                st.caption("Pandas not available; shown as plaintext.")


# ============================
# 12) Conductors
# ============================
elif page == "Conductors":
    with theory_tab:
        header("Conductors — Theory", "OESC Section 4 (Rule 4-004) workflow + worked example case study.")
        show_code_note(code_mode)
        if code_mode == "OESC":
            render_md_safe("conductors_oesc.md")
        else:
            render_md_safe("conductors_nec.md")

    with calc_tab:
        header("Conductors — Calculator", "Workflow helper: design current, table selection, correction-factor math, and k-value voltage drop check.")
        show_code_note(code_mode)

        if code_mode == "NEC":
            st.info(
                "Calculator logic below follows the OESC/CEC workflow summary (Rule 4-004 style). "
                "Switch the sidebar jurisdiction to **OESC** for best alignment."
            )

        st.markdown("### Conductor Selection Flowchart")
        dot = """
digraph G {
  rankdir=TB;
  node [shape=box, style=rounded];

  d1 [label="Path"];
  d1 -> d2 [label="Free air"];
  d2 [label="<= 25% spacing", shape=diamond, fixedsize=true, width=1.2, height=0.8, margin=0.05];
  d2 -> d3 [label="No"];
  d3 [label="Table 1/3"];
  d2 -> d4 [label="Yes"];
  d4 [label="<= 4 Conductors", shape=diamond, fixedsize=true, width=1.2, height=0.8, margin=0.05];
  d5 [label="Table 1/3 x 5B"];
  d6 [label="Table 2/4 x 5C"];
  d4 -> d5 [label="Yes"];
  d4 -> d6 [label="No"];

  d1 -> d7 [label="Raceway/Cable"];
  d7 [label="<= 3 Conductors", shape=diamond, fixedsize=true, width=1.2, height=0.8, margin=0.05];
  d7 -> d6 [label="No"];
  d8 [label="Table 2/4"];
  d7 -> d8 [label="Yes"];
}
"""
        st.graphviz_chart(dot)

        st.markdown("## 1) Ampacity workflow helper (service factor + table selection)")

        cable_name = st.text_input(
            "Cable name / tag",
            value="",
            key="cond_cable_name",
            help="Identifier used in the export report (for example: Feeder FDR-1).",
        )

        c1, c2, c3 = st.columns([1, 1, 1], gap="large")
        with c1:
            I_load = st.number_input("Load current (A)", min_value=0.0, value=100.0, step=1.0, key="cond_I_load")
        with c2:
            sf = st.number_input("Service factor (SF)", min_value=1.0, value=1.25, step=0.05, key="cond_sf")
        with c3:
            use_parallel = st.checkbox(
                "Run additional parallel sets",
                value=False,
                key="cond_use_parallel",
            )
            if use_parallel:
                extra_sets = st.number_input(
                    "Additional parallel sets",
                    min_value=1,
                    value=1,
                    step=1,
                    key="cond_additional_sets",
                    help="1 additional set = 2 total runs; 2 additional sets = 3 total runs.",
                )
                n_parallel = 1 + int(extra_sets)
            else:
                n_parallel = 1

        mat = st.selectbox(
            "Conductor material (table family)",
            ["Copper (Tables 1–2)", "Aluminum (Tables 3–4)"],
            index=0,
            key="cond_material",
        )

        construction = st.selectbox(
            "Conductor construction",
            ["Single conductors", "Multi-conductor cable"],
            index=0,
            key="cond_construction",
        )
        is_multi = construction.startswith("Multi")

        install = st.selectbox(
            "Installation method / condition",
            [
                "Free air (ventilated / ladder tray)",
                "Raceway or cable (conduit/tubing/cable)",
                "Underground (direct buried / direct-buried raceway)",
            ],
            index=0,
            key="cond_install",
        )

        st.markdown("### Ambient/temperature adjustments (Table 5A)")
        use_temp_corr = st.checkbox(
            "Apply ambient temperature correction (Table 5A)",
            value=False,
            key="cond_use_temp_corr",
        )

        temp_factor = 1.0
        temp_factor_source = "None"

        if use_temp_corr:
            if oesc_tables is None:
                st.warning("Table 5A lookup unavailable; enter the correction factor manually.")
                temp_factor = st.number_input(
                    "Temperature correction factor (Table 5A)",
                    min_value=0.01,
                    max_value=1.00,
                    value=0.94,
                    step=0.01,
                    key="cond_temp_factor_manual",
                )
                temp_factor_source = "Manual (Table 5A)"
            else:
                table5a_meta = oesc_tables.get_table_meta("5A") or {}
                table5a_rows = table5a_meta.get("rows", [])
                table5a_cols = table5a_meta.get("columns", [])
                temp_options = [str(c) for c in table5a_cols if c is not None]

                ambient_key = None
                if table5a_rows:
                    for k in table5a_rows[0].keys():
                        if "Ambient" in str(k):
                            ambient_key = k
                            break

                ambient_vals = []
                if ambient_key:
                    ambient_vals = sorted(
                        {r.get(ambient_key) for r in table5a_rows if r.get(ambient_key) is not None}
                    )

                ambient_choices = [30] + [v for v in ambient_vals if v is not None and v > 30]
                ambient_c = st.selectbox(
                    "Ambient temperature (°C)",
                    ambient_choices if ambient_choices else [30],
                    index=0,
                    key="cond_ambient_temp",
                )

                default_label = None
                for candidate in ("90°C",):
                    if candidate in temp_options:
                        default_label = candidate
                        break
                temp_rating_label = st.selectbox(
                    "Conductor insulation temperature rating (°C)",
                    temp_options if temp_options else ["60°C", "75°C", "90°C"],
                    index=temp_options.index(default_label) if temp_options and default_label in temp_options else 0,
                    key="cond_temp_rating",
                )

                if ambient_c <= 30:
                    temp_factor = 1.0
                    temp_factor_source = "Table 5A (≤30°C)"
                else:
                    row_match = None
                    for r in table5a_rows:
                        if ambient_key and r.get(ambient_key) == ambient_c:
                            row_match = r
                            break
                    if row_match is None:
                        st.warning("Ambient temperature not found in Table 5A; enter the correction factor manually.")
                        temp_factor = st.number_input(
                            "Temperature correction factor (Table 5A)",
                            min_value=0.01,
                            max_value=1.00,
                            value=0.94,
                            step=0.01,
                            key="cond_temp_factor_manual_fallback",
                        )
                        temp_factor_source = "Manual (Table 5A)"
                    else:
                        temp_factor = row_match.get(temp_rating_label)
                        if temp_factor is None:
                            st.warning("Table 5A factor not available for this temperature rating; enter manually.")
                            temp_factor = st.number_input(
                                "Temperature correction factor (Table 5A)",
                                min_value=0.01,
                                max_value=1.00,
                                value=0.94,
                                step=0.01,
                                key="cond_temp_factor_manual_fallback2",
                            )
                            temp_factor_source = "Manual (Table 5A)"
                        else:
                            temp_factor = float(temp_factor)
                            temp_factor_source = "Table 5A"

        I_design_total = I_load * sf
        I_per_set = safe_div(I_design_total, n_parallel) if n_parallel else None

        m1, m2 = st.columns(2, gap="large")
        m1.metric("Design current (total)", fmt(I_design_total, "A"))
        m2.metric("Design current per parallel set", fmt(I_per_set, "A"))

        def cu_table(free_air: bool):
            return "Table 1" if free_air else "Table 2"

        def al_table(free_air: bool):
            return "Table 3" if free_air else "Table 4"

        is_cu = mat.startswith("Copper")

        subrule = "—"
        amp_table = "—"
        corr_table = None
        corr_needed = False
        corr_hint = ""

        if install.startswith("Free air"):
            if is_multi:
                st.info(
                    "Multi-conductor cable in free air is handled using the raceway/cable ampacity tables in this helper. "
                    "Verify applicability for your installation."
                )
                n_ccc_freeair = st.number_input(
                    "Number of current-carrying conductors in cable",
                    min_value=1,
                    value=3,
                    step=1,
                    key="cond_freeair_nccc",
                )
                if n_ccc_freeair <= 3:
                    subrule = "4-004 (1) & (2) — multiconductor in free air (1–3 CCC)"
                    amp_table = cu_table(False) if is_cu else al_table(False)
                else:
                    subrule = "4-004 (1) & (2) — multiconductor in free air (4+ CCC)"
                    amp_table = cu_table(False) if is_cu else al_table(False)
                    corr_table = "Table 5C"
                    corr_needed = True
                    corr_hint = "Enter k_corr from Table 5C (4+ current-carrying conductors)."
            else:
                n_single = st.number_input(
                    "Number of single conductors in the group",
                    min_value=1,
                    value=4,
                    step=1,
                    key="cond_freeair_nsingle",
                )

                spacing = st.radio(
                    "Spacing between cables (% of largest cable diameter)",
                    ["≥ 100%", "25% to 100%", "< 25%"],
                    index=0,
                    horizontal=True,
                    key="cond_freeair_spacing",
                )

                if spacing == "≥ 100%":
                    subrule = "4-004 (1) & (2) — single in free air"
                    amp_table = cu_table(True) if is_cu else al_table(True)
                elif spacing == "25% to 100%":
                    subrule = "4-004 (8) — single in free air"
                    amp_table = cu_table(True) if is_cu else al_table(True)
                    corr_table = "Table 5D"
                    corr_needed = True
                    corr_hint = "Enter k_corr from Table 5D (spacing 25%–100%)."
                else:
                    if n_single <= 4:
                        subrule = "4-004 (9) — ≤4 single in free air"
                        amp_table = cu_table(True) if is_cu else al_table(True)
                        corr_table = "Table 5B"
                        corr_needed = True
                        corr_hint = "Enter k_corr from Table 5B (spacing <25%, ≤4 singles)."
                    else:
                        subrule = "4-004 (11) — ≥5 single in free air"
                        amp_table = cu_table(False) if is_cu else al_table(False)
                        corr_table = "Table 5C"
                        corr_needed = True
                        corr_hint = "Enter k_corr from Table 5C (spacing <25%, ≥5 singles)."

        elif install.startswith("Raceway"):
            n_ccc_label = (
                "Number of current-carrying conductors in cable"
                if is_multi
                else "Number of conductors in raceway/cable (use current-carrying count per your code interpretation)"
            )
            n_ccc = st.number_input(
                n_ccc_label,
                min_value=1,
                value=3,
                step=1,
                key="cond_raceway_nccc",
            )

            if n_ccc <= 3:
                subrule = "4-004 (1) & (2) — 1 to 3 in raceway/cable"
                amp_table = cu_table(False) if is_cu else al_table(False)
            else:
                subrule = "4-004 (1) & (2) — 4 or more in raceway/cable"
                amp_table = cu_table(False) if is_cu else al_table(False)
                corr_table = "Table 5C"
                corr_needed = True
                corr_hint = "Enter k_corr from Table 5C (4+ in raceway/cable)."

        else:
            size_class = st.selectbox(
                "Conductor size class (per chart split)",
                ["No. 1/0 AWG and larger", "Smaller than No. 1/0 AWG"],
                index=0,
                key="cond_ug_sizeclass",
            )
            in_diagrams = st.radio(
                "Is the configuration covered in Diagrams D8 to D11",
                ["Yes", "No"],
                index=0,
                horizontal=True,
                key="cond_ug_diagrams",
            )

            if size_class.startswith("No. 1/0") and in_diagrams == "Yes":
                subrule = "4-004 (1) & (2)(d) — underground, ≥1/0, config in D8–D11"
                amp_table = "Tables D8A to D11B (or IEEE 835)"
            elif size_class.startswith("No. 1/0") and in_diagrams == "No":
                subrule = "4-004 (1) & (2)(e) — underground, ≥1/0, config NOT in D8–D11"
                amp_table = "IEEE 835 calculation method"
            elif size_class.startswith("Smaller") and in_diagrams == "No":
                subrule = "4-004 (1) & (2)(f) — underground, <1/0, config NOT in D8–D11"
                amp_table = f"{cu_table(False) if is_cu else al_table(False)} (or IEEE 835)"
            else:
                subrule = "Underground case (not explicitly shown in the chart)"
                amp_table = f"{cu_table(False) if is_cu else al_table(False)} (confirm applicability)"
                st.warning(
                    "The chart explicitly calls out diagram usage for ≥1/0 AWG. "
                    "For <1/0 AWG, the summary points to IEEE 835 or Tables 2/4 depending on configuration. "
                    "Confirm in the full code/diagrams for your exact installation."
                )

        st.divider()
        st.markdown("### Table / factor guidance result")
        st.success(f"**Subrule path:** {subrule}")
        st.success(f"**Use ampacity from:** {amp_table}")

        corr_factor = 1.0
        corr_factor_source = "None"
        if corr_needed:
            if corr_table == "Table 5B":
                use_table5b = st.checkbox(
                    "Use Table 5B lookup (auto)",
                    value=True,
                    key="cond_use_table5b",
                )
                if use_table5b:
                    if oesc_tables is None:
                        st.warning("Table 5B lookup unavailable; enter the factor manually.")
                        corr_factor = st.number_input(
                            f"Correction factor k_corr ({corr_table})",
                            min_value=0.01,
                            max_value=1.00,
                            value=0.80,
                            step=0.01,
                            key="cond_corr_factor_5b_manual",
                            help=corr_hint,
                        )
                        corr_factor_source = "Manual (Table 5B)"
                    else:
                        rows_5b = oesc_tables.get_table_rows("5B") or []
                        factor = None
                        for r in rows_5b:
                            if r.get("Number of conductors") == n_single:
                                factor = r.get("Correction factor")
                                break
                        if factor is None:
                            st.warning("Table 5B has factors for 2–4 conductors. Enter the factor manually.")
                            corr_factor = st.number_input(
                                f"Correction factor k_corr ({corr_table})",
                                min_value=0.01,
                                max_value=1.00,
                                value=0.80,
                                step=0.01,
                                key="cond_corr_factor_5b_manual_fallback",
                                help=corr_hint,
                            )
                            corr_factor_source = "Manual (Table 5B)"
                        else:
                            corr_factor = float(factor)
                            corr_factor_source = "Table 5B"
                else:
                    corr_factor = st.number_input(
                        f"Correction factor k_corr ({corr_table})",
                        min_value=0.01,
                        max_value=1.00,
                        value=0.80,
                        step=0.01,
                        key="cond_corr_factor_5b_manual_opt",
                        help=corr_hint,
                    )
                    corr_factor_source = "Manual (Table 5B)"
            elif corr_table == "Table 5D":
                if oesc_tables is None:
                    st.warning("Table 5D lookup unavailable; enter the factor manually.")
                    corr_factor = st.number_input(
                        f"Correction factor k_corr ({corr_table})",
                        min_value=0.01,
                        max_value=1.00,
                        value=0.80,
                        step=0.01,
                        key="cond_corr_factor_5d_manual",
                        help=corr_hint,
                    )
                    corr_factor_source = "Manual (Table 5D)"
                else:
                    rows_5d = oesc_tables.get_table_rows("5D") or []
                    options_5d = []
                    for r in rows_5d:
                        h = r.get("Horizontal count")
                        v = r.get("Vertical layers")
                        f = r.get("Correction factor")
                        try:
                            h_i = int(h)
                            v_i = int(v)
                            f_f = float(f)
                            options_5d.append((h_i, v_i, f_f))
                        except Exception:
                            continue

                    if not options_5d:
                        st.warning("Table 5D rows not available; enter the factor manually.")
                        corr_factor = st.number_input(
                            f"Correction factor k_corr ({corr_table})",
                            min_value=0.01,
                            max_value=1.00,
                            value=0.80,
                            step=0.01,
                            key="cond_corr_factor_5d_manual_fallback",
                            help=corr_hint,
                        )
                        corr_factor_source = "Manual (Table 5D)"
                    else:
                        options_5d = sorted(options_5d, key=lambda x: (x[1], x[0]))
                        vertical_choices = sorted({opt[1] for opt in options_5d})
                        selected_v_5d = st.selectbox(
                            "Vertical layers (Table 5D)",
                            vertical_choices,
                            index=0,
                            key="cond_table5d_vertical",
                        )

                        horizontal_choices = sorted({opt[0] for opt in options_5d if opt[1] == selected_v_5d})
                        selected_h_5d = st.selectbox(
                            "Horizontal count (Table 5D)",
                            horizontal_choices,
                            index=0,
                            key="cond_table5d_horizontal",
                        )

                        selected_5d = next(
                            (opt for opt in options_5d if opt[0] == selected_h_5d and opt[1] == selected_v_5d),
                            None,
                        )
                        if selected_5d is None:
                            corr_factor = st.number_input(
                                f"Correction factor k_corr ({corr_table})",
                                min_value=0.01,
                                max_value=1.00,
                                value=0.80,
                                step=0.01,
                                key="cond_corr_factor_5d_manual_unmatched",
                                help=corr_hint,
                            )
                            corr_factor_source = "Manual (Table 5D)"
                        else:
                            corr_factor = float(selected_5d[2])
                            corr_factor_source = f"Table 5D (Horizontal {selected_h_5d}, Vertical {selected_v_5d})"
            else:
                corr_factor = st.number_input(
                    f"Correction factor k_corr ({corr_table})",
                    min_value=0.01,
                    max_value=1.00,
                    value=0.80,
                    step=0.01,
                    key="cond_corr_factor",
                    help=corr_hint,
                )
                corr_factor_source = corr_table or "Manual"

            st.info(f"Correction factor source: **{corr_factor_source}**")

        if use_temp_corr:
            st.info(f"Temperature factor source: **{temp_factor_source}**")

        k_total = None
        if corr_factor is not None and temp_factor is not None:
            k_total = corr_factor * temp_factor

        I_table_required = None
        if I_per_set is not None and k_total is not None:
            I_table_required = safe_div(I_per_set, k_total)

        st.metric("Total correction factor (k_total)", fmt(k_total))
        st.markdown("**Correction factor breakdown**")
        st.write(
            f"- k_corr = **{fmt(corr_factor)}** (source: {corr_factor_source})"
        )
        st.write(
            f"- k_temp = **{fmt(temp_factor)}** (source: {temp_factor_source})"
        )
        st.write(
            f"- k_total = k_corr x k_temp = **{fmt(k_total)}**"
        )
        st.metric("Minimum base-table ampacity to look for", fmt(I_table_required, "A"))

        st.markdown("### Auto-select conductor from ampacity table")
        recommended_size_display = None
        recommended_source_table = None
        recommended_temp_col_c = None
        recommended_base_ampacity = None
        recommended_adjusted_ampacity_per_set = None
        def _to_float_local(x):
            try:
                if x is None or x in ("—", "-"):
                    return None
                return float(x)
            except Exception:
                return None

        amp_table_id = None
        m = re.search(r"Table\s*([1-4])", str(amp_table))
        if m:
            amp_table_id = m.group(1)

        auto_pick_ready = amp_table_id is not None and oesc_tables is not None and I_table_required is not None
        if auto_pick_ready:
            auto_pick = st.checkbox(
                "Auto-pick smallest size that meets required base ampacity",
                value=True,
                key="cond_auto_pick",
            )
            if auto_pick:
                table_meta = oesc_tables.get_table_meta(amp_table_id) or {}
                table_rows = table_meta.get("rows", [])
                size_key = "Size (AWG/kcmil)"
                if table_rows and size_key not in table_rows[0]:
                    for k in table_rows[0].keys():
                        if "size" in str(k).lower():
                            size_key = k
                            break

                temp_cols = table_meta.get("columns", [])
                temp_col_map = {}
                temp_options = []
                for col in temp_cols:
                    m2 = re.search(r"(\d+)", str(col))
                    if m2:
                        val = int(m2.group(1))
                        temp_col_map[val] = col
                        temp_options.append(val)
                temp_options = sorted(set(temp_options))

                default_temp = 75 if 75 in temp_options else (temp_options[0] if temp_options else None)
                temp_choice = st.selectbox(
                    "Table column (insulation temp rating)",
                    temp_options if temp_options else [60, 75, 90],
                    index=temp_options.index(default_temp) if temp_options and default_temp in temp_options else 0,
                    key="cond_auto_table_temp_choice",
                )

                selected_row = None
                selected_base = None
                col_label = temp_col_map.get(temp_choice)
                if col_label:
                    for r in table_rows:
                        base_val = _to_float_local(r.get(col_label))
                        if base_val is not None and base_val >= float(I_table_required):
                            selected_row = r
                            selected_base = base_val
                            break

                if selected_row is None or selected_base is None:
                    st.warning(
                        "No size in the selected table column meets the required base ampacity. "
                        "Consider a higher temperature column or another table (if applicable)."
                    )
                else:
                    selected_size = str(selected_row.get(size_key, "(size not found)"))
                    adjusted_ampacity = selected_base * float(k_total) if k_total is not None else None
                    selected_size_display = format_cond_size(selected_size)
                    recommended_size_display = selected_size_display
                    recommended_source_table = amp_table
                    recommended_temp_col_c = temp_choice
                    recommended_base_ampacity = selected_base
                    recommended_adjusted_ampacity_per_set = adjusted_ampacity
                    st.markdown("### Recommended conductor size")
                    st.markdown(f"## **{selected_size_display}**")
                    st.caption(f"From {amp_table}")
                    st.metric("Base ampacity (table)", fmt(selected_base, "A"))
                    if adjusted_ampacity is not None and n_parallel and n_parallel > 1:
                        st.metric("Adjusted ampacity per set", fmt(adjusted_ampacity, "A"))
                        st.metric("Adjusted ampacity (all sets)", fmt(adjusted_ampacity * n_parallel, "A"))
                    else:
                        st.metric("Adjusted ampacity", fmt(adjusted_ampacity, "A"))

                    st.markdown("**Ampacity derating breakdown (selected cable)**")
                    st.write(
                        f"- Base ampacity ({amp_table}, {selected_size_display}, {temp_choice}°C column) = **{fmt(selected_base, 'A')}**"
                    )
                    st.write(
                        f"- k_corr = **{fmt(corr_factor)}** (source: {corr_factor_source})"
                    )
                    st.write(
                        f"- k_temp = **{fmt(temp_factor)}** (source: {temp_factor_source})"
                    )
                    st.write(
                        f"- k_total = k_corr x k_temp = **{fmt(k_total)}**"
                    )
                    st.write(
                        f"- Adjusted ampacity per set = base x k_total = **{fmt(adjusted_ampacity, 'A')}**"
                    )
                    st.write(
                        f"- Required base ampacity = I_per_set / k_total = **{fmt(I_table_required, 'A')}**"
                    )
                    st.write(
                        f"- Design current per set = **{fmt(I_per_set, 'A')}**"
                    )

                    if adjusted_ampacity is not None and I_per_set is not None:
                        if adjusted_ampacity < I_per_set:
                            st.error(
                                "Adjusted ampacity per set is below the load current per set. "
                                "Choose a larger conductor or reduce correction factors."
                            )
                        else:
                            st.success("Adjusted ampacity per set meets or exceeds the load current per set.")
        else:
            st.caption("Auto-selection is available only when Tables 1-4 are selected and the table library is loaded.")
            with st.expander("Why auto-selection is disabled", expanded=False):
                st.write(f"- Table selection detected: **{amp_table}**")
                st.write(f"- Table id parsed (1-4): **{amp_table_id if amp_table_id else 'None'}**")
                st.write(f"- Table library loaded: **{'Yes' if oesc_tables is not None else 'No'}**")
                st.write(
                    f"- Required base ampacity computed: **{'Yes' if I_table_required is not None else 'No'}**"
                )
                if oesc_tables is None and _TABLES_IMPORT_ERROR:
                    st.write(f"- Table library import error: `{_TABLES_IMPORT_ERROR}`")

        st.markdown("### Optional: Check selected conductor ampacity (manual override)")
        use_amp_check = st.checkbox(
            "Enable manual ampacity check",
            value=False,
            key="cond_use_amp_check",
        )

        if use_amp_check:
            base_ampacity = None

            if amp_table_id and oesc_tables is not None:
                use_lookup = st.checkbox(
                    f"Lookup base ampacity from {amp_table}",
                    value=True,
                    key="cond_use_amp_lookup",
                )
                if use_lookup:
                    table_meta = oesc_tables.get_table_meta(amp_table_id) or {}
                    table_rows = table_meta.get("rows", [])
                    size_key = "Size (AWG/kcmil)"
                    if table_rows and size_key not in table_rows[0]:
                        for k in table_rows[0].keys():
                            if "size" in str(k).lower():
                                size_key = k
                                break
                    sizes = [str(r.get(size_key)) for r in table_rows if r.get(size_key) is not None]
                    sizes = sizes if sizes else []

                    temp_cols = table_meta.get("columns", [])
                    temp_col_map = {}
                    temp_options = []
                    for col in temp_cols:
                        m2 = re.search(r"(\d+)", str(col))
                        if m2:
                            val = int(m2.group(1))
                            temp_col_map[val] = col
                            temp_options.append(val)
                    temp_options = sorted(set(temp_options))

                    size_choice = st.selectbox(
                        "Conductor size (from table)",
                        sizes if sizes else ["(no sizes found)"],
                        index=0,
                        key="cond_size_choice",
                        format_func=lambda s: format_cond_size(s),
                    )

                    default_temp = 75 if 75 in temp_options else (temp_options[0] if temp_options else None)
                    temp_choice = st.selectbox(
                        "Table column (insulation temp rating)",
                        temp_options if temp_options else [60, 75, 90],
                        index=temp_options.index(default_temp) if temp_options and default_temp in temp_options else 0,
                        key="cond_table_temp_choice",
                    )

                    if sizes:
                        for r in table_rows:
                            if str(r.get(size_key)) == str(size_choice):
                                col_label = temp_col_map.get(temp_choice)
                                base_ampacity = r.get(col_label) if col_label else None
                                break

                    if base_ampacity is None:
                        st.warning("Selected size/temperature not found in table; enter base ampacity manually.")
                        base_ampacity = st.number_input(
                            "Base ampacity from table (A)",
                            min_value=0.0,
                            value=0.0,
                            step=1.0,
                            key="cond_base_ampacity_manual_fallback",
                        )
                else:
                    base_ampacity = st.number_input(
                        "Base ampacity from table (A)",
                        min_value=0.0,
                        value=0.0,
                        step=1.0,
                        key="cond_base_ampacity_manual",
                    )
            else:
                st.caption("Auto table lookup unavailable for this ampacity source. Enter base ampacity manually.")
                base_ampacity = st.number_input(
                    "Base ampacity from table (A)",
                    min_value=0.0,
                    value=0.0,
                    step=1.0,
                    key="cond_base_ampacity_manual_only",
                )

            adjusted_ampacity = None
            if base_ampacity is not None and k_total is not None:
                adjusted_ampacity = float(base_ampacity) * float(k_total)

            st.metric("Base ampacity (selected)", fmt(base_ampacity, "A"))
            if adjusted_ampacity is not None and n_parallel and n_parallel > 1:
                st.metric("Adjusted ampacity per set", fmt(adjusted_ampacity, "A"))
                st.metric("Adjusted ampacity (all sets)", fmt(adjusted_ampacity * n_parallel, "A"))
            else:
                st.metric("Adjusted ampacity", fmt(adjusted_ampacity, "A"))

            if adjusted_ampacity is not None and I_per_set is not None:
                if adjusted_ampacity < I_per_set:
                    st.error(
                        "Adjusted ampacity per set is below the load current per set. "
                        "Choose a larger conductor or reduce correction factors."
                    )
                else:
                    st.success("Adjusted ampacity per set meets or exceeds the load current per set.")

        st.markdown("### 📄 Export calculation report")

        def append_to_value_line(cell, value: str, paragraph_index: int = 1):
            if len(cell.paragraphs) > paragraph_index:
                p = cell.paragraphs[paragraph_index]
            else:
                p = cell.add_paragraph()
            p.add_run(f" {value}")

        def set_table_borders(table):
            tbl = table._tbl
            tblPr = tbl.tblPr
            borders = OxmlElement("w:tblBorders")
            for border_name in ("top", "left", "bottom", "right", "insideH", "insideV"):
                border = OxmlElement(f"w:{border_name}")
                border.set(qn("w:val"), "single")
                border.set(qn("w:sz"), "8")
                border.set(qn("w:space"), "0")
                border.set(qn("w:color"), "000000")
                borders.append(border)
            tblPr.append(borders)

        corr_math = "Adjusted ampacity = Base ampacity x k_corr x k_temp"
        if recommended_base_ampacity is not None and corr_factor is not None and temp_factor is not None:
            corr_math = (
                f"Adjusted ampacity = {float(recommended_base_ampacity):.6g} x "
                f"{float(corr_factor):.6g} x {float(temp_factor):.6g} = "
                f"{float(recommended_adjusted_ampacity_per_set):.6g} A"
            )

        inputs_rows = [
            ("Cable Name", cable_name.strip() if cable_name and cable_name.strip() else "(not provided)"),
            ("Load current I_load (A)", fmt(I_load, "A")),
            ("Service factor SF", fmt(sf)),
            ("Design current I_design (A)", fmt(I_design_total, "A")),
            ("Parallel sets N_parallel", str(n_parallel)),
            ("Design current per set I_per_set (A)", fmt(I_per_set, "A")),
            ("Conductor material", mat),
            ("Conductor construction", construction),
            ("Installation path", install),
        ]
        if use_temp_corr:
            inputs_rows.extend([
                ("Ambient temperature (°C)", fmt(st.session_state.get("cond_ambient_temp"), "°C")),
                ("Insulation temp rating column", str(st.session_state.get("cond_temp_rating", "—"))),
            ])

        table_rows = [
            ("Subrule path", subrule),
            ("Ampacity table used", amp_table),
            ("Correction table used", corr_table if corr_table else "(none)"),
            ("Temperature correction table", "Table 5A" if use_temp_corr else "(none)"),
        ]

        factor_rows = [
            ("k_corr", fmt(corr_factor), corr_factor_source),
            ("k_temp", fmt(temp_factor), temp_factor_source),
            ("k_total = k_corr x k_temp", fmt(k_total), "Calculated"),
            ("Required base ampacity I_table = I_per_set / k_total", fmt(I_table_required, "A"), "Calculated"),
        ]

        def build_cond_word_report():
            doc = Document("content/files/Template.docx")
            table = doc.sections[0].header.tables[0]

            append_to_value_line(table.cell(0, 3), PROJECT_NUMBER)
            append_to_value_line(table.cell(0, 4), "#")
            append_to_value_line(table.cell(2, 3), DESIGNER_NAME)
            append_to_value_line(table.cell(2, 4), datetime.now().strftime("%m/%d/%Y"))
            append_to_value_line(table.cell(3, 3), "checked by")
            append_to_value_line(table.cell(3, 4), "checked date")
            append_to_value_line(table.cell(3, 2), "Conductor Cable Size Report")

            doc.add_heading("Cable Name", level=1)
            doc.add_paragraph(cable_name.strip() if cable_name and cable_name.strip() else "(not provided)")

            doc.add_heading("Input Parameters", level=1)
            t_inputs = doc.add_table(rows=1, cols=2)
            t_inputs.rows[0].cells[0].text = "Parameter"
            t_inputs.rows[0].cells[1].text = "Value"
            for label, value in inputs_rows:
                r = t_inputs.add_row().cells
                r[0].text = str(label)
                r[1].text = str(value)
            set_table_borders(t_inputs)

            doc.add_heading("Which Tables Were Used", level=1)
            t_tables = doc.add_table(rows=1, cols=2)
            t_tables.rows[0].cells[0].text = "Item"
            t_tables.rows[0].cells[1].text = "Selection"
            for label, value in table_rows:
                r = t_tables.add_row().cells
                r[0].text = str(label)
                r[1].text = str(value)
            set_table_borders(t_tables)

            doc.add_heading("Correction Factors Applied", level=1)
            t_factors = doc.add_table(rows=1, cols=3)
            t_factors.rows[0].cells[0].text = "Factor"
            t_factors.rows[0].cells[1].text = "Value"
            t_factors.rows[0].cells[2].text = "Source"
            for label, value, source in factor_rows:
                r = t_factors.add_row().cells
                r[0].text = str(label)
                r[1].text = str(value)
                r[2].text = str(source)
            set_table_borders(t_factors)

            doc.add_heading("Math Showing Correction Factors on Ampacity", level=1)
            doc.add_paragraph("k_total = k_corr x k_temp")
            doc.add_paragraph(corr_math)

            doc.add_heading("Recommended Cable Size", level=1)
            p = doc.add_paragraph()
            p.add_run(
                recommended_size_display
                if recommended_size_display
                else "(not auto-selected in this run)"
            ).bold = True
            if recommended_source_table:
                doc.add_paragraph(f"Source: {recommended_source_table}")
            if recommended_temp_col_c is not None:
                doc.add_paragraph(f"Table column: {recommended_temp_col_c}°C")
            if recommended_base_ampacity is not None:
                doc.add_paragraph(f"Base ampacity: {fmt(recommended_base_ampacity, 'A')}")
            if recommended_adjusted_ampacity_per_set is not None:
                doc.add_paragraph(f"Adjusted ampacity per set: {fmt(recommended_adjusted_ampacity_per_set, 'A')}")

            bio = io.BytesIO()
            doc.save(bio)
            return bio.getvalue()

        def build_cond_excel_report():
            wb = Workbook()
            def _cond_safe_float(x):
                try:
                    return None if x is None else float(x)
                except Exception:
                    return None

            def autosize(ws):
                for col in ws.columns:
                    max_len = 0
                    col_letter = get_column_letter(col[0].column)
                    for cell in col:
                        try:
                            v = "" if cell.value is None else str(cell.value)
                            max_len = max(max_len, len(v))
                        except Exception:
                            pass
                    ws.column_dimensions[col_letter].width = min(60, max(10, max_len + 2))

            ws = wb.active
            ws.title = "Summary"
            ws["A1"] = "Conductor Cable Size Report"
            ws["A1"].font = Font(bold=True, size=14)
            ws["A3"] = "Generated"
            ws["B3"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ws["A4"] = "Cable Name"
            ws["B4"] = cable_name.strip() if cable_name and cable_name.strip() else "(not provided)"

            row = 6
            for label, value in inputs_rows:
                ws[f"A{row}"] = label
                ws[f"B{row}"] = value
                row += 1

            row += 1
            ws[f"A{row}"] = "Recommended cable size"
            ws[f"A{row}"].font = Font(bold=True)
            ws[f"B{row}"] = recommended_size_display if recommended_size_display else "(not auto-selected in this run)"
            row += 1
            ws[f"A{row}"] = "Recommended source table"
            ws[f"B{row}"] = recommended_source_table if recommended_source_table else "—"
            row += 1
            ws[f"A{row}"] = "Recommended table column (°C)"
            ws[f"B{row}"] = recommended_temp_col_c if recommended_temp_col_c is not None else "—"
            row += 1
            ws[f"A{row}"] = "Base ampacity (A)"
            ws[f"B{row}"] = _cond_safe_float(recommended_base_ampacity)
            row += 1
            ws[f"A{row}"] = "Adjusted ampacity per set (A)"
            ws[f"B{row}"] = _cond_safe_float(recommended_adjusted_ampacity_per_set)
            autosize(ws)

            ws = wb.create_sheet("Tables Used")
            ws.append(["Item", "Selection"])
            for c in ws[1]:
                c.font = Font(bold=True)
            for label, value in table_rows:
                ws.append([label, value])
            autosize(ws)

            ws = wb.create_sheet("Correction Factors")
            ws.append(["Factor", "Value", "Source"])
            for c in ws[1]:
                c.font = Font(bold=True)
            for label, value, source in factor_rows:
                ws.append([label, value, source])
            ws.append([])
            ws.append(["Ampacity math", corr_math, ""])
            autosize(ws)

            bio = io.BytesIO()
            wb.save(bio)
            return bio.getvalue()

        can_export_cond = (I_table_required is not None) and (k_total is not None)

        exp_c1, exp_c2 = st.columns([1, 1], gap="large")
        with exp_c1:
            if st.button("Prepare Word report (.docx)", key="cond_build_docx"):
                try:
                    st.session_state["cond_docx_bytes"] = build_cond_word_report()
                    st.success("Word report prepared. Use the download button below.")
                except Exception as e:
                    st.error(f"Failed to build Word report: {e}")

            cond_docx_bytes = st.session_state.get("cond_docx_bytes", None)
            st.download_button(
                "⬇️ Download Word report (.docx)",
                data=cond_docx_bytes if cond_docx_bytes else b"",
                file_name="Conductor_Cable_Size_Report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                disabled=(not can_export_cond) or (cond_docx_bytes is None),
                key="cond_download_docx",
            )

        with exp_c2:
            if st.button("Prepare Excel report (.xlsx)", key="cond_build_xlsx"):
                try:
                    st.session_state["cond_xlsx_bytes"] = build_cond_excel_report()
                    st.success("Excel report prepared. Use the download button below.")
                except Exception as e:
                    st.error(f"Failed to build Excel report: {e}")

            cond_xlsx_bytes = st.session_state.get("cond_xlsx_bytes", None)
            st.download_button(
                "⬇️ Download Excel report (.xlsx)",
                data=cond_xlsx_bytes if cond_xlsx_bytes else b"",
                file_name="Conductor_Cable_Size_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                disabled=(not can_export_cond) or (cond_xlsx_bytes is None),
                key="cond_download_xlsx",
            )

        st.caption(
            "Export includes: cable name, inputs, correction factors, ampacity correction math, tables used, and recommended cable size."
        )

        st.markdown("### Equations used")
        eq(r"I_{design} = I_{load}\times SF")
        eq(r"I_{per\_set} = \frac{I_{design}}{N_{parallel}}")
        eq(r"k_{total} = k_{corr}\cdot k_{temp}")
        eq(r"I_{table} = \frac{I_{per\_set}}{k_{total}}")

