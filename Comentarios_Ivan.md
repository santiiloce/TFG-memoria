# Comentarios sobre la memoria

Revisión del borrador que describe `ESTADO.md` (26/10/2026): 18 ficheros de capítulos y apéndices, 2.974 líneas. Hecho sobre el árbol limpio del repositorio y sin recompilar. Todas las notas se apoyan en el texto, en `library.bib` o en las cifras que el propio documento declara; las que no pude comprobar lo dicen.

**Gravedad.**
**alta** — incumple una regla del repositorio o un requisito de entrega, o es un error que el tribunal va a señalar y que no se resuelve en cinco minutos.
**media** — el contenido está, pero el argumento no cierra.
**baja** — forma, consistencia y pulido.

Las notas van agrupadas por capítulo y numeradas `capítulo.orden`; las que afectan a todo el documento llevan `G`. Cada una tiene tres campos: qué hay hoy, por qué es un problema y qué hacer.

---

## Transversales

**G1** · `todo el documento` · **alta**

**Descripción.** 174 marcas `\pendiente` y 48 `\revisar` en 2.974 líneas; los capítulos 1, 3, 12, 13 y 14 no tienen una sola línea de prosa.

**Fallo.** La Parte II, que es la parte matemática que pidió el tutor, es la menos escrita del documento. Tal como está, la memoria no se sostiene: hay diez capítulos con estructura y sin texto.

**Solución.** Escribir 3, 4, 5 y 6 antes de pulir nada más. Los comentarios de cada capítulo ya dicen qué va en cada sección, así que el trabajo es de redacción, no de planificación.

---

**G2** · `caps. 5, 8, 9 y 10` · **media**

**Descripción.** De las 48 marcas `\revisar`, unas veinte registran cambios ya hechos («añadidas las citas a MSP, MaxLogit y Energy», «el enlace a GitHub se sustituye por la cita») en lugar de encargos pendientes.

**Fallo.** Se imprimen en naranja con el mismo aspecto que una tarea que el autor tiene que resolver, así que el PDF no se puede leer ni como memoria ni como lista de trabajo.

**Solución.** Separar los dos usos: el registro de lo ya cambiado tiene su sitio en `ESTADO.md`, y en el documento conviene que quede solo lo que exige acción del autor.

---

**G3** · `preliminares/declaracion-originalidad.tex` · **alta**

**Descripción.** No hay declaración de uso de herramientas de IA generativa, y las notas del capítulo 1 la listan como punto a cubrir.

**Fallo.** Es un requisito de entrega, no contenido científico: si falta, el trámite se bloquea al final, cuando ya no hay tiempo.

**Solución.** Comprobar en la normativa de la UGR si aplica y, si aplica, redactarla y colocarla.

---

**G4** · `preliminares/` · **alta**

**Descripción.** Resumen, summary (800–1500 palabras), agradecimientos y dedicatoria están vacíos.

**Fallo.** Son requisito de la plantilla y del reglamento, y el summary es lo único que leerá una parte del tribunal.

**Solución.** Escribirlos al final, pero reservando el tiempo: el summary es el que más horas cuesta y el que menos se puede improvisar.

---

**G5** · `preambulo-propio.tex:70-78` · **media**

**Descripción.** `\Pin`, `\Pout`, `\Din`, `\Dout`, `\Xin` y `\Xout` están definidas y no aparecen nunca; el capítulo 4 usa `\mathcal{D}_{\mathrm{ID}}` para lo mismo.

**Fallo.** Hay dos notaciones para el mismo objeto, y cuando se escriban los capítulos 3 a 7 cada uno usará la que tenga a mano.

**Solución.** Elegir una y usarla en todo el documento; borrar la otra del preámbulo.

---

**G6** · `caps. 8-11 y apéndices` · **media**

**Descripción.** Más de veinte figuras y tablas que ningún `\cref` del texto cita: las curvas y matrices del 9, las tablas del 10 y del 11 y los apéndices.

**Fallo.** Un flotante sin referencia obliga al lector a buscar dónde se discute, y en la defensa se nota.

**Solución.** Referenciarlos al escribir el análisis de cada uno; están listados en `ESTADO.md`.

---

**G7** · `caps. 8, 10 y 11` · **media**

**Descripción.** Muchas marcas están al final de la sección y no donde falta el texto; en el capítulo 8, el `\revisar{traducción casi literal}` aparece unas ochenta líneas después del pasaje al que se refiere.

**Fallo.** El lector no sabe qué párrafo hay que tocar.

