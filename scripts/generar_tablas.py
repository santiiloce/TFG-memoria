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
import re
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


# Pies de tabla: como máximo unas tres líneas. Lo que sobra pasa a una nota bajo la tabla.
LIMITE_PIE = 300   # caracteres de texto visible (unas tres líneas)


def _texto_visible(t):
    t = re.sub(r'\\(cite|cref|Cref|label|ref)\*?(\[[^\]]*\])?\{[^}]*\}', '[1]', t)
    t = re.sub(r'\\[a-zA-Z]+\*?', '', t)
    return re.sub(r'\s+', ' ', re.sub(r'[{}$\\~^_]', '', t))


def _frases(t):
    """Divide en frases por '. ' seguido de mayúscula, $, \\ o paréntesis, fuera de llaves."""
    frases, ini, prof = [], 0, 0
    for i, c in enumerate(t):
        prof += (c == '{') - (c == '}')
        if (c == '.' and prof == 0 and i + 2 < len(t) and t[i + 1] == ' '
                and re.match(r'[A-ZÁÉÍÓÚÑ$\\(]', t[i + 2])):
            frases.append(t[ini:i + 1])
            ini = i + 2
    frases.append(t[ini:])
    return [f for f in frases if f.strip()]


def partir_pie(caption):
    """Devuelve (pie, resto): el pie llega hasta la frase que dice si más alto o más bajo es mejor."""
    if len(_texto_visible(caption)) <= LIMITE_PIE:
        return caption, None
    frases = _frases(caption)
    n_pie = 1
    for i, f in enumerate(frases[:3]):
        if 'mejor' in f:
            n_pie = i + 1
            break
    if len(_texto_visible(' '.join(frases[:n_pie]))) > LIMITE_PIE:
        n_pie = 1
    resto = ' '.join(frases[n_pie:]).strip()
    return ' '.join(frases[:n_pie]), (resto or None)


def columnas_a_ancho(columnas):
    """Especificación de tabular* que reparte el espacio sobrante entre las columnas."""
    if columnas.startswith('@{}'):
        return '@{\\extracolsep{\\fill}}' + columnas[3:]
    return '@{\\extracolsep{\\fill}}' + columnas


def tabla(caption, label, columnas, cuerpo, tamano='\\small', sep=None, entorno='tabular', ancho=None,
          notas=None):
    caption, resto = partir_pie(caption)
    if resto:
        notas = resto + (' ' + notas if notas else '')
    l = ['\\begin{table}', '\\centering', tamano]
    if sep:
        l.append('\\setlength{\\tabcolsep}{%s}' % sep)
    l += ['\\caption{%s}' % caption, '\\label{%s}' % label]
    if entorno == 'tabularx':
        l.append('\\begin{tabularx}{%s}{%s}' % (ancho or '\\textwidth', columnas))
    else:
        entorno = 'tabular*'
        l.append('\\begin{tabular*}{\\linewidth}{%s}' % columnas_a_ancho(columnas))
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


def filas_familias(metodos_validos, fila_de, ncol, fila_media=None):
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
        if fila_media:
            cuerpo.append(fila_media(lista))
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


def media(filas, columnas):
    """Media aritmética de cada columna sobre los cinco modelos de MODELOS."""
    return {c: sum(float(filas[m][c]) for m in MODELOS) / len(MODELOS) for c in columnas}


