# Reviewer guide — Paper 2

This repository documents the reproducibility evidence for **observation-calendar and meteorological-source sensitivity in drought-direction diagnostics across Bangladesh**. It is **Paper 2**, distinct from the previously submitted reanalysis bias-correction paper (Paper 1).

## Evidence boundaries

- **Existing field analysis:** 36-location Bangladesh panel; primary SPEI-3 (PM) → surface-soil CCM diagnostic support in 21/36 locations. A full soil-to-vegetation directional chain was **not established**.
- **Official synthetic extension:** 6 truth-known systems, 200 independently seeded realizations per system, 13 analysis configurations per realization = **15,600 attempted model evaluations**, with **2,160 independent CCM null-reference records**. Computed with `pyEDM 2.5.7` and `tigramite 5.2.10.1`; Granger uses the same synthetic realizations.
- **Availability:** 6 previously selected observation masks (S04=90, S06=0, S08=82, S28=94, S30=0, S32=104 available NDVI months, out of 138).
- The **weather-conditioned mask** is a *synthetic value-dependent missingness stress test*, not an observed cloud dataset. It preserves the number of valid observations **within each calendar month**.
- Comparisons among methods are descriptive and conditional on eligibility; 15,600 evaluations are **not** 15,600 independent simulated datasets.
- Observational forcing comparisons are not independent in-situ soil-moisture validation. Non-estimable links must not be interpreted as absent ecological effects.

## How to inspect

1. Read `README.md` and `data/README.md` first.
2. Check `results/official/Official_Final_Summary.csv` (attempted, eligible, detected and both denominators).
3. Check `results/official/Paired_Weather_minus_Empirical_Bootstrap.csv` (exploratory replicate-cluster bootstrap; **not multiplicity-adjusted**).
4. Compare `results/field/Existing_Field_CCM_Support_Snapshot.csv` with the field scope described above.
5. Run `python scripts/verify_results.py` for structural tests, or provide the separately archived original `Paper2_OneClick_OUTPUTS.zip` to verify p-values and raw counts.
6. Use `python scripts/make_figures.py` to reproduce repository SVG/PNG figures from the saved summary tables.

## Disclosure

The public repository intentionally excludes proprietary/third-party raw BMD/NASA/MODIS data, personal details, submission drafts and unpublished cover letters. The original processed research archive and full per-replicate Kaggle checkpoints are retained separately by the research team; access and redistribution are subject to the original providers' terms. Their absence means this repository alone supports **summary-level verification**, not a full independent re-execution of the field-data workflow.

**Submission note:** If the target journal requires double-anonymous review, share a suitably anonymized evidence package or a journal-approved data/code link rather than assuming this public repository is anonymous.