**Solución.** Colocar cada marca en el punto exacto donde falta el contenido.

---

**G8** · `library.bib` · **media**

**Descripción.** Cinco entradas llevan `note = {VERIFICAR}`: `openood15`, `vovk2005`, `wilcoxon1945`, `storas2025` y `kagglepanda128`.

**Fallo.** Una referencia sin verificar en la bibliografía de un TFG es un riesgo directo, y dos de ellas son trabajos que el tribunal conoce.

**Solución.** Cerrarlas antes de la entrega y quitar las notas del `.bib`.

---

**G9** · `capitulos/08-materiales-metodos.tex:40-78` · **baja**

**Descripción.** La tabla `tab:clases` usa `[htbp]`, un `\vspace{2pt}` manual y una `minipage` con nota al pie dentro del flotante.

**Fallo.** Se aparta de las convenciones del repositorio (flotantes `[tbp]`, sin `\vspace` manual) y la nota al pie puede descolocarse al recomponer.

**Solución.** `[tbp]`, quitar el `\vspace` y pasar la nota al pie al texto o a una línea de la tabla.

---

**G10** · `capitulos/04-ood-metricas.tex:20` · **media**

**Descripción.** La cita «(Scheirer et al., 2012)» está escrita en texto plano y no tiene entrada en `library.bib`.

**Fallo.** El lector ve un Autor (año) que no puede localizar en las referencias; y al convertirla en `\cite` sin añadir la entrada, la bibliografía deja de compilar. Es el único caso del documento: los otros sesenta `\cite` resuelven.

**Solución.** Añadir la entrada (la de 2012 es la de CVPR, *Toward Open Set Recognition*; la de TPAMI es de 2013: elegir una y ser consistente) y citarla con `\cite`.

---

**G11** · `todo el documento` · **alta**

**Descripción.** 62 de los 67 entornos matemáticos —definiciones, proposiciones, teoremas y observaciones— no se citan ni una sola vez desde la prosa.

**Fallo.** El aparato formal queda aislado: la Parte II no se conecta con la Parte III ni consigo misma, y las métricas que el capítulo 10 usa no se apoyan en ninguna de esas definiciones.

**Solución.** Referenciar cada definición con `\cref` desde el párrafo que la usa y decidir qué entornos se quedan: uno que ningún `\cref` toca es candidato a sobra.

---

## Capítulo 1 — Introducción

**1.1** · `capitulos/01-introduccion.tex` · **alta**

**Descripción.** Las diez secciones son esqueleto, cada una con una marca y con los puntos que debe cubrir en comentarios.

**Fallo.** La introducción es lo primero que se lee y donde la guía de la UGR exige objetivos, resultados y grado de consecución.

**Solución.** Redactar en el orden de los comentarios existentes y dejar el Gantt y el presupuesto para el final.

---

**1.2** · `capitulos/01-introduccion.tex:102-109` · **media**

**Descripción.** El Gantt y la planificación económica exigen fechas y costes que no están en ningún fichero del repositorio, aunque las horas de GPU sí están en `resultados.txt` y en `config.json`.

**Fallo.** Es el punto del documento con más riesgo de inventar una cifra.

**Solución.** Fijar de dónde sale cada dato antes de escribir la sección.

---

## Capítulo 2 — Estado del arte

**2.1** · `capitulos/02-estado-arte.tex:45` · **alta**

**Descripción.** Un recordatorio se imprime en negrita dentro de la prosa: «poner ejemplo de método de detección OOD vs ID en entrenamiento».

**Fallo.** No es texto de memoria, y hoy se lee en el PDF en medio de un párrafo.

**Solución.** Convertirlo en marca `\pendiente` o escribir el ejemplo.

---

**2.2** · `02:44-53, 06:74, 07:9-16, 08:20 y 08:86` · **alta**

**Descripción.** Siete pasajes son traducción casi literal de su fuente: Yang et al. en el capítulo 2, un texto de las notas en el 6, el libro de explicabilidad en el 7 y el artículo del conjunto de datos y el de NCT-CRC en el 8. Cinco ya están marcados; el del capítulo 7 no.

**Fallo.** Una traducción casi literal sin cita es plagio, y es el riesgo más caro de todos los que aparecen en el documento.

**Solución.** Reescribirlos con redacción propia y cita. Los reescribe el autor, no el agente; conviene tratarlos como una sola lista de trabajo.

---

**2.3** · `capitulos/02-estado-arte.tex:44-53` · **media**

