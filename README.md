# AI/ML Questions · Preguntas IA/ML

Especificación v2 · 15 de octubre de 2026 · versión alfa

Un sitio gratuito para aprender conceptos de inteligencia artificial y machine learning con preguntas de opción múltiple, desde lo básico (qué es RAG) hasta lo de nicho (cuándo un LLM es determinista, KAN, PINN), en tres niveles. Está en inglés por defecto y se puede ver en español. No pide cuenta ni guarda datos personales; quien quiera puede donar por Ko-fi.

Este documento define qué contiene el banco, cómo se escribe cada pregunta, dónde se guarda y cómo se produce a escala.

**Cambios en v2**

- Inglés por defecto y español opcional, en la interfaz y en las preguntas (sección 14).
- Nombre nuevo, AI/ML Questions / Preguntas IA/ML, con la insignia «alpha» (sección 13).
- El sitio filtra por 8 contenidos que agrupan las 17 áreas (sección 6).
- Cada pregunta declara su nivel en la taxonomía de Bloom, y una difícil debe exigir analizar o evaluar (sección 3).
- Reglas de redacción de Haladyna, revisadas por el validador y por un paso nuevo de la verificación (sección 5).
- La rúbrica de dificultad usa Bloom en lugar del criterio `cognitive` (sección 12).
- `keep_order` para mostrar en orden las alternativas numéricas.

## 1. Principios

