from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

from docx.enum.section import WD_ORIENT
from docx.shared import Pt
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
import pandas as pd
import streamlit as st

from calc_common.formatting import Quantity, fmt
from calc_common.report_helper import (
    add_word_table,
    init_word_doc,
    render_export_buttons,
    report_identity,
    save_word_doc,
    wb_to_bytes,
)

ValueGetter = Callable[[dict[str, Any]], Any]
WordRefBuilder = Callable[[Any, list[dict[str, Any]]], None]

INPUT_HEADER_FILL = PatternFill("solid", fgColor="EDEDED")
RESULT_HEADER_FILL = PatternFill("solid", fgColor="D6E4F0")
RESULT_FONT_COLORS = {"green": "1B7F3B", "blue": "1F4E79"}


RESULTS_SHEET = "Results"
INPUTS_SHEET = "Inputs"

BLANK = (None, "", "—")


@dataclass
class Group:
    """A set of columns the Word report prints in one cell. Excel keeps them apart."""
    label: str
    sep: str = " / "


@dataclass
class Column:
    header: str
    get: ValueGetter
    color: str | None = None  # headline emphasis: green = the answer, blue = the key selection
    result: bool = False  # value the calculator derived, as opposed to one the designer entered
    group: str | None = None  # key into ReportSpec.groups — Word prints the group in one cell
    always: bool = False  # keep the column even when every row shares one value


@dataclass
class ReportSpec:
    code: str # jurisdiction (eg. nec, oesc)
    calculator: str # package directory name (eg. voltage_drop)
    report_title: str # eg. Voltage Drop — Calculation Results
    sheet_name: str # name for the excel sheet
    cols: list[Column | tuple[str, ValueGetter]]  # Column, or legacy (header, getter) tuple
    code_reference: Callable[[list[dict[str, Any]]], str]  # "per NEC …" line from queued results
    notes: Callable[[list[dict[str, Any]]], list[str]]  # note lines under the table
    tag: str = "Tag"
    word_reference: WordRefBuilder | None = None  # appends equations/assumptions to the Word report
    groups: dict[str, Group] = field(default_factory=dict)  # Word-only cell merging
    prefix: str = field(init=False)  # namespaces every session_state and widget key

    def __post_init__(self):
        self.prefix = f"{self.code}_{self.calculator}_schedule"


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

def _rows_for(spec: ReportSpec, rows: list[dict[str, Any]], columns: list[Column]) -> list[dict[str, Any]]:
    table_rows: list[dict[str, Any]] = []
    for row in rows:
        result = row.get("result", {})
        data_row: dict[str, Any] = {spec.tag: row.get("tag", "")}
        for c in columns:
            data_row[c.header] = _safe(c.get, result)
        table_rows.append(data_row)
    return table_rows

