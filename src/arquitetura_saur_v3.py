# ===============================================================
# ARQUITETURA SAUR v3 — REESTRUTURAÇÃO retorno ago/26_2
# Mudanças vs v2:
#   - Acabamento deixa de ser módulo (M9 antigo) -> propriedade global k11,
#     modelada como dimensão "Acabamento" (padrão/marítima) aplicada ao produto.
#   - Antigo M10 (quadro elétrico) -> renumerado como M9.
#   - M1 dividido: extração (fina/grossa/helicoide + SUCÇÃO) fica no M1;
#     o NIR sai para um módulo próprio M10 (sem/com NIR), entregando k14.
#   - Nova propriedade k14 "Verificação de qualidade in-line" (0..5) -> NIR.
#   - Novos acoplamentos: NIR só com haste de grão (fina/grossa);
#     sucção usa transporte pneumático (grão).
# Requer na MESMA pasta: modelo_R.py
# ===============================================================
import numpy as np
from modelo_R import (Arquitetura, Propriedade, VarianteModulo, Cenario,
                      modelo_R, importancia_necessidades, importancia_propriedades,
                      normalizar_pesos_propriedade)


def arquitetura_saur():
    segmentos = ["Unid. logísticas", "Armazéns e coop.",
                 "Term. portuários", "Usinas óleo/farelo", "Usinas açúcar"]
    necessidades = ["Confiabilidade amostra", "Velocidade", "Automação", "Segurança",
                    "Durabilidade", "Rastreabilidade", "Integração", "Custo aquisição"]

    # 13 propriedades de utilidade (k8 custo fora daqui). k14 nova = NIR.
    propriedades = [
        Propriedade("Qtd", "crescente", 12, 55, "aditiva"),      # k1
        Propriedade("Vaz", "crescente", 8, 40, "aditiva"),       # k2
        Propriedade("Tmp", "decrescente", 90, 450, "aditiva"),   # k3
        Propriedade("Aut", "crescente", 2, 5, "aditiva"),        # k4
        Propriedade("Tel", "crescente", 2, 4, "aditiva"),        # k5
        Propriedade("Alc", "crescente", 18, 24, "aditiva"),      # k6
        Propriedade("Vid", "crescente", 30, 80, "aditiva"),      # k7
        Propriedade("Ant", "crescente", 2, 5, "aditiva"),        # k9
        Propriedade("Ins", "decrescente", 4, 10, "aditiva"),     # k10
        Propriedade("Prot", "crescente", 500, 3000, "aditiva"),  # k11 acabamento (global)
        Propriedade("Tens", "crescente", 0, 0, "aditiva"),       # k12 tensão
        Propriedade("Quart", "crescente", 1, 5, "aditiva"),      # k13 quarteamento
        Propriedade("Qual", "crescente", 0, 5, "aditiva"),       # k14 verificação qualidade in-line (NIR)
    ]

    CVR = np.array([
        [6, 6, 5, 8, 8],  # Confiabilidade amostra
        [8, 5, 8, 5, 4],  # Velocidade
        [5, 1, 4, 4, 5],  # Automação
        [7, 2, 7, 1, 2],  # Segurança
        [3, 7, 2, 7, 6],  # Durabilidade
        [2, 3, 6, 3, 3],  # Rastreabilidade
        [4, 4, 3, 6, 7],  # Integração
        [1, 8, 1, 2, 1],  # Custo aquisição
    ], dtype=float)

    # QFD (I x 13) — ordem: Qtd,Vaz,Tmp,Aut,Tel,Alc,Vid,Ant,Ins,Prot,Tens,Quart,Qual
    # última coluna (Qual/k14) = proposta a validar (resposta do 1o autor):
    #   Confiab 9, Veloc 3, Autom 3, Seg 0, Durab 0, Rastr 9, Integr 3, Custo 3
    QFD = np.array([
        [9, 1, 1, 1, 0, 9, 0, 0, 0, 0, 0, 9, 9],  # Confiabilidade amostra
        [3, 9, 9, 3, 0, 1, 0, 3, 0, 0, 0, 0, 3],  # Velocidade
        [0, 3, 3, 9, 3, 0, 0, 3, 1, 0, 3, 0, 3],  # Automação
        [0, 3, 1, 9, 1, 1, 0, 9, 3, 0, 0, 0, 0],  # Segurança
        [0, 0, 0, 1, 1, 0, 9, 1, 1, 9, 0, 1, 0],  # Durabilidade
        [0, 0, 0, 1, 9, 0, 0, 0, 0, 0, 0, 0, 9],  # Rastreabilidade
        [0, 1, 1, 1, 1, 1, 1, 1, 9, 1, 9, 0, 3],  # Integração
        [1, 3, 3, 3, 1, 0, 3, 1, 3, 3, 1, 3, 3],  # Custo de aquisição
    ], dtype=float)
    # k11 (Prot / acabamento salt-spray) = NICHO portuário: o mercado geral não o
    # valoriza (ninguém pede marítimo fora de terminais portuários). Modelado com
    # utilidade ~0 → o marítimo é super-especificação p/ o mercado geral e some da
    # fronteira eficiente (fica como opção documentada de nicho). Índice da coluna Prot = 9.
    QFD[:, 9] = 0.0

    # Dimensões do produto. Módulos M1..M8 (funções), M9 = quadro (antigo M10),
    # M10 = NIR (novo), e "Acabamento" = propriedade global (padrão/marítima).
    modulos = ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10", "Acabamento"]
    variantes_modulo = {
        # M1 Coleta (extração) — NIR removido; + haste de sucção (arroz, 20 kg/ciclo @11 pts)
        "M1": [VarianteModulo("Haste fina (grãos)", {"Qtd": 18}, 1500),
               VarianteModulo("Haste grossa (grãos)", {"Qtd": 45}, 2000),
               VarianteModulo("Haste helicoide (açúcar)", {"Qtd": 30}, 18000),
               VarianteModulo("Haste de sucção (arroz)", {"Qtd": 20}, 1200)],
        "M2": [VarianteModulo("Fixo s/ desarme", {"Tmp": 50}, 9000),
               VarianteModulo("Fixo c/ desarme", {"Tmp": 50}, 10600),
               VarianteModulo("Telescópico c/ desarme", {"Tmp": 42}, 14500)],
        "M3": [VarianteModulo("Giro motorredutor", {"Tmp": 20}, 10000),
               VarianteModulo("Giro servomotor", {"Tmp": 20}, 16000)],
        "M4": [VarianteModulo("Cremalheira 1 pista", {"Tmp": 30, "Vaz": 22}, 27000),
               VarianteModulo("Cremalheira servo 1 pista", {"Tmp": 30, "Vaz": 22}, 43000),
               VarianteModulo("Cremalheira 2 pistas", {"Tmp": 30, "Vaz": 38}, 35000)],
        "M5": [VarianteModulo("Pneumático (grãos)", {"Tmp": 35}, 14000),
               VarianteModulo("Mecânico (açúcar)", {"Tmp": 55}, 9000)],
        "M6": [VarianteModulo("Manual", {"Aut": 2, "Tel": 2, "Ant": 2}, 6000),
               VarianteModulo("IA assistente", {"Aut": 4, "Tel": 3, "Ant": 4, "Tmp": -8}, 25000),
               VarianteModulo("IA + telemetria", {"Aut": 5, "Tel": 4, "Ant": 5, "Tmp": -8}, 38000)],
        "M7": [VarianteModulo("18 m", {"Alc": 18, "Vid": 55, "Ins": 6}, 35000),
               VarianteModulo("24 m", {"Alc": 24, "Vid": 55, "Ins": 9}, 48000)],
        "M8": [VarianteModulo("Manual", {"Quart": 1}, 1100),
               VarianteModulo("Quarteador", {"Quart": 4}, 12000),
               VarianteModulo("Quarteador + retorno", {"Quart": 5}, 16000)],
        # M9 Quadro elétrico (antigo M10)
        "M9": [VarianteModulo("Quadro 220 V", {"Tens": 0}, 8000),
               VarianteModulo("Quadro 380 V", {"Tens": 0}, 8000),
               VarianteModulo("Quadro 440 V", {"Tens": 0}, 8000)],
        # M10 Sensoriamento de qualidade (NIR) — novo módulo, entrega k14
        "M10": [VarianteModulo("Sem NIR", {}, 0),
                VarianteModulo("Com NIR", {"Qual": 5}, 170000)],
        # Acabamento — propriedade global do produto (k11), 2 opções
        "Acabamento": [VarianteModulo("Pintura padrão", {"Prot": 500}, 3000),
                       VarianteModulo("Pintura marítima", {"Prot": 3000}, 9000)],
    }

    config = {}  # âncoras retroativas dispensadas nesta reestruturação
    arq = Arquitetura(segmentos, necessidades, propriedades, CVR, QFD, modulos, variantes_modulo, config)
    limites = {"w_seg_min": np.array([0.25, 0.28, 0.08, 0.05, 0.00]),
               "w_seg_max": np.array([0.40, 0.54, 0.25, 0.15, 0.18]),
               "eps_max": 0.30, "delta_max": 0.15}
    return arq, limites


