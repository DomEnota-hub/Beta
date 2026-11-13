#!/usr/bin/env python3
"""Locate CHME3 raw link targets in preserved documents without publishing edges."""

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "content-packs/diesel/chme3-family/migration"
AUDIT = BASE / "source-audit.json"
OUTPUT = BASE / "raw-target-evidence.candidate.json"
DOCUMENTS = (BASE / "remaining-document-source-index.json",
             BASE / "atlas-source-index.json")
NAMES = {"chme3": "ЧМЭ3", "chme3t": "ЧМЭ3Т", "chme3e": "ЧМЭ3Э"}


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def target_objects(document, file, wanted):
    found = defaultdict(list)

    def walk(value, pointer):
        if isinstance(value, dict):
            if value.get("id") in wanted:
                found[value["id"]].append({
                    "evidencePath": file.relative_to(ROOT).as_posix() + "#" + pointer,
                    "sourceObjectSha256": canonical_hash(value),
                    "applicability": value.get("applicability", []),
                    "objectFields": list(value),
                })
            for key, child in value.items():
                walk(child, pointer + "/" + key.replace("~", "~0").replace("/", "~1"))
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, pointer + "/" + str(index))

    walk(document, "")
    return found


def project():
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    raw = audit["unresolvedReferences"]
    assert len(raw) == 610
    wanted = {row["sourceTargetId"] for row in raw}
    assert len(wanted) == 19
    targets = defaultdict(list)
    for file in DOCUMENTS:
        found = target_objects(json.loads(file.read_text(encoding="utf-8")), file, wanted)
        for key, values in found.items():
            targets[key].extend(values)
    assert set(targets) == wanted
    assert {key: len(values) for key, values in targets.items() if len(values) > 1} == {
        "CHME3T-EQ-EDB-CONTROL": 2,
    }
    grouped = {}
    conflicts = []
    counts = Counter()
    for row in raw:
        key = row["sourceTargetId"]
        variant = row["variant"]
        evidence = targets[key]
        compatible = any(NAMES[variant] in item["applicability"] for item in evidence)
        state = "TARGET_PRESERVED_VARIANT_COMPATIBLE" if compatible else "CROSS_VARIANT_TARGET_NOT_LINKED"
        counts[state] += 1
        group = grouped.setdefault((row["source"], variant), [])
        group.append(key)
        if not compatible:
            conflicts.append({"sourceEntryId": row["source"], "sourceVariant": variant,
                              "rawTargetId": key, "runtimeLinkCreated": False})
    assert counts == {"TARGET_PRESERVED_VARIANT_COMPATIBLE": 602,
                      "CROSS_VARIANT_TARGET_NOT_LINKED": 8}
    return {"schemaVersion": 1, "donorCommit": audit["donorCommit"],
            "publicationStatus": "CANDIDATE", "runtimeImport": False,
            "interpretation": "Targets exist in original documentary snapshots; compatible source provenance is not a proven canonical runtime edge or action authority. Eight variant conflicts remain unresolved.",
            "counts": dict(counts), "uniqueTargetCount": len(wanted),
            "targets": dict(sorted(targets.items())),
            "sourceGroups": [{"sourceEntryId": source, "sourceVariant": variant,
                              "rawTargetIds": keys} for (source, variant), keys in grouped.items()],
            "crossVariantConflicts": conflicts}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(project(), ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert OUTPUT.read_text(encoding="utf-8") == encoded
    else:
        OUTPUT.write_text(encoded, encoding="utf-8")
    print("CHME3_RAW_TARGET_EVIDENCE_PASS 610 19 602 8")


if __name__ == "__main__":
    main()
