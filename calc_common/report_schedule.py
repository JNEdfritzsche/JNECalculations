from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from docx.enum.section import WD_ORIENT
from docx.shared import Pt
from openpyxl import Workbook
from openpyxl.styles import Font
import pandas as pd
import streamlit as st

from calc_common.report_helper import (
    add_word_table,
    autosize_cols,
    init_word_doc,
    render_export_buttons,
    save_word_doc,
    wb_to_bytes,
    write_columnar_table,
)

ValueGetter = Callable[[dict[str, Any]], Any]
WordRefBuilder = Callable[[Any, list[dict[str, Any]]], None]


@dataclass
class Column:
    header: str
    get: ValueGetter
    color: str | None = None


@dataclass
class ReportSpec:
    prefix: str # jurisdiction & calculator type (eg. nec_voltage_drop)
    report_title: str # eg. Voltage Drop — Calculation Results
    sheet_name: str # name for the excel sheet
    cols: list[Column | tuple[str, ValueGetter]]  # Column, or legacy (header, getter) tuple
    code_reference: Callable[[list[dict[str, Any]]], str]  # "per NEC …" line from queued results
    notes: Callable[[list[dict[str, Any]]], list[str]]  # note lines under the table
    tag: str = "Tag"
    word_reference: WordRefBuilder | None = None  # appends equations/assumptions to the Word report


# ============================================================
# st.session_state helpers
# ============================================================
def _rows_key(spec: ReportSpec) -> str:
    return f"{spec.prefix}_rows"

def _table_key(spec: ReportSpec) -> str:
    return f"{spec.prefix}_table"

def _remove_row_by_index(spec: ReportSpec, index: int):
    rows = get_rows(spec)
    if 0 <= index < len(rows):
        rows.pop(index)

def _remove_row_by_tag(spec: ReportSpec, tag: str):
    rows = get_rows(spec)
    for i, row in enumerate(rows):
        if row["tag"] == tag:
            rows.pop(i)
            break

def get_rows(spec: ReportSpec) -> list[dict[str, Any]]:
    key = _rows_key(spec)
    if key not in st.session_state:
        st.session_state[key] = []
    return st.session_state[key]

def add_row(spec: ReportSpec, tag: str, result: dict[str, Any]):
    get_rows(spec).append({"tag": tag, "result": result})

def remove_row(spec: ReportSpec, identifier: str | int):
    if isinstance(identifier, int):
        _remove_row_by_index(spec, identifier)
    else:
        _remove_row_by_tag(spec, identifier)

def clear(spec: ReportSpec) -> None:
    st.session_state[_rows_key(spec)] = []


# ============================================================
# row builder helpers
# ============================================================

def _as_columns(spec: ReportSpec) -> list[Column]:
    """Normalize spec.cols (Column objects and/or legacy (header, getter) tuples)."""
    return [c if isinstance(c, Column) else Column(c[0], c[1]) for c in spec.cols]

def _safe(get: ValueGetter, result: dict[str, Any]) -> Any:
    try:
        val = get(result)
    except Exception:
        return "—"
    return val if val not in (None, "") else "—"

def _headers(spec: ReportSpec) -> list[str]:
    return [spec.tag] + [c.header for c in _as_columns(spec)]

