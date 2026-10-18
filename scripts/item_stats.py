#!/usr/bin/env python3
"""Computes the statistics of each question from the anonymous answers stored in Cloudflare D1.

For each question: how many people answered it, the share who got it right (the difficulty index)
and its estimate with the prior of its level, the discrimination (whether the people who do better
on the rest of their quiz get it right more often) and how often each option is chosen. It then
flags what needs a look: a level that does not match, a question close to chance, low or negative
discrimination, distractors that do not work (Haladyna and Downing, 1993) and a gap between the
English and the Spanish version. docs/statistics.md explains every number.

Usage:
    npx wrangler d1 export ai-ml-questions --remote --table answers --output answers.sql
    python scripts/item_stats.py answers.sql
    python scripts/item_stats.py answers.sql --json stats.json   # every number, for other tools

It also reads the JSON that `wrangler d1 execute ... --json` prints, and CSV files with the table's
columns. By default it uses first attempts only: the first time a browser answered each question.
"""

import argparse
import csv
import json
import math
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# From docs/difficulty.md: the prior of each level, its weight in answers and the bands of p.
PRIOR = {"easy": 0.80, "medium": 0.55, "hard": 0.33}
PRIOR_WEIGHT = 10
BANDS = (("easy", 0.70), ("medium", 0.40), ("hard", 0.0))
# Close to chance: under 5 points above guessing, which is 30% with four options (docs/difficulty.md).
NEAR_CHANCE = 0.05
LOW_DISCRIMINATION = 0.10
# A distractor chosen by under 5% does not work (Haladyna and Downing, 1993; Tarrant, Ware and
# Mohammed, 2009). In an easy question that happens even to plausible distractors, so there it also
# has to get under half of its even share of the wrong answers, and there have to be at least 5
# wrong answers per distractor before judging.
RARE_DISTRACTOR = 0.05
MIN_WRONG_PER_DISTRACTOR = 5
# Other answers from the same quiz needed to estimate how well that person did elsewhere.
MIN_OTHERS = 5
Z95 = 1.96
COLUMNS = ("quiz", "question", "version", "choice", "correct", "lang", "mode", "first")
LANGUAGES = ("en", "es")
MODES = ("study", "exam")


# Reading the data

def find_rows(data):
    """The rows inside the JSON of `wrangler d1 execute --json`, of the D1 API, or a plain list."""
    if isinstance(data, dict):
        for key in ("results", "result"):
            if key in data:
                return find_rows(data[key])
        return []
    if isinstance(data, list):
        if data and all(isinstance(r, dict) and "question" in r for r in data):
            return data
        return [row for item in data for row in find_rows(item)]
    return []


def load_rows(path):
    """Reads an export of the answers table: .sql from `wrangler d1 export`, .json or .csv."""
    if path.suffix == ".sql":
        db = sqlite3.connect(":memory:")
        db.executescript(path.read_text(encoding="utf-8"))
        db.row_factory = sqlite3.Row
        raw = [dict(r) for r in db.execute("SELECT * FROM answers ORDER BY id")]
    elif path.suffix == ".csv":
        with path.open(newline="", encoding="utf-8") as f:
            raw = list(csv.DictReader(f))
    else:
        raw = find_rows(json.loads(path.read_text(encoding="utf-8")))
    rows = []
    for r in raw:
        try:
            row = {"id": int(r.get("id") or 0)}
            for col in COLUMNS:
                row[col] = int(r[col]) if col in ("version", "correct", "first") else str(r[col])
        except (KeyError, TypeError, ValueError):
            sys.exit(f"{path}: every row needs the columns {', '.join(COLUMNS)}. This one does not: {r}")
        rows.append(row)
    return rows


def load_bank():
    return {
        q["id"]: q
        for path in sorted((ROOT / "questions").glob("*.json"))
        for q in json.loads(path.read_text(encoding="utf-8"))
    }


# Statistics

def wilson(k, n):
    """95% Wilson interval for a proportion: honest with few answers and near 0 or 1."""
    if n == 0:
        return (0.0, 1.0)
    p, z2 = k / n, Z95 * Z95
    centre = (p + z2 / (2 * n)) / (1 + z2 / n)
    half = Z95 * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / (1 + z2 / n)
    return (max(0.0, centre - half), min(1.0, centre + half))


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0 or syy == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(sxx * syy)


def band(p):
    return next(name for name, low in BANDS if p >= low)


def pct(x):
    return f"{100 * x:.0f}%"


def select(rows, bank, use_all):
    """Keeps one answer per quiz and question, to the current version, first attempts by default."""
    summary = Counter(rows=len(rows))
    seen, used = set(), []
    for r in sorted(rows, key=lambda r: r["id"]):
        key = (r["quiz"], r["question"], r["version"])
        q = bank.get(r["question"])
        if key in seen:
            summary["duplicates"] += 1
        elif q is None:
            summary["unknown questions"] += 1
        elif r["version"] != q["version"]:
            summary["older versions"] += 1
        elif not r["first"] and not use_all:
            summary["repeat attempts"] += 1
        else:
            used.append(r)
        seen.add(key)
    return summary, used


