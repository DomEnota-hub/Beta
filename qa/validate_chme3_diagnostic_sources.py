#!/usr/bin/env python3
"""Verify closed status and ID/title-only matching for diagnostic records."""
import argparse
import json
from pathlib import Path

from migrate_chme3_diagnostic_sources import DEST, PINS, PACKS, build
from map_chme3_diagnostic_sources import mapping, OUTPUT


def validate(root, donor_root=None):
    index = json.loads((root / DEST).read_text())
    assert index["donorCommit"] == "3176d6ee228f0ed4b78371f45209e10c1c724eff"
    assert index["publicationStatus"] == "CANDIDATE"
    assert index["actionDisposition"] == "INFORMATION_ONLY"
    assert index["runtimeImport"] is False
    assert index["relationPolicy"] == "ID_AND_TITLE_MATCH_DOES_NOT_CONFER_AUTHORITY_OR_FIELD_EQUIVALENCE"
    assert [(d["sourcePath"], d["sourceBlobSha"]) for d in index["documents"]] == list(PINS.items())
    canonical = {}
    for pack in PACKS:
        for entry in json.loads((root / pack).read_text())["entries"]:
            canonical[(pack, entry["id"])] = entry
    seen = set()
    for match in index["matches"]:
        assert match["relation"] == "ID_AND_TITLE_MATCH_ONLY"
        assert match["sourceId"] not in seen
        seen.add(match["sourceId"])
        doc = next(d for d in index["documents"] if d["sourcePath"] == match["sourcePath"])
        source = doc["sourceObject"]["scenarios"][int(match["sourcePointer"].split("/")[-1])]
        entry = canonical[(match["canonicalPack"], match["canonicalId"])]
        assert source["id"] == match["sourceId"] == entry["sourceObject"]["object"]["id"]
        assert source["title"] == entry["sourceObject"]["object"]["title"]
    assert len(seen) == len(canonical) == 68
    if donor_root:
        expected = json.dumps(build(donor_root, root), ensure_ascii=False, separators=(",", ":")) + "\n"
        assert (root / DEST).read_text() == expected
    ledger = json.loads((root / "docs/data-migration/document-object-ledger.json").read_text())
    assert (root / OUTPUT).read_text() == json.dumps(mapping(ledger, root), ensure_ascii=False, indent=2) + "\n"
    return len(index["documents"])


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--donor-root", type=Path)
    a = p.parse_args()
    print("CHME3_DIAGNOSTIC_SOURCES_PASS", validate(a.root, a.donor_root))