**Descripción.** El texto sobre OOD, OSR y su evaluación llega antes de presentar la taxonomía, y la figura `fig:taxonomia-yang` no se cita ni se sitúa el trabajo en la subtarea (d).

**Fallo.** El lector no sabe por qué aparece esa figura ni en qué casilla del esquema cae el trabajo.

**Solución.** Presentar la taxonomía primero, situar el trabajo en (d) y justificar ahí la inclusión de PANDA con la caída de exactitud del 96,88 % al 90,77 %.

---

**2.4** · `02:49 y 02:101-107` · **media**

**Descripción.** El capítulo explica LRP, CRP y explicaciones glocales, que es el contenido del capítulo 7, y describe las métricas de evaluación, que es el capítulo 4.

**Fallo.** Tres capítulos cuentan lo mismo con palabras distintas, y el que se lea segundo parecerá repetitivo.

**Solución.** Dejar en el 2 solo el estado del arte —quién y qué— y llevar el desarrollo formal al 4 y al 7.

---

**2.5** · `capitulos/02-estado-arte.tex:49` · **baja**

**Descripción.** Una marca `\revisar` advierte sobre la expresión «En este estudio», que ya no aparece en el texto.

**Fallo.** Apunta a un pasaje que no existe y hace dudar de las demás marcas.

**Solución.** Eliminarla.

---

## Capítulo 3 — Aprendizaje supervisado y redes profundas

**3.1** · `capitulos/03-aprendizaje-supervisado.tex` · **alta**

**Descripción.** 17 entornos vacíos —definiciones, proposiciones y demostraciones— y ninguna línea de prosa; los enunciados están en comentarios.

**Fallo.** Es el arranque de la parte matemática y hoy no tiene contenido, y todo lo que viene después se apoya aquí.

**Solución.** Escribirlo primero. Las demostraciones más rentables son la optimalidad del clasificador de Bayes, la equivalencia entre entropía cruzada y máxima verosimilitud y el óptimo del *label smoothing*, que se usa en el capítulo 12.

---

**3.2** · `capitulos/03-aprendizaje-supervisado.tex:7-11` · **media**

**Descripción.** La notación de la que dependen los capítulos 4 a 12 —espacio de entrada, `C = 14`, `D = 768`, extractor de características— está en un comentario de cabecera.

**Fallo.** Sin fijarla en el texto, cada capítulo reinventa la suya y aparecen dos notaciones para lo mismo (ver G5).

**Solución.** Un apartado corto de notación al principio del capítulo, usado en el resto.

---

## Capítulo 4 — Formalización de la detección OOD y métricas

**4.1** · `capitulos/04-ood-metricas.tex:10-48` · **alta**

**Descripción.** La definición de ID/OOD se apoya en una `\cite` suelta al final de una lista y la del objetivo, en una referencia escrita en texto plano; no queda claro de dónde sale cada una.

**Fallo.** Ninguna de las dos se usa después en la memoria, así que el lector no puede saber si son el marco del trabajo o un resumen de la literatura.

**Solución.** Citar la fuente de cada definición, comprobar la transcripción contra el original y declarar su papel en una frase; si no se usan, recortarlas.

---

**4.2** · `capitulos/04-ood-metricas.tex:20-38` · **alta**

**Descripción.** El objetivo de la detección se formula como la minimización del riesgo de espacio abierto, remitiendo a una referencia que no está en la bibliografía.

**Fallo.** No se puede verificar si la fórmula es fiel al original, y el capítulo 10 no evalúa con ella: ninguno de los resultados la usa.

**Solución.** Recuperar el original, añadir la entrada a `library.bib` y citarla con `\cite`; después decidir si se mantiene como marco —con una frase que explique por qué no se evalúa así— o se elimina.

---

**4.3** · `04:20 y 04:42` · **alta**

**Descripción.** El texto remite a «la Definición 1» y a «la definición 2», escritas a mano.

**Fallo.** Los entornos se numeran por capítulo, así que el PDF dice «Definición 4.1» y «4.2»: las dos referencias apuntan a definiciones que no existen con ese número.

**Solución.** `\cref` a `def:ID` y a `def:objetivoOOD`.

---

**4.4** · `capitulos/04-ood-metricas.tex:45-48` · **alta**

**Descripción.** La definición se abre como `\begin{definicion}[Detección OOD estándar]{def:deteccionOODestandar}`.

**Fallo.** El label va en un argumento obligatorio, así que no se registra; el entorno queda sin etiqueta y su cuerpo queda fuera, como texto suelto.

