# AI/ML Questions

**English** · [Español](README.es.md)

Specification v2 · October 15, 2026 · alpha version

A free site for learning artificial intelligence and machine learning concepts through multiple-choice questions, from the basics (what RAG is) to niche topics (when an LLM is deterministic, KAN, PINN), at three levels. It opens in English and can be switched to Spanish. It asks for no account and stores no personal data; anyone who wants to can donate on Ko-fi.

This document defines what the bank contains, how each question is written, where it is stored and how questions are produced at scale.

**Changes in v2**

- English by default and Spanish as an option, in the interface and in the questions (section 14).
- New name, AI/ML Questions / Preguntas IA/ML, with an "alpha" badge (section 13).
- The site filters by 8 topics that group the 17 areas (section 6).
- Each question states its level in Bloom's taxonomy, and a hard question must require analyzing or evaluating (section 3).
- Haladyna's item-writing rules, checked by the validator and by a new step of the review (section 5).
- The difficulty rubric uses Bloom instead of the `cognitive` criterion (section 12).
- `keep_order` to show numeric options in order.

## 1. Principles

- **Learning is the goal.** Every option explains why it is right or wrong, and a hard question requires reasoning, not recalling an obscure fact.
- **No clues in the wording.** You get a question right by knowing the answer, not by how the options are written.
- **Stable knowledge first.** Most of the bank comes from what does not change: math, classical models, papers, architectures and established definitions. What does change is marked and has a review date.
- **Everything has a source.** A paper, a book, official documentation, a post or a reproducible experiment.
- **Strange Machines is a layer on top.** Questions that come from the posts and from [ml-toy-experiments](https://github.com/CristobalSantana/ml-toy-experiments) carry `collection: "strange-machines"` and link to the post or the experiment.
- **Free and without accounts.** The site does not need to know who is answering.

## 2. Target composition

| Stability (`stability`) | What it includes | Share of the bank | Review |
|---|---|---|---|
| `stable` | Math, classical ML, papers, architectures, established definitions | ~80% | Only if someone reports a mistake |
| `slow` | Good practices and decision criteria: RAG or fine-tuning, sparse or dense | ~15% | Every year (`review_by`) |
| `volatile` | Tools, products, specific vector databases, newly described phenomena | ~5% | Every 6 months (`review_by`) |

The `strange-machines` collection cuts across these classes: any of its questions can have any stability.

## 3. Levels and Bloom's taxonomy

| Level | Dot | Bloom | What it requires | Example from the bank |
|---|---|---|---|---|
| `easy` | Green | `remember`, `understand` | Define, recognize or explain a concept. Introductory-course level. | What does the cosine similarity between two embeddings measure? |
| `medium` | Yellow | `understand`, `apply` | Apply a concept, interpret a metric or do a short calculation. The level of someone who works with ML. | Compute precision and recall in a fraud problem. |
| `hard` | Red | `analyze`, `evaluate` | Analyze a new scenario or choose between options under several constraints. Senior or research level. | At temperature 0, a model always gives the same answer on your computer and sometimes a different one on a busy server. What explains both observations? |

The `bloom` field uses the revised Bloom's taxonomy (Anderson and Krathwohl, 2001), which orders cognitive processes from least to most demanding:

| `bloom` | What the person answering does | Rubric score |
|---|---|---|
| `remember` | Retrieves a fact or a definition. | 0 |
| `understand` | Explains, classifies, compares or interprets a concept. | 0 |
| `apply` | Uses a procedure or a concept in a concrete case, including a calculation. | 1 |
| `analyze` | Breaks a case into parts and reasons about how they relate: explains what is observed or finds the cause. | 2 |
| `evaluate` | Judges options against explicit criteria and picks the best one under constraints. | 2 |

The sixth level, `create`, does not fit a multiple-choice question and is left out.

- **A hard question is not a niche fact.** A niche topic raises `specialization` in the rubric, but a `hard` question must also be `analyze` or `evaluate`, and the validator treats anything else as an error. That is why hard questions are written as new scenarios, with numbers or observations that do not appear that way in any book, so they cannot be answered by recognizing a phrase.
- A `medium` question is `understand` or `apply`, and sometimes `analyze` in a simple case. An `easy` one marked `analyze` or `evaluate` triggers a warning.
- Rule of thumb: if the answer shows up in the first line of a search engine, the question is not hard.

The current 103 questions break down into `remember` 3, `understand` 45, `apply` 29, `analyze` 16 and `evaluate` 10.

The level is estimated up front with a rubric and corrected with real answers (section 12).

## 4. Question types

| Type (`type`) | What it is |
|---|---|
| `concept` | A definition or a mechanism. |
| `scenario` | A case with concrete constraints and a best decision. |
| `calculation` | A short calculation with numbers. |
| `code` | Read a code snippet, predict its output or find the bug. |
| `evidence` | An answer backed by a cited experimental result. |

"Why choose X over Y?" questions are always written as `scenario`, with volume, budget or other explicit constraints, because without context they have no right answer.

For now every question has a single answer (`format: "single"`) with 3 to 5 options. The `multiple` format (mark every correct option) remains available in the schema.

## 5. Writing rules

The questions follow the guidelines of Haladyna, Downing and Rodriguez (2002), a review of 31 rules for writing multiple-choice questions. Their purpose here is that the answer cannot be deduced from the wording: the correct option tends to give itself away by being the longest, the most qualified or the only one without absolutes.

**The validator checks** (`scripts/validate.py`, in each language):

| Rule | Result |
|---|---|
| The correct option is not longer than 1.2 times the distractors' average | Warning |
| The longest option is at most 2.5 times as long as the shortest | Warning |
| No option uses absolutes: always, never, completely; siempre, nunca, completamente… | Warning |
| No option says "all/none of the above" or «todas/ninguna de las anteriores» | Error |
| The question is phrased positively: no "not" or "except"; no «no», «excepto» or «salvo» | Warning |
| A `hard` question is `analyze` or `evaluate` | Error |

The validator summary also shows in what share of the bank the correct option is the longest one and in what share it is the shortest. With four options, chance gives about 25% for each; a very high share for "longest" is a clue people learn even when every question passes the 1.2× rule. In the October 2026 review it went down from 46% to 20% in English.

**The review with another model checks** what depends on meaning ([`prompts/verificar.md`](prompts/verificar.md)):

- **Clues in the options (step 0):** the model sees only the options, without the stem, and bets on one. If it gets it right with confidence in two different orders, the wording gives the answer away and the question is rewritten.
- **Homogeneity:** the options cover the same kind of content with the same grammatical form, none overlaps another and there are no pairs of exact opposites.
- **Plausible distractors:** each one matches a mistake people actually make.
- **The central idea is in the stem:** the question can be answered without looking at the options.

Also:

- Three well-made options are enough (Rodriguez, 2005): three plausible options beat four with an absurd one.
- The site shuffles the options in each quiz. Options with a natural order (numbers, steps) are shown in the written order with `keep_order: true`, and then the author varies the position of the correct option from question to question.

## 6. Taxonomy and topics

17 areas and 203 subtopics, in [`taxonomy.json`](taxonomy.json). Each question belongs to one area and one subtopic.

The site does not show the 17 areas: the filters and the results use 8 **topics** that group them.

| Topic (en · es) | Areas | Includes, for example |
|---|---|---|
| Classical machine learning · Machine learning tradicional | `math`, `ml-foundations`, `classical-ml`, `probabilistic`, `production`, `rl` | Linear algebra, bias and variance, gradient boosting, Bayesian ML, dataset shift, Q-learning |
| Neural networks · Redes neuronales | `deep-learning`, `architectures` | Backpropagation, optimizers, CNNs, GANs, diffusion, PINNs, KANs |
| Transformers & LLMs · Transformers y LLMs | `llm`, `adaptation` | Attention, context window, determinism, prompting, LoRA, RLHF |
| Retrieval & RAG · Retrieval y RAG | `retrieval` | BM25, sparse and dense vectors, HNSW, vector databases |
| Computer vision · Visión por computador | `vision` | Convolution, detection, segmentation, ViT, CLIP |
| Agents, harness & phenomena · Agentes, harness y fenómenos | `agents`, `phenomena` | Tools, ReAct, MCP, double descent, grokking, sycophancy |
| Evaluation & responsible AI · Evaluación e IA responsable | `evaluation`, `responsible` | Precision and recall, calibration, SHAP, fairness, privacy |
| Landmark papers · Papers clave | `papers` | From the perceptron (1958) to KAN (2024) |

- **Topics are only presentation.** They live in `groups`, inside `taxonomy.json`, and questions store their area and subtopic, not their topic. Regrouping means editing that list and rebuilding the site: no question is touched and no statistics are lost.
- The validator requires each area to belong to exactly one topic.
- Quiz sampling uses the areas (section 9), so regrouping does not change which questions come up either.
- `rl` stayed in classical machine learning because its foundations (MDPs, Q-learning, policy gradients) predate LLMs. RLHF and DPO are in `adaptation`, under Transformers & LLMs, next to prompting and fine-tuning.

| Area | Subtopics | Includes, for example |
|---|---|---|
| `math` · Math for ML | 9 | Linear algebra, SVD, Bayes, MLE and MAP, entropy and KL |
| `ml-foundations` · ML foundations | 10 | Bias and variance, regularization, cross-validation, class imbalance |
| `classical-ml` · Classical models | 13 | Regression, SVMs, trees, gradient boosting, clustering, PCA |
| `evaluation` · Metrics and evaluation | 11 | Precision and recall, ROC and PR, calibration, skill scores, evaluation harnesses |
| `deep-learning` · Neural networks and training | 12 | Backpropagation, optimizers, normalization, residual connections |
| `architectures` · Architectures | 17 | CNNs, RNNs, VAEs, GANs, transformers, diffusion, GNNs, SSMs, PINNs, FNOs, KANs |
| `llm` · Transformers and LLMs | 13 | Tokenization, attention, scaling laws, decoding, determinism, KV cache |
| `adaptation` · Adaptation and alignment | 10 | Prompting, fine-tuning, LoRA, RLHF, DPO, distillation |
| `retrieval` · Retrieval, embeddings and RAG | 11 | BM25, sparse and dense vectors, HNSW, vector databases, reranking |
| `agents` · Agents and harness | 9 | Tools, the ReAct loop, memory, harnesses, prompt injection, MCP |
| `probabilistic` · Bayesian ML and uncertainty | 10 | Bayesian inference, MCMC, variational inference, Gaussian processes, conformal prediction |
| `production` · ML in production | 9 | Dataset shift, drift detection, leakage, monitoring, serving |
| `vision` · Computer vision | 10 | Convolution, detection, segmentation, ViT, CLIP |
| `rl` · Reinforcement learning | 8 | MDPs, Q-learning, policy gradients, PPO, reward design |
| `responsible` · Interpretability, fairness and safety | 7 | SHAP, mechanistic interpretability, fairness, privacy |
| `papers` · Landmark papers | 28 | From the perceptron (1958) and Attention Is All You Need (2017) to KAN (2024) |
| `phenomena` · AI phenomena | 16 | Double descent, grokking, hallucination, sycophancy, model collapse |

Adding a subtopic means editing `taxonomy.json`. Area and subtopic ids never change afterwards, because questions refer to them.

## 7. Question format

Each file in `questions/` is a list of the questions in one area (`questions/llm.json`, and so on). The full schema is in [`schema/question.schema.json`](schema/question.schema.json).

| Field | Content |
|---|---|
| `id` | `<area>-<4 digits>`, for example `llm-0001`. Permanent: if the question is retired, its id is not reused. |
| `version` | Goes up when the stem, the options or the answer change, so statistics are not mixed. |
| `area`, `subtopic` | Ids from `taxonomy.json`. |
| `level`, `type`, `format`, `stability` | The values in sections 2 to 4. |
| `bloom` | The cognitive process the question requires (section 3). |
| `difficulty` | The up-front rubric: `steps`, `specialization` and `distractors`, from 0 to 2 each (section 12). |
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

Every text is a map by language, `{ "en": "...", "es": "..." }`. English is required and Spanish optional, but a question must have the same languages in all its texts. The options and the answer are the same in every language.

Example:

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

## 8. Where the questions are stored

**The questions need no Supabase, Firebase or database.** They are read-only content that changes when you publish, so they live as JSON in this repository, with change history and review by pull request, and the site serves them as static files.

- **Size, measured with the current 103 questions:** about 3.5 KB per question as minified JSON with both languages, and 1.2 KB compressed with gzip. 2,000 questions come to about 7 MB, or 2.5 MB compressed: about 150 KB compressed per area. With one file per area, the browser downloads only the chosen areas.
- **PWA:** on the first visit, the service worker stores every question so the site works offline. With 2,000 questions that would be about 2.5 MB compressed. If that is too heavy for phones, `build_site.py` can write one file per language, which halves the size, or the service worker can store each area only when it is requested.
- **Hosting:** Cloudflare (Workers with static assets, or Pages) or GitHub Pages. On Cloudflare, requests for static assets are free and unlimited.
- **Accepted trade-off:** the answers travel to the browser, so anyone who opens the developer tools can see them. On a practice site without rankings this does not matter: cheating only hurts the cheater.

### When a backend is needed (phase 2)

| Need | Why | Option |
|---|---|---|
| Calibrating difficulty with real data | Right and wrong answers must be stored per question | Cloudflare Worker + D1 |
| Reporting mistakes from the site | A form that stores the report | Worker + D1, or no backend: a link that opens a GitHub issue |
| Rankings or certificates | Answers must be graded on the server so nobody can cheat | Worker + D1 |
| Accounts and progress across devices | Authentication is needed | Supabase (Postgres and Auth) |

**Recommendation: Cloudflare D1**, because it lives next to the hosting. Its free plan gives 5 million rows read and 100,000 rows written per day, with 5 GB of storage; since September 1, 2026, once the daily limit is reached, queries fail until midnight UTC, which is acceptable for statistics. Supabase's free plan gives 500 MB per project and pauses projects after a week without activity, which complicates a site with sporadic traffic. Firebase offers nothing this project needs.

For statistics it is enough to store `(id, version, chosen option, correct, date)`, with no IP addresses or user identifiers.

## 9. Quiz rules

- **Count:** 10, 25, 50, 100 or 200 questions. If fewer questions match the chosen filters, an "All (N)" option appears.
- **Filters:** levels and topics. Collection and stability are left for later.
- **Sampling:** stratified by area and level, so a mixed quiz is not dominated by the area with the most questions. It uses the 17 areas, not the 8 topics, so regrouping topics does not change which questions come up. It never repeats a question within a quiz and avoids recently seen ones (history stored in the browser).
- **Shuffled options** in each quiz, except with `keep_order`; that is why the answer is stored by id and not by position. In 500,000 test shuffles, the correct option landed in each position between 24.9% and 25.1% of the time.
- **Visible difficulty:** each question shows a green, yellow or red dot with the level written next to it, so it does not rely on color alone.
- **Modes:** study (explanation after each answer) and exam (score and explanations at the end).
- **Long quizzes:** 200 questions take about 2 to 3 hours, so progress is saved in the browser.
- **At the end:** score by topic and level, review of mistakes, a result to share (section 13) and a Ko-fi button.
- **On each question:** a button to report a mistake and, for `volatile` questions, the date of the last review.
- **Only questions** with `origin` `human` or `llm_reviewed` are published.

## 10. How to produce many questions

1. **Pick a cell** (area × level) with few questions; the summary of `scripts/validate.py` shows the table.
2. **Generate a batch** with [`prompts/generar.md`](prompts/generar.md). The prompt asks for each question in English and Spanish, with its Bloom level and following the writing rules. Everything generated enters as `llm_draft`.
3. **Validate** with `python scripts/validate.py`: the schema, the writing rules of section 5 and whether the rubric matches the level.
4. **Review with another model** using [`prompts/verificar.md`](prompts/verificar.md), in three steps: look only at the options (to find clues), answer without seeing the key, and audit with the key (facts, sources, writing rules, Bloom, rubric and translation). A question is rewritten or discarded if it has a clue, if the model's answer does not match the key, if two options are defensible or if the explanation has a mistake.
5. **Review by hand** every hard question, every niche one and a sample of the rest, including the Spanish version. On approval, `origin` becomes `llm_reviewed`.
6. **Publish** when `python scripts/validate.py --publish` passes without errors.
7. **Maintain:** the validator warns when a `review_by` date has passed; mistake reports come in as issues.

Estimated effort: at 2 to 3 minutes of review per question, 500 questions take between 17 and 25 hours, a bit more with a thorough check of the translation.

## 11. Volume goals

There are 51 cells (17 areas × 3 levels). Today there are 103 questions, about 2 per cell.

- **First batch (done, October 2026):** context window and prompts, in the subtopics `llm/context-kv-cache`, `adaptation/prompting`, `adaptation/choosing-adaptation`, `agents/memory-context`, `agents/agent-security` (prompt injection), `phenomena/prompt-sensitivity` and `phenomena/in-context-learning`. It shipped together with questions from the other areas, and the bank went from 22 to 103 questions.
- **Launch:** about 10 questions per cell, around 500 in total.
- **Long term:** about 35 per cell, around 1,800. Large areas (architectures, LLMs, papers) can have more and small ones (RL, interpretability) fewer.

## 12. Difficulty

Difficulty is expressed with the classical difficulty index: the proportion of people who answer the question correctly, p. Each color corresponds to a band of p:

| Dot | Level | Expected share of correct answers |
|---|---|---|
| Green | `easy` | 70% or more |
| Yellow | `medium` | Between 40% and 70% |
| Red | `hard` | Under 40% |

With four options, someone guessing gets 25% right, so a well-built hard question lands between 25% and 40%.

### Up front: rubric

Before there are answers, the band is estimated by adding the Bloom score (section 3) and three criteria from 0 to 2, stored in the `difficulty` field:

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| Bloom (`bloom`) | `remember` or `understand` | `apply` | `analyze` or `evaluate` |
| `steps` | One step to the answer | Two or three steps | Four or more |
| `specialization` | Covered in any introductory course | Learned by working in the field | Niche or research |
| `distractors` | Easy to rule out | One is plausible | Several match common mistakes |

The sum goes from 0 to 8: 0–2 is green, 3–5 yellow and 6–8 red.

- Bloom replaces v1's `cognitive` criterion, which measured the same thing without a recognized framework.
- Besides the sum, the validator requires `analyze` or `evaluate` for every `hard` question. A niche question with good distractors can score high, but if it only asks for recall, its difficulty comes from memory, not reasoning.
- The validator warns when `level` does not match what the rubric suggests. The reviewer can keep a different level for a good reason.
- In the review, a second model estimates Bloom and scores the rubric without seeing what the generator chose. If the sums differ by 2 points or more, the person reviewing decides.
- All 103 questions are scored, and in every one the rubric matches the level.

### After the fact: Bayesian update (phase 2)

Once there are anonymous statistics, each question starts from a Beta prior centered on its band, with mean m = 0.80 (green), 0.55 (yellow) or 0.33 (red) and a weight equivalent to n₀ = 10 answers. If n people then answer it and k get it right, the estimate is:

```
p = (n₀ · m + k) / (n₀ + n)
```

For example, a red question answered by 40 people, 30 of whom get it right, ends up at p = (3.3 + 30) / 50 ≈ 0.67 and turns yellow.

- **Color change:** when the question has at least 30 answers and p falls in another band, so it does not change because of luck in the first answers.
- **Review:** if p stays below 0.30 with 30 answers or more, it is close to chance, which often reveals a wrong key or an ambiguous question.
- **Recalibrating the rubric:** since the rubric is stored next to the measured level, with enough data a logistic regression of correctness on Bloom and the three criteria can be fitted. That shows which criteria really predict difficulty, and the rubric becomes a model trained on the answers.

### Discrimination and reliability

- **Discrimination:** whether the people who score better on the rest of the quiz get the question right more often. A point-biserial correlation below 0.10 means the question does not tell levels apart; a negative one usually reveals a wrong key.
- **Reliability:** Cronbach's alpha measures the reliability of a fixed test, not the difficulty of a question, and assumes everyone answers the same questions. Since each quiz is drawn at random from the bank, an item response theory model (Rasch or 2PL) fits better. It estimates difficulty and discrimination on a common scale even when each person sees different questions, and its marginal reliability plays the role of alpha.

## 13. Website

`site/` is a static site: HTML, CSS and JavaScript with no frameworks, with the fonts bundled. Its only external script is Cloudflare Web Analytics (see "Visits").

### Name

**AI/ML Questions** in English and **Preguntas IA/ML** in Spanish, with an "alpha" badge («alfa» in Spanish) for as long as the site is in alpha. The name is descriptive on purpose: it says what the site is with the same words someone would type into a search engine. To change it:

- `site/app.js`: `siteName` in `STRINGS.en` and in `STRINGS.es`.
- `site/index.html`: the `<title>`, `og:site_name` and the initial header text.
- `site/manifest.webmanifest`: `name` and `short_name`.
- `scripts/make_assets.py`: `NAME`. Then run the script to regenerate `og-image.png`.

To end the alpha, delete the `<span class="badge">` from `site/index.html`.

### Screens

1. **Home:** the name, the language switch (EN/ES) and the site's goal. Then difficulty (the three dots), topics, number of questions and mode, with how many questions are available for those filters. If there is an unfinished quiz, it offers to resume it.
2. **Question:** the dot with the level written next to it, the topic and subtopic, the stem, and the options as answer-sheet bubbles. In study mode, answering marks the correct option and shows each option's rationale, the explanation and the sources. On a computer, keys 1 to 4 (or A to D) choose and Enter moves on. The language can be switched mid-quiz without losing progress.
3. **Results:** score, correct answers by difficulty and by topic, the message to share, Ko-fi and the review of mistakes, with the option to retry only the missed questions.

### Sharing on LinkedIn

LinkedIn's share URL (`https://www.linkedin.com/sharing/share-offsite/?url=...`) accepts only the link; the post text cannot be prefilled. So the button copies the message to the clipboard and opens LinkedIn with the link, and the person pastes the text. On phones, the "Share…" button («Compartir…» in Spanish) opens the system's share menu.

The message is built from the result, in the chosen language, and the person can edit it before copying:

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

- The topics line appears only if the quiz had at least two topics with two or more questions each, and with different results.
- The Spanish link ends in `#es`, so whoever opens it sees the site in Spanish.

LinkedIn builds the link card from the Open Graph tags in `index.html`: the title "How much do you know about AI and machine learning?", the description and `og-image.png` (1200 × 627). The card is in English and the same for both languages, because LinkedIn ignores what comes after the `#`; a Spanish card would need its own path, such as `/es/`, with its own tags. Since the site is static, the card is the same for everyone; an image with each person's score needs a Worker to generate it (phase 2). LinkedIn caches the card, so after changing it you have to refresh it with LinkedIn's Post Inspector.

### PWA

With `manifest.webmanifest` and `sw.js`, the site can be installed on a phone and works offline. On the first visit, the service worker stores what `precache.json` lists (the page, the fonts, the icons and every question); after that it answers from what it stored and updates it in the background. `scripts/build_site.py` changes the service worker version whenever a file changes, so browsers download the new files.

### Build and test

```bash
python scripts/build_site.py                  # reviewed questions only
python scripts/build_site.py --include-drafts # drafts too, for testing
python -m http.server 8000 --directory site   # open http://localhost:8000
python scripts/make_assets.py                 # icons and og-image.png (pip install playwright)
```

The service worker only works on `localhost` or over HTTPS.

### Publishing on Cloudflare

The repository is [CristobalSantana/ai-ml-questions](https://github.com/CristobalSantana/ai-ml-questions). The site is published as a Cloudflare Worker called `ai-ml-questions`, connected to the repository through Workers Builds. [`wrangler.jsonc`](wrangler.jsonc) tells it to publish the `site/` folder as is, as static files, with no build step, because `site/data` is already generated in the repository.

- Every push to `main` republishes the site on its own; the status of each deployment is in the Cloudflare dashboard, under the Worker, in the **Deployments** or **Builds** tab.
- The `name` in `wrangler.jsonc` must match the Worker's name in the dashboard.
- The public address is https://ai-ml-questions.strangemachines.workers.dev/. If it changes, or if a custom domain is added under **Domains & Routes**, update `CONFIG.siteUrl` in `site/app.js` and the `og:url` and `og:image` tags in `site/index.html`, because LinkedIn needs absolute URLs.

Before each push that changes questions or the site, regenerate `site/data` and the service worker version. While the questions are still drafts (`llm_draft`), the site is published with `python scripts/build_site.py --include-drafts`; once they are reviewed, without that option.

`CONFIG` in `site/app.js` also holds the Ko-fi page (`kofiUrl`) and the link for reporting mistakes (`reportUrl`), which opens an issue in the repository.

### Visits

The site counts visits with Cloudflare Web Analytics: the `beacon.min.js` script at the end of `site/index.html`, with the site's token. It uses no cookies and does not identify visitors, so no cookie banner is needed. The numbers (visits, page views, countries, where people come from and load speed) are in the Cloudflare dashboard under **Analytics & Logs → Web Analytics**. Ad blockers often block the script, so the numbers come out somewhat below the real ones. The service worker does not intercept those requests because they go to another domain.

## 14. Language

- **English by default.** The site opens in English and can be switched to Spanish with the EN/ES button; the choice is saved in the browser.
- **Links per language.** `#es` or `#en` at the end of the link opens the site in that language. The order of precedence is: the link's language, the saved choice and, if there is neither, English. The site ignores the browser's language, so the default is always English.
- **Questions.** English is required and Spanish optional; if a question has no Spanish, it is shown in English. The validator summary counts how many questions each language has.
- **Interface.** The texts are in `STRINGS`, in `site/app.js`, one set per language. Adding another language means adding it to `CONFIG.languages`, to `STRINGS`, to the schema and to the questions.
- **This document.** `README.md` (English) and `README.es.md` (Spanish) say the same thing; a change in one goes into the other too.

Strange Machines and ml-toy-experiments are in English, which favors English for reach; Spanish has less competition and serves readers in Chile and Latin America.

## 15. License

- Questions: CC BY-SA 4.0 ([`LICENSE-QUESTIONS`](LICENSE-QUESTIONS)). Anyone can reuse them if they credit the source and share under the same license.
- Code: MIT ([`LICENSE`](LICENSE)), like ml-toy-experiments.
- Fonts: STIX Two Text, IBM Plex Sans and IBM Plex Mono, under the SIL Open Font License 1.1 (`site/fonts/OFL-*.txt`).

## 16. Files

```
README.md, README.es.md      this specification, in English and Spanish
LICENSE, LICENSE-QUESTIONS   licenses for the code (MIT) and the questions (CC BY-SA 4.0)
wrangler.jsonc               configuration of the Cloudflare Worker that publishes site/
taxonomy.json                8 topics, 17 areas and 203 subtopics, in English and Spanish
schema/question.schema.json  the format of a question (JSON Schema 2020-12)
questions/<area>.json        the questions, one file per area
scripts/validate.py          validates the bank, the writing rules and coverage (pip install jsonschema)
scripts/build_site.py        generates site/data, site/precache.json and the service worker version
scripts/make_assets.py       generates the icons and og-image.png (pip install playwright)
prompts/generar.md           prompt for generating batches of questions (in Spanish)
prompts/verificar.md         prompt for reviewing questions with another model
site/index.html              the page and the tags for sharing
site/styles.css, fonts.css   styles and fonts
site/app.js                  the quiz logic; CONFIG and the texts (STRINGS) at the top
site/manifest.webmanifest    data for installing the PWA
site/sw.js                   service worker for working offline
site/icons/, og-image.png    icons and the image for the share card
site/fonts/                  the fonts and their licenses
site/data/                   generated: taxonomy, index and questions per area
```

The current 103 questions cover the 17 areas, the three levels, the three stability classes and the five Bloom levels, are in English and Spanish, and remain marked as `llm_draft` until you review them.

## References

- Haladyna, T. M., Downing, S. M., & Rodriguez, M. C. (2002). A review of multiple-choice item-writing guidelines for classroom assessment. *Applied Measurement in Education*, 15(3), 309–333. https://doi.org/10.1207/S15324818AME1503_5
- Rodriguez, M. C. (2005). Three options are optimal for multiple-choice items: A meta-analysis of 80 years of research. *Educational Measurement: Issues and Practice*, 24, 3–13.
- Anderson, L. W., & Krathwohl, D. R. (Eds.). (2001). *A taxonomy for learning, teaching, and assessing: A revision of Bloom's taxonomy of educational objectives*. Longman.
