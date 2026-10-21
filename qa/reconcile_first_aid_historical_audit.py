#!/usr/bin/env python3
"""Relate the pinned Beta49 audit rows to the preserved Common card IDs."""

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "content-packs/locomotive-migration/migration/historical-documents.candidate.json"
CARDS = ROOT / "content-packs/common/first-aid/topics.pack.json"
OUT = ROOT / "content-packs/common/first-aid/migration/beta49-audit-relations.candidate.json"
AUDIT = "docs/first-aid-audit-beta49.md"

# The two renamed titles are explicit and never guessed by fuzzy matching.
IDS = {
    "Нет сознания": "unconscious", "Не дышит / СЛР": "cpr",
    "Кровотечение": "bleeding", "Кровь из носа": "nosebleed",
    "Подавился": "airway", "Травмы и переломы": "trauma",
    "Рана груди / живота": "chest_abdomen", "Ожоги": "burn",
    "Перегревание": "heat", "Электротравма": "electric",
    "Отравление": "poisoning", "Химическое поражение": "chemical",
    "Переохлаждение": "hypothermia", "Обморожение": "frostbite",
    "Укус / ужаливание": "bites", "Острая реакция на стресс": "stress",
    "Судороги": "seizure", "Аптечка": "worker-kit",
}
ADDITIONS = {"Кровь из носа", "Рана груди / живота", "Перегревание"}
NUMERIC = {
    "Оценка дыхания": ("cpr", "10 секунд"),
    "Надавливания при СЛР взрослому": ("cpr", "100–120"),
    "Соотношение СЛР": ("cpr", "30 надавливаний и 2 вдоха"),
    "Термический ожог": ("burn", "20 минут"),
    "Химический ожог кожи": ("chemical", "20 минут"),
    "Жгут": ("bleeding", "5–7 см"),
    "Носовое кровотечение": ("nosebleed", "15–20 минут"),
}


def sha(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def table(text, heading):
    section = text.split("## " + heading + "\n", 1)[1].split("\n## ", 1)[0]
    return [line.strip().split("|")[1:-1] for line in section.splitlines()
            if line.startswith("| ") and not line.startswith("|---")
            and not line.startswith("| ---")][1:]


def project():
    archive = json.loads(ARCHIVE.read_text())
    document, = [d for d in archive["documents"] if d["sourcePath"] == AUDIT]
    text = document["exactSourceText"]
    cards = {e["id"].split(".")[-1]: e for e in json.loads(CARDS.read_text())["entries"]
             if e["type"] == "FIRST_AID"}
    assert len(cards) == len(IDS) == 18
    audit_rows = table(text, "Результаты по карточкам")
    assert len(audit_rows) == 15
    rows = []
    for cells in audit_rows:
        assert len(cells) == 4
        title, historical_status, finding, change = map(str.strip, cells)
        assert title in IDS and title not in ADDITIONS
        card = cards[IDS[title]]
        assert card["publicationStatus"] == "CANDIDATE"
        assert card["actionDisposition"] == "INFORMATION_ONLY"
        rows.append({"auditTitle": title, "auditRecord": {"statusBeforeBeta49": historical_status,
                     "finding": finding, "changeRecordedInBeta49": change},
                     "canonicalCandidateId": card["id"],
                     "canonicalCandidateTitle": card["title"],
                     "canonicalCandidateSha256": sha(json.dumps(card, ensure_ascii=False, sort_keys=True,
                                                                   separators=(",", ":"))),
                     "relationship": "HISTORICAL_AUDIT_MENTION_ONLY"})
    addition_section = text.split("## Устранённые пробелы\n", 1)[1].split("\n## ", 1)[0]
    for title in ("Кровь из носа", "Рана груди / живота", "Перегревание"):
        match = re.search(r'^- «' + re.escape(title) + r'» — (.+)$', addition_section, re.M)
        assert match
        card = cards[IDS[title]]
        rows.append({"auditTitle": title, "auditRecord": {"additionDescription": match.group(1)},
                     "canonicalCandidateId": card["id"],
                     "canonicalCandidateTitle": card["title"],
                     "canonicalCandidateSha256": sha(json.dumps(card, ensure_ascii=False, sort_keys=True,
                                                                   separators=(",", ":"))),
                     "relationship": "HISTORICAL_AUDIT_MENTION_ONLY"})
    assert len(rows) == len({r["canonicalCandidateId"] for r in rows}) == 18
    numeric = []
    numeric_rows = table(text, "Проверенные числовые параметры")
    assert len(numeric_rows) == len(NUMERIC) == 7
    for cells in numeric_rows:
        assert len(cells) == 2
        label, value = map(str.strip, cells)
        key, literal = NUMERIC[label]
        card = cards[key]
        body = json.dumps(card["blocks"], ensure_ascii=False)
        assert literal in body, (label, literal)
        numeric.append({"auditParameter": label, "historicalAuditValue": value,
                        "canonicalCandidateId": card["id"], "matchedCandidateFragment": literal,
                        "relationship": "TEXTUAL_SOURCE_COMPARISON_NOT_CURRENT_MEDICAL_APPROVAL"})
    return {"schemaVersion": 1, "donorCommit": archive["donorCommit"],
            "sourcePath": AUDIT, "sourceBlobSha": document["sourceBlobSha"],
            "sourceTextSha256": sha(text), "publicationStatus": "CANDIDATE",
            "runtimeImport": False, "currentAuthorityVerified": False,
            "actionAuthorityGranted": False,
            "note": "The 15 historical audit rows, three added topics and seven number rows are cross-references to existing Common candidate cards. Historical 'current' labels and external source links are preserved only in the source document; this comparison neither updates medical guidance nor proves every procedural field.",
            "cardRelations": rows, "numericRelations": numeric}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    projected = project()
    encoded = json.dumps(projected, ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert OUT.read_text() == encoded
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(encoded)
    print("FIRST_AID_HISTORICAL_AUDIT_PASS 15 3 7")


if __name__ == "__main__":
    main()
