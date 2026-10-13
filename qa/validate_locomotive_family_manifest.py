#!/usr/bin/env python3
"""Check pinned shared manifest and its closed mixed-owner disposition."""
import argparse
import json
from pathlib import Path

from migrate_locomotive_family_manifest import DEST, SOURCE, SHA, build
from map_locomotive_family_manifest import OUTPUT, mapping


def validate(root, donor_root=None):
    index = json.loads((root / DEST).read_text())
    assert index["sourcePath"] == SOURCE and index["sourceBlobSha"] == SHA
    assert index["donorCommit"] == "3176d6ee228f0ed4b78371f45209e10c1c724eff"
    assert index["owner"] == "MIXED_REVIEW_REQUIRED"
    assert index["publicationStatus"] == "CANDIDATE"
    assert index["actionDisposition"] == "INFORMATION_ONLY"
    assert index["runtimeImport"] is False
    assert {f["familyId"] for f in index["sourceObject"]["families"]} == {"chme3-family", "tem2-family"}
    if donor_root:
        expected = json.dumps(build(donor_root), ensure_ascii=False, separators=(",", ":")) + "\n"
        assert (root / DEST).read_text() == expected
    ledger = json.loads((root / "docs/data-migration/document-object-ledger.json").read_text())
    assert (root / OUTPUT).read_text() == json.dumps(mapping(ledger, root), ensure_ascii=False, indent=2) + "\n"
    return 12


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--donor-root", type=Path)
    a = p.parse_args()
    print("LOCOMOTIVE_FAMILY_MANIFEST_PASS", validate(a.root, a.donor_root))
