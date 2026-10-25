"""Tests for scripts/waitlist.py, on a made-up export of the waitlist database.

Run them with:  pip install jsonschema pytest && python -m pytest tests
"""
import csv
from pathlib import Path

import waitlist

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = (ROOT / "migrations-waitlist" / "0001_waitlist.sql").read_text(encoding="utf-8")
ROWS = """
INSERT INTO waitlist (email, at, lang, place) VALUES ('ana@example.com', '2026-10-26T10:00:00Z', 'es', 'home');
INSERT INTO waitlist (email, at, lang, place) VALUES ('bo@example.com', '2026-10-27T11:00:00Z', 'en', 'results');
INSERT INTO waitlist (email, at, lang, place) VALUES ('cy@example.com', '2026-11-03T12:00:00Z', 'en', 'home');
INSERT INTO interest (day, lang, opens) VALUES ('2026-10-26', 'es', 4);
INSERT INTO interest (day, lang, opens) VALUES ('2026-10-27', 'en', 6);
INSERT INTO interest (day, lang, opens) VALUES ('2026-11-02', 'en', 2);
"""


def export(tmp_path):
    path = tmp_path / "waitlist.sql"
    path.write_text(SCHEMA + ROWS, encoding="utf-8")
    return path


def test_the_summary_counts_sign_ups_and_opened_cards_by_week(tmp_path):
    summary = waitlist.summarize(*waitlist.load(export(tmp_path)))
    total = summary["total"]
    assert (total["signups"], total["en"], total["es"], total["home"], total["results"], total["opened"]) == (3, 2, 1, 2, 1, 12)
    assert list(summary["weeks"]) == ["2026-W44", "2026-W45"]
    assert summary["weeks"]["2026-W44"]["signups"] == 2 and summary["weeks"]["2026-W44"]["opened"] == 10
    assert summary["weeks"]["2026-W45"]["signups"] == 1 and summary["weeks"]["2026-W45"]["opened"] == 2


def test_the_emails_are_exported_with_their_language(tmp_path):
    rows, _ = waitlist.load(export(tmp_path))
    out = tmp_path / "emails.csv"
    waitlist.export_emails(rows, out)
    with out.open(newline="", encoding="utf-8") as f:
        lines = list(csv.reader(f))
    assert lines[0] == ["email", "lang", "signed_up"]
    assert lines[1:] == [["ana@example.com", "es", "2026-10-26"], ["bo@example.com", "en", "2026-10-27"], ["cy@example.com", "en", "2026-11-03"]]


def test_an_empty_waitlist_reports_zero(tmp_path, capsys):
    path = tmp_path / "waitlist.sql"
    path.write_text(SCHEMA, encoding="utf-8")
    waitlist.report(waitlist.summarize(*waitlist.load(path)))
    out = capsys.readouterr().out
    assert "0 sign-ups" in out and "opened by 0 browsers" in out
