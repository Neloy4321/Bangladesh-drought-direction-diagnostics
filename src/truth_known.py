"""Synthetic DGP and source-matched missingness for Paper 2.

This module transcribes the frozen method protocol from the executed one-click
Kaggle workflow. The real field data are never generated here. A real panel is
used ONLY to obtain the six quality-accepted vegetation observation calendars.
"""
import io
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

SYSTEMS = ("null_ar","weak_ar","strong_ar","common_driver",
           "null_logistic","coupled_logistic")
MASKS = ("S04","S06","S08","S28","S30","S32")
MASK_COUNTS = (90,0,82,94,0,104)
SEED = 20261112
MASTER = "paper2/results/paper2_master_panel.csv"


def original_masks(source):
    """Read either an original research ZIP or an extracted master CSV."""
    source = Path(source)
    if source.is_file() and source.suffix.lower() == ".zip":
        with zipfile.ZipFile(source) as z:
            candidates = [x for x in z.namelist()
                          if x == MASTER or x.endswith("/paper2_master_panel.csv")]
            if len(candidates) != 1:
                raise ValueError("Archive must contain exactly one master panel")
            data = pd.read_csv(io.BytesIO(z.read(candidates[0])),
                               usecols=["point_id","date_month","ndvi_anom"])
    else:
        candidates = [source] if source.is_file() else list(source.rglob("paper2_master_panel.csv"))
        if len(candidates) != 1:
            raise ValueError("Expected one extracted paper2_master_panel.csv")
        data = pd.read_csv(candidates[0],
                           usecols=["point_id","date_month","ndvi_anom"])
    data = data[(data.date_month >= "2015-01-01") &
                (data.date_month <= "2026-06-01")]
    expected = pd.period_range("2015-01","2026-06",freq="M")
    masks = {}
    for point_id in MASKS:
        g = data[data.point_id == point_id].sort_values("date_month")
        if len(g) != 138:
            raise ValueError(f"{point_id}: expected 138 monthly records")
        if list(pd.to_datetime(g.date_month).dt.to_period("M")) != list(expected):
            raise ValueError(f"{point_id}: months not continuous")
        masks[point_id] = g.ndvi_anom.notna().to_numpy(dtype=bool)
    counts = tuple(int(v.sum()) for v in masks.values())
    if counts != MASK_COUNTS:
        raise ValueError(f"Input masks changed: {counts} != {MASK_COUNTS}")
    return masks


def simulate(system, replicate, seed=SEED, n=138, burn=500):
    """X, Y, Z; X→Y direct edge is known in weak/strong AR and coupled logistic."""
    if system not in SYSTEMS:
        raise ValueError(system)
    rng = np.random.default_rng(
        np.random.SeedSequence([seed,replicate,SYSTEMS.index(system)]))
    N = n + burn
    x = np.zeros(N)
    y = np.zeros(N)
    z = np.zeros(N)
    if "logistic" in system:
        x[0], y[0], z[0] = rng.uniform(.2,.8,3)
        b = .15 if system == "coupled_logistic" else 0.0
        for t in range(1,N):
            x[t] = 3.8*x[t-1]*(1-x[t-1])
            z[t] = 3.75*z[t-1]*(1-z[t-1])
            y[t] = (1-b)*3.7*y[t-1]*(1-y[t-1])+b*x[t-1]
    else:
        b = {"null_ar":0., "weak_ar":.2,
             "strong_ar":.5,"common_driver":0.}[system]
        noise = rng.normal(size=(N,3))
        for t in range(2,N):
            z[t] = .5*z[t-1]+noise[t,2]
            if system == "common_driver":
                x[t] = .5*x[t-1]+.8*z[t-1]+noise[t,0]
                y[t] = .5*y[t-1]+.8*z[t-2]+noise[t,1]
            else:
                x[t] = .5*x[t-1]+noise[t,0]
                y[t] = .5*y[t-1]+b*x[t-1]+noise[t,1]
    return np.stack([x[-n:],y[-n:],z[-n:]],axis=1)


def mask_for(base, data, strategy, replicate, seed=SEED):
    """Observed mask for Y; X and Z are completely observed."""
    n = len(base)
    if strategy == "complete":
        return np.ones(n,dtype=bool)
    if strategy == "empirical":
        return np.asarray(base,dtype=bool).copy()
    rng = np.random.default_rng(np.random.SeedSequence(
        [seed,replicate,101,{"count_random":1,"weather_month_matched":2}[strategy]]))
    out = np.zeros(n,dtype=bool)
    if strategy == "count_random":
        out[rng.choice(n,size=int(base.sum()),replace=False)] = True
    elif strategy == "weather_month_matched":
        x = data[:,0]
        scale = x.std()+1e-12
        for month in range(12):
            idx = np.arange(month,n,12)
            k = int(base[idx].sum())
            if k:
                wet = (x[idx]-x.mean())/scale
                score = .9*wet+.55*rng.normal(size=len(idx))
                out[idx[np.argsort(score)[:k]]] = True
        if any(out[j::12].sum() != base[j::12].sum() for j in range(12)):
            raise AssertionError("Month-of-year mask counts not preserved")
    if out.sum() != base.sum():
        raise AssertionError("Total mask count mismatch")
    return out


def masked_xyz(data, base, strategy, replicate, seed=SEED):
    observed = mask_for(base,data,strategy,replicate,seed)
    a = np.asarray(data,float).copy()
    a[~observed,1] = np.nan
    return a,observed