def _build_table_rows(spec: ReportSpec, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return _rows_for(spec, rows, _as_columns(spec))

def _result_headers(spec: ReportSpec) -> set[str]:
    return {c.header for c in _as_columns(spec) if c.result}

def _split_columns(spec: ReportSpec) -> list[tuple[str, list[Column]]]:
    """Results first — the answers are what the schedule is read for."""
    columns = _as_columns(spec)
    return [
        (RESULTS_SHEET, [c for c in columns if c.result]),
        (INPUTS_SHEET, [c for c in columns if not c.result]),
    ]

def _partition(columns: list[Column], table_rows: list[dict[str, Any]]) -> tuple[list[Column], list[tuple[str, Any]]]:
    """Columns that vary, and the (header, value) pairs that are the same on every row.

    A column carrying one repeated value says nothing a single line below the table
    cannot. Headline columns are exempt — burying the answer in a footnote is wrong
    even when every row agrees. With fewer than two rows nothing is meaningfully
    constant, so everything is kept.
    """
    if len(table_rows) < 2:
        return columns, []

    kept: list[Column] = []
    constant: list[tuple[str, Any]] = []
    for column in columns:
        values = [row.get(column.header) for row in table_rows]
        if all(v in BLANK for v in values):
            # An empty column states nothing, so there is nothing to hoist either.
            continue
        if column.always or column.color:
            kept.append(column)
        elif len({str(v) for v in values}) == 1:
            constant.append((column.header, values[0]))
        else:
            kept.append(column)
    return kept, constant

def _joined(members: list[Column], sep: str) -> ValueGetter:
    def get(result: dict[str, Any]) -> str:
        parts = [str(_safe(m.get, result)) for m in members]
        # "Not required → Not required" says it twice.
        return parts[0] if len(set(parts)) == 1 else sep.join(parts)
    return get

def _grouped(columns: list[Column], spec: ReportSpec) -> list[Column]:
    """Word only — collapse each declared group into a single column."""
    members: dict[str, list[Column]] = {}
    for column in columns:
        if column.group:
            members.setdefault(column.group, []).append(column)

    out: list[Column] = []
    done: set[str] = set()
    for column in columns:
        key = column.group
        if not key or key not in spec.groups:
            out.append(column)
            continue
        if key in done:
            continue
        done.add(key)
        group_columns = members[key]
        # A group whose other members were hoisted out is just that one column, and
        # labelling a lone trade size "Conduit" would misread.
        if len(group_columns) == 1:
            out.append(group_columns[0])
            continue
        group = spec.groups[key]
        out.append(Column(
            group.label,
            _joined(group_columns, group.sep),
            color=next((c.color for c in group_columns if c.color), None),
            result=any(c.result for c in group_columns),
        ))
    return out

def _constants_line(constant: list[tuple[str, Any]]) -> str:
    return "Same for all rows:   " + "   ·   ".join(f"{header} {value}" for header, value in constant)


# ============================================================
# Excel cell helpers
# ============================================================

def _numbers(values: list[Any]) -> list[float]:
    out = []
    for value in values:
        if isinstance(value, Quantity):
            out.append(value.number)
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            out.append(float(value))
    return out

def _column_unit(values: list[Any]) -> str | None:
    """The one unit a column carries, or None where its rows disagree."""
    units = {v.unit for v in values if isinstance(v, Quantity) and v.unit}
    return units.pop() if len(units) == 1 else None

def _excel_header(header: str, unit: str | None, numeric: bool) -> str:
    if not numeric or not unit or f"({unit})" in header:
        return header
    return f"{header} ({unit})"

def _excel_value(value: Any, numeric: bool, has_numbers: bool) -> Any:
    if isinstance(value, Quantity):
        return value.number if numeric else str(value)
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int, float)):
        return value
    if value in (None, ""):
        return None
    # A blank keeps formulas clean where the column carries numbers; in a text
    # column the dash is the value, so blanking it just looks like missing data.
    if value == "—":
        return None if has_numbers else "—"
    return str(value)

def _number_format(values: list[Any]) -> str | None:
    """One format per column, sized to its smallest value so nothing renders as an exponent."""
    magnitudes = [abs(n) for n in _numbers(values) if n]
    if not magnitudes:
        return None
    decimals = min(8, max(0, 3 - math.floor(math.log10(min(magnitudes)))))
    return "#,##0" + ("." + "#" * decimals if decimals else "")

MIN_COL_WIDTH = 9
MAX_COL_WIDTH = 34
MAX_HEADER_LINES = 4


def _display_len(value: Any) -> int:
    # A float's repr runs far longer than the number format shows it as.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return len(str(value or ""))
    return len(str(fmt(value)))


def _column_width(header: str, cells: list[Any]) -> int:
    """Size to the data, not the header — headers wrap, so a long one like
    'Sec. breaker selected (A)' should not stretch a column of 3-digit values."""
    widest_data = max((_display_len(c) for c in cells), default=0)
    longest_word = min(max((len(w) for w in header.split()), default=0), 14)
    return max(MIN_COL_WIDTH, min(MAX_COL_WIDTH, max(widest_data, longest_word) + 2))


