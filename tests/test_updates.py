"""Tests for updates.json, the changes listed on the site's home screen.

Run them with:  pip install jsonschema pytest && python -m pytest tests
"""
import copy
import json
from pathlib import Path

import pytest

import build_site

ROOT = Path(__file__).resolve().parent.parent
GOOD = {"date": "2026-10-25", "text": {"en": "Something changed.", "es": "Algo cambió."}}


def broken(**changes):
    update = copy.deepcopy(GOOD)
    for key, value in changes.items():
        if key in ("en", "es"):
            update["text"][key] = value
        else:
            update[key] = value
    return update


def test_a_good_update_passes():
    assert build_site.update_problems([GOOD]) == []


@pytest.mark.parametrize(
    "update, problem",
    [
        (broken(date="25/10/2026"), "the date must be a real day"),
        (broken(date="20261025"), "the date must be a real day"),
        (broken(date="2026-02-30"), "the date must be a real day"),
        ({"date": "2026-10-25", "text": {"en": "Something changed."}}, "needs a text in each language"),
        (broken(en=""), "the text is empty"),
        (broken(es="x" * 161), "the limit is 160"),
        (broken(link="https://example.com"), "needs exactly a date and a text"),
    ],
)
def test_a_broken_update_is_caught(update, problem):
    problems = build_site.update_problems([update])
    assert any(problem in p for p in problems), problems


def test_the_updates_file_passes():
    assert build_site.update_problems(json.loads((ROOT / "updates.json").read_text(encoding="utf-8"))) == []


def test_the_site_shows_the_current_updates():
    """site/data is committed, so after editing updates.json the site has to be built again."""
    index = json.loads((ROOT / "site" / "data" / "index.json").read_text(encoding="utf-8"))
    assert index.get("updates") == build_site.load_updates(), "run python scripts/build_site.py --include-drafts"
