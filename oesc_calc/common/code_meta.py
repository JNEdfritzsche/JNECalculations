from __future__ import annotations

from lib import oesc_tables


def oesc_edition(table_id: str | None = None) -> str:
    return f"OESC {oesc_tables.edition_of(table_id)}"


def table_title(table_id: str) -> str:
    return oesc_tables.TITLE_OVERRIDES.get(table_id, f"Table {table_id}")


def cite(table_ids) -> str:
    seen = []
    for table_id in table_ids or []:
        if table_id and table_id not in seen:
            seen.append(table_id)
    return ", ".join(seen) if seen else "—"
