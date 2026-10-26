#!/usr/bin/env python3
"""Genera las tablas LaTeX de la memoria a partir de los resultados congelados.

Lee (solo lectura) los CSV/JSON de /mnt/homeGPU/slcerro/OpenOOD/results_* y escribe un
fichero .tex por tabla en tablas/. Solo usa la biblioteca estándar.

Uso (desde la raíz del repositorio):
    python3 scripts/generar_tablas.py [--resultados /ruta/a/OpenOOD] [--salida tablas]

Las tablas generadas no se editan a mano: si cambian los resultados o el formato, se
modifica este script y se vuelve a ejecutar.
"""
import argparse
import csv
import json
import os
from collections import OrderedDict

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
RAIZ_RESULTADOS = '/mnt/homeGPU/slcerro/OpenOOD'
FASE_C = 'results_ood/faseC_2026-10-20'
FASE_A = 'results_ood/faseA_2026-10-20_11-19-35'
FASE_B = 'results_ood/faseB_paper_2026-10-20'
STOODX_VAL = 'results_ood/stoodx_validacion'

# ---------------------------------------------------------------------------
# Nombres para la memoria
# ---------------------------------------------------------------------------
METODOS = OrderedDict([
    ('msp', 'MSP'), ('mls', 'MaxLogit'), ('ebo', 'Energy'),
    ('react', 'ReAct'), ('ash', 'ASH$^{a}$'), ('dice', 'DICE'),
    ('knn', 'KNN'), ('mds', 'MDS'), ('rmds', 'RMDS'), ('vim', 'ViM'),
    ('she', 'SHE (prod.\\ escalar)'), ('she_cosine', 'SHE (coseno)'), ('she_euclidean', 'SHE (euclídea)'),
    ('stoodx_100', 'STOOD-X (100\\,\\%)'), ('stoodx_875', 'STOOD-X (87,5\\,\\%)'),
    ('stoodx_100_kc', 'STOOD-X $K_c$$^{\\dagger}$'),
])
FAMILIAS = [
    ('Basados en logits', ['msp', 'mls', 'ebo']),
    ('Modificación de activaciones', ['react', 'ash', 'dice']),
    ('Características y distancias', ['knn', 'mds', 'rmds', 'vim', 'she', 'she_cosine', 'she_euclidean']),
    ('STOOD-X', ['stoodx_100', 'stoodx_875', 'stoodx_100_kc']),
]
CONJUNTOS = OrderedDict([
    ('near_nct_tum_norm', 'TUM+NORM'), ('near_nct_tum', 'TUM'), ('near_nct_norm', 'NORM'),
    ('afin_nct_str', 'STR'), ('afin_nct_lym', 'LYM'), ('afin_nct_mus', 'MUS'),
    ('cov_panda', 'PANDA'), ('control_res_128', 'Control 128\\,px'), ('far_dtd', 'DTD'),
])
ANEXO = OrderedDict([('anexo_nct_adi', 'ADI'), ('anexo_nct_back', 'BACK'),
                     ('anexo_nct_deb', 'DEB'), ('anexo_nct_muc', 'MUC')])
MODELOS = OrderedDict([
    ('swin_small_patch4_window7_224', 'Swin-S'), ('convnext_small', 'ConvNeXt-S'),
    ('tf_efficientnetv2_s', 'EfficientNetV2-S'), ('vit_base_patch16_224', 'ViT-B/16'),
    ('resnet50', 'ResNet-50'),
])
EXPLORATORIOS = {'stoodx_100_kc'}

NOTA_BOOT = ('IC del 95\\,\\% por \\emph{bootstrap} (1.000 remuestreos estratificados, semilla 0). '
             'Clase positiva: OOD.')
NOTA_MARCAS = ('$^{a}$ASH reduce la exactitud ID al {acc_ash}\\,\\%. '
               '$^{\\dagger}$Variante exploratoria ($K_c=\\min(500,\\lfloor n_c/2\\rfloor)$), propuesta tras ver '
               'datos OOD; no es el método principal.')

