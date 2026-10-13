#!/usr/bin/env python3
"""Assert every CHME3 JSON document ledger row has one exact source destination."""
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
)


def validate(root=ROOT):
    directory = root / "docs/data-migration"
    ledger = json.loads((directory / "document-object-ledger.json").read_text())
    expected = {(r["sourcePath"], r["sourcePointer"]): r for r in ledger["rows"]
                if r["ownerGuess"] == "chme3-family"}
    assert len(expected) == 1379
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
            assert row["publicationStatus"] == "CANDIDATE" and row["runtimeImport"] is False
            covered[key] = name
    assert covered.keys() == expected.keys()
    return len(covered)


if __name__ == "__main__":
    print("CHME3_DOCUMENT_COVERAGE_PASS", validate())
