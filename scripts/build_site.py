#!/usr/bin/env python3
"""Builds the site's data from the question bank.

Writes to site/data/ the taxonomy, an index with the counts per area and level, and one
minified file of questions per area. It also writes site/precache.json (what the service worker
stores to work offline) and updates the version in site/sw.js.

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
    }
    write_json(DATA / "index.json", index)
    return total, len(counts)


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
    total, areas = build_data(args.include_drafts)
    if total == 0:
        print("WARNING  No publishable questions. Review some, or use --include-drafts to test.")
    files = write_precache()
    version = bump_service_worker(files)
    drafts = " (drafts included)" if args.include_drafts else ""
    print(f"site/data: {total} questions in {areas} areas{drafts}")
    print(f"precache.json: {len(files) + 1} entries · service worker version {version}")


if __name__ == "__main__":
    main()
