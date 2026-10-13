#!/usr/bin/env python3
"""Validate pinned, non-executable CHME3 profile evidence and object map."""
import argparse
import json
from pathlib import Path

from migrate_chme3_profiles import DEST, PINS, VARIANTS, build
from map_chme3_profiles import mapping, OUTPUT


def validate(root, donor_root=None):
    index = json.loads((root / DEST).read_text())
    assert index["publicationStatus"] == "CANDIDATE"
    assert index["actionDisposition"] == "INFORMATION_ONLY"
    assert index["runtimeImport"] is False
    assert index["profileBindings"] == VARIANTS
    assert [(d["sourcePath"], d["sourceBlobSha"]) for d in index["documents"]] == list(PINS.items())
    legacy, manifest, electronic, inheritance = [d["sourceObject"] for d in index["documents"]]
    assert manifest["canonicalLayers"]["variants"] == VARIANTS
    assert {p["id"] for p in legacy["profiles"]} == set(VARIANTS)
    assert electronic["profileId"] == inheritance["profileId"] == "chme3e-electronic"
    assert "CHME3-SYS-EDB" in inheritance["hardExclusions"]
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
    print("CHME3_PROFILE_SOURCES_PASS", validate(a.root, a.donor_root))
