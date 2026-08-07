from __future__ import annotations

from typing import Any

import re
# ----------------------------
# Table Helpers
# ----------------------------

def _rows_from_columns(columns: list[str], data: list[list[Any]]) -> list[dict[str, Any]]:
    """Build list-of-Dicts rows from a columns list and a list-of-lists data matrix."""
    rows: list[dict[str, Any]] = []
    for row in data:
        rows.append({col: row[i] if i < len(row) else None for i, col in enumerate(columns)})
    return rows


def make_table(title: str, columns: list[str], data: list[list[Any]], **meta: Any) -> dict[str, Any]:
    """Build a table dict from columns and a list-of-lists matrix, validating row widths."""
    for i, row in enumerate(data):
        if len(row) != len(columns):
            raise ValueError(
                f"{title}: row {i} has {len(row)} values but {len(columns)} columns were given."
            )
    return {'title': title, 'columns': columns, 'rows': _rows_from_columns(columns, data), **meta}

def get_col_integers(columns: list[str]) -> list[int]:
    integers = []
    for col in columns:
        integer = re.search(r'\d+', col)
        if integer:
            integers.append(int(integer.group()))

    return integers

def get_row_headers(rows: list[dict], header_keys: str | list[str]) -> list[list[str]] | list[str]:
    headers = []
    for row in rows:
        if isinstance(header_keys, str):
            header = row.get(header_keys)
            if header: headers.append(header)
        else:
            row_headers = [row.get(key) for key in header_keys]
            if row_headers:
                headers.append(row_headers)
    return headers
        

def get_table_row(
    table: dict[str, Any],
    criteria: dict[str, Any],
) -> dict[str, Any] | None:
    """First row matching every criterion, or None if the table has no such row.

    A criterion naming a column the table does not have is a mistake rather than a miss,
    so it raises: returning None there would look exactly like 'no matching row' and the
    calculator would quietly show a blank answer.
    """
    columns = table.get("columns") or []
    unknown = [key for key in criteria if key not in columns]
    if unknown:
        raise KeyError(
            f"{table.get('title', '<table>')}: no column {unknown}. "
            f"Columns are: {columns}"
        )

    for row in table["rows"]:
        if all(row.get(key) == value for key, value in criteria.items()):
            return row
    return None


def get_populated_columns(
    row: dict[str, Any] | None,
    columns: list[str] | None = None,
) -> list[str]:
    if row is None:
        return []
    keys = columns if columns is not None else list(row.keys())
    return [col for col in keys if row.get(col) is not None]

        