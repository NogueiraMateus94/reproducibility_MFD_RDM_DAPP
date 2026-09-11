# ===============================================================
# MODELO R — Cadeia de relacionamentos (componente R do XLRM)
# Projeto de famílias de produtos sob incerteza profunda
# Implementa as Eqs. 1-11 e 23-30 do manuscrito (Rev10)
# ===============================================================
#
# Papel deste módulo dentro do RDM:
#   O componente R do framework XLRM (Seção 4.5.1) é o conjunto de
#   relacionamentos analíticos que, dado um CENÁRIO (vetor de incertezas
#   theta) e uma ARQUITETURA modular fixa, devolve as MEDIDAS de
#   desempenho de cada variante de produto: utilidade U_p (Eq. 11) e
#   custo variável C_p (agregação da Eq. 26 / Eq. 30).
#
#   Este é exatamente o bloco que NÃO existia no código herdado
#   (domínio farmacêutico). A casca RDM (EMA/PRIM/Regret) será conectada
#   numa etapa posterior; aqui foca-se só em R.
#
# Observação de escopo:
#   Os dados em `exemplo_arquitetura()` são ILUSTRATIVOS (temática de
#   veículos elétricos, citada no manuscrito). Servem apenas para validar
#   a cadeia de equações. A arquitetura real (família Saur ou outra)
#   substitui esse bloco sem alterar a lógica.
# ===============================================================

from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np


# ---------------------------------------------------------------
# ESTRUTURA DA ARQUITETURA (entradas fixas do projeto)
# ---------------------------------------------------------------

@dataclass
class Propriedade:
    nome: str
    monotonicidade: str          # "crescente" (quanto maior melhor) ou "decrescente"
    l_min: float                 # limite inferior dos valores-alvo (Eq. 8-9)
    l_max: float                 # limite superior dos valores-alvo
    agregacao: str = "aditiva"   # "aditiva" | "multiplicativa"  (Eq. 30)


@dataclass
class VarianteModulo:
    nome: str
    # nível NOMINAL realizado por esta variante para cada propriedade
    # (Eq. 23). Propriedades não afetadas omitidas -> elemento neutro.
    niveis_nom: dict[str, float]
    custo_nom: float             # custo variável nominal C_mq^nom (Eq. 24)


@dataclass
class Arquitetura:
    segmentos: list[str]                       # j = 1..J
    necessidades: list[str]                    # i = 1..I
    propriedades: list[Propriedade]            # k = 1..K
    CVR: np.ndarray                            # I x J, rankings r_ij (1..I)
    QFD: np.ndarray                            # I x K, escala log {0,1,3,9}
    modulos: list[str]                         # m = 1..M
    variantes_modulo: dict[str, list[VarianteModulo]]   # modulo -> variantes
    # Tabela de Configuração (Eq. 27): variante de produto -> {modulo: nome_variante}
    config: dict[str, dict[str, str]]

    def __post_init__(self):
        self.J = len(self.segmentos)
        self.I = len(self.necessidades)
        self.K = len(self.propriedades)
        self.prop_idx = {p.nome: idx for idx, p in enumerate(self.propriedades)}


# ---------------------------------------------------------------
# CENÁRIO (vetor de incertezas theta — componente X do XLRM)
# ---------------------------------------------------------------
#
# Num cenário, sorteiam-se SEM probabilidades (intervalos plausíveis):
#   - pesos de segmento W_seg,j  (Eq. 1), sujeitos a Σ W_seg,j = 1
#   - desvio realizado de nível por propriedade (dentro de ±eps_max) (Eq. 23)
#   - desvio realizado de custo (dentro de ±delta_max) (Eq. 26)
#
# Aqui o cenário é um dicionário; o acoplamento ao LHS do EMA Workbench
# fica para a etapa de integração da casca RDM.

@dataclass
class Cenario:
    w_seg: np.ndarray                 # vetor J, já normalizado (Σ = 1)
    desvio_nivel: dict[str, float]    # propriedade -> fator em [-eps_max, +eps_max]
    desvio_custo: float               # fator global em [-delta_max, +delta_max]
    # Opcional: rankings r_ij também podem ser incertos; por ora fixos na arquitetura.


def amostrar_pesos_simplex(rng: np.random.Generator, J: int,
                           w_min: np.ndarray, w_max: np.ndarray) -> np.ndarray:
    """
    Sorteia W_seg,j respeitando Σ W_seg,j = 1 (Eq. 1).

    PONTO-CHAVE que o código herdado NÃO trata: o EMA amostra cada
    RealParameter de forma independente, o que viola a soma unitária.
    Aqui sorteia-se dentro dos limites [w_min, w_max] e renormaliza-se
    para o simplex. (Alternativa mais rigorosa: amostragem Dirichlet.)
    """
    bruto = rng.uniform(w_min, w_max)
    return bruto / bruto.sum()


