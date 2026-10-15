#!/usr/bin/env python3
"""Relate two historical acceptance audits to exact preserved item identities."""

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "content-packs/locomotive-migration/migration/historical-documents.candidate.json"
ERMAK = ROOT / "content-packs/electric/ermak/acceptance/migration/kotlin-source.candidate.json"
VL80S = ROOT / "content-packs/electric/vl80s/acceptance"
OUT = ROOT / "docs/data-migration/historical-acceptance-audit-relations.json"
PATHS = ("docs/acceptance-audit-beta48.md", "docs/acceptance-audit-beta50.md")


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def project():
    archive = json.loads(HISTORY.read_text())
    sources = {d["sourcePath"]: d for d in archive["documents"]}
    assert all(path in sources for path in PATHS)
    ermak = json.loads(ERMAK.read_text())
    required = json.loads((VL80S / "required.pack.json").read_text())["entries"]
    expanded = json.loads((VL80S / "items.pack.json").read_text())["entries"]
    assert len(required) == 15 and len(expanded) == 66
    assert len(ermak["requiredChecks"]) == 18 and len(ermak["expandedChecks"]) == 111
    assert len({x["id"] for x in required + expanded}) == 81
    assert len({x["originalId"] for x in ermak["requiredChecks"] + ermak["expandedChecks"]}) == 129
    assert all(x["acceptanceMeta"]["requiredBaseItem"] for x in required)
    assert all(x["acceptanceMeta"].get("requiredBaseItem") is not True for x in expanded)
    assert all(not x["currentRequirednessVerified"] and not x["actionAuthorityGranted"]
               for x in ermak["requiredChecks"])
    assert not ermak["runtimeImport"] and not ermak["currentRequirednessVerified"]

    relations = []
    for path in PATHS:
        source = sources[path]
        text = source["exactSourceText"]
        vl80_section = text.split("## ВЛ80С\n", 1)[1].split("\n## ", 1)[0]
        ermak_section = text.split('## 2ЭС5К / 3ЭС5К «Ермак»\n', 1)[1].split("\n## ", 1)[0]
        for fragment in ("15 ", "66 "):
            assert fragment in vl80_section, (path, fragment)
        for fragment in ("18 ", "111 "):
            if fragment == "111 " and path.endswith("beta48.md"):
                # Beta48 calls these generated equipment cards without a numeric claim.
                continue
            assert fragment in ermak_section, (path, fragment)
        assert "ЦТ/3549" in vl80_section and "ЦТ-533" in ermak_section
        assert "Не применяется" in ermak_section
        relations.append({"sourcePath": path, "sourceBlobSha": source["sourceBlobSha"],
                          "sourceTextSha256": digest(text),
                          "historicalVl80sSectionSha256": digest(vl80_section),
                          "historicalErmakSectionSha256": digest(ermak_section),
                          "claimRelation": "HISTORICAL_COUNT_AND_MODE_CROSS_REFERENCE",
                          "presentRequirednessVerified": False})
    return {"schemaVersion": 1, "donorCommit": archive["donorCommit"],
            "publicationStatus": "CANDIDATE", "runtimeImport": False,
            "currentRequirednessVerified": False, "actionAuthorityGranted": False,
            "note": "The audit counts and source-mode separation are related to preserved item IDs. This does not establish current requiredness, exact source-to-item procedural parity, approved execution order, or authority of CT/3549 and CT-533.",
            "audits": relations,
            "preservedItemSets": [
                {"modelId": "vl80s", "requiredSourcePack": "content-packs/electric/vl80s/acceptance/required.pack.json",
                 "requiredIds": [x["id"] for x in required],
                 "expandedSourcePack": "content-packs/electric/vl80s/acceptance/items.pack.json",
                 "expandedIds": [x["id"] for x in expanded],
                 "relationship": "COUNT_AND_DISTINCT_ID_PARITY_ONLY"},
                {"modelId": "ermak", "sourceCandidate": str(ERMAK.relative_to(ROOT)),
                 "requiredIds": [x["originalId"] for x in ermak["requiredChecks"]],
                 "expandedIds": [x["originalId"] for x in ermak["expandedChecks"]],
                 "relationship": "KOTLIN_SOURCE_ITEM_IDENTITY"}]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = project()
    encoded = json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert OUT.read_text() == encoded
    else:
        OUT.write_text(encoded)
    print("HISTORICAL_ACCEPTANCE_AUDIT_PASS 2 15 66 18 111")


if __name__ == "__main__":
    main()
