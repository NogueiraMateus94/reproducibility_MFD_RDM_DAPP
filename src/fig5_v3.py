# Adaptive Pathways Map — Intermediate-coverage strategy (v3, EN, no internal title)
# Five uncertainty axes. Cost tipping updated to +5.1% (warning +4%).
import warnings; warnings.filterwarnings("ignore")
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

AZUL = "#2d4a6b"
COR = {"MT": "#C0622E", "HG": "#2E8B7A", "CP": "#B8860B", "MD": "#6B5B95"}
PORT = "#7f7f7f"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                     "axes.edgecolor": "#333", "axes.linewidth": 0.9})

PORTLABEL = "Portfolio  P₂  (Intermediate cov.)"
HL = 8.0
xL = -0.4
TIP_OFF = 0.6

def desenha_regua(ax, y, marcas, label, xmax_linha):
    ax.annotate("", xy=(xmax_linha, y), xytext=(xL, y),
                arrowprops=dict(arrowstyle="->", color="#333", lw=1.2))
    for x, rot in marcas:
        ax.plot([x, x], [y-0.12, y+0.12], color="#333", lw=0.9)
        ax.text(x, y-0.32, rot, ha="center", va="top", fontsize=6.8, color="#555")
    ax.text(xmax_linha+0.15, y-0.32, "(years)", ha="left", va="top", fontsize=6.5, color="#777")
    ax.text(xL-0.15, y, label, ha="right", va="center", fontsize=7.5, color="#333")

REGUA_LENTA_STD = [(0,"0"),(2,"2"),(4,"4"),(6,"6"),(8,"8")]
REGUA_RAPIDA_STD = [(0,"0"),(2,"1"),(4,"2")]

PAINEIS = [
    {"letra":"(a)", "titulo":"Axis — Total cost deviation  δ  (PRIM)",
     "condicao":"Condition:  δ = total cost deviation (%)",
     "cond_ticks":[(2.0,"+4%"),(4.0,"+5.1%")],
     "transf": 2.0, "tip_align": 4.0,
     "acoes":[("α₁: Alt. gear-motor suppliers  (HG)","HG"),
              ("α₂: Mobile-carriage productivity gain  (HG)","HG")],
     "regua_lenta":REGUA_LENTA_STD, "xmax_lenta":8.5,
     "regua_rapida":[(0,"0"),(2,"1"),(4,"2")], "xmax_rapida":4.6},
    {"letra":"(b)", "titulo":"Axis — Operational performance (conformity)",
     "condicao":"Condition:  sampling time (min)  |  conformity",
     "cond_ticks":[(2.0,"4 min")],
     "transf": 2.0,
     "acoes":[("α₄: New precision/speed components  (MT)","MT")],
     "nota_cond":"conformity = ≤ 4 min (largest truck, 11 pts) + assertiveness > 95% + reaches the bottom",
     "regua_lenta":REGUA_LENTA_STD, "xmax_lenta":8.5,
     "regua_rapida":[(0,"0"),(2,"0.5"),(4,"1")], "xmax_rapida":4.6},
    {"letra":"(c)", "titulo":"Axis — Market evolution (sugar)",
     "condicao":"Condition:  W$_{seg}$ (sugar-segment weight)",
     "cond_ticks":[(2.0,"~0.09"),(4.0,"0.18\n(max.)")],
     "transf": 2.0, "tip_align": 4.0,
     "acoes":[("α₅: Sugar-segment product line  (CP)","CP")],
     "regua_lenta":REGUA_LENTA_STD, "xmax_lenta":8.5,
     "regua_rapida":[(0,"0"),(2,"1"),(4,"2")], "xmax_rapida":4.6},
    {"letra":"(d)", "titulo":"Axis — On-demand (binary trigger)",
     "condicao":"Condition:  occurrence (0 → 1)",
     "cond_ticks":[(2.0,"1")],
     "transf": 2.0,
     "acoes":[("α₆: AI adaptation — coffee  (CP)","CP"),
              ("α₇: Panel vendor-list compliance  (MD)","MD")],
     "binario": True,
     "regua_lenta":[(0,"0"),(2,"event")], "xmax_lenta":4.6,
     "regua_rapida":[(0,"0"),(2,"event")], "xmax_rapida":4.6},
    {"letra":"(e)", "titulo":"Axis — Quick rod-change interface",
     "condicao":"Condition:  no. of clients with mixed demand",
     "cond_ticks":[(2.0,"> 3 clients")],
     "transf": 2.0,
     "acoes":[("α₃: Quick rod-change interface  (HG)","HG")],
     "regua_lenta":REGUA_LENTA_STD, "xmax_lenta":8.5,
     "regua_rapida":[(0,"0"),(2,"1"),(4,"2")], "xmax_rapida":4.6},
]

