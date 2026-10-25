#!/usr/bin/env python3
"""Builds the site's data from the question bank.

Writes to site/data/ the taxonomy, an index with the counts per area and level and the updates
listed on the home screen (from updates.json), and one minified file of questions per area. It
also writes the number of questions and topics into site/index.html (so the header does not change
size when the data arrives), site/precache.json (what the service worker stores to work offline)
and the version in site/sw.js.

Usage:
    python scripts/build_site.py                  # reviewed questions only (human, llm_reviewed)
    python scripts/build_site.py --include-drafts # drafts too, for testing the prototype
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
DATA = SITE / "data"
PUBLISHABLE = {"human", "llm_reviewed"}
LEVELS = ("easy", "medium", "hard")
# Site files the service worker does not need to store.
NOT_PRECACHED = {"sw.js", "precache.json"}
# The updates on the home screen are one short sentence per language; the limits keep them brief.
MAX_UPDATE = {"en": 140, "es": 160}


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def validate():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate.py")], capture_output=True, text=True
    )
    if result.returncode != 0:
        print(result.stdout)
        sys.exit("The bank has errors; fix them before building the site.")


def build_data(include_drafts):
    taxonomy = json.loads((ROOT / "taxonomy.json").read_text(encoding="utf-8"))
    if DATA.exists():
        shutil.rmtree(DATA)

    slim = {
        "groups": taxonomy["groups"],
        "areas": [
            {
                "id": area["id"],
                "name": area["name"],
                "subtopics": [{"id": s["id"], "name": s["name"]} for s in area["subtopics"]],
            }
            for area in taxonomy["areas"]
        ]
    }
    write_json(DATA / "taxonomy.json", slim)

    counts, files, total = {}, [], 0
    for area in taxonomy["areas"]:
        path = ROOT / "questions" / f"{area['id']}.json"
        questions = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
        if not include_drafts:
            questions = [q for q in questions if q["origin"] in PUBLISHABLE]
        if not questions:
            continue
        write_json(DATA / "questions" / f"{area['id']}.json", questions)
        files.append(f"data/questions/{area['id']}.json")
        counts[area["id"]] = {level: sum(q["level"] == level for q in questions) for level in LEVELS}
        total += len(questions)

    index = {
        "generated": date.today().isoformat(),
        "drafts_included": include_drafts,
        "total": total,
        "counts": counts,
        "files": files,
        "updates": load_updates(),
    }
    write_json(DATA / "index.json", index)
    topics = sum(any(area in counts for area in group["areas"]) for group in taxonomy["groups"])
    return total, len(counts), topics


def update_problems(updates):
    """What is wrong in updates.json: each update needs a date and one short sentence per language."""
    problems = []
    if not isinstance(updates, list):
        return ["updates.json must be a list of updates"]
    for i, u in enumerate(updates, 1):
        when = u.get("date") if isinstance(u, dict) else None
        where = f"update {i} ({when})" if when else f"update {i}"
        if not isinstance(u, dict) or set(u) != {"date", "text"}:
            problems.append(f"{where}: needs exactly a date and a text")
            continue
        try:
            valid = bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", when)) and date.fromisoformat(when)
        except (TypeError, ValueError):
            valid = False
        if not valid:
            problems.append(f"{where}: the date must be a real day, as YYYY-MM-DD")
        text = u["text"] if isinstance(u["text"], dict) else {}
        if set(text) != set(MAX_UPDATE):
            problems.append(f"{where}: needs a text in each language ({', '.join(MAX_UPDATE)})")
        for lang, limit in MAX_UPDATE.items():
            sentence = text.get(lang)
            if lang in text and not (isinstance(sentence, str) and sentence.strip()):
                problems.append(f"{where} [{lang}]: the text is empty")
            elif isinstance(sentence, str) and len(sentence) > limit:
                problems.append(f"{where} [{lang}]: {len(sentence)} characters; the limit is {limit}")
    return problems


def load_updates():
    """The changes listed on the home screen (updates.json), newest first. Entries of the same day
    keep the order of the file."""
    path = ROOT / "updates.json"
    if not path.exists():
        return []
    updates = json.loads(path.read_text(encoding="utf-8"))
    problems = update_problems(updates)
    if problems:
        sys.exit("updates.json has errors:\n" + "\n".join(f"  {p}" for p in problems))
    return sorted(updates, key=lambda u: u["date"], reverse=True)


def write_bank_size(total, topics):
    """Puts the counts in the header of index.html, in English, as app.js shows them (bankSize)."""
    page = SITE / "index.html"
    label = f"{total} {'question' if total == 1 else 'questions'} · {topics} {'topic' if topics == 1 else 'topics'}"
    span = f'<span class="bank-size" id="bank-size" data-total="{total}" data-topics="{topics}">{label}</span>'
    text, n = re.subn(r'<span class="bank-size" id="bank-size"[^>]*>[^<]*</span>', span, page.read_text(encoding="utf-8"), count=1)
    if n != 1:
        sys.exit('Could not find <span class="bank-size" id="bank-size"> in site/index.html.')
    page.write_text(text, encoding="utf-8")


def write_precache():
    files = sorted(
        p.relative_to(SITE).as_posix()
        for p in SITE.rglob("*")
        if p.is_file()
        and p.relative_to(SITE).as_posix() not in NOT_PRECACHED
        and not p.name.startswith(".")
        and p.suffix != ".txt"
    )
    write_json(SITE / "precache.json", ["./", *files])
    return files


def bump_service_worker(files):
    digest = hashlib.sha256()
    for name in files:
        digest.update(name.encode())
        digest.update((SITE / name).read_bytes())
    version = digest.hexdigest()[:12]
    sw = SITE / "sw.js"
    text = sw.read_text(encoding="utf-8")
    new_text, n = re.subn(r'const VERSION = "[^"]*";', f'const VERSION = "{version}";', text, count=1)
    if n != 1:
        sys.exit("Could not find the const VERSION line in site/sw.js.")
    sw.write_text(new_text, encoding="utf-8")
    return version


def main():
    parser = argparse.ArgumentParser(description="Builds the site data.")
    parser.add_argument("--include-drafts", action="store_true", help="include unreviewed questions (llm_draft)")
    args = parser.parse_args()

    validate()
    total, areas, topics = build_data(args.include_drafts)
    if total == 0:
        print("WARNING  No publishable questions. Review some, or use --include-drafts to test.")
    write_bank_size(total, topics)
    files = write_precache()
    version = bump_service_worker(files)
    drafts = " (drafts included)" if args.include_drafts else ""
    print(f"site/data: {total} questions in {areas} areas{drafts}")
    print(f"precache.json: {len(files) + 1} entries · service worker version {version}")


if __name__ == "__main__":
    main()
