#!/usr/bin/env python3
"""Planificación económica del TFG (sección de planificación del capítulo 1).

Calcula las partidas de coste, imprime la tabla y escribe tablas/t01_costes.tex.
Solo usa la biblioteca estándar. Uso (desde la raíz del repositorio):
    python3 scripts/costes_tfg.py

Precios verificados el 21/11/2026 (fuentes en library.bib, entradas precio*).
Horas de cómputo medidas con
    sacct -u slcerro -S 2026-03-01 -X -P --format=JobID,JobName,Start,End,ElapsedRaw,NodeList,AllocTRES,State
el 21/11/2026 (271 trabajos, incluidos los fallidos y cancelados; ninguno entre abril y septiembre).
"""
import os

# ---------------------------------------------------------------------------
# Personal (autor)
# ---------------------------------------------------------------------------
HORAS_AUTOR = 17 * 8 + 12 * 22          # mar-jun (dedicación parcial) + sep-nov
SALARIO_BRUTO = 35534.0                 # Payscale 2026, ML Engineer, inicio de carrera, España
COTIZACION = {                          # Orden PJC/297/2026 (cotización empresarial)
    'contingencias comunes': 0.2360,
    'desempleo (indefinido)': 0.0550,
    'FOGASA': 0.0020,
    'formación profesional': 0.0060,
    'MEI': 0.0075,
}
AT_EP = 0.0150                          # tarifa de primas, trabajo de oficina (por confirmar)
JORNADA_ANUAL = 1800.0                  # horas/año de referencia (por confirmar la fuente)

# ---------------------------------------------------------------------------
# Hardware
# ---------------------------------------------------------------------------
PORTATIL = 666.04                       # HP Pavilion x360 14-dw0028ns, con IVA
VIDA_UTIL = 4.0                         # años (Guía TFG, § 6.3.1)
MESES_USO = 4 + 2.8                     # mar-jun + sep-24 nov
USD_POR_EUR = 1.0968                    # Banco de España, 18/11/2026 (BOE-A-2026-24272)

# Horas de clúster por tipo (sacct). Todas las GPU usadas (TITAN Xp en atenea y titan, RTX 2080 Ti
# en zeus, Quadro RTX 8000 en dionisio, hera) son Pascal/Turing: se valoran con g4dn.xlarge (T4).
# Ninguna es de clase V100 o superior, así que p3.2xlarge no se usa.
HORAS_GPU = {'entrenamiento de los 5 modelos': 112.86,
             'inferencia y evaluación OOD': 7.71,
             'explicabilidad (LRP/CRP, EG)': 53.70}
HORAS_CPU = 29.28                       # corrupciones, ConvNeXt-S en CPU y pruebas de LRP (12 núcleos)
PRECIO_GPU_USD = 0.526                  # g4dn.xlarge bajo demanda, us-east-1, Linux
PRECIO_CPU_USD = 0.68                   # c6i.4xlarge (16 vCPU), us-east-1, Linux

# ---------------------------------------------------------------------------
# Bibliografía (coste evitado por la suscripción de la Biblioteca de la UGR)
# Clasificación por DOI o revista de las entradas de library.bib (artículos y capítulos).
# Acceso abierto (0 €): arXiv, NeurIPS, ICLR, ICML/PMLR, JMLR, DMLR, CVF (CVPR, ICCV, CVPRW),
# PLOS, Nature Communications, Scientific Reports, MDPI, SciELO, tesis y material docente.
# ---------------------------------------------------------------------------
PAGO = {
    'Elsevier': (31.50, ['sevillano2026', 'fawcett2006', 'montavon2017', 'montavon2018',
                         'barredo2020', 'linmans2023', 'hornik1989multilayer', 'leshno1993multilayer']),
    'Springer': (39.95, ['yang2024', 'ming2024finetuning', 'mcnemar1947', 'zhang2018excitation',
                         'cybenko1989approximation', 'sun2022dice', 'zhang2016excitation',
                         'huibinder2019', 'montavon2019lrp']),
    # Sin precio verificado: 31,50 USD como referencia conservadora.
    'IEEE (fuera de CVF)': (31.50, ['zimmerer2022', 'ruff2021', 'ayensa2026', 'macenko2009',
                                    'todi2023convnext', 'landecker2013', 'motzkus2022']),
    'Otras editoriales': (31.50, ['pang2020', 'mann1947', 'wilcoxon1945', 'efron1979', 'virtanen2020',
                                  'achtibat2023', 'bulten2022', 'schomig2021', 'pinkus1999approximation',
                                  'wilk1968', 'lilliefors1967', 'dunn1961']),
}

# Libros: consultados en la Biblioteca de la UGR o en línea, sin coste. Estimación del autor
# (21/11/2026): unos 40 € por libro para los 3 más usados.
LIBROS_N = 3
LIBROS_PRECIO_EUR = 40.0

INDIRECTOS = 0.10                       # Guía TFG, § 6.3


def calcular():
    coste_hora = SALARIO_BRUTO * (1 + sum(COTIZACION.values()) + AT_EP) / JORNADA_ANUAL
    personal = HORAS_AUTOR * coste_hora
    portatil = PORTATIL / VIDA_UTIL * (MESES_USO / 12)
    gpu_h = sum(HORAS_GPU.values())
    cluster = (gpu_h * PRECIO_GPU_USD + HORAS_CPU * PRECIO_CPU_USD) / USD_POR_EUR
    biblio = {k: (len(v), p, len(v) * p / USD_POR_EUR) for k, (p, v) in PAGO.items()}
    libros = LIBROS_N * LIBROS_PRECIO_EUR
    biblio_total = sum(x[2] for x in biblio.values()) + libros
    sin_cluster = personal + portatil + biblio_total
    con_cluster = sin_cluster + cluster
    return dict(libros=libros, coste_hora=coste_hora, personal=personal, portatil=portatil, gpu_h=gpu_h,
                cluster=cluster, biblio=biblio, biblio_total=biblio_total,
                total_con=con_cluster * (1 + INDIRECTOS), total_sin=sin_cluster * (1 + INDIRECTOS),
                ind_con=con_cluster * INDIRECTOS, ind_sin=sin_cluster * INDIRECTOS)


