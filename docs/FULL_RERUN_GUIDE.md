# Full-model rerun guide (archived protocol)

The public scripts in `src/` expose the same truth-known data-generation and
inferential configuration as the executed Kaggle benchmark:

- `src/truth_known.py`: six DGPs and six original empirical observation masks.
- `src/official_methods.py`: actual pyEDM, Tigramite and Granger calls.
- `scripts/verify_results.py`: exact integrity checks against the archived raw trace.
- `scripts/make_figures.py`: regenerated, directly inspectable vector figures.

**Important:** The current public scripts are **reference modules**, not a
standalone 15,600-run checkpoint orchestration. The original executed one-click
Kaggle notebook and full trace are held in the research archive. Do **not**
claim that invoking the method wrappers alone reproduces the entire published
run. Exact reproducibility additionally requires the original archive,
environment versions, independent null-score calibration and the run's
random-state discipline.

The original experiment used the official `pyEDM 2.5.7` and `tigramite 5.2.10.1`.
For the synthetic missingness comparison it ran 200 independent realizations
for each of six systems, two masked strategies on each of six masks, plus
one complete-data control. The original Kaggle source uses more extensive
checkpoint orchestration and null-loop logic than the compact wrappers here.

If the original Kaggle ZIP is available, this command independently checks
the recorded model p-values against the null calibration:

```bash
python scripts/verify_results.py --kaggle-zip /path/to/Paper2_OneClick_OUTPUTS.zip
```

Neither raw provider data nor identifying manuscript drafts are included
in this public repository without separate coauthor/data-license approval.
