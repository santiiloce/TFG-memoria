# AGENTS.md — Memoria del TFG

TFG de Santiago López Cerro (Doble Grado en Ingeniería Informática y Matemáticas, Universidad de Granada), tutorizado por Francisco Herrera Triguero e Iván Sevillano García: **detección de datos fuera de distribución (OOD) y explicabilidad en la clasificación de imágenes histopatológicas de próstata**. El tutor ha pedido reforzar la parte matemática.

Plantilla oficial https://github.com/latex-mat-ugr/Plantilla-TFG: clase `ugrTFG.cls` (basada en `scrbook`), **pdflatex**, BibTeX con `plain-es` (citas numéricas). Compilación: `latexmk -pdf tfg.tex`.

## Reglas obligatorias

1. **No inventar nada**: ni cifras, ni resultados, ni referencias, ni afirmaciones técnicas. Cada número sale de las notas del autor (`notas/memoria2-pandoc.tex`) o de los ficheros de resultados; si hay discrepancia, manda el fichero de resultados y se marca con `\revisar{}`. Si falta algo, `\pendiente{...}`.
2. **El texto es del autor.** Se transcribe y reorganiza su redacción, sin reescribirla con otro estilo. Se pueden corregir ortografía, erratas y concordancias. Cualquier cambio de contenido, por pequeño que sea, se marca con `\revisar{qué se cambió y por qué}`.
3. **No se redacta prosa nueva en la memoria**: ni introducciones, conclusiones, análisis, definiciones ni demostraciones. Lo que el autor no haya escrito queda como esqueleto: título, `\pendiente{}` y los puntos y cifras en comentarios LaTeX (`%`).
4. **Fuera del repositorio solo se lee.** Nunca escribir, mover ni borrar nada en `/mnt/homeGPU/slcerro/tfg-referencias/`, `/mnt/homeGPU/slcerro/tfg/executions/`, `/mnt/homeGPU/slcerro/OpenOOD/` ni, sobre todo, en `/mnt/homeGPU/slcerro/TrainTest` (enlace de solo lectura a datos del tutor). Las figuras se **copian** a `img/` dentro del repo.
5. **Git:** no hacer commits ni push, ni ningún comando que modifique el historial de git (los commits los hace el autor). Al terminar cada tarea, dar la salida de `git status --short` y un mensaje de commit propuesto en una línea, sin trailers (ni Co-Authored-By ni similares). La atribución automática está desactivada en `.claude/settings.json` (`"attribution": {"commit": "", "pr": ""}`): ningún commit ni PR debe llevar la línea `Co-Authored-By` ni la firma «Generated with Claude Code».
6. **Compilación:** al terminar cada tarea, el documento compila sin errores con `latexmk -pdf tfg.tex`.
7. Ante una duda que cambie la estructura, parar y preguntar.

Además:

- Los pasajes de las notas traducidos casi literalmente de otras fuentes se marcan con `\revisar{traducción casi literal; parafrasear y citar}`. **No los parafrasea el agente**: los reescribe el autor.
- Los `resumen.md`, `analisis.md` y demás documentos de `OpenOOD/results_*` **no son texto del autor**: sus cifras pueden ir en comentarios `%`, pero su prosa no se copia a la memoria.
- La exactitud del Swin-S en toda la memoria es **0,9688 [0,9658; 0,9717]** (`results_fase1`). Diferencia Swin − ConvNeXt: **+0,0020**, no significativa (McNemar p = 0,19).
- El título está registrado: **no se cambia**.
- Pasajes que comparen el artículo de STOOD-X con su implementación pública (Iván Sevillano es primer autor): tono neutro y descriptivo, marcados con `\revisar{tono}`.

## Convenciones

