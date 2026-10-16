# Prompt for generating questions

Replace the variables in `{{ }}` and send the whole block to an LLM. Ask for small batches (5 to 10 questions): quality drops in large ones.

---

You are a machine learning specialist who writes multiple-choice questions to help professionals learn. Write {{n}} new questions about:

- Area: `{{area}}` ({{area_name}})
- Subtopic: `{{subtopic}}` ({{subtopic_name}})
- Level: `{{level}}`

Write each question first in English and then in Spanish. The Spanish version is a natural translation, not a literal one, with the same options in the same order. Use neutral Latin American Spanish and avoid regional words, such as Chilean «calzar», «ficha» or «chico» for "small". Follow the terminology in `docs/spanish-style.md`: keep the terms the field uses in English (chunk, embedding, few-shot, in-context learning, sycophancy, prompt sensitivity), and use the established Spanish ones (fragmento for a retrieved passage, variable for an input feature, sobreajuste, alucinación).

## Level and Bloom's taxonomy

Each question states the cognitive process it requires (`bloom`), following the revised Bloom's taxonomy:

| `bloom` | What the person answering does |
|---|---|
| `remember` | Retrieves a fact or a definition. |
| `understand` | Explains, classifies, compares or interprets a concept. |
| `apply` | Uses a procedure or a concept in a concrete case, including a calculation. |
| `analyze` | Breaks a case into parts and reasons about how they relate: explains observations, finds the cause. |
| `evaluate` | Judges options against explicit criteria and picks the best one under constraints. |

- `easy`: `remember` or `understand`.
- `medium`: `understand` or `apply` (sometimes `analyze` in simple cases).
- `hard`: only `analyze` or `evaluate`. A hard question is not a niche fact to recall: it is a new scenario that forces reasoning. A niche topic raises the rubric score, but that alone is not enough.

For the higher levels, use new material: a scenario with numbers or observations that do not appear that way in any book, so the question cannot be answered by recognizing a phrase.

## Difficulty rubric

Score each question on three criteria, from 0 to 2 each:

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| `steps` | One step to the answer | Two or three steps | Four or more |
| `specialization` | Covered in any introductory course | Learned by working in the field | Niche or research |
| `distractors` | Easy to rule out | One is plausible | Several match common mistakes |

The rubric sum plus the Bloom score (`remember` and `understand` 0, `apply` 1, `analyze` and `evaluate` 2) goes from 0 to 8: 0–2 corresponds to `easy`, 3–5 to `medium` and 6–8 to `hard`. Score the question as written. If it does not match the requested level, rewrite it; do not adjust the scores to force a match.

## Writing rules (Haladyna, Downing and Rodriguez, 2002)

Stem:

1. The central idea goes in the stem: a reader should be able to answer without looking at the options.
2. Phrase it positively. Avoid "which one is NOT…?"; if it is unavoidable, highlight the negation.
3. No filler: every sentence in the stem is needed to answer.
4. If a word repeats in every option, move it to the stem.
5. The stem must not point to the answer. If the name of a method or paper spells out the correct option (ResNet and "residual", DDPM and "denoising"), reword the stem or the options.

Options:

6. Exactly one correct option. No expert should be able to defend another one.
7. All homogeneous in content and grammatical structure, and of similar length. The correct option must not stand out as the longest, the most qualified or the only one with a justification. Across the batch, the correct option should be the longest in only about one question in four, and the shortest in about another quarter, as chance would give.
8. No absolutes (always, never, completely, in all cases): they give away the false options.
9. No "all of the above", "none of the above" or combinations such as "A and B".
10. Each distractor is a mistake people actually make: a known confusion, a step done wrong, an idea that used to be true. Nothing absurd and no filler.
11. The options are independent: they do not overlap and do not form pairs of exact opposites that give the answer away.
12. Three well-made options are enough (Rodriguez, 2005). Prefer three plausible options to four with an absurd one.
13. If the options have a natural order (numbers, steps), write them in that order, set `keep_order: true` and vary the position of the correct option across questions. Otherwise the site shuffles them.

## Explanations and sources

- Each option has a `rationale` of one or two sentences that explains why it is right or wrong.
- The `explanation` has 2 to 4 sentences and adds something that is not in the options: the mechanism, a number or a practical consequence.
- Keep technical terms in English where the field uses them that way (precision, recall, embedding, fine-tuning), also in the Spanish version.
- Cite only sources you are certain exist: the original paper, a standard textbook or official documentation. Never invent a URL; if you are not sure of the exact URL, leave out the `url` field. If you do not know a reliable source for a claim, change the question.
- When you cite a result, state what the source actually reported (which model, which benchmark, which number), not a general impression of it.
- Do not repeat or paraphrase these questions, which already exist in the subtopic:

{{existing_stems}}

## Output format

Return only a valid JSON array, with no text before or after it, where each element follows the schema in `schema/question.schema.json`:

- `id`: from `{{area}}-{{first_number}}` onward, consecutive, with 4 digits.
- `version`: 1.
- `bloom`: one of the five values in the table.
- `format`: `"single"`, with 3 or 4 options starting at `a`, and `answer` with a single id.
- `difficulty`: the rubric, for example `{ "steps": 1, "specialization": 0, "distractors": 2 }`.
- Every text as a language object: `{ "en": "...", "es": "..." }`.
- `origin`: `"llm_draft"`.
- `reviewed_at`: `"{{date}}"`. If the stability is `slow` or `volatile`, add `review_by` 1 year or 6 months after that date.

## Examples from the bank

{{two_example_questions_as_json}}
