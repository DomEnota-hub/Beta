#!/usr/bin/env python3
"""Preserve shared donor source labels in model-owned, non-runtime inventories."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = "app/src/main/assets/technical/source_presentations.json"
SOURCE_SHA = "6dde42099f5c6e9f1226212ae5e42c6a04fde00c"
DONOR_COMMIT = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
DESTINATIONS = {
    "chme3-family": "content-packs/diesel/chme3-family/migration/source-presentations.candidate.json",
    "ermak": "content-packs/electric/ermak/migration/source-presentations.candidate.json",
    "tem2-family": "content-packs/diesel/tem2-family/migration/source-presentations.candidate.json",
}


def object_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("donor", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    source_file = args.donor / SOURCE_PATH
    actual_sha = subprocess.check_output(["git", "hash-object", str(source_file)], text=True).strip()
    assert actual_sha == SOURCE_SHA, actual_sha
    source = json.loads(source_file.read_text())
    overlay = json.loads((ROOT / "docs/data-migration/source-presentation-dispositions.json").read_text())
    assert overlay["sourcePath"] == SOURCE_PATH and overlay["sourceBlobSha"] == SOURCE_SHA
    assert len(source["sources"]) == len(overlay["rows"]) == 57
    groups = {owner: [] for owner in DESTINATIONS}
    accounted = set()
    for row in overlay["rows"]:
        raw_id = row["rawSourceId"]
        assert raw_id not in accounted and row["sourcePointer"] == "/sources/" + raw_id
        obj = source["sources"][raw_id]
        assert set(obj) == {"title", "detail"}
        assert obj == row["sourceObject"] and object_hash(obj) == row["sourceObjectSha256"]
        assert row["canonicalSourceId"] is None and row["disposition"] == "DEFERRED_SCOPE"
        assert row["ownerGuess"] in groups
        groups[row["ownerGuess"]].append({
            "rawSourceId": raw_id,
            "sourcePointer": row["sourcePointer"],
            "sourceObjectSha256": row["sourceObjectSha256"],
            "sourceObject": obj,
            "canonicalSourceId": None,
        })
        accounted.add(raw_id)
    assert accounted == set(source["sources"])
    assert {owner: len(rows) for owner, rows in groups.items()} == {
        "chme3-family": 38, "ermak": 7, "tem2-family": 12}
    for owner, rel in DESTINATIONS.items():
        path = ROOT / rel
        inventory = {
            "schemaVersion": 1,
            "recordKind": "SOURCE_PRESENTATION_DISPLAY_LABEL",
            "modelOwnerGuess": owner,
            "donorCommit": DONOR_COMMIT,
            "sourcePath": SOURCE_PATH,
            "sourceBlobSha": SOURCE_SHA,
            "publicationStatus": "CANDIDATE",
            "runtimeImport": False,
            "sourceIdentityResolved": False,
            "rows": groups[owner],
        }
        encoded = json.dumps(inventory, ensure_ascii=False, indent=2) + "\n"
        if args.check:
            assert path.read_text() == encoded, path
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(encoded)
        print(owner, len(groups[owner]), rel)


if __name__ == "__main__":
    main()