**Solución.** `\label{def:deteccionOODestandar}` dentro del entorno, y el cuerpo dentro también.

---

**4.5** · `capitulos/04-ood-metricas.tex:83` · **media**

**Descripción.** El párrafo anuncia «tres métricas» y después se describen cinco: AUROC, FPR@95, AUPR-In, AUPR-Out y CCR@FPRx.

**Fallo.** La enumeración del principio no coincide con el contenido de la sección.

**Solución.** Reescribir la apertura con la lista real y decir cuál es la principal.

---

**4.6** · `capitulos/04-ood-metricas.tex:10-48` · **media**

**Descripción.** `\mathcal{D}_{\mathrm{ID}}` se usa como distribución y como conjunto, `p` denota dos densidades distintas y en el texto queda un `$\mathcal{D}_{\mathrm{ID}]}$` con un corchete suelto.

**Fallo.** La notación no distingue distribución de soporte, que es justo lo que hace falta para hablar de cambio de distribución.

**Solución.** Fijar el convenio en la §3 y revisar el capítulo entero.

---

**4.7** · `capitulos/04-ood-metricas.tex:20-48` · **baja**

**Descripción.** Erratas: «definde», «riegso», «incunbe», «semátnicas», «distribución.Se» y «el objetivo forma».

**Fallo.** Cinco palabras mal en un párrafo son la primera impresión del capítulo.

**Solución.** Pasada de corrección.

---

## Capítulo 5 — Métodos de detección post hoc

**5.1** · `capitulos/05-metodos-posthoc.tex` · **alta**

**Descripción.** 17 entornos vacíos: las definiciones de MSP, MaxLogit, Energy, ReAct, ASH, DICE, KNN, MDS, RMDS, ViM, SHE y STOOD-X, y las proposiciones de LogSumExp, Mahalanobis–LDA y residuo de PCA.

**Fallo.** Es exactamente la parte que pidió el tutor: los métodos están descritos en prosa, pero sin la definición formal no se distinguen de un resumen de la literatura.

**Solución.** Escribir las definiciones en el orden del capítulo. Las tres proposiciones son las de más valor y las de menos esfuerzo: caben en una página.

---

**5.2** · `capitulos/05-metodos-posthoc.tex:25` · **media**

**Descripción.** Energy se describe como «el logaritmo de la suma de las exponenciales de todos los logits».

**Fallo.** Faltan la temperatura y el signo, así que el lector no puede reproducir lo que el capítulo 10 evalúa.

**Solución.** Dar la expresión completa en la definición y dejar la prosa como interpretación.

---

**5.3** · `capitulos/05-metodos-posthoc.tex:33 y 05:95` · **media**

**Descripción.** `prop:logsumexp` y `prop:mds-lda` existen solo como comentario.

**Fallo.** Son las dos piezas que justifican los métodos —la cota suave del máximo y la relación con el análisis discriminante lineal— y hoy no están en el texto.

**Solución.** Enunciarlas y demostrarlas; la segunda se demuestra en cinco líneas.

---

**5.4** · `capitulos/05-metodos-posthoc.tex:131-140` · **media**

**Descripción.** En STOOD-X, `X_k` es el conjunto de los K vecinos, pero `k` también indexa al vecino; `X_{\mathrm{set}}` y `X_k^{i}` se definen de pasada.

**Fallo.** La definición formal no se puede leer sin adivinar qué es cada símbolo.

**Solución.** Renombrar el conjunto (por ejemplo `N_K(x)`) y separar índice de conjunto.

---

## Capítulo 6 — Inferencia estadística

**6.1** · `capitulos/06-inferencia.tex:117-153` · **alta**

**Descripción.** El teorema central del límite se enuncia como una explicación, sin hipótesis, y el de De Moivre-Laplace lleva la condición escrita con un `X_B` que no está definido en ninguna parte.

**Fallo.** Un enunciado que no es un enunciado no se puede demostrar ni citar, y el párrafo que los usa los menciona por su nombre sin `\cref`: los dos teoremas están en el aire.

**Solución.** Enunciarlos con hipótesis y fuente y referenciarlos con `\cref`, o sustituirlos por una remisión a Canavos sin reproducirlos como teoremas.

---

**6.2** · `capitulos/06-inferencia.tex:145 y tablas/t09_mcnemar.tex` · **alta**

