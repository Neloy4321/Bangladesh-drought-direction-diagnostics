"""Official-library inference wrappers for the Paper 2 synthetic benchmark.

This is a public reference implementation, reflecting the executed Kaggle
protocol and preserving method-specific sample-support gates. It has not been
independently re-run end-to-end *from this GitHub repository*. Match checksums
against the original archived Kaggle outputs before claiming exact replication.
"""
import inspect
import json
import numpy as np
import pandas as pd
from scipy.stats import f as f_distribution


def granger(a,lag=3,min_n=40):
    t = np.arange(lag,len(a))
    if len(t) == 0:return (np.nan,np.nan,0)
    arr = np.column_stack([a[t,1]]
                          +[a[t-k,1] for k in range(1,lag+1)]
                          +[a[t-k,0] for k in range(1,lag+1)]
                          +[a[t-k,2] for k in range(1,lag+1)])
    arr = arr[np.isfinite(arr).all(axis=1)]
    n = len(arr)
    if n < min_n or n <= 1+3*lag:return (np.nan,np.nan,n)
    y = arr[:,0];constant = np.ones((n,1))
    ly,lx,lz = arr[:,1:4],arr[:,4:7],arr[:,7:10]
    def test(base,full):
        b0 = np.linalg.lstsq(base,y,rcond=None)[0]
        b1 = np.linalg.lstsq(full,y,rcond=None)[0]
        s0 = np.square(y-base@b0).sum()
        s1 = np.square(y-full@b1).sum()
        df = n-full.shape[1]
        if df <= 0 or s1 <= 1e-15:return np.nan
        f = max(0.,(s0-s1)/lag/(s1/df))
        return float(f_distribution.sf(f,lag,df))
    pair = test(np.column_stack([constant,ly]),
                np.column_stack([constant,ly,lx]))
    conditioned = test(np.column_stack([constant,ly,lz]),
                       np.column_stack([constant,ly,lz,lx]))
    return pair,conditioned,n


def ccm_vectors(a):
    if len(a) < 3:return (0,0)
    t = np.arange(2,len(a))
    f = (np.isfinite(a[t,1]) & np.isfinite(a[t-1,1]) &
         np.isfinite(a[t-2,1]) & np.isfinite(a[t-1,0]))
    r = (np.isfinite(a[t,0]) & np.isfinite(a[t-1,0]) &
         np.isfinite(a[t-2,0]) & np.isfinite(a[t-1,1]))
    return int(f.sum()),int(r.sum())


def ccm(a,random_seed):
    import pyEDM
    n_f,n_r = ccm_vectors(a)
    if min(n_f,n_r) < 40:return np.nan,"below_vector_gate",n_f,n_r
    n = min(n_f,n_r)
    libs = sorted({20,max(21,int(.5*n)),max(22,int(.8*n))})
    df = pd.DataFrame({"Time":np.arange(1,len(a)+1),"X":a[:,0],"Y":a[:,1]})
    result = pyEDM.CCM(dataFrame=df,columns="Y",target="X",E=3,Tp=-1,tau=-1,
        exclusionRadius=12,libSizes=libs,sample=10,seed=int(random_seed),parallel=False)
    required={"LibSize","Y:X","X:Y"}
    if not required.issubset(result.columns) or int(result.LibSize.iloc[-1]) != libs[-1]:
        raise RuntimeError("pyEDM CCM response schema/library size mismatch")
    f,r = float(result["Y:X"].iloc[-1]),float(result["X:Y"].iloc[-1])
    if not np.isfinite(f) or not np.isfinite(r):
        return np.nan,"nonfinite",n_f,n_r
    return f-r,"ok",n_f,n_r


def pcmci(a):
    import tigramite.data_processing as pp
    from tigramite.pcmci import PCMCI
    from tigramite.independence_tests.parcorr import ParCorr
    if len(a) < 45 or np.isfinite(a[:,1]).sum() < 40:
        return np.nan,"below_support",0
    missing = -99999.
    frame = pp.DataFrame(np.where(np.isfinite(a),a,missing),
                         missing_flag=missing,remove_missing_upto_maxlag=False,
                         var_names=["X","Y","Z"])
    model = PCMCI(dataframe=frame,cond_ind_test=ParCorr(),verbosity=0)
    if not {"tau_min","tau_max","pc_alpha","max_conds_dim","max_combinations"}.issubset(
            inspect.signature(model.run_pc_stable).parameters):
        raise RuntimeError("Tigramite PC1 API changed")
    parents = model.run_pc_stable(tau_min=1,tau_max=3,pc_alpha=.2,
                                  max_conds_dim=3,max_combinations=1)
    result = model.run_mci(tau_min=1,tau_max=3,parents=parents,
                           max_conds_py=3,max_conds_px=3,
                           alpha_level=.05,fdr_method="none")
    p = np.asarray(result["p_matrix"],float)
    if p.shape != (3,3,4):raise RuntimeError("Unexpected PCMCI p_matrix")
    methods=("_set_link_assumptions","_set_max_condition_dim",
             "_get_int_parents","_iter_indep_conds")
    if not all(hasattr(model,name) for name in methods):
        raise RuntimeError("Tigramite MCI condition iterator API changed")
    links = model._set_link_assumptions(None,1,3)
    mp = model._set_max_condition_dim(3,1,3)
    mx = model._set_max_condition_dim(3,1,3)
    parent_int = model._get_int_parents(parents)
    ci = model.cond_ind_test
    opts={"cut_off":getattr(ci,"cut_off","2xtau_max"),
          "mask_type":getattr(ci,"mask_type",None)}
    observed={}
    for j,i,tau,Z in model._iter_indep_conds(parent_int,links,mp,mx):
        if (i,j) not in ((0,1),(1,0)) or abs(int(tau)) not in (1,2,3):
            continue
        X=[(int(i),int(tau))];Y=[(int(j),0)]
        try:
            arr,*_ = frame.construct_array(X=X,Y=Y,Z=Z,tau_max=3,
                                          do_checks=True,**opts)
            n=arr.shape[1]
        except ValueError as err:
            if "No valid samples" in str(err):n=0
            else:raise
        observed[(i,j,abs(int(tau)))] = n
    required=[(i,j,lag) for (i,j) in ((0,1),(1,0)) for lag in (1,2,3)]
    if not all(k in observed for k in required):
        return np.nan,"incomplete_mci_lags",0
    min_n=min(observed.values())
    if min_n < 40:return np.nan,"below_mci_sample_gate",min_n
    values=p[0,1,1:4]
    reverse=p[1,0,1:4]
    if not np.isfinite(values).all() or not np.isfinite(reverse).all():
        return np.nan,"nonfinite_mci_p",min_n
    # Bonferroni across the three prespecified forward lags.
    return float(min(1.,3*values.min())),"ok",min_n
