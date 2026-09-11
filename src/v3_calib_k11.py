# -*- coding: utf-8 -*-
import warnings; warnings.filterwarnings("ignore")
import numpy as np, itertools
import arquitetura_saur_v3 as A3
from modelo_R import (Cenario, importancia_necessidades, importancia_propriedades,
                      normalizar_pesos_propriedade, normalizar_nivel,
                      agregar_niveis_produto, custo_variante)

def frontier_stats(prot_durab):
    ARQ, LIM = A3.arquitetura_saur()
    # Prot (k11) é a coluna índice 9 da QFD; linha 5 (Durabilidade) domina.
    ARQ.QFD[4,9] = prot_durab   # Durabilidade -> Prot
    wm = (LIM["w_seg_min"]+LIM["w_seg_max"])/2; wm = wm/wm.sum()
    CEN = Cenario(wm, {p.nome:0.0 for p in ARQ.propriedades}, 0.0)
    WPROP = normalizar_pesos_propriedade(importancia_propriedades(ARQ, importancia_necessidades(ARQ, wm)))
    w_k11 = WPROP[9]
    def vms(cfg): return [next(v for v in ARQ.variantes_modulo[m] if v.nome==cfg[m]) for m in ARQ.modulos]
    def avaliar(vl):
        U=sum(WPROP[k]*normalizar_nivel(p,agregar_niveis_produto(ARQ,p,vl,CEN)) for k,p in enumerate(ARQ.propriedades))
        return U, custo_variante(vl,CEN)
    opcoes=[[v.nome for v in ARQ.variantes_modulo[m]] for m in ARQ.modulos]
    dados=[]
    for combo in itertools.product(*opcoes):
        cfg=dict(zip(ARQ.modulos,combo))
        if not A3.coerente(cfg): continue
        U,C=avaliar(vms(cfg)); dados.append((U,C,cfg))
    o=sorted(dados,key=lambda t:(t[1],-t[0])); pf=[]; mU=-1e9
    for u,c,cfg in o:
        if u>mU+1e-12: pf.append((u,c,cfg)); mU=u
    mar=sum(1 for u,c,cfg in pf if cfg["Acabamento"]=="Pintura marítima")
    return len(pf), mar, w_k11

print("Durab->Prot | fronteira | marítima | peso_k11")
for pd in [9,5,3,2,1]:
    n,mar,w = frontier_stats(pd)
    print(f"     {pd}      |    {n}     |   {mar} ({100*mar/n:.0f}%)   | {w:.4f}")
