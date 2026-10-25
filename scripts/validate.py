#!/usr/bin/env python3
"""Validates the question bank against the schema, the taxonomy and the writing rules.

Usage:
    python scripts/validate.py            # checks everything and prints a summary
    python scripts/validate.py --publish  # also fails if any draft is left (origin: llm_draft)

Requires: pip install jsonschema

GitHub runs it on every push and pull request (.github/workflows/check.yml); errors make the
check fail, and both errors and warnings appear on the line of the question. tests/ checks that
each rule catches what it should.
"""

import argparse
import itertools
import json
import os
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:
    sys.exit("jsonschema is missing. Install it with: pip install jsonschema")

ROOT = Path(__file__).resolve().parent.parent
LEVELS = ["easy", "medium", "hard"]
BLOOM = ["remember", "understand", "apply", "analyze", "evaluate"]
BLOOM_SCORE = {"remember": 0, "understand": 0, "apply": 1, "analyze": 2, "evaluate": 2}
OPTION_IDS = "abcde"
# Highest rubric sum (0 to 8) for each level.
RUBRIC_BANDS = ((2, "easy"), (5, "medium"), (8, "hard"))

# Rules from Haladyna, Downing and Rodriguez (2002) that can be checked automatically.
LONGEST_RATIO = 1.2  # the correct option must not stand out as the longest
SPREAD_RATIO = 2.5  # and the options must not differ too much in length
ABSOLUTES = {
    "en": r"\b(always|never|completely|absolutely|in all cases|in every case|under no circumstances)\b",
    "es": r"\b(siempre|nunca|jamás|completamente|absolutamente|en todos los casos|en ningún caso|bajo ninguna circunstancia)\b",
}
FORBIDDEN = {
    "en": r"\b(all|none|both) of the above\b",
    "es": r"\b(todas|ninguna|ambas) (de )?las anteriores\b",
}
NEGATIVE_QUESTION = {
    "en": r"\b(not|except)\b",
    "es": r"\b(no|excepto|salvo)\b",
}
# An option made only of other options' letters, such as "A and B" or "Both A and C". The site
# shuffles the options, so the letters would point to the wrong ones.
COMBINATION = r"^\s*(?:(?i:both|ambas|todas)\s+)?\(?[A-E]\)?(?:\s*,\s*\(?[A-E]\)?)*\s+(?i:and|or|y|e|o|u)\s+\(?[A-E]\)?\.?\s*$"
# Options shorter than this are not compared for overlap: "0.5" inside "0.55" means nothing.
MIN_OVERLAP = 12

# Length limits, in characters: a longer stem or option is hard to read on a phone. Spanish runs
# 10% to 15% longer than English, so it gets more room. Code goes in its own field.
MAX_PROMPT = {"en": 300, "es": 350}
MAX_OPTION = {"en": 150, "es": 170}
MAX_CODE_LINES = 15


def rubric_score(q):
    return BLOOM_SCORE[q["bloom"]] + sum(q["difficulty"].values())


def rubric_level(q):
    """The level that the question's difficulty rubric suggests."""
    score = rubric_score(q)
    return next(level for top, level in RUBRIC_BANDS if score <= top)


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def check_taxonomy(taxonomy, errors):
    """Returns {area: {subtopics}} and {area: topic}, and records problems in the taxonomy."""
    areas = {}
    for area in taxonomy["areas"]:
        if area["id"] in areas:
            errors.append(f"taxonomy.json: repeated area '{area['id']}'")
        subtopics = [s["id"] for s in area["subtopics"]]
        repeated = sorted({s for s in subtopics if subtopics.count(s) > 1})
        if repeated:
            errors.append(f"taxonomy.json: repeated subtopics in '{area['id']}': {', '.join(repeated)}")
        areas[area["id"]] = set(subtopics)

    group_of = {}
    group_ids = [g["id"] for g in taxonomy.get("groups", [])]
    for gid in sorted({g for g in group_ids if group_ids.count(g) > 1}):
        errors.append(f"taxonomy.json: repeated topic '{gid}'")
    for group in taxonomy.get("groups", []):
        for area in group["areas"]:
            if area not in areas:
                errors.append(f"taxonomy.json: topic '{group['id']}' includes the nonexistent area '{area}'")
            elif area in group_of:
                errors.append(f"taxonomy.json: area '{area}' is in both '{group_of[area]}' and '{group['id']}'")
            else:
                group_of[area] = group["id"]
    for area in areas:
        if area not in group_of:
            errors.append(f"taxonomy.json: area '{area}' is not in any topic")
    return areas, group_of


