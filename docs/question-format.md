# Question format

Each file in `questions/` is a list of the questions in one area (`questions/llm.json`, and so on). The full schema is in [`schema/question.schema.json`](../schema/question.schema.json), and `python scripts/validate.py` checks every file against it.

## Question types

| Type (`type`) | What it is |
|---|---|
| `concept` | A definition or a mechanism. |
| `scenario` | A case with concrete constraints and a best decision. |
| `calculation` | A short calculation with numbers. |
| `code` | Read a code snippet, predict its output or find the bug. |
| `evidence` | An answer backed by a cited experimental result. |

"Why choose X over Y?" questions are always written as `scenario`, with volume, budget or other explicit constraints, because without context they have no right answer.

For now every question has a single answer (`format: "single"`) with 3 to 5 options. The `multiple` format (mark every correct option) remains available in the schema.

## Fields

| Field | Content |
|---|---|
| `id` | `<area>-<4 digits>`, for example `llm-0001`. Permanent: if the question is retired, its id is not reused. |
| `version` | Goes up when a change could affect how people answer: the meaning of the stem, of an option or the key. Wording and translation fixes that keep the meaning do not change it. This keeps answer statistics comparable. |
| `area`, `subtopic` | Ids from `taxonomy.json`. |
| `level` | `easy`, `medium` or `hard` ([Difficulty](difficulty.md)). |
| `bloom` | The cognitive process the question requires ([Difficulty](difficulty.md#blooms-taxonomy)). |
| `type`, `format` | The values above. |
| `stability` | `stable`, `slow` or `volatile` ([Question bank](question-bank.md#target-composition)). |
| `difficulty` | The up-front rubric: `steps`, `specialization` and `distractors`, from 0 to 2 each ([Difficulty](difficulty.md#up-front-rubric)). |
| `prompt` | The stem. |
| `options` | 3 to 5 options, each with `id` (a–e), `text` and `rationale`. |
| `keep_order` | Optional. With `true`, the site shows the options in the written order instead of shuffling them. |
| `answer` | List with the correct ids. |
| `explanation` | What is shown after answering, with context that does not fit in the options. |
| `hint` | Optional. |
| `code` | Required for `code` questions: `lang` and `source`. |
| `sources` | At least one: `kind`, `title` and, when they exist, `authors`, `year`, `url`. |
| `tags`, `collection` | Optional, for filtering. |
| `origin` | `human`, `llm_draft` (an unreviewed draft) or `llm_reviewed`. |
| `reviewed_at`, `review_by` | Last review and deadline for the next one. `review_by` is required for `slow` and `volatile`. |

## Languages

Every text is a map by language, `{ "en": "...", "es": "..." }`. English is required and Spanish optional, but a question must have the same languages in all its texts. The options and the answer are the same in every language. The Spanish version follows the [Spanish style](spanish-style.md) guide.

## Example

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

(Trimmed to two options for the example; the schema requires at least three.)
