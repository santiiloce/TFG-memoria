# Estado de la memoria (borrador del 26/10/2026)

Compila sin errores con `latexmk -pdf tfg.tex` (108 páginas en total). No hay referencias ni citas sin definir. Las marcas `\pendiente` (rojo) y `\revisar` (naranja) se ocultan con `\borradorfalse` en `preambulo-propio.tex`.

## Secciones con contenido y secciones en esqueleto

Palabras de prosa del autor por capítulo (sin comentarios, marcas, tablas, figuras ni entornos de teorema):

| Capítulo | Prosa | Estado |
|---|---|---|
| Preliminares (agradecimientos, summary, resumen) | 0 | Esqueleto. Hecho: índice de acrónimos. |
| 1. Introducción | 0 | Esqueleto completo: contexto, problema, motivación, preguntas e hipótesis, objetivos, fuentes, estructura, Gantt y costes. |
| 2. Estado del arte | 600 | Con contenido: taxonomía (con la figura de Yang et al.), criterio conservador, métodos excluidos y explicabilidad. Esqueleto: histopatología, near/far-OOD, Clever Hans, CRP glocal. |
| 3. Aprendizaje supervisado | 0 | Esqueleto con entornos `definicion`/`proposicion`/`demostracion`. |
| 4. Formalización OOD y métricas | 348 | Descripción informal de las métricas (de las notas). Definiciones y teoremas en esqueleto (AUROC = P(...) = U/(n₁n₂), etc.). |
| 5. Métodos post hoc | 824 | Descripción de los grupos 1–3 y de STOOD-X (de las notas). Definiciones formales en esqueleto. |
| 6. Inferencia estadística | 31 | Esqueleto: Mann-Whitney, bootstrap y McNemar, predicción conforme (teorema de cobertura, APS/LAC, Mondrian). |
| 7. Explicabilidad (LRP, CRP) | 0 | Esqueleto. |
| 8. Materiales y métodos | 989 | Con contenido: conjunto ID, partición, conjuntos OOD, NCT-CRC, PANDA, DataLoader y Learner. Esqueleto: integridad, control/DTD, entorno, configuración del entrenamiento. |
| 9. Clasificación ID | 302 | Tablas y figuras de los cinco modelos y elección del Swin (texto de las notas, con marcas). Esqueleto: análisis de cada tabla, agrupaciones y discusión. |
| 10. Detección OOD | 740 | Con contenido: cinco bloques con tabla, figura y análisis de las notas; «Conclusión» abre la discusión. Pendientes: conclusiones parciales e integración. |
| 11. STOOD-X | 539 | Con contenido: configuración, puntuación, resultados, calibración, sensibilidad a K y ejemplos. Pendientes: diferencias con la implementación pública, conclusiones parciales y discusión. |
| 12. Predicción conforme | 0 | Esqueleto con tablas y figuras y las cifras en comentarios. |
| 13. Fuga por lámina | 0 | Esqueleto con tablas y figuras y las cifras en comentarios. |
| 14. Explicabilidad y sesgos | 0 | Esqueleto (en desarrollo). |
| 15. Conclusiones | 25 | Solo la frase de limitaciones de las notas; resto en esqueleto. |
| Apéndice A (AUPR) | — | Tablas completas. |
| Apéndice B (anexo NCT) | — | Tabla completa; falta el texto. |
| Apéndice C | — | Esqueleto. |

## Figuras que hay que regenerar

Extraídas del .docx; solo existen allí:

- `img/cap08/docx_image10.png`, `docx_image11.png`: adenocarcinoma colorrectal frente a ductal ID (`fig:nct-tum-vs-id`).
- `img/cap08/docx_image12.png`, `docx_image13.png`: STR y LYM (`fig:nct-str-lym`).
- `img/cap08/docx_image6.png`, `docx_image17.png`: PANDA frente a ID (`fig:panda-vs-id`).

El resto de las figuras son copias de los originales (`tfg/executions/def1/param*` y `OpenOOD/results_*`). La figura de taxonomía es la **figura 2** de Yang et al. (no la 1), recortada del PDF de `OpenOOD/docs/`. Los ejemplos de STOOD-X se han convertido de PNG a JPEG (calidad 90) para reducir el tamaño.

