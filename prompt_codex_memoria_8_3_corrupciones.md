# Prompt para Codex (memoria): corrupciones sintéticas en el § 8.3 «Conjuntos OOD» y la CEC en el capítulo 4

Excepción a la regla 3 de AGENTS.md: en esta subsección redacta un borrador de prosa, marcado entero con \revisar{borrador del agente, reescribir}

> Lanza Codex desde la raíz del repositorio de la memoria (`TFG-memoria`). Sigue **AGENTS.md** al pie de la letra.
>
> Fuentes de cifras, de solo lectura:
> - `/mnt/homeGPU/slcerro/OpenOOD/results_corrupciones/`: `resumen.md`, `decisiones.md`, `tiempos.md`, los CSV y `figuras_memoria/`.
> - El prompt de la fase 8, que tienes abajo, como contexto del diseño.
>
> Esta tarea es **solo la metodología**. Los resultados y su análisis van en otra tarea posterior, en el capítulo 10, después de `sec:ood-panda`.

## Objetivo

Incorporar a la memoria la descripción del experimento de **covariate shift sintético**: las corrupciones de Zhang et al. (2022) aplicadas al test ID. Hay que tocar tres sitios:
1. el § 8.3 (`sec:conjuntos-ood`);
2. la tabla `tab:diseno-ood`;
3. una definición nueva de la métrica CEC en el capítulo 4 (`sec:metricas`).

## Reglas (además de AGENTS.md)

- **El texto es del autor.** No redactes prosa nueva. Deja esqueletos: título, `\pendiente{}` y **todos los puntos y cifras en comentarios `%`**, ordenados tal como el autor los irá redactando. Se permiten frases técnicas mínimas, como el pie de la tabla y el de la figura o el enunciado formal de la definición. Todo lo que añadas va con `\revisar{añadido por el agente: …}`.
- Las cifras salen de `results_corrupciones/`. Si algo de este prompt no coincide con los ficheros de resultados, mandan los ficheros: márcalo con `\revisar{}` y dímelo.
- La prosa de `resumen.md` y `decisiones.md` **no se copia**; solo se usan sus cifras y hechos.
- No toques el capítulo 10 en esta tarea.

## 1. Subsección nueva en el § 8.3

Después de `\subsection{Control de resolución y DTD}` (`sec:control-dtd`) y antes de `\section{Entorno de ejecución}`, añade:

```latex
\subsection{Corrupciones sintéticas}\label{sec:corrupciones}
```

Su contenido es un esqueleto con `\pendiente{descripción de las corrupciones sintéticas}` y, en comentarios, los puntos siguientes. Comprueba cada cifra en los ficheros:

1. **Motivación.**
   - PANDA combina cambio de centro, de escala y de fondo, así que no aísla el efecto de cada uno.
   - Aquí se busca un *covariate shift* controlado y graduable, aplicado sobre las mismas imágenes del test ID.
   - Enlaza con `\cref{def:covariate-shift}`.
2. **Papel en el diseño: covariate shift sintético, no near-OOD.** La etiqueta de cada imagen no cambia; solo cambia P(X).
   - Enlaza con `\cref{def:deteccionfullspectrum}`: en la detección del espectro completo, estas imágenes se aceptarían como csID.
   - Aquí se evalúa si los detectores las señalan, con un criterio clínico: rechazar lo que el clasificador puede clasificar mal.
   - `\pendiente{justificación del autor}`.
3. **Generador.**
   - Banco de pruebas de Zhang et al. (MICCAI 2022), código público: commit `2b288c11f944192bea7ffae912687d27b3ad220f`. El repositorio no tiene licencia.
   - Son 9 corrupciones habituales en patología digital, con 5 niveles de severidad. Se usan los **niveles 1, 3 y 5**: 27 celdas, más la imagen limpia (nivel 0).
   - Antecedente en próstata: Schömig-Markiefka et al. (2021).