def coerente(cfg):
    """Regras de acoplamento (v3)."""
    m1 = cfg["M1"]; m5 = cfg["M5"]; m2 = cfg["M2"]; m6 = cfg["M6"]
    # (i) M1<->M5: sonda define transporte. Helicoide (açúcar) -> mecânico; demais (grão/sucção) -> pneumático
    if "helicoide" in m1.lower():
        if m5 != "Mecânico (açúcar)":
            return False
    else:
        if m5 != "Pneumático (grãos)":
            return False
    # (ii) M6<->M2 (regra A): IA exige braço fixo
    ia = m6 in ("IA assistente", "IA + telemetria")
    if ia and "Telescópico" in m2:
        return False
    # (iii) M3<->M4 servo é pacote
    m3 = cfg["M3"]; m4 = cfg["M4"]
    if ("servomotor" in m3.lower()) != ("servo" in m4.lower()):
        return False
    # (iv) NIR só com haste de grão (fina/grossa) — não helicoide, não sucção
    if cfg["M10"] == "Com NIR":
        if not ("grãos" in m1.lower() and "helicoide" not in m1.lower()):
            return False
    return True


if __name__ == "__main__":
    import itertools
    arq, lim = arquitetura_saur()
    print("Módulos/dim:", arq.modulos)
    cnt = {m: len(arq.variantes_modulo[m]) for m in arq.modulos}
    print("Variantes/dim:", cnt, "| RAW =", int(np.prod(list(cnt.values()))))
    opcoes = [[v.nome for v in arq.variantes_modulo[m]] for m in arq.modulos]
    nc = sum(1 for c in itertools.product(*opcoes) if coerente(dict(zip(arq.modulos, c))))
    print("BUILDABLE =", nc)