**Descripción.** La tabla de contingencia de McNemar aparece dos veces —escrita a mano aquí y generada en el capítulo 9— y las dos dan intervalos distintos para la misma diferencia: +0,0020 [−0,0011; 0,0049] marginal frente a [−0,0013; 0,0049] por lámina, sin decir cuál es cuál.

**Fallo.** Dos resultados distintos para el mismo contraste en el mismo documento es lo que más rápido rompe la confianza del lector.

**Solución.** Dejar una sola tabla, la generada, y explicar los dos intervalos por separado en el texto.

---

**6.3** · `capitulos/06-inferencia.tex` · **media**

**Descripción.** El capítulo reúne herramientas con tres usos distintos —puntuación de STOOD-X, comparación de modelos y cuantificación de la incertidumbre— sin decir qué se usa para qué.

**Fallo.** El lector no sabe para qué están Mann-Whitney o McNemar hasta que los encuentra dos capítulos más adelante.

**Solución.** Un párrafo de apertura que asigne cada herramienta a su uso y remita al capítulo donde se aplica.

---

**6.4** · `capitulos/06-inferencia.tex:150 y 06:205` · **baja**

**Descripción.** Dos `\pendiente{planteamiento}` sobre secciones que ya tienen el planteamiento escrito.

**Fallo.** El lector cree que falta algo que está.

**Solución.** Eliminarlas.

---

**6.5** · `capitulos/06-inferencia.tex:250` · **baja**

**Descripción.** El intervalo por percentiles usa `\lceil` en los dos extremos.

**Fallo.** La corrección hace el intervalo asimétrico sin necesidad y no coincide con la convención habitual.

**Solución.** Fijar una convención y decirla.

---

## Capítulo 7 — Explicabilidad

**7.1** · `capitulos/07-explicabilidad.tex:9-16` · **alta**

**Descripción.** El capítulo abre con «Explicación sacada del libro Explainable AI… \pendiente{citar}», que es un recordatorio de trabajo, y el párrafo siguiente parece traducción literal del mismo libro, sin marca.

**Fallo.** Una nota de trabajo se imprime en la memoria y el pasaje que introduce es el de riesgo de plagio de la nota 2.2.

**Solución.** Sustituir la frase por la cita real del libro y reescribir el párrafo con redacción propia.

---

**7.2** · `capitulos/07-explicabilidad.tex:54` · **alta**

**Descripción.** «\emph{} Se trata de ~\cite{bach2015,montavon2019lrp} es una técnica de explicación aplicable…».

**Fallo.** El grupo vacío y la sintaxis dejan la frase sin sujeto; hoy se lee así en el PDF.

**Solución.** Reescribir con el sujeto explícito y la cita detrás.

---

**7.3** · `capitulos/07-explicabilidad.tex:71-90` · **alta**

**Descripción.** En la regla de propagación de LRP, el índice del sumatorio del denominador es el mismo `j` que etiqueta la relevancia que se calcula, y la frase que intenta arreglarlo («este último se denota $j$») se contradice a sí misma.

**Fallo.** La ecuación, tal como está, no es una regla de reparto válida.

**Solución.** Usar dos índices —uno para la neurona y otro para el recorrido— y reescribir la frase.

---

**7.4** · `capitulos/07-explicabilidad.tex:135-215` · **media**

**Descripción.** Hay dos entornos para la misma regla: LRP-ε completa en la línea 135 y vacía en la 202; y una definición de conservación, vacía en la 191, que la regla ya cumple.

**Fallo.** Parecen dos reglas distintas y no lo son.

**Solución.** Dejar una sola definición de LRP-ε y enunciar la conservación como proposición demostrada, no como definición.

---

**7.5** · `capitulos/07-explicabilidad.tex:54 y 07:100-104` · **baja**

**Descripción.** «recitificadores» por rectificadores, y «Sea LRP para redes…, compuesto por neuronas» es una frase sin verbo principal.

**Fallo.** Dos descuidos en la primera página del capítulo.

**Solución.** Corrección.

---

## Capítulo 8 — Materiales y métodos

**8.1** · `capitulos/08-materiales-metodos.tex:31-33` · **alta**

**Descripción.** Dos fragmentos de las notas están pegados tal cual: «G3 estan bien delimitadas y en g4 hay una organización más anormal…» y «Ambas son proliferacion tumorales…».

**Fallo.** No son texto de memoria: faltan concordancias y tildes y no se entiende la frase.

**Solución.** Redactarlos o moverlos a comentario hasta que se redacten.

---

**8.2** · `capitulos/08-materiales-metodos.tex:14-28` · **alta**

