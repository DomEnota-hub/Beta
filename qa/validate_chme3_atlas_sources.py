#!/usr/bin/env python3
"""Validate pinned, non-executable CHME3 atlas evidence and object map."""
import argparse
import json
from pathlib import Path

from migrate_chme3_atlas_sources import DEST, PINS, build
from map_chme3_atlas_sources import mapping, OUTPUT


def validate(root, donor_root=None):
    index = json.loads((root / DEST).read_text())
    assert index["publicationStatus"] == "CANDIDATE"
    assert index["actionDisposition"] == "INFORMATION_ONLY"
    assert index["runtimeImport"] is False
    assert index["pairPolicy"] == "INDEX_AND_CARD_RETAINED_SEPARATELY"
    assert len(index["pairedRecords"]) == 103
    assert all(len(p["occurrences"]) == 2 and
               {o["role"] for o in p["occurrences"]} == {"CARD", "INDEX"}
               for p in index["pairedRecords"])
    assert sum(p["nameComparison"] == "MISSING_CARD_NAME" for p in index["pairedRecords"]) == 33
    assert [p["sourceId"] for p in index["pairedRecords"]
            if p["nameComparison"] == "DIFFERENT_NAMES"] == ["CHME3T-EQ-BRAKE-RESISTORS"]
    assert [(d["sourcePath"], d["sourceBlobSha"]) for d in index["documents"]] == list(PINS.items())
    if donor_root:
        expected = json.dumps(build(donor_root), ensure_ascii=False, separators=(",", ":")) + "\n"
        assert (root / DEST).read_text() == expected
    ledger = json.loads((root / "docs/data-migration/document-object-ledger.json").read_text())
    assert (root / OUTPUT).read_text() == json.dumps(mapping(ledger, root), ensure_ascii=False, indent=2) + "\n"
    return len(index["documents"])


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--donor-root", type=Path)
    a = p.parse_args()
    print("CHME3_ATLAS_SOURCES_PASS", validate(a.root, a.donor_root))
