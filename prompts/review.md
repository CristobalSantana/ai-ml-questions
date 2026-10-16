# Prompt for reviewing questions

Use a different model from the one that generated the question, so it does not share the same blind spots. The review has three steps, best done in separate conversations. Use the English version; the Spanish one is checked afterwards as a translation.

## Step 0: options only

This step detects wording clues: if the answer can be guessed without reading the question, the wording gives it away. Send only the options, without the stem, in a shuffled order.

---

Below are the options of a multiple-choice question, without the question itself. Based only on how they are written, which one is most likely the correct answer? If none stands out, say so.

{{shuffled_options}}

Return only this JSON:

```json
{ "id": "{{id}}", "pick": "a", "confidence": 0.0, "cue": "" }
```

- `pick`: the option you would bet on, or `"none"`.
- `cue`: in one sentence, what in the wording made you pick it.

---

Repeat the step with the options in another order. If the model picks the correct option in both rounds with a confidence above 0.4, the question has a clue and is rewritten.

## Step A: answer without the key

Send the stem and the options (without `answer`, `rationale` or `explanation`).

---

You are a machine learning expert. Answer this multiple-choice question and assess its quality.

{{stem_and_options}}

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

## Step B: audit with the key

Send the full question.

---

Review this multiple-choice question, which includes the correct answer and the explanations.

{{full_question_as_json}}

1. Check, claim by claim, that the marked answer is correct, that every `rationale` is true, that the `explanation` has no factual errors, and that the cited sources exist and support what is claimed. Do not assume a source exists because its title sounds plausible.
2. Check the item-writing rules of Haladyna, Downing and Rodriguez (2002): the central idea is in the stem; the stem is positive and does not point to the answer; options are homogeneous in content and grammar and similar in length; the correct option does not stand out as the longest or most qualified; there are no absolutes (always, never), no "all/none of the above", no overlapping options and no pair of exact opposites; every distractor is a plausible, real mistake.
3. Score difficulty with this rubric, from 0 to 2 per criterion, without looking at the question's `difficulty` field:

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| `steps` | One step to the answer | Two or three steps | Four or more |
| `specialization` | Covered in any introductory course | Learned by working in the field | Niche or research |
| `distractors` | Easy to rule out | One is plausible | Several match frequent mistakes |

4. Check that a `hard` question demands `analyze` or `evaluate`, not recall of a niche fact.
5. Check that the Spanish version says the same as the English one, in neutral Latin American Spanish without regional words.

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

## How to decide

| Result | Action |
|---|---|
| Step 0 picks the correct option with confidence in both rounds | Rewrite the options: there is a clue |
| Step A matches the key, with no problems and no other defensible options, and step B returns `ok` | Goes on to human review |
| Step A does not match the key | Review by hand: the key may be wrong or the question ambiguous |
| There are `other_defensible` options or the `ambiguous` problem | Rewrite or discard |
| The estimated Bloom level is lower than the declared one, or a hard question does not require analyzing or evaluating | Rewrite it as a scenario or lower the level |
| Step B returns `fix` or reports `writing_issues` | Fix and review again |
| Step B returns `discard`, or there are doubtful sources with no replacement | Discard |
| The rubric sum differs by 2 points or more from the generator's | You decide the score and the level |

Passing this review does not replace human review: it only filters out the obvious mistakes before they reach you.