def t09_agrupaciones(R, S):
    m5 = {f['modelo']: f for f in leer_csv(os.path.join(R, 'results_agrupaciones/metricas_5clases.csv'))
          if f['variante'] == 'a'}
    mb = {f['modelo']: f for f in leer_csv(os.path.join(R, 'results_agrupaciones/metricas_binario.csv'))
          if f['variante'] == 'pin_maligno'}
    cuerpo = ['\\toprule', '& \\multicolumn{2}{c}{5 categorías} & \\multicolumn{4}{c}{Binario} \\\\',
              '\\cmidrule(lr){2-3}\\cmidrule(lr){4-7}',
              'Modelo & Exactitud (\\%) & BA & Exactitud (\\%) & Sens. & Esp. & BA \\\\', '\\midrule']
    def fila(nombre, a, b):
        return '%s & %s & %s & %s & %s & %s & %s \\\\' % (
            nombre, pct(a['exactitud'], 2), n(a['balanced_accuracy']), pct(b['exactitud'], 2),
            n(b['sensibilidad_TPR']), n(b['especificidad_TNR']), n(b['balanced_accuracy']))

    for m, nombre in MODELOS.items():
        cuerpo.append(fila(nombre, m5[m], mb[m]))
    cuerpo += ['\\midrule', fila('Media (5 modelos)', media(m5, ['exactitud', 'balanced_accuracy']),
                                  media(mb, ['exactitud', 'sensibilidad_TPR', 'especificidad_TNR', 'balanced_accuracy']))]
    A = ARTICULO
    cuerpo += ['\\midrule', 'XCiT-M (artículo) & %s & -- & %s & %s & %s & %s \\\\' % (
        pct(A['acc_5'], 2), pct(A['acc_bin'], 2), n(A['tpr']), n(A['tnr']), n((A['tpr'] + A['tnr']) / 2)),
        '\\bottomrule']
    cap = ('Clasificación agrupada en el test ID a partir de las predicciones de 14 clases (más alto es mejor). '
           'Cinco categorías: NM (\\clase{No\\_Cancer}, estroma, glándulas no neoplásicas, inflamatorio), G3, G4, '
           'G5 y NT (PIN de alto grado, carcinoma intraductal, adenocarcinoma ductal). Binario: maligno = '
           'G3 + G4 + G5 + NT. Sens.: sensibilidad; Esp.: especificidad; BA: \\emph{balanced accuracy}. '
           'Referencia: XCiT-Medium del artículo del conjunto de datos~\\cite{ayensa2026}, con otro reparto de '
           'NM y NT (su BA se calcula como la media de Sens. y Esp.). Media: media aritmética de los cinco modelos.')
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
    mg = media(filas, ['sensibilidad_G3', 'sensibilidad_G4', 'sensibilidad_G5'])
    cuerpo += ['\\midrule', 'Media (5 modelos) & %s & %s & %s \\\\' % (
        n(mg['sensibilidad_G3']), n(mg['sensibilidad_G4']), n(mg['sensibilidad_G5']))]
    A = ARTICULO
    cuerpo += ['\\midrule', 'XCiT-M (artículo) & %s & %s & %s \\\\' % (n(A['G3']), n(A['G4']), n(A['G5'])),
               '\\bottomrule']
    cap = ('Sensibilidad de las categorías G3, G4 y G5 en el test ID (más alto es mejor). Son las categorías '
           'directamente comparables con el artículo del conjunto de datos~\\cite{ayensa2026}, porque coinciden '
           'en número de imágenes. Media: media aritmética de los cinco modelos.')
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
    cab = ' & '.join(CONJUNTOS[c] for c in conjuntos) + ' & Media'

    def valores(m, k):
        v = [float(datos[(m, c)][k]) for c in conjuntos]
        return v + [sum(v) / len(v)]

    def celdas(vals):
        return ' & '.join(n(x) for x in vals)

    def fila(m):
        return '%s & %s & %s \\\\' % (METODOS[m], celdas(valores(m, 'AUROC')), celdas(valores(m, 'FPR@95')))

    def fila_media(lista):
        med = {k: [sum(col) / len(lista) for col in zip(*(valores(m, k) for m in lista))]
               for k in ('AUROC', 'FPR@95')}
        return '\\textit{Media del grupo} & %s & %s \\\\' % (celdas(med['AUROC']), celdas(med['FPR@95']))

    cuerpo = ['\\toprule',
              '& \\multicolumn{6}{c}{\\AUROC $\\uparrow$} & \\multicolumn{6}{c}{\\FPRn{95} $\\downarrow$} \\\\',
              '\\cmidrule(lr){2-7}\\cmidrule(lr){8-13}', 'Método & %s & %s \\\\' % (cab, cab), '\\midrule']
    cuerpo += filas_familias(set(metodos), fila, 13, fila_media)
    cuerpo.append('\\bottomrule')
    cap = ('Control interno con las clases de \\nctcrc: tejido glandular de colon (TUM y NORM) frente a tejidos '
           'análogos a clases ID (STR, LYM y MUS). \\AUROC (más alto es mejor) y \\FPRn{95} (más bajo es mejor). '
           'Clase positiva: OOD. Media: media aritmética de los cinco conjuntos. Media del grupo: media '
           'aritmética de todas las filas del grupo. %s') % NOTA_MARCAS.replace('{acc_ash}', acc_ash(datos))
    escribir(S, 't10_control_interno.tex', tabla(cap, 'tab:ood-control-interno', 'l' + 'c' * 12, cuerpo,
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
            '$<0{,}001$' if p == 0 else n(p, 3)))
    cuerpo.append('\\bottomrule')
    cap = ('\\emph{Bootstrap} pareado (1.000 remuestreos, semilla 0) de la diferencia \\AUROC(RMDS) $-$ '
           '\\AUROC(método) en el near-OOD principal (TUM+NORM); RMDS es el método de referencia, por lo que no tiene fila propia. Diferencia positiva: RMDS es mejor. '
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


def tC_corr_k144(R, S):
    """FPR@95 y AUROC de STOOD-X (100 %) con K = 500 y K = 144 frente al mejor de los otros 13 detectores."""
    origen = CORR + '/stoodx_K144/comparacion_fpr95.csv'
    m = {(f['corrupcion'], f['nivel']): f for f in leer_csv(os.path.join(R, origen))}
    nombres = nombres_corr(R)
    assert len(m) == 27 and all((c, nv) in m for c in nombres for nv in ('1', '3', '5'))
    neg = lambda x, g: '\\textbf{%s}' % n(x) if g == 'True' else n(x)
    cuerpo = ['\\toprule',
              '& & \\multicolumn{3}{c}{\\FPRn{95} $\\downarrow$} & & \\multicolumn{2}{c}{\\AUROC\\ de \\stoodx $\\uparrow$} \\\\',
              '\\cmidrule(lr){3-5}\\cmidrule(lr){7-8}',
              'Corrupción & Nivel & $K=500$ & $K=144$ & Mejor otro & Detector & $K=500$ & $K=144$ \\\\', '\\midrule']
    for i, c in enumerate(nombres):
        if i:
            cuerpo.append('\\midrule')
        for j, nv in enumerate(('1', '3', '5')):
            f = m[(c, nv)]
            cuerpo.append('%s & %s & %s & %s & %s & %s & %s & %s \\\\' % (
                nombres[c] if j == 0 else '', nv, neg(f['FPR95_K500'], f['gana_K500']),
                neg(f['FPR95_K144'], f['gana_K144']), n(f['FPR95_mejor_otro']), nombre_det(f['mejor_otro']),
                n(f['AUROC_K500']), n(f['AUROC_K144'])))
    cuerpo.append('\\bottomrule')
    g500 = sum(f['gana_K500'] == 'True' for f in m.values())
    g144 = sum(f['gana_K144'] == 'True' for f in m.values())
    cap = ('\\FPRn{95} (más bajo es mejor) de \\stoodx (100\\,\\%% de las características) con $K=500$ y con $K=144$ '
           '(\\cref{sec:stoodx-seleccion-k}) en cada corrupción y nivel de severidad, frente al mejor de los otros 13 '
           'detectores en esa celda, y \\AUROC (más alto es mejor) de \\stoodx con ambos valores de $K$. ID: las '
           'imágenes limpias del test; OOD: sus versiones corruptas. En negrita, el \\FPRn{95} de \\stoodx cuando es '
           'menor que el del mejor otro detector (%d de 27 celdas con $K=500$ y %d con $K=144$). Sin IC.') % (g500, g144)
    escribir(S, 'tC_corr_k144.tex', tabla(cap, 'tab:apc-corr-k144', 'llcccccc', cuerpo, '\\scriptsize', '3pt'),
             origen + ' (fase8_stoodx_k.py)')


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
# Capítulo 11: detección OOD conforme (sección de STOOD-X)
# ---------------------------------------------------------------------------
def t11_ood_conforme(R, S):
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
    escribir(S, 't11_ood_conforme.tex', tabla(cap, 'tab:conforme-ood', 'llcccccc', cuerpo,
                                              '\\scriptsize', '3pt'),
             'results_conforme/deteccion_ood_conforme.csv')


# ---------------------------------------------------------------------------
# Capítulo 12: explicabilidad
# ---------------------------------------------------------------------------
CRP = 'results_crp'


def ic_tupla(texto, d=3, escala=1.0):
    """'(a, b)' de los CSV de results_crp -> [a; b]."""
    a, b = [float(v) * escala for v in texto.strip('()').split(',')]
    return ic(a, b, d)


def t12_controles(R, S):
    origen = CRP + '/explicaciones_f9/M/controles_resumen.csv'
    filas = {(f['metodo'], f['criterio']): f for f in leer_csv(os.path.join(R, origen))}
    cuerpo = ['\\toprule',
              'Método & Presencia & Diversidad & Aleatorización & Cobertura (\\%) & Suelo de ruido \\\\',
              '\\midrule']
    for m in ('A', 'EG'):
        for crit, nom in (('orig', 'original'), ('z', 'estandarizada')):
            f = filas[(m, crit)]
            suelo = '--' if not f['suelo_ruido_abs_rho'] else '%s %s' % (n(f['suelo_ruido_abs_rho']),
                                                                          ic_tupla(f['IC_suelo']))
            cuerpo.append('%s & %s & %s %s & %s %s & %s %s & %s \\\\' % (
                m if crit == 'orig' else '', nom,
                n(f['diversidad_abs_rho']), ic_tupla(f['IC_div']),
                n(f['ale_abs_rho']), ic(f['ale_min'], f['ale_max']),
                pct(f['cobertura_4'], 2), ic_tupla(f['IC_cob'], 2, 100), suelo))
        if m == 'A':
            cuerpo.append('\\midrule')
    cuerpo.append('\\bottomrule')
    cap = ('Controles de las explicaciones de ConvNeXt-S en el espacio M (16 casos, imagen y 3 vecinos, 4 canales), con la '
           'variante A de LRP y con EG condicionado. Diversidad: $|\\rho|$ media entre los 4 mapas de cada fila (mediana de '
           '64 filas; más bajo, mapas más distintos). Aleatorización: $|\\rho|$ con el mapa del modelo con la última etapa y '
           'la cabeza aleatorizadas (mediana de 5 sorteos [mín.; máx.]; más bajo, el mapa depende más de los pesos). '
           'Cobertura: fracción de la relevancia total que suman los 4 canales (la referencia uniforme es 0,52\\,\\%). '
           'Suelo de ruido: $|\\rho|$ entre las semillas 0 y 1 de EG (más alto, más reproducible). Intervalos del 95\\,\\% '
           'por bootstrap.')
    escribir(S, 't12_controles.tex', tabla(cap, 'tab:xai-controles', 'llcccc', cuerpo, '\\scriptsize', '3pt'), origen)


def t12_ablacion(R, S):
    origen = CRP + '/fase10_eg/tabla/t3_ablacion.csv'
    filas = {(f['variante'], f['k'], f['metodo']): f for f in leer_csv(os.path.join(R, origen))}
    cuerpo = ['\\toprule', 'Sustitución & $k$ & A & EG & G$\\times$E & Azar \\\\', '\\midrule']
    for var, nom in (('media_train', 'media de train'), ('cero', 'cero')):
        for k in ('1', '3', '5', '10'):
            celdas = []
            for m in ('A', 'EG', 'G×E'):
                f = filas[(var, k, m)]
                celdas.append('%s %s' % (n(f['caida_media']), ic(f['IC_inf'], f['IC_sup'])))
            azar = float(filas[(var, k, 'A')]['caida_azar'])
            cuerpo.append('%s & %s & %s & %s \\\\' % (nom if k == '1' else '', k, ' & '.join(celdas),
                                                       ('$-$' + n(-azar)) if azar < 0 else n(azar)))
        if var == 'media_train':
            cuerpo.append('\\midrule')
    cuerpo.append('\\bottomrule')
    cap = ('Ablación de conceptos en ConvNeXt-S (112 imágenes de test): caída media de la salida de la clase $f_c$ al '
           'sustituir los $k$ canales más relevantes de la salida del último bloque (768 canales) según cada método (por la media de train o por '
           'cero), con intervalo del 95\\,\\% por bootstrap. Más alto: los canales elegidos pesan más en la predicción. '
           'Azar: media de 10 sorteos de $k$ canales.')
    escribir(S, 't12_ablacion.tex', tabla(cap, 'tab:xai-ablacion', 'llcccc', cuerpo, '\\scriptsize', '3pt'), origen)


def t12_atlas(R, S):
    F10 = CRP + '/fase10_eg'
    est = leer_json(os.path.join(R, F10, 'paso4/muestra/resultados/estabilidad_resumen.json'))
    pur = {f['medida']: f for f in leer_csv(os.path.join(R, F10, 'tabla/t7_atlas_pureza.csv'))}
    sem = {(f['medida'], f['fila']): f for f in leer_csv(os.path.join(R, F10, 'comprobaciones_finales/pureza_semillas.csv'))}
    sref = {f['canales']: f for f in leer_csv(os.path.join(R, F10, 'tabla/t7_atlas_solape_referencias.csv'))}
    scon = leer_csv(os.path.join(R, F10, 'tabla/t6_atlas_solape_conceptos.csv'))
    kc, km = [k for k in pur if k.startswith('Pureza de clase')][0], [k for k in pur if k.startswith('Pureza de la clase')][0]
    cuerpo = ['\\toprule', 'Atlas & Clase del concepto & Clase mayoritaria \\\\', '\\midrule']
    for nom, col, fila in (('EG, muestra, semilla 0', 'EG (muestra)', None), ('EG, muestra, semilla 1', None, 'EG semilla 1'),
                           ('A, muestra', 'A (muestra)', None), ('A, train completo', 'A (fase 4, train completo)', None),
                           ('G$\\times$E, train completo', 'GxE (fase 4, train completo)', None)):
        if fila:
            v = (sem[('pureza_concepto', fila)]['mediana'], sem[('pureza_mayoritaria', fila)]['mediana'])
        else:
            v = (pur[kc][col], pur[km][col])
        cuerpo.append('%s & %s & %s \\\\' % (nom, n(v[0]), n(v[1])))
    cuerpo += ['\\midrule', '\\multicolumn{3}{@{}l}{\\textit{Estabilidad de EG entre semillas (%d canales concepto)}} \\\\' % est['conceptos'],
               'Referencias comunes del top-8, mediana [mín.; máx.] & \\multicolumn{2}{c}{%s [%d; %d]} \\\\' % (
                   n(est['solape_mediana'], 0), est['solape_min'], est['solape_max']),
               'Conceptos con solape bajo ($\\le 4$ de 8) & \\multicolumn{2}{c}{%d de %d} \\\\' % (est['n_bajo_le4'], est['conceptos']),
               'Spearman en las 50 candidatas, mediana & \\multicolumn{2}{c}{%s} \\\\' % n(est['spearman_mediana']),
               '\\midrule', '\\multicolumn{3}{@{}l}{\\textit{Solapes}} \\\\',
               'Conceptos comunes EG y A (de 56) & \\multicolumn{2}{c}{%d} \\\\' % sum(int(f['EG_y_A']) for f in scon),
               'Referencias comunes EG y A (de 8, media) & \\multicolumn{2}{c}{%s} \\\\' % n(sref['concepto']['EGm_y_Am'], 2),
               'Referencias comunes A muestra y A train completo (de 8, media) & \\multicolumn{2}{c}{%s} \\\\' % n(sref['concepto']['Am_y_A4'], 2),
               '\\bottomrule']
    cap = ('Atlas RelMax de ConvNeXt-S (4 conceptos por clase y 8 referencias por concepto). Pureza: mediana de la fracción '
           'de las 8 referencias que son de la clase del concepto o de su clase mayoritaria (más alto, referencias más '
           'homogéneas). Muestra: muestra estratificada del train (5\\,\\% por clase, mínimo 50; 4.654 imágenes). Con la '
           'semilla 1, el top-8 se elige entre las 50 candidatas de la semilla 0. Los solapes de referencias se dan en los '
           'canales concepto.')
    escribir(S, 't12_atlas.tex', tabla(cap, 'tab:xai-atlas', 'lcc', cuerpo, '\\small'),
             F10 + '/{paso4/muestra/resultados,tabla,comprobaciones_finales}')


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

    nota = ('(a) \\AUROC con el control de 128\\,px como clase '
            'negativa y PANDA como positiva: por encima de 0,5, la puntuación coloca PANDA como más OOD que el control; '
            'ConvNeXt-S en el espacio M. %s %s (b) Porcentaje de imágenes con la puntuación $-z$ de \\stoodx ($K=500$) '
            'saturada ($U=n_1n_2$) en cada espacio de ConvNeXt-S; en C solo se calculó en el test ID, TUM y NORM.') % (
                NOTA_BOOT.replace(' Clase positiva: OOD.', ''), NOTA_B.split(' KNN,')[0])
    l = ['\\begin{table}', '\\centering', '\\footnotesize', '\\setlength{\\tabcolsep}{4pt}',
         '\\caption{\\stoodx y la saturación con los dos modelos.}', '\\label{tab:convnext-stoodx}', '',
         '\\textit{(a) PANDA frente al control}\\par\\smallskip',
         '\\begin{tabular*}{\\linewidth}{@{\\extracolsep{\\fill}}lcc}', '\\toprule', 'Método & Swin-S & ConvNeXt-S \\\\', '\\midrule']
    l += filas_familias(set(METODOS_CNX), fila_pv, 3)
    l += ['\\bottomrule', '\\end{tabular*}', '', '\\bigskip',
          '\\textit{(b) Imágenes saturadas}\\par\\smallskip',
          '\\begin{tabular*}{\\linewidth}{@{\\extracolsep{\\fill}}lcccc}', '\\toprule',
          'Conjunto & Swin-S & ConvNeXt-S (M) & ConvNeXt-S (B) & ConvNeXt-S (C) \\\\', '\\midrule']
    for c, nombre in [('id_test', 'Test ID')] + list(CONJUNTOS.items()):
        celdas = [sat.get(k) for k in [('swin', '-', c), ('convnext', 'M', c), ('convnext', 'B', c),
                                       ('convnext', 'C', c)]]
        l.append('%s & %s \\\\' % (nombre, ' & '.join(pct(f['frac_saturadas']) + '\\,\\%' if f else '--'
                                                         for f in celdas)))
    l += ['\\bottomrule', '\\end{tabular*}', '', '\\smallskip', '\\parbox{\\linewidth}{\\scriptsize %s}' % nota,
          '\\end{table}']
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

    t11_stoodx(R, S, datos)
    t11_barrido_k(R, S)
    t11_seleccion_k(R, S)
    t11_k144_vs_k500(R, S)
    t11_calibracion(R, S)
    t11_saturacion(R, S)
    t11_saturacion(R, S, FASE_B_K144, 144, 't11_saturacion_k144.tex', 'tab:stoodx-saturacion-k144')

    t11_ood_conforme(R, S)


    t12_controles(R, S)
    t12_ablacion(R, S)
    t12_atlas(R, S)

    tA_aupr(R, S, datos, 'AUPR_In', 'tA_aupr_in.tex', 'tab:aupr-in', '\\AUPRin (clase positiva: ID)')
    tA_aupr(R, S, datos, 'AUPR_Out', 'tA_aupr_out.tex', 'tab:aupr-out', '\\AUPRout (clase positiva: OOD)')

    tC_corr_completa(R, S, 'AUROC', 'tC_corr_auroc.tex', 'tab:apc-corr-auroc', '\\AUROC (más alto es mejor)')
    tC_corr_completa(R, S, 'FPR95', 'tC_corr_fpr95.tex', 'tab:apc-corr-fpr95', '\\FPRn{95} (más bajo es mejor)')
    tC_corr_k144(R, S)

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