def text_fields(q):
    fields = [q["prompt"], q["explanation"]]
    if "hint" in q:
        fields.append(q["hint"])
    for option in q["options"]:
        fields += [option["text"], option["rationale"]]
    return fields


def parse_date(value, where, field, errors):
    try:
        return date.fromisoformat(value)
    except ValueError:
        errors.append(f"{where}: {field} is not a valid date ({value})")
        return None


def question_sentence(prompt):
    """The last sentence that ends in '?', which is the question proper."""
    parts = re.split(r"(?<=[.!?])\s+", prompt.strip())
    questions = [p for p in parts if p.endswith("?")]
    return questions[-1] if questions else ""


def normalized(text):
    """The words and numbers of a text, in lowercase, to compare options."""
    return " ".join(re.findall(r"\w+", text.lower()))


def first_number(text, lang):
    """The first number in a text, read with the language's separators: 4,096.5 or 4.096,5."""
    found = re.search(r"-?\d[\d.,]*", text)
    if not found:
        return None
    digits = found.group(0).rstrip(".,")
    digits = digits.replace(",", "") if lang == "en" else digits.replace(".", "").replace(",", ".")
    try:
        return float(digits)
    except ValueError:
        return None


def check_options(q, texts, lang, where, errors, warnings):
    """Options that repeat or overlap, that differ in form, or that break their natural order."""
    words = {oid: normalized(text) for oid, text in texts.items()}
    if len(set(words.values())) < len(words):
        errors.append(f"{where} [{lang}]: two options say the same thing")
    for a, b in itertools.permutations(words, 2):
        if len(words[a]) >= MIN_OVERLAP and words[a] != words[b] and f" {words[a]} " in f" {words[b]} ":
            warnings.append(f"{where} [{lang}]: option {a} is contained in option {b}; options should not overlap")
    if len({text.rstrip()[-1:] in ".!?" for text in texts.values()}) > 1:
        warnings.append(f"{where} [{lang}]: some options end with a period and others do not")
    if q.get("keep_order"):
        numbers = [first_number(text, lang) for text in texts.values()]
        if None not in numbers and numbers not in (sorted(numbers), sorted(numbers, reverse=True)):
            warnings.append(f"{where} [{lang}]: keep_order is set, but the numbers in the options are not in order")


def check_writing(q, where, errors, warnings):
    """Clues that give the answer away without knowing the topic (Haladyna et al., 2002), and the
    length limits."""
    for lang in q["prompt"]:
        prompt = q["prompt"][lang]
        if len(prompt) > MAX_PROMPT[lang]:
            errors.append(f"{where} [{lang}]: the stem has {len(prompt)} characters; the limit is {MAX_PROMPT[lang]}")
        if not prompt.rstrip().endswith("?"):
            errors.append(f"{where} [{lang}]: the stem must end with the question itself, a '?'")
        texts = {o["id"]: o["text"][lang] for o in q["options"]}
        lengths = {oid: len(t) for oid, t in texts.items()}
        right = q["answer"][0]
        others = [n for oid, n in lengths.items() if oid not in q["answer"]]
        if q["format"] == "single" and others:
            mean = sum(others) / len(others)
            if lengths[right] >= max(lengths.values()) and lengths[right] > LONGEST_RATIO * mean:
                warnings.append(
                    f"{where} [{lang}]: the correct option is the longest ({lengths[right] / mean:.2f} times the average of the others)"
                )
        if max(lengths.values()) > SPREAD_RATIO * min(lengths.values()):
            warnings.append(f"{where} [{lang}]: the options differ a lot in length ({min(lengths.values())} to {max(lengths.values())} characters)")
        for oid, text in texts.items():
            if len(text) > MAX_OPTION[lang]:
                errors.append(f"{where} [{lang}]: option {oid} has {len(text)} characters; the limit is {MAX_OPTION[lang]}")
            found = re.search(ABSOLUTES[lang], text, re.IGNORECASE)
            if found:
                warnings.append(f"{where} [{lang}]: option {oid} uses an absolute ('{found.group(0)}'), which gives away that it is false")
            if re.search(FORBIDDEN[lang], text, re.IGNORECASE):
                errors.append(f"{where} [{lang}]: option {oid} uses 'all or none of the above'")
            if re.search(COMBINATION, text):
                errors.append(f"{where} [{lang}]: option {oid} combines other options ('{text.strip()}'), but the site shuffles them")
        check_options(q, texts, lang, where, errors, warnings)
        sentence = question_sentence(prompt)
        if re.search(NEGATIVE_QUESTION[lang], sentence, re.IGNORECASE):
            warnings.append(f"{where} [{lang}]: the question is phrased negatively; rewrite it positively if possible")


