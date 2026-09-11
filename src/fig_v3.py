# -*- coding: utf-8 -*-
import warnings; warnings.filterwarnings("ignore")
import numpy as np, itertools
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import arquitetura_saur_v3 as A3
import cb_v3 as CB
from modelo_R import (Cenario, importancia_necessidades, importancia_propriedades,
                      normalizar_pesos_propriedade, normalizar_nivel, agregar_niveis_produto, custo_variante)
ARQ,LIM=A3.arquitetura_saur()
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"figure.dpi":200,"axes.edgecolor":"#555","axes.linewidth":0.8})
AZ="#2d4a6b"; CORES={"Cost-entry":"#C0622E","Intermediate-coverage":"#2E8B7A","Dual-lane":"#6B5B95","Premium-focus":"#B8860B"}
wm=(LIM['w_seg_min']+LIM['w_seg_max'])/2; wm=wm/wm.sum()
CEN=Cenario(wm,{p.nome:0.0 for p in ARQ.propriedades},0.0)
WP=normalizar_pesos_propriedade(importancia_propriedades(ARQ,importancia_necessidades(ARQ,wm)))
def vms(cfg): return [next(v for v in ARQ.variantes_modulo[m] if v.nome==cfg[m]) for m in ARQ.modulos]
def av(cfg):
    vl=vms(cfg); U=sum(WP[k]*normalizar_nivel(p,agregar_niveis_produto(ARQ,p,vl,CEN)) for k,p in enumerate(ARQ.propriedades)); return U,custo_variante(vl,CEN)
# all coherent configs
op=[[v.nome for v in ARQ.variantes_modulo[m]] for m in ARQ.modulos]; dd=[]
for c in itertools.product(*op):
    cfg=dict(zip(ARQ.modulos,c))
    if A3.coerente(cfg): dd.append(av(cfg))
Us=[u for u,c in dd]; Cs=[c for u,c in dd]
# frontier
o=sorted(dd,key=lambda t:(t[1],-t[0])); pf=[]; mU=-1e9
for u,c in o:
    if u>mU+1e-12: pf.append((u,c)); mU=u
# strategy nominal points (restrictive variant)
_,store,Ur,Cr,restr=CB.eval_full(CB.EST,10,42)  # just for restr
pts={}
for e,cfgs in CB.EST.items():
    U,C=av(cfgs[restr[e]]); pts[e]=(C,U)
# ===== FIG 2: Pareto =====
fig,ax=plt.subplots(figsize=(7.8,5.6))
ax.scatter(Cs,Us,s=8,c="#C9CDD2",alpha=0.45,edgecolors="none",zorder=1,label=f"{len(dd)} coherent configurations")
ax.plot([c for u,c in pf],[u for u,c in pf],"-o",color="#1F7A3D",lw=1.6,ms=3.5,zorder=3,label=f"Efficiency frontier ({len(pf)} pts)")
ax.axvline(170000,color="#777",lw=1.1,ls="--"); ax.axhline(0.45,color="#777",lw=1.1,ls="--")
ax.text(109000,0.855,"admitted region",fontsize=8,color="#3a6b3a",fontweight="bold")
# star EVERY configuration composing the strategies (7 total; matches Table 4)
for e,cfgs in CB.EST.items():
    for cfg in cfgs:
        U,C=av(cfg)
        ax.scatter([C],[U],marker="*",s=300,c=CORES[e],edgecolors="white",linewidths=1.3,zorder=6)
# relocated labels: text in empty areas with leader arrows to the markers
_lab={"Cost-entry":(127000,0.243,"center","top"),
      "Intermediate-coverage":(120000,0.565,"left","center"),
      "Dual-lane":(140000,0.705,"left","center")}
for e,(x,y,ha,va) in _lab.items():
    ax.text(x,y,e.replace("-","-\n") if e=="Intermediate-coverage" else e,
        ha=ha,va=va,fontsize=7.6,fontweight="bold",color=CORES[e],zorder=7,
        bbox=dict(boxstyle="round,pad=0.2",fc="white",ec="none",alpha=0.75))
# premium-focus: keep at top-right, placed to the left of its star (no clutter there)
_Cp,_Up=pts["Premium-focus"]
ax.annotate("Premium-focus",xy=(_Cp,_Up),xytext=(-9,3),textcoords="offset points",ha="right",fontsize=7.6,fontweight="bold",color=CORES["Premium-focus"],zorder=7)
ax.set_xlabel("Variable cost  C$_p$  (BRL)",fontweight="bold"); ax.set_ylabel("Utility  U$_p$",fontweight="bold")
ax.xaxis.set_major_formatter(lambda x,_:f"{x/1000:.0f}k")
ax.set_xlim(105000,365000); ax.set_ylim(0.15,0.88)
ax.legend(loc="lower right",fontsize=8.5,frameon=True)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
plt.tight_layout(); plt.savefig("fig2_pareto_v3.png",bbox_inches="tight"); plt.close()
print("fig2_pareto_v3.png OK | frontier pts:",len(pf))
