#!/usr/bin/env python3
"""Q-Q plot de las distancias de Mahalanobis (test ID) frente a la chi-cuadrado con D grados de libertad.

Si h(x) | y = c ~ N(mu_c, Sigma) (hipótesis de MDS), d^2 = (h - mu_c)^T Sigma^{-1} (h - mu_c) ~ chi^2_D.
mu_c y Sigma se estiman con id_train como en MDS (covarianza común); d^2 se calcula sobre id_test con su
clase verdadera. Lee (solo lectura) las características del Swin-S de OpenOOD/features/completo/.

Uso (desde la raíz del repositorio; necesita numpy, scipy, scikit-learn y matplotlib):
    python scripts/figura_qq_mahalanobis.py
"""
import json
import numpy as np
import sklearn.covariance
from scipy.stats import chi2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

FEATURES = '/mnt/homeGPU/slcerro/OpenOOD/features/completo'
MDS_REF = '/mnt/homeGPU/slcerro/OpenOOD/results_ood/faseA_2026-10-20_11-19-35/scores_mds.npz'
SALIDA = 'img/cap10/qq_mahalanobis_chi2.pdf'

clases = json.load(open(f'{FEATURES}/info.json'))['clases_id']
tr, te = np.load(f'{FEATURES}/id_train.npz'), np.load(f'{FEATURES}/id_test.npz')
Ftr, ytr = tr['feats'].astype(np.float64), tr['label']
Fte, yte = te['feats'].astype(np.float64), te['label']
K, D = len(clases), Ftr.shape[1]

# Mismo ajuste que el postprocesador MDS de OpenOOD (laminas.py: ajustar_mds)
medias = np.stack([Ftr[ytr == c].mean(0) for c in range(K)])
cov = sklearn.covariance.EmpiricalCovariance(assume_centered=False).fit(Ftr - medias[ytr])
P = cov.precision_
d2 = np.stack([np.einsum('ij,jk,ik->i', Fte - medias[c], P, Fte - medias[c]) for c in range(K)], 1)

# Comprobación: -min_c d^2 reproduce la puntuación MDS de la fase A
ref = np.load(MDS_REF)['id_test_conf']
assert np.max(np.abs(-d2.min(1) - ref)) / np.max(np.abs(ref)) < 1e-3

d2_propia = d2[np.arange(len(yte)), yte]
colores = plt.cm.tab20(np.linspace(0, 1, 20))[:K]
fig, ax = plt.subplots(figsize=(7.5, 5.5))
for c in range(K):
    x = np.sort(d2_propia[yte == c])
    n = len(x)
    ax.plot(chi2.ppf((np.arange(1, n + 1) - 0.5) / n, D), x, '.', ms=2.5, color=colores[c],
            label=f'{clases[c].replace("_", " ")} ($n={n}$)')
lim = [chi2.ppf(0.5 / 1000, D), chi2.ppf(1 - 0.5 / 1000, D)]
ax.plot(lim, lim, 'k--', lw=1, label='$y = x$')
ax.set_xlabel(rf'Cuantiles teóricos de $\chi^2_{{{D}}}$')
ax.set_ylabel(r'Cuantiles empíricos de $d^2_{\mathrm{M}}$ (test ID)')
ax.set_yscale('log')
ax.legend(fontsize=7, markerscale=3, loc='center left', bbox_to_anchor=(1.01, 0.5))
fig.tight_layout()
fig.savefig(SALIDA, bbox_inches='tight')
fig.savefig(SALIDA.replace('.pdf', '.png'), dpi=150, bbox_inches='tight')

for c in range(K):
    x = d2_propia[yte == c]
    print(f'{clases[c]:32s} n={len(x):5d} mediana d2={np.median(x):9.1f}  (chi2_{D}: {chi2.median(D):.1f})')
