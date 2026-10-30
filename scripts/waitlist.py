#!/usr/bin/env python3
"""Summarizes the waitlists of the products that do not exist yet, and exports their emails.

The products are Interview, Enterprise and the online book (CONFIG.products in site/app.js). Reads
an export of the Cloudflare D1 database ai-ml-questions-waitlist (docs/waitlist.md):

    npx wrangler d1 export ai-ml-questions-waitlist --remote --output waitlist.sql
    python scripts/waitlist.py waitlist.sql                                    # sign-ups and opened cards
    python scripts/waitlist.py waitlist.sql --product book --emails book.csv   # one product's emails

waitlist.sql and the CSV files hold personal data. They are in .gitignore; delete them once used.
"""

import argparse
import csv
import sqlite3
import sys
from collections import Counter
from datetime import date
from pathlib import Path

PRODUCTS = ("interview", "enterprise", "book")
LANGUAGES = ("en", "es")
PLACES = ("home", "results")


def load(path):
    """Sign-ups and counts of opened cards in an export made by `wrangler d1 export`.

    An export made before there were several products has the old tables, waitlist and interest,
    whose rows are all about Interview."""
    db = sqlite3.connect(":memory:")
    db.executescript(Path(path).read_text(encoding="utf-8"))
    db.row_factory = sqlite3.Row
    tables = {row["name"] for row in db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    if "signups" in tables:
        signups = [dict(r) for r in db.execute("SELECT email, product, at, lang, place FROM signups ORDER BY at, email, product")]
        opens = [dict(r) for r in db.execute("SELECT day, lang, product, opens FROM opens ORDER BY day")] if "opens" in tables else []
    elif "waitlist" in tables:
        signups = [dict(r) for r in db.execute("SELECT email, 'interview' AS product, at, lang, place FROM waitlist ORDER BY at, email")]
        opens = [dict(r) for r in db.execute("SELECT day, lang, 'interview' AS product, opens FROM interest ORDER BY day")] if "interest" in tables else []
    else:
        sys.exit(f"{path} has no waitlist tables: export the database ai-ml-questions-waitlist.")
    return signups, opens


def week(day):
    """ISO week of a date or timestamp, as 2026-W44."""
    year, number, _ = date.fromisoformat(day[:10]).isocalendar()
    return f"{year}-W{number:02d}"


def summarize(signups, opens):
    """Per product: totals and one row per week, with sign-ups by language and place, and the
    browsers that opened its card."""
    summary = {}

    def row(product, key):
        weeks = summary.setdefault(product, {})
        return weeks.setdefault(key, Counter())

    for person in signups:
        r = row(person["product"], week(person["at"]))
        r["signups"] += 1
        r[person["lang"]] += 1
        r[person["place"]] += 1
    for count in opens:
        row(count["product"], week(count["day"]))["opened"] += count["opens"]

    result = {}
    for product in sorted(summary, key=lambda p: PRODUCTS.index(p) if p in PRODUCTS else len(PRODUCTS)):
        weeks = summary[product]
        total = Counter()
        for r in weeks.values():
            total.update(r)
        result[product] = {"total": total, "weeks": dict(sorted(weeks.items()))}
    return result


def share(part, whole):
    return f"{part} of {whole} ({round(100 * part / whole)}%)" if whole else f"{part} of 0"


def report(summary):
    if not summary:
        print("Waitlists: 0 sign-ups; cards opened by 0 browsers")
        return
    for n, (product, s) in enumerate(summary.items()):
        t = s["total"]
        if n:
            print()
        print(f"{product}: {t['signups']} sign-ups"
              f" ({' · '.join(f'{x} {t[x]}' for x in LANGUAGES)}; {' · '.join(f'{x} {t[x]}' for x in PLACES)})")
        print(f"  card opened by {t['opened']} browsers")
        # Each browser is counted once per product, the first time it opens that card, so this
        # approximates the share of people who saw the price and the form and left their email.
        print(f"  sign-ups on the home screen per browser that opened the card: {share(t['home'], t['opened'])}")
        columns = ("signups", *LANGUAGES, *PLACES, "opened")
        print(f"  {'Week':<9}  " + "  ".join(f"{c:>7}" for c in columns))
        for key, r in s["weeks"].items():
            print(f"  {key:<9}  " + "  ".join(f"{r[c]:>7}" for c in columns))


def export_emails(signups, path, product=None):
    """The emails with their product and language, so each announcement goes to the right people
    in the right language."""
    rows = [p for p in signups if product is None or p["product"] == product]
    with Path(path).open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["email", "product", "lang", "signed_up"])
        for person in rows:
            writer.writerow([person["email"], person["product"], person["lang"], person["at"][:10]])
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description="Summarizes the waitlists of Interview, Enterprise and the online book.")
    parser.add_argument("export", type=Path, help="waitlist.sql, from npx wrangler d1 export ai-ml-questions-waitlist")
    parser.add_argument("--product", choices=PRODUCTS, help="only this product")
    parser.add_argument("--emails", type=Path, help="also write the emails to this CSV file (personal data)")
    args = parser.parse_args()

    signups, opens = load(args.export)
    if args.product:
        signups = [p for p in signups if p["product"] == args.product]
        opens = [c for c in opens if c["product"] == args.product]
    report(summarize(signups, opens))
    if args.emails:
        n = export_emails(signups, args.emails)
        print(f"\n{n} emails written to {args.emails}. It holds personal data: delete it once used.")


if __name__ == "__main__":
    main()
