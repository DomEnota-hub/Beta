#!/usr/bin/env python3
"""Project the pinned Kotlin Ermak acceptance source without activating routes."""

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content-packs/locomotive-migration/source-assets/TechnicalDataRepository.kt"
OUTPUT = ROOT / "content-packs/electric/ermak/acceptance/migration/kotlin-source.candidate.json"
EQUIPMENT = ROOT / "content-packs/electric/ermak/atlas/equipment"
DONOR_BLOB = "26a7dfce56f6f99f43a220923a1a66096af093c1"
EQUIPMENT_BLOB = "47a8d2424d69943fba9747746aa6ad8c8f4e2e98"


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def project():
    raw = SOURCE.read_bytes()
    assert hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == DONOR_BLOB
    text = raw.decode("utf-8")
    assert text.count("private fun loadErmakAcceptance(): List<TechnicalEntry>") == 1
    function = text.split("private fun loadErmakAcceptance(): List<TechnicalEntry> {", 1)[1]
    function = function.split("private fun loadErmakSystems(): List<TechnicalEntry>", 1)[0]
    requirements = function.split("requirements = listOf(", 1)[1].split("\n        )\n    )", 1)[0]
    pairs = re.findall(r'^\s*"([^"\n]+)" to "([^"\n]+)"[,]?$', requirements, re.M)
    assert len(pairs) == 18 and requirements.count('" to "') == 18
    assert "prefix = \"ER-REQ\"" in function
    assert "ERMAK_REQUIRED_ACCEPTANCE_COUNT = 18" in text
    source = "ИДМБ.661142.009РЭ7 (3ТС.001.012РЭ7), раздел 3.10 «Техническое обслуживание ТО-1»"
    assert f'source = "{source}"' in function
    required = [{"originalId": f"ER-REQ-{i:02}", "order": i,
                 "title": title, "check": check, "originalStatus": "MANDATORY_CHECK",
                 "sourceLabelFromDonor": source,
                 "publicationStatus": "CANDIDATE", "currentRequirednessVerified": False,
                 "actionAuthorityGranted": False}
                for i, (title, check) in enumerate(pairs, 1)]
    assert len({x["originalId"] for x in required}) == 18

    entries = []
    for path in sorted(EQUIPMENT.glob("*.pack.json")):
        entries.extend(json.loads(path.read_text())["entries"])
    assert len(entries) == len({e["id"] for e in entries}) == 111
    expanded = []
    for entry in entries:
        original = entry["sourceObject"]
        assert original["sourceBlobSha"] == EQUIPMENT_BLOB
        assert original["object"]["id"] == entry["id"]
        expanded.append({"originalId": "ER-ACC-" + entry["id"].removeprefix("ER-EQ-"),
                         "sourceEquipmentId": entry["id"],
                         "sourceEquipmentObjectSha256": digest(canonical(original["object"])),
                         "originalTitle": entry["title"],
                         "sourcePack": str(path.relative_to(ROOT)),
                         "originalStatus": "CHECK", "publicationStatus": "CANDIDATE",
                         "actionAuthorityGranted": False})
    expanded.sort(key=lambda x: x["originalId"])
    assert len({x["originalId"] for x in expanded}) == 111
    assert not ({x["originalId"] for x in expanded} & {x["originalId"] for x in required})

    route_ids = re.findall(r'"(ER-ROUTE-[a-z_]+)"', function)
    assert route_ids == ["ER-ROUTE-route_canonical", "ER-ROUTE-route_from_outside",
                         "ER-ROUTE-route_from_cab", "ER-ROUTE-required"]
    for token in ("fullAcceptanceSequence(requiredIds, fromOutside)",
                  "fullAcceptanceSequence(requiredIds, fromCab)",
                  "val fromOutside = routeSequence(outside + middle + cabin)",
                  "val fromCab = routeSequence(cabin + middle.asReversed() + outside.asReversed())",
                  "Если узел отсутствует на конкретном исполнении, используйте статус «Не применяется».",
                  "Она не является подтверждённой нормативной последовательностью ежедневной приёмки."):
        assert token in function
    return {"schemaVersion": 1, "donorCommit": "3176d6ee228f0ed4b78371f45209e10c1c724eff",
            "sourcePath": "app/src/main/java/ru/railbrake/calculator/core/TechnicalDataRepository.kt",
            "sourceBlobSha": DONOR_BLOB, "sourceFunctionSha256": digest(function),
            "sourceAsset": str(SOURCE.relative_to(ROOT)), "equipmentSourceBlobSha": EQUIPMENT_BLOB,
            "publicationStatus": "CANDIDATE", "runtimeImport": False,
            "currentRequirednessVerified": False, "actionAuthorityGranted": False,
            "note": "The 18 original required pairs, 111 equipment-derived check identities and four route IDs are source objects. Dynamic location ordering, execution-specific applicability and present mandatory scope are not projected or approved. Original Kotlin remains the exact source contract.",
            "requiredChecks": required, "expandedChecks": expanded,
            "routeIdsFromDonor": route_ids}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(project(), ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert OUTPUT.read_text() == encoded
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(encoded)
    print("ERMAK_ACCEPTANCE_SOURCE_PASS 18 111 4")


if __name__ == "__main__":
    main()
