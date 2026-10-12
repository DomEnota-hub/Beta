#!/usr/bin/env python3
"""Verify pinned, non-executable TEM2 family/profile source contracts."""
import argparse
import hashlib
import json
from pathlib import Path

from migrate_tem2_profiles import DEST, PINS, VARIANTS, build

SHA = "df5aaf7bc404896cada594afd164b60aea159112e52bae230c00d769feaa3cd6"


def validate(root, donor_root=None):
    assert hashlib.sha256((root / DEST).read_bytes()).hexdigest() == SHA
    index = json.loads((root / DEST).read_text())
    assert index["publicationStatus"] == "CANDIDATE"
    assert index["actionDisposition"] == "INFORMATION_ONLY"
    assert index["runtimeImport"] is False
    assert index["profileBindings"] == VARIANTS
    assert [(d["sourcePath"], d["sourceBlobSha"]) for d in index["documents"]] == list(PINS.items())
    manifest, contract, tem2, tem2u = [d["sourceObject"] for d in index["documents"]]
    assert manifest["canonicalLayers"]["variants"] == VARIANTS
    assert contract["integrationDefaults"]["failClosedOnUnknownExecution"] is True
    assert tem2["profileId"] == "tem2-base" and tem2u["profileId"] == "tem2u-improved"
    if donor_root:
        expected = json.dumps(build(donor_root), ensure_ascii=False,
                              separators=(",", ":")) + "\n"
        assert (root / DEST).read_text() == expected
    return len(index["documents"])


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--donor-root", type=Path)
    a = p.parse_args()
    print("TEM2_PROFILE_SOURCES_PASS", validate(a.root, a.donor_root))
