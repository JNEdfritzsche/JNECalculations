"""Load NEC code tables from the CSV files in data/nec_tables/.

Each table is one CSV carrying its own metadata as `#` front matter, so the data and
everything describing it live in a single file that can be read next to the codebook page.
See data/nec_tables/README.md for the authoring guide.

The dicts returned here are the same shape `make_table()` produces, so nothing downstream
needs to know whether a table came from a CSV or from Python.
"""

from __future__ import annotations

import csv
import difflib
import re
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "nec_tables"

# Front matter directives. Anything else is either a free comment (no colon) or an error,
# so that a misspelled `# titel:` is caught instead of silently dropping the title.
SINGLE_KEYS = {"title", "edition", "source", "units", "condition", "header_rows"}
LIST_KEYS = {"note"}
COLUMN_TYPE_KEYS = {"text", "number"}
DIRECTIVE_KEYS = SINGLE_KEYS | LIST_KEYS | COLUMN_TYPE_KEYS

_DIRECTIVE = re.compile(r"^#\s*([A-Za-z][A-Za-z0-9_]*)\s*:\s?(.*)$")
_CONTINUATION = re.compile(r"^#\s{2,}(\S.*)$")
_INTEGER = re.compile(r"^[+-]?\d+$")

# float() accepts these, and every one of them would be a silent data error.
_NOT_NUMBERS = {"nan", "inf", "-inf", "+inf", "infinity", "-infinity", "+infinity"}

# Tables that have been loaded, keyed by id. `nec_tables.py` re-exports this as TABLES,
# so declaring a table is what registers it — there is no second list to keep in step.
TABLES: dict[str, dict[str, Any]] = {}

# Every id a `nec_table()` call asked for, so the checker can spot a CSV that no
# constant declares (and vice versa).
DECLARED: set[str] = set()

_GROUP_PARTS: dict[str, dict[str, dict[str, Any]]] = {}


class TableFormatError(Exception):
    """A CSV could not be read as a table. The message names the file and the fix."""


def _fail(path: Path, message: str, line: int | None = None) -> None:
    where = f"{path.name}:{line}" if line else path.name
    raise TableFormatError(f"{where}: {message}")


def _did_you_mean(word: str, options) -> str:
    close = difflib.get_close_matches(word, sorted(options), n=1)
    return f"\n    did you mean: {close[0]}" if close else ""


# ----------------------------
# front matter
# ----------------------------
def _parse_front_matter(lines: list[str], path: Path) -> tuple[dict[str, Any], int]:
    """Read the leading `#` block. Returns the directives and the index of the first
    non-comment line."""
    single: dict[str, str] = {}
    notes: list[str] = []
    text_cols: list[str] = []
    number_cols: list[str] = []
    last_key: str | None = None
    index = len(lines)

    for position, raw in enumerate(lines):
        line = raw.rstrip("\n\r")
        if not line.lstrip().startswith("#"):
            index = position
            break

        match = _DIRECTIVE.match(line)
        continuation = _CONTINUATION.match(line)

        if match is None:
            if continuation and last_key:
                # a wrapped directive, e.g. a title too long for one line
                if last_key in LIST_KEYS:
                    notes[-1] += " " + continuation.group(1).strip()
                else:
                    single[last_key] += " " + continuation.group(1).strip()
            else:
                last_key = None  # a plain comment
            continue

        key, value = match.group(1).lower(), match.group(2).rstrip()

        if key not in DIRECTIVE_KEYS:
            _fail(
                path,
                f"unknown setting '# {key}:'\n"
                f"    valid settings are: {', '.join(sorted(DIRECTIVE_KEYS))}"
                f"{_did_you_mean(key, DIRECTIVE_KEYS)}",
                position + 1,
            )

        if key in SINGLE_KEYS:
            if key in single:
                _fail(path, f"'# {key}:' is given more than once", position + 1)
            single[key] = value.strip()
            last_key = key
        elif key in LIST_KEYS:
            notes.append(value.strip())
            last_key = key
        elif key == "text":
            text_cols.append(value.strip())
            last_key = None
        elif key == "number":
            number_cols.append(value.strip())
            last_key = None

    return (
        {
            "single": single,
            "notes": notes,
            "text_columns": text_cols,
            "number_columns": number_cols,
        },
        index,
    )


# ----------------------------
# headers
# ----------------------------
def _resolve_tier(tier_row: list[str], width: int) -> list[str | None]:
    """An empty cell in a tier row continues the heading to its left, which is how the
    codebook prints a banded header. A leading empty cell means no heading at all."""
    resolved: list[str | None] = []
    current: str | None = None
    for i in range(width):
        cell = tier_row[i].strip() if i < len(tier_row) else ""
        if cell:
            current = cell
        resolved.append(current)
    return resolved