# ---------------------------------------------------------------
# CADEIA DE EQUAÇÕES
# ---------------------------------------------------------------

def importancia_necessidades(arq: Arquitetura, w_seg: np.ndarray) -> np.ndarray:
    """
    W_nec,i = Σ_j W_seg,j · r_ij        (Eq. 2)
    Retorna vetor de tamanho I.
    """
    return arq.CVR @ w_seg


def importancia_propriedades(arq: Arquitetura, w_nec: np.ndarray) -> np.ndarray:
    """
    W_prop,k = Σ_i W_nec,i · r_ik       (Eq. 6)
    Retorna vetor de tamanho K.
    """
    return arq.QFD.T @ w_nec


def normalizar_pesos_propriedade(w_prop: np.ndarray) -> np.ndarray:
    """
    W̄_prop,k = W_prop,k / Σ_k W_prop,k   (Eq. 10) -> soma 1.
    """
    return w_prop / w_prop.sum()


def normalizar_nivel(prop: Propriedade, l_pk: float) -> float:
    """
    Normaliza o nível efetivo da variante (Eqs. 8 e 9).
    Crescente:   (l - l_min) / (l_max - l_min)
    Decrescente: (l_max - l) / (l_max - l_min)
    Valores ~1 => mais desejáveis. Pode extrapolar 1 (ver Tabela 2, M).
    """
    span = prop.l_max - prop.l_min
    if span == 0:
        return 0.0
    if prop.monotonicidade == "crescente":
        return (l_pk - prop.l_min) / span
    else:  # decrescente
        return (prop.l_max - l_pk) / span


def nivel_efetivo_variante_modulo(vm: VarianteModulo, prop_nome: str,
                                  desvio: float) -> float:
    """
    Nível efetivo de uma variante de módulo para a propriedade,
    aplicando a margem de erro de especificação (Eq. 23):
        l = l_nom · (1 + desvio),  desvio ∈ [-eps_max, +eps_max]
    """
    l_nom = vm.niveis_nom.get(prop_nome, None)
    if l_nom is None:
        return None
    return l_nom * (1.0 + desvio)


def agregar_niveis_produto(arq: Arquitetura, prop: Propriedade,
                           variantes_mod: list[VarianteModulo],
                           cen: Cenario) -> float:
    """
    Nível efetivo da variante de PRODUTO para a propriedade k,
    agregando as variantes de módulo que a compõem (Eq. 30).
        Aditiva:        Σ l_mq,k
        Multiplicativa: Π l_mq,k
    Módulos que não afetam a propriedade usam o elemento neutro
    (0 para soma, 1 para produto).
    """
    desvio = cen.desvio_nivel.get(prop.nome, 0.0)
    contrib = []
    for vm in variantes_mod:
        l = nivel_efetivo_variante_modulo(vm, prop.nome, desvio)
        if l is not None:
            contrib.append(l)
    if not contrib:
        return prop.l_min  # propriedade não realizada por nenhum módulo
    if prop.agregacao == "aditiva":
        return float(np.sum(contrib))
    else:  # multiplicativa
        return float(np.prod(contrib))


def utilidade_variante(arq: Arquitetura, w_prop_norm: np.ndarray,
                       variantes_mod: list[VarianteModulo],
                       cen: Cenario) -> float:
    """
    U_p = Σ_k W̄_prop,k · l̄_pk            (Eq. 11)
    """
    U = 0.0
    for k, prop in enumerate(arq.propriedades):
        l_pk = agregar_niveis_produto(arq, prop, variantes_mod, cen)
        l_norm = normalizar_nivel(prop, l_pk)
        U += w_prop_norm[k] * l_norm
    return U


def custo_variante(variantes_mod: list[VarianteModulo], cen: Cenario) -> float:
    """
    Custo variável efetivo da variante de produto: soma dos custos das
    variantes de módulo (Eq. 26 agregada aditivamente, cf. medida M da
    Tabela 2): C_p = Σ C_mq · (1 + delta),  delta ∈ [-delta_max, +delta_max].
    """
    fator = 1.0 + cen.desvio_custo
    return float(sum(vm.custo_nom for vm in variantes_mod) * fator)


# ---------------------------------------------------------------
# MODELO R COMPLETO  (theta + portfólio -> medidas M)
# ---------------------------------------------------------------

