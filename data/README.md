# Data provenance and redistribution boundaries

The 36-station Bangladesh monthly panel and vegetation-quality masks originated from an author-collected research package. Its sources included BMD daily observations, ERA5-Land, NASA POWER, MODIS vegetation/land surface temperature products and BBS agricultural series. All rights and access terms remain with the providers.

### Input required for a full rerun

The original author-side archive must contain:
```
paper2/results/paper2_master_panel.csv
paper2/results/T2_CCM_configuration.csv
paper2/results/T3_method_agreement.csv
```

Input months for the synthetic missingness masks: **2015-01 through 2026-06** (138 calendar months). Six preselected quality-accepted NDVI masks have counts: S04 90, S06 0, S08 82, S28 94, S30 0, S32 104. The 36-station field master covers 2000-01 through 2026-06 (318 months per station).

**Input master-panel SHA-256 (the bytes actually used in Kaggle):** `1756c44881b1f9deb857e49a79a435ba8d836da2ae65f8dc3765e0f091ab4009`.

The original full research ZIP is **not** uploaded to this public repository. Neither is a rehosted copy of the external datasets. Anyone reproducing the analysis must obtain the source files under their providers' access terms and confirm matching preprocessing/quality controls.

The public `results/` CSVs are derived statistics, not station-level source data. The field and source-dependent results use shared ERA5 meteorological/soil-family information; **they are not independent physical validation**. No new independent in-situ soil-moisture validation is claimed.

### Raw computational evidence

The separate archived `Paper2_OneClick_OUTPUTS.zip` contains `Official_Eval_Checkpoint.csv` (15,600 records) and `Official_Null_Scores_Checkpoint.csv` (2,160 records), along with the summaries published here. The full trace is **not** in this repository's initial public release; see `reproducibility/EVIDENCE_MANIFEST.md` for checksums and auditing instructions. An editor/reviewer seeking full independent verification can request the archive from the authors under an appropriate sharing arrangement.

### Review anonymity

The GitHub repository name/owner may disclose author identity. Do not link a public author-controlled repository in an anonymized submission without checking journal requirements.