# Artículo del dataset (Ayensa-Jiménez et al.), XCiT-Medium: figuras 2 (5 categorías) y 3 (binario).
# Mismos valores que usa OpenOOD/agrupaciones.py.
ARTICULO = {'acc_5': 0.9834, 'acc_bin': 0.9925, 'tpr': 0.984, 'tnr': 0.997,
            'G3': 0.814, 'G4': 0.967, 'G5': 0.978}


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def leer_csv(ruta):
    with open(ruta, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def leer_json(ruta):
    with open(ruta, encoding='utf-8') as f:
        return json.load(f)


def n(x, d=3):
    """Número con coma decimal para LaTeX (0{,}968)."""
    if x is None or x == '':
        return '--'
    return ('{:.%df}' % d).format(float(x)).replace('.', '{,}')


def pct(x, d=1):
    return n(100 * float(x), d)


def entero(x):
    return '\\num{%d}' % int(float(x))


def ic(a, b, d=3):
    return '[%s; %s]' % (n(a, d), n(b, d))


def negrita(s, cond):
    return '\\textbf{%s}' % s if cond else s


def clase(c):
    return '\\clase{%s}' % c.replace('_', '\\_')


def escribir(salida, nombre, lineas, origen):
    ruta = os.path.join(salida, nombre)
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write('%% Generado por scripts/generar_tablas.py a partir de %s. No editar a mano.\n' % origen)
        f.write('\n'.join(lineas) + '\n')
    print('  ' + ruta)


def tabla(caption, label, columnas, cuerpo, tamano='\\small', sep=None, entorno='tabular', ancho=None):
    l = ['\\begin{table}[htbp]', '\\centering', tamano]
    if sep:
        l.append('\\setlength{\\tabcolsep}{%s}' % sep)
    l += ['\\caption{%s}' % caption, '\\label{%s}' % label]
    if entorno == 'tabularx':
        l.append('\\begin{tabularx}{%s}{%s}' % (ancho or '\\textwidth', columnas))
    else:
        l.append('\\begin{%s}{%s}' % (entorno, columnas))
    l += cuerpo
    l += ['\\end{%s}' % entorno, '\\end{table}']
    return l


def por_metodo_conjunto(filas):
    return {(f['metodo'], f['conjunto']): f for f in filas}


def mejores(datos, metodos, conjunto, columna, mayor):
    vals = [float(datos[(m, conjunto)][columna]) for m in metodos
            if m not in EXPLORATORIOS and (m, conjunto) in datos]
    return max(vals) if mayor else min(vals)


def filas_familias(metodos_validos, fila_de, ncol):
    cuerpo = []
    primera = True
    for nombre, lista in FAMILIAS:
        lista = [m for m in lista if m in metodos_validos]
        if not lista:
            continue
        if not primera:
            cuerpo.append('\\midrule')
        primera = False
        cuerpo.append('\\multicolumn{%d}{@{}l}{\\textit{%s}} \\\\' % (ncol, nombre))
        for m in lista:
            cuerpo.append(fila_de(m))
    return cuerpo


# ---------------------------------------------------------------------------
# Capítulo 8: partición del conjunto ID
# ---------------------------------------------------------------------------
def t08_particion(R, S):
    filas = leer_csv(os.path.join(R, 'results_integridad/inventario_por_clase.csv'))
    cuerpo = ['\\toprule',
              '& \\multicolumn{2}{c}{Original} & \\multicolumn{3}{c}{Partición del TFG} \\\\',
              '\\cmidrule(lr){2-3}\\cmidrule(lr){4-6}',
              'Clase & Train & Val & Train & Validación & Test \\\\', '\\midrule']
    for f in filas:
        nombre = '\\textbf{Total}' if f['clase'] == 'TOTAL' else clase(f['clase'])
        if f['clase'] == 'TOTAL':
            cuerpo.append('\\midrule')
        cuerpo.append('%s & %s & %s & %s & %s & %s \\\\' % (
            nombre, entero(f['orig_train']), entero(f['orig_val']), entero(f['train']),
            entero(f['val']), entero(f['test'])))
    cuerpo.append('\\bottomrule')
    cap = ('Número de imágenes por clase en la partición original del conjunto ID (carpetas \\texttt{train} y '
           '\\texttt{val}) y en la partición usada en este trabajo (el \\texttt{train} original dividido 80/20 por '
           'clase en entrenamiento y validación; el \\texttt{val} original como test).')
    escribir(S, 't08_particion.tex',
             tabla(cap, 'tab:particion', 'lrrrrr', cuerpo, '\\small'),
             'results_integridad/inventario_por_clase.csv')


# ---------------------------------------------------------------------------
# Capítulo 9: clasificación ID
# ---------------------------------------------------------------------------
def t09_modelos(R, S):
    filas = {f['modelo']: f for f in leer_csv(os.path.join(R, 'results_fase1/metricas_modelos.csv'))}
    cuerpo = ['\\toprule',
              'Modelo & Exactitud & IC 95\\,\\% (imagen) & IC 95\\,\\% (lámina) & F1 macro & IC 95\\,\\% (imagen) '
              '& IC 95\\,\\% (lámina) & \\emph{Balanced acc.} \\\\', '\\midrule']
    for m, nombre in MODELOS.items():
        f = filas[m]
        cuerpo.append('%s & %s & %s & %s & %s & %s & %s & %s \\\\' % (
            nombre, n(f['exactitud'], 4), ic(f['exactitud_IC_inf'], f['exactitud_IC_sup'], 4),
            ic(f['exactitud_IC_lamina_inf'], f['exactitud_IC_lamina_sup'], 4),
            n(f['f1_macro'], 4), ic(f['f1_macro_IC_inf'], f['f1_macro_IC_sup'], 4),
            ic(f['f1_macro_IC_lamina_inf'], f['f1_macro_IC_lamina_sup'], 4), n(f['balanced_accuracy'], 4)))
    cuerpo.append('\\bottomrule')
    cap = ('Clasificación de las 14 clases en el test ID (12.618 imágenes) con los cinco modelos: exactitud, F1 '
           'macro y \\emph{balanced accuracy} (más alto es mejor). IC del 95\\,\\% por \\emph{bootstrap} '
           '(1.000 remuestreos, semilla 0) sobre imágenes y sobre láminas (remuestreo de las 95 láminas). '
           'ConvNeXt-S se evalúa a 256\\,px y el resto a 224\\,px, cada uno con el preprocesado de su entrenamiento.')
    escribir(S, 't09_modelos.tex',
             tabla(cap, 'tab:modelos', 'lccccccc', cuerpo, '\\scriptsize', '3pt'),
             'results_fase1/metricas_modelos.csv')


def t09_recall_clase(R, S):
    filas = leer_csv(os.path.join(R, 'results_fase1/recall_por_clase.csv'))
    rec = {(f['modelo'], f['clase']): f for f in filas}
    clases = sorted({f['clase'] for f in filas}, key=lambda c: -int(rec[(list(MODELOS)[0], c)]['n']))
    cuerpo = ['\\toprule', 'Clase & $n$ & ' + ' & '.join(MODELOS.values()) + ' \\\\', '\\midrule']
    for c in clases:
        vals = [float(rec[(m, c)]['recall']) for m in MODELOS]
        mx = max(vals)
        celdas = [negrita(n(v, 2), v == mx) for v in vals]
        cuerpo.append('%s & %s & %s \\\\' % (clase(c), entero(rec[(list(MODELOS)[0], c)]['n']), ' & '.join(celdas)))
    cuerpo.append('\\bottomrule')
    cap = ('Sensibilidad (\\emph{recall}) por clase en el test ID de los cinco modelos (más alto es mejor); '
           '$n$: imágenes de test de la clase. En negrita, el mejor valor de cada clase.')
    escribir(S, 't09_recall_clase.tex',
             tabla(cap, 'tab:recall-clase', 'lrccccc', cuerpo, '\\scriptsize', '4pt'),
             'results_fase1/recall_por_clase.csv')


def t09_mcnemar(R, S):
    d = leer_json(os.path.join(R, 'results_fase1/swin_vs_convnext.json'))
    m = d['mcnemar']
    b = d['bootstrap_pareado']
    cuerpo = ['\\toprule', '& ConvNeXt-S acierta & ConvNeXt-S falla \\\\', '\\midrule',
              'Swin-S acierta & %s & %s \\\\' % (entero(m['ambos_aciertan']), entero(m['solo_swin_acierta'])),
              'Swin-S falla & %s & %s \\\\' % (entero(m['solo_convnext_acierta']), entero(m['ambos_fallan'])),
              '\\bottomrule']
    cap = ('Tabla de contingencia de aciertos de Swin-S y ConvNeXt-S sobre las mismas 12.618 imágenes de test. '
           'Test de McNemar: $p$ exacto (binomial) $= %s$; $\\chi^2$ con corrección de continuidad $= %s$ '
           '($p = %s$). \\emph{Bootstrap} pareado de la diferencia de exactitud Swin-S $-$ ConvNeXt-S: '
           '$%s$ %s ($p = %s$; por lámina %s, $p = %s$); de F1 macro: $%s$ %s ($p = %s$).') % (
        n(m['p_exacto_binomial'], 3), n(m['chi2_continuidad'], 2), n(m['p_chi2'], 3),
        ('+' if b['exactitud_imagen']['diferencia'] >= 0 else '') + n(b['exactitud_imagen']['diferencia'], 4),
        ic(b['exactitud_imagen']['IC_inf'], b['exactitud_imagen']['IC_sup'], 4), n(b['exactitud_imagen']['p_bootstrap'], 2),
        ic(b['exactitud_lamina']['IC_inf'], b['exactitud_lamina']['IC_sup'], 4), n(b['exactitud_lamina']['p_bootstrap'], 2),
        n(b['f1_macro_imagen']['diferencia'], 4),
        ic(b['f1_macro_imagen']['IC_inf'], b['f1_macro_imagen']['IC_sup'], 4), n(b['f1_macro_imagen']['p_bootstrap'], 2))
    escribir(S, 't09_mcnemar.tex',
             tabla(cap, 'tab:mcnemar', 'lcc', cuerpo, '\\small'),
             'results_fase1/swin_vs_convnext.json')


def t09_agrupaciones(R, S):
    m5 = {f['modelo']: f for f in leer_csv(os.path.join(R, 'results_agrupaciones/metricas_5clases.csv'))
          if f['variante'] == 'a'}
    mb = {f['modelo']: f for f in leer_csv(os.path.join(R, 'results_agrupaciones/metricas_binario.csv'))
          if f['variante'] == 'pin_maligno'}
    cuerpo = ['\\toprule', '& \\multicolumn{2}{c}{5 categorías} & \\multicolumn{4}{c}{Binario} \\\\',
              '\\cmidrule(lr){2-3}\\cmidrule(lr){4-7}',
              'Modelo & Exactitud (\\%) & BA & Exactitud (\\%) & Sens. & Esp. & BA \\\\', '\\midrule']
    for m, nombre in MODELOS.items():
        a, b = m5[m], mb[m]
        cuerpo.append('%s & %s & %s & %s & %s & %s & %s \\\\' % (
            nombre, pct(a['exactitud'], 2), n(a['balanced_accuracy']), pct(b['exactitud'], 2),
            n(b['sensibilidad_TPR']), n(b['especificidad_TNR']), n(b['balanced_accuracy'])))
    A = ARTICULO
    cuerpo += ['\\midrule', 'XCiT-M (artículo) & %s & -- & %s & %s & %s & %s \\\\' % (
        pct(A['acc_5'], 2), pct(A['acc_bin'], 2), n(A['tpr']), n(A['tnr']), n((A['tpr'] + A['tnr']) / 2)),
        '\\bottomrule']
    cap = ('Clasificación agrupada en el test ID a partir de las predicciones de 14 clases (más alto es mejor). '
           'Cinco categorías: NM (\\clase{No\\_Cancer}, estroma, glándulas no neoplásicas, inflamatorio), G3, G4, '
           'G5 y NT (PIN de alto grado, carcinoma intraductal, adenocarcinoma ductal). Binario: maligno = '
           'G3 + G4 + G5 + NT. Sens.: sensibilidad; Esp.: especificidad; BA: \\emph{balanced accuracy}. '
           'Referencia: XCiT-Medium del artículo del conjunto de datos~\\cite{ayensa2025}, con otro reparto de '
           'NM y NT (su BA se calcula como la media de Sens. y Esp.).')
    escribir(S, 't09_agrupaciones.tex',
             tabla(cap, 'tab:agrupaciones', 'lcccccc', cuerpo, '\\footnotesize', '4pt'),
             'results_agrupaciones/metricas_5clases.csv y metricas_binario.csv')


def t09_sensibilidad_gleason(R, S):
    filas = {f['modelo']: f for f in leer_csv(os.path.join(R, 'results_agrupaciones/sensibilidad_G3_G4_G5.csv'))
             if f['variante'] == 'a'}
    f0 = filas[list(MODELOS)[0]]
    cuerpo = ['\\toprule', 'Modelo & G3 ($n=%s$) & G4 ($n=%s$) & G5 ($n=%s$) \\\\' % (
        entero(f0['n_G3']), entero(f0['n_G4']), entero(f0['n_G5'])), '\\midrule']
    for m, nombre in MODELOS.items():
        f = filas[m]
        cuerpo.append('%s & %s & %s & %s \\\\' % (nombre, n(f['sensibilidad_G3']), n(f['sensibilidad_G4']),
                                                  n(f['sensibilidad_G5'])))
    A = ARTICULO
    cuerpo += ['\\midrule', 'XCiT-M (artículo) & %s & %s & %s \\\\' % (n(A['G3']), n(A['G4']), n(A['G5'])),
               '\\bottomrule']
    cap = ('Sensibilidad de las categorías G3, G4 y G5 en el test ID (más alto es mejor). Son las categorías '
           'directamente comparables con el artículo del conjunto de datos~\\cite{ayensa2025}, porque coinciden '
           'en número de imágenes.')
    escribir(S, 't09_sensibilidad_gleason.tex',
             tabla(cap, 'tab:sensibilidad-gleason', 'lccc', cuerpo, '\\small'),
             'results_agrupaciones/sensibilidad_G3_G4_G5.csv')


# ---------------------------------------------------------------------------
# Capítulo 10: detección OOD
# ---------------------------------------------------------------------------
def acc_ash(datos):
    return pct(datos[('ash', 'near_nct_tum_norm')]['ACC_ID'], 1)


def t10_bloque(R, S, datos, conjunto, nombre_fich, label, titulo):
    metodos = [m for m in METODOS if (m, conjunto) in datos]
    best = {
        'AUROC': mejores(datos, metodos, conjunto, 'AUROC', True),
        'FPR@95': mejores(datos, metodos, conjunto, 'FPR@95', False),
        'CCR@FPR5': mejores(datos, metodos, conjunto, 'CCR@FPR5', True),
    }

    def fila(m):
        f = datos[(m, conjunto)]
        ex = m in EXPLORATORIOS
        a, fp, cc = float(f['AUROC']), float(f['FPR@95']), float(f['CCR@FPR5'])
        return '%s & %s %s & %s %s & %s \\\\' % (
            METODOS[m],
            negrita(n(a), not ex and round(a, 3) == round(best['AUROC'], 3)), ic(f['AUROC_IC_inf'], f['AUROC_IC_sup']),
            negrita(n(fp), not ex and round(fp, 3) == round(best['FPR@95'], 3)), ic(f['FPR@95_IC_inf'], f['FPR@95_IC_sup']),
            negrita(n(cc), not ex and round(cc, 3) == round(best['CCR@FPR5'], 3)))

    cuerpo = ['\\toprule',
              'Método & \\AUROC $\\uparrow$ [IC 95\\,\\%] & \\FPRn{95} $\\downarrow$ [IC 95\\,\\%] & '
              '\\CCRn{5} $\\uparrow$ \\\\', '\\midrule']
    cuerpo += filas_familias(set(metodos), fila, 4)
    cuerpo.append('\\bottomrule')
    cap = ('%s: \\AUROC y \\CCRn{5} (más alto es mejor) y \\FPRn{95} (más bajo es mejor) de los 16 métodos. %s '
           'En negrita, el mejor valor entre los métodos no exploratorios. %s') % (
        titulo, NOTA_BOOT, NOTA_MARCAS.replace('{acc_ash}', acc_ash(datos)))
    escribir(S, nombre_fich, tabla(cap, label, 'lccc', cuerpo, '\\footnotesize', '4pt'),
             FASE_C + '/tabla_principal.csv')


def t10_control_interno(R, S, datos):
    conjuntos = ['near_nct_tum', 'near_nct_norm', 'afin_nct_str', 'afin_nct_lym', 'afin_nct_mus']
    metodos = [m for m in METODOS]
    cab = ' & '.join(CONJUNTOS[c] for c in conjuntos)

    def fila(m):
        a = [n(datos[(m, c)]['AUROC']) for c in conjuntos]
        fp = [n(datos[(m, c)]['FPR@95']) for c in conjuntos]
        return '%s & %s & %s \\\\' % (METODOS[m], ' & '.join(a), ' & '.join(fp))

    cuerpo = ['\\toprule',
              '& \\multicolumn{5}{c}{\\AUROC $\\uparrow$} & \\multicolumn{5}{c}{\\FPRn{95} $\\downarrow$} \\\\',
              '\\cmidrule(lr){2-6}\\cmidrule(lr){7-11}', 'Método & %s & %s \\\\' % (cab, cab), '\\midrule']
    cuerpo += filas_familias(set(metodos), fila, 11)
    cuerpo.append('\\bottomrule')
    cap = ('Control interno con las clases de \\nctcrc: tejido glandular de colon (TUM y NORM) frente a tejidos '
           'análogos a clases ID (STR, LYM y MUS). \\AUROC (más alto es mejor) y \\FPRn{95} (más bajo es mejor). '
           'Clase positiva: OOD. %s') % NOTA_MARCAS.replace('{acc_ash}', acc_ash(datos))
    escribir(S, 't10_control_interno.tex', tabla(cap, 'tab:ood-control-interno', 'l' + 'c' * 10, cuerpo,
                                                 '\\scriptsize', '2.5pt'),
             FASE_C + '/tabla_principal.csv')


def t10_panda_control(R, S, datos):
    metodos = [m for m in METODOS]

    def fila(m):
        p, c = datos[(m, 'cov_panda')], datos[(m, 'control_res_128')]
        dif = float(p['AUROC']) - float(c['AUROC'])
        return '%s & %s %s & %s %s & %s%s & %s & %s \\\\' % (
            METODOS[m], n(p['AUROC']), ic(p['AUROC_IC_inf'], p['AUROC_IC_sup']),
            n(c['AUROC']), ic(c['AUROC_IC_inf'], c['AUROC_IC_sup']),
            '+' if dif >= 0 else '', n(dif), n(p['FPR@95']), n(c['FPR@95']))

    cuerpo = ['\\toprule',
              '& \\multicolumn{3}{c}{\\AUROC $\\uparrow$ [IC 95\\,\\%]} & \\multicolumn{2}{c}{\\FPRn{95} $\\downarrow$} \\\\',
              '\\cmidrule(lr){2-4}\\cmidrule(lr){5-6}',
              'Método & PANDA & Control 128\\,px & Diferencia & PANDA & Control \\\\', '\\midrule']
    cuerpo += filas_familias(set(metodos), fila, 6)
    cuerpo.append('\\bottomrule')
    cap = ('Cambio de centro y resolución: PANDA (próstata de otros centros) frente al control de resolución '
           '(las mismas imágenes del test ID reducidas a 128\\,px). \\AUROC (más alto es mejor) y \\FPRn{95} '
           '(más bajo es mejor). Diferencia: \\AUROC de PANDA menos \\AUROC del control. %s %s') % (
        NOTA_BOOT, NOTA_MARCAS.replace('{acc_ash}', acc_ash(datos)))
    escribir(S, 't10_panda_control.tex', tabla(cap, 'tab:ood-panda-control', 'lccccc', cuerpo,
                                               '\\scriptsize', '3pt'),
             FASE_C + '/tabla_principal.csv')


def t10_familias(R, S, datos):
    metodos = ['msp', 'mls', 'ebo', 'react', 'ash', 'dice', 'she', 'she_cosine', 'she_euclidean']
    cab = ' & '.join(CONJUNTOS.values())

    def fila(m):
        return '%s & %s & %s \\\\' % (METODOS[m], ' & '.join(n(datos[(m, c)]['AUROC']) for c in CONJUNTOS),
                                      pct(datos[(m, 'near_nct_tum_norm')]['ACC_ID'], 2))

    cuerpo = ['\\toprule', 'Método & %s & Exact.\\ ID (\\%%) \\\\' % cab, '\\midrule']
    cuerpo += filas_familias(set(metodos), fila, len(CONJUNTOS) + 2)
    cuerpo.append('\\bottomrule')
    cap = ('Métodos basados en logits, en la modificación de activaciones y variantes de SHE: \\AUROC (más alto '
           'es mejor) en los nueve conjuntos y exactitud ID de la clasificación resultante. Clase positiva: OOD. '
           '$^{a}$ASH modifica las características y con ellas la predicción.')
    escribir(S, 't10_familias.tex', tabla(cap, 'tab:ood-familias', 'l' + 'c' * (len(CONJUNTOS) + 1), cuerpo,
                                          '\\scriptsize', '2.5pt'),
             FASE_C + '/tabla_principal.csv')


def t10_bootstrap_rmds(R, S):
    filas = leer_csv(os.path.join(R, FASE_C, 'bootstrap_pareado_rmds.csv'))
    cuerpo = ['\\toprule', 'Método & Diferencia & IC 95\\,\\% & $p$ \\\\', '\\midrule']
    for f in filas:
        d = float(f['dif_AUROC_rmds_menos_metodo'])
        p = float(f['p_bootstrap'])
        cuerpo.append('%s & %s%s & %s & %s \\\\' % (
            METODOS[f['metodo']], '+' if d >= 0 else '$-$', n(abs(d)), ic(f['IC_inf'], f['IC_sup']),
            '$<0{,}001$' if p == 0 else n(p, 2)))
    cuerpo.append('\\bottomrule')
    cap = ('\\emph{Bootstrap} pareado (1.000 remuestreos, semilla 0) de la diferencia \\AUROC(RMDS) $-$ '
           '\\AUROC(método) en el near-OOD principal (TUM+NORM). Diferencia positiva: RMDS es mejor. '
           '$p<0{,}001$: ninguna réplica cruzó el cero. $^{a}$, $^{\\dagger}$: como en \\cref{tab:ood-near}.')
    escribir(S, 't10_bootstrap_rmds.tex', tabla(cap, 'tab:ood-bootstrap-rmds', 'lccc', cuerpo, '\\footnotesize'),
             FASE_C + '/bootstrap_pareado_rmds.csv')


# ---------------------------------------------------------------------------
# Capítulo 11: STOOD-X
# ---------------------------------------------------------------------------
def t11_stoodx(R, S, datos):
    metodos = ['stoodx_100', 'stoodx_875', 'stoodx_100_kc', 'knn', 'rmds']
    cuerpo = ['\\toprule',
              '& ' + ' & '.join('\\multicolumn{2}{c}{%s}' % METODOS[m] for m in metodos) + ' \\\\',
              ''.join('\\cmidrule(lr){%d-%d}' % (2 + 2 * i, 3 + 2 * i) for i in range(len(metodos))),
              'Conjunto & ' + ' & '.join(['\\AUROC & \\FPRn{95}'] * len(metodos)) + ' \\\\', '\\midrule']
    for c, nombre in CONJUNTOS.items():
        celdas = []
        for m in metodos:
            celdas += [n(datos[(m, c)]['AUROC']), n(datos[(m, c)]['FPR@95'])]
        cuerpo.append('%s & %s \\\\' % (nombre, ' & '.join(celdas)))
    cuerpo.append('\\bottomrule')
    cap = ('\\stoodx con el 100\\,\\% y el 87,5\\,\\% de las características ($K=500$, puntuación $-z$) y la variante '
           'exploratoria $K_c$, frente a KNN y RMDS: \\AUROC (más alto es mejor) y \\FPRn{95} (más bajo es mejor) '
           'en los nueve conjuntos. Clase positiva: OOD. $^{\\dagger}$Variante exploratoria, propuesta tras ver '
           'datos OOD.')
    escribir(S, 't11_stoodx.tex', tabla(cap, 'tab:stoodx-resultados', 'l' + 'c' * 10, cuerpo,
                                        '\\scriptsize', '2.5pt'),
             FASE_C + '/tabla_principal.csv')


def t11_barrido_k(R, S):
    filas = leer_csv(os.path.join(R, STOODX_VAL, 'barrido_K_y_configuraciones.csv'))
    conj = ['near_nct_tum_norm', 'afin_nct_lym', 'cov_panda', 'far_dtd']
    por = OrderedDict()
    for f in filas:
        por.setdefault((f['config'], int(f['K'])), {})[f['conjunto']] = f
    orden = sorted([k for k in por if k[0] == '100'], key=lambda k: k[1]) + \
        [k for k in por if k[0] == '875'] + [k for k in por if k[0] == '100_kc']
    cuerpo = ['\\toprule',
              '& ' + ' & '.join('\\multicolumn{2}{c}{%s}' % CONJUNTOS[c] for c in conj) + ' & Tiempo & $p=0$ \\\\',
              ''.join('\\cmidrule(lr){%d-%d}' % (2 + 2 * i, 3 + 2 * i) for i in range(len(conj))),
              '$K$ & ' + ' & '.join(['\\AUROC & \\FPRn{95}'] * len(conj)) + ' & (ms/img) & test ID \\\\',
              '\\midrule']
    for k in orden:
        d = por[k]
        f0 = d[conj[0]]
        if k[0] == '100':
            etiqueta = str(k[1])
        elif k[0] == '875':
            etiqueta = '%d (87,5\\,\\%%)' % k[1]
            cuerpo.append('\\midrule')
        else:
            etiqueta = '$K_c$$^{\\dagger}$'
        celdas = []
        for c in conj:
            celdas += [n(d[c]['AUROC_menos_z']), n(d[c]['FPR@95_menos_z'])]
        t = float(f0['ms_por_imagen_gpu']) + float(f0['ms_por_imagen_cpu'])
        cuerpo.append('%s & %s & %s & %s\\,\\%% \\\\' % (etiqueta, ' & '.join(celdas), n(t, 1),
                                                        pct(f0['prop_p0_id_test'], 1)))
    cuerpo.append('\\bottomrule')
    cap = ('Sensibilidad de \\stoodx al número de vecinos $K$ (análisis de sensibilidad; \\emph{no} se usa para '
           'elegir $K$). Subconjunto de validación: 1.000 imágenes del test ID (estratificadas por clase) y 500 de '
           'cada conjunto OOD, semilla 0. Puntuación $-z$; 100\\,\\% de las características salvo indicación. '
           '\\AUROC: más alto es mejor; \\FPRn{95}: más bajo es mejor. Tiempo por imagen: GPU (cálculo de '
           'distancias) más CPU (test de Mann-Whitney). Última columna: proporción del test ID con $p=0$ exacto '
           '(subdesbordamiento). $^{\\dagger}$Variante exploratoria $K_c=\\min(500,\\lfloor n_c/2\\rfloor)$.')
    escribir(S, 't11_barrido_k.tex', tabla(cap, 'tab:stoodx-barrido-k', 'l' + 'c' * 10, cuerpo,
                                           '\\scriptsize', '2.5pt'),
             STOODX_VAL + '/barrido_K_y_configuraciones.csv')


def t11_calibracion(R, S):
    filas = [f for f in leer_csv(os.path.join(R, STOODX_VAL, 'calibracion_id_val.csv')) if f['config'] == 'K=500']
    filas.sort(key=lambda f: (f['clase_pred'] in ('global', 'todas', 'TOTAL'), -int(float(f['n_c_train']))))
    cuerpo = ['\\toprule',
              'Clase predicha & $n_c$ & $n_{\\mathrm{val}}$ & KS $D$ & $p<0{,}05$ & $p=0$ & $p=1$ & Mediana de $p$ \\\\',
              '\\midrule']
    for f in filas:
        nombre = f['clase_pred']
        if nombre in ('global', 'todas', 'TOTAL'):
            cuerpo.append('\\midrule')
            nombre = '\\textbf{Todas}'
        else:
            nombre = clase(nombre)
        med = float(f['mediana_p'])
        cuerpo.append('%s & %s & %s & %s & %s\\,\\%% & %s\\,\\%% & %s\\,\\%% & %s \\\\' % (
            nombre, entero(f['n_c_train']) if f['n_c_train'] else '--', entero(f['n_val']), n(f['KS_D'], 3),
            pct(f['prop_p_lt_0.05']), pct(f['prop_p_0']), pct(f['prop_p_1']),
            '$\\approx 0$' if med < 1e-3 else n(med, 3)))
    cuerpo.append('\\bottomrule')
    cap = ('Calibración de los $p$-valores de \\stoodx ($K=500$) en la validación ID (solo datos ID), por clase '
           'predicha. Si el test estuviera calibrado, los $p$-valores seguirían una $U(0,1)$: KS $D$ (distancia de '
           'Kolmogorov-Smirnov a la uniforme) cercano a 0 y alrededor de un 5\\,\\% de $p<0{,}05$. $n_c$: imágenes '
           'de entrenamiento predichas en la clase (conjunto de referencia); $n_{\\mathrm{val}}$: imágenes de '
           'validación predichas en ella.')
    escribir(S, 't11_calibracion.tex', tabla(cap, 'tab:stoodx-calibracion', 'lrrccccc', cuerpo,
                                             '\\scriptsize', '3pt'),
             STOODX_VAL + '/calibracion_id_val.csv')


def t11_saturacion(R, S):
    filas = [f for f in leer_csv(os.path.join(R, FASE_B, 'empates_saturacion.csv')) if f['metodo'] == 'stoodx_100']
    cuerpo = ['\\toprule',
              'Conjunto & Saturadas test ID & Saturadas OOD & \\AUROC & \\AUROC peor caso & \\AUROC mejor caso \\\\',
              '\\midrule']
    for f in filas:
        if f['conjunto'] not in CONJUNTOS:
            continue
        cuerpo.append('%s & %s\\,\\%% & %s\\,\\%% & %s & %s & %s \\\\' % (
            CONJUNTOS[f['conjunto']], pct(f['frac_saturadas_id_test']), pct(f['frac_saturadas_ood']),
            n(f['AUROC']), n(f['AUROC_peor']), n(f['AUROC_mejor'])))
    cuerpo.append('\\bottomrule')
    cap = ('Saturación de la puntuación $-z$ de \\stoodx (100\\,\\%, $K=500$) por separación completa: proporción '
           'de imágenes con $U=n_1n_2$ y cotas de su efecto en el \\AUROC (más alto es mejor), forzando el peor y '
           'el mejor orden entre las imágenes ID y OOD saturadas. \\FPRn{95} y \\CCRn{5} no cambian en ningún '
           'conjunto.')
    escribir(S, 't11_saturacion.tex', tabla(cap, 'tab:stoodx-saturacion', 'lccccc', cuerpo, '\\footnotesize', '4pt'),
             FASE_B + '/empates_saturacion.csv')


# ---------------------------------------------------------------------------
# Capítulo 12: predicción conforme
# ---------------------------------------------------------------------------
def t12_ood_conforme(R, S):
    filas = leer_csv(os.path.join(R, 'results_conforme/deteccion_ood_conforme.csv'))
    conj = ['near_nct_tum_norm', 'afin_nct_lym', 'cov_panda', 'control_res_128', 'far_dtd']
    cuerpo = ['\\toprule', 'Método & $\\alpha$ & Falsas alarmas test ID [IC 95\\,\\%] & ' +
              ' & '.join(CONJUNTOS[c] for c in conj) + ' \\\\', '\\midrule']
    anterior = None
    for f in filas:
        nombre = f['nombre'].replace('%', '\\%').replace('-z', '$-z$')
        if anterior is not None and nombre != anterior:
            cuerpo.append('\\midrule')
        cuerpo.append('%s & %s & %s %s & %s \\\\' % (
            nombre if nombre != anterior else '', n(f['alfa'], 2), n(f['falsas_alarmas_id_test']),
            ic(f['FA_IC_inf'], f['FA_IC_sup']), ' & '.join(n(f['detectado_' + c]) for c in conj)))
        anterior = nombre
    cuerpo.append('\\bottomrule')
    cap = ('Detección OOD conforme con el umbral calibrado en la validación ID (22.691 imágenes). Falsas alarmas: '
           'proporción del test ID marcada como OOD, con IC exacto del 95\\,\\% (debe ser compatible con $\\alpha$ '
           'si validación y test son intercambiables). Resto de columnas: proporción detectada como OOD en cada '
           'conjunto (más alto es mejor).')
    escribir(S, 't12_ood_conforme.tex', tabla(cap, 'tab:conforme-ood', 'llcccccc', cuerpo,
                                              '\\scriptsize', '3pt'),
             'results_conforme/deteccion_ood_conforme.csv')


def t12_aps_raps(R, S):
    filas = leer_csv(os.path.join(R, 'results_conforme/aps_raps_resumen.csv'))
    d = {(f['metodo'], f['alfa'], f['conjunto']): f for f in filas}
    cuerpo = ['\\toprule',
              '& & \\multicolumn{3}{c}{Test ID} & \\multicolumn{2}{c}{Control 128\\,px} \\\\',
              '\\cmidrule(lr){3-5}\\cmidrule(lr){6-7}',
              'Método & $\\alpha$ & Cobertura [IC 95\\,\\%] & Tamaño & Vacíos & Cobertura & Tamaño \\\\', '\\midrule']
    for alfa in sorted({f['alfa'] for f in filas}, key=float):
        for met in ['APS', 'RAPS']:
            t, c = d.get((met, alfa, 'id_test')), d.get((met, alfa, 'control_res_128'))
            if t is None:
                continue
            cuerpo.append('%s & %s & %s %s & %s & %s\\,\\%% & %s & %s \\\\' % (
                met, n(alfa, 2), n(t['cobertura']), ic(t['cob_IC_inf'], t['cob_IC_sup']), n(t['tamano_medio'], 2),
                pct(t['frac_vacio']), n(c['cobertura']) if c else '--', n(c['tamano_medio'], 2) if c else '--'))
    cuerpo.append('\\bottomrule')
    cap = ('Conjuntos de predicción APS y RAPS sobre las probabilidades del Swin-S, calibrados con el 80\\,\\% de la '
           'validación ID. Cobertura: proporción de imágenes cuya clase verdadera está en el conjunto (objetivo '
           '$1-\\alpha$), con IC exacto del 95\\,\\%; tamaño medio del conjunto (más pequeño es mejor a igual '
           'cobertura) y proporción de conjuntos vacíos.')
    escribir(S, 't12_aps_raps.tex', tabla(cap, 'tab:conforme-aps', 'llccccc', cuerpo, '\\footnotesize', '3pt'),
             'results_conforme/aps_raps_resumen.csv')


def t12_aps_tamano_ood(R, S):
    filas = leer_csv(os.path.join(R, 'results_conforme/aps_raps_resumen.csv'))
    d = {(f['metodo'], f['alfa'], f['conjunto']): f for f in filas}
    conj = ['id_test'] + [c for c in CONJUNTOS if any(k[2] == c for k in d)]
    nombres = dict(CONJUNTOS, id_test='Test ID')
    cuerpo = ['\\toprule', 'Método & $\\alpha$ & ' + ' & '.join(nombres[c] for c in conj) + ' \\\\', '\\midrule']
    for alfa in sorted({f['alfa'] for f in filas}, key=float):
        for met in ['APS', 'RAPS']:
            if (met, alfa, 'id_test') not in d:
                continue
            cuerpo.append('%s & %s & %s \\\\' % (met, n(alfa, 2), ' & '.join(
                n(d[(met, alfa, c)]['tamano_medio'], 2) if (met, alfa, c) in d else '--' for c in conj)))
    cuerpo.append('\\bottomrule')
    cap = ('Tamaño medio de los conjuntos de predicción APS y RAPS en el test ID y en los conjuntos OOD. Un '
           'tamaño mayor fuera de distribución indica que el conjunto refleja la incertidumbre ante entradas OOD.')
    escribir(S, 't12_aps_tamano_ood.tex', tabla(cap, 'tab:conforme-tamano-ood', 'll' + 'c' * len(conj), cuerpo,
                                                '\\scriptsize', '3pt'),
             'results_conforme/aps_raps_resumen.csv')


def t12_mondrian_global(R, S):
    filas = leer_csv(os.path.join(R, 'results_conforme/mondrian/global.csv'))
    cuerpo = ['\\toprule', 'Puntuación & $\\alpha$ & Versión & Cobertura test ID [IC 95\\,\\%] & Tamaño medio & '
              'Clases $<1-\\alpha$ & Cobertura control 128\\,px \\\\', '\\midrule']
    ctrl = {(f['puntuacion'], f['alfa'], f['version']): f for f in filas if f['conjunto'] == 'control_res_128'}
    previo = None
    for f in filas:
        if f['conjunto'] != 'id_test':
            continue
        clave = (f['puntuacion'], f['alfa'])
        if previo is not None and clave != previo:
            cuerpo.append('\\midrule')
        c = ctrl.get((f['puntuacion'], f['alfa'], f['version']))
        cuerpo.append('%s & %s & %s & %s %s & %s & %s / 14 & %s \\\\' % (
            f['puntuacion'], n(f['alfa'], 2), f['version'].capitalize(), n(f['cobertura']),
            ic(f['cob_IC_inf'], f['cob_IC_sup']), n(f['tamano_medio'], 2), f['clases_por_debajo_1_menos_alfa'],
            n(c['cobertura']) if c else '--'))
        previo = clave
    cuerpo.append('\\bottomrule')
    cap = ('Predicción conforme marginal frente a Mondrian (condicionada por clase) con las puntuaciones LAC y APS. '
           'Cobertura (objetivo $1-\\alpha$) con IC exacto del 95\\,\\%, tamaño medio del conjunto, número de '
           'clases con cobertura puntual por debajo de $1-\\alpha$ en el test ID y cobertura en el control de '
           'resolución (\\emph{covariate shift} con las mismas etiquetas).')
    escribir(S, 't12_mondrian_global.tex', tabla(cap, 'tab:mondrian-global', 'lllcccc', cuerpo,
                                                 '\\scriptsize', '3pt'),
             'results_conforme/mondrian/global.csv')


def t12_mondrian_clase(R, S):
    filas = [f for f in leer_csv(os.path.join(R, 'results_conforme/mondrian/por_clase.csv'))
             if f['puntuacion'] == 'LAC' and f['alfa'] == '0.05' and f['conjunto'] == 'id_test']
    d = {(f['clase'], f['version']): f for f in filas}
    clases = sorted({f['clase'] for f in filas}, key=lambda c: int(d[(c, 'mondrian')]['n_cal']))
    cuerpo = ['\\toprule', '& & & \\multicolumn{2}{c}{Cobertura} & \\multicolumn{2}{c}{Tamaño medio} \\\\',
              '\\cmidrule(lr){4-5}\\cmidrule(lr){6-7}',
              'Clase & $n_y$ & $k_y$ & Marginal & Mondrian & Marginal & Mondrian \\\\', '\\midrule']
    for c in clases:
        mg, mo = d[(c, 'marginal')], d[(c, 'mondrian')]
        k = entero(mo['k_y']) + ('$^{\\max}$' if mo['umbral_es_maximo'] == 'True' else '')
        cuerpo.append('%s & %s & %s & %s & %s & %s & %s \\\\' % (
            clase(c), entero(mo['n_cal']), k, n(mg['cobertura']), n(mo['cobertura']),
            n(mg['tamano_medio'], 2), n(mo['tamano_medio'], 2)))
    cuerpo.append('\\bottomrule')
    cap = ('Cobertura por clase en el test ID con la puntuación LAC y $\\alpha=0{,}05$: versión marginal frente '
           'a Mondrian (objetivo: $0{,}95$ en cada clase). $n_y$: imágenes de calibración de la clase; '
           '$k_y=\\lceil (n_y+1)(1-\\alpha)\\rceil$. $^{\\max}$: $k_y=n_y$, el umbral es la mayor puntuación de '
           'calibración de la clase.')
    escribir(S, 't12_mondrian_clase.tex', tabla(cap, 'tab:mondrian-clase', 'lrrcccc', cuerpo,
                                                '\\scriptsize', '3pt'),
             'results_conforme/mondrian/por_clase.csv')


# ---------------------------------------------------------------------------
# Capítulo 13: fuga por lámina
# ---------------------------------------------------------------------------
def t13_contiguidad(R, S):
    d = leer_json(os.path.join(R, 'results_integridad/informe.json'))
    c = d['contiguidad']
    filas = [('\\texttt{val} original respecto a \\texttt{train} original', 'orig_train∩orig_val',
              'orig_val_respecto_a_orig_train', 'orig_val'),
             ('Validación respecto a entrenamiento (TFG)', 'train∩val', 'val_respecto_a_train', 'val'),
             ('Test respecto a entrenamiento (TFG)', 'train∩test', 'test_respecto_a_train', 'test')]
    cuerpo = ['\\toprule', 'Comparación & Láminas compartidas & Con su lámina en la referencia & '
              'Con un parche contiguo en la referencia \\\\', '\\midrule']
    for nombre, kl, kc, kp in filas:
        cuerpo.append('%s & %d / %d & %s\\,\\%% & %s\\,\\%% \\\\' % (
            nombre, d['laminas_compartidas'][kl], d['laminas'][kp], pct(c[kc]['frac_con_lamina_en_ref']),
            pct(c[kc]['frac_contiguo_8_vecinos'])))
    cuerpo.append('\\bottomrule')
    cap = ('Fuga entre particiones por lámina, deducida de los nombres de fichero '
           '(\\texttt{<lámina>\\_<x>\\_<y>\\_<tamaño>.png}): láminas compartidas, proporción de parches cuya '
           'lámina aparece en la partición de referencia y proporción con un parche contiguo (8 vecinos a 224\\,px) '
           'en ella.')
    escribir(S, 't13_contiguidad.tex', tabla(cap, 'tab:fuga-contiguidad', '>{\\raggedright\\arraybackslash}X ccc',
                                             cuerpo, '\\footnotesize', None, 'tabularx'),
             'results_integridad/informe.json')


def t13_vecino(R, S):
    filas = leer_csv(os.path.join(R, 'results_ood_laminas/fuga_vecino_mas_cercano.csv'))
    cuerpo = ['\\toprule', 'Clase & $n$ & Misma lámina & Misma lámina y contiguo & Misma clase & '
              'Azar (misma lámina) \\\\', '\\midrule']
    for f in filas:
        nombre = '\\textbf{Todas}' if f['clase'] == 'todas' else clase(f['clase'])
        cuerpo.append('%s & %s & %s & %s & %s & %s \\\\' % (
            nombre, entero(f['n']), n(f['nn_misma_lamina']), n(f['nn_misma_lamina_y_contiguo']),
            n(f['nn_misma_clase']), n(f['azar_misma_lamina_dentro_de_la_clase'])))
        if f['clase'] == 'todas':
            cuerpo.append('\\midrule')
    cuerpo.append('\\bottomrule')
    cap = ('Vecino más cercano en entrenamiento (distancia coseno, características de 768 dimensiones del Swin-S) '
           'de cada parche del test ID: proporción que es de la misma lámina, de la misma lámina y contiguo, y de '
           'la misma clase. Azar: proporción esperada de misma lámina eligiendo el vecino al azar dentro de la '
           'clase.')
    escribir(S, 't13_vecino.tex', tabla(cap, 'tab:fuga-vecino', 'lrcccc', cuerpo, '\\scriptsize', '3pt'),
             'results_ood_laminas/fuga_vecino_mas_cercano.csv')


def t13_loso(R, S):
    filas = leer_csv(os.path.join(R, 'results_ood_laminas/comparacion_original_vs_loso.csv'))
    d = {(f['metodo'], f['conjunto']): f for f in filas}
    conj = [c for c in CONJUNTOS if ('knn', c) in d]
    cuerpo = ['\\toprule',
              '& \\multicolumn{3}{c}{KNN} & \\multicolumn{3}{c}{MDS} \\\\',
              '\\cmidrule(lr){2-4}\\cmidrule(lr){5-7}',
              'Conjunto & \\AUROC & \\FPRn{95} & \\CCRn{5} & \\AUROC & \\FPRn{95} & \\CCRn{5} \\\\', '\\midrule']
    for c in conj:
        celdas = []
        for m in ['knn', 'mds']:
            f = d[(m, c)]
            for k in ['AUROC', 'FPR@95', 'CCR@FPR5']:
                celdas.append('%s $\\to$ %s' % (n(f[k + '_original']), n(f[k + '_loso'])))
        cuerpo.append('%s & %s \\\\' % (CONJUNTOS[c], ' & '.join(celdas)))
    cuerpo.append('\\bottomrule')
    cap = ('Sensibilidad de la detección OOD a la fuga por lámina: KNN y MDS con todo el entrenamiento como '
           'referencia (original) $\\to$ excluyendo, para cada parche del test ID, los parches de entrenamiento de '
           'su lámina (\\emph{leave-one-slide-out}). \\AUROC y \\CCRn{5}: más alto es mejor; \\FPRn{95}: más bajo '
           'es mejor. Los conjuntos OOD se puntúan con todo el entrenamiento.')
    escribir(S, 't13_loso.tex', tabla(cap, 'tab:fuga-loso', 'lcccccc', cuerpo, '\\scriptsize', '2.5pt'),
             'results_ood_laminas/comparacion_original_vs_loso.csv')


def t13_control_interno(R, S):
    filas = leer_csv(os.path.join(R, 'results_ood_laminas/control_interno/resumen_control_interno.csv'))
    cols = ['TUM', 'NORM', 'STR', 'LYM', 'MUS', 'PANDA', 'LYM_menos_media_TUM_NORM']
    cuerpo = ['\\toprule', 'Método & Versión & TUM & NORM & STR & LYM & MUS & PANDA & LYM $-$ media(TUM, NORM) \\\\',
              '\\midrule']
    previo = None
    for f in filas:
        if previo is not None and f['metodo'] != previo:
            cuerpo.append('\\midrule')
        celdas = []
        for k in cols:
            v = float(f[k])
            celdas.append(('$-$' + n(-v)) if v < 0 else n(v))
        cuerpo.append('%s & %s & %s \\\\' % (METODOS[f['metodo']] if f['metodo'] != previo else '',
                                             'original' if f['version'] == 'original' else 'sin lámina',
                                             ' & '.join(celdas)))
        previo = f['metodo']
    cuerpo.append('\\bottomrule')
    cap = ('Control interno de \\nctcrc con y sin la lámina de cada parche en la referencia: \\AUROC (más alto es '
           'mejor) por clase y en PANDA, y diferencia entre LYM y la media de TUM y NORM.')
    escribir(S, 't13_control_interno.tex', tabla(cap, 'tab:fuga-control-interno', 'llccccccc', cuerpo,
                                                 '\\scriptsize', '3pt'),
             'results_ood_laminas/control_interno/resumen_control_interno.csv')


# ---------------------------------------------------------------------------
# Apéndices
# ---------------------------------------------------------------------------
def tA_aupr(R, S, datos, columna, nombre_fich, label, titulo):
    cab = ' & '.join(CONJUNTOS.values())

    def fila(m):
        return '%s & %s \\\\' % (METODOS[m], ' & '.join(n(datos[(m, c)][columna]) for c in CONJUNTOS))

    cuerpo = ['\\toprule', 'Método & %s \\\\' % cab, '\\midrule']
    cuerpo += filas_familias(set(METODOS), fila, len(CONJUNTOS) + 1)
    cuerpo.append('\\bottomrule')
    cap = ('%s de los 16 métodos en los nueve conjuntos (más alto es mejor). %s') % (
        titulo, NOTA_MARCAS.replace('{acc_ash}', acc_ash(datos)))
    escribir(S, nombre_fich, tabla(cap, label, 'l' + 'c' * len(CONJUNTOS), cuerpo, '\\scriptsize', '2.5pt'),
             FASE_C + '/tabla_principal.csv')


def tB_anexo(R, S):
    filas = leer_csv(os.path.join(R, FASE_A, 'resultados_anexo.csv')) + \
        leer_csv(os.path.join(R, FASE_B, 'resultados_anexo.csv'))
    d = por_metodo_conjunto(filas)
    cab = ' & '.join(ANEXO.values())

    def fila(m):
        return '%s & %s & %s \\\\' % (METODOS[m], ' & '.join(n(d[(m, c)]['AUROC']) for c in ANEXO),
                                      ' & '.join(n(d[(m, c)]['FPR@95']) for c in ANEXO))

    metodos = {m for m in METODOS if all((m, c) in d for c in ANEXO)}
    cuerpo = ['\\toprule',
              '& \\multicolumn{4}{c}{\\AUROC $\\uparrow$} & \\multicolumn{4}{c}{\\FPRn{95} $\\downarrow$} \\\\',
              '\\cmidrule(lr){2-5}\\cmidrule(lr){6-9}', 'Método & %s & %s \\\\' % (cab, cab), '\\midrule']
    cuerpo += filas_familias(metodos, fila, 9)
    cuerpo.append('\\bottomrule')
    cap = ('Clases restantes de \\nctcrc: tejido adiposo (ADI), fondo (BACK), restos celulares (DEB) y moco (MUC). '
           '\\AUROC (más alto es mejor) y \\FPRn{95} (más bajo es mejor); clase positiva: OOD. '
           '$^{a}$, $^{\\dagger}$: como en \\cref{tab:ood-near}.')
    escribir(S, 'tB_anexo_nct.tex', tabla(cap, 'tab:anexo-nct', 'l' + 'c' * 8, cuerpo, '\\scriptsize', '3pt'),
             FASE_A + ' y ' + FASE_B + ' (resultados_anexo.csv)')


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--resultados', default=RAIZ_RESULTADOS)
    ap.add_argument('--salida', default='tablas')
    args = ap.parse_args()
    R, S = args.resultados, args.salida
    os.makedirs(S, exist_ok=True)
    print('Generando tablas en ' + S)

    t08_particion(R, S)

    t09_modelos(R, S)
    t09_recall_clase(R, S)
    t09_mcnemar(R, S)
    t09_agrupaciones(R, S)
    t09_sensibilidad_gleason(R, S)

    datos = por_metodo_conjunto(leer_csv(os.path.join(R, FASE_C, 'tabla_principal.csv')))
    t10_bloque(R, S, datos, 'near_nct_tum_norm', 't10_near.tex', 'tab:ood-near',
               'Near-OOD principal (\\nctcrc, TUM+NORM)')
    t10_control_interno(R, S, datos)
    t10_panda_control(R, S, datos)
    t10_bloque(R, S, datos, 'far_dtd', 't10_far.tex', 'tab:ood-far', 'Far-OOD (DTD)')
    t10_familias(R, S, datos)
    t10_bootstrap_rmds(R, S)

    t11_stoodx(R, S, datos)
    t11_barrido_k(R, S)
    t11_calibracion(R, S)
    t11_saturacion(R, S)

    t12_ood_conforme(R, S)
    t12_aps_raps(R, S)
    t12_aps_tamano_ood(R, S)
    t12_mondrian_global(R, S)
    t12_mondrian_clase(R, S)

    t13_contiguidad(R, S)
    t13_vecino(R, S)
    t13_loso(R, S)
    t13_control_interno(R, S)

    tA_aupr(R, S, datos, 'AUPR_In', 'tA_aupr_in.tex', 'tab:aupr-in', '\\AUPRin (clase positiva: ID)')
    tA_aupr(R, S, datos, 'AUPR_Out', 'tA_aupr_out.tex', 'tab:aupr-out', '\\AUPRout (clase positiva: OOD)')
    tB_anexo(R, S)


if __name__ == '__main__':
    main()
