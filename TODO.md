# TODO

## Pending

- [ ] Verify transformer protection calculator fix with @jnenzuvela and close the GitHub issue
  - Fix: `>750V, P&S, 7.5% < Z ≤ 10%` secondary branch now splits on Vsec (≤750V → F:250%/CB:250%, >750V → F:125%/CB:250%)
- [ ] Calculation documents — old design basis docs markup
- [ ] Table checking — confirm all table values being used are correct
- [ ] Stage 1 Release: Approval — final stage for release 1.0

## App — Incomplete Calculators

- [ ] **Power Factor Correction** — currently a placeholder (`st.info("Placeholder — content coming soon.")`); needs full calculator logic (capacitor sizing, reactive power, kVAR correction)

## Documentation — NEC Variants (all currently stubs)

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

## Examples & Validation

- [ ] Motor Protection — validation
- [ ] TX Protection — validation
- [ ] Cable Tray — validation

## Recently Completed

- [x] Motor Protection calculator — full calculator with Table 29 logic, Word/Excel export
- [x] TX Protection calculator — full calculator with flowchart impedance logic, Word/Excel export
- [x] Motor Protection examples — worked examples in `motor_protection_examples_oesc.md`
- [x] TX Protection examples — worked examples in `transformer_protection_examples_nec.md`
- [x] Cable Tray examples — worked examples in `cable_tray_fill_examples_oesc.md`
- [x] Transformer Protection NEC theory — `transformer_protection_nec.md` has real NEC 450.3 methodology
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
