# Statistics

What the site records about each answer, how to get the data, and what the statistics say about each question: its real difficulty, whether it tells apart people who know more, and whether its distractors work.

## What is recorded

When someone answers a question, the site sends one record to the Worker ([`worker/index.js`](../worker/index.js)), which stores it in the Cloudflare D1 database `ai-ml-questions`, table `answers` ([`migrations/0001_answers.sql`](../migrations/0001_answers.sql)):

| Column | What it holds |
|---|---|
| `id` | Row number |
| `at` | When the answer arrived, in UTC |
| `quiz` | A random id the browser makes for each quiz, so the answers of one quiz can be grouped |
| `question`, `version` | The question and the version that was shown |
| `choice` | The id of the chosen option in the bank (`a` to `d`), not its position on screen |
| `correct` | 1 if the choice is the key. The Worker works it out from the published questions, not the browser |
| `lang` | `en` or `es`, the language the question was answered in |
| `mode` | `study` or `exam` |
| `first` | 1 if this browser had never answered the question before |

**What is not recorded:** IP addresses, cookies, the browser or device, accounts, or any identifier that lasts beyond one quiz. Two quizzes by the same person cannot be linked. `first` comes from the history the browser already keeps so as not to repeat questions; only the yes or no leaves the browser.

**When an answer is sent:**

- In study mode, on choosing, because the first choice is final.
- In exam mode, on moving to the next question, so a choice changed before that does not count.
- Retrying the mistakes sends answers with `first = 0`, since those are second attempts.
- Offline, nothing is sent; an answer still pending in study mode is tried again on moving on.

**What the Worker checks:** the question exists on the published site, the version is the current one (a page opened before a question changed gets a 409 and its answer is dropped), the option exists, the fields are well formed and the request does not come from another site. It only takes questions with a single correct option, the only kind the site has.

