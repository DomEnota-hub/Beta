#!/usr/bin/env python3
"""Preserve every Kotlin normal-parameter field, including omitted confidence."""

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content-packs/electric/vl80s/technical-data/migration/source-assets/Vl80sNormalValues.kt"
PACK = ROOT / "content-packs/electric/vl80s/technical-data/normal-values.pack.json"
OUT = ROOT / "content-packs/electric/vl80s/technical-data/migration/kotlin-normal-values.candidate.json"
PIN = "9aacbb1982e0143d6efc40e3579c47c63074b176"
PATTERN = re.compile(
    r'^\s*NormalParameter\(\s*"([^"\n]+)",\s*"([^"\n]+)",\s*"([^"\n]+)",\s*'
    r'"([^"\n]+)",\s*setOf\(([^)]*)\),\s*InformationConfidence\.([A-Z_]+),\s*'
    r'"([^"\n]+)"\s*\)', re.M)


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def project():
    raw = SOURCE.read_bytes()
    assert hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == PIN
    text = raw.decode("utf-8")
    matches = list(PATTERN.finditer(text))
    assert len(matches) == text.count("        NormalParameter(") == 6
    entries = json.loads(PACK.read_text())["entries"]
    by_alias = {e["aliases"][0]: e for e in entries}
    assert len(by_alias) == len(entries) == 6
    rows = []
    for m in matches:
        key, title, normal, applicability, equipment, confidence, source = m.groups()
        ids = re.findall(r'"([^"\n]+)"', equipment)
        assert equipment.strip() == ", ".join(json.dumps(v, ensure_ascii=False) for v in ids)
        entry = by_alias[key]
        assert entry["title"] == title and entry["summary"] == normal
        assert entry["blocks"] == [{"title": "Применимость", "lines": [applicability]},
                                   {"title": "Источник", "lines": [source]}]
        assert entry["migrationRefs"] == {"sourceFile": SOURCE.name, "sourceId": key,
                                           "sourceBlobSha": PIN}
        assert entry["actionDisposition"] == "INFORMATION_ONLY"
        rows.append({"sourceId": key, "candidateId": entry["id"],
                     "sourceFragmentSha256": digest(m.group(0)),
                     "sourceConfidence": confidence, "sourceEquipmentIds": ids,
                     "sourceTitle": title, "sourceNormalValue": normal,
                     "sourceApplicability": applicability, "sourceCitation": source,
                     "candidatePublicationStatus": entry["publicationStatus"],
                     "currentAuthorityVerified": False})
    assert {r["sourceId"] for r in rows} == set(by_alias)
    return {"schemaVersion": 1,
            "donorCommit": "3176d6ee228f0ed4b78371f45209e10c1c724eff",
            "sourcePath": "app/src/main/java/ru/railbrake/calculator/core/Vl80sNormalValues.kt",
            "sourceBlobSha": PIN, "sourceAsset": str(SOURCE.relative_to(ROOT)),
            "publicationStatus": "CANDIDATE", "runtimeImport": False,
            "currentAuthorityVerified": False, "actionAuthorityGranted": False,
            "note": "Exact six source values and original InformationConfidence labels. The existing card text is equal, but those confidence labels and original equipment aliases were not represented in the normal-values cards. The donor confidence label does not verify present source authority or permissible action; existing pack publication status is recorded, not changed here.",
            "rows": rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(project(), ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert OUT.read_text() == encoded
    else:
        OUT.write_text(encoded)
    print("VL80S_NORMAL_VALUES_SOURCE_PASS 6")


if __name__ == "__main__":
    main()