def check_question(q, path, areas, seen_ids, errors, warnings):
    qid = q["id"]
    where = f"{path.name} {qid}"

    if path.stem != q["area"]:
        errors.append(f"{where}: it is in {path.name} but its area is '{q['area']}'")
    if not qid.startswith(q["area"] + "-"):
        errors.append(f"{where}: the id must start with the area ('{q['area']}-')")
    if qid in seen_ids:
        errors.append(f"{where}: repeated id (also in {seen_ids[qid]})")
    seen_ids[qid] = path.name

    if q["area"] not in areas:
        errors.append(f"{where}: area '{q['area']}' does not exist in taxonomy.json")
    elif q["subtopic"] not in areas[q["area"]]:
        errors.append(f"{where}: subtopic '{q['subtopic']}' does not exist in area '{q['area']}'")

    option_ids = [o["id"] for o in q["options"]]
    expected = list(OPTION_IDS[: len(option_ids)])
    if option_ids != expected:
        errors.append(f"{where}: the options must be in the order {', '.join(expected)}")
    missing = [a for a in q["answer"] if a not in option_ids]
    if missing:
        errors.append(f"{where}: the answer points to options that do not exist: {', '.join(missing)}")

    if len({frozenset(field) for field in text_fields(q)}) > 1:
        errors.append(f"{where}: every text must be in the same languages")

    reviewed = parse_date(q["reviewed_at"], where, "reviewed_at", errors)
    if reviewed and reviewed > date.today():
        errors.append(f"{where}: reviewed_at is in the future")
    if "review_by" in q:
        review_by = parse_date(q["review_by"], where, "review_by", errors)
        if reviewed and review_by:
            if review_by <= reviewed:
                errors.append(f"{where}: review_by must be later than reviewed_at")
            elif review_by < date.today():
                warnings.append(f"{where}: its review date has passed ({q['review_by']})")

    if q["type"] == "evidence" and not any(s["kind"] in ("experiment", "paper") for s in q["sources"]):
        errors.append(f"{where}: an evidence question needs an experiment or a paper as a source")
    if "code" in q:
        lines = len(q["code"]["source"].rstrip("\n").splitlines())
        if lines > MAX_CODE_LINES:
            errors.append(f"{where}: the code has {lines} lines; the limit is {MAX_CODE_LINES}")

    # A hard question requires analyzing or evaluating, not recalling something niche.
    if q["level"] == "hard" and q["bloom"] in ("remember", "understand"):
        errors.append(f"{where}: a hard question must require analyzing or evaluating (bloom is '{q['bloom']}')")
    if q["level"] == "easy" and q["bloom"] in ("analyze", "evaluate"):
        warnings.append(f"{where}: it is easy but requires '{q['bloom']}'; check the level")

    suggested = rubric_level(q)
    if suggested != q["level"]:
        warnings.append(f"{where}: the rubric adds up to {rubric_score(q)} and suggests {suggested}, but the level is {q['level']}")

    check_writing(q, where, errors, warnings)


def length_cues(questions):
    """How often the correct option is the longest or the shortest one, across the whole bank.

    By chance, with four options, each case happens in 25% of the questions. A very high share
    for "longest" is a clue people learn; a very low share for "shortest" is one too.
    """
    parts = []
    for lang in ("en", "es"):
        n = longest = shortest = expected = 0
        for q in questions:
            if q.get("keep_order") or len(q["answer"]) != 1:
                continue
            key = q["answer"][0]
            lens = {o["id"]: len(o["text"].get(lang, o["text"]["en"])) for o in q["options"]}
            others = [v for k, v in lens.items() if k != key]
            n += 1
            longest += lens[key] > max(others)
            shortest += lens[key] < min(others)
            expected += 1 / len(lens)
        if n:
            name = {"en": "English", "es": "Spanish"}[lang]
            parts.append(f"{name}, the correct option is the longest in {longest / n:.0%} and the shortest in {shortest / n:.0%}")
    return "; ".join(parts) + f" (by chance, {expected / n:.0%} each)" if parts else "no questions"


