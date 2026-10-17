#!/usr/bin/env python3
"""Preserve pinned extended diagnostic text outside end-user runtime."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = "app/src/main/assets/technical/extended_emergency_runtime.json"
SOURCE_SHA = "24e5415a4d4ec7f2a6c0613c2adb2ab25af1b03e"
ROOT_SHA256 = "07f7627195ced273b70655d090fc4b416e8ea1552004d02c0b4dc71d82f46f16"
DESTINATIONS = {
    "chme3-family": ROOT / "content-packs/diesel/chme3-family/diagnostics/extended/source-candidates.candidate.json",
    "tem2-family": ROOT / "content-packs/diesel/tem2-family/diagnostics/extended/source-candidates.candidate.json",
}
METADATA = ROOT / "content-packs/locomotive-migration/extended-emergency-source-metadata.candidate.json"


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode()).hexdigest()


def project(source, overlay):
    assert overlay["sourcePath"] == SOURCE_PATH and overlay["sourceBlobSha"] == SOURCE_SHA
    assert (len(source["scenarioRouting"]), len(source["records"])) == (92, 77)
    assert len(overlay["rows"]) == 169
    roots = {k: v for k, v in source.items() if k not in ("scenarioRouting", "records")}
    assert digest(roots) == ROOT_SHA256
    groups = {owner: [] for owner in DESTINATIONS}
    seen = set()
    for row in overlay["rows"]:
        kind, index_text = row["sourcePointer"].strip("/").split("/")
        assert kind in ("scenarioRouting", "records") and index_text.isdecimal()
        index = int(index_text)
        key = kind, index
        assert key not in seen
        obj = source[kind][index]
        assert digest(obj) == row["sourceObjectSha256"]
        assert row["canonicalId"] is None and row["disposition"] == "DEFERRED_SCOPE"
        assert row["ownerGuess"] in groups
        groups[row["ownerGuess"]].append({
            "sourcePointer": row["sourcePointer"],
            "sourceId": row["sourceId"],
            "sourceObjectSha256": row["sourceObjectSha256"],
            "sourceObject": obj,
            "canonicalId": None,
        })
        seen.add(key)
    assert len(seen) == 169
    assert {owner: len(rows) for owner, rows in groups.items()} == {
        "chme3-family": 122, "tem2-family": 47}
    metadata = {
        "schemaVersion": 1, "donorCommit": overlay["donorCommit"],
        "sourcePath": SOURCE_PATH, "sourceBlobSha": SOURCE_SHA,
        "sourceRootSha256": ROOT_SHA256, "sourceRootWithoutRoutesAndRecords": roots,
        "publicationStatus": "CANDIDATE", "runtimeImport": False,
        "note": "Donor policy/statistics are source data; extended-mode display and action permission require separate implementation."
    }
    return groups, metadata


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("donor", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = args.donor / SOURCE_PATH
    assert subprocess.check_output(["git", "hash-object", str(path)], text=True).strip() == SOURCE_SHA
    source = json.loads(path.read_text())
    overlay = json.loads((ROOT / "docs/data-migration/extended-emergency-source-dispositions.json").read_text())
    groups, metadata = project(source, overlay)
    outputs = {METADATA: metadata}
    for owner, rows in groups.items():
        outputs[DESTINATIONS[owner]] = {
            "schemaVersion": 1, "donorCommit": overlay["donorCommit"],
            "sourcePath": SOURCE_PATH, "sourceBlobSha": SOURCE_SHA,
            "modelOwnerGuess": owner, "publicationStatus": "CANDIDATE",
            "runtimeImport": False, "requiresWarnedExtendedMode": True,
            "actionAuthorityGranted": False, "rows": rows,
        }
    for path, obj in outputs.items():
        encoded = json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n"
        if args.check:
            assert path.read_text() == encoded, path
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(encoded)
    print("EXTENDED_EMERGENCY_SOURCE_PASS", 92, 77)


if __name__ == "__main__":
    main()
