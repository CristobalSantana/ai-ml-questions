#!/usr/bin/env python3
"""Genera los datos del sitio a partir del banco de preguntas.

Escribe en site/data/ la taxonomía, un índice con los conteos por área y nivel, y un archivo
minificado de preguntas por área. Además escribe site/precache.json (lo que el service worker
guarda para funcionar sin conexión) y actualiza la versión de site/sw.js.

Uso:
    python scripts/build_site.py                  # solo preguntas revisadas (human, llm_reviewed)
    python scripts/build_site.py --include-drafts # también borradores, para probar el prototipo
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
# Archivos del sitio que el service worker no necesita guardar.
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
        sys.exit("El banco tiene errores; corrígelos antes de generar el sitio.")


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
        sys.exit("No encontré la línea const VERSION en site/sw.js.")
    sw.write_text(new_text, encoding="utf-8")
    return version


def main():
    parser = argparse.ArgumentParser(description="Genera los datos del sitio.")
    parser.add_argument("--include-drafts", action="store_true", help="incluye preguntas sin revisar (llm_draft)")
    args = parser.parse_args()

    validate()
    total, areas = build_data(args.include_drafts)
    if total == 0:
        print("AVISO  No hay preguntas publicables. Revisa algunas o usa --include-drafts para probar.")
    files = write_precache()
    version = bump_service_worker(files)
    drafts = " (con borradores)" if args.include_drafts else ""
    print(f"site/data: {total} preguntas en {areas} áreas{drafts}")
    print(f"precache.json: {len(files) + 1} entradas · versión del service worker {version}")


if __name__ == "__main__":
    main()
