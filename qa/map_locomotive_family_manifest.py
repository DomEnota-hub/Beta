#!/usr/bin/env python3
"""Exact destinations for shared family manifest rows, without owner promotion."""
import argparse
import hashlib
import json
from pathlib import Path

from migrate_locomotive_family_manifest import DEST, SOURCE, SHA

OUTPUT = Path("docs/data-migration/locomotive-family-manifest-dispositions.json")


def mapping(ledger, root):
    index = json.loads((root / DEST).read_text())
    assert index["owner"] == "MIXED_REVIEW_REQUIRED" and index["runtimeImport"] is False
    rows = [r for r in ledger["rows"] if r["sourcePath"] == SOURCE]
    assert len(rows) == 12
    mapped = []
    for row in rows:
        pointer = row["sourcePointer"]
        assert row["ownerGuess"] == "MIXED_REVIEW_REQUIRED" and row["sourceBlobSha"] == SHA
        node = index["sourceObject"]
        for token in pointer.lstrip("/").split("/"):
            token = token.replace("~1", "/").replace("~0", "~")
            node = node[int(token)] if isinstance(node, list) else node[token]
        digest = hashlib.sha256(json.dumps(node, sort_keys=True, ensure_ascii=False,
                                            separators=(",", ":")).encode()).hexdigest()
        assert digest == row["sha256"]
        mapped.append({"sourcePath": SOURCE, "sourceBlobSha": SHA,
                       "sourcePointer": pointer, "sourceObjectSha256": digest,
                       "sourceId": row["sourceId"],
                       "destination": f"{DEST}#/sourceObject{pointer}",
                       "destinationCanonicalIds": [], "disposition": "MIGRATED",
                       "owner": "MIXED_REVIEW_REQUIRED", "publicationStatus": "CANDIDATE",
                       "runtimeImport": False, "confidence": "PINNED_SOURCE_PRESERVATION"})
    assert len({r["sourcePointer"] for r in mapped}) == 12
    return {"schemaVersion": 1, "donorCommit": ledger["donorCommit"],
            "mappedCount": 12, "rows": mapped}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--ledger", type=Path, required=True)
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--output", type=Path, default=OUTPUT)
    p.add_argument("--verify-output", action="store_true")
    a = p.parse_args()
    rendered = json.dumps(mapping(json.loads(a.ledger.read_text()), a.root), ensure_ascii=False, indent=2) + "\n"
    if a.verify_output:
        assert a.output.read_text() == rendered
    else:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(rendered)
    print("LOCOMOTIVE_FAMILY_MANIFEST_DISPOSITION_PASS", 12)
