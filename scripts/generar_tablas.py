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
FASE_C = 'results_ood/faseC_K144'   # faseC_2026-10-20 más la fila de STOOD-X con K = 144
FASE_A = 'results_ood/faseA_2026-10-20_11-19-35'
FASE_B = 'results_ood/faseB_paper_2026-10-20'
STOODX_VAL = 'results_ood/stoodx_validacion'
FASE_B_K144 = 'results_ood/faseB_paper_K144'
SELECCION_K = 'results_ood/stoodx_seleccion_k'

# ---------------------------------------------------------------------------
# Nombres para la memoria
# ---------------------------------------------------------------------------
METODOS = OrderedDict([
    ('msp', 'MSP'), ('mls', 'MaxLogit'), ('ebo', 'Energy'),
    ('react', 'ReAct'), ('ash', 'ASH$^{a}$'), ('dice', 'DICE'),
    ('knn', 'KNN'), ('mds', 'MDS'), ('rmds', 'RMDS'), ('vim', 'ViM'),
    ('she', 'SHE (prod.\\ escalar)'), ('she_cosine', 'SHE (coseno)'), ('she_euclidean', 'SHE (euclídea)'),
    ('stoodx_100', 'STOOD-X (100\\,\\%)'), ('stoodx_100_k144', 'STOOD-X ($K=144$)$^{\\ddagger}$'),
    ('stoodx_875', 'STOOD-X (87,5\\,\\%)'),
    ('stoodx_100_kc', 'STOOD-X $K_c$$^{\\dagger}$'),
])
FAMILIAS = [
    ('Basados en logits', ['msp', 'mls', 'ebo']),
    ('Modificación de activaciones', ['react', 'ash', 'dice']),
    ('Características y distancias', ['knn', 'mds', 'rmds', 'vim', 'she', 'she_cosine', 'she_euclidean']),
    ('STOOD-X', ['stoodx_100', 'stoodx_100_k144', 'stoodx_875', 'stoodx_100_kc']),
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
               'datos OOD; no es el método principal. $^{\\ddagger}$100\\,\\% de las características y $K=144$, elegido '
               'solo con la validación ID (\\cref{sec:stoodx-seleccion-k}); el resto de filas de \\stoodx usan '
               '$K=500$, el valor del artículo.')

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


def tabla(caption, label, columnas, cuerpo, tamano='\\small', sep=None, entorno='tabular', ancho=None,
          notas=None):
    l = ['\\begin{table}[tbp]', '\\centering', tamano]
    if sep:
        l.append('\\setlength{\\tabcolsep}{%s}' % sep)
    l += ['\\caption{%s}' % caption, '\\label{%s}' % label]
    if entorno == 'tabularx':
        l.append('\\begin{tabularx}{%s}{%s}' % (ancho or '\\textwidth', columnas))
    else:
        l.append('\\begin{%s}{%s}' % (entorno, columnas))
    l += cuerpo
    l.append('\\end{%s}' % entorno)
    if notas:
        l += ['', '\\smallskip', '\\parbox{\\linewidth}{\\scriptsize %s}' % notas]
    l.append('\\end{table}')
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


# Capítulo 8: parámetros de las corrupciones sintéticas (Zhang et al., 2022)
# ---------------------------------------------------------------------------
# Rótulos de la columna «Parámetro» (texto, no cifras); las cifras salen del CSV.
PARAM_CORRUPCION = OrderedDict([
    ('brightness', 'Incremento de V (HSV)'),
    ('saturate', 'Incremento de S (HSV)'),
    ('hue', 'Incremento de H (HSV, circular)$^{c}$'),
    ('marking_blur', 'Tamaño de la mancha (alto $\\times$ ancho)$^{a}$'),
    ('bubble_blur', 'Proporción de mezcla con la burbuja$^{b}$'),
    ('jpeg_compression', 'Calidad JPEG'),
    ('pixelate', 'Factor de reducción (filtro BOX)'),
    ('defocus_blur', '(radio del disco; $\\sigma$ del antialias)'),
    ('motion_blur', '(radio; $\\sigma$) de ImageMagick; ángulo $\\mathcal{U}(-45^\\circ, 45^\\circ)$'),
])


