# -*- coding: utf-8 -*-
import warnings; warnings.filterwarnings("ignore")
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
import cb_v3 as CB
AZ="#2d4a6b"; COR={"Cost-entry":"#C0622E","Intermediate-coverage":"#2E8B7A","Dual-lane":"#6B5B95","Premium-focus":"#B8860B"}
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"figure.dpi":200,"axes.edgecolor":"#555","axes.linewidth":0.8})
N=800
Xdf,store,Ur,Cr,restr=CB.eval_full(CB.EST,N,42)
d=Xdf["dev_custo"].to_numpy()*100
devcols=[c for c in Xdf.columns if c.startswith("dev_") and c!="dev_custo"]
eps=Xdf[devcols].mean(axis=1).to_numpy()*100
# ===== FIG 3: PRIM (intermediate & dual-lane) =====
expo=[("Intermediate-coverage","+5.1%",5.1),("Dual-lane","−3.4%",-3.4)]
fig,axs=plt.subplots(1,2,figsize=(9.5,4.2),squeeze=False)
for j,(e,lab,thr) in enumerate(expo):
    ax=axs[0][j]; rob=CB.robust(store,e,CB.U_MIN,CB.C_MAX); fail=~rob
    ax.scatter(d[rob],eps[rob],s=7,c="#3D5A73",alpha=0.4,edgecolors="none")
    ax.scatter(d[fail],eps[fail],s=7,c="#C0622E",alpha=0.45,edgecolors="none")
    ax.add_patch(Rectangle((thr,-11),(31-thr),22,fill=True,facecolor="#B22222",alpha=0.07,zorder=1))
    ax.add_patch(Rectangle((thr,-11),(31-thr),22,fill=False,edgecolor="#B22222",lw=1.7,ls="--",zorder=5))
    ax.text(0.04,0.96,f"PRIM box\nδ ≥ {lab}",transform=ax.transAxes,color="#B22222",fontsize=7.6,fontweight="bold",va="top",bbox=dict(boxstyle="round,pad=0.25",fc="white",ec="none",alpha=0.85))
    ax.axhline(0,color="#ccc",lw=0.7); ax.axvline(0,color="#ccc",lw=0.7)
    ax.set_xlim(-16,32); ax.set_ylim(-12,12)
    # panel title removed (identified in the caption); professor comment
    ax.set_xlabel("Cost deviation  δ  (%)",fontsize=8.5)
    if j==0: ax.set_ylabel("Mean specification deviation  ε  (%)",fontsize=8.5)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
h=[Line2D([0],[0],marker="o",color="w",markerfacecolor="#3D5A73",markersize=7,label="Robust scenario"),
   Line2D([0],[0],marker="o",color="w",markerfacecolor="#C0622E",markersize=7,label="Vulnerable scenario"),
   Line2D([0],[0],color="#B22222",lw=1.7,ls="--",label="PRIM box boundary")]
fig.legend(handles=h,loc="lower center",ncol=3,frameon=True,fontsize=8.5,bbox_to_anchor=(0.5,-0.02))
plt.tight_layout(rect=[0,0.03,1,1]); plt.savefig("fig3_prim_v3.png",bbox_inches="tight"); plt.close()
print("fig3 OK")
# ===== FIG 4: Regret =====
EN=list(CB.EST.keys())
U=np.column_stack([Ur[e] for e in EN]); C=np.column_stack([Cr[e] for e in EN])
regU=U.max(1,keepdims=True)-U; regC=C-C.min(1,keepdims=True)
rUn=regU/regU.max(); rCn=regC/regC.max()
fig,axs=plt.subplots(1,3,figsize=(13,4.2),sharey=True)
for ax,pct in zip(axs,[75,90,95]):
    pts={e:(np.percentile(rCn[:,j],pct),np.percentile(rUn[:,j],pct)) for j,e in enumerate(EN)}
    ordn=sorted(pts.items(),key=lambda kv:(kv[1][0],kv[1][1])); nd=[]; mU=np.inf
    for e,(rc,ru) in ordn:
        if ru<mU-1e-9: nd.append((rc,ru)); mU=ru
    if len(nd)>=2: ax.plot([p[0] for p in nd],[p[1] for p in nd],"--",color="#999",lw=1.2,label="non-dominance frontier")
    for e,(rc,ru) in pts.items():
        ax.scatter([rc],[ru],s=190,c=COR[e],edgecolors="black",linewidths=1.2,zorder=4)
        if e=="Premium-focus":
            ax.annotate(e,(rc,ru),xytext=(rc+0.01,ru+0.09),ha="right",fontsize=7,fontweight="bold",color=COR[e])
        else:
            ax.annotate(e,(rc,ru),xytext=(rc+0.045,ru+0.01),fontsize=7,fontweight="bold",color=COR[e])
    # panel title removed (percentiles identified in the caption); professor comment
    ax.set_xlabel("Normalized cost regret",fontsize=9); ax.set_xlim(-0.05,1.1); ax.set_ylim(-0.05,1.1)
    ax.grid(ls=":",color="#eee"); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
axs[0].set_ylabel("Normalized utility regret",fontsize=9); axs[0].legend(loc="upper right",fontsize=7.5)
plt.tight_layout(); plt.savefig("fig4_regret_v3.png",bbox_inches="tight"); plt.close()
print("fig4 OK")
