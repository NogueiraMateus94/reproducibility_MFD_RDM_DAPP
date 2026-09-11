# -*- coding: utf-8 -*-
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, itertools
import arquitetura_saur_v3 as A3
from modelo_R import (Cenario, importancia_necessidades, importancia_propriedades,
                      normalizar_pesos_propriedade, normalizar_nivel,
                      agregar_niveis_produto, custo_variante)
ARQ, LIM = A3.arquitetura_saur()
PROPS = [p.nome for p in ARQ.propriedades]         # 13 propriedades
WCOLS = ["w_"+str(i) for i in range(ARQ.J)]
U_MIN, C_MAX = 0.45, 170000.0
DELTA=(-0.15,0.30); EPS=(-0.10,0.10)
wm=(LIM["w_seg_min"]+LIM["w_seg_max"])/2; wm=wm/wm.sum()
CENnom=Cenario(wm,{p:0.0 for p in PROPS},0.0)
WPROPnom=normalizar_pesos_propriedade(importancia_propriedades(ARQ,importancia_necessidades(ARQ,wm)))
def _vms(cfg): return [next(v for v in ARQ.variantes_modulo[m] if v.nome==cfg[m]) for m in ARQ.modulos]
def _avaliar(vl,cen=CENnom,wprop=WPROPnom):
    U=sum(wprop[k]*normalizar_nivel(p,agregar_niveis_produto(ARQ,p,vl,cen)) for k,p in enumerate(ARQ.propriedades))
    return U, custo_variante(vl,cen)

def frontier():
    op=[[v.nome for v in ARQ.variantes_modulo[m]] for m in ARQ.modulos]; dd=[]
    for c in itertools.product(*op):
        cfg=dict(zip(ARQ.modulos,c))
        if A3.coerente(cfg): u,cc=_avaliar(_vms(cfg)); dd.append((u,cc,cfg))
    o=sorted(dd,key=lambda t:(t[1],-t[0])); pf=[]; mU=-1e9
    for u,c,cfg in o:
        if u>mU+1e-12: pf.append(cfg); mU=u
    return pf
PF=frontier()
EST={"Cost-entry":[PF[1]],
     "Intermediate-coverage":[PF[11],PF[15]],
     "Dual-lane":[PF[17],PF[18]],
     "Premium-focus":[PF[26],PF[27]]}

def sample_cb(N,seed=42):
    rng=np.random.default_rng(seed); keys=WCOLS+[f"dev_{p}" for p in PROPS]+["dev_custo"]
    d=len(keys); u=np.zeros((N,d))
    for j in range(d):
        perm=rng.permutation(N); u[:,j]=(perm+rng.random(N))/N
    lo=np.array([LIM["w_seg_min"][i] for i in range(ARQ.J)]+[EPS[0]]*len(PROPS)+[DELTA[0]])
    hi=np.array([LIM["w_seg_max"][i] for i in range(ARQ.J)]+[EPS[1]]*len(PROPS)+[DELTA[1]])
    return pd.DataFrame(lo+u*(hi-lo),columns=keys)

def eval_full(est,N,seed=42):
    Xdf=sample_cb(N,seed)
    restr={e:int(np.argmax([_avaliar(_vms(c))[1] for c in cfgs])) for e,cfgs in est.items()}
    store={e:{"U":[],"C":[]} for e in est}; Ur={e:np.zeros(N) for e in est}; Cr={e:np.zeros(N) for e in est}
    for i,row in Xdf.iterrows():
        w=row[WCOLS].to_numpy(float); w=w/w.sum()
        devn={p:row[f"dev_{p}"] for p in PROPS}; cen=Cenario(w,devn,row["dev_custo"])
        wprop=normalizar_pesos_propriedade(importancia_propriedades(ARQ,importancia_necessidades(ARQ,w)))
        for e,cfgs in est.items():
            us=[];cs=[]
            for c in cfgs:
                U,C=_avaliar(_vms(c),cen,wprop); us.append(U); cs.append(C)
            store[e]["U"].append(us); store[e]["C"].append(cs)
            Ur[e][i]=us[restr[e]]; Cr[e][i]=cs[restr[e]]
    for e in est: store[e]["U"]=np.array(store[e]["U"]); store[e]["C"]=np.array(store[e]["C"])
    return Xdf,store,Ur,Cr,restr
def robust(store,e,um,cm):
    U=store[e]["U"];C=store[e]["C"]; return ((U>=um)&(C<=cm)).all(axis=1)

if __name__=="__main__":
    N=800
    print("nominal (variante restritiva):")
    for e,cfgs in EST.items():
        U,C=_avaliar(_vms(cfgs[int(np.argmax([_avaliar(_vms(c))[1] for c in cfgs]))]))
        print(f"  {e:22s} U={U:.3f} C={C:,.0f}")
    Xdf,store,Ur,Cr,restr=eval_full(EST,N,42)
    print("\nrobustez (N=800, seed42, Conduta B, U_min=0.45 C_max=170k):")
    for e in EST:
        print(f"  {e:22s} rho={robust(store,e,U_MIN,C_MAX).mean()*100:5.1f}%")
    # PRIM delta-only nas expostas
    d=Xdf["dev_custo"].to_numpy()
    print("\nPRIM (delta) por estrategia:")
    for e in EST:
        fail=~robust(store,e,U_MIN,C_MAX); nf=fail.sum()
        if nf==0 or nf==len(fail): print(f"  {e:22s} classe unica (rho trivial)"); continue
        best=None
        for t in np.linspace(d.min(),d.max(),400):
            ins=d>=t
            if ins.sum()==0: continue
            den=(fail&ins).sum()/ins.sum(); cov=(fail&ins).sum()/nf
            if den>=0.9 and (best is None or cov>best[1]): best=(t,cov,den)
        print(f"  {e:22s} delta>=%+.1f%% (cov=%.2f den=%.2f)"%(best[0]*100,best[1],best[2]) if best else f"  {e}: sem caixa")
