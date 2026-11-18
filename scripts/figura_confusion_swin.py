#!/usr/bin/env python3
"""Matriz de confusión de 5 categorías (opción a) solo de Swin-S, para la figura del capítulo 9.

Lee (solo lectura) OpenOOD/results_agrupaciones/confusion_5clases_a.npz y reproduce el estilo de
fig_confusion de OpenOOD/agrupaciones.py con un único panel y letra más grande.

Uso (desde la raíz del repositorio; necesita matplotlib, p. ej. el entorno fastai_env_ood):
    python scripts/figura_confusion_swin.py
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ORIGEN = '/mnt/homeGPU/slcerro/OpenOOD/results_agrupaciones/confusion_5clases_a.npz'
SALIDA = 'img/cap09/fig_confusion_5clases_swin.pdf'

d = np.load(ORIGEN, allow_pickle=True)
etiquetas = list(d['etiquetas'])
C = d['swin_small_patch4_window7_224']
filas = C / C.sum(1, keepdims=True)
assert C.sum() == 12618, C.sum()

fig, ax = plt.subplots(figsize=(5.2, 4.8))
ax.imshow(filas, cmap='Blues', vmin=0, vmax=1)
for i in range(len(etiquetas)):
    for j in range(len(etiquetas)):
        ax.text(j, i, f'{C[i, j]}\n{100 * filas[i, j]:.1f} %'.replace('.', ','), ha='center', va='center',
                fontsize=10, color='white' if filas[i, j] > 0.6 else 'black')
ax.set_xticks(range(len(etiquetas)), etiquetas, fontsize=11)
ax.set_yticks(range(len(etiquetas)), etiquetas, fontsize=11)
ax.set_xlabel('Clase predicha', fontsize=11)
ax.set_ylabel('Clase verdadera', fontsize=11)
ax.set_title(f'Swin-S: exactitud {100 * np.trace(C) / C.sum():.2f} %'.replace('.', ','), fontsize=12)
fig.tight_layout()
fig.savefig(SALIDA, bbox_inches='tight')
print(SALIDA)
