# -*- coding: utf-8 -*-
import warnings; warnings.filterwarnings("ignore")
import numpy as np, json
from scipy.stats import spearmanr
import cb_v3 as CB
EN=list(CB.EST.keys())
N=800
Xdf,store,Ur,Cr,restr=CB.eval_full(CB.EST,N,42)
out={}
# rho
rho={e:float(CB.robust(store,e,CB.U_MIN,CB.C_MAX).mean()) for e in EN}
out["rho"]={e:round(rho[e]*100,1) for e in EN}
# frontier meta
out["counts"]={"raw":31104,"buildable":4536,"frontier":len(CB.PF)}
# nominal coords
out["nominal"]={e:{"U":round(CB._avaliar(CB._vms(CB.EST[e][restr[e]]))[0],3),
                   "C":int(CB._avaliar(CB._vms(CB.EST[e][restr[e]]))[1])} for e in EN}
# PRIM delta boxes (exposed strategies)
d=Xdf["dev_custo"].to_numpy()
def prim_delta(e):
    fail=~CB.robust(store,e,CB.U_MIN,CB.C_MAX); nf=fail.sum()
    if nf==0 or nf==len(fail): return None
    best=None
    for t in np.linspace(d.min(),d.max(),600):
        ins=d>=t
        if ins.sum()==0: continue
        den=(fail&ins).sum()/ins.sum(); cov=(fail&ins).sum()/nf
        if den>=0.9 and (best is None or cov>best[1]): best=(t,cov,den,ins.mean())
    return best
out["prim"]={}
for e in EN:
    b=prim_delta(e)
    if b: out["prim"][e]={"delta":round(b[0]*100,1),"cov":round(b[1],2),"den":round(b[2],2),"mass":round(b[3],2)}
# grid
UM=[0.40,0.45,0.50,0.55]; CM=[160000,170000,180000,190000]
grid=[]; wins={}
for um in UM:
    row=[]
    for cm in CM:
        rr={e:CB.robust(store,e,um,cm).mean() for e in EN}
        win=max(rr,key=rr.get); row.append((win,round(rr[win]*100)))
        wins[win]=wins.get(win,0)+1
    grid.append(row)
out["grid"]={"UM":UM,"CM":[c//1000 for c in CM],"rows":[[[w,v] for w,v in r] for r in grid],"wins":wins}
# regret over the 4 strategies
U=np.column_stack([Ur[e] for e in EN]); C=np.column_stack([Cr[e] for e in EN])
regU=U.max(1,keepdims=True)-U; regC=C-C.min(1,keepdims=True)
regUn=regU/regU.max(); regCn=regC/regC.max()
reg={}
for j,e in enumerate(EN):
    reg[e]={"uP":"/".join(f"{np.percentile(regUn[:,j],p):.2f}" for p in (75,90,95)),
            "cP":"/".join(f"{np.percentile(regCn[:,j],p):.2f}" for p in (75,90,95)),
            "low_u":f"{(np.argmin(regU,1)==j).mean()*100:.0f}%","low_c":f"{(np.argmin(regC,1)==j).mean()*100:.0f}%"}
rs,_=spearmanr(regUn.ravel(),regCn.ravel())
out["regret"]={"tab":reg,"spearman":round(float(rs),2)}
# convergence
Ns=[25,50,100,200,400,800,1600,3200]; rhoN={}
for n in Ns:
    _,st,_,_,_=CB.eval_full(CB.EST,n,42); rhoN[n]={e:CB.robust(st,e,CB.U_MIN,CB.C_MAX).mean() for e in EN}
conv=[]; prev=None
for n in Ns:
    dmax="—" if prev is None else "%.1f%%"%(max(abs(rhoN[n][e]-rhoN[prev][e]) for e in EN)*100)
    conv.append([n]+[round(rhoN[n][e]*100,1) for e in EN]+[dmax]); prev=n
out["convergence"]={"policies":EN,"rows":conv}
json.dump(out,open("_v3_data.json","w"),ensure_ascii=False,indent=1)
print("== rho ==",out["rho"])
print("== prim ==",out["prim"])
print("== grid wins ==",out["grid"]["wins"])
print("== spearman ==",out["regret"]["spearman"])
print("== conv (N=800 dmax) ==",conv[5][-1])
print("dumped _v3_data.json")