def rest_scores(used, bank):
    """How well each person did on the other questions of the quiz, beyond what was expected.

    Each quiz is a different random draw, so the plain share of correct answers would mostly
    measure how hard its questions were. Instead, each other question contributes its result
    minus its expected share of correct answers, estimated without that quiz's own answer.
    """
    n, k = Counter(), Counter()
    for r in used:
        n[r["question"]] += 1
        k[r["question"]] += r["correct"]

    def residual(r):
        prior = PRIOR[bank[r["question"]]["level"]]
        expected = (PRIOR_WEIGHT * prior + k[r["question"]] - r["correct"]) / (PRIOR_WEIGHT + n[r["question"]] - 1)
        return r["correct"] - expected

    by_quiz = defaultdict(list)
    for r in used:
        by_quiz[r["quiz"]].append(r)
    rest = {}
    for quiz, answers in by_quiz.items():
        if len(answers) - 1 < MIN_OTHERS:
            continue
        residuals = [residual(r) for r in answers]
        total = sum(residuals)
        for r, own in zip(answers, residuals):
            rest[(quiz, r["question"])] = (total - own) / (len(answers) - 1)
    return rest


def split(answers, field, values):
    out = {}
    for value in values:
        part = [r for r in answers if r[field] == value]
        if part:
            k = sum(r["correct"] for r in part)
            out[value] = {"n": len(part), "p": k / len(part), "ci": wilson(k, len(part))}
    return out


def flags(item, min_n):
    out = []
    n, n_rest, r = item["n"], item["n_rest"], item["discrimination"]
    if n >= min_n:
        chance = 1 / len(item["options"])
        if item["estimate"] < chance + NEAR_CHANCE:
            out.append(f"close to chance ({pct(item['estimate'])} correct; guessing gives {pct(chance)}): check the key and the wording")
        elif item["suggested_level"] != item["level"]:
            out.append(f"answers suggest {item['suggested_level']} ({pct(item['estimate'])} correct), but it is marked {item['level']}")
    # A sign only counts when it is clear: beyond 1.96/√n, which a correlation of zero rarely reaches by chance.
    margin = Z95 / math.sqrt(n_rest) if n_rest else 1.0
    if n_rest >= min_n and r is not None:
        if r < -margin:
            out.append(f"negative discrimination ({r:+.2f}): people who do better elsewhere get it wrong more often; check the key")
        elif r < LOW_DISCRIMINATION:
            out.append(f"low discrimination ({r:+.2f}): it barely tells people who know more apart")
    distractors = [o for o in item["options"] if not o["key"]]
    wrong_share = 1 - item["p"]
    judge_rare = n >= min_n and n * wrong_share >= MIN_WRONG_PER_DISTRACTOR * len(distractors)
    rare, attractive = [], []
    for o in distractors:
        if judge_rare and o["share"] < min(RARE_DISTRACTOR, wrong_share / len(distractors) / 2):
            rare.append(f"{o['id']} ({pct(o['share'])})")
        if n_rest >= min_n and o["r"] is not None and o["r"] > margin:
            attractive.append(f"{o['id']} ({o['r']:+.2f})")
    if rare:
        out.append(f"distractors almost nobody chooses, which do not work: {', '.join(rare)}")
    if attractive:
        out.append(f"distractors that attract people who do better elsewhere: {', '.join(attractive)}; one may be defensible")
    en, es = item["languages"].get("en"), item["languages"].get("es")
    if en and es and min(en["n"], es["n"]) >= min_n and (en["ci"][1] < es["ci"][0] or es["ci"][1] < en["ci"][0]):
        out.append(f"English {pct(en['p'])} and Spanish {pct(es['p'])} correct: check the translation")
    return out