def t08_corrupciones(R, S):
    import re
    origen = 'results_corrupciones/parametros_corrupciones.csv'
    filas = {f['codigo']: f for f in leer_csv(os.path.join(R, origen))}
    assert list(filas) == list(PARAM_CORRUPCION), 'corrupciones del CSV distintas de las esperadas'
    mancha = re.compile(r'^(\d+)x(\d+) px en (\(\d+, \d+\))$')
    posiciones = set()

    def valor(codigo, v):
        if codigo == 'marking_blur':
            alto, ancho, pos = mancha.match(v).groups()
            posiciones.add(pos)
            return '%s $\\times$ %s\\,px' % (alto, ancho)
        return v.replace('.', '{,}')

    cuerpo = ['\\toprule', 'Corrupción & Parámetro & Nivel 1 & Nivel 3 & Nivel 5 \\\\', '\\midrule']
    for codigo, rotulo in PARAM_CORRUPCION.items():
        f = filas[codigo]
        cuerpo.append('%s & %s & %s & %s & %s \\\\' % (
            f['corrupcion'][0].upper() + f['corrupcion'][1:], rotulo,
            valor(codigo, f['nivel_1']), valor(codigo, f['nivel_3']), valor(codigo, f['nivel_5'])))
    cuerpo.append('\\bottomrule')
    assert len(posiciones) == 1, 'la mancha no está en una posición fija'
    pos = posiciones.pop().replace('(', '').replace(')', '')
    # El número de burbujas del repositorio (6) consta en results_corrupciones/decisiones.md.
    notas = ('Marcas y burbujas usan los recursos de 224\\,px del propio repositorio (el código usa por defecto '
             'los de 96\\,px). Solo el desenfoque por movimiento es aleatorio: su semilla se deriva con SHA-256 del '
             'fichero, la corrupción y el nivel. '
             '$^{a}$Siempre la misma mancha, en la posición fija (%s). '
             '$^{b}$Se usa siempre la primera de las 6 burbujas del repositorio, en posición fija. '
             '$^{c}$Implementación marcada como poco fiable en el código original.') % pos
    cap = ('Parámetros de las nueve corrupciones de Zhang et al.~\\cite{zhang2022corruptions} en los niveles de '
           'severidad 1, 3 y 5. La severidad crece con el parámetro, salvo en JPEG y pixelado, en los que crece '
           'al bajar la calidad o el factor.')
    escribir(S, 't08_corrupciones.tex',
             tabla(cap, 'tab:corrupciones',
                   '@{}l>{\\raggedright\\arraybackslash}Xccc@{}', cuerpo, '\\footnotesize', '4pt',
                   'tabularx', notas=notas),
             origen)


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
    clases = sorted({f['clase'] for f in filas}, key=lambda c: (-int(rec[(list(MODELOS)[0], c)]['n']), c))
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
           'Referencia: XCiT-Medium del artículo del conjunto de datos~\\cite{ayensa2026}, con otro reparto de '
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
           'directamente comparables con el artículo del conjunto de datos~\\cite{ayensa2026}, porque coinciden '
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
    cap = ('%s: \\AUROC y \\CCRn{5} (más alto es mejor) y \\FPRn{95} (más bajo es mejor) de los %d métodos. %s '
           'En negrita, el mejor valor entre los métodos no exploratorios. %s') % (
        titulo, len(METODOS), NOTA_BOOT, NOTA_MARCAS.replace('{acc_ash}', acc_ash(datos)))
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
    cap = ('PANDA (próstata de otros centros, adquirida a una escala mucho menor) frente al control de resolución '
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
# Capítulo 10: corrupciones sintéticas (results_corrupciones y su fase 8b)
# ---------------------------------------------------------------------------
CORR = 'results_corrupciones'
CORR_PRINCIPALES = ['msp', 'mds', 'knn', 'vim', 'rmds', 'stoodx_100']
NOTA_BOOT_CORR = ('IC del 95\\,\\% por \\emph{bootstrap} pareado por imagen (1.000 réplicas, semilla 0).')


def nombre_det(d):
    """Nombre del detector sin la marca de ASH de las tablas principales (su nota no aplica aquí)."""
    return METODOS[d].replace('$^{a}$', '')


def nombres_corr(R):
    """Código de la corrupción -> nombre en castellano (de parametros_corrupciones.csv), en el orden de la tabla 8."""
    filas = {f['codigo']: f['corrupcion'] for f in leer_csv(os.path.join(R, CORR, 'parametros_corrupciones.csv'))}
    return OrderedDict((c, filas[c][0].upper() + filas[c][1:]) for c in PARAM_CORRUPCION)


def celdas_corr(R):
    return [(c, l) for c in nombres_corr(R) for l in ('1', '3', '5')]


def fila_celda(nombres, c, l):
    return '%s & %s' % (nombres[c] if l == '1' else '', l)


def separador_corr(c, l, primera):
    return [] if (l != '1' or primera) else ['\\addlinespace[2pt]']


def t10_corr_exactitud(R, S):
    origen = CORR + '/exactitud_celda.csv'
    e = {(f['corrupcion'], f['nivel']): f for f in leer_csv(os.path.join(R, origen))}
    nombres = nombres_corr(R)
    limpia = e[('limpia', '0')]
    cuerpo = ['\\toprule',
              '& \\multicolumn{3}{c}{Exactitud $\\uparrow$} & \\multicolumn{3}{c}{Caída respecto a la limpia} \\\\',
              '\\cmidrule(lr){2-4}\\cmidrule(lr){5-7}',
              'Corrupción & Nivel 1 & Nivel 3 & Nivel 5 & Nivel 1 & Nivel 3 & Nivel 5 \\\\', '\\midrule']
    for c in nombres:
        fs = [e[(c, l)] for l in ('1', '3', '5')]
        cuerpo.append('%s & %s & %s \\\\' % (nombres[c], ' & '.join(n(f['exactitud']) for f in fs),
                                            ' & '.join(n(f['caida_exactitud']) for f in fs)))
        cuerpo.append('& %s & %s \\\\[2pt]' % (
            ' & '.join('{\\tiny %s}' % ic(f['exactitud_ic_inf'], f['exactitud_ic_sup']) for f in fs),
            ' & '.join('{\\tiny %s}' % ic(f['caida_ic_inf'], f['caida_ic_sup']) for f in fs)))
    cuerpo.append('\\bottomrule')
    cap = ('Exactitud del Swin-S (más alto es mejor) en cada corrupción y nivel de severidad, y caída respecto a la '
           'imagen limpia (exactitud %s %s), con su IC debajo. %s') % (
        n(limpia['exactitud']), ic(limpia['exactitud_ic_inf'], limpia['exactitud_ic_sup']),
        NOTA_BOOT_CORR)
    escribir(S, 't10_corr_exactitud.tex', tabla(cap, 'tab:ood-corr-exactitud', 'lcccccc', cuerpo,
                                                '\\scriptsize', '3pt'), origen)


def t10_corr_metrica(R, S, columna, mayor, nombre_fich, label, titulo):
    origen = CORR + '/metricas_celda.csv'
    m = {(f['detector'], f['corrupcion'], f['nivel']): f for f in leer_csv(os.path.join(R, origen))}
    nombres = nombres_corr(R)
    cuerpo = ['\\toprule', 'Corrupción & Nivel & %s \\\\' % ' & '.join(nombre_det(d) for d in CORR_PRINCIPALES),
              '\\midrule']
    for i, (c, l) in enumerate(celdas_corr(R)):
        vals = [round(float(m[(d, c, l)][columna]), 3) for d in CORR_PRINCIPALES]
        mejor = max(vals) if mayor else min(vals)
        cuerpo += separador_corr(c, l, i == 0)
        cuerpo.append('%s & %s \\\\' % (fila_celda(nombres, c, l),
                                        ' & '.join(negrita(n(v), v == mejor) for v in vals)))
    cuerpo.append('\\bottomrule')
    cap = ('%s de los seis detectores principales en cada corrupción y nivel de severidad. ID: las imágenes limpias '
           'del test; OOD: sus versiones corruptas. En negrita, el mejor valor de cada fila. Las demás '
           'configuraciones y los IC del 95\\,\\%% están en la \\cref{%s}.') % (titulo, label.replace('ood-', 'apc-'))
    escribir(S, nombre_fich, tabla(cap, label, 'llcccccc', cuerpo, '\\scriptsize', '3pt'), origen)


def tC_corr_completa(R, S, columna, nombre_fich, label, titulo):
    """Longtable: una fila por detector y corrupción; columnas, los niveles 1, 3 y 5 con su IC."""
    origen = CORR + '/metricas_celda.csv'
    m = {(f['detector'], f['corrupcion'], f['nivel']): f for f in leer_csv(os.path.join(R, origen))}
    nombres = nombres_corr(R)
    detectores = [d for d in METODOS if (d, 'brightness', '1') in m]
    assert len(detectores) == 15, detectores
    cab = ['\\toprule', 'Detector & Corrupción & Nivel 1 & Nivel 3 & Nivel 5 \\\\', '\\midrule']
    cap = ('%s de las 15 configuraciones de detectores en cada corrupción y nivel de severidad. ID: las imágenes '
           'limpias del test; OOD: sus versiones corruptas. %s') % (titulo, NOTA_BOOT_CORR)
    l = ['{\\scriptsize', '\\setlength{\\tabcolsep}{4pt}', '\\begin{longtable}{llccc}',
         '\\caption{%s}\\label{%s} \\\\' % (cap, label)] + cab + ['\\endfirsthead',
         '\\multicolumn{5}{@{}l}{\\textit{(continuación)}} \\\\'] + cab + ['\\endhead', '\\bottomrule', '\\endlastfoot']
    for i, d in enumerate(detectores):
        if i:
            l.append('\\midrule')
        for j, c in enumerate(nombres):
            fs = [m[(d, c, nv)] for nv in ('1', '3', '5')]
            l.append('%s & %s & %s \\\\' % (nombre_det(d) if j == 0 else '', nombres[c], ' & '.join(
                '%s %s' % (n(f[columna]), ic(f[columna + '_ic_inf'], f[columna + '_ic_sup'])) for f in fs)))
    l += ['\\end{longtable}', '}']
    escribir(S, nombre_fich, l, origen)


def t10_corr_cec(R, S):
    origen = CORR + '/cec.csv'
    filas = [f for f in leer_csv(os.path.join(R, origen)) if f['corrupcion'] == 'global']

    def principal(f):
        v = f['CEC_saturadas_como_empate']
        return float(v) if v else float(f['CEC'])

    filas.sort(key=principal)
    cuerpo = ['\\toprule', 'Detector & CEC $\\downarrow$ & IC 95\\,\\% & Pares empatados (\\%) \\\\', '\\midrule']
    for f in filas:
        if f['CEC_saturadas_como_empate']:
            # Variante principal (decisión del autor): pares con los dos niveles saturados = empate. Sin IC en el CSV.
            cuerpo.append('%s$^{\\ast}$ & %s & -- & %s$^{\\ast\\ast}$ \\\\' % (
                nombre_det(f['detector']), n(principal(f)), n(f['pct_pares_ambos_saturados'], 2)))
        else:
            cuerpo.append('%s & %s & %s & %s \\\\' % (
                nombre_det(f['detector']), n(f['CEC']), ic(f['CEC_ic_inf'], f['CEC_ic_sup']),
                n(f['pct_pares_empatados'], 3)))
    cuerpo.append('\\bottomrule')
    sx = {f['detector']: f for f in filas if f['CEC_saturadas_como_empate']}
    notas = ('0 = ordenación monótona; 0,5 = azar. La CEC de MSP es la métrica de Zhang et '
             'al.~\\cite{zhang2022corruptions} adaptada a nuestros niveles. '
             '$^{\\ast}$Los pares en los que los dos niveles tienen la puntuación saturada cuentan como empate; con '
             'empates exactos, la CEC es %s %s (100\\,\\%%) y %s %s (87,5\\,\\%%). '
             '$^{\\ast\\ast}$Pares con los dos niveles saturados.') % (
        n(sx['stoodx_100']['CEC']), ic(sx['stoodx_100']['CEC_ic_inf'], sx['stoodx_100']['CEC_ic_sup']),
        n(sx['stoodx_875']['CEC']), ic(sx['stoodx_875']['CEC_ic_inf'], sx['stoodx_875']['CEC_ic_sup']))
    cap = ('CEC global (más bajo es mejor) de las 15 configuraciones de detectores, de menor a mayor, sobre las '
           'nueve corrupciones y los niveles 0, 1, 3 y 5. %s Pares empatados: porcentaje de pares de niveles con '
           'la misma puntuación.') % NOTA_BOOT_CORR
    escribir(S, 't10_corr_cec.tex', tabla(cap, 'tab:ood-corr-cec', 'lccc', cuerpo, '\\footnotesize', '4pt',
                                          notas=notas), origen)


def t10_corr_saturacion(R, S):
    origen = CORR + '/saturacion_stoodx.csv'
    s = {(f['corrupcion'], f['nivel']): f for f in leer_csv(os.path.join(R, origen)) if f['detector'] == 'stoodx_100'}
    nombres = nombres_corr(R)
    cuerpo = ['\\toprule', 'Corrupción & Nivel 1 & Nivel 3 & Nivel 5 \\\\', '\\midrule']
    for c in nombres:
        cuerpo.append('%s & %s \\\\' % (nombres[c], ' & '.join(n(s[(c, l)]['pct_saturadas'], 1) for l in ('1', '3', '5'))))
    cuerpo.append('\\bottomrule')
    cap = ('Porcentaje de imágenes con la puntuación de \\stoodx (100\\,\\%%, $K=500$) saturada ($U=n_1n_2$; '
           '\\cref{obs:u-empates}) en cada corrupción y nivel de severidad. Referencia: %s\\,\\%% en las imágenes '
           'limpias del test.') % n(s[('limpia', '0')]['pct_saturadas'], 2)
    escribir(S, 't10_corr_saturacion.tex', tabla(cap, 'tab:ood-corr-saturacion', 'lccc', cuerpo, '\\footnotesize',
                                                 '6pt'), origen)


def t10_corr_auroc_err(R, S):
    origen = CORR + '/fase8b/auroc_err_celda.csv y stoodx_variantes_auroc_err_celda.csv'
    a = {(f['detector'], f['corrupcion'], f['nivel']): f
         for f in leer_csv(os.path.join(R, CORR, 'fase8b/auroc_err_celda.csv'))}
    v = {(f['variante'], f['corrupcion'], f['nivel']): f
         for f in leer_csv(os.path.join(R, CORR, 'fase8b/stoodx_variantes_auroc_err_celda.csv'))}
    nombres = nombres_corr(R)
    nombres['limpia'] = 'Limpia'

    def val(d, c, l):
        if d == 'stoodx_100':
            f = v[('empates_reales', c, l)]
            return f['AUROC_err'], f['IC_inf'], f['IC_sup']
        f = a[(d, c, l)]
        return f['AUROC_err'], f['IC_inf'], f['IC_sup']

    cuerpo = ['\\toprule', 'Corrupción & Nivel & Errores & %s \\\\' % ' & '.join(
        nombre_det(d) + ('$^{\\ast}$' if d == 'stoodx_100' else '') for d in CORR_PRINCIPALES), '\\midrule']
    for i, (c, l) in enumerate([('limpia', '0')] + celdas_corr(R)):
        vals = [val(d, c, l) for d in CORR_PRINCIPALES]
        mejor = max(round(float(x[0]), 3) for x in vals)
        if i == 1:
            cuerpo.append('\\midrule')
        else:
            cuerpo += separador_corr(c, l, i <= 1)
        nombre = '%s & %s' % (nombres[c] if l in ('0', '1') else '', '--' if l == '0' else l)
        cuerpo.append('%s & %s & %s \\\\' % (nombre, entero(a[('msp', c, l)]['n_errores']), ' & '.join(
            negrita(n(x[0]), round(float(x[0]), 3) == mejor) for x in vals)))
        cuerpo.append('& & & %s \\\\[1pt]' % ' & '.join('{\\tiny %s}' % ic(x[1], x[2]) for x in vals))
    cuerpo.append('\\bottomrule')
    o = v[('original', 'pixelate', '5')]
    e = v[('empates_reales', 'pixelate', '5')]
    notas = ('$^{\\ast}$Las imágenes con la puntuación saturada reciben la misma puntuación (empate real, que el AUROC '
             'cuenta como $\\tfrac{1}{2}$); con la puntuación $-z$ original, su orden lo decide un término del orden '
             'de $10^{-8}$ (por ejemplo, pixelado 5: %s con empates reales frente a %s con la original; la variante '
             'original está en \\texttt{stoodx\\_variantes\\_auroc\\_err\\_celda.csv}).') % (n(e['AUROC_err']),
                                                                                         n(o['AUROC_err']))
    cap = ('\\AUROC de detección de errores de clasificación (clase positiva: imagen mal clasificada; más alto es '
           'mejor) de los seis detectores principales, en la imagen limpia y en cada corrupción y nivel, con su IC '
           'debajo. Errores: número de imágenes mal clasificadas de las \\num{12618} de la celda. En negrita, el '
           'mejor valor de cada fila. %s') % NOTA_BOOT_CORR
    escribir(S, 't10_corr_auroc_err.tex', tabla(cap, 'tab:ood-corr-auroc-err', 'llrcccccc', cuerpo,
                                                '\\scriptsize', '2.5pt', notas=notas), CORR + '/' + origen)


def t10_corr_aurc(R, S):
    origen = CORR + '/fase8b/aurc.csv'
    filas = {(f['detector'], f['variante']): f for f in leer_csv(os.path.join(R, origen))}
    orden = [('oraculo', 'bruta', 'Oráculo'), ('knn', 'bruta', None), ('mds', 'bruta', None), ('vim', 'bruta', None),
             ('rmds', 'bruta', None), ('stoodx_100', 'saturadas_empatadas', None), ('msp', 'bruta', None),
             ('azar', 'bruta', 'Azar')]
    cuerpo = ['\\toprule', 'Detector & AURC $\\downarrow$ & IC 95\\,\\% \\\\', '\\midrule']
    for d, var, rot in orden:
        f = filas[(d, var)]
        nombre = rot or nombre_det(d) + ('$^{\\ast}$' if d == 'stoodx_100' else '')
        if d == 'azar':
            cuerpo.append('\\midrule')
        cuerpo.append('%s & %s & %s \\\\' % (nombre, n(f['AURC']), ic(f['IC_inf'], f['IC_sup'])))
        if d == 'oraculo':
            cuerpo.append('\\midrule')
    cuerpo.append('\\bottomrule')
    o = filas[('stoodx_100', 'bruta')]
    total = float(filas[('oraculo', 'bruta')]['n_puntos'])
    assert int(total) == 12618 * 28
    notas = ('$^{\\ast}$Imágenes saturadas con la misma puntuación (empate real); con la puntuación original, %s %s.') % (
        n(o['AURC']), ic(o['IC_inf'], o['IC_sup']))
    cap = ('Área bajo la curva riesgo-cobertura (AURC; más bajo es mejor) conjunta de las imágenes limpias y las 27 '
           'celdas (\\num{%d} imágenes; tasa de error global %s), al aceptar las imágenes de mayor a menor '
           'puntuación. Oráculo: rechaza primero los errores; azar: riesgo constante. IC del 95\\,\\%% por '
           '\\emph{bootstrap} por imagen original (cada réplica arrastra sus 28 versiones).') % (
        int(total), n(filas[('azar', 'bruta')]['tasa_error_total']))
    escribir(S, 't10_corr_aurc.tex', tabla(cap, 'tab:ood-corr-aurc', 'lcc', cuerpo, '\\footnotesize', '4pt',
                                           notas=notas), origen)


UMBRAL_DETECTORES = ['stoodx_100', 'msp', 'vim']
UMBRAL_CELDAS = [('limpia', '0'), ('brightness', '5'), ('jpeg_compression', '5'), ('pixelate', '5'),
                 ('defocus_blur', '3'), ('motion_blur', '5')]


def filas_umbral(R, celdas, con_ic):
    origen = CORR + '/fase8b/umbral_fijo_celda.csv'
    u = {(f['detector'], f['corrupcion'], f['nivel']): f for f in leer_csv(os.path.join(R, origen))
         if f['origen_umbral'] == 'id_val'}
    nombres = nombres_corr(R)
    nombres['limpia'] = 'Limpia'
    cuerpo = []
    for i, (c, l) in enumerate(celdas):
        if i:
            cuerpo.append('\\midrule' if con_ic else '\\addlinespace[2pt]')
        for j, d in enumerate(UMBRAL_DETECTORES):
            f = u[(d, c, l)]
            g = float(f['ganancia_selectiva'])
            gan = ('+' if g >= 0 else '$-$') + n(abs(g))
            if con_ic:
                gan += ' {\\tiny %s}' % ic_signo(f['ganancia_selectiva_IC_inf'], f['ganancia_selectiva_IC_sup'])
            celda = ('%s %s' % (nombres[c], '' if l == '0' else l)).strip() if j == 0 else ''
            cuerpo.append('%s & %s & %s & %s & %s & %s & %s & %s \\\\' % (
                celda, n(f['exactitud_celda']) if j == 0 else '', nombre_det(d), n(f['aceptacion']),
                n(f['exactitud_aceptadas']), n(f['exactitud_rechazadas']), gan, n(f['captura_errores'])))
    return cuerpo, u


CAB_UMBRAL = ('Celda & Exact.\\ & Detector & Acept. & Exact.\\ acept.\\ $\\uparrow$ & '
              'Exact.\\ rech. & Ganancia $\\uparrow$ & Captura $\\uparrow$ \\\\')
NOTA_UMBRAL = ('Exact.: exactitud de toda la celda; acept.: aceptación (fracción aceptada) y aceptadas; rech.: '
               'rechazadas. Umbral: percentil 5 de las puntuaciones de la validación ID (acepta el 95\\,\\% de \\texttt{id\\_val}); '
               'se acepta si la puntuación es mayor o igual. Ganancia (selectiva): exactitud de las aceptadas menos la de '
               'toda la celda. Captura (de errores): fracción de las imágenes mal clasificadas que se rechazan.')


def t10_corr_umbral(R, S):
    cuerpo, u = filas_umbral(R, UMBRAL_CELDAS, True)
    cap = ('Clasificación selectiva con un umbral fijo en una selección de celdas, para \\stoodx (100\\,\\%%), MSP y '
           'ViM (más alto es mejor en exactitud de las aceptadas, ganancia y captura). %s Ganancia con su IC del '
           '95\\,\\%% por \\emph{bootstrap} por imagen (1.000 réplicas). Todas las celdas, en la '
           '\\cref{tab:apc-corr-umbral}.') % NOTA_UMBRAL
    escribir(S, 't10_corr_umbral.tex', tabla(cap, 'tab:ood-corr-umbral', 'lllccccc',
                                             ['\\toprule', CAB_UMBRAL, '\\midrule'] + cuerpo + ['\\bottomrule'],
                                             '\\scriptsize', '2.5pt'), CORR + '/fase8b/umbral_fijo_celda.csv')


def tC_corr_umbral(R, S):
    cuerpo, u = filas_umbral(R, [('limpia', '0')] + celdas_corr(R), False)
    cap = ('Clasificación selectiva con el umbral fijo de la \\cref{tab:ood-corr-umbral} en todas las celdas, para '
           '\\stoodx (100\\,\\%%), MSP y ViM. %s Los IC están en \\texttt{umbral\\_fijo\\_celda.csv}.') % NOTA_UMBRAL
    cab = ['\\toprule', CAB_UMBRAL, '\\midrule']
    l = ['{\\scriptsize', '\\setlength{\\tabcolsep}{2.5pt}', '\\begin{longtable}{lllccccc}',
         '\\caption{%s}\\label{tab:apc-corr-umbral} \\\\' % cap] + cab + [
        '\\endfirsthead', '\\multicolumn{8}{@{}l}{\\textit{(continuación)}} \\\\'] + cab + [
        '\\endhead', '\\bottomrule', '\\endlastfoot'] + cuerpo + ['\\end{longtable}', '}']
    escribir(S, 'tC_corr_umbral.tex', l, CORR + '/fase8b/umbral_fijo_celda.csv')


# ---------------------------------------------------------------------------
# Capítulo 11: STOOD-X
# ---------------------------------------------------------------------------
def t11_stoodx(R, S, datos):
    metodos = ['stoodx_100', 'stoodx_875', 'stoodx_100_kc', 'stoodx_100_k144', 'knn', 'rmds']
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
    cap = ('\\stoodx con el 100\\,\\% y el 87,5\\,\\% de las características ($K=500$, puntuación $-z$), la variante '
           'exploratoria $K_c$ y $K=144$, frente a KNN y RMDS: \\AUROC (más alto es mejor) y \\FPRn{95} (más bajo '
           'es mejor) en los nueve conjuntos. Clase positiva: OOD. $^{\\dagger}$Variante exploratoria, propuesta '
           'tras ver datos OOD. $^{\\ddagger}$$K$ elegido solo con la validación ID (\\cref{sec:stoodx-seleccion-k}).')
    escribir(S, 't11_stoodx.tex', tabla(cap, 'tab:stoodx-resultados', 'l' + 'c' * (2 * len(metodos)), cuerpo,
                                        '\\scriptsize', '2.5pt'),
             FASE_C + '/tabla_principal.csv')


def t11_seleccion_k(R, S):
    medias = leer_csv(os.path.join(R, SELECCION_K, 'seleccion_k_loco.csv'))
    por_clase = leer_csv(os.path.join(R, SELECCION_K, 'seleccion_k_loco_por_clase.csv'))
    elegido = leer_json(os.path.join(R, SELECCION_K, 'K_elegido.json'))['K_elegido']
    mejor_k = {}
    for f in por_clase:
        h = f['clase_retenida']
        if h not in mejor_k or float(f['AUROC']) > float(mejor_k[h]['AUROC']):
            mejor_k[h] = f
    victorias = {}
    for f in mejor_k.values():
        victorias[int(f['K'])] = victorias.get(int(f['K']), 0) + 1
    assert sum(victorias.values()) == 14
    cuerpo = ['\\toprule',
              '$K$ & \\AUROC medio $\\uparrow$ & \\FPRn{95} medio $\\downarrow$ & Clases en que es el mejor \\\\',
              '\\midrule']
    for f in medias:
        k = int(f['K'])
        cuerpo.append('%s & %s & %s & %d \\\\' % (negrita(str(k), k == elegido), negrita(n(f['AUROC']), k == elegido),
                                                n(f['FPR@95']), victorias.get(k, 0)))
    cuerpo.append('\\bottomrule')
    cap = ('Selección de $K$ de \\stoodx (100\\,\\% de las características, puntuación $-z$) por validación '
           '\\emph{leave-one-class-out} en la validación ID: cada una de las 14 clases ID hace por turno de '
           'pseudo-OOD frente al resto de la validación, sin sus imágenes en la referencia de entrenamiento y con '
           'su logit anulado. \\AUROC (más alto es mejor) y \\FPRn{95} (más bajo es mejor) medios sobre las 14 '
           'clases, y número de clases retenidas en las que cada $K$ obtiene el mayor \\AUROC. En negrita, el $K$ '
           'elegido. No se usa ningún dato de test ni OOD.')
    escribir(S, 't11_seleccion_k.tex', tabla(cap, 'tab:stoodx-seleccion-k', 'cccc', cuerpo, '\\footnotesize'),
             SELECCION_K + '/seleccion_k_loco.csv y seleccion_k_loco_por_clase.csv')


def t11_k144_vs_k500(R, S):
    filas = {f['conjunto']: f for f in leer_csv(os.path.join(R, FASE_B_K144, 'comparacion_K144_vs_K500.csv'))}
    cuerpo = ['\\toprule',
              '& \\multicolumn{4}{c}{\\AUROC $\\uparrow$} & \\multicolumn{2}{c}{\\FPRn{95} $\\downarrow$} & '
              '\\multicolumn{2}{c}{\\CCRn{5} $\\uparrow$} \\\\',
              '\\cmidrule(lr){2-5}\\cmidrule(lr){6-7}\\cmidrule(lr){8-9}',
              'Conjunto & $K=500$ & $K=144$ & Diferencia [IC 95\\,\\%] & $p$ & $K=500$ & $K=144$ & $K=500$ & $K=144$ \\\\',
              '\\midrule']
    for c, nombre in CONJUNTOS.items():
        f = filas[c]
        d, p = float(f['dAUROC']), float(f['p_boot'])
        cuerpo.append('%s & %s & %s & %s%s %s & %s & %s & %s & %s & %s \\\\' % (
            nombre, n(f['AUROC_500']), n(f['AUROC_144']), '+' if d >= 0 else '$-$', n(abs(d)),
            ic(f['IC_lo'], f['IC_hi']), '$<0{,}001$' if p == 0 else n(p, 3),
            n(f['FPR95_500']), n(f['FPR95_144']), n(f['CCR_500']), n(f['CCR_144'])))
    cuerpo.append('\\bottomrule')
    cap = ('\\stoodx (100\\,\\% de las características, puntuación $-z$) con $K=500$ (valor del artículo) y con '
           '$K=144$ (elegido solo con la validación ID, \\cref{tab:stoodx-seleccion-k}), sobre las mismas imágenes. '
           '\\AUROC y \\CCRn{5}: más alto es mejor; \\FPRn{95}: más bajo es mejor. Diferencia: \\AUROC($K=144$) '
           '$-$ \\AUROC($K=500$), con IC y $p$ por \\emph{bootstrap} pareado (1.000 remuestreos, semilla 0); '
           '$p<0{,}001$: ninguna réplica cruzó el cero. Clase positiva: OOD.')
    escribir(S, 't11_k144_vs_k500.tex', tabla(cap, 'tab:stoodx-k144-k500', 'lcccccccc', cuerpo,
                                              '\\scriptsize', '3pt'),
             FASE_B_K144 + '/comparacion_K144_vs_K500.csv (comparar_k144_k500.py)')


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


def t11_saturacion(R, S, fase=FASE_B, k=500, fich='t11_saturacion.tex', label='tab:stoodx-saturacion'):
    filas = [f for f in leer_csv(os.path.join(R, fase, 'empates_saturacion.csv')) if f['metodo'] == 'stoodx_100']
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
    cap = ('Saturación de la puntuación $-z$ de \\stoodx (100\\,\\%%, $K=%d$) por separación completa: proporción '
           'de imágenes con $U=n_1n_2$ y cotas de su efecto en el \\AUROC (más alto es mejor), forzando el peor y '
           'el mejor orden entre las imágenes ID y OOD saturadas. \\FPRn{95} y \\CCRn{5} no cambian en ningún '
           'conjunto.') % k
    escribir(S, fich, tabla(cap, label, 'lccccc', cuerpo, '\\footnotesize', '4pt'),
             fase + '/empates_saturacion.csv')


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
    clases = sorted({f['clase'] for f in filas}, key=lambda c: (int(d[(c, 'mondrian')]['n_cal']), c))
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
                                             cuerpo, '\\scriptsize', None, 'tabularx'),
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
    cap = ('%s de los %d métodos en los nueve conjuntos (más alto es mejor). %s') % (
        titulo, len(METODOS), NOTA_MARCAS.replace('{acc_ash}', acc_ash(datos)))
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
# Apéndice D: detección OOD con ConvNeXt-S (fase 9b, espacio principal M)
# ---------------------------------------------------------------------------
CONVNEXT = 'results_ood_convnext/espacio_principal'
# Mismos métodos que la tabla principal, sin las variantes exploratorias de STOOD-X.
METODOS_CNX = OrderedDict((m, METODOS[m].replace('$^{a}$', '')) for m in METODOS
                          if m not in ('stoodx_875', 'stoodx_100_kc', 'stoodx_100_k144'))