**Descripción.** Erratas y descuidos en el arranque: «hispatología», «cancer», «espcialmente», «clasificacion» tres veces, «proliferacion», «necrósis», «adíposo», «dificil», «Resnet50» y «los modelos de clasificar mal».

**Fallo.** Es el primer capítulo con contenido y concentra más erratas que el resto del documento junto.

**Solución.** Pasada de corrección antes de seguir.

---

**8.3** · `capitulos/08-materiales-metodos.tex:23-28` · **media**

**Descripción.** Los porcentajes de confusión no cierran: 23,21 % de error más 66,07 % de acierto dejan un 10,7 % sin explicar, y el texto afirma que el único error es con cribiformes; en el otro caso, 14,28 + 85,7 = 99,98.

**Fallo.** Un lector con calculadora encuentra el hueco en diez segundos.

**Solución.** Decir a qué clase van las imágenes restantes o dar el porcentaje sobre el total de la clase, y redondear de forma consistente.

---

**8.4** · `capitulos/08-materiales-metodos.tex:23-33` · **media**

**Descripción.** El análisis de las confusiones entre las 14 clases está en el capítulo de materiales.

**Fallo.** El lector lee el análisis de una matriz de confusión tres capítulos antes de ver la matriz.

**Solución.** Llevarlo al capítulo 9, junto a `fig:confusion-swin`.

---

**8.5** · `capitulos/08-materiales-metodos.tex:23` · **media**

**Descripción.** El texto remite a «la figura 9.10», escrita a mano.

**Fallo.** Hoy acierta, pero cualquier figura que se añada al capítulo 9 la deja apuntando a otra.

**Solución.** `\cref{fig:confusion-swin}`.

---

**8.6** · `capitulos/08-materiales-metodos.tex:12-52` · **media**

**Descripción.** El capítulo alterna la primera persona del plural («contábamos», «el primer reto al que nos enfrentamos») con la tercera del resto de la memoria.

**Fallo.** El registro cambia dentro del mismo capítulo y delata el origen de cada párrafo.

**Solución.** Unificar en impersonal.

---

**8.7** · `capitulos/08-materiales-metodos.tex:52` · **baja**

**Descripción.** «El repositorio cuenta con dos subcarpetas».

**Fallo.** Es el conjunto de datos, no el repositorio; y ese párrafo habla de los ficheros, no del código.

**Solución.** Cambiar el término.

---

**8.8** · `capitulos/08-materiales-metodos.tex:34 y 08:45` · **baja**

**Descripción.** El bloque de comentario `% En el preámbulo: \usepackage{booktabs}…` está duplicado.

**Fallo.** Ruido en el fuente, sin efecto en el PDF.

**Solución.** Borrar el duplicado.

---

## Capítulo 9 — Clasificación ID

**9.1** · `capitulos/09-clasificacion-id.tex:141-160` · **alta**

**Descripción.** El argumento de la elección —«se selecciona Swin por ser el que mejor resultado ha obtenido»— contradice el test que está tres párrafos más arriba: McNemar da p = 0,19 y ConvNeXt-S tiene mejor F1 macro y mejor *balanced accuracy*.

**Fallo.** El capítulo se apoya en una diferencia que él mismo demuestra no significativa; quien lea las dos partes se queda con la duda de si se entendió el test.

**Solución.** Presentarlo como empate técnico entre Swin-S y ConvNeXt-S y justificar la elección por un criterio distinto del resultado: coste, tamaño o transferencia a otros conjuntos.

---

**9.2** · `capitulos/09-clasificacion-id.tex` · **alta**

**Descripción.** Seis tablas y once figuras, y ningún párrafo de análisis: nueve `\pendiente{análisis}` y cinco conclusiones parciales vacías.

**Fallo.** Un capítulo de resultados sin análisis no es un capítulo de resultados, y el patrón del repositorio —tabla, análisis breve, conclusión parcial— está solo enunciado.

**Solución.** Escribir un párrafo por tabla o figura, empezando por las cinco matrices de confusión, que es donde están las confusiones entre clases (nota 8.4).

---

**9.3** · `capitulos/09-clasificacion-id.tex:34, 51, 69, 88 y 108` · **media**

**Descripción.** Cinco líneas sueltas con cifras y sin frase: «Pérdida en test: 0,6788; exactitud en test: 0,9525.»

**Fallo.** Son apuntes, no prosa, y hoy se imprimen tal cual.

**Solución.** Convertirlos en comentarios `%` o en la frase de análisis que les corresponde.

