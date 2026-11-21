#!/usr/bin/env python3
"""Test de Friedman (con la corrección de Iman-Davenport), post hoc de Nemenyi y diagrama de diferencia
crítica (CD) de Demšar (2006, secs. 3.2.2 y 3.2.4) sobre el AUROC de los detectores OOD del Swin-S.

Bloques: los ocho conjuntos OOD de results_ood/faseC_K144 salvo TUM+NORM (es la unión de TUM y NORM).
Métodos: KNN, MDS, RMDS, ViM, SHE (euclídea), STOOD-X (100 %, K = 500) y STOOD-X (100 %, K = 144).
Rango 1 = mayor AUROC; empates con rango medio. Se usa el AUROC sin redondear.

Uso (desde la raíz del repositorio; necesita numpy, scipy y matplotlib):
    python scripts/figura_cd_nemenyi.py
"""
import csv
import numpy as np
from scipy.stats import rankdata, chi2, f, studentized_range
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

TABLA = '/mnt/homeGPU/slcerro/OpenOOD/results_ood/faseC_K144/tabla_principal.csv'
SALIDA = 'img/cap10/cd_nemenyi_auroc.pdf'
ALFA = 0.05
METODOS = {'knn': 'KNN', 'mds': 'MDS', 'rmds': 'RMDS', 'vim': 'ViM', 'she_euclidean': 'SHE (euclídea)',
           'stoodx_100': 'STOOD-X ($K=500$)', 'stoodx_100_k144': 'STOOD-X ($K=144$)'}
CONJUNTOS = ['near_nct_tum', 'near_nct_norm', 'afin_nct_str', 'afin_nct_lym', 'afin_nct_mus',
             'cov_panda', 'control_res_128', 'far_dtd']

auroc = {(r['metodo'], r['conjunto']): float(r['AUROC']) for r in csv.DictReader(open(TABLA))}
met = list(METODOS)
A = np.array([[auroc[(m, c)] for m in met] for c in CONJUNTOS])   # N x k
N, k = A.shape
R = np.vstack([rankdata(-fila) for fila in A])                    # rango 1 = mejor
Rm = R.mean(0)

chi2_F = 12 * N / (k * (k + 1)) * (np.sum(Rm ** 2) - k * (k + 1) ** 2 / 4)
F_F = (N - 1) * chi2_F / (N * (k - 1) - chi2_F)
p_chi2 = chi2.sf(chi2_F, k - 1)
p_F = f.sf(F_F, k - 1, (k - 1) * (N - 1))
q = studentized_range.ppf(1 - ALFA, k, np.inf) / np.sqrt(2)
CD = q * np.sqrt(k * (k + 1) / (6 * N))
assert abs(q - 2.949) < 1e-3 or k != 7   # tabla 5(a) de Demšar para k = 7

orden = np.argsort(Rm)
print(f'N = {N}, k = {k}')
print('AUROC por conjunto (filas) y método (columnas):', [METODOS[m] for m in met])
for c, fila, r in zip(CONJUNTOS, A, R):
    print(f'  {c:16s}', ' '.join(f'{a:.4f}({x:.1f})' for a, x in zip(fila, r)))
print('Rangos medios:', ', '.join(f'{METODOS[met[i]]} {Rm[i]:.3f}' for i in orden))
print(f'chi2_F = {chi2_F:.4f} (p = {p_chi2:.3g});  F_F = {F_F:.4f} con ({k-1}, {(k-1)*(N-1)}) gl (p = {p_F:.3g})')
print(f'q_{ALFA} = {q:.4f};  CD = {CD:.4f}')
print('Pares con diferencia de rangos >= CD:')
for a in range(k):
    for b in range(a + 1, k):
        if abs(Rm[a] - Rm[b]) >= CD:
            print(f'  {METODOS[met[a]]} ({Rm[a]:.3f}) - {METODOS[met[b]]} ({Rm[b]:.3f}) = {Rm[a]-Rm[b]:+.3f}')

# Grupos no significativamente distintos: tramos maximales de métodos consecutivos (por rango) con
# diferencia entre extremos < CD (Demšar, fig. 1a).
rs = Rm[orden]
grupos = []
for i in range(k):
    j = max(j for j in range(i, k) if rs[j] - rs[i] < CD)
    if j > i and not any(a <= i and j <= b for a, b in grupos):
        grupos.append((i, j))

# Diagrama CD: eje de rangos invertido (el mejor a la derecha)
fig, ax = plt.subplots(figsize=(6.3, 2.6))
x = lambda r: k + 1 - r
ax.set_xlim(0.3, k + 0.7)
ax.set_ylim(-0.1 * k - 0.2 - 0.15 * len(grupos), 1.0)
ax.axis('off')
ax.hlines(0, x(k), x(1), color='k', lw=1)
for t in range(1, k + 1):
    ax.vlines(x(t), 0, 0.08, color='k', lw=1)
    ax.text(x(t), 0.13, str(t), ha='center', va='bottom', fontsize=9)
for t in np.arange(1.5, k, 1):
    ax.vlines(x(t), 0, 0.04, color='k', lw=0.7)
ax.hlines(0.6, x(k), x(k) + CD, color='k', lw=1)
ax.vlines([x(k), x(k) + CD], 0.55, 0.65, color='k', lw=1)
ax.text(x(k) + CD / 2, 0.68, f'CD = {CD:.2f}'.replace('.', ','), ha='center', va='bottom', fontsize=9)
mitad = (k + 1) // 2
for pos, i in enumerate(orden):
    xi = x(Rm[i])
    if pos < mitad:   # mejores, a la derecha
        y = -0.25 - 0.22 * pos
        ax.plot([xi, xi, x(1) + 0.15], [0, y, y], color='k', lw=0.8)
        ax.text(x(1) + 0.2, y, f'{METODOS[met[i]]} ({Rm[i]:.3f})'.replace('.', ','), va='center', fontsize=8.5)
    else:
        y = -0.25 - 0.22 * (k - 1 - pos)
        ax.plot([xi, xi, x(k) - 0.15], [0, y, y], color='k', lw=0.8)
        ax.text(x(k) - 0.2, y, f'({Rm[i]:.3f}) {METODOS[met[i]]}'.replace('.', ','), va='center', ha='right',
                fontsize=8.5)
for g, (a, b) in enumerate(grupos):
    y = -0.08 - 0.07 * g
    ax.hlines(y, x(rs[a]) + 0.04, x(rs[b]) - 0.04, color='k', lw=3)
fig.savefig(SALIDA, bbox_inches='tight')
print('Guardada', SALIDA, '; grupos:', [[METODOS[met[orden[t]]] for t in range(a, b + 1)] for a, b in grupos])