def _build_column_tiers(tiers: list[list[str]], columns: list[str]) -> dict[str, list[str]]:
    """Map each column key to the headings stacked above it, outermost first."""
    resolved = [_resolve_tier(tier, len(columns)) for tier in tiers]
    return {
        column: [tier[i] for tier in resolved if tier[i] is not None]
        for i, column in enumerate(columns)
    }


# ----------------------------
# cell values
# ----------------------------
def _to_number(value: str) -> int | float | None:
    """Return the number a cell holds, or None if it does not hold one. Thousands
    separators are deliberately not accepted — '1,500' is text, write 1500."""
    text = value.strip()
    if not text or text.lower() in _NOT_NUMBERS or "_" in text:
        return None
    if _INTEGER.match(text):
        return int(text)
    try:
        return float(text)
    except ValueError:
        return None


def _type_columns(
    columns: list[str],
    rows: list[list[str]],
    text_columns: list[str],
    number_columns: list[str],
    path: Path,
) -> dict[str, bool]:
    """Decide per column whether it holds numbers, for the whole column at once.

    Typing cell by cell would split a column like size_awg_kcmil into 14 (int) and '1/0'
    (str), and every lookup keyed on the numeric sizes would then silently miss.
    """
    forced_number = "rest" in number_columns
    named_numbers = {c for c in number_columns if c != "rest"}

    for declared in set(text_columns) | named_numbers:
        if declared not in columns:
            _fail(
                path,
                f"'{declared}' is declared in the front matter but is not a column"
                f"{_did_you_mean(declared, columns)}",
            )

    numeric: dict[str, bool] = {}
    for index, column in enumerate(columns):
        cells = [row[index] for row in rows if index < len(row) and row[index].strip()]

        if column in text_columns:
            numeric[column] = False
            continue

        if column in named_numbers or forced_number:
            for row_number, cell in enumerate(cells, start=1):
                if _to_number(cell) is None:
                    _fail(
                        path,
                        f"column '{column}' is declared '# number:' but row {row_number} "
                        f"contains '{cell}', which is not a number\n"
                        f"    either fix the cell, or leave it empty if the codebook has no value",
                    )
            numeric[column] = True
            continue

        numeric[column] = bool(cells) and all(_to_number(c) is not None for c in cells)

    return numeric


# ----------------------------
# loading
# ----------------------------
def read_table_file(path: Path) -> dict[str, Any]:
    """Parse one CSV into the table dict shape used across the app."""
    if not path.exists():
        raise TableFormatError(
            f"{path.name}: no such file in {DATA_DIR}"
            f"{_did_you_mean(path.name, [p.name for p in DATA_DIR.glob('*.csv')])}"
        )

    try:
        raw = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise TableFormatError(
            f"{path.name}: not valid UTF-8 ({exc}). Re-save the file as UTF-8 — in Excel "
            f"that is 'CSV UTF-8 (Comma delimited)'."
        ) from None

    lines = raw.splitlines()
    front, start = _parse_front_matter(lines, path)

    body = list(csv.reader(lines[start:]))
    body_offset = start + 1  # 1-based physical line number of body[0]

    if not body:
        _fail(path, "the file has front matter but no column names and no data")

    header_rows = 1
    if "header_rows" in front["single"]:
        given = front["single"]["header_rows"]
        if not _INTEGER.match(given):
            _fail(path, f"'# header_rows:' must be a whole number, got '{given}'")
        header_rows = int(given)
        if header_rows < 1:
            _fail(path, "'# header_rows:' must be at least 1")
        if header_rows > len(body):
            _fail(path, f"'# header_rows: {header_rows}' but the file only has {len(body)} rows")

    tier_rows = body[: header_rows - 1]
    columns = [c.strip() for c in body[header_rows - 1]]
    data_rows = body[header_rows:]
    header_line = body_offset + header_rows - 1

    if not columns or not any(columns):
        _fail(path, "the column-name row is empty", header_line)
    if "" in columns:
        _fail(path, f"column {columns.index('') + 1} has no name", header_line)
    duplicates = {c for c in columns if columns.count(c) > 1}
    if duplicates:
        _fail(path, f"duplicate column name(s): {', '.join(sorted(duplicates))}", header_line)

    for tier_index, tier in enumerate(tier_rows):
        if len(tier) > len(columns):
            _fail(
                path,
                f"header tier row has {len(tier)} cells but there are {len(columns)} columns",
                body_offset + tier_index,
            )

    cleaned: list[list[str]] = []
    line_numbers: list[int] = []
    for offset, row in enumerate(data_rows):
        if not any(cell.strip() for cell in row):
            continue  # blank rows, which spreadsheets append freely
        line = body_offset + header_rows + offset
        if len(row) != len(columns):
            _fail(
                path,
                f"row has {len(row)} values but {len(columns)} columns were given\n"
                f"    row: {','.join(row)}",
                line,
            )
        cleaned.append(row)
        line_numbers.append(line)

    numeric = _type_columns(columns, cleaned, front["text_columns"], front["number_columns"], path)

    rows: list[dict[str, Any]] = []
    for row in cleaned:
        record: dict[str, Any] = {}
        for index, column in enumerate(columns):
            cell = row[index].strip()
            if not cell:
                record[column] = None
            elif numeric[column]:
                record[column] = _to_number(cell)
            else:
                record[column] = row[index]
        rows.append(record)

    single = front["single"]
    if not single.get("title"):
        _fail(path, "'# title:' is missing — every table needs one")

    table: dict[str, Any] = {
        "title": single["title"],
        "columns": columns,
        "rows": rows,
    }
    for key in ("edition", "source", "units", "condition"):
        if single.get(key):
            table[key] = single[key]
    if front["notes"]:
        table["notes"] = front["notes"]
    if tier_rows:
        table["header_tiers"] = tier_rows
        table["column_tiers"] = _build_column_tiers(tier_rows, columns)

    table["_source_file"] = str(path)
    table["_line_numbers"] = line_numbers
    table["_declared_types"] = set(front["text_columns"]) | set(front["number_columns"])
    return table


