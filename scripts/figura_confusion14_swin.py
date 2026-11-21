#!/usr/bin/env python3
"""Matriz de confusión de 14 clases de Swin-S en el test, normalizada por filas (porcentajes), capítulo 9.

Lee (solo lectura) OpenOOD/results_fase1/predicciones_swin_small_patch4_window7_224.npz.
Cada fila suma 100 %: la diagonal es la sensibilidad de cada clase.

Uso (desde la raíz del repositorio):
    python scripts/figura_confusion14_swin.py
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ORIGEN = '/mnt/homeGPU/slcerro/OpenOOD/results_fase1/predicciones_swin_small_patch4_window7_224.npz'
SALIDA = 'img/cap09/fig_confusion_swin_porcentajes.pdf'

d = np.load(ORIGEN)
y, p = d['label'], d['pred']
k = d['probs'].shape[1]
# nombre de cada clase = carpeta de la imagen en el test
nombres = [os.path.basename(os.path.dirname(d['paths'][y == i][0])).replace('_', ' ') for i in range(k)]
C = np.zeros((k, k), int)
np.add.at(C, (y, p), 1)
assert C.sum() == 12618 and C[0, 0] == 2092 and C[7, 7] == 13, C  # mismos recuentos que Confusion_Matrix_TEST
filas = 100 * C / C.sum(1, keepdims=True)

fig, ax = plt.subplots(figsize=(11, 10))
ax.imshow(filas, cmap='Blues', vmin=0, vmax=100)
for i in range(k):
    for j in range(k):
        if C[i, j]:
            txt = f'{filas[i, j]:.1f}'.replace('.', ',') if filas[i, j] >= 0.1 else '<0,1'
            ax.text(j, i, txt,ha='center', va='center', fontsize=9,
                    color='white' if filas[i, j] > 60 else 'black')
ax.set_xticks(range(k), nombres, rotation=90, fontsize=10)
ax.set_yticks(range(k), nombres, fontsize=10)
ax.set_xlabel('Clase predicha', fontsize=11)
ax.set_ylabel('Clase verdadera', fontsize=11)
fig.tight_layout()
fig.savefig(SALIDA, bbox_inches='tight')
print(SALIDA)
