#!/usr/bin/env python3
"""Valida el banco de preguntas contra el esquema, la taxonomía y las reglas de redacción.

Uso:
    python scripts/validate.py            # revisa todo y muestra un resumen
    python scripts/validate.py --publish  # además falla si queda algún borrador (origin: llm_draft)

Requiere: pip install jsonschema
"""

import argparse
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:
    sys.exit("Falta jsonschema. Instálalo con: pip install jsonschema")

ROOT = Path(__file__).resolve().parent.parent
LEVELS = ["easy", "medium", "hard"]
BLOOM = ["remember", "understand", "apply", "analyze", "evaluate"]
BLOOM_SCORE = {"remember": 0, "understand": 0, "apply": 1, "analyze": 2, "evaluate": 2}
OPTION_IDS = "abcde"
# Suma máxima de la rúbrica (0 a 8) para cada nivel.
RUBRIC_BANDS = ((2, "easy"), (5, "medium"), (8, "hard"))

# Reglas de Haladyna, Downing y Rodriguez (2002) que se pueden revisar automáticamente.
LONGEST_RATIO = 1.2  # la correcta no debe destacar por ser la más larga
SPREAD_RATIO = 2.5  # ni las alternativas tener largos muy distintos
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


def rubric_score(q):
    return BLOOM_SCORE[q["bloom"]] + sum(q["difficulty"].values())


def rubric_level(q):
    """Nivel que sugiere la rúbrica de dificultad de la pregunta."""
    score = rubric_score(q)
    return next(level for top, level in RUBRIC_BANDS if score <= top)


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def check_taxonomy(taxonomy, errors):
    """Devuelve {área: {subtemas}} y {área: grupo}, y anota los problemas de la taxonomía."""
    areas = {}
    for area in taxonomy["areas"]:
        if area["id"] in areas:
            errors.append(f"taxonomy.json: área repetida '{area['id']}'")
        subtopics = [s["id"] for s in area["subtopics"]]
        repeated = sorted({s for s in subtopics if subtopics.count(s) > 1})
        if repeated:
            errors.append(f"taxonomy.json: subtemas repetidos en '{area['id']}': {', '.join(repeated)}")
        areas[area["id"]] = set(subtopics)

    group_of = {}
    group_ids = [g["id"] for g in taxonomy.get("groups", [])]
    for gid in sorted({g for g in group_ids if group_ids.count(g) > 1}):
        errors.append(f"taxonomy.json: grupo repetido '{gid}'")
    for group in taxonomy.get("groups", []):
        for area in group["areas"]:
            if area not in areas:
                errors.append(f"taxonomy.json: el grupo '{group['id']}' incluye el área inexistente '{area}'")
            elif area in group_of:
                errors.append(f"taxonomy.json: el área '{area}' está en '{group_of[area]}' y en '{group['id']}'")
            else:
                group_of[area] = group["id"]
    for area in areas:
        if area not in group_of:
            errors.append(f"taxonomy.json: el área '{area}' no está en ningún grupo")
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
        errors.append(f"{where}: {field} no es una fecha válida ({value})")
        return None


def question_sentence(prompt):
    """La última oración que termina en '?', que es la pregunta propiamente tal."""
    parts = re.split(r"(?<=[.!?])\s+", prompt.strip())
    questions = [p for p in parts if p.endswith("?")]
    return questions[-1] if questions else ""


def check_writing(q, where, errors, warnings):
    """Pistas que delatan la respuesta sin saber el tema (Haladyna et al., 2002)."""
    for lang in q["prompt"]:
        texts = {o["id"]: o["text"][lang] for o in q["options"]}
        lengths = {oid: len(t) for oid, t in texts.items()}
        right = q["answer"][0]
        others = [n for oid, n in lengths.items() if oid not in q["answer"]]
        if q["format"] == "single" and others:
            mean = sum(others) / len(others)
            if lengths[right] >= max(lengths.values()) and lengths[right] > LONGEST_RATIO * mean:
                warnings.append(
                    f"{where} [{lang}]: la correcta es la alternativa más larga ({lengths[right] / mean:.2f} veces el promedio de las demás)"
                )
        if max(lengths.values()) > SPREAD_RATIO * min(lengths.values()):
            warnings.append(f"{where} [{lang}]: las alternativas tienen largos muy distintos ({min(lengths.values())} a {max(lengths.values())} caracteres)")
        for oid, text in texts.items():
            found = re.search(ABSOLUTES[lang], text, re.IGNORECASE)
            if found:
                warnings.append(f"{where} [{lang}]: la alternativa {oid} usa un absoluto ('{found.group(0)}'), que delata que es falsa")
            if re.search(FORBIDDEN[lang], text, re.IGNORECASE):
                errors.append(f"{where} [{lang}]: la alternativa {oid} usa 'todas o ninguna de las anteriores'")
        sentence = question_sentence(q["prompt"][lang])
        if re.search(NEGATIVE_QUESTION[lang], sentence, re.IGNORECASE):
            warnings.append(f"{where} [{lang}]: la pregunta está en negativo; reescríbela en positivo si se puede")