# ViM, ReAct, ASH y DICE se evalúan en B; el resto de métodos de características, en M.
METODOS_CNX['react'] = 'ReAct$^{B}$'
METODOS_CNX['ash'] = 'ASH$^{a,B}$'
METODOS_CNX['dice'] = 'DICE$^{a,B}$'
METODOS_CNX['vim'] = 'ViM$^{B}$'
NOTA_B = ('$^{B}$En el espacio B (512 dimensiones): requieren la capa que entra en el clasificador lineal. '
          'KNN, MDS, RMDS, SHE y \\stoodx, en M (768); MSP, MaxLogit y Energy, en los logits.')
PRINCIPALES_CNX = ['msp', 'knn', 'mds', 'rmds', 'vim', 'stoodx_100']
NOTA_BOOT_PAR = ('IC del 95\\,\\% por \\emph{bootstrap} pareado por imagen (1.000 remuestreos estratificados ID/OOD, '
                 'semilla 0).')


def leer_csv_cnx(ruta):
    """CSV de la fase 9b: números con coma decimal; se pasan a punto solo los campos que son un número."""
    def num(v):
        try:
            float(v.replace(',', '.'))
            return v.replace(',', '.')
        except (ValueError, AttributeError):
            return v
    return [{k: num(v) for k, v in f.items()} for f in leer_csv(ruta)]


