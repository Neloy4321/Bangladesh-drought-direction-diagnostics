# Evidence release and integrity checks

## Archived execution

- Run state: **COMPLETE_OFFICIAL / FINISHED** (from `Run_Progress.json`).
- Evaluation configurations: **15,600** (6 systems × 200 synthetic realizations × [6 masks × 2 strategies + complete]).
- Null calibration: **2,160** records; at least 120 finite scores for each estimable CCM stratum.
- Saved final integrity tests: **8/8 pass**.
- Saved preflight: **40/40 pass**.
- Official run versions: Python 3.13.18; pyEDM 2.5.7; Tigramite 5.2.10.1; NumPy 2.1.3; pandas 2.3.3; SciPy 1.16.3.
- Distinct simulation IDs: 200 per system (1,200 total).
- Eligible method rows across 15,600 attempts: CCM **10,800**, PCMCI **9,342**, Granger **10,800**; conditioned-lag OLS **10,800**.

## Exact external archive file digests (SHA-256)

These are cryptographic digests of archived files; the *full raw checkpoints themselves are NOT included* in this initial public release.

| File (inside author archive `Paper2_OneClick_OUTPUTS.zip`) | SHA-256 |
|---|---|
| `Official_Final_Summary.csv` | `0f87592e9f5a4daf29e554a6ad01dab40ca27c5ed90ee0f7fc2882b7ed4c8861` |
| `Paired_Weather_minus_Empirical_Bootstrap.csv` | `d1d24ef19e68adbcf42ec8d42262656c7b4185cd614f07bfa3fc03665f9473e1` |
| `Official_Eval_Checkpoint.csv` | `d0b74bf72c76a526d564685874f583c078e3b3f87363666516fd25356c375ddf` |
| `Official_Null_Scores_Checkpoint.csv` | `33276245b07c8822768c3254bc50e5adf10a2a2e7ab5c08526f64ad17d009647` |
| `Final_Integrity_Checks.csv` | `47f5c549d4cedaddbf4f45026d55b43ab664b5d06a6ea66c153ef9246041e22a` |
| `Existing_Field_CCM_Support_Snapshot.csv` | `dccaa56b7049f23eba45b3a24bcf6543ccedba966eab09a7b9252397086c9dbd` |
| `Official_Config.json` | `f2f9163c5885cedfdeadb9e4c4ebbc56f91c3380e05f9a61ed117fe1ee2187d4` |

**Byte-level distinction:** The public `results/official/Official_Final_Summary.csv` is a normalized, numerically equivalent transcription of the completed 72-row summary (same attempted/eligible/detected counts and derived fractions); it is **not guaranteed byte-for-byte identical** to the author's original Kaggle CSV. The SHA-256 digests above identify the **original unmodified files inside the archived Kaggle ZIP**, not the GitHub-normalized copy. Use the supplied raw archive if an exact SHA or p-value rerun is required.

The raw archive was independently read after execution: all **72** summary rows matched the raw per-evaluation counts, and 10,800 finite CCM p-values matched reference-null recalculation to floating-point precision. This is a computational-consistency check, **not** a scientific proof of causality.

## How to verify

```bash
pip install -r requirements.txt
python scripts/verify_results.py
python scripts/verify_results.py --kaggle-zip /path/to/Paper2_OneClick_OUTPUTS.zip
```

The second command independently counts per-method outcomes and checks CCM null-calibrated p-values against the supplied raw trace.

### Material deliberately excluded

- Proprietary/restricted raw BMD, external reanalysis/satellite data and BBS source files.
- Unpublished manuscript drafts and identifying author correspondence.
- Experimental synthetic regression or independently coded CCM **development pilots** presented as if they were official pyEDM/Tigramite outputs.
- The submitted Paper 1's event-preserving precipitation-correction workflow.

## Citation and journal policy

This repository is a public evidence index; a double-anonymous journal may require a private or anonymized reviewer package. Verify permissions and anonymity requirements before referencing this URL in a submitted manuscript.
