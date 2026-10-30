"""Tests for scripts/waitlist.py and the waitlist migrations, on made-up exports of the database.

Run them with:  pip install jsonschema pytest && python -m pytest tests
"""
import csv
import sqlite3
from pathlib import Path

import waitlist

ROOT = Path(__file__).resolve().parent.parent
MIGRATIONS = sorted((ROOT / "migrations-waitlist").glob("*.sql"))
SCHEMA = "\n".join(path.read_text(encoding="utf-8") for path in MIGRATIONS)
ROWS = """
INSERT INTO signups (email, product, at, lang, place) VALUES ('ana@example.com', 'interview', '2026-10-26T10:00:00Z', 'es', 'home');
INSERT INTO signups (email, product, at, lang, place) VALUES ('ana@example.com', 'book', '2026-10-31T09:00:00Z', 'es', 'home');
INSERT INTO signups (email, product, at, lang, place) VALUES ('bo@example.com', 'interview', '2026-10-27T11:00:00Z', 'en', 'results');
INSERT INTO signups (email, product, at, lang, place) VALUES ('cy@example.com', 'enterprise', '2026-11-03T12:00:00Z', 'en', 'home');
INSERT INTO opens (day, lang, product, opens) VALUES ('2026-10-26', 'es', 'interview', 4);
INSERT INTO opens (day, lang, product, opens) VALUES ('2026-10-27', 'en', 'interview', 6);
INSERT INTO opens (day, lang, product, opens) VALUES ('2026-10-31', 'es', 'book', 3);
INSERT INTO opens (day, lang, product, opens) VALUES ('2026-11-02', 'en', 'enterprise', 2);
"""


def export(tmp_path, text=SCHEMA + ROWS):
    path = tmp_path / "waitlist.sql"
    path.write_text(text, encoding="utf-8")
    return path


def test_the_summary_counts_sign_ups_and_opened_cards_per_product_and_week(tmp_path):
    summary = waitlist.summarize(*waitlist.load(export(tmp_path)))
    assert list(summary) == ["interview", "enterprise", "book"]
    interview = summary["interview"]["total"]
    assert (interview["signups"], interview["en"], interview["es"], interview["home"], interview["results"], interview["opened"]) == (2, 1, 1, 1, 1, 10)
    assert list(summary["interview"]["weeks"]) == ["2026-W44"]
    assert summary["book"]["total"]["signups"] == 1 and summary["book"]["total"]["opened"] == 3
    assert list(summary["enterprise"]["weeks"]) == ["2026-W45"]


def test_the_emails_are_exported_with_their_product_and_language(tmp_path):
    rows, _ = waitlist.load(export(tmp_path))
    out = tmp_path / "emails.csv"
    assert waitlist.export_emails(rows, out, product="interview") == 2
    with out.open(newline="", encoding="utf-8") as f:
        lines = list(csv.reader(f))
    assert lines[0] == ["email", "product", "lang", "signed_up"]
    assert lines[1:] == [["ana@example.com", "interview", "es", "2026-10-26"], ["bo@example.com", "interview", "en", "2026-10-27"]]


def test_an_empty_waitlist_reports_zero(tmp_path, capsys):
    waitlist.report(waitlist.summarize(*waitlist.load(export(tmp_path, SCHEMA))))
    out = capsys.readouterr().out
    assert "0 sign-ups" in out and "opened by 0 browsers" in out


def test_an_export_from_before_the_products_counts_as_interview(tmp_path):
    old = MIGRATIONS[0].read_text(encoding="utf-8") + """
INSERT INTO waitlist (email, at, lang, place) VALUES ('ana@example.com', '2026-10-26T10:00:00Z', 'es', 'home');
INSERT INTO interest (day, lang, opens) VALUES ('2026-10-26', 'es', 4);
"""
    summary = waitlist.summarize(*waitlist.load(export(tmp_path, old)))
    assert list(summary) == ["interview"]
    assert summary["interview"]["total"]["signups"] == 1 and summary["interview"]["total"]["opened"] == 4


def test_the_migrations_keep_what_arrives_while_the_worker_is_updated():
    db = sqlite3.connect(":memory:")
    db.executescript(MIGRATIONS[0].read_text(encoding="utf-8"))
    db.execute("INSERT INTO waitlist (email, lang, place) VALUES ('ana@example.com', 'es', 'home')")
    db.execute("INSERT INTO interest (day, lang, opens) VALUES ('2026-10-30', 'es', 3)")
    db.executescript(MIGRATIONS[1].read_text(encoding="utf-8"))
    # The old Worker, until the new one is deployed: one more sign-up and two more opened cards.
    db.execute("INSERT INTO waitlist (email, lang, place) VALUES ('bo@example.com', 'en', 'results') ON CONFLICT (email) DO NOTHING")
    for _ in range(2):
        db.execute("INSERT INTO interest (day, lang, opens) VALUES ('2026-10-30', 'es', 1) ON CONFLICT (day, lang) DO UPDATE SET opens = opens + 1")
    # The new Worker: one more opened card.
    db.execute("INSERT INTO opens (day, lang, product, opens) VALUES ('2026-10-30', 'es', 'interview', 1) ON CONFLICT (day, lang, product) DO UPDATE SET opens = opens + 1")
    db.executescript(MIGRATIONS[2].read_text(encoding="utf-8"))
    assert db.execute("SELECT email, product FROM signups ORDER BY email").fetchall() == [("ana@example.com", "interview"), ("bo@example.com", "interview")]
    assert db.execute("SELECT opens FROM opens").fetchall() == [(6,)]
    assert {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")} == {"signups", "opens"}