def eur(x):
    """1234.5 -> '1.234,50' (formato español)."""
    s = f'{x:,.2f}'
    return s.replace(',', 'X').replace('.', ',').replace('X', '.')


def num(x, d=2):
    return f'{x:.{d}f}'.replace('.', ',')


def tabla_latex(r):
    cot = sum(COTIZACION.values())
    filas = [
        ('Personal (autor)',
         f'{HORAS_AUTOR}\\,h $\\times$ {num(r["coste_hora"])}\\,€/h '
         f'(\\num{{35534}}\\,€ $\\times$ (1 + {num(100 * cot)}\\,\\% + {num(100 * AT_EP)}\\,\\%) / \\num{{1800}}\\,h)',
         r['personal']),
        ('Portátil',
         f'{num(PORTATIL)}\\,€ / {VIDA_UTIL:.0f} años $\\times$ {num(MESES_USO, 1)}/12 años',
         r['portatil']),
        ('Clúster de GPU (precio de mercado)',
         f'{num(r["gpu_h"])}\\,h GPU $\\times$ {num(PRECIO_GPU_USD, 3)}\\,USD/h + '
         f'{num(HORAS_CPU)}\\,h CPU $\\times$ {num(PRECIO_CPU_USD)}\\,USD/h; {num(USD_POR_EUR, 4)}\\,USD/€',
         r['cluster']),
        ('Software', 'Libre o de código abierto', 0.0),
    ]
    for k, (n, p, e) in r['biblio'].items():
        filas.append((f'Bibliografía: {k}', f'{n} $\\times$ {num(p)}\\,USD', e))
    lineas = [
        '% Generado por scripts/costes_tfg.py: no editar a mano.',
        '\\begin{table}[tbp]',
        '\\centering',
        '\\footnotesize',
        '\\caption{Planificación económica del TFG: partidas, cálculo y coste en euros. Precios '
        'verificados el 21/11/2026. El clúster se valora a precio de alquiler en la nube; para la UGR '
        'no tuvo coste. La bibliografía es un coste evitado gracias a la suscripción de la Biblioteca '
        'de la UGR.}',
        '\\label{tab:costes}',
        '\\begin{tabularx}{\\textwidth}{@{}>{\\raggedright\\arraybackslash}p{0.27\\textwidth}'
        '>{\\raggedright\\arraybackslash}X r@{}}',
        '\\toprule',
        'Partida & Cálculo & Coste (€) \\\\',
        '\\midrule',
    ]
    for a, b, c in filas:
        lineas.append(f'{a} & {b} & {eur(c)} \\\\')
    lineas += [
        f'Bibliografía: libros & {LIBROS_N} libros $\\times$ {num(LIBROS_PRECIO_EUR)}\\,€ (estimación) & '
        f'{eur(r["libros"])} \\\\',
        'Despliegue y mantenimiento & No aplica & 0,00 \\\\',
        f'Costes indirectos (con clúster) & {INDIRECTOS * 100:.0f}\\,\\% del subtotal & {eur(r["ind_con"])} \\\\',
        '\\midrule',
        f'\\textbf{{Total con el clúster a precio de mercado}} & & \\textbf{{{eur(r["total_con"])}}} \\\\',
        f'\\textbf{{Total sin el clúster}} (indirectos: {eur(r["ind_sin"])}\\,€) & & '
        f'\\textbf{{{eur(r["total_sin"])}}} \\\\',
        '\\bottomrule',
        '\\end{tabularx}',
        '\\end{table}',
    ]
    return '\n'.join(lineas) + '\n'


def main():
    r = calcular()
    # Autocomprobaciones
    assert HORAS_AUTOR == 400
    assert abs(sum(COTIZACION.values()) - 0.3065) < 1e-12
    assert 25 < r['coste_hora'] < 27
    assert abs(r['total_con'] - r['total_sin'] - r['cluster'] * (1 + INDIRECTOS)) < 1e-6
    assert len({k for _, v in PAGO.values() for k in v}) == sum(len(v) for _, v in PAGO.values())

    print(f'Coste por hora del autor: {r["coste_hora"]:.2f} €/h')
    print(f'Personal: {r["personal"]:.2f} €')
    print(f'Portátil: {r["portatil"]:.2f} €')
    print(f'Clúster: {r["gpu_h"]:.2f} h GPU + {HORAS_CPU:.2f} h CPU = {r["cluster"]:.2f} €')
    for k, (n, p, e) in r['biblio'].items():
        print(f'Bibliografía {k}: {n} x {p} USD = {e:.2f} €')
    print(f'Bibliografía libros: {LIBROS_N} x {LIBROS_PRECIO_EUR} € = {r["libros"]:.2f} €')
    print(f'Bibliografía total: {r["biblio_total"]:.2f} €')
    print(f'Indirectos: {r["ind_con"]:.2f} € (con clúster), {r["ind_sin"]:.2f} € (sin clúster)')
    print(f'Total con clúster: {r["total_con"]:.2f} €; sin clúster: {r["total_sin"]:.2f} €')

    salida = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tablas', 't01_costes.tex')
    with open(salida, 'w', encoding='utf-8') as f:
        f.write(tabla_latex(r))
    print(f'Escrito {os.path.normpath(salida)}')


if __name__ == '__main__':
    main()
