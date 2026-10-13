#!/usr/bin/env python3
"""Validate closed CHME3 acceptance source documents and object mappings."""
import argparse
import json
from pathlib import Path

from migrate_chme3_acceptance_sources import DEST, PINS, build
from map_chme3_acceptance_sources import mapping, OUTPUT


def validate(root, donor_root=None):
    index = json.loads((root / DEST).read_text())
    assert index["publicationStatus"] == "CANDIDATE"
    assert index["actionDisposition"] == "INFORMATION_ONLY"
    assert index["runtimeImport"] is False
    assert [(d["sourcePath"], d["sourceBlobSha"]) for d in index["documents"]] == list(PINS.items())
    contract, required, manifest, electronic = [d["sourceObject"] for d in index["documents"]]
    assert len(required["items"]) == 21 and len(electronic["profileExtendedChecks"]) == 4
    assert len(contract["routes"]) == 7
    assert manifest["familyId"] == electronic["familyId"] == "chme3-family"
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
    print("CHME3_ACCEPTANCE_SOURCES_PASS", validate(a.root, a.donor_root))