---

**9.4** · `capitulos/09-clasificacion-id.tex:148-161` · **media**

**Descripción.** «Tres pilares» con una enumeración de tres y, después, un `itemize` con un cuarto punto —«Complementariedad de enfoques»— fuera de la lista.

**Fallo.** El cuarto punto queda descolgado y sin numerar.

**Solución.** Integrarlo en la enumeración o convertirlo en párrafo.

---

**9.5** · `capitulos/09-clasificacion-id.tex:148-158` · **media**

**Descripción.** Los tres pilares no tienen cita, y la frase del «techo de rendimiento cercano al límite de información útil» no se apoya en ningún resultado.

**Fallo.** Son afirmaciones de autoridad sin fuente, y sobre ellas se apoya la elección del modelo.

**Solución.** Citar los pilares (Liu et al., 2021) y quitar o respaldar el techo de rendimiento.

---

## Capítulo 10 — Detección OOD

**10.1** · `capitulos/10-deteccion-ood.tex:26-28` · **alta**

**Descripción.** Siguen en el texto las dos afirmaciones que las marcas `\revisar` corrigen: que los métodos de características superan «de forma sistemática… en todos los conjuntos», cuando RMDS queda por debajo de MSP en LYM, y que el rango de FPR@95 vale para todos, cuando STOOD-X está en 0,349.

**Fallo.** El texto del autor contradice sus propios datos, y son las marcas naranjas del mismo párrafo las que lo señalan.

**Solución.** Reescribir las dos frases con los rangos correctos y quitar las marcas.

---

**10.2** · `capitulos/10-deteccion-ood.tex` · **alta**

**Descripción.** Quedan cinco conclusiones parciales y la integración final.

**Fallo.** Las secciones tienen análisis, pero el capítulo no cierra: no hay una frase que diga qué se concluye de cada bloque ni cómo se integran.

**Solución.** Escribir las cinco conclusiones parciales, una o dos frases cada una, y la discusión final.

---

**10.3** · `capitulos/10-deteccion-ood.tex:26` y §10.1 tras `tablas/t10_near` · **media**

**Descripción.** La sección de near-OOD se abre dos veces: el párrafo del autor y, después de la tabla, un párrafo que repite el título de la sección en negrita.

**Fallo.** El lector cree que empieza una sección nueva.

**Solución.** Fusionarlos en un solo arranque.

---

**10.4** · `capitulos/10-deteccion-ood.tex:75` · **media**

**Descripción.** Aquí se dice que «cerca de un tercio» de las imágenes de PANDA y del control saturan el estadístico, mientras el capítulo 11 da un 19 % para PANDA y un 66 % para TUM+NORM.

**Fallo.** Dos cifras incompatibles para el mismo fenómeno en capítulos consecutivos.

**Solución.** Dar la cifra del control de resolución —que es la que falta— y unificar las tres.

---

**10.5** · `capitulos/10-deteccion-ood.tex:97-98` · **media**

**Descripción.** «Al contrario de lo habitual en la literatura», sin cita.

**Fallo.** Afirma una tendencia general de la literatura sin respaldo, y sobre ella se apoya la hipótesis del *label smoothing*.

**Solución.** Citar los trabajos en los que MSP queda por debajo de MaxLogit y Energy.

---

**10.6** · `capitulos/10-deteccion-ood.tex:10` · **baja**

**Descripción.** El fichero de resultados del que salen todas las cifras (`faseC_2026-10-20`) está solo en un comentario.

**Fallo.** El lector no puede saber qué versión de los resultados está viendo.

**Solución.** Indicarlo en la introducción del capítulo o en el pie de las tablas.

---

## Capítulo 11 — STOOD-X

**11.1** · `capitulos/11-stoodx.tex:19-27` · **alta**

**Descripción.** El apartado que explica en qué difiere la implementación pública del artículo, y por qué se reimplementó, es un `\pendiente` y un `\revisar{tono}` vacíos.

**Fallo.** Sin ese apartado no se entiende por qué no se usó el código del artículo, que es lo normal, y es la primera pregunta que va a hacer el tribunal.

**Solución.** Escribirlo en tono descriptivo, teniendo en cuenta que el tutor es primer autor del método.

---

**11.2** · `capitulos/11-stoodx.tex:16` · **media**

**Descripción.** El capítulo no tiene introducción: arranca en «Implementación» con una sola frase.

**Fallo.** El lector pasa del capítulo 10 a un apartado técnico sin saber qué va a leer.

