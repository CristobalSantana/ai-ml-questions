"""Tests for scripts/validate.py.

Each test takes a question that passes every check, breaks one rule on purpose and checks that
the validator notices. The last test runs the validator on the whole bank.

Run them with:  pip install jsonschema pytest && python -m pytest tests
"""
import copy
from pathlib import Path

import pytest

import validate

ROOT = Path(__file__).resolve().parent.parent
AREAS, _ = validate.check_taxonomy(validate.load_json(ROOT / "taxonomy.json"), [])
SCHEMA = validate.Draft202012Validator(validate.load_json(ROOT / "schema" / "question.schema.json"))


def option(oid, en, es):
    return {
        "id": oid,
        "text": {"en": en, "es": es},
        "rationale": {"en": "Why it is right or wrong.", "es": "Por qué es correcta o incorrecta."},
    }


# A question that passes every check. Each test changes one thing.
BASE = {
    "id": "retrieval-9001",
    "version": 1,
    "area": "retrieval",
    "subtopic": "embeddings-similarity",
    "level": "easy",
    "bloom": "understand",
    "type": "concept",
    "format": "single",
    "stability": "stable",
    "difficulty": {"steps": 0, "specialization": 0, "distractors": 1},
    "prompt": {
        "en": "What does the cosine similarity between two embeddings measure?",
        "es": "¿Qué mide la similitud coseno entre dos embeddings?",
    },
    "options": [
        option("a", "The angle between the two vectors, regardless of their lengths.",
               "El ángulo entre los dos vectores, sin importar su largo."),
        option("b", "The straight-line distance between the tips of the two vectors.",
               "La distancia en línea recta entre las puntas de los vectores."),
        option("c", "The number of dimensions that both vectors have in common.",
               "La cantidad de dimensiones que ambos vectores tienen en común."),
        option("d", "The difference between the lengths of the two vectors.",
               "La diferencia entre el largo de los dos vectores."),
    ],
    "answer": ["a"],
    "explanation": {
        "en": "Cosine similarity compares directions, not lengths.",
        "es": "La similitud coseno compara direcciones, no largos.",
    },
    "sources": [{"kind": "book", "title": "Introduction to Information Retrieval"}],
    "origin": "human",
    "reviewed_at": "2026-10-01",
}


def question(**changes):
    """A copy of BASE with some fields replaced."""
    q = copy.deepcopy(BASE)
    q.update(changes)
    return q


def with_option(q, oid, **texts):
    """Replaces the text of one option, in the languages given."""
    for o in q["options"]:
        if o["id"] == oid:
            o["text"].update(texts)
    return q


def with_options(q, pairs):
    """Replaces the text of every option with (English, Spanish) pairs."""
    for o, (en, es) in zip(q["options"], pairs):
        o["text"] = {"en": en, "es": es}
    return q


def problems(q):
    """The errors and warnings that the validator finds in one question."""
    errors, warnings = [f"schema: {e.message}" for e in SCHEMA.iter_errors(q)], []
    if not errors:
        validate.check_question(q, ROOT / "questions" / f"{q['area']}.json", AREAS, {}, errors, warnings)
    return errors, warnings


def flagged(messages, *fragments):
    return any(all(fragment in m for fragment in fragments) for m in messages)


def test_the_base_question_passes():
    assert problems(question()) == ([], [])


# Length limits: a long stem or option is hard to read on a phone.

@pytest.mark.parametrize("lang, limit", [("en", 300), ("es", 350)])
def test_a_stem_over_the_limit_is_an_error(lang, limit):
    q = question()
    q["prompt"][lang] = "x" * limit + "?"
    errors, _ = problems(q)
    assert flagged(errors, f"[{lang}]", f"the stem has {limit + 1} characters")


@pytest.mark.parametrize("lang, limit", [("en", 300), ("es", 350)])
def test_a_stem_at_the_limit_passes(lang, limit):
    q = question()
    q["prompt"][lang] = "x" * (limit - 1) + "?"
    errors, _ = problems(q)
    assert errors == []


@pytest.mark.parametrize("lang, limit", [("en", 150), ("es", 170)])
def test_an_option_over_the_limit_is_an_error(lang, limit):
    q = with_option(question(), "b", **{lang: "x" * limit + "."})
    errors, _ = problems(q)
    assert flagged(errors, f"[{lang}]", f"option b has {limit + 1} characters")


def test_code_over_the_limit_is_an_error():
    source = "\n".join(f"x = {i}" for i in range(16))
    errors, _ = problems(question(type="code", code={"lang": "python", "source": source}))
    assert flagged(errors, "the code has 16 lines")


# Writing rules from Haladyna, Downing and Rodriguez (2002).

def test_a_stem_that_is_not_a_question_is_an_error():
    q = question()
    q["prompt"]["en"] = "Cosine similarity measures the angle between two embeddings."
    errors, _ = problems(q)
    assert flagged(errors, "[en]", "must end with the question")


