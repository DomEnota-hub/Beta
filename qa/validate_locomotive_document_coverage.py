#!/usr/bin/env python3
"""Assert all locomotive JSON-document ledger rows have one exact source destination."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPS = (
    "chme3-source-registry-dispositions.json",
    "chme3-profile-dispositions.json",
    "chme3-acceptance-dispositions.json",
    "chme3-atlas-dispositions.json",
    "chme3-graph-dispositions.json",
    "chme3-diagnostic-dispositions.json",
    "chme3-remaining-document-dispositions.json",
    "tem2-acceptance-dispositions.json",
    "tem2-profile-dispositions.json",
    "tem2-source-registry-dispositions.json",
    "tem2-stage2-dispositions.json",
    "tem2-stage3-dispositions.json",
    "locomotive-family-manifest-dispositions.json",
)


def validate(root=ROOT):
    directory = root / "docs/data-migration"
    ledger = json.loads((directory / "document-object-ledger.json").read_text())
    expected = {(r["sourcePath"], r["sourcePointer"]): r for r in ledger["rows"]}
    assert len(expected) == len(ledger["rows"]) == 1748
    covered = {}
    for name in MAPS:
        data = json.loads((directory / name).read_text())
        assert data["donorCommit"] == ledger["donorCommit"]
        assert len(data["rows"]) == data["mappedCount"]
        for row in data["rows"]:
            key = (row["sourcePath"], row["sourcePointer"])
            assert key in expected and key not in covered, (name, key)
            assert row["sourceBlobSha"] == expected[key]["sourceBlobSha"]
            assert row["sourceObjectSha256"] == expected[key]["sha256"]
            covered[key] = name
    assert covered.keys() == expected.keys()
    assert sum(n.startswith("chme3-") for n in covered.values()) == 1379
    assert sum(n.startswith("tem2-") for n in covered.values()) == 357
    assert sum(n == "locomotive-family-manifest-dispositions.json" for n in covered.values()) == 12
    return len(covered)


if __name__ == "__main__":
    print("LOCOMOTIVE_DOCUMENT_COVERAGE_PASS", validate())