def _write_schedule_table(ws, header_row: int, tag: str, cols: list[Column],
                          table_rows: list[dict[str, Any]]) -> None:
    headers = [tag] + [c.header for c in cols]
    columns: list[Column | None] = [None, *cols]  # the tag column has no Column
    header_lines = 1

    for col_idx, (header, column) in enumerate(zip(headers, columns), start=1):
        values = [row.get(header) for row in table_rows]
        unit = _column_unit(values)
        # Mixed units in one column can't be hoisted into the header, so that column stays text.
        numeric = unit is not None or not any(isinstance(v, Quantity) and v.unit for v in values)
        has_numbers = bool(_numbers(values))
        is_result = bool(column and column.result)

        label = _excel_header(header, unit, numeric)
        cell = ws.cell(row=header_row, column=col_idx, value=label)
        cell.font = Font(bold=True)
        cell.fill = RESULT_HEADER_FILL if is_result else INPUT_HEADER_FILL
        cell.alignment = Alignment(wrap_text=True, vertical="bottom")

        number_format = _number_format(values) if numeric else None
        color = RESULT_FONT_COLORS.get(column.color) if column else None
        font = Font(bold=is_result, color=color) if (is_result or color) else None

        written = []
        for offset, value in enumerate(values, start=1):
            data = ws.cell(row=header_row + offset, column=col_idx,
                           value=_excel_value(value, numeric, has_numbers))
            written.append(data.value)
            if font is not None:
                data.font = font
            if number_format and isinstance(data.value, (int, float)):
                data.number_format = number_format

        width = _column_width(label, written)
        ws.column_dimensions[get_column_letter(col_idx)].width = width
        header_lines = max(header_lines, min(MAX_HEADER_LINES, -(-len(label) // max(1, width - 1))))

    ws.row_dimensions[header_row].height = 14 * header_lines
    ws.freeze_panes = ws.cell(row=header_row + 1, column=1)
    if table_rows:
        last = get_column_letter(len(headers))
        ws.auto_filter.ref = f"A{header_row}:{last}{header_row + len(table_rows)}"

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

    for title, columns in _split_columns(spec):
        kept, constant = _partition(columns, _rows_for(spec, rows, columns))
        if not kept and not constant:
            continue

        heading = doc.add_paragraph().add_run(title)
        heading.bold = True
        heading.font.size = Pt(10)

        if kept:
            display = _grouped(kept, spec)
            add_word_table(
                doc,
                [spec.tag] + [c.header for c in display],
                _rows_for(spec, rows, display),
                font_size_header=8,
                font_size=8,
                bold_columns={c.header for c in display if c.result},
            )

        if constant:
            para = doc.add_paragraph()
            run = para.add_run(_constants_line(constant))
            run.italic = True
            run.font.size = Pt(8)

    # Calculator-supplied reference content (equations, etc.).
    if spec.word_reference:
        spec.word_reference(doc, results)

    for note in spec.notes(results):
        para = doc.add_paragraph()
        note_run = para.add_run(f"Note: {note}")
        note_run.italic = True
        note_run.font.size = Pt(8)

    return save_word_doc(doc)

def _write_identity(ws) -> int:
    row = 1
    for label, value in zip(("Project No.", "Designer"), report_identity()):
        ws.cell(row=row, column=1, value=label).font = Font(bold=True)
        ws.cell(row=row, column=2, value=value)
        row += 1
    return row + 1

def build_schedule_excel(spec: ReportSpec, rows: list[dict[str, Any]]):
    results = [row.get("result", {}) for row in rows]

    wb = Workbook()
    sheets = _split_columns(spec)

    for index, (title, columns) in enumerate(sheets):
        ws = wb.active if index == 0 else wb.create_sheet()
        ws.title = title

        row = _write_identity(ws)
        kept, constant = _partition(columns, _rows_for(spec, rows, columns))
        table_rows = _rows_for(spec, rows, kept)

        _write_schedule_table(ws, row, spec.tag, kept, table_rows)
        row += len(table_rows) + 2

        if constant:
            cell = ws.cell(row=row, column=1, value=_constants_line(constant))
            cell.font = Font(italic=True, size=9)
            row += 2

        if index:
            continue

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

    hoisted = sum(
        len(_partition(columns, _rows_for(spec, rows, columns))[1])
        for _title, columns in _split_columns(spec)
    )
    note = "The exports split results and inputs into separate tables."
    if hoisted:
        note += f" {hoisted} column{'s' if hoisted != 1 else ''} identical on every row move to a note."
    st.caption(note)


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