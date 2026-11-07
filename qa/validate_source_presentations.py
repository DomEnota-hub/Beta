#!/usr/bin/env python3
"""Check the 57 model-owned display labels against the pinned source ledger."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = json.loads((ROOT / "docs/data-migration/source-presentation-dispositions.json").read_text())
PATHS = {
    "chme3-family": "content-packs/diesel/chme3-family/migration/source-presentations.candidate.json",
    "ermak": "content-packs/electric/ermak/migration/source-presentations.candidate.json",
    "tem2-family": "content-packs/diesel/tem2-family/migration/source-presentations.candidate.json",
}


def object_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode()).hexdigest()


expected = {r["rawSourceId"]: r for r in OVERLAY["rows"]}
assert len(expected) == 57
seen = set()
for owner, rel in PATHS.items():
    inventory = json.loads((ROOT / rel).read_text())
    assert inventory["recordKind"] == "SOURCE_PRESENTATION_DISPLAY_LABEL"
    assert inventory["modelOwnerGuess"] == owner
    assert inventory["sourcePath"] == OVERLAY["sourcePath"]
    assert inventory["sourceBlobSha"] == OVERLAY["sourceBlobSha"]
    assert inventory["donorCommit"] == OVERLAY["donorCommit"]
    assert inventory["publicationStatus"] == "CANDIDATE"
    assert inventory["runtimeImport"] is False and inventory["sourceIdentityResolved"] is False
    for row in inventory["rows"]:
        raw_id = row["rawSourceId"]
        assert raw_id not in seen and raw_id in expected, raw_id
        source = expected[raw_id]
        assert source["ownerGuess"] == owner
        assert row["sourcePointer"] == source["sourcePointer"]
        assert row["sourceObject"] == source["sourceObject"]
        assert row["sourceObjectSha256"] == source["sourceObjectSha256"] == object_hash(row["sourceObject"])
        assert row["canonicalSourceId"] is None
        seen.add(raw_id)
    assert len(inventory["rows"]) == {"chme3-family": 38, "ermak": 7, "tem2-family": 12}[owner]
assert seen == set(expected)
for runtime_index in (ROOT / "content-packs").rglob("runtime-index.json"):
    assert not any(rel in runtime_index.read_text() for rel in PATHS.values()), runtime_index
print("SOURCE_PRESENTATIONS_PASS", len(seen))
