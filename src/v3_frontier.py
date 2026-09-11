# -*- coding: utf-8 -*-
import warnings; warnings.filterwarnings("ignore")
import numpy as np, itertools
import arquitetura_saur_v3 as A3
from modelo_R import (Cenario, importancia_necessidades, importancia_propriedades,
                      normalizar_pesos_propriedade, normalizar_nivel,
                      agregar_niveis_produto, custo_variante)
ARQ, LIM = A3.arquitetura_saur()
wm = (LIM["w_seg_min"]+LIM["w_seg_max"])/2; wm = wm/wm.sum()
CEN = Cenario(wm, {p.nome:0.0 for p in ARQ.propriedades}, 0.0)
WPROP = normalizar_pesos_propriedade(importancia_propriedades(ARQ, importancia_necessidades(ARQ, wm)))
def vms(cfg): return [next(v for v in ARQ.variantes_modulo[m] if v.nome==cfg[m]) for m in ARQ.modulos]
def avaliar(vlist):
    U = sum(WPROP[k]*normalizar_nivel(p, agregar_niveis_produto(ARQ,p,vlist,CEN)) for k,p in enumerate(ARQ.propriedades))
    return U, custo_variante(vlist, CEN)
opcoes=[[v.nome for v in ARQ.variantes_modulo[m]] for m in ARQ.modulos]
dados=[]
for combo in itertools.product(*opcoes):
    cfg=dict(zip(ARQ.modulos,combo))
    if not A3.coerente(cfg): continue
    U,C=avaliar(vms(cfg)); dados.append((U,C,cfg))
print("configs construíveis:",len(dados))
o=sorted(dados,key=lambda t:(t[1],-t[0])); pf=[]; mU=-1e9
for u,c,cfg in o:
    if u>mU+1e-12: pf.append((u,c,cfg)); mU=u
print("pontos na fronteira:",len(pf))
print("faixa custo fronteira: %.0f a %.0f"%(pf[0][1],pf[-1][1]))
print("faixa U: %.3f a %.3f"%(pf[0][0],pf[-1][0]))
# quantos da fronteira têm NIR / sucção / marítima
nir=sum(1 for u,c,cfg in pf if cfg["M10"]=="Com NIR")
suc=sum(1 for u,c,cfg in pf if "sucção" in cfg["M1"].lower())
mar=sum(1 for u,c,cfg in pf if cfg["Acabamento"]=="Pintura marítima")
print(f"fronteira: com NIR={nir}, com sucção={suc}, marítima={mar}")
# print frontier compactly
print("\n#  U      C        M1 / M6 / M8 / M10(NIR) / Acab")
for i,(u,c,cfg) in enumerate(pf):
    print("%2d %.3f %8.0f  %s | %s | %s | %s | %s"%(i,u,c,cfg["M1"][:14],cfg["M6"][:12],cfg["M8"][:12],cfg["M10"],cfg["Acabamento"][:8]))
