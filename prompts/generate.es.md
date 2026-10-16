# Prompt para generar preguntas

Este prompt se escribió originalmente en español; la versión en inglés es [`generate.md`](generate.md). Las dos dicen lo mismo, así que un cambio en una va también en la otra.

Reemplaza las variables entre `{{ }}` y envía el bloque completo a un LLM. Pide lotes pequeños (5 a 10 preguntas): la calidad cae en lotes grandes.

---

Eres un especialista en machine learning que escribe preguntas de opción múltiple para que profesionales aprendan. Escribe {{n}} preguntas nuevas sobre:

- Área: `{{area}}` ({{area_nombre}})
- Subtema: `{{subtopic}}` ({{subtema_nombre}})
- Nivel: `{{level}}`

Escribe cada pregunta primero en inglés y después en español. La versión en español es una traducción natural, no literal, con las mismas alternativas en el mismo orden. Usa español latinoamericano neutro y evita palabras regionales, como las chilenas «calzar», «ficha» o «chico» por «pequeño». Sigue la terminología de `docs/spanish-style.md`: conserva en inglés los términos que el campo usa así (chunk, embedding, few-shot, in-context learning, sycophancy, prompt sensitivity) y usa los términos en español ya establecidos (fragmento para un pasaje recuperado, variable para una feature de entrada, sobreajuste, alucinación).

## Nivel y taxonomía de Bloom

Cada pregunta declara el proceso cognitivo que exige (`bloom`), según la taxonomía de Bloom revisada:

| `bloom` | Qué hace quien responde |
|---|---|
| `remember` | Recupera un dato o una definición. |
| `understand` | Explica, clasifica, compara o interpreta un concepto. |
| `apply` | Usa un procedimiento o un concepto en un caso concreto, incluido un cálculo. |
| `analyze` | Separa un caso en partes y razona cómo se relacionan: explica observaciones, encuentra la causa. |
| `evaluate` | Juzga opciones con criterios explícitos y elige la mejor bajo restricciones. |

- `easy`: `remember` o `understand`.
- `medium`: `understand` o `apply` (a veces `analyze` en casos simples).
- `hard`: solo `analyze` o `evaluate`. Una pregunta difícil no es un dato de nicho para recordar: es un escenario nuevo que obliga a razonar. Si el tema es de nicho, eso sube la rúbrica, pero no basta.

Para niveles altos, usa material nuevo: un escenario con números u observaciones que no aparezca así en ningún libro, para que la pregunta no se responda reconociendo una frase.

## Rúbrica de dificultad

Puntúa cada pregunta con tres criterios, de 0 a 2 cada uno:

| Criterio | 0 | 1 | 2 |
|---|---|---|---|
| `steps` | Un paso hasta la respuesta | Dos o tres pasos | Cuatro o más |
| `specialization` | Está en cualquier curso introductorio | Se aprende trabajando en el área | Nicho o investigación |
| `distractors` | Se descartan con facilidad | Uno es plausible | Varios corresponden a errores frecuentes |

La suma de la rúbrica más el puntaje de Bloom (`remember` y `understand` 0, `apply` 1, `analyze` y `evaluate` 2) va de 0 a 8: 0–2 corresponde a `easy`, 3–5 a `medium` y 6–8 a `hard`. Puntúa la pregunta tal como quedó escrita. Si no coincide con el nivel pedido, reescríbela; no ajustes los puntajes para forzarla.

## Reglas de redacción (Haladyna, Downing y Rodriguez, 2002)

Enunciado:

1. La idea central va en el enunciado: quien lo lee debe poder responder sin mirar las alternativas.
2. Redacta en positivo. Evita "¿cuál NO…?"; si es imprescindible, destaca la negación.
3. Sin relleno: cada frase del enunciado es necesaria para responder.
4. Si una palabra se repite en todas las alternativas, muévela al enunciado.
5. El enunciado no debe apuntar a la respuesta. Si el nombre de un método o de un paper delata la alternativa correcta (ResNet y «residual», DDPM y «denoising»), cambia la redacción del enunciado o de las alternativas.

Alternativas:

6. Exactamente una correcta. Ningún experto debería poder defender otra.
7. Todas homogéneas en contenido y en estructura gramatical, y de largo parecido. La correcta no puede destacar por ser la más larga, la más matizada ni la única con una justificación. En el lote, la correcta debe ser la más larga solo en cerca de una de cada cuatro preguntas, y la más corta en otra cuarta parte, como pasaría al azar.
8. Sin absolutos (siempre, nunca, completamente, en todos los casos): delatan a las falsas.
9. Nada de "todas las anteriores", "ninguna de las anteriores" ni combinaciones como "A y B".
10. Cada distractor es un error que alguien comete de verdad: una confusión conocida, un paso mal hecho, una idea que fue cierta antes. Nada absurdo ni de relleno.
11. Las alternativas son independientes: no se traslapan y no forman pares de opuestos exactos que delaten la respuesta.
12. Tres alternativas bien hechas bastan (Rodriguez, 2005). Prefiere tres plausibles a cuatro con una absurda.
13. Si las alternativas tienen un orden natural (números, pasos), escríbelas en ese orden, marca `keep_order: true` y varía la posición de la correcta entre preguntas. Si no, el sitio las baraja.

## Explicaciones y fuentes

- Cada alternativa lleva un `rationale` de una o dos oraciones que explica por qué es correcta o incorrecta.
- La `explanation` tiene 2 a 4 oraciones y agrega algo que no está en las alternativas: el mecanismo, un número o una consecuencia práctica.
- Términos técnicos en inglés cuando así se usan en el campo (precision, recall, embedding, fine-tuning), también en la versión en español.
- Cita solo fuentes que sabes con certeza que existen: el paper original, un libro de texto estándar o documentación oficial. Nunca inventes una URL; si no estás seguro de la URL exacta, omite el campo `url`. Si no conoces una fuente confiable para una afirmación, cambia la pregunta.
- Cuando cites un resultado, di lo que la fuente reportó de verdad (qué modelo, qué benchmark, qué número), no una impresión general.
- No repitas ni parafrasees estas preguntas que ya existen en el subtema:

{{enunciados_existentes}}

## Formato de salida

Devuelve solo un arreglo JSON válido, sin texto antes ni después, donde cada elemento cumple el esquema de `schema/question.schema.json`:

- `id`: desde `{{area}}-{{primer_numero}}` en adelante, correlativos, con 4 dígitos.
- `version`: 1.
- `bloom`: uno de los cinco valores de la tabla.
- `format`: `"single"`, con 3 o 4 alternativas desde `a` y `answer` con un solo id.
- `difficulty`: la rúbrica, por ejemplo `{ "steps": 1, "specialization": 0, "distractors": 2 }`.
- Todos los textos como objetos de idioma: `{ "en": "...", "es": "..." }`.
- `origin`: `"llm_draft"`.
- `reviewed_at`: `"{{fecha}}"`. Si la vigencia es `slow` o `volatile`, agrega `review_by` a 1 año o 6 meses de esa fecha.

## Ejemplos del banco

{{dos_preguntas_de_ejemplo_en_json}}
