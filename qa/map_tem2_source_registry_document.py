#!/usr/bin/env python3
"""Exact object-level dispositions for the pinned TEM2 source registry."""
import argparse
import hashlib
import json
from pathlib import Path

from migrate_tem2_source_registry import DEST, META, SOURCE


def mapping(ledger, root):
    pack = json.loads((root / DEST).read_text())
    meta = json.loads((root / META).read_text())
    rows = [r for r in ledger["rows"] if r["sourcePath"] == SOURCE]
    assert len(rows) == 23
    mapped = []
    for row in rows:
        pointer = row["sourcePointer"]
        if pointer.startswith("/sources/"):
            index = int(pointer.split("/")[2])
            entry = pack["entries"][index]
            node = entry["sourceObject"]["object"]
            assert node["id"] == row["sourceId"]
            destination = f"{DEST}#/entries/{index}/sourceObject/object"
            canonical = entry["id"]
        else:
            node = meta["rootMetadata"]
            for token in pointer.lstrip("/").split("/"):
                node = node[int(token)] if isinstance(node, list) else node[token]
            destination = f"{META}#/rootMetadata{pointer}"
            canonical = None
        exact = json.dumps(node, sort_keys=True, ensure_ascii=False,
                           separators=(",", ":")).encode()
        assert hashlib.sha256(exact).hexdigest() == row["sha256"], pointer
        mapped.append({"sourcePath": SOURCE, "sourceBlobSha": row["sourceBlobSha"],
                       "sourcePointer": pointer, "sourceObjectSha256": row["sha256"],
                       "sourceId": row["sourceId"], "destination": destination,
                       "destinationCanonicalId": canonical, "disposition": "MIGRATED",
                       "publicationStatus": "CANDIDATE", "confidence": "PINNED_OBJECT_EQUIVALENCE"})
    assert len({r["sourcePointer"] for r in mapped}) == 23
    return {"schemaVersion": 1, "donorCommit": ledger["donorCommit"],
            "sourcePath": SOURCE, "mappedCount": 23, "rows": mapped}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--ledger", type=Path, required=True)
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--output", type=Path,
                   default=Path("docs/data-migration/tem2-source-registry-dispositions.json"))
    p.add_argument("--verify-output", action="store_true")
    a = p.parse_args()
    result = mapping(json.loads(a.ledger.read_text()), a.root)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if a.verify_output:
        assert a.output.read_text() == rendered
    else:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(rendered)
    print("TEM2_SOURCE_REGISTRY_DISPOSITION_PASS", result["mappedCount"])