**Solución.** Tres o cuatro frases de presentación.

---

**11.3** · `capitulos/11-stoodx.tex` · **media**

**Descripción.** Seis `\pendiente{conclusión parcial}` y la discusión global, con el análisis del cuerpo ya escrito.

**Fallo.** El material está; solo falta cerrar cada sección, que es lo más barato del documento ahora mismo.

**Solución.** Una o dos frases por sección.

---

## Capítulo 12 — Predicción conforme

**12.1** · `capitulos/12-prediccion-conforme.tex` · **alta**

**Descripción.** Esqueleto: doce marcas y seis flotantes sin análisis, con las cifras en comentarios.

**Fallo.** Es el capítulo que conecta la parte estadística con la aplicación y hoy no tiene texto.

**Solución.** Escribirlo en el orden de las secciones, con las cifras que ya están en los comentarios.

---

**12.2** · `capitulos/12-prediccion-conforme.tex:10-16` · **alta**

**Descripción.** La limitación de intercambiabilidad —la validación se usó para elegir época y viene del `train` original, mientras que el test viene del `val` original— está solo en un comentario.

**Fallo.** De eso depende que las garantías de cobertura y de falsas alarmas signifiquen algo; si no se dice, el capítulo promete más de lo que puede dar.

**Solución.** Subirlo a la introducción del capítulo y a las limitaciones del 15, y repetirlo donde se interpretan las coberturas.

---

## Capítulo 13 — Fuga por lámina

**13.1** · `capitulos/13-fuga-lamina.tex` · **alta**

**Descripción.** Esqueleto: nueve marcas y cuatro tablas sin análisis.

**Fallo.** La fuga por lámina condiciona la interpretación de todos los resultados anteriores y hoy es un título con cifras en comentarios.

**Solución.** Escribirlo antes que los análisis del 9 y del 10, porque cambia qué se puede afirmar en ellos.

---

**13.2** · `capitulos/13-fuga-lamina.tex:27-28` · **media**

**Descripción.** La identificación de las láminas a partir del nombre de fichero se presenta como un hecho.

**Fallo.** Es una deducción —el propio capítulo la marca como no documentada— y presentada como hecho el tribunal la tomará por dato.

**Solución.** Presentarla como hipótesis con su evidencia: 95 prefijos, cuatro campos en el nombre y rejilla de 224 px frente al paso de 256 del artículo.

---

## Capítulo 14 — Explicabilidad y eliminación de sesgos

**14.1** · `capitulos/14-explicabilidad-sesgos.tex` · **alta**

**Descripción.** El capítulo está vacío, con un `\pendiente{capítulo en desarrollo}`.

**Fallo.** Es un objetivo del TFG y el capítulo 15 tiene que declarar si se alcanzó; tal como está, no se puede.

**Solución.** Decidir cuanto antes si entra completo, entra parcial con lo que haya de CRP, o se convierte en trabajo futuro y se quita del listado de objetivos.

---

## Capítulo 15 — Conclusiones y trabajo futuro

**15.1** · `capitulos/15-conclusiones.tex` · **alta**

**Descripción.** Veinticinco palabras; las conclusiones objetivo por objetivo están vacías.

**Fallo.** Es la sección que lee el tribunal entera y la única que no se puede escribir deprisa.

**Solución.** Escribirla al final, objetivo por objetivo, contra `sec:objetivos`, y responder a cada pregunta de investigación.

---

**15.2** · `capitulos/15-conclusiones.tex:18` · **media**

**Descripción.** La única frase existente —la detección OOD no protege frente a cambios en el criterio diagnóstico— está suelta al principio de las limitaciones.

**Fallo.** Es una buena idea sin desarrollo, y sin ella el resto de limitaciones no tiene hilo.

**Solución.** Desarrollarla como limitación principal y ordenar las demás detrás.

---

## Apéndices

**A.1** · `apendices/` · **media**

**Descripción.** El apéndice A no tiene texto, el B tiene un `\pendiente` y el C dos.

**Fallo.** Hoy el lector encuentra tablas y figuras sin una línea que le diga qué mirar.

**Solución.** Dos o tres frases por apéndice.

---

**A.2** · `apendices/B-anexo-nct.tex:8` · **baja**

**Descripción.** Los tamaños de ADI, BACK, DEB y MUC están solo en un comentario.

**Fallo.** El anexo no le dice nada al lector: ni qué son esas clases ni cuántas imágenes hay.

**Solución.** Pasar las cifras al texto.