**Limits:** each answer is one Worker request and one row written. The free plan allows 100,000 of each per day; past that, answers are lost until midnight UTC, and the site keeps working because its files do not go through the Worker. There is no login, so anyone could send made-up answers within these rules. The script drops duplicates and answers to older versions, but not every kind of noise; if it becomes a problem, a [rate limiting binding](https://developers.cloudflare.com/workers/runtime-apis/bindings/rate-limit/) or Turnstile can be added to the Worker.

## Seeing the data

**In the Cloudflare dashboard:** on the **D1 SQL database** page, select `ai-ml-questions` and then **Console**, where SQL queries can be run:

```sql
-- How many answers there are
SELECT COUNT(*) FROM answers;

-- First attempts and share correct per question
SELECT question, COUNT(*) AS n, ROUND(AVG(correct), 2) AS p
FROM answers WHERE first = 1 GROUP BY question ORDER BY n DESC;

-- How often each option is chosen in one question
SELECT choice, COUNT(*) FROM answers WHERE question = 'retrieval-0005' AND first = 1 GROUP BY choice;
```

The table has no indexes, because each one would add a row written per answer, so every query reads the whole table. The free plan allows 5 million rows read per day, which is plenty for this.

**With the script:** export the table and run [`scripts/item_stats.py`](../scripts/item_stats.py) on it.

```bash
npx wrangler login                       # once, with the Cloudflare account
npx wrangler d1 export ai-ml-questions --remote --table answers --output answers.sql
python scripts/item_stats.py answers.sql                  # report
python scripts/item_stats.py answers.sql --json stats.json # every number, for other tools
python scripts/item_stats.py answers.sql --all             # also repeat attempts
```

It also reads the JSON that `npx wrangler d1 execute ai-ml-questions --remote --json --command "SELECT * FROM answers"` prints, and CSV files with the table's columns. `answers.sql`, `answers.json` and `stats.json` are in `.gitignore`, so an export is not committed by mistake.

**Locally:** `npx wrangler dev` runs the site and the Worker together with a local D1. The table is created there with `npx wrangler d1 migrations apply ai-ml-questions --local`. In the remote database it already exists; in a new database it is created with `--remote`.

## What the script computes

It uses the answers to the current version of each question, one per quiz, and by default only first attempts, because whoever sees a question again may remember the answer.

- **Difficulty index (p):** the share of people who got the question right, with its 95% Wilson interval, which stays honest with few answers.
- **Estimate:** p combined with the prior of the question's level, as in [Difficulty](difficulty.md#after-the-fact-bayesian-update): p̂ = (n₀ · m + k) / (n₀ + n), with n₀ = 10. Its band is the level the answers suggest.
- **Discrimination (r):** the point-biserial correlation between getting the question right and how well the same person did on the rest of the quiz. Each quiz is a different random draw, so the plain share of correct answers in the rest of the quiz would mostly measure how hard its questions were. Instead, each other question adds its result minus its expected share of correct answers, estimated without that quiz's own answer. It needs at least 5 other answers in the same quiz.
- **Options:** the share of people who chose each option, and the same correlation computed for choosing that option. A distractor that works attracts people who do worse on the rest of the quiz, so its correlation is negative.
- **By language and mode:** p in English and in Spanish, and in study and exam mode, in the JSON.

## What it flags

Only questions with at least 30 answers are flagged (`--min-n` changes the number).

| Flag | Rule | What to look at |
|---|---|---|
| Level | The estimate falls in another band | Change `level` if it persists, so the colored dot matches |
| Close to chance | The estimate is less than 5 points above guessing: 30% with four options, 38% with three | A wrong key or an ambiguous question |
| Negative discrimination | r below −1.96/√n | People who know more get it wrong more often: usually a wrong key |
| Low discrimination | r below 0.10 | The question does not tell levels apart: confusing, a trick, or too easy |
| Distractor almost nobody chooses | Chosen by under 5% of people, with at least 5 wrong answers per distractor. In a question people find easy, it also has to get under half of its even share of the wrong answers | An implausible distractor: rewrite it with a real, common mistake |
| Distractor that attracts people who know more | Its correlation is above 1.96/√n | It may be defensible: check whether it is also correct |
| English vs. Spanish | With 30 answers in each, the two 95% intervals do not overlap | The translation changes the question |

- **The 5% rule** comes from Haladyna and Downing (1993), and Tarrant, Ware and Mohammed (2009) apply it as a distractor chosen by fewer than 5% of examinees or with a positive discrimination. In an easy question most people choose the key, so even plausible distractors fall under 5%; hence the extra condition for easy questions.
- **Signs only count when they are clear.** With n answers, a correlation that is really zero rarely goes beyond ±1.96/√n by chance (0.36 with 30 answers, 0.20 with 100). That is why a negative discrimination or a positive distractor is flagged only beyond that margin, while Tarrant and colleagues count any positive value.
- These are reasons to look at a question, not verdicts. The person reviewing decides, and a change that could affect how people answer raises the question's `version`, which starts its statistics over.

## Caveats

- **Who answers:** the people who use the site, not a sample of a population. The levels describe difficulty for them.
- **First attempts are per browser:** a person who uses two devices answers for the first time twice.
- **Study mode** shows explanations along the way, which can help with later questions in the same quiz. The JSON splits p by mode to check whether that matters.
- **Versions:** the Worker only accepts answers to the current version, and the script analyzes only that one. Answers to older versions stay in the table.

## Next steps

- **Item response theory:** with enough answers, a Rasch or 2PL model fitted on the same table puts every question on a common scale even though each person sees different questions ([Difficulty](difficulty.md#discrimination-and-reliability)).
- **Recalibrating the rubric:** a logistic regression of correctness on Bloom and the three rubric criteria shows which ones really predict difficulty.

## References

- Haladyna, T. M. (2004). *Developing and validating multiple-choice test items* (3rd ed.). Lawrence Erlbaum.
- Haladyna, T. M., & Downing, S. M. (1993). How many options is enough for a multiple-choice test item? *Educational and Psychological Measurement, 53*(4), 999–1010.
- Tarrant, M., Ware, J., & Mohammed, A. M. (2009). An assessment of functioning and non-functioning distractors in multiple-choice questions: A descriptive analysis. *BMC Medical Education, 9*, 40. https://doi.org/10.1186/1472-6920-9-40
- Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. *Journal of the American Statistical Association, 22*(158), 209–212.
