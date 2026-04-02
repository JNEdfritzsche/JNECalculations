# TODO

## Pending

- [ ] Verify transformer protection calculator fix with @jnenzuvela and close the GitHub issue
  - Fix: `>750V, P&S, 7.5% < Z ≤ 10%` secondary branch now splits on Vsec (≤750V → F:250%/CB:250%, >750V → F:125%/CB:250%)

## App — Incomplete Calculators

- [ ] **Power Factor Correction** — currently a placeholder (`st.info("Placeholder — content coming soon.")`); needs full calculator logic (capacitor sizing, reactive power, kVAR correction)

## Documentation — NEC Variants (all currently stubs)

All 8 calculators with complete OESC docs are missing equivalent NEC content:

- [ ] Transformer Protection — `content/markdown/transformer_protection_nec.md`
- [ ] Transformer Feeders — `content/markdown/transformer_feeders_nec.md`
- [ ] Motor Protection — `content/markdown/motor_protection_nec.md`
- [ ] Motor Feeders — `content/markdown/motor_feeder_nec.md`
- [ ] Cable Tray Fill — `content/markdown/cable_tray_fill_nec.md`
- [ ] Conduit Fill — `content/markdown/conduit_fill_nec.md`
- [ ] Voltage Drop — `content/markdown/voltage_drop_nec.md`
- [ ] Conductors — `content/markdown/conductors_nec.md`

## Documentation — Incomplete OESC + NEC (both sparse)

- [ ] Heat Trace — `heat_trace_oesc.md` & `heat_trace_nec.md` (basic load formula only, needs full methodology)
- [ ] Power Factor Correction — `power_factor_correction_oesc.md` & `power_factor_correction_nec.md` (stubs, "coming soon")
- [ ] Grounding/Bonding examples — `grounding_bonding_examples_oesc.md` & `grounding_bonding_examples_nec.md` (placeholder text only)
- [ ] Grounding/Bonding NEC — `grounding_bonding_nec.md` (stub, "under development")
- [ ] Demand Load NEC — `demand_load_nec.md` (stub, no content)

## Recently Completed

- [x] Transformer protection flowchart logic fix (>750V P&S, 7.5–10% Z secondary branch)
- [x] Table hyperlinks in theory/examples tabs — `Table X` references auto-link to Table Library
- [x] Table 50 added to table registry with full data
- [x] Table 16 added to table registry with full data
- [x] `oesc_tables.py` table definitions reordered numerically (1→50, then D2→D_SYSTEM_FACTOR)
- [x] Appendix hyperlinks — navigate to correct table via `?table=X` query param
- [x] Singular "Tables X" naming fixed across markdown files
- [x] Transformer protection examples moved to Examples tab
- [x] `lib/theory.py` and `streamlit_app.py` cleanup/refactor
- [x] Demand Load OESC theory written (Section 8)
- [x] Grounding/Bonding OESC theory written (Section 10)
- [x] Grounding/Bonding calculator replaced with real Table 16 lookup (Rule 10-616)
