#!/usr/bin/env python3
"""Map all Stage-4 TEM2 document object-ledger rows to preserved destinations."""
import argparse
import hashlib
import json
from pathlib import Path

from migrate_tem2_acceptance import ROOT, SOURCE


def mapping(ledger, root):
    pack_path = ROOT / "acceptance/items-stage4.pack.json"
    route_path = ROOT / "acceptance/routes-stage4.json"
    pack = json.loads((root / pack_path).read_text())
    route = json.loads((root / route_path).read_text())
    rows = [r for r in ledger["rows"] if r["sourcePath"] == SOURCE]
    assert len(rows) == 50
    mapped = []
    for row in rows:
        pointer = row["sourcePointer"]
        if pointer.startswith(("/coreChecks/", "/profileChecks/")):
            kind, index = pointer.split("/")[1:]
            entry_index = int(index) + (14 if kind == "profileChecks" else 0)
            entry = pack["entries"][entry_index]
            assert entry["sourceObject"]["object"]["id"] == row["sourceId"]
            dest = f"{pack_path}#/entries/{entry_index}/sourceObject/object"
            canonical = entry["id"]
            node = entry["sourceObject"]["object"]
        elif pointer.startswith("/routes/"):
            index = int(pointer.split("/")[2])
            assert route["routes"][index]["sourceObject"]["id"] == row["sourceId"]
            dest = f"{route_path}#/routes/{index}/sourceObject"
            canonical = route["routes"][index]["canonicalId"]
            node = route["routes"][index]["sourceObject"]
        else:
            dest = f"{route_path}#/rootMetadata{pointer}"
            canonical = None
            node = route["rootMetadata"]
            for token in pointer.lstrip("/").split("/"):
                node = node[int(token)] if isinstance(node, list) else node[token]
        exact = json.dumps(node, sort_keys=True, ensure_ascii=False,
                           separators=(",", ":")).encode()
        assert hashlib.sha256(exact).hexdigest() == row["sha256"], pointer
        mapped.append({"sourcePath": SOURCE, "sourceBlobSha": row["sourceBlobSha"],
                       "sourcePointer": pointer, "sourceObjectSha256": row["sha256"],
                       "sourceId": row["sourceId"], "destination": dest,
                       "destinationCanonicalId": canonical, "disposition": "MIGRATED",
                       "publicationStatus": "CANDIDATE", "confidence": "PINNED_OBJECT_EQUIVALENCE"})
    assert len({x["sourcePointer"] for x in mapped}) == 50
    return {"schemaVersion": 1, "donorCommit": ledger["donorCommit"],
            "sourcePath": SOURCE, "mappedCount": 50, "rows": mapped}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--ledger", type=Path, required=True)
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--output", type=Path, default=Path("docs/data-migration/tem2-acceptance-dispositions.json"))
    p.add_argument("--verify-output", action="store_true")
    a = p.parse_args()
    result = mapping(json.loads(a.ledger.read_text()), a.root)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if a.verify_output:
        assert a.output.read_text() == rendered
    else:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(rendered)
    print("TEM2_ACCEPTANCE_DISPOSITION_PASS", result["mappedCount"])
