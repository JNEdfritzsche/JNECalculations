# TODO

## Pending

- [ ] Commit and push `.gitignore` update (`.claude/` entry added)
- [ ] Verify transformer protection calculator fix with @jnenzuvela and close the GitHub issue
  - Fix: `>750V, P&S, 7.5% < Z ≤ 10%` secondary branch now splits on Vsec (≤750V → F:250%/CB:250%, >750V → F:125%/CB:250%)

## App — Incomplete Calculators

- [ ] **Power Factor Correction** — currently a placeholder (`st.info("Placeholder — content coming soon.")` at line 5064); needs full calculator logic (capacitor sizing, reactive power, kVAR correction)
- [ ] **Grounding/Bonding** — stub logic with hardcoded AWG values (lines 1844–1863, results say "placeholder"); needs real table lookups from OESC Rule 26-200 / NEC Table 250.102(C)

## App — Navigation

- [ ] Fix appendix hyperlinks to navigate directly to the correct table in the table reference section

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
- [ ] Demand Load — `demand_load_oesc.md` & `demand_load_nec.md` (stubs, no content)
- [ ] Power Factor Correction — `power_factor_correction_oesc.md` & `power_factor_correction_nec.md` (stubs, "coming soon")
- [ ] Grounding/Bonding — `grounding_bonding_oesc.md` & `grounding_bonding_nec.md` (stubs, "under development")
- [ ] Grounding/Bonding examples — `grounding_bonding_examples_oesc.md` & `grounding_bonding_examples_nec.md` (placeholder text only)

## Recently Completed

- [x] Updated calculator logic to reflect new flowchart (transformer protection)
- [x] Refactored transformer protection calculation to follow flowchart
