from __future__ import annotations

from typing import Any

from lib import oesc_tables

SIZE_KEY = "Size (AWG/kcmil)"
AMBIENT_KEY = "Ambient (°C)"


def _rows(table_id: str) -> list[dict[str, Any]]:
    return oesc_tables.get_table_rows(table_id) or []


def temperature_columns(table_id: str) -> list[int]:
    columns = (oesc_tables.get_table_meta(table_id) or {}).get("columns") or []
    temps = []
    for column in columns:
        text = str(column).replace("°C", "").strip()
        if text.isdigit():
            temps.append(int(text))
    return sorted(set(temps))


def ampacity_sizes(table_id: str) -> list[str]:
    return [str(row.get(SIZE_KEY)) for row in _rows(table_id) if row.get(SIZE_KEY) is not None]


def ampacity(table_id: str, size: str, temp_c: int) -> float | None:
    column = f"{temp_c}°C"
    for row in _rows(table_id):
        if str(row.get(SIZE_KEY)) == str(size):
            value = row.get(column)
            return None if value is None else float(value)
    return None


def smallest_size_for(table_id: str, required_ampacity: float, temp_c: int) -> tuple[str | None, float | None]:
    column = f"{temp_c}°C"
    for row in _rows(table_id):
        value = row.get(column)
        if value is None:
            continue
        if float(value) >= float(required_ampacity):
            return str(row.get(SIZE_KEY)), float(value)
    return None, None


def ambient_options() -> list[int]:
    return [int(row[AMBIENT_KEY]) for row in _rows("5A") if row.get(AMBIENT_KEY) is not None]


def temperature_correction(ambient_c: int, temp_rating_c: int) -> float | None:
    column = f"{temp_rating_c}°C"
    for row in _rows("5A"):
        if int(row.get(AMBIENT_KEY, -999)) == int(ambient_c):
            value = row.get(column)
            return None if value is None else float(value)
    return None


def correction_5b(n_conductors: int) -> float | None:
    for row in _rows("5B"):
        if row.get("Number of conductors") == n_conductors:
            return float(row["Correction factor"])
    return None


def correction_5c(n_conductors: int) -> tuple[float | None, str | None]:
    for row in _rows("5C"):
        band = str(row.get("Number of insulated conductors", ""))
        low, _, high = band.replace("–", "-").partition("-")
        try:
            if high:
                if int(low) <= n_conductors <= int(high):
                    return float(row["Ampacity correction factor"]), band
            elif "over" in band.lower():
                if n_conductors >= int("".join(c for c in band if c.isdigit())):
                    return float(row["Ampacity correction factor"]), band
            elif int(low) == n_conductors:
                return float(row["Ampacity correction factor"]), band
        except ValueError:
            continue
    return None, None


def correction_5d_options() -> list[tuple[int, int, float]]:
    options = []
    for row in _rows("5D"):
        try:
            options.append((
                int(row["Horizontal count"]),
                int(row["Vertical layers"]),
                float(row["Correction factor"]),
            ))
        except (KeyError, TypeError, ValueError):
            continue
    return options


def correction_5d(horizontal: int, vertical: int) -> float | None:
    for h, v, factor in correction_5d_options():
        if h == horizontal and v == vertical:
            return factor
    return None
