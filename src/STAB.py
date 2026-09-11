# ===============================================================
# AVALIAÇÃO DE ESTABILIDADE PARA A DEFINIÇÃO DA QTD. DE CENÁRIOS
# ===============================================================

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# ===============================================================
# CONSTRUÇÃO DO DATASET
# ===============================================================

N = [25, 50, 100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600, 51200]

delta_max = [None, 4.0, 1.0, 4.0, 4.2, 2.7, 0.9, 1.1, 1.5, 0.6, 0.8, 0.2]

delta_max = [np.nan if v is None else v for v in delta_max]

# ===============================================================
# CRIAÇÃO DO GRÁFICO
# ===============================================================

# --- Criação do gráfico ---
plt.figure(figsize=(10,6))

# Linha e pontos
plt.plot(N, delta_max, marker='o', linestyle='-', color='blue', label='Δmax')

# Linha horizontal
plt.axhline(y=1.0, color='red', linestyle='--', label='Stability threshold (ε = 1%)')

# Eixo X logarítmico
plt.xscale('log', base=2)

# Definir ticks do eixo X exatamente nos valores de N
plt.xticks(N)

# Separador de milhar no eixo X
plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))

# Porcentagem no eixo Y
plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f'{y:.1f}%'))

# Rótulos e título
plt.xlabel('Scenario sample size (N)')
plt.ylabel('Maximum deviation across all policies and criteria (Δmax)')
plt.grid(True, which="both", ls="--", linewidth=0.5)
plt.legend()

plt.tight_layout()
plt.show()

print("Gauss")
