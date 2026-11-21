# Estado de la memoria (21/11/2026)

Compila sin errores con `latexmk -pdf tfg.tex`: **226 páginas** (bibliografía en la p. 199). No hay referencias ni citas sin definir. Las marcas `\pendiente` (rojo) y `\revisar` (naranja) se ocultan con `\borradorfalse` en `preambulo-propio.tex`.

## Cambios de estructura recientes

- 21/11/2026: recorte de relleno en el capítulo 3 (Bayes, tipos de relleno, ejemplo de NLP, demostración de equivarianza a permutaciones, extras de ViT, ResNet-50 y ConvNeXt), en el 5 (observaciones de SHE) y en el 6 (TCL y De Moivre-Laplace).
- 21/11/2026: de la predicción conforme solo queda la detección OOD conforme, ahora sección 11.6 de STOOD-X (`sec:conforme-ood`). Se han eliminado APS, RAPS y Mondrian (caps. 6 y 12), sus tablas, figuras y funciones de `generar_tablas.py`. El antiguo capítulo 12 desaparece: Explicabilidad pasa a ser el 12 (`capitulos/12-explicabilidad-sesgos.tex`, `img/cap12/`, `tablas/t12_*`) y Conclusiones el 13 (`capitulos/13-conclusiones.tex`).
- Antes: el capítulo de fuga por lámina se eliminó; se añadieron los apéndices D (detección OOD con ConvNeXt-S) y E (glosario).

## Capítulos

Página de inicio, palabras de texto aproximadas (sin comentarios, marcas, fórmulas, figuras ni tablas) y número de marcas:

| Capítulo | Pág. | Palabras | `\pendiente` | `\revisar` |
|---|---|---|---|---|
| Preliminares (agradecimientos, summary, resumen) | v | — | 3 | 0 |
| 1. Introducción | 3 | 62 | 10 | 0 |
| 2. Estado del arte | 5 | 7343 | 0 | 1 |
| 3. Aprendizaje supervisado y redes profundas | 23 | 9318 | 1 | 11 |
| 4. Formalización de la detección OOD y métricas | 53 | 2509 | 3 | 3 |
| 5. Métodos de detección post hoc | 61 | 3270 | 1 | 0 |
| 6. Inferencia estadística | 71 | 4326 | 0 | 0 |
| 7. Explicabilidad | 85 | 3010 | 6 | 0 |
| 8. Materiales y métodos | 97 | 3087 | 4 | 9 |
| 9. Clasificación ID | 107 | 2279 | 5 | 7 |
| 10. Detección OOD | 117 | 2393 | 14 | 21 |
| 11. STOOD-X (incluye la detección OOD conforme) | 135 | 1813 | 4 | 8 |
| 12. Explicabilidad y eliminación de sesgos | 145 | 494 | 5 | 0 |
| 13. Conclusiones y trabajo futuro | 153 | 41 | 4 | 0 |
| A. Tablas de AUPR-In y AUPR-Out | 157 | — | 0 | 0 |
| B. Anexo NCT-CRC (ADI, BACK, DEB, MUC) | 159 | — | 1 | 0 |
| C. Material complementario | 161 | — | 3 | 6 |
| D. Detección OOD con ConvNeXt-S | 189 | 486 | 7 | 0 |
| E. Glosario | 197 | — | 1 | 0 |

Lo que falta por redactar, a grandes rasgos: introducción (cap. 1), resumen, summary y agradecimientos; los análisis bajo las tablas y figuras de los caps. 9, 10, 11 y 12; las discusiones globales de los caps. 10 y 11; las conclusiones (cap. 13); canonización, reglas por capa y regla $z^{+}$ en el cap. 7; y los textos breves de los apéndices B, C, D y E. Detalle en la lista de marcas.

## Figuras

Ya no se usa ninguna figura extraída del .docx. El resto son copias de los originales (`tfg/executions/def1/param*` y `OpenOOD/results_*`). La figura de taxonomía es la figura 2 de Yang et al., recortada del PDF de `OpenOOD/docs/`. Los ejemplos de STOOD-X están en JPEG (calidad 90) para reducir el tamaño.

