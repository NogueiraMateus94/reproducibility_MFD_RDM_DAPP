# -*- coding: utf-8 -*-
"""
Cost anonymization helper (v3).

If absolute monetary values must be withheld, every cost is multiplied by a single
undisclosed constant k (each module-variant nominal cost and the cost ceiling C_MAX).
Because the utility U_p, the dimensionless deviation margins epsilon and delta, and the
cost ceiling all scale together, the robustness ranking, the PRIM vulnerability region
(expressed in delta) and the threshold grid are INVARIANT.

Usage:  python anonymize_costs.py [k]        (default k = 0.573)
"""
import sys, warnings; warnings.filterwarnings("ignore")
import cb_v3 as CB

def rho_at_scale(k, N=800, seed=42):
    saved = {}
    for m in CB.ARQ.modulos:
        for v in CB.ARQ.variantes_modulo[m]:
            saved[id(v)] = v.custo_nom
            v.custo_nom = v.custo_nom * k
    cmax = CB.C_MAX * k
    try:
        _, store, _, _, _ = CB.eval_full(CB.EST, N, seed)
        rho = {e: CB.robust(store, e, CB.U_MIN, cmax).mean() for e in CB.EST}
    finally:
        for m in CB.ARQ.modulos:
            for v in CB.ARQ.variantes_modulo[m]:
                v.custo_nom = saved[id(v)]
    return rho

if __name__ == "__main__":
    k = float(sys.argv[1]) if len(sys.argv) > 1 else 0.573
    r1 = rho_at_scale(1.0); rk = rho_at_scale(k)
    print(f"{'strategy':26s} {'rho (k=1, BRL)':>16s} {'rho (k='+str(k)+')':>16s}")
    for e in r1:
        print(f"{e:26s} {r1[e]*100:15.1f}% {rk[e]*100:15.1f}%")
    print("\nConclusions invariant under cost scaling:",
          all(abs(r1[e]-rk[e]) < 1e-12 for e in r1))