## Referencias marcadas `VERIFICAR` (`library.bib`)

- `openood15`: decidir si se cita OpenOOD v1.5 o la versión de 2022 (`openood`), según el commit usado (3c35632).
- `vovk2005`: Crossref no da los autores de la 1.ª edición; se han tomado de la 2.ª (2022).
- `wilcoxon1945`: Crossref solo da la página inicial (80).
- `storas2025`: confirmar que es el artículo al que se refieren las notas; falta el número de artículo.

Otras observaciones de la bibliografía:

- STOOD-X se publicó en *Pattern Recognition* 177 (2026): clave `sevillano2026`. El artículo del conjunto de datos, en IEEE CAI 2026: clave `ayensa2026`.
- Pang et al. se publicó en 2021 (las notas dicen 2020).
- La sede de los artículos de congresos sin DOI (NeurIPS, ICLR, ICML) sale del comentario de los autores en arXiv. No se han añadido volúmenes ni páginas que no estuvieran confirmados.
- Se ha añadido `macenko2009` (DOI enlazado en las notas) y `kather2018` (registro de Zenodo del conjunto NCT-CRC).

## Dudas abiertas

1. Fuente de los parches de 128 px de PANDA (conjunto de Kaggle `panda-16x128x128-tiles-data`): cómo citarla.
2. Dónde citar Zhang et al. (2021) y Fang et al. (2022), que aparecen en la lista de referencias pero no en el texto.
3. Si se cita a Micikevicius et al. (2018) para la precisión mixta.
4. Artículos originales de KNN, RMDS, ViM y SHE: no aparecen en las notas ni en la lista; ¿se añaden?
5. Contenido del apéndice C (material complementario).
6. Gantt: `pgfgantt` ya está cargado; faltan las fechas.
7. Para compilar se han instalado en el TeX Live del usuario (`~/texlive/2026`) los paquetes `siunitx`, `cleveref`, `multirow` y `pgfgantt`.

## Tablas

Se generan con `python3 scripts/generar_tablas.py` a partir de `OpenOOD/results_*` (solo lectura). No hay que editarlas a mano.

## Marcas en el texto

### \pendiente