def nec_table(table_id: str, group: str | None = None) -> dict[str, Any]:
    """Load data/nec_tables/<table_id>.csv and register it.

    Declaring the constant is what puts the table in TABLES, so there is no separate
    registry to keep in step. Group parts register under their group instead.
    """
    DECLARED.add(table_id)
    table = read_table_file(DATA_DIR / f"{table_id}.csv")
    table["_id"] = table_id

    if group is None:
        TABLES[table_id] = table
    else:
        part_key = table_id[len(group) + 1 :] if table_id.startswith(f"{group}_") else table_id
        _GROUP_PARTS.setdefault(group, {})[part_key] = table
    return table


def nec_group(group_id: str, title: str) -> dict[str, Any]:
    """Assemble the parts declared with `group=` into the one table they are printed as.

    Chapter 9 Table 4 is a single table published as 13 sections; each section is its own
    CSV, and the order they are declared in is the order they appear in the app.
    """
    parts = _GROUP_PARTS.get(group_id)
    if not parts:
        raise TableFormatError(
            f"{group_id}: nec_group() was called before any part declared group='{group_id}'"
        )

    columns = next(iter(parts.values()))["columns"]
    for part_key, part in parts.items():
        if part["columns"] != columns:
            raise TableFormatError(
                f"{group_id}: section '{part_key}' has different columns from the others.\n"
                f"    every section of a grouped table must share one column list."
            )

    table = {"title": title, "columns": columns, "tables": parts, "_id": group_id}
    TABLES[group_id] = table
    return table


def register_python_table(table_id: str, table: dict[str, Any]) -> dict[str, Any]:
    """Register a table still defined in Python, so CSV-backed and Python-backed tables
    work side by side while the data is being converted."""
    table.setdefault("_id", table_id)
    table["_python"] = True
    TABLES[table_id] = table
    return table


# ----------------------------
# navigating a decked header
# ----------------------------
def column_tiers(table: dict[str, Any], column: str) -> list[str]:
    """The headings stacked above one column, outermost first."""
    return table.get("column_tiers", {}).get(column, [])


def columns_under(table: dict[str, Any], *tier_path: str) -> list[str]:
    """Every column sitting under the given headings, in table order.

    columns_under(TABLE_310_16, "Copper") -> the three copper ampacity columns.
    """
    tiers = table.get("column_tiers")
    if not tiers:
        return []
    wanted = [t.strip().lower() for t in tier_path]
    return [
        column
        for column, path in tiers.items()
        if [p.strip().lower() for p in path[: len(wanted)]] == wanted
    ]


def column_at(table: dict[str, Any], *tier_path: str) -> str:
    """The single column under the given headings.

    Use this instead of building a column name by string formatting: if the table changes,
    this raises with the real headings rather than quietly returning nothing.
    """
    found = columns_under(table, *tier_path)
    if len(found) == 1:
        return found[0]

    path = " > ".join(tier_path)
    if not found:
        available = sorted({" > ".join(p) for p in table.get("column_tiers", {}).values()})
        raise KeyError(
            f"{table.get('title', '<table>')}: no column under '{path}'.\n"
            f"    headings are: {'; '.join(available) or '(this table has no header tiers)'}"
        )
    raise KeyError(
        f"{table.get('title', '<table>')}: '{path}' covers {len(found)} columns "
        f"({', '.join(found)}) — name a deeper heading to pick one."
    )


def tier_values(table: dict[str, Any], level: int = 0) -> list[str]:
    """The distinct headings at one level of the header, in table order."""
    seen: list[str] = []
    for path in table.get("column_tiers", {}).values():
        if len(path) > level and path[level] not in seen:
            seen.append(path[level])
    return seen


__all__ = [
    "DATA_DIR",
    "TABLES",
    "DECLARED",
    "TableFormatError",
    "read_table_file",
    "nec_table",
    "nec_group",
    "register_python_table",
    "column_tiers",
    "columns_under",
    "column_at",
    "tier_values",
]