def tex_texto(s):
    """Texto de los CSV de la fase 9 (UTF-8 con símbolos) a LaTeX compilable con pdflatex."""
    for a, b in [('%', '\\%'), ('_', '\\_'), ('−', '$-$'), ('→', '$\\to$'), ('≈', '$\\approx$'),
                 ('≥', '$\\geq$'), ('·', '$\\cdot$'), ('≤', '$\\leq$'), ('′', '$\'$'), ('|', '$|$'), (' > ', ' $>$ '),
                 (' < ', ' $<$ ')]:
        s = s.replace(a, b)
    return s


def signo(x, d=3):
    return ('+' if float(x) >= 0 else '$-$') + n(abs(float(x)), d)


def ic_signo(a, b, d=3):
    return '[%s; %s]' % (signo(a, d), signo(b, d))


def nota_acc_cnx(datos):
    return ('$^{a}$Modifican la predicción: la exactitud ID baja al %s\\,\\%% (ASH) y al %s\\,\\%% (DICE, con el '
            'postprocesador de OpenOOD sin cambios).') % (pct(datos[('ash', 'near_nct_tum_norm')]['ACC_ID'], 1),
                                                          pct(datos[('dice', 'near_nct_tum_norm')]['ACC_ID'], 1))


def tD_configuracion(R, S):
    cfg = {f['parametro']: f for f in leer_csv_cnx(os.path.join(R, CONVNEXT, 'configuracion_convnext.csv'))}
    v = lambda k: tex_texto(cfg[k]['valor'])
    nt = lambda k: tex_texto(cfg[k]['nota'])
    mant, expo = cfg['max_dif_logits']['valor'].split('e')
    dif = '$%s\\cdot 10^{%d}$' % (mant.replace('.', '{,}'), int(expo))
    filas = [
        ('Modelo', '%s; mismo entrenamiento que en el \\cref{sec:protocolo}' % v('modelo')),
        ('Cabeza', '%s. %s' % (v('cabeza'), nt('cabeza'))),
        ('Criterio del espacio', v('criterio_espacio')),
        ('Espacio principal', '%s: %s. Máx.\\ $|$media espacial $-$ C[:, 768:]$|$ en 100 imágenes de test ID: %s' % (
            v('espacio_principal'), nt('espacio_principal'), n(cfg['comprobacion_M']['valor'], 1))),
        ('ViM, ReAct, ASH y DICE', '%s: %s. Máx.\\ $|W\'B+b\'-\\mathrm{logits}|$ en los 11 conjuntos: %s' % (
            v('espacio_vim_react_ash_dice'), nt('espacio_vim_react_ash_dice'), dif)),
        ('Logits', '%s: %s' % (v('espacio_logits'), nt('espacio_logits'))),
        ('Espacios de sensibilidad', '%s (%s)' % (v('espacio_sensibilidad'), nt('espacio_sensibilidad'))),
        ('Dimensión de ViM', '%s (%s)' % (v('vim_dim'), nt('vim_dim'))),
        ('$K$ de \\stoodx', '%s (%s)' % (v('stoodx_K'), nt('stoodx_K'))),
        ('Ejecución', 'nodo %s, %s, %s (%s)' % (v('nodo'), v('cpu_gpu'), v('precision'), nt('cpu_gpu'))),
        ('Tiempo con M', '%s (%s)' % (v('tiempo_total_M'), nt('tiempo_total_M'))),
        ('Tiempo con B y C', '%s (%s)' % (v('tiempo_total_fase9'), nt('tiempo_total_fase9'))),
        ('Memoria con M (MaxRSS)', '%s (%s)' % (v('maxrss_M'), nt('maxrss_M'))),
        ('Exactitud de test', '%s (%s)' % (n(cfg['exactitud_test']['valor'], 5), nt('exactitud_test'))),
    ]
    cuerpo = ['\\toprule', 'Parámetro & Valor \\\\', '\\midrule']
    cuerpo += ['%s & %s \\\\' % f for f in filas]
    cuerpo.append('\\bottomrule')
    cap = ('Configuración de la evaluación OOD con ConvNeXt-S y diferencias con la del Swin-S. M, B y C son los '
           'espacios de características; $W\'$ y $b\'$, la última capa lineal con la BatchNorm plegada.')
    escribir(S, 'tD_configuracion.tex', tabla(cap, 'tab:convnext-config', '@{}l>{\\raggedright\\arraybackslash}X@{}',
                                              cuerpo, '\\footnotesize', entorno='tabularx'),
             CONVNEXT + '/configuracion_convnext.csv')


