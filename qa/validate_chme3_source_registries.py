#!/usr/bin/env python3
"""Fail closed on ambiguous CHME3 source IDs and verify exact source snapshots."""
import argparse
import json
from pathlib import Path

from migrate_chme3_source_registries import DEST, PINS, build
from map_chme3_source_registries import mapping, OUTPUT


def validate(root, donor_root=None):
    index = json.loads((root / DEST).read_text())
    assert index["publicationStatus"] == "CANDIDATE"
    assert index["actionDisposition"] == "INFORMATION_ONLY"
    assert index["runtimeImport"] is False
    assert index["sourceIdPolicy"] == "DOCUMENT_SCOPED_UNRESOLVED"
    assert index["sourceRecordOccurrences"] == 39 and index["distinctSourceIds"] == 38
    assert [d["sourcePath"] for d in index["documents"]] == list(PINS)
    assert [d["sourceBlobSha"] for d in index["documents"]] == list(PINS.values())
    assert [d["sourceId"] for d in index["duplicateSourceIds"]] == ["CHME3-SRC-NOTIK-1996"]
    assert len(index["duplicateSourceIds"][0]["occurrences"]) == 2
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
