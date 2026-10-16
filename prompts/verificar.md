# Prompt para verificar preguntas

Usa un modelo distinto del que generó la pregunta, para que no comparta sus mismos puntos ciegos. La verificación tiene tres pasos y conviene hacerlos en conversaciones separadas. Usa la versión en inglés; la española se revisa después como traducción.

## Paso 0: solo las alternativas

Detecta pistas de redacción: si la respuesta se adivina sin leer la pregunta, la redacción la delata. Envía solo las alternativas, sin el enunciado, en un orden barajado.

---

Below are the options of a multiple-choice question, without the question itself. Based only on how they are written, which one is most likely the correct answer? If none stands out, say so.

{{alternativas_barajadas}}

Return only this JSON:

```json
{ "id": "{{id}}", "pick": "a", "confidence": 0.0, "cue": "" }
```

- `pick`: the option you would bet on, or `"none"`.
- `cue`: in one sentence, what in the wording made you pick it.

---

Repite el paso con otro orden de las alternativas. Si en las dos rondas elige la correcta con confianza mayor a 0,4, la pregunta tiene una pista y se reescribe.

## Paso A: responder sin ver la clave

Envía el enunciado y las alternativas (sin `answer`, `rationale` ni `explanation`).

---

You are a machine learning expert. Answer this multiple-choice question and assess its quality.

{{enunciado_y_alternativas}}

Return only this JSON:

```json
{
  "id": "{{id}}",
  "chosen": "a",
  "confidence": 0.0,
  "other_defensible": [],
  "bloom": "apply",
  "problems": []
}
```

- `chosen`: the option you think is correct.
- `confidence`: between 0 and 1.
- `other_defensible`: other options an expert could defend as correct.
- `bloom`: the cognitive process the question demands (remember, understand, apply, analyze, evaluate).
- `problems`: any that apply, each with one sentence of detail: `"ambiguous"`, `"factual_error"`, `"outdated"`, `"confusing_wording"`, `"implausible_distractor"`, `"negative_stem"`.

---

## Paso B: auditar con la clave

Envía la pregunta completa.

---

Review this multiple-choice question, which includes the correct answer and the explanations.

{{pregunta_completa_en_json}}

1. Check, claim by claim, that the marked answer is correct, that every `rationale` is true, that the `explanation` has no factual errors, and that the cited sources exist and support what is claimed. Do not assume a source exists because its title sounds plausible.
2. Check the item-writing rules of Haladyna, Downing and Rodriguez (2002): the central idea is in the stem; the stem is positive; options are homogeneous in content and grammar and similar in length; the correct option does not stand out as the longest or most qualified; there are no absolutes (always, never), no "all/none of the above", no overlapping options and no pair of exact opposites; every distractor is a plausible, real mistake.
3. Score difficulty with this rubric, from 0 to 2 per criterion, without looking at the question's `difficulty` field:

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| `steps` | One step to the answer | Two or three steps | Four or more |
| `specialization` | Covered in any introductory course | Learned by working in the field | Niche or research |
| `distractors` | Easy to rule out | One is plausible | Several match frequent mistakes |

4. Check that a `hard` question demands `analyze` or `evaluate`, not recall of a niche fact.
5. Check that the Spanish version says the same as the English one.

Return only this JSON:

```json
{
  "id": "{{id}}",
  "verdict": "ok",
  "errors": [],
  "writing_issues": [],
  "doubtful_sources": [],
  "bloom": "analyze",
  "rubric": { "steps": 0, "specialization": 0, "distractors": 0 },
  "translation_issues": []
}
```

- `verdict`: `"ok"`, `"fix"` or `"discard"`.

---

## Cómo decidir

| Resultado | Acción |
|---|---|
| Paso 0 elige la correcta con confianza en las dos rondas | Reescribir las alternativas: hay una pista |
| Paso A coincide con la clave, sin problemas ni otras defendibles, y paso B da `ok` | Pasa a revisión humana |
| Paso A no coincide con la clave | Revisar a mano: puede estar mal la clave o la pregunta ser ambigua |
| Hay `other_defensible` o el problema `ambiguous` | Reescribir o descartar |
| El Bloom estimado es más bajo que el declarado, o una difícil no exige analizar ni evaluar | Reescribir como escenario o bajar el nivel |
| Paso B da `fix` o reporta `writing_issues` | Corregir y volver a verificar |
| Paso B da `discard`, o hay fuentes dudosas sin reemplazo | Descartar |
| La suma de la rúbrica difiere en 2 puntos o más de la del generador | Decides tú el puntaje y el nivel |

Pasar la verificación no reemplaza la revisión humana: solo filtra los errores evidentes antes de que llegues tú.