## Bibliografía

108 entradas en `library.bib`. Siguen marcadas `VERIFICAR`:

- `vovk2005`: Crossref no da los autores de la 1.ª edición; se han tomado de la 2.ª (2022).
- `wilcoxon1945`: Crossref solo da la página inicial (80).
- `kagglepanda128`: el autor sale del nombre de usuario de la URL (`iafoss`) y falta la fecha de publicación. Consultado el 26/10/2026.

Otras observaciones: STOOD-X se publicó en *Pattern Recognition* 177 (2026), clave `sevillano2026`; el artículo del conjunto de datos, en IEEE CAI 2026, clave `ayensa2026`. Pang et al. es de 2021 (las notas dicen 2020).

## Dudas abiertas

1. Gantt: `pgfgantt` ya está cargado; faltan las fechas.
2. Los paquetes `siunitx`, `cleveref`, `multirow` y `pgfgantt` están instalados en el TeX Live del usuario (`~/texlive/2026`).
3. `tablas/t09_mcnemar.tex` se genera pero no se usa (la tabla de McNemar del cap. 9 está escrita en el capítulo, `tab:mcnemar-swin-convnext`).
4. Flotantes que no cita ningún `\cref` del texto (añadir la referencia al redactar el análisis o valorar si sobran):
   - Capítulo 3: `fig:correlacion-cruzada`.
   - Capítulo 9: `fig:curvas-swin`, `fig:confusion-swin`, `tab:agrupaciones`.
   - Capítulo 10: `tab:ood-near`, `tab:ood-far`, `tab:ood-familias`, `tab:ood-corr-exactitud`, `tab:ood-corr-auroc`, `tab:ood-corr-fpr95`, `tab:ood-corr-umbral`, `tab:ood-corr-cec`, `tab:ood-corr-saturacion`, `fig:ood-corr-cec`, `fig:ood-corr-auroc-err`, `fig:ood-corr-riesgo-cobertura`.
   - Capítulo 11: `tab:stoodx-resultados`, `tab:stoodx-calibracion`, `fig:stoodx-calibracion`, `fig:stoodx-barrido-k`.
   - Apéndices: `tab:aupr-in`, `tab:aupr-out`, `tab:anexo-nct`, `tab:apc-corr-*`, `tab:convnext-*` (salvo `tab:convnext-conclusiones` y `tab:convnext-stoodx`), las figuras `fig:stoodx-kc-*` salvo `fig:stoodx-kc-id-alta`, `fig:muestras-primera`, `fig:muestras-azar`, `fig:muestras-adeno-norm`, `fig:muestras-adeno-tum` y `fig:apc-corr-dispersion`.

## Tablas