- `preliminares/agradecimientos.tex:10` — agradecimientos
- `preliminares/resumen.tex:16` — resumen en castellano
- `preliminares/summary.tex:24` — summary en inglés (800--1500 palabras)
- `capitulos/01-introduccion.tex:21` — contexto
- `capitulos/01-introduccion.tex:31` — descripción del problema
- `capitulos/01-introduccion.tex:41` — motivación
- `capitulos/01-introduccion.tex:53` — preguntas de investigación e hipótesis
- `capitulos/01-introduccion.tex:63` — objetivos generales
- `capitulos/01-introduccion.tex:76` — objetivos específicos y grado de consecución
- `capitulos/01-introduccion.tex:86` — principales fuentes consultadas
- `capitulos/01-introduccion.tex:91` — estructura de la memoria
- `capitulos/01-introduccion.tex:102` — planificación temporal y diagrama de Gantt
- `capitulos/01-introduccion.tex:109` — planificación económica
- `capitulos/02-estado-arte.tex:19` — estado del arte de la clasificación histopatológica
- `capitulos/02-estado-arte.tex:27` — presentación de la taxonomía de Yang et al.~\cite{yang2024}
- `capitulos/02-estado-arte.tex:42` — situar el trabajo en la subtarea (d) de la \cref{fig:taxonomia-yang} y justificar la inclusión de PANDA: en un contexto clínico también interesa avisar de cambios de apariencia que degradan el clasificador (la exactitud cae del 96,88\,\% en el test ID al 90,77\,\% en el control de resolución)
- `capitulos/02-estado-arte.tex:49` — citar
- `capitulos/02-estado-arte.tex:59` — introducción al cambio semántico y al desplazamiento de covariables
- `capitulos/02-estado-arte.tex:67` — near-OOD y far-OOD
- `capitulos/02-estado-arte.tex:81` — ubicar las citas a Zhang et al. (2021) y Fang et al. (2022)
- `capitulos/02-estado-arte.tex:96` — efecto Clever Hans en XAI y aprendizaje de relaciones espurias en la clasificación de imágenes
- `capitulos/02-estado-arte.tex:101` — desarrollar y citar (Achtibat et al.~\cite{achtibat2023})
- `capitulos/02-estado-arte.tex:109` — LRP, CRP y explicaciones glocales, usando el concepto de CRP glocal como en el artículo de CRP
- `capitulos/03-aprendizaje-supervisado.tex:20` — definición formal
- `capitulos/03-aprendizaje-supervisado.tex:25` — enunciado
- `capitulos/03-aprendizaje-supervisado.tex:28` — demostración
- `capitulos/03-aprendizaje-supervisado.tex:35` — definición
- `capitulos/03-aprendizaje-supervisado.tex:39` — definición
- `capitulos/03-aprendizaje-supervisado.tex:46` — enunciado
- `capitulos/03-aprendizaje-supervisado.tex:49` — demostración
- `capitulos/03-aprendizaje-supervisado.tex:55` — definición
- `capitulos/03-aprendizaje-supervisado.tex:62` — enunciado
- `capitulos/03-aprendizaje-supervisado.tex:66` — demostración
- `capitulos/03-aprendizaje-supervisado.tex:76` — reglas de actualización
- `capitulos/03-aprendizaje-supervisado.tex:80` — reglas de actualización
- `capitulos/03-aprendizaje-supervisado.tex:85` — observación
- `capitulos/03-aprendizaje-supervisado.tex:95` — definición
- `capitulos/03-aprendizaje-supervisado.tex:103` — definición
- `capitulos/03-aprendizaje-supervisado.tex:113` — enunciado: complejidad global frente a por ventanas
- `capitulos/03-aprendizaje-supervisado.tex:119` — ConvNeXt
- `capitulos/04-ood-metricas.tex:15` — introducción: factorización $P(X,Y) = P(Y \mid X)\,P(X)$
- `capitulos/04-ood-metricas.tex:18` — definición
- `capitulos/04-ood-metricas.tex:22` — definición
- `capitulos/04-ood-metricas.tex:30` — definición
- `capitulos/04-ood-metricas.tex:46` — citar a Fawcett~\cite{fawcett2006} para la curva ROC
- `capitulos/04-ood-metricas.tex:50` — definición
- `capitulos/04-ood-metricas.tex:56` — enunciado
- `capitulos/04-ood-metricas.tex:59` — demostración
- `capitulos/04-ood-metricas.tex:64` — enunciado
- `capitulos/04-ood-metricas.tex:67` — demostración
- `capitulos/04-ood-metricas.tex:75` — completar qué se mide con ese umbral (la proporción de ID rechazadas como OOD; más bajo es mejor)
- `capitulos/04-ood-metricas.tex:78` — definición
- `capitulos/04-ood-metricas.tex:87` — definición
- `capitulos/04-ood-metricas.tex:97` — definición
- `capitulos/05-metodos-posthoc.tex:13` — introducción del capítulo y notación común
- `capitulos/05-metodos-posthoc.tex:29` — definición formal
- `capitulos/05-metodos-posthoc.tex:34` — enunciado
- `capitulos/05-metodos-posthoc.tex:37` — demostración
- `capitulos/05-metodos-posthoc.tex:43` — desarrollo
- `capitulos/05-metodos-posthoc.tex:61` — definición formal
- `capitulos/05-metodos-posthoc.tex:67` — desarrollo
- `capitulos/05-metodos-posthoc.tex:82` — citar los artículos originales de KNN, RMDS, ViM y SHE (no aparecen en las notas)
- `capitulos/05-metodos-posthoc.tex:86` — definición
- `capitulos/05-metodos-posthoc.tex:91` — definición
- `capitulos/05-metodos-posthoc.tex:98` — enunciado
- `capitulos/05-metodos-posthoc.tex:101` — demostración
- `capitulos/05-metodos-posthoc.tex:106` — definición
- `capitulos/05-metodos-posthoc.tex:113` — definición
- `capitulos/05-metodos-posthoc.tex:117` — enunciado
- `capitulos/05-metodos-posthoc.tex:121` — definición
- `capitulos/05-metodos-posthoc.tex:134` — definición formal
- `capitulos/05-metodos-posthoc.tex:139` — segunda etapa del método: explicaciones
- `capitulos/06-inferencia.tex:15` — introducción al test (Mann y Whitney~\cite{mann1947}; Wilcoxon~\cite{wilcoxon1945})
- `capitulos/06-inferencia.tex:16` — sustituir por fuente académica (la explicación del test de las notas enlaza a un blog)
- `capitulos/06-inferencia.tex:20` — definición
- `capitulos/06-inferencia.tex:25` — enunciado
- `capitulos/06-inferencia.tex:28` — demostración
- `capitulos/06-inferencia.tex:33` — enunciado
- `capitulos/06-inferencia.tex:41` — desarrollo
- `capitulos/06-inferencia.tex:47` — desarrollo
- `capitulos/06-inferencia.tex:59` — definición
- `capitulos/06-inferencia.tex:65` — enunciado
- `capitulos/06-inferencia.tex:68` — demostración
- `capitulos/06-inferencia.tex:84` — desarrollo de la predicción conforme dividida
- `capitulos/06-inferencia.tex:87` — definición
- `capitulos/06-inferencia.tex:94` — enunciado
- `capitulos/06-inferencia.tex:99` — demostración
- `capitulos/06-inferencia.tex:105` — definición
- `capitulos/06-inferencia.tex:111` — definición
- `capitulos/06-inferencia.tex:118` — enunciado
- `capitulos/06-inferencia.tex:121` — demostración
- `capitulos/07-explicabilidad.tex:18` — definición
- `capitulos/07-explicabilidad.tex:22` — enunciado
- `capitulos/07-explicabilidad.tex:25` — demostración
- `capitulos/07-explicabilidad.tex:29` — definición
- `capitulos/07-explicabilidad.tex:40` — CRP
- `capitulos/08-materiales-metodos.tex:52` — verificación de la integridad de la partición
- `capitulos/08-materiales-metodos.tex:135` — fuente de los parches de 128\,px de PANDA (conjunto de Kaggle «panda-16x128x128-tiles-data»): decidir cómo citarla
- `capitulos/08-materiales-metodos.tex:161` — control de resolución y DTD~\cite{cimpoi2014}
- `capitulos/08-materiales-metodos.tex:175` — hardware y software
- `capitulos/08-materiales-metodos.tex:189` — sustituir por fuente académica
- `capitulos/08-materiales-metodos.tex:191` — ¿citar a Micikevicius et al.~\cite{micikevicius2018} para el entrenamiento con precisión mixta?
- `capitulos/08-materiales-metodos.tex:200` — completar la configuración del entrenamiento (preprocesado, pérdida con \emph{label smoothing}, política de entrenamiento y parada temprana)
- `capitulos/09-clasificacion-id.tex:12` — introducción del capítulo: cinco arquitecturas preentrenadas con ajuste fino (ViT-B/16, ResNet-50, ConvNeXt-S, EfficientNetV2-S y Swin-S) y evaluación en el test ID
- `capitulos/09-clasificacion-id.tex:24` — análisis de la \cref{tab:modelos}
- `capitulos/09-clasificacion-id.tex:26` — conclusión parcial
- `capitulos/09-clasificacion-id.tex:50` — análisis
- `capitulos/09-clasificacion-id.tex:70` — análisis
- `capitulos/09-clasificacion-id.tex:89` — análisis
- `capitulos/09-clasificacion-id.tex:109` — análisis (pérdida en test: 0,6757; exactitud en test: 0,9538)
- `capitulos/09-clasificacion-id.tex:131` — análisis (pérdida en test: 0,6356; exactitud en test: 0,9688)
- `capitulos/09-clasificacion-id.tex:133` — conclusión parcial de las curvas y matrices de confusión
- `capitulos/09-clasificacion-id.tex:145` — análisis de la \cref{tab:recall-clase}
- `capitulos/09-clasificacion-id.tex:147` — conclusión parcial
- `capitulos/09-clasificacion-id.tex:175` — conclusión parcial
- `capitulos/09-clasificacion-id.tex:194` — análisis de la \cref{tab:agrupaciones}
- `capitulos/09-clasificacion-id.tex:211` — análisis de la \cref{tab:sensibilidad-gleason} y de la \cref{fig:confusion-5clases}
- `capitulos/09-clasificacion-id.tex:213` — conclusión parcial
- `capitulos/09-clasificacion-id.tex:224` — discusión global
- `capitulos/10-deteccion-ood.tex:13` — introducción del capítulo: modelo, 16 métodos (13 de OpenOOD y tres configuraciones de STOOD-X), nueve conjuntos (\cref{tab:diseno-ood}) y métricas (\cref{sec:auroc,sec:fpr95,sec:ccr}); IC por \emph{bootstrap} (\cref{sec:bootstrap-mcnemar})
- `capitulos/10-deteccion-ood.tex:48` — conclusión parcial
- `capitulos/10-deteccion-ood.tex:67` — conclusión parcial
- `capitulos/10-deteccion-ood.tex:82` — conclusión parcial
- `capitulos/10-deteccion-ood.tex:90` — conclusión parcial
- `capitulos/10-deteccion-ood.tex:102` — conclusión parcial
- `capitulos/10-deteccion-ood.tex:114` — integración de las conclusiones parciales
- `capitulos/11-stoodx.tex:12` — introducción del capítulo
- `capitulos/11-stoodx.tex:27` — diferencias entre la implementación pública y la descripción del artículo, y motivo de la reimplementación
- `capitulos/11-stoodx.tex:47` — conclusión parcial
- `capitulos/11-stoodx.tex:58` — conclusión parcial
- `capitulos/11-stoodx.tex:75` — conclusión parcial
- `capitulos/11-stoodx.tex:93` — conclusión parcial
- `capitulos/11-stoodx.tex:131` — análisis de las \cref{fig:stoodx-ejemplos-detectadas,fig:stoodx-ejemplos-id,fig:stoodx-ejemplos-falsas}
- `capitulos/11-stoodx.tex:139` — discusión global
- `capitulos/12-prediccion-conforme.tex:16` — introducción del capítulo y limitación de intercambiabilidad entre validación y test
- `capitulos/12-prediccion-conforme.tex:31` — análisis de la \cref{tab:conforme-ood}
- `capitulos/12-prediccion-conforme.tex:33` — conclusión parcial
- `capitulos/12-prediccion-conforme.tex:54` — análisis de la \cref{tab:conforme-aps} y de la \cref{fig:conforme-cobertura}
- `capitulos/12-prediccion-conforme.tex:72` — análisis de la \cref{tab:conforme-tamano-ood} y de la \cref{fig:conforme-tamanos-clase}
- `capitulos/12-prediccion-conforme.tex:74` — conclusión parcial
- `capitulos/12-prediccion-conforme.tex:86` — análisis de la \cref{tab:mondrian-global}
- `capitulos/12-prediccion-conforme.tex:102` — análisis de la \cref{tab:mondrian-clase} y de la \cref{fig:mondrian-cobertura-clase}
- `capitulos/12-prediccion-conforme.tex:119` — análisis de la \cref{fig:mondrian-beta}
- `capitulos/12-prediccion-conforme.tex:146` — análisis de la \cref{fig:mondrian-glomeruloide}
- `capitulos/12-prediccion-conforme.tex:148` — conclusión parcial
- `capitulos/12-prediccion-conforme.tex:156` — discusión global
- `capitulos/13-fuga-lamina.tex:12` — introducción del capítulo
- `capitulos/13-fuga-lamina.tex:27` — identificación de las láminas a partir de los nombres de fichero
- `capitulos/13-fuga-lamina.tex:35` — análisis de la \cref{tab:fuga-contiguidad}
- `capitulos/13-fuga-lamina.tex:44` — análisis de la \cref{tab:fuga-vecino}
- `capitulos/13-fuga-lamina.tex:46` — conclusión parcial
- `capitulos/13-fuga-lamina.tex:56` — análisis de la \cref{tab:fuga-loso}
- `capitulos/13-fuga-lamina.tex:70` — análisis de la \cref{tab:fuga-control-interno} y de la \cref{fig:fuga-control-interno}
- `capitulos/13-fuga-lamina.tex:72` — conclusión parcial
- `capitulos/13-fuga-lamina.tex:83` — limitación metodológica
- `capitulos/14-explicabilidad-sesgos.tex:18` — capítulo en desarrollo
- `capitulos/15-conclusiones.tex:14` — conclusiones, objetivo por objetivo
- `capitulos/15-conclusiones.tex:26` — resto de limitaciones
- `capitulos/15-conclusiones.tex:33` — trabajo futuro
- `apendices/B-anexo-nct.tex:9` — breve introducción del anexo y análisis
- `apendices/C-material-complementario.tex:11` — material complementario