4. **Parámetros por corrupción y nivel:** van en una tabla generada (apartado 3). En el comentario, solo la referencia a la tabla.
5. **Cómo se aplican.**
   - Sobre las **12.618** imágenes del test ID (PNG RGB de 224 px), en píxeles uint8 y **antes** del redimensionado y de la normalización de ImageNet. Después sigue el mismo flujo de inferencia que el resto de conjuntos.
   - Solo el desenfoque por movimiento es aleatorio. Su semilla se deriva de forma determinista (SHA-256 del fichero, la corrupción y el nivel), así que cada imagen corrupta se puede regenerar. Comprobado: 23/23 regeneraciones idénticas bit a bit.
   - Marcas y burbujas: el código usa por defecto recursos de 96 px; se usaron los de 224 px del propio repositorio, sin modificar el código.
   - La implementación de `hue` (tono) está marcada en su código como poco fiable.
   - No se sustituyó ninguna corrupción.
6. **Qué no se incluye y por qué.**
   - No hay transformaciones geométricas: la orientación del tejido es arbitraria y el modelo se entrenó con volteo y rotación (§ del protocolo de entrenamiento).
   - El brillo y el contraste estaban en el aumento de datos del entrenamiento (`aug_transforms` de fastai, ±0,2, p = 0,75). Se mantiene el brillo como control: se espera que el modelo sea robusto a él.
7. **Diseño pareado.**
   - Las imágenes limpias son las ID y sus versiones corruptas de cada celda son las OOD.
   - Las referencias de los detectores son las mismas que en el resto del capítulo 10 (train limpio), sin reajustar nada.
   - Así el efecto de la corrupción queda aislado de cualquier diferencia de centro, escala o lámina.
8. **Métricas** (definidas en el capítulo 4; enlaza con `\cref`):
   - exactitud del clasificador por celda;
   - AUROC y FPR@95 por celda, con IC del 95 % por *bootstrap* pareado por imagen (1.000 réplicas, semilla 0);
   - CEC (apartado 4);
   - porcentaje de imágenes con la puntuación de STOOD-X saturada (`\cref{obs:u-empates}`);
   - correlación de Spearman entre la caída de exactitud y el AUROC sobre las 27 celdas.
9. **Muestra y ejecución.**
   - Se usó el test completo. La regla de recursos fijada de antemano daba una submuestra de 3.000, porque el test completo tardaba unas 14 h en CPU. El cambio se decidió **antes de ver resultados**.
   - Comprobación de que el nivel 0 reproduce la evaluación del resto del capítulo: predicciones idénticas al 100 %, Spearman ≥ 0,9999998 en todos los detectores y exactitud igual a la del test (comprueba que la cifra coincide con 0,9688 sin contradecir AGENTS.md).
   - El hardware va en el § Entorno de ejecución (apartado 6), no aquí.

**Figura:** copia `results_corrupciones/figuras_memoria/a_ejemplo_corrupciones.pdf` a `img/cap08/` y colócala en esta subsección.
- Pie, como frase técnica mínima: «Ejemplo de las nueve corrupciones de Zhang et al. en los niveles de severidad 1, 3 y 5 sobre una imagen del test ID. Fuente de las corrupciones: …».
- Comprueba en `decisiones.md` de qué imagen y clase se trata y ponlo en el pie.

## 2. Fila nueva en `tab:diseno-ood`

Añade una fila entre «Control de resolución» y «DTD»:
- Conjunto: «Corrupciones sintéticas (12.618 × 27)».
- Papel: «Covariate shift sintético».
- ¿Qué cambia?: «Las mismas imágenes del test ID con 9 corrupciones en 3 niveles de severidad».
- Objetivo: «Comprobar si el detector señala artefactos de adquisición y si su puntuación gradúa la severidad».

Márcala con `\revisar{fila añadida por el agente}`. Revisa que la tabla sigue cabiendo con `tabularx`.

## 3. Tabla generada de parámetros

En `scripts/generar_tablas.py`, añade la función `t08_corrupciones`. Debe leer los parámetros de un fichero de `results_corrupciones/`; si no existe un CSV de parámetros, usa el que se generó en el reconocimiento. Si solo están en `decisiones.md`, **no los copies a mano en el script**: dímelo y propón cómo exportarlos.

- Salida: `tablas/t08_corrupciones.tex`, con etiqueta `tab:corrupciones`.
- Columnas: corrupción, parámetro, nivel 1, nivel 3, nivel 5.
- Notas al pie: los recursos de 224 px de marcas y burbujas; `hue` marcada como poco fiable en el código original.
- Inclúyela en la subsección con `\input`.
- Ejecuta el script y comprueba que el resto de tablas no cambia (`git diff --stat tablas/`).

