# Documentation

The specification of [AI/ML Questions](../README.md): what the question bank contains, how each question is written and checked, and how the site works and is published. It describes version 2, from October 2026.

| Document | What it covers |
|---|---|
| [Question bank](question-bank.md) | Principles, target composition, the 17 areas and 8 topics, size goals |
| [Question format](question-format.md) | Question types, every field of a question, a full example |
| [Writing rules](writing-rules.md) | Item-writing rules, what the validator checks and what the model review checks |
| [Spanish style](spanish-style.md) | Terminology and style for the Spanish version of each question |
| [Difficulty](difficulty.md) | Levels, Bloom's taxonomy, the difficulty rubric and how it is calibrated with real answers |
| [Statistics](statistics.md) | What is recorded about each answer, how to get the data, and the difficulty, discrimination and distractors of each question |
| [Workflow](workflow.md) | How questions are generated, checked and published at scale |
| [Website](site.md) | Quiz rules, screens, sharing, offline use and languages |
| [Hosting](hosting.md) | Where the questions live, building the site, publishing on Cloudflare and visit analytics |

## Files

```
README.md, README.es.md      short introduction, in English and Spanish
CONTRIBUTING.md              how to report mistakes, review questions and propose new ones
docs/                        this documentation
docs/images/                 the screenshots in the READMEs, made by scripts/make_assets.py
LICENSE, LICENSE-QUESTIONS   licenses for the code (MIT) and the questions (CC BY-SA 4.0)
wrangler.jsonc               configuration of the Cloudflare Worker: publishes site/ and binds the D1 database
worker/index.js              the Worker's code: stores each answer, anonymously
migrations/0001_answers.sql  the table of answers in D1
taxonomy.json                8 topics, 17 areas and 203 subtopics, in English and Spanish
schema/question.schema.json  the format of a question (JSON Schema 2020-12)
questions/<area>.json        the questions, one file per area
scripts/validate.py          validates the bank, the writing rules and coverage (pip install jsonschema)
scripts/build_site.py        generates site/data, the counts in the header, site/precache.json and the service worker version
scripts/item_stats.py        statistics of each question from an export of the answers
scripts/make_assets.py       generates the icons, og-image.png and the README screenshots (pip install playwright pillow)
prompts/generate.md          prompt for generating batches of questions
prompts/review.md            prompt for reviewing questions with another model
prompts/*.es.md              the same two prompts in Spanish, the language they were first written in
site/index.html              the page and the tags for sharing
site/styles.css, fonts.css   styles and fonts
site/app.js                  the quiz logic; CONFIG and the interface texts (STRINGS) at the top
site/manifest.webmanifest    data for installing the site as an app
site/sw.js                   service worker for working offline
site/icons/, og-image.png    icons and the image for the share card
site/fonts/                  the fonts and their licenses
site/data/                   generated: taxonomy, index and questions per area
```

## Language

Everything in the repository is in English: code, comments, prompts, the schema, commit messages and this documentation. Spanish is for content people read on the site: the questions, the taxonomy names and the interface texts, plus the short [`README.es.md`](../README.es.md). The two prompts also keep their Spanish versions, [`generate.es.md`](../prompts/generate.es.md) and [`review.es.md`](../prompts/review.es.md), because they were first written in Spanish; each pair says the same thing.

## History

**Version 2 (October 2026)**

- English by default and Spanish as an option, in the interface and in the questions.
- New name, AI/ML Questions / Preguntas IA/ML, with an "alpha" badge.
- The site filters by 8 topics that group the 17 areas.
- Each question states its level in Bloom's taxonomy, and a hard question must require analyzing or evaluating.
- Haladyna's item-writing rules, checked by the validator and by a new step of the model review.
- The difficulty rubric uses Bloom instead of the old `cognitive` criterion.
- `keep_order` to show numeric options in order.
- The bank grew from 22 to 103 questions, starting with the context window and prompting.
- The site records each answer anonymously in Cloudflare D1, and `scripts/item_stats.py` computes the difficulty, discrimination and distractor statistics of each question.