Se generan con `python3 scripts/generar_tablas.py` a partir de `OpenOOD/results_*` (solo lectura). No hay que editarlas a mano. El 21/11/2026 el script regenera las 47 tablas idénticas a las de `tablas/`.

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
- `capitulos/01-introduccion.tex:75` — objetivos específicos y grado de consecución
- `capitulos/01-introduccion.tex:85` — principales fuentes consultadas
- `capitulos/01-introduccion.tex:90` — estructura de la memoria
- `capitulos/01-introduccion.tex:101` — planificación temporal y diagrama de Gantt
- `capitulos/01-introduccion.tex:108` — planificación económica
- `capitulos/03-aprendizaje-supervisado.tex:1602` — definir el escalado por capa y añadirlo a la ecuación del bloque: requiere Touvron et al.~(2021), \emph{Going deeper with image transformers}, ICCV (ref.~[74…
- `capitulos/04-ood-metricas.tex:108` — aprendibilidad de la detección OOD (Fang et al.~\cite{fang2022})
- `capitulos/04-ood-metricas.tex:256` — definición
- `capitulos/04-ood-metricas.tex:265` — definición
- `capitulos/05-metodos-posthoc.tex:13` — introducción del capítulo y notación común
- `capitulos/07-explicabilidad.tex:9` — introducción del capítulo: modelos de caja negra frente a caja blanca (petición del tutor, reunión del 30 oct); el trabajo se centra en LRP y CRP
- `capitulos/07-explicabilidad.tex:24` — enlazar con los resultados propios: control interno del capítulo de detección OOD
- `capitulos/07-explicabilidad.tex:264` — para qué se usa: en la primera capa suaviza el mapa en el espacio de entrada y lo hace invariante a la normalización de la entrada~\cite{achtibat2023}
- `capitulos/07-explicabilidad.tex:267` — reglas por capa: recomendación de Montavon et al. (LRP-0 en capas superiores, $\varepsilon$ en intermedias, $\gamma$ en inferiores) y composite LRP$_{\vareps…
- `capitulos/07-explicabilidad.tex:388` — canonización: BatchNorm, sesgos, conexiones residuales y particularidades de ConvNeXt
- `capitulos/07-explicabilidad.tex:395` — definición, proposición (submultiplicatividad del coeficiente de Dobrushin) y su relación con la insensibilidad a la clase
- `capitulos/08-materiales-metodos.tex:114` — verificación de la integridad de la partición
- `capitulos/08-materiales-metodos.tex:197` — justificación del autor
- `capitulos/08-materiales-metodos.tex:268` — hardware y software
- `capitulos/08-materiales-metodos.tex:282` — sustituir por fuente académica
- `capitulos/09-clasificacion-id.tex:52` — análisis
- `capitulos/09-clasificacion-id.tex:70` — análisis
- `capitulos/09-clasificacion-id.tex:87` — análisis
- `capitulos/09-clasificacion-id.tex:105` — análisis (pérdida en test: 0,6757; exactitud en test: 0,9538)
- `capitulos/09-clasificacion-id.tex:125` — análisis (pérdida en test: 0,6356; exactitud en test: 0,9688)
- `capitulos/10-deteccion-ood.tex:16` — introducción del capítulo: modelo, 17 métodos (13 de OpenOOD y cuatro configuraciones de STOOD-X: 100\,\% y 87,5\,\% con $K = 500$, $K_c$ y $K = 144$, \cref{…
- `capitulos/10-deteccion-ood.tex:32` — nota al pie sobre la diferencia de exactitud por cambio de entorno
- `capitulos/10-deteccion-ood.tex:199` — análisis
- `capitulos/10-deteccion-ood.tex:234` — proposición del autor: valor de saturación de la $-z$ con separación completa
- `capitulos/10-deteccion-ood.tex:235` — análisis
- `capitulos/10-deteccion-ood.tex:252` — análisis
- `capitulos/10-deteccion-ood.tex:263` — introducción de la subsección
- `capitulos/10-deteccion-ood.tex:297` — análisis
- `capitulos/10-deteccion-ood.tex:314` — análisis
- `capitulos/10-deteccion-ood.tex:345` — análisis del autor
- `capitulos/10-deteccion-ood.tex:441` — análisis de la \cref{tab:ood-global}
- `capitulos/10-deteccion-ood.tex:481` — cita de Tellez et al.\ (2019), si se usa: falta el documento
- `capitulos/10-deteccion-ood.tex:482` — discusión global
- `capitulos/10-deteccion-ood.tex:489` — remisión al \cref{ap:convnext}: conclusiones que se mantienen y que dependen del modelo
- `capitulos/11-stoodx.tex:13` — introducción del capítulo
- `capitulos/11-stoodx.tex:29` — diferencias entre la implementación pública y la descripción del artículo, y motivo de la reimplementación
- `capitulos/11-stoodx.tex:227` — análisis de los ejemplos del \cref{ap:complementario} (\cref{fig:stoodx-ejemplos-detectadas,fig:stoodx-ejemplos-id,fig:stoodx-ejemplos-falsas,fig:stoodx-ejem…
- `capitulos/11-stoodx.tex:250` — discusión global
- `capitulos/12-explicabilidad-sesgos.tex:18` — introducción del capítulo
- `capitulos/12-explicabilidad-sesgos.tex:64` — análisis de la \cref{fig:xai-id-aceptada}, la \cref{fig:xai-ood-aceptada} y la \cref{tab:xai-controles}
- `capitulos/12-explicabilidad-sesgos.tex:84` — análisis de la \cref{fig:xai-canal102}
- `capitulos/12-explicabilidad-sesgos.tex:95` — análisis de la \cref{fig:xai-ablacion} y la \cref{tab:xai-ablacion}
- `capitulos/12-explicabilidad-sesgos.tex:108` — análisis de la \cref{fig:xai-atlas-estroma} y la \cref{tab:xai-atlas}
- `capitulos/13-conclusiones.tex:14` — conclusiones, objetivo por objetivo
- `capitulos/13-conclusiones.tex:27` — límites teóricos de la detección OOD: aprendibilidad (Fang et al.~\cite{fang2022})
- `capitulos/13-conclusiones.tex:28` — resto de limitaciones
- `capitulos/13-conclusiones.tex:35` — trabajo futuro
- `apendices/B-anexo-nct.tex:9` — breve introducción del anexo y análisis
- `apendices/C-material-complementario.tex:12` — presentación de las figuras
- `apendices/C-material-complementario.tex:58` — presentación de las figuras
- `apendices/C-material-complementario.tex:305` — presentación
- `apendices/D-convnext.tex:28` — introducción del autor
- `apendices/D-convnext.tex:42` — comentario breve
- `apendices/D-convnext.tex:98` — comentario breve
- `apendices/D-convnext.tex:121` — comentario breve
- `apendices/D-convnext.tex:137` — comentario breve
- `apendices/D-convnext.tex:151` — comentario breve
- `apendices/D-convnext.tex:190` — conclusión del autor
- `apendices/E-glosario.tex:14` — definiciones del glosario
Total: 72

### \revisar
- `capitulos/02-estado-arte.tex:396` — Iván, me gustaría que revisases esta parte por si hubiera algo mal explicado o que no se entendiera
- `capitulos/03-aprendizaje-supervisado.tex:23` — párrafo añadido a petición del autor para justificar la unificación de la notación; antes, $K$ era también el número de capas ocultas (\cref{def:mlp}) y de b…
- `capitulos/03-aprendizaje-supervisado.tex:200` — corregido: $|\cdot|$ actúa sobre los multiíndices $\alpha\in\mathbb{N}^n$, no sobre $H_k$ (antes «$|\cdot|:H_K \Rightarrow \mathbb{N}$»); los coeficientes $p…
- `capitulos/03-aprendizaje-supervisado.tex:207` — desarrollo añadido a petición del autor: se explicitan $W$, que $W^\perp=\{0\}$ y la descomposición $H_k=W\oplus W^\perp$; antes decía «Si $q$ es ortogonal a…
- `capitulos/03-aprendizaje-supervisado.tex:242` — añadido a petición del autor el paso intermedio: se divide por $\sigma^{(k)}(b_k)\ne 0$; antes decía «Por (a), $x^k\in\overline{\mathcal{M}(\sigma)}$ para to…
- `capitulos/03-aprendizaje-supervisado.tex:243` — añadido a petición del autor el argumento de $\varepsilon/2$; antes decía «La clausura contiene todos los polinomios y, por el teorema de Weierstrass, es tod…
- `capitulos/03-aprendizaje-supervisado.tex:386` — notación unificada: el vector \emph{one-hot} y los objetivos suavizados se llamaban $y$ e $y^{LS}$; ahora son $q$ y $q^{LS}$, como en la \cref{prop:ce-mv}, p…
- `capitulos/03-aprendizaje-supervisado.tex:411` — añadido a petición del autor el paso intermedio del desarrollo y la frase que explica por qué la primera suma se reduce a $-\log p_y$
- `capitulos/03-aprendizaje-supervisado.tex:425` — enunciado generalizado a petición del autor; antes decía «Si además $q_k > 0$ para todo $k$, la igualdad se da si y solo si $p = q$»
- `capitulos/03-aprendizaje-supervisado.tex:448` — desarrollo añadido a petición del autor: se explica qué es $S$ (soporte de $q$, $k$ índice de clase), por qué se restringe la suma a $S$, la igualdad interme…
- `capitulos/03-aprendizaje-supervisado.tex:457` — caso de igualdad reescrito para el enunciado general; antes suponía $q_k > 0$ para todo $k$
- `capitulos/03-aprendizaje-supervisado.tex:559` — añadido a petición del autor: se escriben explícitamente las tres operaciones componente a componente
- `capitulos/04-ood-metricas.tex:45` — Iván
- `capitulos/04-ood-metricas.tex:138` — traducción casi literal; parafrasear y citar
- `capitulos/04-ood-metricas.tex:262` — las notas decían que en AUPR-Out interesa un valor «más bajo»; es incorrecto: en ambas versiones interesa un valor alto
- `capitulos/08-materiales-metodos.tex:31` — Iván
- `capitulos/08-materiales-metodos.tex:98` — Iván, ¿hace falta que ponga lo de la semilla?
- `capitulos/08-materiales-metodos.tex:135` — Iván, como consideras añadir aquí un par de imágenes LYM y de ID de esntroma para ver le parecido mencionado
- `capitulos/08-materiales-metodos.tex:154` — Iván y Jesús: Que muestras crees que serán las más propensas a que se acaben confundiendo
- `capitulos/08-materiales-metodos.tex:214` — la exactitud del nivel 0 es 0,96870, igual a la de las \emph{features} congeladas de la evaluación OOD (0,9687 [0,9657; 0,9716] en exactitud\_celda.csv), per…
- `capitulos/08-materiales-metodos.tex:238` — fila «Corrupciones sintéticas» añadida por el agente (\cref{sec:corrupciones})
- `capitulos/08-materiales-metodos.tex:239` — tabla de las notas: corregidas erratas y redacción mínima («si descarta por el centro o por el tejido», «discriminación», «órgano»)
- `capitulos/08-materiales-metodos.tex:243` — Iván: Considero que no aporta nada añadir los entornos que he usado y las cosas que tengo instalados en ellos porque cada poco suelen cambiar, entonces algo …
- `capitulos/08-materiales-metodos.tex:246` — el enlace a GitHub se sustituye por la cita; el enlace al cuaderno de Colab con la explicación de uso y su captura de pantalla no van a la memoria
- `capitulos/09-clasificacion-id.tex:169` — exactitud del Swin-S: 96,87\,\% en las notas, 96,88\,\% en results\_fase1 (valor único de la memoria)
- `capitulos/09-clasificacion-id.tex:170` — la diferencia no es estadísticamente significativa (McNemar $p = 0{,}19$, \cref{tab:mcnemar-swin-convnext}; ConvNeXt-S tiene además mayor F1 macro y \emph{ba…
- `capitulos/09-clasificacion-id.tex:294` — Iván y Jesús
- `capitulos/09-clasificacion-id.tex:304` — iván, debo hacer la comparación entre el total de muestras de solo estas tres clases o entre todas
- `capitulos/09-clasificacion-id.tex:312` — Iván y Jesús: lo que no sé cómo justificar es que se confunda con NM, sería interesante apuntar que sería conveniente más muestras de Gleason3 en particular …
- `capitulos/10-deteccion-ood.tex:31` — el autor atribuye la diferencia a un cambio de entorno (versión de PyTorch y hardware), pero según los ficheros la fase 1 y la extracción OOD comparten entor…
- `capitulos/10-deteccion-ood.tex:34` — la tabla principal de las notas (\texttt{tabla\_principal\_ood.tex}) se divide en una tabla por bloque; las tablas de AUPR van al \cref{ap:aupr}
- `capitulos/10-deteccion-ood.tex:104` — reforzar: con ConvNeXt-S (espacio M), menos saturado (22,0\,\% en TUM+NORM y 2,6\,\% en el control, frente a 66,3\,\% y 19,0\,\% en el Swin), STOOD-X sí dist…
- `capitulos/10-deteccion-ood.tex:105` — estas cifras de STOOD-X son con $K = 500$. Con $K = 144$, PANDA (0,939) y el control (0,935) siguen casi igualados (\cref{tab:ood-panda-control}) con menos s…
- `capitulos/10-deteccion-ood.tex:116` — propuesta: matizar con las corrupciones sintéticas (\cref{sec:ood-corr-saturacion}): allí la saturación de \stoodx crece con la severidad (hasta el 86,4\,\% …
- `capitulos/10-deteccion-ood.tex:200` — tablas completas, con IC y el resto de detectores, en el apéndice C (\cref{sec:apc-corrupciones}): confirmar ubicación
- `capitulos/10-deteccion-ood.tex:212` — comprobar qué variante de la CEC de \stoodx muestra la figura (la de empates exactos, 0,138, o la de pares saturados como empate, 0,128): la tabla usa 0,128
- `capitulos/10-deteccion-ood.tex:236` — tono: comparación de \stoodx con ViM y MDS
- `capitulos/10-deteccion-ood.tex:253` — tono
- `capitulos/10-deteccion-ood.tex:273` — la figura usa la puntuación original de \stoodx, no la variante con empates reales de la \cref{tab:ood-corr-auroc-err}; regenerarla con la variante principal
- `capitulos/10-deteccion-ood.tex:298` — tono
- `capitulos/10-deteccion-ood.tex:315` — tono
- `capitulos/10-deteccion-ood.tex:325` — la figura usa la puntuación original de \stoodx (AURC 0,113), no la variante con empates reales (0,108) de la \cref{tab:ood-corr-aurc}
- `capitulos/10-deteccion-ood.tex:346` — tono
- `capitulos/10-deteccion-ood.tex:355` — añadido el AUROC con $K = 144$; quitado el punto suelto tras la tabla
- `capitulos/10-deteccion-ood.tex:361` — «al contrario de lo habitual en la literatura»: falta cita
- `capitulos/10-deteccion-ood.tex:362` — ReAct mejora a Energy en ocho de los nueve conjuntos; en el control de resolución queda por debajo (0,602 frente a 0,622)
- `capitulos/10-deteccion-ood.tex:363` — el 27,5\,\% se midió en la validación ID
- `capitulos/10-deteccion-ood.tex:447` — conclusiones propias del Swin; con ConvNeXt-S cambian (\cref{tab:convnext-conclusiones})
- `capitulos/10-deteccion-ood.tex:448` — donde dice que \stoodx «es el más sensible a la resolución», propuesta de integrar dos cosas: que es el más sensible al \emph{covariate shift} en general (co…
- `capitulos/10-deteccion-ood.tex:449` — la conclusión vale para los métodos con su configuración por defecto (STOOD-X con $K = 500$). Con $K = 144$, elegido solo con datos ID, STOOD-X es el mejor e…
- `capitulos/11-stoodx.tex:30` — tono
- `capitulos/11-stoodx.tex:35` — tono
- `capitulos/11-stoodx.tex:55` — subsección redactada por el agente a petición del autor (excepción a la regla de no redactar prosa); revisar estilo y contenido
- `capitulos/11-stoodx.tex:69` — párrafo redactado por el agente a petición del autor; revisar
- `capitulos/11-stoodx.tex:88` — añadido «Con $K = 500$» al principio del párrafo: con $K = 144$ estas afirmaciones dejan de valer (párrafo siguiente)
- `capitulos/11-stoodx.tex:102` — párrafos sobre $K = 144$ redactados por el agente a petición del autor; revisar
- `capitulos/11-stoodx.tex:117` — añadido «con $K = 500$»: la calibración no se ha comprobado con $K = 144$, así que no se puede afirmar nada sobre ella
- `capitulos/11-stoodx.tex:196` — cambiado «que se mantiene en el valor del artículo» por la remisión a la selección de $K$ solo con datos ID
- `apendices/C-material-complementario.tex:214` — pie de figura redactado por el agente
- `apendices/C-material-complementario.tex:296` — pie de figura redactado por el agente
- `apendices/C-material-complementario.tex:306` — tablas completas en el apéndice C: confirmar ubicación
- `apendices/C-material-complementario.tex:331` — sección y título añadidos por el agente para alojar las dos figuras
- `apendices/C-material-complementario.tex:341` — pie de figura redactado por el agente
- `apendices/C-material-complementario.tex:348` — pie de figura redactado por el agente
Total: 64