## 4. Definición de la CEC en el capítulo 4

En `capitulos/04-ood-metricas.tex`, dentro de `sec:metricas` y después de `sec:ccr`, añade:

```latex
\subsection{Estabilidad de la ordenación por severidad (CEC)}\label{sec:cec}
```

Contenido: `\pendiente{introducción del autor}` y un entorno `definicion` con el enunciado formal. Es texto técnico mínimo, márcalo con `\revisar{}`.

> Sean los niveles de severidad L = (ℓ₀ = 0, ℓ₁, …, ℓ_m), con m + 1 niveles, y s(x, c, ℓ) la puntuación de un detector, en la que un valor mayor significa más ID, para la imagen x con la corrupción c en el nivel ℓ (ℓ = 0 es la imagen limpia). Para cada par de niveles a < b, el par es **discordante** si s(x,c,ℓ_b) > s(x,c,ℓ_a) y **empatado** si son iguales. Se define
>
> CEC(x, c) = [#discordantes + ½ #empatados] / C(m+1, 2),
>
> y la CEC del detector es la media sobre las imágenes y las corrupciones. Vale 0 cuando la ordenación es perfectamente monótona, 0,5 cuando es la que daría el azar y 1 cuando el orden está invertido.

Además:
- **Observación**, en comentarios para que la redacte el autor: sin empates, CEC(x, c) = (1 − τ_a)/2, donde τ_a es la τ de Kendall entre la secuencia de puntuaciones y el orden de severidad. Comprobado numéricamente en `resumen.md` §7, con un error de 1,1e-16. Deja `\pendiente{proposición y demostración (autor)}`.
- **Adaptación de la métrica de Zhang et al.**, en comentarios: la definen con la confianza máxima del softmax y cuentan los pares discordantes ordenando con burbuja. Aquí se sustituye la confianza por la puntuación de cada detector, se normaliza por el número real de pares (6 con 4 niveles) y los empates cuentan ½. Su código usa 15 pares (6 niveles) y cuenta los empates como 1. Tono neutro: no decir que el artículo se equivoca.

## 5. Bibliografía

Hacen falta estas referencias. **No las completes de memoria.** Según AGENTS.md, las fuentes tienen que estar en `tfg-referencias/papers/`. Comprueba si están; si no, haz la lista y pídemelas.
- Zhang, Sun, Li, Zheng, Zhu y Yang, *Benchmarking the Robustness of Deep Neural Networks to Common Corruptions in Digital Pathology*, MICCAI 2022 (arXiv:2206.14973). Clave propuesta: `zhang2022corruptions`.
- Schömig-Markiefka et al., *Quality control stress test for deep learning-based diagnostic model in digital pathology*, Modern Pathology 34 (2021) 2098–2108, doi:10.1038/s41379-021-00859-x. Clave propuesta: `schomig2021`.
- Howard y Gugger, *Fastai: A Layered API for Deep Learning*, Information 11(2):108 (2020), doi:10.3390/info11020108, para `aug_transforms`. Mira si ya está en `library.bib` con otra clave.

Mientras falten los documentos, usa `\cite{}` con la clave propuesta y añade al `.bib` la entrada mínima, con `\revisar{entrada sin documento en tfg-referencias}` en el texto.

## 6. Entorno de ejecución (`sec:entorno`)

Solo en comentarios, añade un punto sobre el cálculo de las corrupciones:
- CPU de dionisio (Intel Xeon Silver 4216), 12 hilos, fp32, entorno `fastai_env_ood`.
- No se pudo usar GPU: la TITAN Xp de atenea (sm_61) no la soporta torch 2.8.0+cu128, y el resto de GPU estaban ocupadas.
- Tiempo de cálculo: 13 h 25 min; MaxRSS ≈ 10,6 GB.
- Wand 0.6.13 e ImageMagick 6.9.10, copiados en `results_corrupciones/pydeps/`.

## Entrega

- Compila con `latexmk -pdf tfg.tex` sin errores ni referencias rotas.
- Dame:
  - la lista de cambios con fichero y línea;
  - las discrepancias entre este prompt y los ficheros de resultados;
  - las referencias que faltan en `tfg-referencias/`;
  - la salida de `git status --short` y un mensaje de commit propuesto en una línea, sin trailers.
