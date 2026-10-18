# Contributing

Thank you for helping. The bank is in alpha: a model drafted the questions and a person has not reviewed them all yet, so the most useful help is finding and fixing mistakes.

Issues and pull requests can be written in English or Spanish.

## Report a mistake

Under each question on the site there is a "Report a mistake" link. It opens an issue with the question's id and stem already filled in; add what is wrong and, if you can, a source. You can also [open an issue](https://github.com/CristobalSantana/ai-ml-questions/issues/new) directly.

Worth reporting:

- The key is wrong, or a second option is also defensible.
- A rationale or the explanation says something false.
- A source does not exist or does not support what the question says.
- The wording gives the answer away.
- The level does not match how hard the question is.
- The Spanish reads like a translation.

## Review the questions of an area

The questions are in `questions/<area>.json`, one file per area; the areas are listed in [`taxonomy.json`](taxonomy.json). Pick an area you know and, for each question, check that:

1. It can be answered without looking at the options, and the key is the only defensible answer.
2. Each rationale is true, and each wrong option is a mistake people actually make.
3. The sources exist and support the explanation.
4. The level fits: `easy` is introductory-course level, `medium` is for someone who works with ML, and `hard` is senior or research level ([Difficulty](docs/difficulty.md)).
5. The Spanish says the same as the English and follows the [Spanish style](docs/spanish-style.md).

Report what you find in an issue, one per question or one per area with a list, or fix it in a pull request.

## Propose a question

Open an issue with the stem, the options, the correct one, why each option is right or wrong, and a source. If you would rather write the JSON yourself, follow the steps for pull requests.

Write questions in your own words: do not copy them from books, courses or other sites.

## Pull requests

1. Edit `questions/<area>.json`. Every field is described in [Question format](docs/question-format.md), and the rules for writing questions are in [Writing rules](docs/writing-rules.md).
2. Follow these rules for the fields:
   - **`id`** never changes. A new question takes the number after the highest one in its file.
   - **`version`** goes up by 1 when a change could affect how people answer: the meaning of the stem or of an option, or the key. A fix that keeps the meaning does not change it. This keeps the statistics of each version comparable.
   - **`origin`** of a new question is `human` if you wrote it yourself and `llm_draft` if a model drafted it. Leave it as it is in existing questions; it changes to `llm_reviewed` when a review is approved.
   - **`reviewed_at`** is the date of the last review; update it if you checked the question against its sources. `slow` and `volatile` questions also need a later `review_by`.
   - English is required and Spanish optional, but every text of a question must have the same languages.
3. Run the validator:
   ```bash
   pip install jsonschema
   python scripts/validate.py
   ```
   It must end without errors. Warnings point at possible problems, such as a clue in the wording; check them.
4. To see your question on the site, follow [Run it locally](README.md#run-it-locally). Commit only your changes to `questions/`: the files that `build_site.py` writes in `site/` are regenerated after merging.
5. In the pull request, say what you changed and which sources you checked.

## Using a model

Most questions started as drafts written with a model, so using one to draft or translate is fine. What matters is that a person checks every fact and source: say in the pull request that you used a model and what you checked yourself. The prompts this project uses are in [`prompts/`](prompts/).

## Code

Bug fixes and improvements to the site, the validator or the scripts are welcome. The site is HTML, CSS and JavaScript without frameworks; [Website](docs/site.md) and [Hosting](docs/hosting.md) explain how it works. Code and comments are in English. For a large change, open an issue first so we can agree on the approach.

## License

By contributing, you agree that your questions are published under [CC BY-SA 4.0](LICENSE-QUESTIONS) and your code under [MIT](LICENSE), like the rest of the project.
