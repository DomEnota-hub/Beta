#!/usr/bin/env python3
"""Check exact donor provenance, graph transformation, and closed status."""
import argparse
import json
from pathlib import Path

from migrate_chme3_graph_sources import DEST, PINS, PACKS, build, normalized
from map_chme3_graph_sources import mapping, OUTPUT


def validate(root, donor_root=None):
    index = json.loads((root / DEST).read_text())
    assert index["donorCommit"] == "3176d6ee228f0ed4b78371f45209e10c1c724eff"
    assert index["publicationStatus"] == "CANDIDATE"
    assert index["actionDisposition"] == "INFORMATION_ONLY"
    assert index["runtimeImport"] is False
    assert index["relationPolicy"] == "SOURCE_GRAPH_PRESERVED_CANONICAL_GRAPH_TRANSFORM_VERIFIED"
    assert [(d["sourcePath"], d["sourceBlobSha"]) for d in index["documents"]] == list(PINS.items())
    canonical = {}
    for pack in PACKS:
        for entry in json.loads((root / pack).read_text())["entries"]:
            canonical[(pack, entry["id"])] = entry
    seen = set()
    for link in index["links"]:
        assert link["relation"] == "GRAPH_EQUALS_CANONICAL_AFTER_UNKNOWN_BRANCH_REMOVAL"
        assert link["sourceId"] not in seen
        seen.add(link["sourceId"])
        doc = next(d for d in index["documents"] if d["sourcePath"] == link["sourcePath"])
        scenario = doc["sourceObject"]["scenarios"][int(link["sourcePointer"].split("/")[-1])]
        entry = canonical[(link["canonicalPack"], link["canonicalId"])]
        assert scenario["scenarioId"] == link["sourceId"] == entry["sourceObject"]["object"]["id"]
        assert scenario["runtimeGraph"] == normalized(entry["sourceObject"]["object"]["graph"])
    assert len(seen) == len(canonical) == 68
    assert sum(len(s["runtimeGraph"]["nodes"]) for d in index["documents"] for s in d["sourceObject"]["scenarios"]) == 898
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
    print("CHME3_GRAPH_SOURCES_PASS", validate(a.root, a.donor_root))
