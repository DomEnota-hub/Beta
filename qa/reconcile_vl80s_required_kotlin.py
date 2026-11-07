#!/usr/bin/env python3
"""Compare the pinned Kotlin VL80S required items with preserved source cards."""

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content-packs/locomotive-migration/source-assets/TechnicalDataRepository.kt"
PACK = ROOT / "content-packs/electric/vl80s/acceptance/required.pack.json"
JSON_SOURCE = ROOT / "content-packs/electric/vl80s/migration/acceptance-source.candidate.json"
OUT = ROOT / "content-packs/electric/vl80s/acceptance/migration/kotlin-required.candidate.json"
PIN = "26a7dfce56f6f99f43a220923a1a66096af093c1"


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def project():
    raw = SOURCE.read_bytes()
    assert hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == PIN
    text = raw.decode("utf-8")
    assert text.count("private fun loadVl80sAcceptance(): List<TechnicalEntry>") == 1
    function = text.split("private fun loadVl80sAcceptance(): List<TechnicalEntry> {", 1)[1]
    function = function.split("private fun loadVl80sElectrical()", 1)[0]
    source_pairs = function.split("requirements = listOf(", 1)[1].split("\n            )", 1)[0]
    pairs = re.findall(r'^\s*"([^"\n]+)" to "([^"\n]+)"[,]?$', source_pairs, re.M)
    assert len(pairs) == source_pairs.count('" to "') == 15
    assert 'prefix = "VL80-REQ"' in function
    assert 'VL80S_REQUIRED_ACCEPTANCE_COUNT = 15' in text
    source_label = "ВЛ80С. Руководство по эксплуатации: раздел IV «Техническое обслуживание ТО-1 электровоза локомотивными бригадами» и раздел «Приёмка электровоза в депо»"
    assert f'source = "{source_label}"' in function
    cards = json.loads(PACK.read_text())["entries"]
    assert len(cards) == 15
    rows = []
    for order, ((title, check), card) in enumerate(zip(pairs, cards), 1):
        original_id = f"VL80-REQ-{order:02}"
        assert card["id"] == original_id and card["title"] == title and card["summary"] == check
        assert card["acceptanceMeta"]["requiredBaseItem"] is True
        assert card["actionDisposition"] == "INFORMATION_ONLY"
        rows.append({"originalId": original_id, "order": order, "sourceTitle": title,
                     "sourceCheck": check, "sourceLabelFromDonor": source_label,
                     "canonicalCandidateId": card["id"],
                     "candidatePublicationStatus": card["publicationStatus"],
                     "currentRequirednessVerified": False, "actionAuthorityGranted": False})
    assert len({r["originalId"] for r in rows}) == 15
    root = json.loads(JSON_SOURCE.read_text())["sourceObject"]
    route_ids = [r["id"] for r in root["routes"]]
    assert route_ids == ["route_canonical", "route_list", "route_from_outside", "route_from_cab",
                         "route_running_gear", "route_machine_room", "route_functional"]
    assert 'id = "VL80-ROUTE-required"' in function
    assert 'sequence=fullAcceptanceSequence(requiredIds, ids)' in function
    assert 'id="VL80-ROUTE-${route.optString("id")}"' in function
    return {"schemaVersion": 1,
            "donorCommit": "3176d6ee228f0ed4b78371f45209e10c1c724eff",
            "sourcePath": "app/src/main/java/ru/railbrake/calculator/core/TechnicalDataRepository.kt",
            "sourceBlobSha": PIN, "sourceFunctionSha256": digest(function),
            "sourceAsset": str(SOURCE.relative_to(ROOT)),
            "expandedJsonSource": str(JSON_SOURCE.relative_to(ROOT)),
            "publicationStatus": "CANDIDATE", "runtimeImport": False,
            "currentRequirednessVerified": False, "actionAuthorityGranted": False,
            "note": "Exact Kotlin order, titles and checks of 15 originally required items match preserved cards. Seven expanded route IDs occur in the pinned JSON and are read by Kotlin; execution order, applicability and present-day mandatory scope are not approved by this count/text comparison.",
            "requiredChecks": rows, "expandedRouteIdsFromSource": route_ids,
            "requiredRouteIdFromKotlin": "VL80-ROUTE-required"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = project()
    encoded = json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert OUT.read_text() == encoded
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(encoded)
    print("VL80S_REQUIRED_KOTLIN_PASS 15 7")


if __name__ == "__main__":
    main()