def modelo_R(arq: Arquitetura, cen: Cenario,
             portfolio: list[str] | None = None) -> dict[str, dict[str, float]]:
    """
    Avalia as medidas de desempenho (U_p, C_p) de cada variante de produto
    de um portfólio, num dado cenário.

    Parâmetros
    ----------
    arq        : arquitetura modular fixa
    cen        : cenário (vetor de incertezas theta)
    portfolio  : lista de nomes de variantes de produto a avaliar
                 (subconjunto P_ℓ ⊆ {V_1..V_P}, componente L). Se None,
                 avalia todas as variantes definidas na config.

    Retorna
    -------
    dict {nome_variante: {"U": ..., "C": ...}}
    """
    # --- Propagação de importâncias (depende do cenário via w_seg) ---
    w_nec = importancia_necessidades(arq, cen.w_seg)          # Eq. 2
    w_prop = importancia_propriedades(arq, w_nec)             # Eq. 6
    w_prop_norm = normalizar_pesos_propriedade(w_prop)        # Eq. 10

    if portfolio is None:
        portfolio = list(arq.config.keys())

    resultado = {}
    for vp_nome in portfolio:
        # variantes de módulo que compõem esta variante de produto (Eq. 27)
        comp = arq.config[vp_nome]
        variantes_mod = []
        for modulo, vm_nome in comp.items():
            vm = next(v for v in arq.variantes_modulo[modulo] if v.nome == vm_nome)
            variantes_mod.append(vm)

        U = utilidade_variante(arq, w_prop_norm, variantes_mod, cen)   # Eq. 11
        C = custo_variante(variantes_mod, cen)                         # Eq. 26
        resultado[vp_nome] = {"U": U, "C": C}

    return resultado


# ---------------------------------------------------------------
# EXEMPLO ILUSTRATIVO (placeholder — substituir pela arquitetura real)
# ---------------------------------------------------------------

def exemplo_arquitetura() -> tuple[Arquitetura, dict]:
    """
    Exemplo mínimo coerente: família de veículos elétricos.
      Segmentos (J=3): Urbano, Familiar, Performance
      Necessidades (I=4): Autonomia, Conforto, Custo de aquisição, Desempenho
      Propriedades (K=3): autonomia_km (cresc.), potencia_cv (cresc.), peso_kg (decresc.)
      Módulos (3): Bateria, Powertrain, Estrutura
    """
    segmentos = ["Urbano", "Familiar", "Performance"]
    necessidades = ["Autonomia", "Conforto", "Custo_aquisicao", "Desempenho"]

    propriedades = [
        Propriedade("autonomia_km", "crescente", l_min=250, l_max=650, agregacao="aditiva"),
        Propriedade("potencia_cv", "crescente", l_min=90,  l_max=400, agregacao="aditiva"),
        Propriedade("peso_kg",     "decrescente", l_min=1300, l_max=2200, agregacao="aditiva"),
    ]

    # CVR (I x J): ranking de cada necessidade em cada segmento (1=menos, I=mais prioritária)
    #            Urbano  Familiar  Performance
    CVR = np.array([
        [3, 2, 2],   # Autonomia
        [2, 4, 1],   # Conforto
        [4, 3, 1],   # Custo de aquisição (alta prioridade p/ Urbano)
        [1, 1, 4],   # Desempenho (alta prioridade p/ Performance)
    ], dtype=float)

    # QFD (I x K): relação necessidade x propriedade, escala log {0,1,3,9}
    #              autonomia  potencia  peso
    QFD = np.array([
        [9, 1, 3],   # Autonomia
        [0, 1, 3],   # Conforto
        [1, 1, 9],   # Custo de aquisição (sensível a peso/material)
        [1, 9, 3],   # Desempenho
    ], dtype=float)

    modulos = ["Bateria", "Powertrain", "Estrutura"]

    variantes_modulo = {
        "Bateria": [
            VarianteModulo("Bat_Std", {"autonomia_km": 320, "peso_kg": 480}, custo_nom=8000),
            VarianteModulo("Bat_LR",  {"autonomia_km": 520, "peso_kg": 620}, custo_nom=13500),
        ],
        "Powertrain": [
            VarianteModulo("PT_Eco",   {"potencia_cv": 130, "peso_kg": 180}, custo_nom=4200),
            VarianteModulo("PT_Sport", {"potencia_cv": 340, "peso_kg": 240}, custo_nom=9800),
        ],
        "Estrutura": [
            VarianteModulo("Est_Aco",  {"peso_kg": 950}, custo_nom=3000),
            VarianteModulo("Est_Alu",  {"peso_kg": 720}, custo_nom=5600),
        ],
    }

    # Tabela de Configuração (Eq. 27): cada variante de produto = combinação de variantes de módulo
    config = {
        "V_Urbano":     {"Bateria": "Bat_Std", "Powertrain": "PT_Eco",   "Estrutura": "Est_Aco"},
        "V_Familiar":   {"Bateria": "Bat_LR",  "Powertrain": "PT_Eco",   "Estrutura": "Est_Aco"},
        "V_Performance":{"Bateria": "Bat_LR",  "Powertrain": "PT_Sport", "Estrutura": "Est_Alu"},
        "V_Premium":    {"Bateria": "Bat_LR",  "Powertrain": "PT_Sport", "Estrutura": "Est_Aco"},
    }

    arq = Arquitetura(segmentos, necessidades, propriedades, CVR, QFD,
                      modulos, variantes_modulo, config)

    # Limites de incerteza (intervalos plausíveis, sem probabilidades)
    limites = {
        "w_seg_min": np.array([0.20, 0.25, 0.10]),   # W_seg,j^min (Eq. 1)
        "w_seg_max": np.array([0.45, 0.50, 0.35]),   # W_seg,j^max
        "eps_max": 0.08,                              # margem de especificação (Eq. 22)
        "delta_max": 0.15,                            # margem de custo (Eq. 25)
    }
    return arq, limites