- **Aprender es el objetivo.** Cada alternativa explica por qué es correcta o incorrecta, y una pregunta difícil exige razonar, no recordar un dato raro.
- **Sin pistas en la redacción.** Se acierta por saber, no por cómo están escritas las alternativas.
- **Conocimiento estable primero.** La mayor parte del banco sale de lo que no cambia: matemáticas, modelos clásicos, papers, arquitecturas y definiciones establecidas. Lo que sí cambia se marca y tiene fecha de revisión.
- **Todo tiene fuente.** Un paper, un libro, documentación oficial, un post o un experimento reproducible.
- **Strange Machines es una capa encima.** Las preguntas que salen de los posts y de [ml-toy-experiments](https://github.com/CristobalSantana/ml-toy-experiments) llevan `collection: "strange-machines"` y enlazan al post o al experimento.
- **Gratis y sin cuentas.** El sitio no necesita saber quién responde.

## 2. Composición objetivo

| Vigencia (`stability`) | Qué incluye | Parte del banco | Revisión |
|---|---|---|---|
| `stable` | Matemáticas, ML clásico, papers, arquitecturas, definiciones establecidas | ~80% | Solo si alguien reporta un error |
| `slow` | Buenas prácticas y criterios de decisión: RAG o fine-tuning, sparse o dense | ~15% | Cada año (`review_by`) |
| `volatile` | Herramientas, productos, bases vectoriales específicas, fenómenos recién descritos | ~5% | Cada 6 meses (`review_by`) |

La colección `strange-machines` es transversal: una pregunta suya puede ser de cualquier vigencia.

## 3. Niveles y taxonomía de Bloom

| Nivel | Pelotita | Bloom | Qué exige | Ejemplo del banco |
|---|---|---|---|---|
| `easy` | Verde | `remember`, `understand` | Definir, reconocer o explicar un concepto. Nivel de un curso introductorio. | ¿Qué mide la similitud coseno entre dos embeddings? |
| `medium` | Amarilla | `understand`, `apply` | Aplicar un concepto, interpretar una métrica o hacer un cálculo corto. Nivel de alguien que trabaja con ML. | Calcular precision y recall en un problema de fraude. |
| `hard` | Roja | `analyze`, `evaluate` | Analizar un escenario nuevo o decidir entre opciones con varias restricciones. Nivel senior o de investigación. | Con temperatura 0, un modelo responde siempre igual en tu computador y a veces distinto en un servidor con carga. ¿Qué explica las dos observaciones? |

El campo `bloom` usa la taxonomía de Bloom revisada (Anderson y Krathwohl, 2001), que ordena los procesos cognitivos de menor a mayor exigencia:

| `bloom` | Qué hace quien responde | Puntaje en la rúbrica |
|---|---|---|
| `remember` | Recupera un dato o una definición. | 0 |
| `understand` | Explica, clasifica, compara o interpreta un concepto. | 0 |
| `apply` | Usa un procedimiento o un concepto en un caso concreto, incluido un cálculo. | 1 |
| `analyze` | Separa un caso en partes y razona cómo se relacionan: explica lo que se observa o encuentra la causa. | 2 |
| `evaluate` | Juzga opciones con criterios explícitos y elige la mejor bajo restricciones. | 2 |

El sexto nivel, `create`, no cabe en una pregunta de opción múltiple y queda fuera.

- **Una pregunta difícil no es un dato de nicho.** Un tema de nicho sube `specialization` en la rúbrica, pero una pregunta `hard` además debe ser `analyze` o `evaluate`, y el validador lo trata como error. Por eso las difíciles se escriben como escenarios nuevos, con números u observaciones que no aparecen así en ningún libro, para que no se respondan reconociendo una frase.
- Una pregunta `medium` es `understand` o `apply`, y a veces `analyze` en un caso simple. Una `easy` marcada `analyze` o `evaluate` genera un aviso.
- Regla práctica: si la respuesta aparece en la primera línea de un buscador, la pregunta no es difícil.

Las 103 preguntas actuales se reparten en `remember` 3, `understand` 45, `apply` 29, `analyze` 16 y `evaluate` 10.

El nivel se estima a priori con una rúbrica y se corrige con las respuestas reales (sección 12).

## 4. Tipos de pregunta

| Tipo (`type`) | Qué es |
|---|---|
| `concept` | Una definición o un mecanismo. |
| `scenario` | Un caso con restricciones concretas y una mejor decisión. |
| `calculation` | Un cálculo corto con números. |
| `code` | Leer un fragmento de código, predecir su salida o encontrar el error. |
| `evidence` | Una respuesta respaldada por un resultado experimental citado. |

Las preguntas del tipo "¿por qué elegir X sobre Y?" se escriben siempre como `scenario`, con volumen, presupuesto u otras restricciones explícitas, porque sin contexto no tienen una respuesta correcta.

Por ahora todas las preguntas son de una sola respuesta (`format: "single"`) con 3 a 5 alternativas. El formato `multiple` (marcar todas las correctas) queda disponible en el esquema.

## 5. Reglas de redacción

Las preguntas siguen las pautas de Haladyna, Downing y Rodriguez (2002), una revisión de 31 reglas para escribir preguntas de opción múltiple. Su propósito aquí es que la respuesta no se deduzca de la redacción: la correcta suele delatarse por ser la más larga, la más matizada o la única sin absolutos.

**El validador revisa** (`scripts/validate.py`, en cada idioma):

| Regla | Resultado |
|---|---|
| La correcta no es la alternativa más larga por más de 1,2 veces el promedio de los distractores | Aviso |
| La alternativa más larga no mide más de 2,5 veces la más corta | Aviso |
| Ninguna alternativa usa absolutos: always, never, completely; siempre, nunca, completamente… | Aviso |
| Ninguna alternativa dice «all/none of the above» ni «todas/ninguna de las anteriores» | Error |
| La pregunta está en positivo: sin not ni except; sin no, excepto ni salvo | Aviso |
| Una pregunta `hard` es `analyze` o `evaluate` | Error |

**La verificación con otro modelo revisa** lo que depende del significado ([`prompts/verificar.md`](prompts/verificar.md)):

- **Pistas en las alternativas (paso 0):** el modelo ve solo las alternativas, sin el enunciado, y apuesta por una. Si acierta con confianza en dos órdenes distintos, la redacción delata la respuesta y se reescribe.
- **Homogeneidad:** las alternativas tratan el mismo tipo de contenido con la misma forma gramatical, ninguna se traslapa con otra y no hay pares de opuestos exactos.
- **Distractores plausibles:** cada uno corresponde a un error que alguien comete de verdad.
- **La idea central va en el enunciado:** se puede responder sin mirar las alternativas.

Además:

- Tres alternativas bien hechas bastan (Rodriguez, 2005): mejor tres plausibles que cuatro con una absurda.
- El sitio baraja las alternativas en cada quiz. Las que tienen un orden natural (números, pasos) se muestran en el orden escrito con `keep_order: true`, y en ese caso quien escribe varía la posición de la correcta entre preguntas.

## 6. Taxonomía y contenidos

17 áreas y 203 subtemas, en [`taxonomy.json`](taxonomy.json). Cada pregunta pertenece a un área y a un subtema.

El sitio no muestra las 17 áreas: los filtros y el resultado usan 8 **contenidos** que las agrupan.

| Contenido (en · es) | Áreas | Incluye, por ejemplo |
|---|---|---|
| Classical machine learning · Machine learning tradicional | `math`, `ml-foundations`, `classical-ml`, `probabilistic`, `production`, `rl` | Álgebra lineal, sesgo y varianza, gradient boosting, ML bayesiano, dataset shift, Q-learning |
| Neural networks · Redes neuronales | `deep-learning`, `architectures` | Backpropagation, optimizadores, CNN, GAN, difusión, PINN, KAN |
| Transformers & LLMs · Transformers y LLMs | `llm`, `adaptation` | Atención, ventana de contexto, determinismo, prompting, LoRA, RLHF |
| Retrieval & RAG · Retrieval y RAG | `retrieval` | BM25, vectores sparse y densos, HNSW, bases vectoriales |
| Computer vision · Visión por computador | `vision` | Convolución, detección, segmentación, ViT, CLIP |
| Agents, harness & phenomena · Agentes, harness y fenómenos | `agents`, `phenomena` | Herramientas, ReAct, MCP, double descent, grokking, sycophancy |
| Evaluation & responsible AI · Evaluación e IA responsable | `evaluation`, `responsible` | Precision y recall, calibración, SHAP, equidad, privacidad |
| Landmark papers · Papers clave | `papers` | Del perceptrón (1958) a KAN (2024) |

- **Los contenidos son solo presentación.** Viven en `groups`, dentro de `taxonomy.json`, y las preguntas guardan su área y su subtema, no su contenido. Reagrupar es editar esa lista y volver a generar el sitio: no se toca ninguna pregunta y no se pierden estadísticas.
- El validador exige que cada área esté en exactamente un contenido.
- El muestreo del quiz usa las áreas (sección 9), así que reagrupar tampoco cambia qué preguntas salen.
- `rl` quedó en machine learning tradicional porque sus bases (MDP, Q-learning, policy gradients) son anteriores a los LLM. RLHF y DPO están en `adaptation`, dentro de Transformers y LLMs, junto al prompting y el fine-tuning.

| Área | Subtemas | Incluye, por ejemplo |
|---|---|---|
| `math` · Matemáticas para ML | 9 | Álgebra lineal, SVD, Bayes, MLE y MAP, entropía y KL |
| `ml-foundations` · Fundamentos de ML | 10 | Sesgo y varianza, regularización, validación cruzada, desbalance |
| `classical-ml` · Modelos clásicos | 13 | Regresión, SVM, árboles, gradient boosting, clustering, PCA |
| `evaluation` · Métricas y evaluación | 11 | Precision y recall, ROC y PR, calibración, skill scores, harness de evaluación |
| `deep-learning` · Redes neuronales y entrenamiento | 12 | Backpropagation, optimizadores, normalización, conexiones residuales |
| `architectures` · Arquitecturas | 17 | CNN, RNN, VAE, GAN, transformers, difusión, GNN, SSM, PINN, FNO, KAN |
| `llm` · Transformers y LLMs | 13 | Tokenización, atención, leyes de escala, decodificación, determinismo, KV cache |
| `adaptation` · Adaptación y alineamiento | 10 | Prompting, fine-tuning, LoRA, RLHF, DPO, destilación |
| `retrieval` · Retrieval, embeddings y RAG | 11 | BM25, vectores sparse y densos, HNSW, bases vectoriales, reranking |
| `agents` · Agentes y harness | 9 | Herramientas, bucle ReAct, memoria, harness, prompt injection, MCP |
| `probabilistic` · ML bayesiano e incertidumbre | 10 | Inferencia bayesiana, MCMC, inferencia variacional, procesos gaussianos, conformal |
| `production` · ML en producción | 9 | Dataset shift, detección de drift, leakage, monitoreo, serving |
| `vision` · Visión por computador | 10 | Convolución, detección, segmentación, ViT, CLIP |
| `rl` · Aprendizaje por refuerzo | 8 | MDP, Q-learning, policy gradients, PPO, diseño de recompensas |
| `responsible` · Interpretabilidad, equidad y seguridad | 7 | SHAP, interpretabilidad mecanicista, equidad, privacidad |
| `papers` · Papers clave | 28 | Del perceptrón (1958) y Attention Is All You Need (2017) a KAN (2024) |
| `phenomena` · Fenómenos de IA | 16 | Double descent, grokking, alucinación, sycophancy, model collapse |

Agregar un subtema es editar `taxonomy.json`. Los ids de áreas y subtemas no se cambian después, porque las preguntas los referencian.

## 7. Formato de una pregunta

Cada archivo de `questions/` es una lista de preguntas de un área (`questions/llm.json`, etc.). El esquema completo está en [`schema/question.schema.json`](schema/question.schema.json).

| Campo | Contenido |
|---|---|
| `id` | `<área>-<4 dígitos>`, por ejemplo `llm-0001`. Permanente: si la pregunta se retira, su id no se reutiliza. |
| `version` | Sube cuando cambia el enunciado, las alternativas o la respuesta, para no mezclar estadísticas. |
| `area`, `subtopic` | Ids de `taxonomy.json`. |
| `level`, `type`, `format`, `stability` | Los valores de las secciones 2 a 4. |
| `bloom` | El proceso cognitivo que exige la pregunta (sección 3). |
| `difficulty` | La rúbrica a priori: `steps`, `specialization` y `distractors`, de 0 a 2 cada uno (sección 12). |
| `prompt` | El enunciado. |
| `options` | 3 a 5 alternativas, cada una con `id` (a–e), `text` y `rationale`. |
| `keep_order` | Opcional. Con `true`, el sitio muestra las alternativas en el orden escrito en vez de barajarlas. |
| `answer` | Lista con los ids correctos. |
| `explanation` | Lo que se muestra después de responder, con contexto que no cabe en las alternativas. |
| `hint` | Opcional. |
| `code` | Obligatorio en preguntas de tipo `code`: `lang` y `source`. |
| `sources` | Al menos una: `kind`, `title` y, si existen, `authors`, `year`, `url`. |
| `tags`, `collection` | Opcionales, para filtrar. |
| `origin` | `human`, `llm_draft` (borrador sin revisar) o `llm_reviewed`. |
| `reviewed_at`, `review_by` | Última revisión y fecha límite para la próxima. `review_by` es obligatoria en `slow` y `volatile`. |

Todos los textos son mapas por idioma, `{ "en": "...", "es": "..." }`. El inglés es obligatorio y el español opcional, pero una pregunta debe tener los mismos idiomas en todos sus textos. Las alternativas y la respuesta son las mismas en todos los idiomas.

Ejemplo:

```json
{
  "id": "retrieval-0001",
  "version": 2,
  "area": "retrieval",
  "subtopic": "embeddings-similarity",
  "level": "easy",
  "bloom": "understand",
  "type": "concept",
  "format": "single",
  "stability": "stable",
  "difficulty": { "steps": 0, "specialization": 0, "distractors": 1 },
  "prompt": {
    "en": "What does the cosine similarity between two embeddings measure?",
    "es": "¿Qué mide la similitud coseno entre dos embeddings?"
  },
  "options": [
    {
      "id": "a",
      "text": {
        "en": "The angle between the two vectors, regardless of their lengths.",
        "es": "El ángulo entre los dos vectores, sin importar su largo."
      },
      "rationale": {
        "en": "cos θ = (a·b)/(‖a‖‖b‖). When the vectors are normalized to length 1, it equals the dot product.",
        "es": "cos θ = (a·b)/(‖a‖‖b‖). Si los vectores están normalizados a largo 1, es igual al producto punto."
      }
    },
    {
      "id": "b",
      "text": {
        "en": "The straight-line distance between the tips of the two vectors.",
        "es": "La distancia en línea recta entre las puntas de los vectores."
      },
      "rationale": {
        "en": "That is Euclidean distance, which depends on the vectors' lengths. Only for normalized vectors does it rank results the same way as cosine.",
        "es": "Esa es la distancia euclidiana, que depende del largo de los vectores. Solo con vectores normalizados ordena los resultados igual que el coseno."
      }
    }
  ],
  "answer": ["a"],
  "explanation": {
    "en": "With unit vectors, ‖a − b‖² = 2 − 2·cos θ, so cosine, dot product and Euclidean distance produce the same ranking. That is why embeddings are often normalized and compared with the dot product, which is cheaper to compute.",
    "es": "Con vectores unitarios, ‖a − b‖² = 2 − 2·cos θ, así que el coseno, el producto punto y la distancia euclidiana producen el mismo ranking. Por eso es común normalizar los embeddings y usar el producto punto, que es más barato de calcular."
  },
  "sources": [
    { "kind": "book", "title": "Introduction to Information Retrieval", "authors": "Christopher D. Manning, Prabhakar Raghavan & Hinrich Schütze", "year": 2008 }
  ],
  "origin": "llm_draft",
  "reviewed_at": "2026-10-15"
}
```

(Recortado a dos alternativas para el ejemplo; el esquema exige al menos tres.)

## 8. Dónde se guardan las preguntas

**No hace falta Supabase, Firebase ni una base de datos para las preguntas.** Son contenido de solo lectura que cambia cuando tú publicas, así que viven como JSON en este repositorio, con historial de cambios y revisión por pull request, y el sitio las sirve como archivos estáticos.

- **Tamaño, medido con las 103 preguntas actuales:** unos 3,5 KB por pregunta en JSON minificado con los dos idiomas, y 1,2 KB comprimido con gzip. 2.000 preguntas son unos 7 MB, o 2,5 MB comprimidos: unos 150 KB comprimidos por área. Con un archivo por área, el navegador descarga solo las áreas elegidas.
- **PWA:** en la primera visita, el service worker guarda todas las preguntas para que el sitio funcione sin conexión. Con 2.000 preguntas serían unos 2,5 MB comprimidos. Si eso pesa en el teléfono, `build_site.py` puede escribir un archivo por idioma, que reduce el tamaño a la mitad, o el service worker puede guardar cada área solo cuando se pide.
- **Hosting:** Cloudflare (Workers con assets estáticos, o Pages) o GitHub Pages. En Cloudflare, las peticiones a assets estáticos son gratuitas e ilimitadas.
- **Consecuencia aceptada:** las respuestas viajan al navegador, así que alguien que abra las herramientas de desarrollo puede verlas. En un sitio de práctica sin ranking da igual: hacer trampa solo perjudica a quien la hace.

### Cuándo sí hace falta un backend (fase 2)

| Necesidad | Por qué | Opción |
|---|---|---|
| Calibrar la dificultad con datos reales | Hay que guardar aciertos y errores por pregunta | Cloudflare Worker + D1 |
| Reportar errores desde el sitio | Un formulario que guarde el reporte | Worker + D1, o sin backend: un enlace que abre un issue en GitHub |
| Ranking o certificados | Hay que corregir en el servidor para que no se pueda hacer trampa | Worker + D1 |
| Cuentas y progreso entre dispositivos | Hace falta autenticación | Supabase (Postgres y Auth) |

**Recomendación: Cloudflare D1**, porque vive junto al hosting. Su plan gratuito da 5 millones de filas leídas y 100.000 escritas al día, con 5 GB de almacenamiento; desde el 1 de septiembre de 2026, al pasar el límite diario las consultas fallan hasta la medianoche UTC, algo aceptable para estadísticas. El plan gratuito de Supabase da 500 MB por proyecto y pausa los proyectos tras una semana sin actividad, lo que complica un sitio con tráfico esporádico. Firebase no aporta nada que este proyecto necesite.

Para las estadísticas basta guardar `(id, versión, alternativa elegida, acierto, fecha)`, sin IP ni identificadores de usuario.

## 9. Reglas del quiz

- **Cantidad:** 10, 25, 50, 100 o 200 preguntas. Si con los filtros elegidos hay menos, aparece la opción «Todas (N)».
- **Filtros:** niveles y contenidos. Colección y vigencia quedan para más adelante.
- **Muestreo:** estratificado por área y nivel, para que un quiz mezclado no quede dominado por el área con más preguntas. Usa las 17 áreas y no los 8 contenidos, para que reagrupar los contenidos no cambie qué preguntas salen. No repite preguntas dentro de un quiz y evita las vistas hace poco (historial en el navegador).
- **Alternativas barajadas** en cada quiz, salvo las de `keep_order`; por eso la respuesta se guarda por id y no por posición. En 500.000 barajadas de prueba, la correcta cayó en cada posición entre el 24,9% y el 25,1% de las veces.
- **Dificultad visible:** cada pregunta muestra una pelotita verde, amarilla o roja con el nivel escrito al lado, para no depender solo del color.
- **Modos:** estudio (explicación después de cada respuesta) y examen (resultado y explicaciones al final).
- **Quizzes largos:** 200 preguntas toman unas 2 a 3 horas, así que el avance se guarda en el navegador.
- **Al terminar:** puntaje por contenido y nivel, repaso de errores, resultado para compartir (sección 13) y botón de Ko-fi.
- **En cada pregunta:** botón para reportar un error y, en las `volatile`, la fecha de la última revisión.
- **Solo se publican** preguntas con `origin` `human` o `llm_reviewed`.

## 10. Cómo producir muchas preguntas

1. **Elegir una celda** (área × nivel) con pocas preguntas; el resumen de `scripts/validate.py` muestra la tabla.
2. **Generar un lote** con [`prompts/generar.md`](prompts/generar.md). El prompt pide cada pregunta en inglés y en español, con su nivel de Bloom y siguiendo las reglas de redacción. Todo lo generado entra como `llm_draft`.
3. **Validar** con `python scripts/validate.py`: el esquema, las reglas de redacción de la sección 5 y que la rúbrica calce con el nivel.
4. **Verificar con otro modelo** usando [`prompts/verificar.md`](prompts/verificar.md), en tres pasos: ver solo las alternativas (busca pistas), responder sin ver la clave, y auditar con la clave (hechos, fuentes, reglas de redacción, Bloom, rúbrica y traducción). Se reescribe o descarta toda pregunta con una pista, donde no coincida con la clave, donde dos alternativas sean defendibles o donde la explicación tenga un error.
5. **Revisar a mano** todas las difíciles, todas las de nicho y una muestra de las demás, incluida su versión en español. Al aprobar, `origin` pasa a `llm_reviewed`.
6. **Publicar** cuando `python scripts/validate.py --publish` pasa sin errores.
7. **Mantener:** el validador avisa cuando vence un `review_by`; los reportes de errores entran como issues.

Esfuerzo estimado: a 2 o 3 minutos de revisión por pregunta, 500 preguntas son entre 17 y 25 horas, algo más si se revisa a fondo la traducción.

## 11. Metas de volumen

Hay 51 celdas (17 áreas × 3 niveles). Hoy hay 103 preguntas, unas 2 por celda.

- **Primer lote (listo, octubre de 2026):** ventana de contexto y prompts, en los subtemas `llm/context-kv-cache`, `adaptation/prompting`, `adaptation/choosing-adaptation`, `agents/memory-context`, `agents/agent-security` (prompt injection), `phenomena/prompt-sensitivity` y `phenomena/in-context-learning`. Salió junto con preguntas de las demás áreas, y el banco pasó de 22 a 103 preguntas.
- **Lanzamiento:** unas 10 preguntas por celda, cerca de 500 en total.
- **Largo plazo:** unas 35 por celda, cerca de 1.800. Las áreas grandes (arquitecturas, LLMs, papers) pueden tener más y las pequeñas (RL, interpretabilidad) menos.

## 12. Dificultad

La dificultad se expresa con el índice de dificultad clásico: la proporción de personas que aciertan la pregunta, p. Cada color corresponde a una banda de p:

| Pelotita | Nivel | Aciertos esperados |
|---|---|---|
| Verde | `easy` | 70% o más |
| Amarilla | `medium` | Entre 40% y 70% |
| Roja | `hard` | Menos de 40% |

Con cuatro alternativas, quien responde al azar acierta un 25%, así que una pregunta difícil bien construida queda entre 25% y 40%.

### A priori: rúbrica

Antes de que haya respuestas, la banda se estima sumando el puntaje de Bloom (sección 3) y tres criterios de 0 a 2, guardados en el campo `difficulty`:

| Criterio | 0 | 1 | 2 |
|---|---|---|---|
| Bloom (`bloom`) | `remember` o `understand` | `apply` | `analyze` o `evaluate` |
| `steps` | Un paso hasta la respuesta | Dos o tres pasos | Cuatro o más |
| `specialization` | Está en cualquier curso introductorio | Se aprende trabajando en el área | Nicho o investigación |
| `distractors` | Se descartan con facilidad | Uno es plausible | Varios corresponden a errores frecuentes |

La suma va de 0 a 8: 0–2 es verde, 3–5 amarilla y 6–8 roja.

- Bloom reemplaza al criterio `cognitive` de v1, que medía lo mismo sin un marco reconocido.
- Además de la suma, el validador exige `analyze` o `evaluate` en toda pregunta `hard`. Una pregunta de nicho con buenos distractores puede sumar mucho, pero si solo pide recordar, su dificultad es de memoria y no de razonamiento.
- El validador avisa cuando `level` no coincide con lo que sugiere la rúbrica. Quien revisa puede mantener otro nivel si tiene una razón.
- En la verificación, un segundo modelo estima Bloom y puntúa la rúbrica sin ver lo que puso el generador. Si las sumas difieren en 2 puntos o más, decide quien revisa.
- Las 103 preguntas están puntuadas, y en todas la rúbrica coincide con el nivel.

### A posteriori: actualización bayesiana (fase 2)

Cuando haya estadísticas anónimas, cada pregunta parte de un prior Beta centrado en su banda, con media m = 0,80 (verde), 0,55 (amarilla) o 0,33 (roja) y un peso equivalente a n₀ = 10 respuestas. Si después la responden n personas y k aciertan, la estimación es:

```
p = (n₀ · m + k) / (n₀ + n)
```

Por ejemplo, una pregunta roja que responden 40 personas, de las cuales aciertan 30, queda en p = (3,3 + 30) / 50 ≈ 0,67 y pasa a amarilla.

- **Cambio de color:** cuando la pregunta tiene al menos 30 respuestas y p cae en otra banda, para que no cambie por el azar de las primeras respuestas.
- **Revisión:** si p queda bajo 0,30 con 30 respuestas o más, está cerca del azar, lo que suele delatar una clave equivocada o una pregunta ambigua.
- **Recalibrar la rúbrica:** como la rúbrica queda guardada junto al nivel medido, con suficientes datos se ajusta una regresión logística del acierto sobre Bloom y los tres criterios. Eso muestra cuáles predicen de verdad la dificultad, y la rúbrica pasa a ser un modelo entrenado con las respuestas.

### Discriminación y confiabilidad

- **Discriminación:** indica si aciertan más la pregunta quienes tienen mejor puntaje en el resto del quiz. Una correlación punto-biserial bajo 0,10 significa que la pregunta no distingue niveles; una negativa suele delatar una clave equivocada.
- **Confiabilidad:** el alfa de Cronbach mide la confiabilidad de una prueba fija, no la dificultad de una pregunta, y supone que todos responden las mismas preguntas. Como cada quiz sale al azar del banco, conviene un modelo de teoría de respuesta al ítem (Rasch o 2PL). Estima dificultad y discriminación en una escala común aunque cada persona vea preguntas distintas, y su confiabilidad marginal cumple el papel del alfa.

## 13. Sitio web

`site/` es un sitio estático: HTML, CSS y JavaScript sin frameworks ni dependencias externas, con las fuentes incluidas.

### Nombre

**AI/ML Questions** en inglés y **Preguntas IA/ML** en español, con la insignia «alpha» («alfa») mientras dure la versión alfa. Es descriptivo a propósito: dice qué es el sitio con las mismas palabras que alguien escribiría en un buscador. Para cambiarlo:

- `site/app.js`: `siteName` en `STRINGS.en` y en `STRINGS.es`.
- `site/index.html`: el `<title>`, `og:site_name` y el texto inicial del encabezado.
- `site/manifest.webmanifest`: `name` y `short_name`.
- `scripts/make_assets.py`: `NAME`. Después corre el script para regenerar `og-image.png`.

Para quitar la versión alfa, borra de `site/index.html` el `<span class="badge">`.

### Pantallas

1. **Inicio:** el nombre, el selector de idioma (EN/ES) y el objetivo del sitio. Después, dificultad (las tres pelotitas), contenidos, cantidad de preguntas y modo, con cuántas preguntas hay disponibles para esos filtros. Si hay un quiz a medias, ofrece retomarlo.
2. **Pregunta:** la pelotita con el nivel escrito al lado, el contenido y el subtema, el enunciado y las alternativas como burbujas de hoja de respuestas. En modo estudio, al responder se marca la correcta y aparecen la justificación de cada alternativa, la explicación y las fuentes. En el computador, las teclas 1 a 4 (o A a D) eligen y Enter sigue. El idioma se puede cambiar en medio del quiz sin perder el avance.
3. **Resultado:** puntaje, aciertos por dificultad y por contenido, el mensaje para compartir, Ko-fi y el repaso de errores, con la opción de repetir solo los que se fallaron.

### Compartir en LinkedIn

La URL para compartir de LinkedIn (`https://www.linkedin.com/sharing/share-offsite/?url=...`) solo acepta el enlace; el texto de la publicación no se puede precargar. Por eso el botón copia el mensaje al portapapeles y abre LinkedIn con el enlace, y la persona pega el texto. En el teléfono, el botón «Share…» («Compartir…») abre el menú nativo del sistema.

El mensaje se arma con el resultado, en el idioma elegido, y la persona puede editarlo antes de copiarlo:

```
I answered 25 AI and machine learning questions and got 19 right (76%).
🟢 Easy 8/8 · 🟡 Medium 8/12 · 🔴 Hard 3/5
Best topic: Neural networks. Hardest for me: Retrieval & RAG.
How many can you get? https://ai-ml-questions.strangemachines.workers.dev/
```

```
Respondí 25 preguntas de IA y machine learning y acerté 19 (76%).
🟢 Fácil 8/8 · 🟡 Medio 8/12 · 🔴 Difícil 3/5
Lo que mejor me fue: Redes neuronales. Lo que más me costó: Retrieval y RAG.
¿Cuánto sacas tú? https://ai-ml-questions.strangemachines.workers.dev/#es
```

- La línea de contenidos aparece solo si el quiz tuvo al menos dos contenidos con dos o más preguntas cada uno, y con resultados distintos.
- El enlace en español lleva `#es`, para que quien lo abra vea el sitio en español.

LinkedIn arma la tarjeta del enlace con las etiquetas Open Graph de `index.html`: el título «How much do you know about AI and machine learning?», la descripción y `og-image.png` (1200 × 627). La tarjeta está en inglés y es la misma para los dos idiomas, porque LinkedIn no lee lo que va después del `#`; una tarjeta en español necesitaría una ruta propia, como `/es/`, con sus propias etiquetas. Como el sitio es estático, la tarjeta es la misma para todos; una imagen con el puntaje de cada persona necesita un Worker que la genere (fase 2). LinkedIn guarda la tarjeta en caché, así que después de cambiarla hay que refrescarla con su Post Inspector.

### PWA

Con `manifest.webmanifest` y `sw.js`, el sitio se puede instalar en el teléfono y funciona sin conexión. En la primera visita, el service worker guarda lo que lista `precache.json` (la página, las fuentes, los íconos y todas las preguntas); después responde con lo guardado y lo actualiza en segundo plano. `scripts/build_site.py` cambia la versión del service worker cada vez que cambia un archivo, para que los navegadores descarguen lo nuevo.

### Generar y probar

```bash
python scripts/build_site.py                  # solo preguntas revisadas
python scripts/build_site.py --include-drafts # también borradores, para probar
python -m http.server 8000 --directory site   # abre http://localhost:8000
python scripts/make_assets.py                 # íconos y og-image.png (pip install playwright)
```

El service worker solo funciona en `localhost` o con HTTPS.

### Publicar en Cloudflare

El repositorio es [CristobalSantana/ai-ml-questions](https://github.com/CristobalSantana/ai-ml-questions). El sitio se publica como un Worker de Cloudflare llamado `ai-ml-questions`, conectado al repositorio con Workers Builds. [`wrangler.jsonc`](wrangler.jsonc) le dice que publique la carpeta `site/` tal cual, como archivos estáticos, sin paso de compilación, porque `site/data` ya viene generado en el repositorio.

- Cada push a `main` vuelve a publicar el sitio solo; el estado de cada publicación se ve en el panel de Cloudflare, en el Worker, pestaña **Deployments** o **Builds**.
- El `name` de `wrangler.jsonc` debe coincidir con el nombre del Worker en el panel.
- La dirección pública es https://ai-ml-questions.strangemachines.workers.dev/. Si cambia, o si se agrega un dominio propio en **Domains & Routes**, hay que actualizar `CONFIG.siteUrl` en `site/app.js` y las etiquetas `og:url` y `og:image` en `site/index.html`, porque LinkedIn necesita URLs absolutas.

Antes de cada push que cambie preguntas o el sitio, regenera `site/data` y la versión del service worker. Mientras las preguntas sigan como borradores (`llm_draft`), el sitio se publica con `python scripts/build_site.py --include-drafts`; cuando estén revisadas, sin esa opción.

`CONFIG` en `site/app.js` también guarda la página de Ko-fi (`kofiUrl`) y el enlace para reportar errores (`reportUrl`), que abre un issue en el repositorio.

## 14. Idioma

- **Inglés por defecto.** El sitio abre en inglés y se puede cambiar a español con el botón EN/ES; la elección queda guardada en el navegador.
- **Enlaces por idioma.** `#es` o `#en` al final del enlace abre el sitio en ese idioma. El orden de decisión es: el idioma del enlace, la elección guardada y, si no hay ninguna, inglés. El sitio no usa el idioma del navegador, para que el predeterminado sea siempre inglés.
- **Preguntas.** El inglés es obligatorio y el español opcional; si una pregunta no tiene español, se muestra en inglés. El resumen del validador cuenta cuántas preguntas tiene cada idioma.
- **Interfaz.** Los textos están en `STRINGS`, en `site/app.js`, uno por idioma. Agregar otro idioma es agregarlo a `CONFIG.languages`, a `STRINGS`, al esquema y a las preguntas.

Strange Machines y ml-toy-experiments están en inglés, lo que favorece al inglés por alcance; el español tiene menos competencia y queda disponible para el público de Chile y Latinoamérica.

## 15. Licencia

- Preguntas: CC BY-SA 4.0 ([`LICENSE-QUESTIONS`](LICENSE-QUESTIONS)). Cualquiera puede reutilizarlas si cita la fuente y comparte bajo la misma licencia.
- Código: MIT ([`LICENSE`](LICENSE)), como ml-toy-experiments.
- Fuentes: STIX Two Text, IBM Plex Sans e IBM Plex Mono, bajo la SIL Open Font License 1.1 (`site/fonts/OFL-*.txt`).

## 16. Archivos

```
README.md                    esta especificación
LICENSE, LICENSE-QUESTIONS   licencias del código (MIT) y de las preguntas (CC BY-SA 4.0)
wrangler.jsonc               configuración del Worker de Cloudflare que publica site/
taxonomy.json                8 contenidos, 17 áreas y 203 subtemas, en inglés y español
schema/question.schema.json  el formato de una pregunta (JSON Schema 2020-12)
questions/<área>.json        las preguntas, un archivo por área
scripts/validate.py          valida el banco, las reglas de redacción y la cobertura (pip install jsonschema)
scripts/build_site.py        genera site/data, site/precache.json y la versión del service worker
scripts/make_assets.py       genera los íconos y og-image.png (pip install playwright)
prompts/generar.md           prompt para generar lotes de preguntas
prompts/verificar.md         prompt para verificar preguntas con otro modelo
site/index.html              la página y las etiquetas para compartir
site/styles.css, fonts.css   estilos y fuentes
site/app.js                  la lógica del quiz; CONFIG y los textos (STRINGS) al inicio
site/manifest.webmanifest    datos para instalar la PWA
site/sw.js                   service worker para funcionar sin conexión
site/icons/, og-image.png    íconos y la imagen de la tarjeta para compartir
site/fonts/                  las fuentes y sus licencias
site/data/                   generado: taxonomía, índice y preguntas por área
```

Las 103 preguntas actuales cubren las 17 áreas, los tres niveles, las tres vigencias y los cinco niveles de Bloom, están en inglés y en español, y siguen marcadas como `llm_draft` hasta que las revises.

## Referencias

- Haladyna, T. M., Downing, S. M., & Rodriguez, M. C. (2002). A review of multiple-choice item-writing guidelines for classroom assessment. *Applied Measurement in Education*, 15(3), 309–333. https://doi.org/10.1207/S15324818AME1503_5
- Rodriguez, M. C. (2005). Three options are optimal for multiple-choice items: A meta-analysis of 80 years of research. *Educational Measurement: Issues and Practice*, 24, 3–13.
- Anderson, L. W., & Krathwohl, D. R. (Eds.). (2001). *A taxonomy for learning, teaching, and assessing: A revision of Bloom's taxonomy of educational objectives*. Longman.
