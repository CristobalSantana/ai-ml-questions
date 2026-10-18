# Difficulty

Each question has a level, shown on the site as a colored dot with the level written next to it. The level is estimated up front with a rubric and will be corrected with real answers.

## Levels

| Level | Dot | Bloom | What it requires | Example from the bank |
|---|---|---|---|---|
| `easy` | Green | `remember`, `understand` | Define, recognize or explain a concept. Introductory-course level. | What does the cosine similarity between two embeddings measure? |
| `medium` | Yellow | `understand`, `apply` | Apply a concept, interpret a metric or do a short calculation. The level of someone who works with ML. | Compute precision and recall in a fraud problem. |
| `hard` | Red | `analyze`, `evaluate` | Analyze a new scenario or choose between options under several constraints. Senior or research level. | At temperature 0, a model always gives the same answer on your computer and sometimes a different one on a busy server. What explains both observations? |

## Bloom's taxonomy

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

## The difficulty index

Difficulty is expressed with the classical difficulty index: the proportion of people who answer the question correctly, p. Each color corresponds to a band of p:

| Dot | Level | Expected share of correct answers |
|---|---|---|
| Green | `easy` | 70% or more |
| Yellow | `medium` | Between 40% and 70% |
| Red | `hard` | Under 40% |

With four options, someone guessing gets 25% right, so a well-built hard question lands between 25% and 40%.

## Up front: rubric

Before there are answers, the band is estimated by adding the Bloom score and three criteria from 0 to 2, stored in the `difficulty` field:

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| Bloom (`bloom`) | `remember` or `understand` | `apply` | `analyze` or `evaluate` |
| `steps` | One step to the answer | Two or three steps | Four or more |
| `specialization` | Covered in any introductory course | Learned by working in the field | Niche or research |
| `distractors` | Easy to rule out | One is plausible | Several match common mistakes |

The sum goes from 0 to 8: 0–2 is green, 3–5 yellow and 6–8 red.

- Bloom replaces the `cognitive` criterion of version 1, which measured the same thing without a recognized framework.
- Besides the sum, the validator requires `analyze` or `evaluate` for every `hard` question. A niche question with good distractors can score high, but if it only asks for recall, its difficulty comes from memory, not reasoning.
- The validator warns when `level` does not match what the rubric suggests. The reviewer can keep a different level for a good reason.
- In the model review, a second model estimates Bloom and scores the rubric without seeing what the generator chose. If the sums differ by 2 points or more, the person reviewing decides.
- All 103 questions are scored, and in every one the rubric matches the level.

## After the fact: Bayesian update

The site records each answer anonymously, and [`scripts/item_stats.py`](../scripts/item_stats.py) computes what follows ([Statistics](statistics.md)). Each question starts from a Beta prior centered on its band, with mean m = 0.80 (green), 0.55 (yellow) or 0.33 (red) and a weight equivalent to n₀ = 10 answers. If n people then answer it and k get it right, the estimate is:

```
p = (n₀ · m + k) / (n₀ + n)
```

For example, a red question answered by 40 people, 30 of whom get it right, ends up at p = (3.3 + 30) / 50 ≈ 0.67 and turns yellow.

- **Color change:** when the question has at least 30 answers and p falls in another band, so it does not change because of luck in the first answers.
- **Review:** if p stays less than 5 points above guessing with 30 answers or more (below 0.30 with four options), it is close to chance, which often reveals a wrong key or an ambiguous question.
- **Recalibrating the rubric:** since the rubric is stored next to the measured level, with enough data a logistic regression of correctness on Bloom and the three criteria can be fitted. That shows which criteria really predict difficulty, and the rubric becomes a model trained on the answers.

## Discrimination and reliability

- **Discrimination:** whether the people who score better on the rest of the quiz get the question right more often. A point-biserial correlation below 0.10 means the question does not tell levels apart; a negative one usually reveals a wrong key. Since each quiz draws different questions, the rest of the quiz is scored against what was expected of each question ([Statistics](statistics.md#what-the-script-computes)).
- **Reliability:** Cronbach's alpha measures the reliability of a fixed test, not the difficulty of a question, and assumes everyone answers the same questions. Since each quiz is drawn at random from the bank, an item response theory model (Rasch or 2PL) fits better. It estimates difficulty and discrimination on a common scale even when each person sees different questions, and its marginal reliability plays the role of alpha.

## Reference

- Anderson, L. W., & Krathwohl, D. R. (Eds.). (2001). *A taxonomy for learning, teaching, and assessing: A revision of Bloom's taxonomy of educational objectives*. Longman.