@pytest.mark.parametrize("lang, text", [
    ("en", "What does cosine similarity NOT measure?"),
    ("es", "¿Qué NO mide la similitud coseno?"),
])
def test_a_negative_question_is_a_warning(lang, text):
    q = question()
    q["prompt"][lang] = text
    _, warnings = problems(q)
    assert flagged(warnings, f"[{lang}]", "negatively")


def test_a_correct_option_that_stands_out_by_length_is_a_warning():
    longer = "The angle between the two vectors, regardless of their lengths, so it compares meaning."
    _, warnings = problems(with_option(question(), "a", en=longer))
    assert flagged(warnings, "[en]", "the correct option is the longest")


def test_options_of_very_different_lengths_are_a_warning():
    _, warnings = problems(with_option(question(), "d", en="Their size."))
    assert flagged(warnings, "[en]", "differ a lot in length")


@pytest.mark.parametrize("lang, text", [
    ("en", "It always measures the straight-line distance between the vectors."),
    ("es", "Siempre mide la distancia en línea recta entre los vectores."),
])
def test_an_absolute_is_a_warning(lang, text):
    _, warnings = problems(with_option(question(), "b", **{lang: text}))
    assert flagged(warnings, f"[{lang}]", "absolute")


@pytest.mark.parametrize("lang, text", [
    ("en", "All of the above."),
    ("en", "None of the above."),
    ("es", "Todas las anteriores."),
    ("es", "Ninguna de las anteriores."),
])
def test_all_or_none_of_the_above_is_an_error(lang, text):
    errors, _ = problems(with_option(question(), "d", **{lang: text}))
    assert flagged(errors, f"[{lang}]", "all or none of the above")


@pytest.mark.parametrize("lang, text", [
    ("en", "A and B."),
    ("en", "Both A and C."),
    ("en", "A, B and C."),
    ("es", "A y B."),
])
def test_an_option_that_combines_others_is_an_error(lang, text):
    errors, _ = problems(with_option(question(), "d", **{lang: text}))
    assert flagged(errors, f"[{lang}]", "combines other options")


def test_two_options_that_say_the_same_are_an_error():
    same = "The straight-line distance between the tips of the two vectors!"
    errors, _ = problems(with_option(question(), "c", en=same))
    assert flagged(errors, "[en]", "two options say the same thing")


def test_an_option_inside_another_is_a_warning():
    bigger = "The straight-line distance between the tips of the two vectors, and their angle."
    _, warnings = problems(with_option(question(), "c", en=bigger))
    assert flagged(warnings, "[en]", "option b is contained in option c")


def test_options_that_end_differently_are_a_warning():
    no_period = "The straight-line distance between the tips of the two vectors"
    _, warnings = problems(with_option(question(), "b", en=no_period))
    assert flagged(warnings, "[en]", "end with a period")


def test_numbers_out_of_order_with_keep_order_are_a_warning():
    q = with_options(question(keep_order=True), [("0.50", "0,50"), ("0.98", "0,98"), ("0.73", "0,73"), ("0.88", "0,88")])
    _, warnings = problems(q)
    assert flagged(warnings, "[en]", "not in order")
    assert flagged(warnings, "[es]", "not in order")


def test_numbers_in_order_with_keep_order_pass():
    q = with_options(question(keep_order=True), [("0.50", "0,50"), ("0.73", "0,73"), ("0.88", "0,88"), ("0.98", "0,98")])
    _, warnings = problems(q)
    assert not flagged(warnings, "not in order")


def test_thousands_separators_are_read_in_each_language():
    pairs = [("4,096", "4.096"), ("16,384", "16.384"), ("65,536", "65.536"), ("262,144", "262.144")]
    _, warnings = problems(with_options(question(keep_order=True), pairs))
    assert not flagged(warnings, "not in order")


# Other rules.

def test_a_hard_question_must_require_analysis():
    errors, _ = problems(question(level="hard"))
    assert flagged(errors, "a hard question must require analyzing or evaluating")


def test_every_text_needs_the_same_languages():
    q = question()
    del q["options"][1]["rationale"]["es"]
    errors, _ = problems(q)
    assert flagged(errors, "every text must be in the same languages")


def test_the_schema_requires_three_options():
    q = question()
    q["options"] = q["options"][:2]
    errors, _ = problems(q)
    assert flagged(errors, "schema:")


# The whole bank.

def test_every_question_in_the_bank_passes():
    errors, seen = [], {}
    for path in sorted((ROOT / "questions").glob("*.json")):
        for q in validate.load_json(path):
            schema_errors = [f"{path.name} {q.get('id')}: {e.message}" for e in SCHEMA.iter_errors(q)]
            errors += schema_errors
            if not schema_errors:
                validate.check_question(q, path, AREAS, seen, errors, [])
    assert errors == []