def tD_auroc(R, S, datos):
    conjuntos = list(CONJUNTOS)
    best = {c: mejores(datos, METODOS_CNX, c, 'AUROC', True) for c in conjuntos}

    def celda(m, c):
        f = datos[(m, c)]
        s = negrita(n(f['AUROC']), round(float(f['AUROC']), 3) == round(best[c], 3))
        return s + (' %s' % ic(f['AUROC_IC_inf'], f['AUROC_IC_sup']) if c == 'near_nct_tum_norm' else '')

    def fila(m):
        return '%s & %s \\\\' % (METODOS_CNX[m], ' & '.join(celda(m, c) for c in conjuntos))

    cuerpo = ['\\toprule', 'Método & TUM+NORM [IC 95\\,\\%%] & %s \\\\' % ' & '.join(
        CONJUNTOS[c] for c in conjuntos[1:]), '\\midrule']
    cuerpo += filas_familias(set(METODOS_CNX), fila, len(conjuntos) + 1)
    cuerpo.append('\\bottomrule')
    cap = ('ConvNeXt-S, espacio principal M: \\AUROC (más alto es mejor) de los 14 métodos en los nueve conjuntos. '
           'Clase positiva: OOD. En negrita, el mejor valor de cada conjunto. %s Los IC del resto de conjuntos están '
           'en \\texttt{tabla\\_principal\\_convnext.csv}. %s %s') % (
        NOTA_BOOT.replace(' Clase positiva: OOD.', ''), NOTA_B, nota_acc_cnx(datos))
    escribir(S, 'tD_auroc.tex', tabla(cap, 'tab:convnext-auroc', 'l' + 'c' * len(conjuntos), cuerpo,
                                      '\\scriptsize', '2pt'),
             CONVNEXT + '/tabla_principal_convnext.csv')