def check_question(q, path, areas, seen_ids, errors, warnings):
    qid = q["id"]
    where = f"{path.name} {qid}"

    if path.stem != q["area"]:
        errors.append(f"{where}: está en {path.name} pero su área es '{q['area']}'")
    if not qid.startswith(q["area"] + "-"):
        errors.append(f"{where}: el id debe empezar con el área ('{q['area']}-')")
    if qid in seen_ids:
        errors.append(f"{where}: id repetido (también en {seen_ids[qid]})")
    seen_ids[qid] = path.name

    if q["area"] not in areas:
        errors.append(f"{where}: el área '{q['area']}' no existe en taxonomy.json")
    elif q["subtopic"] not in areas[q["area"]]:
        errors.append(f"{where}: el subtema '{q['subtopic']}' no existe en el área '{q['area']}'")

    option_ids = [o["id"] for o in q["options"]]
    expected = list(OPTION_IDS[: len(option_ids)])
    if option_ids != expected:
        errors.append(f"{where}: las alternativas deben ir en orden {', '.join(expected)}")
    missing = [a for a in q["answer"] if a not in option_ids]
    if missing:
        errors.append(f"{where}: la respuesta apunta a alternativas que no existen: {', '.join(missing)}")

    if len({frozenset(field) for field in text_fields(q)}) > 1:
        errors.append(f"{where}: todos los textos deben estar en los mismos idiomas")

    reviewed = parse_date(q["reviewed_at"], where, "reviewed_at", errors)
    if reviewed and reviewed > date.today():
        errors.append(f"{where}: reviewed_at está en el futuro")
    if "review_by" in q:
        review_by = parse_date(q["review_by"], where, "review_by", errors)
        if reviewed and review_by:
            if review_by <= reviewed:
                errors.append(f"{where}: review_by debe ser posterior a reviewed_at")
            elif review_by < date.today():
                warnings.append(f"{where}: venció su fecha de revisión ({q['review_by']})")

    if q["type"] == "evidence" and not any(s["kind"] in ("experiment", "paper") for s in q["sources"]):
        errors.append(f"{where}: una pregunta de tipo evidence necesita un experimento o paper como fuente")

    # Una pregunta difícil exige analizar o evaluar, no recordar algo de nicho.
    if q["level"] == "hard" and q["bloom"] in ("remember", "understand"):
        errors.append(f"{where}: una pregunta difícil debe exigir analizar o evaluar (bloom es '{q['bloom']}')")
    if q["level"] == "easy" and q["bloom"] in ("analyze", "evaluate"):
        warnings.append(f"{where}: es fácil pero exige '{q['bloom']}'; revisa el nivel")

    suggested = rubric_level(q)
    if suggested != q["level"]:
        warnings.append(f"{where}: la rúbrica suma {rubric_score(q)} y sugiere {suggested}, pero el nivel es {q['level']}")

    check_writing(q, where, errors, warnings)


def print_summary(questions, taxonomy, group_of, total_bytes, drafts):
    total = len(questions)
    print(f"Preguntas: {total} en {len({q['area'] for q in questions})} de {len(group_of)} áreas")
    if not total:
        return
    by_level = Counter(q["level"] for q in questions)
    print("Nivel:     " + ", ".join(f"{lvl} {by_level[lvl]}" for lvl in LEVELS))
    by_bloom = Counter(q["bloom"] for q in questions)
    print("Bloom:     " + ", ".join(f"{b} {by_bloom[b]}" for b in BLOOM if by_bloom[b]))
    by_stability = Counter(q["stability"] for q in questions)
    print("Vigencia:  " + ", ".join(f"{k} {v}" for k, v in sorted(by_stability.items())))
    by_type = Counter(q["type"] for q in questions)
    print("Tipo:      " + ", ".join(f"{k} {v}" for k, v in sorted(by_type.items())))
    agree = sum(rubric_level(q) == q["level"] for q in questions)
    print(f"Rúbrica:   coincide con el nivel en {agree} de {total}")
    spanish = sum("es" in q["prompt"] for q in questions)
    print(f"Idiomas:   inglés {total}, español {spanish}")
    print(f"Tamaño:    {total_bytes / 1024:.1f} KB en total, {total_bytes / total / 1024:.2f} KB por pregunta")
    print(f"Borradores sin revisar (llm_draft): {len(drafts)}")
    print()
    names = {g["id"]: g["name"]["es"] for g in taxonomy["groups"]}
    width = max(len(n) for n in names.values())
    print(f"{'contenido'.ljust(width)}  easy  medium  hard  total")
    for gid, name in names.items():
        counts = Counter(q["level"] for q in questions if group_of.get(q["area"]) == gid)
        row = "  ".join(str(counts[lvl]).rjust(len(lvl)) for lvl in LEVELS)
        print(f"{name.ljust(width)}  {row}  {str(sum(counts.values())).rjust(5)}")
    empty = sorted(set(group_of) - {q["area"] for q in questions})
    if empty:
        print(f"\nÁreas sin preguntas: {', '.join(empty)}")


def main():
    parser = argparse.ArgumentParser(description="Valida el banco de preguntas.")
    parser.add_argument("--publish", action="store_true", help="falla si queda algún borrador sin revisar")
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
            errors.append(f"{path.name}: debe contener una lista de preguntas")
            continue
        for i, q in enumerate(data):
            schema_errors = list(validator.iter_errors(q))
            for e in schema_errors:
                location = "/".join(str(p) for p in e.path) or "(raíz)"
                errors.append(f"{path.name}[{i}] {q.get('id', '?')}: {location}: {e.message}")
            if schema_errors:
                continue
            check_question(q, path, areas, seen_ids, errors, warnings)
            if q["origin"] == "llm_draft":
                drafts.append(q["id"])
            questions.append(q)

    if args.publish and drafts:
        errors.append(f"{len(drafts)} borradores sin revisar: {', '.join(drafts)}")

    print_summary(questions, taxonomy, group_of, total_bytes, drafts)
    for w in warnings:
        print(f"AVISO  {w}")
    for e in errors:
        print(f"ERROR  {e}")
    print()
    print("OK" if not errors else f"{len(errors)} errores")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
