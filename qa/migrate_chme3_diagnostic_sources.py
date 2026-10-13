#!/usr/bin/env python3
"""Preserve CHME3 pass3 diagnostic records as closed documentary sources."""
import argparse
import hashlib
import json
from pathlib import Path

from migrate_chme3_graph_sources import PACKS

DEST = Path("content-packs/diesel/chme3-family/migration/diagnostic-source-index.json")
PINS = {
    "docs/locomotives/chme3/diagnostics_996r_detail_pass3.json": "f29c287c2eae1fb60e0cac61cab098fa8cae3c0f",
    "docs/locomotives/chme3/diagnostics_brake_aux_pass3.json": "1094688cc2e633fab21b6f989cc902f7a34d19d2",
    "docs/locomotives/chme3/diagnostics_electrical_control_pass3.json": "41d241cb0b58e5657ef0d6210e7b272d44df52d0",
    "docs/locomotives/chme3/diagnostics_extended_pass3.json": "9fa23a5c9e3da49fb025fb55245227314f6020da",
    "docs/locomotives/chme3/diagnostics_powerplant_pass3.json": "63988703bb795e82f40335a756b8b9bd3cad8e0a",
    "docs/locomotives/diesel/chme3-family/chme3e/diagnostics_stage3.json": "e6ac2baebda3a9f545a5ff1612b0b24d3c58be6e",
}


def read_pinned(root, path, sha):
    raw = (root / path).read_bytes()
    digest = lambda b: hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()
    if digest(raw) != sha and raw.endswith(b"\n"):
        raw = raw[:-1]
    assert digest(raw) == sha, path
    return json.loads(raw)


def build(donor_root, canonical_root):
    documents = [{"sourcePath": p, "sourceBlobSha": sha,
                  "sourceObject": read_pinned(donor_root, p, sha)} for p, sha in PINS.items()]
    canonical = {}
    for pack in PACKS:
        for entry in json.loads((canonical_root / pack).read_text())["entries"]:
            source_id = entry["sourceObject"]["object"]["id"]
            assert source_id not in canonical
            canonical[source_id] = (pack, entry)
    matches = []
    for doc in documents:
        for i, source in enumerate(doc["sourceObject"]["scenarios"]):
            source_id = source["id"]
            pack, entry = canonical.pop(source_id)
            assert source["title"] == entry["sourceObject"]["object"]["title"], source_id
            matches.append({"sourcePath": doc["sourcePath"], "sourcePointer": f"/scenarios/{i}",
                            "sourceId": source_id, "canonicalPack": pack, "canonicalId": entry["id"],
                            "relation": "ID_AND_TITLE_MATCH_ONLY"})
    assert not canonical and len(matches) == 68
    return {"schemaVersion": 1, "donorCommit": "3176d6ee228f0ed4b78371f45209e10c1c724eff",
            "publicationStatus": "CANDIDATE", "actionDisposition": "INFORMATION_ONLY", "runtimeImport": False,
            "relationPolicy": "ID_AND_TITLE_MATCH_DOES_NOT_CONFER_AUTHORITY_OR_FIELD_EQUIVALENCE",
            "matches": matches, "documents": documents}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--donor-root", type=Path, required=True)
    p.add_argument("--canonical-root", type=Path, default=Path("."))
    p.add_argument("--output-root", type=Path, default=Path("."))
    a = p.parse_args()
    target = a.output_root / DEST
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build(a.donor_root, a.canonical_root), ensure_ascii=False, separators=(",", ":")) + "\n")
    print("CHME3_DIAGNOSTIC_SOURCES", len(PINS), 68)