def tD_fpr95_ccr(R, S, datos):
    conjuntos = list(CONJUNTOS)
    best = {c: mejores(datos, METODOS_CNX, c, 'FPR@95', False) for c in conjuntos}
    best_ccr = mejores(datos, METODOS_CNX, 'near_nct_tum_norm', 'CCR@FPR5', True)

    def fila(m):
        fp = [negrita(n(datos[(m, c)]['FPR@95']), round(float(datos[(m, c)]['FPR@95']), 3) == round(best[c], 3))
              for c in conjuntos]
        cc = float(datos[(m, 'near_nct_tum_norm')]['CCR@FPR5'])
        return '%s & %s & %s \\\\' % (METODOS_CNX[m], ' & '.join(fp),
                                      negrita(n(cc), round(cc, 3) == round(best_ccr, 3)))

    k = len(conjuntos)
    cuerpo = ['\\toprule',
              '& \\multicolumn{%d}{c}{\\FPRn{95} $\\downarrow$} & \\CCRn{5} $\\uparrow$ \\\\' % k,
              '\\cmidrule(lr){2-%d}\\cmidrule(lr){%d-%d}' % (k + 1, k + 2, k + 2),
              'Método & %s & TUM+NORM \\\\' % ' & '.join(CONJUNTOS.values()), '\\midrule']
    cuerpo += filas_familias(set(METODOS_CNX), fila, k + 2)
    cuerpo.append('\\bottomrule')
    cap = ('ConvNeXt-S, espacio principal M: \\FPRn{95} (más bajo es mejor) de los 14 métodos en los nueve conjuntos '
           'y \\CCRn{5} (más alto es mejor) en TUM+NORM. Clase positiva: OOD. En negrita, el mejor valor de cada '
           'columna. Los IC de \\FPRn{95} están en \\texttt{tabla\\_principal\\_convnext.csv}. %s %s') % (
        NOTA_B, nota_acc_cnx(datos))
    escribir(S, 'tD_fpr95_ccr.tex', tabla(cap, 'tab:convnext-fpr', 'l' + 'c' * (k + 1), cuerpo,
                                          '\\scriptsize', '2.5pt'),
             CONVNEXT + '/tabla_principal_convnext.csv')


