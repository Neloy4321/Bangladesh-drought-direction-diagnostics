# Bangladesh drought-direction diagnostics — Paper 2

**Reviewer-facing reproducibility materials for a study of observation-calendar and meteorological-source sensitivity in drought-direction diagnostics across Bangladesh.**

> This is **Paper 2**. It is not the separate, already-submitted Paper 1 about transferable reanalysis bias correction. All claims here refer to the archived Paper 2 analyses.

## What is supported

| Evidence | Status | Files |
|---|---|---|
| Archived Bangladesh field diagnostics (36 station locations) | Saved field results; not independent causal ground truth | `results/field/` |
| Official truth-known synthetic benchmark: pyEDM CCM + Tigramite PCMCI + Granger | **Completed in Kaggle**, 6 systems × 200 realizations × 13 scenarios = **15,600 evaluation records** | `results/official/` |
| Null calibration | **2,160 score records**, at least 120 finite reference scores for each estimable CCM stratum | `results/official/` |
| Exact method-level summary | 72 rows, including attempted/eligible/detected and conditional/attempt-based rates | `results/official/Official_Final_Summary.csv` |
| Replicate-cluster paired contrasts | 24 exploratory comparisons, unadjusted percentile intervals | `results/official/Paired_Weather_minus_Empirical_Bootstrap.csv` |
| Original observation geometry | E=2–4 and 1–2 month delays; station eligibility decomposition | `results/eligibility/` |

**Do not infer that a complete meteorology → soil moisture → vegetation causal chain was demonstrated.** Existing PM-based climate-to-soil CCM support was 21/36; direct vegetation links had poor estimability and no supported primary SSMI→NDVI link.

## Repository map

- [Reviewer guide](docs/REVIEWER_GUIDE.md): what each output means, interpretation boundaries and how to check it.
- [Data and licensing](data/README.md): which datasets were used, what is *not* redistributed and why.
- [Methods / protocol](docs/METHODS_AND_PROVENANCE.md): benchmark design and data lineage.
- [Evidence manifest](reproducibility/EVIDENCE_MANIFEST.md): precise provenance of the saved Kaggle experiment.
- [Verified summary tables](results/official/Official_Final_Summary.csv) and [paired contrasts](results/official/Paired_Weather_minus_Empirical_Bootstrap.csv).
- [Field summary](results/field/Existing_Field_CCM_Support_Snapshot.csv).
- [Recreate figures](scripts/make_figures.py) and [verify results](scripts/verify_results.py).
- [Vector figures](figures/): readable directly in GitHub.

## Reproduce the reported summary

```bash
python -m pip install -r requirements.txt
python scripts/verify_results.py
python scripts/make_figures.py
```

The checks above validate the *public summary artifacts*. For the stronger raw-level audit, supply the authors' original `Paper2_OneClick_OUTPUTS.zip` (from the executed Kaggle run):

```bash
python scripts/verify_results.py --kaggle-zip /path/to/Paper2_OneClick_OUTPUTS.zip
```

To regenerate models, the original Paper 2 source archive (including `paper2/results/paper2_master_panel.csv`) is also required. **It is not distributed here** because raw station and gridded-source redistribution rights must be assessed. The genuine execution was with Python 3.13.18, pyEDM 2.5.7, Tigramite 5.2.10.1, NumPy 2.1.3, pandas 2.3.3 and SciPy 1.16.3.

## How to interpret synthetic missingness

The new `weather_month_matched` scenario is a **synthetic observation-selection mechanism dependent on the simulated predictor X**. It exactly preserves month-of-year observation counts from selected real NDVI masks; it is **not measured cloud or rainfall missingness**. There were **1,200 independently seeded system realizations** (200 for each of 6 systems), *not* 15,600 independent physical field experiments. A count of 0 eligible analyses means *not estimable*, not absence of a real effect.

The 120-score Monte Carlo CCM null reference has limited tail resolution; comparisons and confidence intervals in this repository have not been multiplicity-adjusted for all exploratory contrasts.

## Release safeguards

The public repository intentionally excludes original raw BMD/ERA5/MODIS datasets, unverified source copies, third-party journal templates, confidential submission letters, unpublished draft PDFs and identifying metadata beyond the public repository account. A public GitHub URL can compromise double-anonymous review; check the destination journal's policies before including this link in a manuscript.

The repository is an **evidence index, not a certificate of hydrological causality**. Source-derived field inferences and synthetic method benchmarks must be reported separately.

*Authors should verify provenance and have all coauthors approve public release before the final manuscript links this repository.*
