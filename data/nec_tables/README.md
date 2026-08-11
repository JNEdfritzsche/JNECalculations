# NEC Tables

One CSV per table. Tables are grouped into versioned subfolders (e.g., `2026/table_310_16.csv`). Metadata lives at the top as `#` comment lines, then the data.

```
# title: Table 310.16 Ampacities of Insulated Conductors...
# edition: 2026
# note: Refer to 310.15(B) for ambient temperature correction.
# header_rows: 3
,Copper,,,Aluminum or Copper-Clad Aluminum,,
Size (AWG or kcmil),60°C,75°C,90°C,60°C,75°C,90°C
size_awg_kcmil,copper_60c_ampacity,copper_75c_ampacity,...
14,15,20,25,,,
```

Only `# title:` is required. Other keys: `# edition:`, `# source:`, `# note:` (one per line), `# condition:`, `# header_rows:` (default 1), `# text:` / `# number:` to force a column type (`# number: rest` covers the remainder).

**Headers** stack the way the book prints them — one row per band, with a final row of `lower_snake_case` names that the code actually reads. A blank cell in a band row spans left.

**Values** are raw data, not typeset. Leave cells empty where the book uses an em dash. Use plain hyphens for ranges (`8-6`) and fractions as printed (`1 1/2`). No thousands separators. Strip footnote markers from values — the footnote text goes in a `# note:` line.

**Filename** mirrors the table number: `Table 430.52(C)(1)` → `2026/table_430_52_c_1.csv`. To register a new table, drop the CSV into the appropriate version folder and add one line to `lib/nec_tables.py`:

```python
TABLE_430_52_C_1 = nec_table("table_430_52_c_1", version="2026")
```

Importing `lib.nec_tables` validates all files and will tell you what's wrong.
