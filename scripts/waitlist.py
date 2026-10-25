#!/usr/bin/env python3
"""Summarizes the waitlist of the Interview mode, and exports its emails when Interview opens.

Reads an export of the Cloudflare D1 database ai-ml-questions-waitlist (docs/waitlist.md):

    npx wrangler d1 export ai-ml-questions-waitlist --remote --output waitlist.sql
    python scripts/waitlist.py waitlist.sql                      # sign-ups and opened cards, by week
    python scripts/waitlist.py waitlist.sql --emails emails.csv  # the emails, with their language

waitlist.sql and emails.csv hold personal data. Both are in .gitignore; delete them once used.
"""

import argparse
import csv
import sqlite3
import sys
from collections import Counter
from datetime import date
from pathlib import Path

LANGUAGES = ("en", "es")
PLACES = ("home", "results")


def load(path):
    """The rows of the waitlist and interest tables in an export made by `wrangler d1 export`."""
    db = sqlite3.connect(":memory:")
    db.executescript(Path(path).read_text(encoding="utf-8"))
    db.row_factory = sqlite3.Row
    tables = {row["name"] for row in db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    if "waitlist" not in tables:
        sys.exit(f"{path} has no waitlist table: export the database ai-ml-questions-waitlist.")
    waitlist = [dict(r) for r in db.execute("SELECT email, at, lang, place FROM waitlist ORDER BY at, email")]
    interest = [dict(r) for r in db.execute("SELECT day, lang, opens FROM interest ORDER BY day")] if "interest" in tables else []
    return waitlist, interest


def week(day):
    """ISO week of a date or timestamp, as 2026-W44."""
    year, number, _ = date.fromisoformat(day[:10]).isocalendar()
    return f"{year}-W{number:02d}"


def summarize(waitlist, interest):
    """Totals and one row per week: sign-ups by language and place, and browsers that opened the card."""
    weeks = {}

    def row(key):
        return weeks.setdefault(key, Counter())

    for person in waitlist:
        r = row(week(person["at"]))
        r["signups"] += 1
        r[person["lang"]] += 1
        r[person["place"]] += 1
    for count in interest:
        row(week(count["day"]))["opened"] += count["opens"]

    total = Counter()
    for r in weeks.values():
        total.update(r)
    return {"total": total, "weeks": dict(sorted(weeks.items()))}


def share(part, whole):
    return f"{part} of {whole} ({round(100 * part / whole)}%)" if whole else f"{part} of 0"


def report(summary):
    t = summary["total"]
    print(f"Waitlist: {t['signups']} sign-ups"
          f" ({' · '.join(f'{x} {t[x]}' for x in LANGUAGES)}; {' · '.join(f'{x} {t[x]}' for x in PLACES)})")
    print(f"Interview card opened by {t['opened']} browsers")
    # Each browser is counted once, the first time it opens the card, so this approximates the share
    # of people who saw the price and the form and left their email.
    print(f"Sign-ups on the home screen per browser that opened the card: {share(t['home'], t['opened'])}")
    if not summary["weeks"]:
        return
    print()
    columns = ("signups", *LANGUAGES, *PLACES, "opened")
    print(f"{'Week':<9}  " + "  ".join(f"{c:>7}" for c in columns))
    for key, r in summary["weeks"].items():
        print(f"{key:<9}  " + "  ".join(f"{r[c]:>7}" for c in columns))


def export_emails(waitlist, path):
    """The emails with their language, so the message announcing Interview goes in the right one."""
    with Path(path).open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["email", "lang", "signed_up"])
        for person in waitlist:
            writer.writerow([person["email"], person["lang"], person["at"][:10]])


def main():
    parser = argparse.ArgumentParser(description="Summarizes the waitlist of the Interview mode.")
    parser.add_argument("export", type=Path, help="waitlist.sql, from npx wrangler d1 export ai-ml-questions-waitlist")
    parser.add_argument("--emails", type=Path, help="also write the emails to this CSV file (personal data)")
    args = parser.parse_args()

    waitlist, interest = load(args.export)
    report(summarize(waitlist, interest))
    if args.emails:
        export_emails(waitlist, args.emails)
        print(f"\n{len(waitlist)} emails written to {args.emails}. It holds personal data: delete it once used.")


if __name__ == "__main__":
    main()