Total: 161

### \revisar

- `capitulos/02-estado-arte.tex:45` — traducción casi literal; parafrasear y citar
- `capitulos/02-estado-arte.tex:46` — «En este estudio» se refiere al survey de Yang et al., no a este TFG
- `capitulos/02-estado-arte.tex:50` — traducción casi literal; parafrasear y citar
- `capitulos/02-estado-arte.tex:53` — traducción casi literal; parafrasear y citar
- `capitulos/04-ood-metricas.tex:38` — traducción casi literal; parafrasear y citar
- `capitulos/04-ood-metricas.tex:84` — las notas decían que en AUPR-Out interesa un valor «más bajo»; es incorrecto: en ambas versiones interesa un valor alto
- `capitulos/05-metodos-posthoc.tex:24` — en EBO, «de las exponenciales de los argumentos de todos los logits» se ha simplificado a «de las exponenciales de todos los logits»
- `capitulos/06-inferencia.tex:74` — posible traducción casi literal (en las notas aparece bajo «Añadir esta parte de Inferencia Estadística»); comprobar la fuente, parafrasear y citar
- `capitulos/08-materiales-metodos.tex:20` — traducción casi literal; parafrasear y citar
- `capitulos/08-materiales-metodos.tex:21` — añadida la frase de las 85 WSI anotadas (dato del artículo, como se pidió); la primera frase atribuye el apartado al artículo, en lugar del título «información extraída del paper de Iván Sevillano» de las notas
- `capitulos/08-materiales-metodos.tex:28` — las notas daban un total de 126.192; el real es 126.109 (113.491 + 12.618; results\_integridad)
- `capitulos/08-materiales-metodos.tex:29` — la figura de tarta de las notas se sustituye por la \cref{tab:particion}, generada a partir de results\_integridad
- `capitulos/08-materiales-metodos.tex:36` — añadidos el carácter estratificado 80/20 de la división y la ausencia de semilla (results\_integridad, apartado 5)
- `capitulos/08-materiales-metodos.tex:76` — tabla de las notas: corregidas erratas y redacción mínima («si descarta por el centro o por el tejido», «discriminación», «órgano»)
- `capitulos/08-materiales-metodos.tex:86` — traducción casi literal; parafrasear y citar
- `capitulos/08-materiales-metodos.tex:87` — la referencia que acompañaba a NONORM en las notas (DOI 10.1109/ISBI.2009.5193250) es el método de normalización de Macenko, que se aplica a la versión normalizada NCT-CRC-HE-100K y no a NONORM: reubicar la cita
- `capitulos/08-materiales-metodos.tex:88` — el enlace al conjunto de datos (Zenodo) de las notas se sustituye por la cita a Kather et al.
- `capitulos/08-materiales-metodos.tex:108` — figura extraída del docx, regenerar; indicar qué panel es cada tejido
- `capitulos/08-materiales-metodos.tex:125` — figura extraída del docx, regenerar; comprobar el orden de los paneles
- `capitulos/08-materiales-metodos.tex:132` — los enlaces a Kaggle de las notas se sustituyen por la cita a Bulten et al.
- `capitulos/08-materiales-metodos.tex:150` — figura extraída del docx, regenerar; indicar qué panel es cada conjunto
- `capitulos/08-materiales-metodos.tex:166` — el enlace a GitHub se sustituye por la cita; el enlace al cuaderno de Colab con la explicación de uso y su captura de pantalla no van a la memoria
- `capitulos/08-materiales-metodos.tex:182` — la figura de tarta del conjunto reducido de las notas no se incluye; las cifras quedan en el texto
- `capitulos/08-materiales-metodos.tex:187` — las notas citaban solo a Kingma y Ba (Adam); para AdamW la cita correcta es Loshchilov y Hutter (2019)
- `capitulos/08-materiales-metodos.tex:190` — «infiriendo» corregido a «influyendo»
- `capitulos/09-clasificacion-id.tex:19` — la tabla de exactitudes de las notas (salida de \texttt{resultados.txt}) se sustituye por la \cref{tab:modelos}, generada a partir de results\_fase1, con IC; las exactitudes coinciden salvo Swin-S (0,96870 $\to$ 0,9688) y ResNet-50 (0,89634 $\to$ 0,8964), por una imagen de diferencia en la inferencia con precisión mixta
- `capitulos/09-clasificacion-id.tex:69` — las notas daban 0,8963 (\texttt{resultados.txt}); se usa el valor de results\_fase1
- `capitulos/09-clasificacion-id.tex:154` — exactitud del Swin-S: 96,87\,\% en las notas, 96,88\,\% en results\_fase1 (valor único de la memoria)
- `capitulos/09-clasificacion-id.tex:155` — la diferencia no es estadísticamente significativa (McNemar $p = 0{,}19$, \cref{tab:mcnemar}; ConvNeXt-S tiene además mayor F1 macro y \emph{balanced accuracy}): la elección no puede justificarse por un mejor resultado, sino presentarse como elección entre dos modelos empatados
- `capitulos/09-clasificacion-id.tex:158` — justificación sin respaldo bibliográfico; reformular o citar Liu et al. 2021
- `capitulos/09-clasificacion-id.tex:162` — «mediante window7» se ha desarrollado como «mediante ventanas de $7 \times 7$ (\texttt{window7})»
- `capitulos/09-clasificacion-id.tex:167` — diferencia corregida de 0,0019 a +0,0020 (results\_fase1); además, la afirmación del «techo de rendimiento» no está respaldada por los resultados
- `capitulos/10-deteccion-ood.tex:15` — la tabla principal de las notas (\texttt{tabla\_principal\_ood.tex}) se divide en una tabla por bloque; las tablas de AUPR van al \cref{ap:aupr}
- `capitulos/10-deteccion-ood.tex:29` — «de forma sistemática [...] en todos los conjuntos»: RMDS queda por debajo de MSP en LYM (AUROC 0,824 frente a 0,854, \cref{tab:ood-control-interno})
- `capitulos/10-deteccion-ood.tex:30` — el rango de FPR@95 (0,128--0,173) y el CCR@FPR5 (más de 0,82) valen para ViM, MDS, KNN y RMDS, pero no para STOOD-X (0,349 y 0,646)
- `capitulos/10-deteccion-ood.tex:33` — añadidas las referencias a la \cref{tab:ood-bootstrap-rmds} y a la \cref{fig:ood-roc}
- `capitulos/10-deteccion-ood.tex:97` — «al contrario de lo habitual en la literatura»: falta cita
- `capitulos/10-deteccion-ood.tex:98` — ReAct mejora a Energy en ocho de los nueve conjuntos; en el control de resolución queda por debajo (0,602 frente a 0,622)
- `capitulos/10-deteccion-ood.tex:99` — el 27,5\,\% se midió en la validación ID
- `capitulos/11-stoodx.tex:28` — tono
- `capitulos/11-stoodx.tex:33` — tono
- `capitulos/13-fuga-lamina.tex:28` — deducción a partir de los nombres de fichero: 95 láminas y rejilla de 224\,px, frente a las 85 WSI y el paso de 256\,px del artículo

Total: 42

