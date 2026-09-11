# Reproducibility package — *From Robust Architecture to Adaptive Pathways*

Code and data underlying the decision model and analyses of *From Robust Architecture to
Adaptive Pathways: Designing a Modular Grain Sampler Under Deep Uncertainty* — Chapter 4
and Appendix B of the master's thesis *Product Family Design in Contexts of Deep
Uncertainty* (Mateus Nogueira, PPGEPS/Unisinos, 2026), and the manuscript derived from it.
Everything reported there is reproducible from this package with a fixed random seed.

This is the **v3** package, matching the restructured Modular Function Deployment
front-end: surface finish is modelled as a global product property (not a module),
in-line quality sensing (NIR) is its own module, and the collection module carries the
grain/sugar/suction probes. The buildable space is 4,536 configurations.

## Requirements

- Python 3.9+
- `numpy`, `pandas`, `scipy`, `matplotlib`

```
pip install -r requirements.txt
```

`requirements.txt` states minimum versions. `requirements-lock.txt` records the exact
versions of the last verified run — pin those if the reported figures ever have to be
reproduced bit for bit.

## Structure

```
src/
  modelo_R.py             Core R-model: utility U_p and variable cost C_p
  arquitetura_saur_v3.py  Case architecture: 5 segments, 13 utility properties,
                          10 modules (M1 collection incl. suction probe ... M9 electrical
                          panel, M10 NIR) plus the global finish property, variant costs
                          and the coupling rules (coerente())
  cb_v3.py                Conduct-B sampling (delta in [-0.15,+0.30], eps in [-0.10,+0.10]);
                          frontier, 4 strategies, robustness and delta-PRIM
  cb_v3_full.py           Dumps _v3_data.json: rho, counts, PRIM, threshold grid,
                          regret, convergence. This is the authoritative run --
                          the numbers reported in the text come from here
  v3_frontier.py          Enumerates the buildable space and the efficiency frontier
  v3_calib_k11.py         Calibration of the finish property weight (port niche)
  fig_v3.py               Figure 2 (cost-utility plane and efficiency frontier)
  fig34_v3.py             Figure 3 (scenario discovery) and Figure 4 (regret)
  fig5_v3.py              Figure 5 (adaptive pathways map, 5-axis DAPP)
  anonymize_costs.py      Cost-scaling invariance helper (see "Confidentiality")
data/  (human-readable mirror of the parameters; the scripts do NOT read these
       files -- the values live in src/arquitetura_saur_v3.py and were checked
       against the CSVs)
  B1_segments.csv         Target segments and weight intervals W_seg
  B2_CVR.csv              Customer Value Ranking r_ij (needs x segments)
  B3_properties.csv       Product properties, monotonicity and target ranges
  B4_QFD.csv              QFD matrix r_ik (needs x properties)
  B5_variant_specs.csv    Module-variant nominal levels and variable costs
  global_params.csv       U_MIN, C_MAX, margins, seed, ensemble size
```

**Property numbering.** `data/` and the code use a sequential index over the 13 utility
properties. The article's k-numbering additionally reserves k8 for acquisition cost
(handled separately, not a utility axis) and k15 for the general sampling-quality property
that the DPM/MIM documents at the MFD level; neither enters the quantitative enumeration.
The finish property (Prot) carries a QFD weight of zero — it is a port-terminal niche and
therefore originates no configuration on the frontier under the general-market weighting.

## Numbering: this package vs. the thesis

The scripts and this README use the manuscript's numbering. In the thesis:

| Here | In the thesis |
|---|---|
| Supplementary equations (1)-(31) | Equations **(49)-(79)** — add 48 |
| Supplementary tables S1-S16 | **Tables 15-30** — add 14 |
| Figure 2 (cost-utility plane, frontier) | **Figure 15** |
| Figure 3 (scenario discovery) | **Figure 16** |
| Figure 4 (regret) | **Figure 17** |
| Figure 5 (adaptive pathways map) | **Figure 18** |
| Figure S1 (margin-amplitude sensitivity) | **Figure 20** |
| Model formulation | **Appendix B, Section 1** |

## Reproducibility settings

- Random seed: **42** (Latin Hypercube Sampling implemented in-house).
- Baseline ensemble: **N = 800** scenarios (convergence criterion in the supplementary).
- Conduct B input margins: cost deviation delta in [-15%, +30%]; specification margin
  epsilon in [-10%, +10%].
- Thresholds: U_MIN = 0.45, C_MAX = 170,000 BRL.

The buildable configuration space and the efficiency frontier are deterministic; the
robustness, scenario-discovery, threshold-grid and regret analyses use the seeded ensemble.

## How to reproduce

From `src/`:

```
python cb_v3.py         # nominal points, robustness (rho), delta-PRIM boxes
python cb_v3_full.py    # rho, counts, PRIM, threshold grid, regret, convergence -> _v3_data.json
python fig_v3.py        # Figure 2 (cost-utility plane, efficiency frontier)
python fig34_v3.py      # Figure 3 (scenario discovery) and Figure 4 (regret)
python fig5_v3.py       # Figure 5 (adaptive pathways map)
```

Expected headline results: raw combinatorial space of 31,104 arrangements reduced to
**4,536** buildable configurations; efficiency frontier of **28** configurations (about
half inside the admitted region). Robustness: intermediate-coverage **47.8%**, dual-lane
**33.2%**; the two reference strategies are infeasible by construction (cost-entry below
the utility floor, premium-focus above the cost ceiling), so each has robustness 0%.
Scenario discovery: cost-margin PRIM box at delta >= **+5.1%** (coverage 0.95) for
intermediate-coverage and delta >= **-3.4%** (coverage 1.00) for dual-lane. Regret rank
correlation (utility vs cost) **-0.94**; convergence within 1% by N = 800.

## Confidentiality — cost anonymization (optional)

The architecture file carries the firm's absolute variable costs. If those must be
withheld, multiply every monetary value by a single undisclosed constant *k* (each
module-variant nominal cost and the ceiling C_MAX). Because utility, the dimensionless
margins delta and epsilon, and the ceiling all scale together, the robustness ranking,
the PRIM vulnerability region (in delta) and the threshold grid are **invariant**.

```
python anonymize_costs.py 0.573
```

## Licence

Code under the MIT licence; the files under `data/` under CC BY 4.0. See `LICENSE`.

## Citation

Machine-readable metadata is in `CITATION.cff`. In text:

> Nogueira, M.A.S., Gauss, L., de Kwant, C. and Nascimento de Lima, P. (2026).
> *Reproducibility package for "From Robust Architecture to Adaptive Pathways: Designing
> a Modular Grain Sampler Under Deep Uncertainty"*. [DOI to be inserted]
