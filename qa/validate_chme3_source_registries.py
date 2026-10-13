#!/usr/bin/env python3
"""Verify distinct material IDs while preserving both original Notik records."""
import argparse
import json
from pathlib import Path

from migrate_chme3_source_registries import DEST, PINS, NOTIK, NOTIK_MATERIALS, build
from map_chme3_source_registries import mapping, OUTPUT


def validate(root, donor_root=None):
    index = json.loads((root / DEST).read_text())
    assert index["publicationStatus"] == "CANDIDATE"
    assert index["actionDisposition"] == "INFORMATION_ONLY"
    assert index["runtimeImport"] is False
    assert index["sourceIdPolicy"] == "BIBLIOGRAPHIC_ID_WITH_DISTINCT_MATERIAL_IDS"
    assert index["sourceRecordOccurrences"] == 39 and index["distinctSourceIds"] == 38
    assert [d["sourcePath"] for d in index["documents"]] == list(PINS)
    assert [d["sourceBlobSha"] for d in index["documents"]] == list(PINS.values())
    assert [d["sourceId"] for d in index["duplicateSourceIds"]] == [NOTIK]
    assert len(index["duplicateSourceIds"][0]["occurrences"]) == 2
    assert index["unresolvedDuplicateSourceIds"] == []
    identity = index["identityResolution"]
    assert identity["bibliographicSourceId"] == NOTIK
    assert identity["isbn"] == "5-277-01904-9"
    assert identity["kind"] == "TRAINING" and identity["authorityForAction"] == "NO_BY_ITSELF"
    assert [(m["sourcePath"], m["sourcePointer"], m["materialId"], m["materialRole"], m["url"])
            for m in identity["materials"]] == list(NOTIK_MATERIALS)
    assert all(m["bibliographicSourceId"] == NOTIK and m["binaryContentVerified"] is False
               for m in identity["materials"])
    assert len({m["materialId"] for m in identity["materials"]}) == 2
    for material in identity["materials"]:
        doc = next(d for d in index["documents"] if d["sourcePath"] == material["sourcePath"])
        record = doc["sourceObject"]["sources"][int(material["sourcePointer"].split("/")[-1])]
        assert record["id"] == NOTIK and record["url"] == material["url"]
    if donor_root:
        expected = json.dumps(build(donor_root), ensure_ascii=False, separators=(",", ":")) + "\n"
        assert (root / DEST).read_text() == expected
    ledger = json.loads((root / "docs/data-migration/document-object-ledger.json").read_text())
    rendered = json.dumps(mapping(ledger, root), ensure_ascii=False, indent=2) + "\n"
    assert (root / OUTPUT).read_text() == rendered
    return len(index["documents"])


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--donor-root", type=Path)
    a = p.parse_args()
    print("CHME3_SOURCE_REGISTRIES_PASS", validate(a.root, a.donor_root))