def _build_table_rows(spec: ReportSpec, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    columns = _as_columns(spec)
    table_rows: list[dict[str, Any]] = []
    for row in rows:
        result = row.get("result", {})
        data_row: dict[str, Any] = {spec.tag: row.get("tag", "")}
        for c in columns:
            data_row[c.header] = _safe(c.get, result)
        table_rows.append(data_row)
    return table_rows

def _set_landscape(doc) -> None:
    """Widen to landscape so the multi-column schedule table isn't cramped."""
    try:
        section = doc.sections[0]
        width, height = section.page_width, section.page_height
        if width is None or height is None:
            return
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_width, section.page_height = max(width, height), min(width, height)
    except Exception:
        pass

def build_schedule_word(spec: ReportSpec, rows: list[dict[str, Any]]):
    results = [row.get("result", {}) for row in rows]
    doc = init_word_doc(spec.report_title)
    _set_landscape(doc)

    meta = doc.add_paragraph()
    meta_run = meta.add_run(
        f"Generated {datetime.now().strftime('%B %d, %Y · %I:%M %p')}   |   {spec.code_reference(results)}"
    )
    meta_run.italic = True
    meta_run.font.size = Pt(9)

    add_word_table(doc, _headers(spec), _build_table_rows(spec, rows), font_size_header=8, font_size=8)

    # Calculator-supplied reference content (equations, etc.).
    if spec.word_reference:
        spec.word_reference(doc, results)

    for note in spec.notes(results):
        para = doc.add_paragraph()
        note_run = para.add_run(f"Note: {note}")
        note_run.italic = True
        note_run.font.size = Pt(8)

    return save_word_doc(doc)

def build_schedule_excel(spec: ReportSpec, rows: list[dict[str, Any]]):
    results = [row.get("result", {}) for row in rows]

    wb = Workbook()

    # One sheet: the schedule table (headers on row 1, data below), then the code
    # reference and notes underneath it. Per-row citations live in the table's own
    # reference columns, so there is nothing left to put on a second tab.
    ws = wb.active
    ws.title = spec.sheet_name
    row = write_columnar_table(ws, 1, None, _build_table_rows(spec, rows), _headers(spec))

    # Size columns to the table before the long footer lines land, so the notes
    # overflow to the right rather than stretching column A to fit them.
    autosize_cols(ws)

    meta = ws.cell(row=row, column=1)
    meta.value = (
        f"Generated {datetime.now().strftime('%B %d, %Y · %I:%M %p')}"
        f"   |   {spec.code_reference(results)}"
    )
    meta.font = Font(bold=True)
    row += 2

    for note in spec.notes(results):
        cell = ws.cell(row=row, column=1, value=f"Note: {note}")
        cell.font = Font(italic=True, size=9)
        row += 1

    return wb_to_bytes(wb)
    
# ============================================================
# UI
# ============================================================

def render_schedule_commit(spec: ReportSpec, result: dict[str, Any] | None, can_add: bool) -> None:
    rows = get_rows(spec)
    placeholder = f"Calc {len(rows) + 1}"

    with st.form(f"{spec.prefix}_add_form", clear_on_submit=True, border=False):
        tag = st.text_input(spec.tag, key=f"{spec.prefix}_tag", placeholder=placeholder)
        submitted = st.form_submit_button(
            "Add to schedule",
            width="stretch",
            disabled=not can_add,
            type="primary"
        )

    if not can_add:
        st.caption("Enter valid inputs to add this calculation to the schedule.")
    elif rows:
        st.caption(f"{len(rows)} in schedule")

    if submitted and result is not None:
        add_row(spec, tag.strip() or placeholder, result)
        st.rerun()


def render_schedule_table(spec: ReportSpec) -> None:
    rows = get_rows(spec)

    st.markdown("### Report schedule")

    if not rows:
        st.caption("Nothing queued yet. Set up a circuit above, then use **Add to schedule**.")
        return
    c1, _, c2 = st.columns(3)
    c1.caption(f"{len(rows)} calculation{'s' if len(rows) != 1 else ''} queued — select rows to remove them.")
    
    remove_col, clear_col = c2.columns(2)
    
    state = st.dataframe(
        pd.DataFrame(_build_table_rows(spec, rows), columns=_headers(spec)),
        width="stretch",
        on_select="rerun",
        selection_mode="multi-row",
        key=_table_key(spec),
    )
    selected = list(getattr(state, "selection", {}).get("rows", []))


    if remove_col.button(
        f"Remove selected ({len(selected)})",
        key=f"{spec.prefix}_remove_selected",
        disabled=not selected,
        width="stretch",
    ):
        for index in sorted(selected, reverse=True):
            remove_row(spec, int(index))
        st.rerun()

    if clear_col.button("Clear all", key=f"{spec.prefix}_clear_all", width="stretch"):
        clear(spec)
        st.rerun()
    
    

    render_export_buttons(
        prefix=spec.prefix,
        docx_file=f"{spec.prefix}.docx",
        xlsx_file=f"{spec.prefix}.xlsx",
        can_export=True,
        word_builder=lambda: build_schedule_word(spec, get_rows(spec)),
        excel_builder=lambda: build_schedule_excel(spec, get_rows(spec)),
    )


def render_schedule_ui(spec: ReportSpec, result: dict[str, Any] | None, can_add: bool):
    st.markdown("### Add to report")
    render_schedule_commit(spec, result, can_add)
    st.divider()
    render_schedule_table(spec)