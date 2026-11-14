#!/usr/bin/env python3
"""Verify publicly shared Paper 2 statistics and optionally raw Kaggle trace.

Uses standard-library CSV, hashes and independent calculation of reference-null p.
This is a results-integrity check, NOT independent field causal validation.
"""
import argparse
import csv
import hashlib
import io
import math
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METHODS = {
    "ccm": "ccm_p",
    "pcmci": "pcmci_p",
    "granger": "granger_p",
    "conditional_lag_ols": "cond_ols_p",
}
SYSTEMS = {
    "null_ar", "weak_ar", "strong_ar", "common_driver",
    "null_logistic", "coupled_logistic",
}
STRATEGIES = {"complete", "empirical", "weather_month_matched"}

ARCHIVE_SHA256 = {
    "Official_Final_Summary.csv": "0f87592e9f5a4daf29e554a6ad01dab40ca27c5ed90ee0f7fc2882b7ed4c8861",
    "Paired_Weather_minus_Empirical_Bootstrap.csv": "d1d24ef19e68adbcf42ec8d42262656c7b4185cd614f07bfa3fc03665f9473e1",
    "Official_Eval_Checkpoint.csv": "d0b74bf72c76a526d564685874f583c078e3b3f87363666516fd25356c375ddf",
    "Official_Null_Scores_Checkpoint.csv": "33276245b07c8822768c3254bc50e5adf10a2a2e7ab5c08526f64ad17d009647",
    "Final_Integrity_Checks.csv": "47f5c549d4cedaddbf4f45026d55b43ab664b5d06a6ea66c153ef9246041e22a",
}
EXPECTED = {
    "ccm": (15600, 10800, 1976),
    "pcmci": (15600, 9342, 3519),
    "granger": (15600, 10800, 5329),
    "conditional_lag_ols": (15600, 10800, 4014),
}

def rows_from_text(data):
    if isinstance(data, bytes):
        data = data.decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(data)))

def load_csv(path):
    return rows_from_text(Path(path).read_bytes())

def numeric(value):
    return float(value) if value not in ("", "nan", "NaN", "None") else math.nan

def assert_close(a, b, label):
    if not math.isclose(a, b, rel_tol=1e-11, abs_tol=1e-12):
        raise AssertionError(f"{label}: {a} != {b}")

def check_public_tables(base):
    summary = load_csv(base / "results/official/Official_Final_Summary.csv")
    if len(summary) != 72:
        raise AssertionError(f"Expected 72 summary rows, found {len(summary)}")
    keys = set()
    totals = defaultdict(lambda: [0, 0, 0])
    for r in summary:
        key = (r["system"], r["strategy"], r["method"])
        if key in keys:
            raise AssertionError(f"Duplicate summary key: {key}")
        keys.add(key)
        if key[0] not in SYSTEMS or key[1] not in STRATEGIES or key[2] not in METHODS:
            raise AssertionError(f"Unknown summary key: {key}")
        a, e, d = (int(r[k]) for k in ("attempted", "eligible", "detected"))
        if not (0 <= d <= e <= a):
            raise AssertionError(f"Invalid denominator: {key}: {a}, {e}, {d}")
        if a != (200 if r["strategy"] == "complete" else 1200):
            raise AssertionError(f"Unexpected attempts for {key}: {a}")
        for actual, expected_ratio, label in (
            (numeric(r["eligibility_fraction"]), e/a, "eligibility"),
            (numeric(r["detection_given_eligible"]), d/e if e else math.nan, "conditional"),
            (numeric(r["detection_given_attempted"]), d/a, "attempt"),
        ):
            if math.isnan(expected_ratio):
                if not math.isnan(actual):raise AssertionError(f"{key}: {label} must be NaN")
            else:
                assert_close(actual, expected_ratio, f"{key}: {label}")
        for idx, value in enumerate((a, e, d)):
            totals[r["method"]][idx] += value
    for m, expected in EXPECTED.items():
        if tuple(totals[m]) != expected:
            raise AssertionError(f"{m} totals {totals[m]} != {expected}")

    paired = load_csv(base / "results/official/Paired_Weather_minus_Empirical_Bootstrap.csv")
    if len(paired) != 24:
        raise AssertionError(f"Expected 24 paired contrasts, found {len(paired)}")
    if len({(x["system"],x["method"]) for x in paired}) != 24:
        raise AssertionError("Repeated paired contrast")
    for x in paired:
        lo, delta, hi = [numeric(x[k]) for k in ("ci025", "diff", "ci975")]
        if not (lo <= delta <= hi):
            raise AssertionError(f"Interval not ordered: {x}")
        if not (0 < int(x["paired_independent_replicates"]) <= 200):
            raise AssertionError(f"Incorrect bootstrap cluster count: {x}")

    field = load_csv(base / "results/field/Existing_Field_CCM_Support_Snapshot.csv")
    primary = [r for r in field if r["cause"] == "spei_pm_3" and r["effect"] == "ssmi1"]
    assert len(primary) == 1
    assert (int(primary[0]["stations_attempted"]), int(primary[0]["supported"])) == (36, 21)
    assert all(int(r["supported"]) <= int(r["eligible"]) <= int(r["stations_attempted"]) for r in field)
    checks = load_csv(base / "results/official/Final_Integrity_Checks.csv")
    assert len(checks) == 8 and all(r["passed"] == "True" for r in checks)
    print("PUBLIC TABLES PASS: 72 method summaries, 24 contrasts, field scope, 8 saved checks.")
    print("METHOD TOTALS:", dict(totals))
    return summary

