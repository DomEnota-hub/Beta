#!/usr/bin/env python3
"""Verify exact source/destination mapping for every Stage-3 document row."""
import argparse
import hashlib
import json
from pathlib import Path

from migrate_tem2_stage3 import LINEAGE, SOURCE, SOURCES


def mapping(ledger, root):
    lineage = json.loads((root / LINEAGE).read_text())
    source_pack = json.loads((root / SOURCES).read_text())
    rows = [r for r in ledger["rows"] if r["sourcePath"] == SOURCE]
    assert len(rows) == 53
    mapped = []
    for row in rows:
        pointer = row["sourcePointer"]
        if pointer.startswith("/scenarios/"):
            index = int(pointer.split("/")[2])
            item = lineage["scenarios"][index]
            node = item["sourceObject"]
            assert node["id"] == row["sourceId"]
            destination = f"{LINEAGE}#/scenarios/{index}/sourceObject"
            canonical = [x["canonicalId"] for x in item["targets"]]
        elif pointer.startswith("/researchEvidence/"):
            index = int(pointer.split("/")[2])
            item = source_pack["entries"][index]
            node = item["sourceObject"]["object"]
            assert node["id"] == row["sourceId"]
            destination = f"{SOURCES}#/entries/{index}/sourceObject/object"
            canonical = [item["id"]]
        else:
            node = lineage["rootMetadata"]
            for token in pointer.lstrip("/").split("/"):
                node = node[int(token)] if isinstance(node, list) else node[token]
            destination = f"{LINEAGE}#/rootMetadata{pointer}"
            canonical = []
        digest = hashlib.sha256(json.dumps(node, sort_keys=True, ensure_ascii=False,
                                            separators=(",", ":")).encode()).hexdigest()
        assert digest == row["sha256"], pointer
        mapped.append({"sourcePath": SOURCE, "sourceBlobSha": row["sourceBlobSha"],
                       "sourcePointer": pointer, "sourceObjectSha256": digest,
                       "sourceId": row["sourceId"], "destination": destination,
                       "destinationCanonicalIds": canonical, "disposition": "MIGRATED",
                       "publicationStatus": "CANDIDATE", "confidence": "PINNED_OBJECT_EQUIVALENCE"})
    assert len({r["sourcePointer"] for r in mapped}) == 53
    return {"schemaVersion": 1, "donorCommit": ledger["donorCommit"],
            "sourcePath": SOURCE, "mappedCount": 53, "rows": mapped}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--ledger", type=Path, required=True)
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--output", type=Path,
                   default=Path("docs/data-migration/tem2-stage3-dispositions.json"))
    p.add_argument("--verify-output", action="store_true")
    a = p.parse_args()
    result = mapping(json.loads(a.ledger.read_text()), a.root)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if a.verify_output:
        assert a.output.read_text() == rendered
    else:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(rendered)
    print("TEM2_STAGE3_DISPOSITION_PASS", result["mappedCount"])