def cenario_aleatorio(arq: Arquitetura, limites: dict,
                      rng: np.random.Generator) -> Cenario:
    """Gera um cenário sorteando theta dentro dos intervalos plausíveis."""
    w_seg = amostrar_pesos_simplex(rng, arq.J,
                                   limites["w_seg_min"], limites["w_seg_max"])
    desvio_nivel = {
        p.nome: rng.uniform(-limites["eps_max"], limites["eps_max"])
        for p in arq.propriedades
    }
    desvio_custo = rng.uniform(-limites["delta_max"], limites["delta_max"])
    return Cenario(w_seg=w_seg, desvio_nivel=desvio_nivel, desvio_custo=desvio_custo)


# ---------------------------------------------------------------
# DEMONSTRAÇÃO
# ---------------------------------------------------------------

def _demo():
    rng = np.random.default_rng(42)
    arq, limites = exemplo_arquitetura()

    print("=" * 64)
    print("MODELO R — demonstração (exemplo ilustrativo VE)")
    print("=" * 64)

    # Cenário "nominal" (sem desvios, pesos no ponto médio renormalizado)
    w_med = (limites["w_seg_min"] + limites["w_seg_max"]) / 2
    w_med = w_med / w_med.sum()
    cen_nom = Cenario(w_seg=w_med,
                      desvio_nivel={p.nome: 0.0 for p in arq.propriedades},
                      desvio_custo=0.0)

    print(f"\nPesos de segmento (nominal): "
          f"{dict(zip(arq.segmentos, np.round(cen_nom.w_seg, 3)))}")

    w_nec = importancia_necessidades(arq, cen_nom.w_seg)
    w_prop = importancia_propriedades(arq, w_nec)
    w_prop_norm = normalizar_pesos_propriedade(w_prop)
    print("\nImportância das necessidades (Eq. 2):")
    for nome, val in zip(arq.necessidades, w_nec):
        print(f"   {nome:<18} {val:6.3f}")
    print("\nImportância normalizada das propriedades (Eqs. 6+10):")
    for p, val in zip(arq.propriedades, w_prop_norm):
        print(f"   {p.nome:<14} {val:6.3f}")

    print("\n--- Medidas no cenário NOMINAL ---")
    res_nom = modelo_R(arq, cen_nom)
    for vp, m in res_nom.items():
        print(f"   {vp:<16} U_p = {m['U']:.3f}   C_p = R$ {m['C']:,.0f}")

    # Variabilidade sob incerteza: distribuição de U_p e C_p em N cenários
    N = 2000
    Us = {vp: [] for vp in arq.config}
    Cs = {vp: [] for vp in arq.config}
    for _ in range(N):
        cen = cenario_aleatorio(arq, limites, rng)
        res = modelo_R(arq, cen)
        for vp, m in res.items():
            Us[vp].append(m["U"])
            Cs[vp].append(m["C"])

    print(f"\n--- Faixa de U_p e C_p em {N} cenários (incerteza profunda) ---")
    print(f"{'Variante':<16}{'U_p [min..max]':<26}{'C_p [min..max] (R$)':<28}")
    for vp in arq.config:
        u = np.array(Us[vp]); c = np.array(Cs[vp])
        print(f"{vp:<16}"
              f"[{u.min():.3f} .. {u.max():.3f}]      "
              f"[{c.min():,.0f} .. {c.max():,.0f}]")

    print("\n" + "=" * 64)
    print("OK — cadeia de equações Eqs. 1-11 e 23-30 executada.")
    print("=" * 64)


if __name__ == "__main__":
    _demo()