def check_raw_zip(zip_path, summary):
    print("Checking archived Kaggle trace:", zip_path)
    with zipfile.ZipFile(zip_path) as z:
        for name, sha in ARCHIVE_SHA256.items():
            got = hashlib.sha256(z.read(name)).hexdigest()
            if got != sha:
                raise AssertionError(f"SHA-256 mismatch for {name}: {got}")
        nulls = rows_from_text(z.read("Official_Null_Scores_Checkpoint.csv"))
        evaluations = rows_from_text(z.read("Official_Final_Results.csv"))
    if len(nulls) != 2160 or len(evaluations) != 15600:
        raise AssertionError(f"Wrong raw row counts: {len(nulls)} / {len(evaluations)}")
    reference = defaultdict(list)
    for row in nulls:
        score = numeric(row["ccm_score"])
        if math.isfinite(score):
            reference[(row["family"], row["mask_id"], row["strategy"])].append(score)
    counts = defaultdict(lambda: [0, 0, 0])
    checked_ccm = 0
    keys = set()
    for r in evaluations:
        key = r["key"]
        if key in keys:raise AssertionError("Duplicate raw evaluation key")
        keys.add(key)
        for method, pcol in METHODS.items():
            k = (r["system"], r["strategy"], method)
            counts[k][0] += 1
            p = numeric(r[pcol])
            if math.isfinite(p):
                if not 0 <= p <= 1:raise AssertionError(f"Out-of-range p in {key}")
                counts[k][1] += 1
                counts[k][2] += int(p < 0.05)
        ccm_p = numeric(r["ccm_p"])
        if math.isfinite(ccm_p):
            family = "null_logistic" if "logistic" in r["system"] else "null_ar"
            ref = reference[(family,r["mask_id"],r["strategy"])]
            if len(ref) < 120:raise AssertionError(f"Insufficient CCM null scores: {key}")
            expected_p = (1 + sum(v >= numeric(r["ccm_score"]) for v in ref))/(1+len(ref))
            assert_close(ccm_p, expected_p, f"CCM p {key}")
            checked_ccm += 1
        pcmci = numeric(r["pcmci_p"])
        if math.isfinite(pcmci) and numeric(r["pcmci_min_mci_n"]) < 40:
            raise AssertionError(f"PCMCI sample gate violation: {key}")
    for row in summary:
        key = (row["system"], row["strategy"], row["method"])
        observed = counts[key]
        expected = [int(row[k]) for k in ("attempted","eligible","detected")]
        if observed != expected:raise AssertionError(f"{key}: {observed} != {expected}")
    if checked_ccm != 10800:raise AssertionError(f"Unexpected calibrated CCM rows: {checked_ccm}")
    print(f"RAW ARCHIVE PASS: {len(evaluations)} evaluations, {len(nulls)} null scores, {checked_ccm} CCM p-values.")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--kaggle-zip", type=Path, help="Optional author-side Paper2_OneClick_OUTPUTS.zip")
    args=ap.parse_args()
    summary=check_public_tables(ROOT)
    if args.kaggle_zip:check_raw_zip(args.kaggle_zip,summary)
    else:print("Raw checkpoint not supplied: raw p-value verification not attempted.")
    print("PASS. This tests computational consistency only; not causal field validity.")

if __name__=="__main__":
    main()
