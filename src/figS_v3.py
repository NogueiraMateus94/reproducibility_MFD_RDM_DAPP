# -*- coding: utf-8 -*-
# Figure S1 (v3): sensitivity of robustness to margin amplitude. No internal title (professor comment).
import warnings; warnings.filterwarnings("ignore")
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
TEAL="#2E8B7A"; PURP="#6B5B95"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"figure.dpi":200,"axes.edgecolor":"#555","axes.linewidth":0.8})
fig,axs=plt.subplots(1,2,figsize=(12,4.6))
# --- left: epsilon amplitude ---
eps_x=[5,10,20,30]; eps_r=[50.2,47.8,39.2,35.0]
ax=axs[0]
ax.plot(eps_x,eps_r,"-o",color=TEAL,lw=2,ms=8)
for x,y in zip(eps_x,eps_r):
    ax.annotate(f"{y:.1f}%",(x,y),xytext=(0,10),textcoords="offset points",ha="center",fontsize=8.5,fontweight="bold",color=TEAL)
ax.set_xlabel("Specification margin amplitude  ±ε  (%)",fontsize=9.5)
ax.set_ylabel("Robustness of the selected strategy  ρ",fontsize=9.5)
ax.set_xticks(eps_x); ax.set_ylim(30,95)
ax.text(0.5,0.06,"Winner: intermediate-coverage in all cases · PRIM box retains only δ",
        transform=ax.transAxes,ha="center",fontsize=7.5,style="italic",color="#777")
ax.grid(ls=":",color="#eee"); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
# --- right: delta amplitude ---
d_lab=["[−8,+15]","[−15,+30]","[−22,+45]"]; d_x=[0,1,2]; d_r=[65.2,47.8,41.9]; d_star=["+6.8%","+5.1%","+3.4%"]
ax=axs[1]
ax.plot(d_x,d_r,"-o",color=PURP,lw=2,ms=8)
for x,y,s in zip(d_x,d_r,d_star):
    ax.annotate(f"{y:.1f}%\n(δ*={s})",(x,y),xytext=(0,12),textcoords="offset points",ha="center",fontsize=8.5,fontweight="bold",color=PURP)
ax.set_xlabel("Cost margin amplitude  δ  (%)",fontsize=9.5)
ax.set_xticks(d_x); ax.set_xticklabels(d_lab); ax.set_ylim(30,95)
ax.text(0.5,0.06,"Winner: intermediate-coverage in all cases",
        transform=ax.transAxes,ha="center",fontsize=7.5,style="italic",color="#777")
ax.grid(ls=":",color="#eee"); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig("figS1_sensitivity_v3.png",bbox_inches="tight")
plt.close(); print("Figure S1 (v3) generated")
