# Workflow

How questions are produced, checked and published at scale.

1. **Pick a cell** (area × level) with few questions; the summary of `python scripts/validate.py` shows the table by topic and level.
2. **Generate a batch** with [`prompts/generate.md`](../prompts/generate.md). The prompt asks for each question in English and Spanish, with its Bloom level and following the [writing rules](writing-rules.md) and the [Spanish style](spanish-style.md). Ask for small batches (5 to 10 questions): quality drops in large ones. Everything generated enters as `llm_draft`.
3. **Validate** with `python scripts/validate.py`: the schema, the writing rules, the length limits and whether the rubric matches the level ([Difficulty](difficulty.md)). GitHub runs it, with the tests in `tests/`, on every pull request.
4. **Review with another model** using [`prompts/review.md`](../prompts/review.md), in three steps: look only at the options (to find clues), answer without seeing the key, and audit with the key (facts, sources, writing rules, Bloom, rubric and translation). A question is rewritten or discarded if it has a clue, if the model's answer does not match the key, if two options are defensible or if the explanation has a mistake.
5. **Review by hand** every hard question, every niche one and a sample of the rest, including the Spanish version. On approval, `origin` becomes `llm_reviewed`.
6. **Publish** when `python scripts/validate.py --publish` passes without errors, then rebuild the site ([Hosting](hosting.md#building-and-testing)).
7. **Maintain:** the validator warns when a `review_by` date has passed; mistake reports come in as GitHub issues, through the "Report a mistake" link on each question.

Estimated effort: at 2 to 3 minutes of review per question, 500 questions take between 17 and 25 hours, a bit more with a thorough check of the translation.

## What the October 2026 batch taught

The batch that took the bank from 22 to 103 questions went through two independent model reviews before publishing. They found one wrong key (a fairness question that misstated a theorem), two explanations with errors, one of which misdescribed its source, and about 45 smaller problems, such as clues in the wording and regional Spanish. The correct option was also the longest one in almost half the questions. A later pass fixed Spanish terms that read oddly, which led to the [Spanish style](spanish-style.md) guide. The prompts now ask for what those reviews caught, but the human review in step 5 is still the step that makes a question publishable.