def analyze(rows, bank, use_all=False, min_n=30):
    summary, used = select(rows, bank, use_all)
    summary["used"] = len(used)
    summary["quizzes"] = len({r["quiz"] for r in used})
    rest = rest_scores(used, bank)
    summary["answers with a rest score"] = len(rest)

    by_question = defaultdict(list)
    for r in used:
        by_question[r["question"]].append(r)

    items = []
    for qid in sorted(by_question):
        q, answers = bank[qid], by_question[qid]
        n, k = len(answers), sum(r["correct"] for r in answers)
        paired = [(r, rest[(r["quiz"], qid)]) for r in answers if (r["quiz"], qid) in rest]
        scores = [s for _, s in paired]
        chosen = Counter(r["choice"] for r in answers)
        item = {
            "id": qid,
            "version": q["version"],
            "level": q["level"],
            "bloom": q["bloom"],
            "rubric": q["difficulty"],
            "n": n,
            "correct": k,
            "p": k / n,
            "ci": wilson(k, n),
            "estimate": (PRIOR_WEIGHT * PRIOR[q["level"]] + k) / (PRIOR_WEIGHT + n),
            "n_rest": len(paired),
            "discrimination": pearson([r["correct"] for r, _ in paired], scores),
            "options": [
                {
                    "id": o["id"],
                    "key": o["id"] in q["answer"],
                    "n": chosen[o["id"]],
                    "share": chosen[o["id"]] / n,
                    "r": pearson([int(r["choice"] == o["id"]) for r, _ in paired], scores),
                }
                for o in q["options"]
            ],
            "languages": split(answers, "lang", LANGUAGES),
            "modes": split(answers, "mode", MODES),
        }
        item["suggested_level"] = band(item["estimate"])
        item["flags"] = flags(item, min_n)
        items.append(item)
    return summary, items


# Report

def counts_line(counter, keys):
    return " · ".join(f"{key} {counter[key]:,}" for key in keys if counter[key])


def report(summary, items, bank, min_n, use_all):
    out = []
    used = "all attempts" if use_all else "first attempts"
    out.append(f"Answers: {summary['rows']:,} rows · {summary['used']:,} used ({used}) from {summary['quizzes']:,} quizzes")
    left = counts_line(summary, ("repeat attempts", "older versions", "duplicates", "unknown questions"))
    if left:
        out.append(f"Left out: {left}")
    if not items:
        out.append("No answers to analyze yet.")
        return "\n".join(out)
    langs = Counter({lang: sum(i["languages"].get(lang, {}).get("n", 0) for i in items) for lang in LANGUAGES})
    modes = Counter({mode: sum(i["modes"].get(mode, {}).get("n", 0) for i in items) for mode in MODES})
    out.append(f"By language: {counts_line(langs, LANGUAGES)} · by mode: {counts_line(modes, MODES)}")
    enough = sum(i["n"] >= min_n for i in items)
    out.append(
        f"Questions with answers: {len(items)} of {len(bank)} · with {min_n} or more: {enough}"
        f" · answers from quizzes long enough for discrimination: {summary['answers with a rest score']:,}"
    )

    flagged = [i for i in items if i["flags"]]
    out.append("")
    out.append(f"To look at ({len(flagged)})" if flagged else f"Nothing to look at yet: flags need {min_n} answers.")
    for i in sorted(flagged, key=lambda i: (-len(i["flags"]), i["id"])):
        r = "—" if i["discrimination"] is None else f"{i['discrimination']:+.2f}"
        lo, hi = i["ci"]
        out.append(
            f"  {i['id']} v{i['version']} · {i['level']} · {i['n']} answers · {pct(i['p'])} correct"
            f" ({pct(lo)}–{pct(hi)}) · estimate {pct(i['estimate'])} · discrimination {r}"
        )
        out.extend(f"    - {flag}" for flag in i["flags"])

    out.append("")
    out.append("All questions with answers. p: share correct; est.: with the prior of its level; r: discrimination;")
    out.append("a–d: share that chose each option, * marks the key.")
    w = max(len("question"), *(len(i["id"]) for i in items))
    out.append(f"  {'question':<{w}}  {'v':>2}  {'level':<6} {'n':>5}  {'p':>4}  {'est.':>4}  {'r':>5}   a      b      c      d")
    for i in items:
        r = "—" if i["discrimination"] is None else f"{i['discrimination']:+.2f}"
        cells = [f"{pct(o['share']) + ('*' if o['key'] else ''):<6}" for o in i["options"]]
        out.append(
            f"  {i['id']:<{w}}  {i['version']:>2}  {i['level']:<6} {i['n']:>5}  {pct(i['p']):>4}  {pct(i['estimate']):>4}  {r:>5}   "
            + " ".join(cells).rstrip()
        )
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Statistics of each question from the answers stored in D1.")
    parser.add_argument("export", type=Path, help="answers.sql from `wrangler d1 export`, or a .json or .csv file")
    parser.add_argument("--all", action="store_true", help="also use repeat attempts, not only the first one per browser")
    parser.add_argument("--min-n", type=int, default=30, help="answers a question needs before it is flagged (default 30)")
    parser.add_argument("--json", type=Path, help="also write every number to this JSON file")
    args = parser.parse_args()

    bank = load_bank()
    summary, items = analyze(load_rows(args.export), bank, args.all, args.min_n)
    print(report(summary, items, bank, args.min_n, args.all))
    if args.json:
        data = {"summary": dict(summary), "min_n": args.min_n, "first_attempts_only": not args.all, "questions": items}
        args.json.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"\nWrote {args.json}")


if __name__ == "__main__":
    main()