def filas_dif_ic(filas_por_clave, columnas, campo_dif, campo_inf, campo_sup):
    """Una fila con las diferencias por conjunto y, debajo, otra más pequeña con sus IC."""
    cuerpo = []
    for c in CONJUNTOS:
        d = [filas_por_clave.get((k, c)) for k in columnas]
        cuerpo.append('%s & %s \\\\' % (CONJUNTOS[c], ' & '.join(signo(f[campo_dif]) if f else '--' for f in d)))
        cuerpo.append('& %s \\\\[2pt]' % ' & '.join(
            '{\\scriptsize %s}' % ic_signo(f[campo_inf], f[campo_sup]) if f else '' for f in d))
    return cuerpo


def tD_diferencias(R, S):
    d = por_metodo_conjunto(leer_csv_cnx(os.path.join(R, CONVNEXT, 'diferencias_auroc.csv')))
    cuerpo = ['\\toprule', 'Conjunto & %s \\\\' % ' & '.join(METODOS_CNX[m] for m in PRINCIPALES_CNX), '\\midrule']
    cuerpo += filas_dif_ic(d, PRINCIPALES_CNX, 'dif_convnext_menos_swin', 'IC_inf', 'IC_sup')
    cuerpo.append('\\bottomrule')
    cap = ('Diferencia de \\AUROC ConvNeXt-S $-$ Swin-S (positiva: mejor ConvNeXt-S) en los métodos principales, '
           'con su IC debajo; ConvNeXt-S en el espacio M. %s %s Los demás métodos están en '
           '\\texttt{diferencias\\_auroc.csv}.') % (NOTA_BOOT_PAR, NOTA_B.split(' KNN,')[0])
    escribir(S, 'tD_diferencias.tex', tabla(cap, 'tab:convnext-diferencias', 'l' + 'c' * len(PRINCIPALES_CNX),
                                            cuerpo, '\\footnotesize', '2.5pt'),
             CONVNEXT + '/diferencias_auroc.csv')


def tD_conclusiones(R, S):
    filas = leer_csv_cnx(os.path.join(R, CONVNEXT, 'conclusiones_swin.csv'))
    cuerpo = ['\\toprule', '\\# & Conclusión con Swin-S & Swin-S & ConvNeXt-S (M) & Estado con M & Estado con B \\\\',
              '\\midrule']
    mayus = lambda t: t[:1].upper() + t[1:]
    for f in filas:
        # estado_con_B es la última columna y no va entre comillas: csv parte sus comas decimales (clave None).
        est_b = ','.join([f['estado_con_B']] + f.get(None, []))
        cuerpo.append('%s & %s & %s & %s & %s & %s \\\\' % (
            f['num'], tex_texto(f['conclusion']), tex_texto(f['cifra_swin']), tex_texto(f['cifra_convnext']),
            mayus(f['estado']), mayus(tex_texto(est_b))))
    cuerpo.append('\\bottomrule')
    cap = ('Conclusiones del \\cref{cap:deteccion-ood} con Swin-S, una por fila, y cifras que las sostienen con cada '
           'modelo (\\AUROC salvo que se indique otra métrica); ConvNeXt-S en el espacio principal M (ViM, ReAct, ASH '
           'y DICE en B). La última columna da el estado que se obtenía con B como espacio principal. No concluyente: '
           'la ordenación se mantiene, pero los IC se solapan.')
    rr = '>{\\raggedright\\arraybackslash}'
    col = '@{}l%sp{2.2cm}%sX%sX%sp{1.3cm}%sp{1.6cm}@{}' % (rr, rr, rr, rr, rr)
    escribir(S, 'tD_conclusiones.tex', tabla(cap, 'tab:convnext-conclusiones', col, cuerpo, '\\scriptsize', '3pt',
                                             entorno='tabularx'),
             CONVNEXT + '/conclusiones_swin.csv')


def p_valor(p):
    return '$<0{,}0001$' if float(p) < 1e-4 else n(p, 4)


def tD_kendall(R, S):
    filas = leer_csv_cnx(os.path.join(R, CONVNEXT, 'kendall.csv'))
    cuerpo = ['\\toprule',
              '& \\multicolumn{2}{c}{14 métodos} & \\multicolumn{2}{c}{Sin ASH ni DICE (12)} \\\\',
              '\\cmidrule(lr){2-3}\\cmidrule(lr){4-5}', 'Conjunto & $\\tau$ & $p$ & $\\tau$ & $p$ \\\\', '\\midrule']
    for f in filas:
        cuerpo.append('%s & %s & %s & %s & %s \\\\' % (CONJUNTOS[f['conjunto']], n(f['tau']), p_valor(f['p']),
                                                        n(f['tau_sin_ash_dice']), p_valor(f['p_sin_ash_dice'])))
    cuerpo.append('\\bottomrule')
    cap = ('$\\tau$ de Kendall entre las ordenaciones de los métodos por \\AUROC con Swin-S y con ConvNeXt-S, en '
           'cada conjunto ($\\tau=1$: misma ordenación); ConvNeXt-S en el espacio M (ViM, ReAct, ASH y DICE en B). '
           'Valores $p$ sin corregir por comparaciones múltiples.')
    escribir(S, 'tD_kendall.tex', tabla(cap, 'tab:convnext-kendall', 'lcccc', cuerpo, '\\footnotesize', '5pt'),
             CONVNEXT + '/kendall.csv')