def print_summary(questions, taxonomy, group_of, total_bytes, drafts):
    total = len(questions)
    print(f"Questions: {total} in {len({q['area'] for q in questions})} of {len(group_of)} areas")
    if not total:
        return
    by_level = Counter(q["level"] for q in questions)
    print("Level:     " + ", ".join(f"{lvl} {by_level[lvl]}" for lvl in LEVELS))
    by_bloom = Counter(q["bloom"] for q in questions)
    print("Bloom:     " + ", ".join(f"{b} {by_bloom[b]}" for b in BLOOM if by_bloom[b]))
    by_stability = Counter(q["stability"] for q in questions)
    print("Stability: " + ", ".join(f"{k} {v}" for k, v in sorted(by_stability.items())))
    by_type = Counter(q["type"] for q in questions)
    print("Type:      " + ", ".join(f"{k} {v}" for k, v in sorted(by_type.items())))
    agree = sum(rubric_level(q) == q["level"] for q in questions)
    print(f"Rubric:    matches the level in {agree} of {total}")
    spanish = sum("es" in q["prompt"] for q in questions)
    print(f"Languages: English {total}, Spanish {spanish}")
    print("Length:    " + length_cues(questions))
    print(f"Size:      {total_bytes / 1024:.1f} KB in total, {total_bytes / total / 1024:.2f} KB per question")
    print(f"Unreviewed drafts (llm_draft): {len(drafts)}")
    print()
    names = {g["id"]: g["name"]["en"] for g in taxonomy["groups"]}
    width = max(len(n) for n in names.values())
    print(f"{'topic'.ljust(width)}  easy  medium  hard  total")
    for gid, name in names.items():
        counts = Counter(q["level"] for q in questions if group_of.get(q["area"]) == gid)
        row = "  ".join(str(counts[lvl]).rjust(len(lvl)) for lvl in LEVELS)
        print(f"{name.ljust(width)}  {row}  {str(sum(counts.values())).rjust(5)}")
    empty = sorted(set(group_of) - {q["area"] for q in questions})
    if empty:
        print(f"\nAreas without questions: {', '.join(empty)}")


def github_location(message):
    """The file, and line if there is one, that a message is about, for a GitHub annotation."""
    found = re.match(r"(\S+?\.json)(?:\[\d+\])? ([a-z0-9]+(?:-[a-z0-9]+)*-\d{4})\b", message)
    if not found:
        name = message.split(":", 1)[0]
        return f"file={name}" if name.endswith(".json") and " " not in name else ""
    path = ROOT / "questions" / found.group(1)
    needle = f'"id": "{found.group(2)}"'
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    line = next((n for n, text in enumerate(lines, 1) if needle in text), 1)
    return f"file=questions/{found.group(1)},line={line}"


def report(kind, message):
    """Prints an error or a warning; in GitHub Actions, as an annotation on the right line."""
    if os.environ.get("GITHUB_ACTIONS") == "true":
        location = github_location(message)
        print(f"::{kind}{' ' + location if location else ''}::{message.replace('%', '%25')}")
    else:
        print(f"{kind.upper()}  {message}")


def main():
    parser = argparse.ArgumentParser(description="Validates the question bank.")
    parser.add_argument("--publish", action="store_true", help="fail if any unreviewed draft is left")
    args = parser.parse_args()

    errors, warnings, drafts, questions = [], [], [], []
    schema = load_json(ROOT / "schema" / "question.schema.json")
    taxonomy = load_json(ROOT / "taxonomy.json")
    areas, group_of = check_taxonomy(taxonomy, errors)
    validator = Draft202012Validator(schema)

    seen_ids = {}
    total_bytes = 0
    for path in sorted((ROOT / "questions").glob("*.json")):
        total_bytes += path.stat().st_size
        data = load_json(path)
        if not isinstance(data, list):
            errors.append(f"{path.name}: must contain a list of questions")
            continue
        for i, q in enumerate(data):
            schema_errors = list(validator.iter_errors(q))
            for e in schema_errors:
                location = "/".join(str(p) for p in e.path) or "(root)"
                errors.append(f"{path.name}[{i}] {q.get('id', '?')}: {location}: {e.message}")
            if schema_errors:
                continue
            check_question(q, path, areas, seen_ids, errors, warnings)
            if q["origin"] == "llm_draft":
                drafts.append(q["id"])
            questions.append(q)

    if args.publish and drafts:
        errors.append(f"{len(drafts)} unreviewed drafts: {', '.join(drafts)}")

    print_summary(questions, taxonomy, group_of, total_bytes, drafts)
    for w in warnings:
        report("warning", w)
    for e in errors:
        report("error", e)
    print()
    print("OK" if not errors else f"{len(errors)} error{'s' if len(errors) > 1 else ''}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
