# Writing rules

The questions follow the guidelines of Haladyna, Downing and Rodriguez (2002), a review of 31 rules for writing multiple-choice questions. Their purpose here is that the answer cannot be deduced from the wording: the correct option tends to give itself away by being the longest, the most qualified or the only one without absolutes.

The full rules, as given to the model that drafts questions, are in [`prompts/generate.md`](../prompts/generate.md). The Spanish version of each question also follows the [Spanish style](spanish-style.md) guide.

## What the validator checks

`python scripts/validate.py` checks these rules in each language:

| Rule | Result |
|---|---|
| The correct option is not longer than 1.2 times the distractors' average | Warning |
| The longest option is at most 2.5 times as long as the shortest | Warning |
| No option uses absolutes: always, never, completely; siempre, nunca, completamente… | Warning |
| No option says "all/none of the above" or «todas/ninguna de las anteriores» | Error |
| The question is phrased positively: no "not" or "except"; no «no», «excepto» or «salvo» | Warning |
| A `hard` question is `analyze` or `evaluate` | Error |

The validator summary also shows in what share of the bank the correct option is the longest one and in what share it is the shortest. With four options, chance gives about 25% for each; a very high share for "longest" is a clue people learn even when every question passes the 1.2× rule. In the October 2026 review it went down from 46% to 20% in English.

## What the model review checks

A second model reviews what depends on meaning ([`prompts/review.md`](../prompts/review.md)):

- **Clues in the options (step 0):** the model sees only the options, without the stem, and bets on one. If it gets it right with confidence in two different orders, the wording gives the answer away and the question is rewritten.
- **Homogeneity:** the options cover the same kind of content with the same grammatical form, none overlaps another and there are no pairs of exact opposites.
- **Plausible distractors:** each one matches a mistake people actually make.
- **The central idea is in the stem:** the question can be answered without looking at the options.
- **The stem does not point to the answer:** for example, a question about ResNet whose correct option is the only one that says "residual".

## Also

- Three well-made options are enough (Rodriguez, 2005): three plausible options beat four with an absurd one.
- The site shuffles the options in each quiz. Options with a natural order (numbers, steps) are shown in the written order with `keep_order: true`, and then the author varies the position of the correct option from question to question.

## References

- Haladyna, T. M., Downing, S. M., & Rodriguez, M. C. (2002). A review of multiple-choice item-writing guidelines for classroom assessment. *Applied Measurement in Education*, 15(3), 309–333. https://doi.org/10.1207/S15324818AME1503_5
- Rodriguez, M. C. (2005). Three options are optimal for multiple-choice items: A meta-analysis of 80 years of research. *Educational Measurement: Issues and Practice*, 24, 3–13.
