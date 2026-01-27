# lib/__init__.py
"""
lib package initializer.

Expose the essential OESC table names and helpers so imports from the
main app can be simple, e.g.:

    from lib.oesc_tables import get_table_area_mm2, TABLE_6A
    # or
    from lib import oesc_tables

"""

from . import oesc_tables

# explicit exports (optional)
__all__ = [
    "oesc_tables",
    # convenience top-level exports:
    "get_table_entry",
    "get_table_area_mm2",
    "get_table_diameter_mm",
    "TABLE_6A",
    "TABLE_6B",
    "TABLE_6C",
    "TABLE_6D",
    "TABLE_6E",
    "TABLE_6F",
    "TABLE_6G",
    "TABLE_6H",
    "TABLE_6I",
    "TABLE_6J",
    "TABLE_6K",
    "TABLE_9A",
    "TABLE_9B",
    "TABLE_9C",
]

# re-export helpers conveniently at package level
get_table_entry = oesc_tables.get_table_entry
get_table_area_mm2 = oesc_tables.get_table_area_mm2
get_table_diameter_mm = oesc_tables.get_table_diameter_mm

# re-export major tables (so you can: from lib import TABLE_6A)
TABLE_6A = oesc_tables.TABLE_6A
TABLE_6B = oesc_tables.TABLE_6B
TABLE_6C = oesc_tables.TABLE_6C
TABLE_6D = oesc_tables.TABLE_6D
TABLE_6E = oesc_tables.TABLE_6E
TABLE_6F = oesc_tables.TABLE_6F
TABLE_6G = oesc_tables.TABLE_6G
TABLE_6H = oesc_tables.TABLE_6H
TABLE_6I = oesc_tables.TABLE_6I
TABLE_6J = oesc_tables.TABLE_6J
TABLE_6K = oesc_tables.TABLE_6K
TABLE_9A = oesc_tables.TABLE_9A
TABLE_9B = oesc_tables.TABLE_9B
TABLE_9C = oesc_tables.TABLE_9C
