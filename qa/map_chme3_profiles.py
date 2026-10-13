#!/usr/bin/env python3
"""Exact object destinations for the four CHME3 profile/family documents."""
import argparse
import hashlib
import json
from pathlib import Path

from migrate_chme3_profiles import DEST, PINS

OUTPUT = Path("docs/data-migration/chme3-profile-dispositions.json")


def mapping(ledger, root):
    index = json.loads((root / DEST).read_text())
    assert index["runtimeImport"] is False and index["publicationStatus"] == "CANDIDATE"
    doc_indices = {d["sourcePath"]: i for i, d in enumerate(index["documents"])}
    assert set(doc_indices) == set(PINS)
    rows = [r for r in ledger["rows"] if r["sourcePath"] in PINS]
    assert len(rows) == 153
    mapped = []
    for row in rows:
        path, pointer = row["sourcePath"], row["sourcePointer"]
        i = doc_indices[path]
        assert row["sourceBlobSha"] == PINS[path]
        node = index["documents"][i]["sourceObject"]
        for token in pointer.lstrip("/").split("/"):
            token = token.replace("~1", "/").replace("~0", "~")
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
    assert len({(r["sourcePath"], r["sourcePointer"]) for r in mapped}) == 153
    return {"schemaVersion": 1, "donorCommit": ledger["donorCommit"],
            "mappedCount": 153, "rows": mapped}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--ledger", type=Path, required=True)
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--output", type=Path, default=OUTPUT)
    p.add_argument("--verify-output", action="store_true")
    a = p.parse_args()
    result = mapping(json.loads(a.ledger.read_text()), a.root)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if a.verify_output:
        assert a.output.read_text() == rendered
    else:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(rendered)
    print("CHME3_PROFILE_DISPOSITION_PASS", result["mappedCount"])
