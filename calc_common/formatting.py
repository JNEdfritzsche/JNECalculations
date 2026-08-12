from __future__ import annotations

import re

from lib.nec_tables import NEC_2406A_STANDARD


def _safe_float(x):
    """Convert to float, returning None on failure."""
    try:
        return None if x is None else float(x)
    except Exception:
        return None

def _norm(s):
    """Normalize a value to a stripped string."""
    return str(s).strip()

def _lower(s):
    """Normalize a value to a lowercase stripped string."""
    return _norm(s).lower()

def _to_float(x):
    """Convert to float, handling None, dashes, commas, and empty strings."""
    try:
        if x is None:
            return None
        if isinstance(x, (int, float)):
            return float(x)
        s = str(x).strip()
        if s in ("", "—", "-", "–", "None"):
            return None
        return float(s.replace(",", ""))
    except Exception:
        return None

def _best_col(cols, include=(), exclude=()):
    """Return first column name containing ALL include tokens and NONE of exclude tokens (case-insensitive)."""
    for c in cols:
        lc = _lower(c)
        if all(t in lc for t in include) and not any(t in lc for t in exclude):
            return c
    return None

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

def next_standard(value, standard_list=NEC_2406A_STANDARD):
    """Return the next standard value >= value. If value exceeds the list, return None."""
    try:
        v = float(value)
    except Exception:
        return None

    for s in standard_list:
        if s >= v - 1e-12:
            return s
    return None

def next_standard_size(
    value: float,
    sizes: list[float],
    direction: str = "up",
) -> float | None:
    ordered = sorted(sizes)
    
    if direction == "up":
        return next((s for s in ordered if s >= value), None)
    if direction == "down":
        return next((s for s in reversed(ordered) if s <= value), None)

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

__all__ = [
    "_safe_float", "_norm", "_lower", "_to_float", "_best_col", "fmt", "safe_div",
    "_numeric_sort_key", "_numeric_sort", "format_cond_size", "next_standard",
    "next_standard_size", "select_table9_fill_rule",
]