def tD_stoodx(R, S):
    pv = {(f['modelo'], f['metodo']): f for f in leer_csv_cnx(os.path.join(R, CONVNEXT, 'panda_vs_control.csv'))}
    sat = {(f['modelo'], f['espacio'], f['conjunto']): f
           for f in leer_csv_cnx(os.path.join(R, CONVNEXT, 'saturacion_stoodx.csv'))}

    def fila_pv(m):
        celdas = ['%s %s' % (n(pv[(mod, m)]['AUROC_panda_vs_control']),
                             ic(pv[(mod, m)]['IC_inf'], pv[(mod, m)]['IC_sup'])) for mod in ('swin', 'convnext')]
        return '%s & %s \\\\' % (METODOS_CNX[m], ' & '.join(celdas))

    l = ['\\begin{table}[tbp]', '\\centering', '\\footnotesize', '\\setlength{\\tabcolsep}{4pt}',
         '\\caption{\\stoodx y la saturación con los dos modelos. (a) \\AUROC con el control de 128\\,px como clase '
         'negativa y PANDA como positiva: por encima de 0,5, la puntuación coloca PANDA como más OOD que el control; '
         'ConvNeXt-S en el espacio M. %s %s (b) Porcentaje de imágenes con la puntuación $-z$ de \\stoodx ($K=500$) '
         'saturada ($U=n_1n_2$) en cada espacio de ConvNeXt-S; en C solo se calculó en el test ID, TUM y NORM.}' % (
             NOTA_BOOT.replace(' Clase positiva: OOD.', ''), NOTA_B.split(' KNN,')[0]),
         '\\label{tab:convnext-stoodx}', '',
         '\\textit{(a) PANDA frente al control}\\par\\smallskip',
         '\\begin{tabular}{lcc}', '\\toprule', 'Método & Swin-S & ConvNeXt-S \\\\', '\\midrule']
    l += filas_familias(set(METODOS_CNX), fila_pv, 3)
    l += ['\\bottomrule', '\\end{tabular}', '', '\\bigskip',
          '\\textit{(b) Imágenes saturadas}\\par\\smallskip',
          '\\begin{tabular}{lcccc}', '\\toprule',
          'Conjunto & Swin-S & ConvNeXt-S (M) & ConvNeXt-S (B) & ConvNeXt-S (C) \\\\', '\\midrule']
    for c, nombre in [('id_test', 'Test ID')] + list(CONJUNTOS.items()):
        celdas = [sat.get(k) for k in [('swin', '-', c), ('convnext', 'M', c), ('convnext', 'B', c),
                                       ('convnext', 'C', c)]]
        l.append('%s & %s \\\\' % (nombre, ' & '.join(pct(f['frac_saturadas']) + '\\,\\%' if f else '--'
                                                         for f in celdas)))
    l += ['\\bottomrule', '\\end{tabular}', '\\end{table}']
    escribir(S, 'tD_stoodx.tex', l, CONVNEXT + '/panda_vs_control.csv y saturacion_stoodx.csv')


def tD_sensibilidad(R, S):
    d = {(f['a'], f['b'], f['conjunto']): f
         for f in leer_csv_cnx(os.path.join(R, CONVNEXT, 'sensibilidad_pareada.csv'))}
    metodos = ['knn', 'mds', 'rmds', 'she', 'she_cosine', 'she_euclidean', 'stoodx_100']
    conjuntos = list(CONJUNTOS)
    k = len(conjuntos)

    def celda(f, c):
        if f is None:
            return '--'
        s = signo(f['dif_a_menos_b'])
        if float(f['IC_inf']) <= 0 <= float(f['IC_sup']):
            s += '$^{\\circ}$'
        return s + (' %s' % ic_signo(f['IC_inf'], f['IC_sup']) if c == 'near_nct_tum_norm' else '')

    cuerpo = ['\\toprule', 'Método & TUM+NORM [IC 95\\,\\%%] & %s \\\\' % ' & '.join(
        CONJUNTOS[c] for c in conjuntos[1:])]
    for otro in ('B', 'C'):
        cuerpo += ['\\midrule', '\\multicolumn{%d}{l}{\\textit{M $-$ %s}} \\\\' % (k + 1, otro)]
        for m in metodos:
            cuerpo.append('%s & %s \\\\' % (METODOS_CNX[m], ' & '.join(
                celda(d.get(('%s@M' % m, '%s@%s' % (m, otro), c)), c) for c in conjuntos)))
    cuerpo.append('\\bottomrule')
    cap = ('Sensibilidad de ConvNeXt-S al espacio de características: diferencia de \\AUROC entre el espacio '
           'principal M (768 dimensiones) y los espacios B (512) y C (1.536), positiva si M es mejor. %s '
           '$^{\\circ}$: el IC contiene el 0. Los IC del resto de conjuntos están en '
           '\\texttt{sensibilidad\\_pareada.csv}. \\stoodx en C solo se calculó en TUM y NORM.') % NOTA_BOOT_PAR
    escribir(S, 'tD_sensibilidad.tex', tabla(cap, 'tab:convnext-sensibilidad', 'l' + 'c' * k, cuerpo,
                                             '\\scriptsize', '2pt'),
             CONVNEXT + '/sensibilidad_pareada.csv')


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
    t08_corrupciones(R, S)

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
    t10_corr_exactitud(R, S)
    t10_corr_metrica(R, S, 'AUROC', True, 't10_corr_auroc.tex', 'tab:ood-corr-auroc',
                     '\\AUROC (más alto es mejor)')
    t10_corr_metrica(R, S, 'FPR95', False, 't10_corr_fpr95.tex', 'tab:ood-corr-fpr95',
                     '\\FPRn{95} (más bajo es mejor)')
    t10_corr_cec(R, S)
    t10_corr_saturacion(R, S)
    t10_corr_auroc_err(R, S)
    t10_corr_aurc(R, S)
    t10_corr_umbral(R, S)

    t11_stoodx(R, S, datos)
    t11_barrido_k(R, S)
    t11_seleccion_k(R, S)
    t11_k144_vs_k500(R, S)
    t11_calibracion(R, S)
    t11_saturacion(R, S)
    t11_saturacion(R, S, FASE_B_K144, 144, 't11_saturacion_k144.tex', 'tab:stoodx-saturacion-k144')

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

    tC_corr_completa(R, S, 'AUROC', 'tC_corr_auroc.tex', 'tab:apc-corr-auroc', '\\AUROC (más alto es mejor)')
    tC_corr_completa(R, S, 'FPR95', 'tC_corr_fpr95.tex', 'tab:apc-corr-fpr95', '\\FPRn{95} (más bajo es mejor)')
    tC_corr_umbral(R, S)

    cnx = por_metodo_conjunto(leer_csv_cnx(os.path.join(R, CONVNEXT, 'tabla_principal_convnext.csv')))
    tD_configuracion(R, S)
    tD_auroc(R, S, cnx)
    tD_fpr95_ccr(R, S, cnx)
    tD_diferencias(R, S)
    tD_conclusiones(R, S)
    tD_kendall(R, S)
    tD_stoodx(R, S)
    tD_sensibilidad(R, S)


if __name__ == '__main__':
    main()
