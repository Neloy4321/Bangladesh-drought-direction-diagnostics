#!/usr/bin/env python3
"""Rebuild diagnostic figures from the public, validated summary CSVs.

Source tables: results/official/Official_Final_Summary.csv and
results/official/Paired_Weather_minus_Empirical_Bootstrap.csv.
Generated figures are descriptive and NOT independent field causal validation.
"""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"
OUT.mkdir(exist_ok=True)
SYSTEMS = ["null_ar","weak_ar","strong_ar","common_driver","null_logistic","coupled_logistic"]
DISPLAY = ["Null AR","Weak AR","Strong AR","Common driver","Null logistic","Coupled logistic"]
METHODS = ["ccm","pcmci","granger"]
LABELS = ["CCM","PCMCI","Granger"]
STRATS = ["empirical","weather_month_matched"]
STRAT_LABELS = ["Empirical calendar","Driver-conditioned"]

def load(name):
    with (ROOT/name).open(newline="",encoding="utf-8") as fh:
        return list(csv.DictReader(fh))

def save(fig,stem):
    fig.savefig(OUT/(stem+".svg"),bbox_inches="tight")
    fig.savefig(OUT/(stem+".png"),dpi=240,bbox_inches="tight")
    plt.close(fig)

def main():
    data=load(Path("results/official/Official_Final_Summary.csv"))
    d={(r["system"],r["strategy"],r["method"]):r for r in data}
    # Six panels distinguish conditioning on eligibility from completion.
    fig,axes=plt.subplots(3,2,figsize=(13.2,12),sharey=True)
    colors=["#295f85","#b06c40","#668b65"]
    for ax,sys,label in zip(axes.flat,SYSTEMS,DISPLAY):
        x=np.arange(2)
        for k,(method,method_name,color) in enumerate(zip(METHODS,LABELS,colors)):
            heights=[100*float(d[(sys,st,method)]["detection_given_eligible"]) for st in STRATS]
            ax.bar(x+(k-1)*.24,heights,.23,label=method_name,color=color)
        ax.set_xticks(x,STRAT_LABELS,fontsize=9)
        ax.set_title(label,loc="left",fontweight="bold")
        ax.set_ylim(0,104)
        ax.grid(axis="y",alpha=.16)
        ax.set_axisbelow(True)
        if ax in axes[:,0]:ax.set_ylabel("Detection / eligible (%)")
    axes[0,0].legend(ncol=3,loc="upper right",fontsize=8)
    fig.suptitle("Truth-known synthetic benchmarks: detection conditional on estimability",
                 fontsize=14,fontweight="bold",y=.995)
    fig.text(.5,.015,"Nominal p < 0.05; driver-conditioned missingness is synthetic and month-count matched.",
             ha="center",fontsize=9)
    fig.tight_layout(rect=(0,.026,1,.97))
    save(fig,"F1_Official_Detection_By_Method")

    fig,axes=plt.subplots(1,2,figsize=(13.2,5.1),sharey=True)
    for ax,st,lab in zip(axes,STRATS,STRAT_LABELS):
        x=np.arange(len(SYSTEMS))
        for k,(method,method_name,color) in enumerate(zip(METHODS,LABELS,colors)):
            heights=[100*float(d[(sys,st,method)]["eligibility_fraction"]) for sys in SYSTEMS]
            ax.bar(x+(k-1)*.24,heights,.23,label=method_name,color=color)
        ax.set_xticks(x,DISPLAY,rotation=40,ha="right",fontsize=8)
        ax.set_title(lab,loc="left",fontweight="bold")
        ax.set_ylim(0,103)
        ax.grid(axis="y",alpha=.16)
    axes[0].set_ylabel("Eligible / attempted (%)")
    axes[0].legend(loc="upper right",fontsize=8,ncol=3)
    fig.suptitle("Method-specific numerical eligibility",fontsize=14,fontweight="bold")
    fig.tight_layout()
    save(fig,"F2_Official_Eligibility")

    paired=load(Path("results/official/Paired_Weather_minus_Empirical_Bootstrap.csv"))
    chosen=[r for r in paired if r["method"] in METHODS]
    fig,ax=plt.subplots(figsize=(11,10))
    order=sorted(chosen,key=lambda r:(SYSTEMS.index(r["system"]),METHODS.index(r["method"])))
    ys=np.arange(len(order))
    means=np.array([100*float(r["diff"]) for r in order])
    low=np.array([100*float(r["ci025"]) for r in order])
    high=np.array([100*float(r["ci975"]) for r in order])
    ax.errorbar(means,ys,xerr=[means-low,high-means],fmt="o",color="#295f85",ecolor="#7597ae",capsize=2)
    ax.axvline(0,color="#555",ls="--",lw=1)
    ax.set_yticks(ys,[r["system"].replace("_"," ")+" — "+r["method"].upper() for r in order],fontsize=8)
    ax.invert_yaxis();ax.grid(axis="x",alpha=.16)
    ax.set_xlabel("Driver-conditioned minus empirical detection (percentage points)")
    ax.set_title("Replicate-cluster paired contrasts (exploratory 95% intervals)")
    fig.text(.5,.015,"Intervals are not multiplicity-adjusted; paired analyses include only eligible pairs.",
             ha="center",fontsize=9)
    fig.tight_layout(rect=(0,.025,1,1))
    save(fig,"F3_Official_Paired_Exploratory")

    field=load(Path("results/field/Existing_Field_CCM_Support_Snapshot.csv"))
    labs=[r["cause"].replace("_"," ").upper()+" → "+r["effect"].upper() for r in field]
    xx=np.arange(len(field))
    fig,ax=plt.subplots(figsize=(11,4.7))
    ax.bar(xx-.2,[int(r["eligible"]) for r in field],width=.38,label="Estimable",color="#295f85")
    ax.bar(xx+.2,[int(r["supported"]) for r in field],width=.38,label="Supported",color="#b06c40")
    ax.set_xticks(xx,labs,rotation=20,ha="right",fontsize=8)
    ax.set_ylim(0,40);ax.set_ylabel("Stations / 36");ax.legend()
    ax.set_title("Archived field CCM diagnostic support (not new model fitting)")
    fig.tight_layout()
    save(fig,"F4_Field_Eligibility_And_Support")
    print("Regenerated 4 figure panels (SVG + PNG) under figures/")

if __name__=="__main__":
    main()
