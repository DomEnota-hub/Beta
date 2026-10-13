#!/usr/bin/env python3
"""Verify pinned, closed CHME3 documentary sources and all ledger rows."""
import argparse
import json
from pathlib import Path

from migrate_chme3_remaining_documents import DEST, PINS, build
from map_chme3_remaining_documents import mapping, OUTPUT


def validate(root, donor_root=None):
    index = json.loads((root / DEST).read_text())
    assert index["donorCommit"] == "3176d6ee228f0ed4b78371f45209e10c1c724eff"
    assert index["publicationStatus"] == "CANDIDATE"
    assert index["actionDisposition"] == "INFORMATION_ONLY"
    assert index["runtimeImport"] is False
    assert index["identityPolicy"] == "NO_CANONICAL_ID_OR_AUTHORITY_ASSIGNED"
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
    print("CHME3_REMAINING_DOCUMENTS_PASS", validate(a.root, a.donor_root))