def desenha_painel(ax, P):
    acoes = P["acoes"]; n = len(acoes)
    y_port = n + 0.6
    y_acoes = [n - i - 0.4 for i in range(n)]
    transf = P["transf"]
    tip = P.get("tip_align", transf + TIP_OFF)
    ax.plot([xL, tip], [y_port, y_port], "-", color=PORT, lw=6, solid_capstyle="butt", zorder=3)
    ax.text(xL-0.15, y_port, PORTLABEL, ha="right", va="center", fontsize=8, color="#333")
    ax.plot([tip, tip], [y_port-0.22, y_port+0.22], "-", color="black", lw=3, zorder=5)
    ax.plot([transf, transf], [min(y_acoes), y_port], "-", color=PORT, lw=1.6, zorder=2)
    for (label, tipo), yy in zip(acoes, y_acoes):
        cor = COR[tipo]
        ax.plot([transf, HL], [yy, yy], "-", color=cor, lw=6, solid_capstyle="butt", zorder=3)
        ax.plot([transf], [yy], "o", ms=11, mfc="white", mec=cor, mew=2.5, zorder=6)
        ax.text(xL-0.15, yy, label, ha="right", va="center", fontsize=7.8, color="#333")
        ax.annotate("", xy=(HL+0.18, yy), xytext=(HL-0.02, yy),
                    arrowprops=dict(arrowstyle="->", color=cor, lw=1.8), zorder=3)
    y_cond = -0.9; y_lento = -1.9; y_rapido = -2.9
    y_top = y_port + 0.9
    ax.annotate("", xy=(HL+0.35, y_cond), xytext=(xL, y_cond),
                arrowprops=dict(arrowstyle="->", color="#333", lw=1.2))
    ax.text(xL-0.15, y_cond, P["condicao"], ha="right", va="center", fontsize=7.3, color="#333")
    for cx, clab in P.get("cond_ticks", []):
        ax.plot([cx, cx], [y_cond-0.13, y_cond+0.13], color="#B22222", lw=1.4, zorder=4)
        ax.text(cx, y_cond+0.20, clab, ha="center", va="bottom", fontsize=6.6,
                color="#B22222", fontweight="bold")
    if P.get("nota_cond"):
        ax.text(xL, y_cond-0.42, P["nota_cond"], ha="left", va="top", fontsize=6.2,
                style="italic", color="#777")
    desenha_regua(ax, y_lento, P["regua_lenta"], "Slow evolution", P["xmax_lenta"])
    desenha_regua(ax, y_rapido, P["regua_rapida"], "Fast evolution", P["xmax_rapida"])
    ax.set_title(f"{P['letra']}  {P['titulo']}", fontsize=9.3, fontweight="bold",
                 color=AZUL, loc="left", pad=6)
    ax.set_xlim(-5.7, HL+1.0)
    ax.set_ylim(y_rapido-0.9, y_top)
    ax.axis("off")

fig, axs = plt.subplots(5, 1, figsize=(9.4, 15.5))
for ax, P in zip(axs, PAINEIS):
    desenha_painel(ax, P)

leg = [
    Line2D([0],[0], marker="o", color="w", mfc="white", mec="#555", mew=2.2, ms=11, label="Transfer point"),
    Line2D([0],[0], color=PORT, lw=6, label="Portfolio"),
    Line2D([0],[0], marker="|", color="black", markersize=13, markeredgewidth=3, linestyle="None", label="Adaptation tipping point"),
    Line2D([0],[0], color=COR["MT"], lw=6, label="MT mitigation"),
    Line2D([0],[0], color=COR["HG"], lw=6, label="HG protection"),
    Line2D([0],[0], color=COR["CP"], lw=6, label="CP capitalization"),
    Line2D([0],[0], color=COR["MD"], lw=6, label="MD modification"),
]
fig.legend(handles=leg, loc="lower center", ncol=4, frameon=True, fontsize=8,
           bbox_to_anchor=(0.5, -0.005))
plt.tight_layout(rect=[0, 0.025, 1, 1.0])
plt.savefig("fig5_pathways_v3.png", dpi=200, bbox_inches="tight")
plt.close()
print("Figure 5 (v3, EN) generated")