- **Etiquetas:** `cap:`, `sec:`, `fig:`, `tab:`, `eq:`, `def:`, `teo:`. Referencias siempre con `\cref`.
- **Cifras:** coma decimal; intervalos de confianza como [0,9658; 0,9717].
- **Nombres:** clases del dataset, métodos y conjuntos de datos con formato consistente (macros en `preambulo-propio.tex`: `\clase{}`, `\stoodx`, `\nctcrc`, `\AUROC`, `\FPRn{95}`, `\CCRn{5}`...). Las macros de notación se definen una sola vez, en `preambulo-propio.tex`.
- **Términos en inglés** sin traducción consolidada: en cursiva la primera vez, con su acrónimo.
- **Formato:** nada de `\\` para separar párrafos ni `\vspace` manuales. Un fichero por capítulo, con `% !TeX root = ../tfg.tex` en la cabecera.
- Marcas: `\pendiente{}` (rojo) y `\revisar{}` (naranja); el interruptor `\borradorfalse` de `preambulo-propio.tex` las oculta en la versión final.
- Flotantes con `[tbp]`, colocados en el código justo después del párrafo que los cita (o del primer párrafo de su sección si nadie los cita), para no dejar páginas de flotantes medio vacías.
- Las matrices de confusión de 14 clases ocupan el ancho completo de texto. En el capítulo 11 solo va la figura de imágenes de colon aceptadas como ID; el resto de ejemplos de STOOD-X (también los de $K_c$) está en el apéndice C.
- Figuras de otros autores: "Fuente: …" en el caption. Figuras extraídas del .docx: `\revisar{figura extraída del docx, regenerar}`.
- Tablas generadas por `scripts/generar_tablas.py` a partir de `OpenOOD/results_*` (salida en `tablas/`); no editar a mano las tablas generadas: se cambia el script y se vuelve a ejecutar. Cada `\caption` dice qué se mide y si más alto es mejor.

## Estructura

Frontmatter: declaración de originalidad, dedicatoria, agradecimientos, índice de acrónimos (`preliminares/acronimos.tex`), summary (inglés, 800–1500 palabras), resumen, índice.

- **Parte I. Introducción y estado del arte:** 1 Introducción; 2 Estado del arte.
- **Parte II. Fundamentos matemáticos:** 3 Aprendizaje supervisado y redes profundas; 4 Formalización de la detección OOD y métricas; 5 Métodos de detección post hoc; 6 Inferencia estadística; 7 Explicabilidad.
- **Parte III. Experimentación, resultados y discusión:** 8 Materiales y métodos; 9 Clasificación ID; 10 Detección OOD; 11 STOOD-X; 12 Predicción conforme; 13 Fuga por lámina; 14 Explicabilidad y eliminación de sesgos.
- **Parte IV. Conclusiones y trabajo futuro:** 15 Conclusiones y trabajo futuro.
- **Apéndices:** A Tablas de AUPR-In y AUPR-Out; B Anexo NCT-CRC (ADI, BACK, DEB, MUC); C Material complementario.

Ficheros: `capitulos/NN-nombre.tex`, `apendices/X-nombre.tex`, figuras en `img/<capitulo>/`, tablas en `tablas/`.

## Estructura de los capítulos de resultados (9 a 12)

- No se ponen todas las tablas juntas. Cada sección sigue el patrón **tabla o figura → análisis breve de esa tabla → conclusión parcial**.
- Debajo de cada tabla va el párrafo de análisis del autor que le corresponde. Donde falte, `\pendiente{análisis}` con las cifras clave en comentarios `%`.
- Cada capítulo termina con una sección de **discusión global** que integra las conclusiones parciales.
- Capítulo 10: la tabla principal OOD se divide en una tabla por bloque: near-OOD principal (TUM+NORM); control interno (TUM, NORM, STR, LYM, MUS: tabla compacta de AUROC y FPR@95, más `fig5_control_interno_nct`); cambio de centro y resolución (PANDA frente al control, más `fig4_panda_vs_control`); far-OOD (DTD); comparación de familias de métodos (logits y modificación de activaciones). El párrafo «Conclusión» del autor abre la discusión global.
- Al apéndice solo van las tablas de AUPR-In/AUPR-Out y el anexo NCT-CRC (ADI, BACK, DEB, MUC).

## Material de entrada (solo lectura)

- Notas del autor: `notas/memoria2-pandoc.tex` (conversión de `tfg-referencias/Memoria-2.docx`); `notas/` no se compila.
- Curvas y matrices de confusión: `tfg/executions/def1/param0..4` (0 ViT-B/16, 1 ResNet-50, 2 ConvNeXt-S, 3 EfficientNetV2-S, 4 Swin-S).
- Resultados: `OpenOOD/results_fase1`, `results_agrupaciones`, `results_ood` (fase C y `memoria/figuras.md` para captions), `results_ood_laminas`, `results_integridad`, `results_conforme` (y `mondrian/`).
- Artículos de referencia en `OpenOOD/docs/` (Yang et al. 2024, STOOD-X, artículo del dataset).
