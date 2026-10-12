#!/usr/bin/env python3
"""Exact object dispositions for the four TEM2 profile/family documents."""
import argparse
import hashlib
import json
from pathlib import Path

from migrate_tem2_profiles import DEST, PINS


def mapping(ledger, root):
    index = json.loads((root / DEST).read_text())
    document_index = {d["sourcePath"]: i for i, d in enumerate(index["documents"])}
    assert set(document_index) == set(PINS)
    rows = [r for r in ledger["rows"] if r["sourcePath"] in PINS]
    assert len(rows) == 137
    mapped = []
    for row in rows:
        path = row["sourcePath"]
        i = document_index[path]
        pointer = row["sourcePointer"]
        node = index["documents"][i]["sourceObject"]
        for token in pointer.lstrip("/").split("/"):
            node = node[int(token)] if isinstance(node, list) else node[token]
        digest = hashlib.sha256(json.dumps(node, sort_keys=True, ensure_ascii=False,
                                            separators=(",", ":")).encode()).hexdigest()
        assert digest == row["sha256"], (path, pointer)
        mapped.append({"sourcePath": path, "sourceBlobSha": row["sourceBlobSha"],
                       "sourcePointer": pointer, "sourceObjectSha256": digest,
                       "sourceId": row["sourceId"],
                       "destination": f"{DEST}#/documents/{i}/sourceObject{pointer}",
                       "destinationCanonicalIds": [], "disposition": "MIGRATED",
                       "publicationStatus": "CANDIDATE", "runtimeImport": False,
                       "confidence": "PINNED_SOURCE_PRESERVATION"})
    assert len({(r["sourcePath"], r["sourcePointer"]) for r in mapped}) == 137
    return {"schemaVersion": 1, "donorCommit": ledger["donorCommit"],
            "mappedCount": 137, "rows": mapped}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--ledger", type=Path, required=True)
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--output", type=Path,
                   default=Path("docs/data-migration/tem2-profile-dispositions.json"))
    p.add_argument("--verify-output", action="store_true")
    a = p.parse_args()
    result = mapping(json.loads(a.ledger.read_text()), a.root)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if a.verify_output:
        assert a.output.read_text() == rendered
    else:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(rendered)
    print("TEM2_PROFILE_DISPOSITION_PASS", result["mappedCount"])
