#!/usr/bin/env python3
"""Pinned, lossless data import of four Ermak technical object arrays.

The donor gz assets are read only. The canonical packs retain every source
object as a structured snapshot while keeping all entries unpublishable.
"""
import base64
import gzip
import hashlib
import json
from pathlib import Path

DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
ASSETS = {
    "equipment": ("records", "EQUIPMENT", "47a8d2424d69943fba9747746aa6ad8c8f4e2e98"),
    "knowledge": ("articles", "KNOWLEDGE", "08d164fc11c33c241d04ad6ad60c13a3aec996c8"),
    "diagnostics": ("scenarios", "DIAGNOSTIC_SCENARIO", "c3a22c62db42308eb4b7ee44ff2da02f47686625"),
    "schemes": ("schemes", "ATLAS_SCHEME", "33b1f6016308aa13897fdd97d726bccf3e06dcb5"),
}
BASE = Path("content-packs/electric/ermak")


def read_asset(name, donor_dir):
    group, kind, sha = ASSETS[name]
    raw = base64.b64decode((donor_dir / f"ermak_{name}.json.gz.b64").read_text())
    actual = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    assert actual == sha, (name, actual)
    data = json.loads(gzip.decompress(raw))
    records = data[group]
    assert len(records) == len({r["id"] for r in records})
    return records


def typed_links(record, known_ids):
    specs = (("equipmentRefs", "EQUIPMENT"),
             ("knowledgeRefs", "KNOWLEDGE"),
             ("relatedScenarioIds", "RELATED_SCENARIO"))
    links = []
    for field, link_type in specs:
        for target in record.get(field, []):
            if isinstance(target, str) and target in known_ids:
                links.append({"type": link_type, "targetId": target, "role": field})
    for relation in record.get("relations", []):
        target = relation.get("targetId")
        if target in known_ids:
            links.append({"type": "EQUIPMENT", "targetId": target,
                          "role": str(relation.get("type") or "relation")})
    return links


def entry(name, kind, sha, record, known_ids):
    identifier = record["id"]
    title = record.get("name") or record.get("title") or identifier
    refs = sorted({r["sourceId"] if isinstance(r, dict) else r
                   for r in record.get("sourceRefs", []) if isinstance(r, (dict, str))})
    summary = record.get("purpose") or record.get("summary") or record.get("symptom")
    if isinstance(summary, dict):
        summary = None
    source = f"app/src/main/assets/technical/ermak_{name}.json.gz"
    return {
        "id": identifier,
        "type": kind,
        "owner": {"kind": "MODEL", "modelId": "ermak"},
        "applicability": {"modelIds": ["ermak"]},
        "layer": "STANDARD",
        "publicationStatus": "CANDIDATE",
        "provenance": "UNKNOWN",
        "sourceStatus": "UNKNOWN",
        "actionDisposition": "INFORMATION_ONLY",
        "title": title,
        "summary": summary,
        "searchTerms": [str(v) for v in [record.get("slug"), *record.get("aliases", [])] if v],
        "sourceRefs": refs,
        "links": typed_links(record, known_ids),
        "sourceObject": {"sourcePath": source, "sourceBlobSha": sha, "object": record},
    }


def build(donor_dir):
    outputs = {}
    records_by_group = {name: read_asset(name, donor_dir) for name in ASSETS}
    known_ids = {record["id"] for records in records_by_group.values() for record in records}
    assert len(known_ids) == sum(len(records) for records in records_by_group.values())
    for name, (group, kind, sha) in ASSETS.items():
        records = records_by_group[name]
        for offset in range(0, len(records), 20):
            number = offset // 20 + 1
            entries = [entry(name, kind, sha, record, known_ids)
                       for record in records[offset:offset+20]]
            assert len(entries) == len({e["id"] for e in entries})
            pack = {
                "manifest": {
                    "schemaVersion": 1,
                    "packId": f"ermak.{name}.{number:02d}",
                    "packVersion": "0.1.0",
                    "family": "ELECTRIC",
                    "modelIds": ["ermak"],
                    "variantIds": [],
                    "locale": "ru-RU",
                    "entries": [e["id"] for e in entries],
                    "requiresRuntime": "1.1.0",
                    "sourceCatalogVersion": f"test-{DONOR[:8]}-ermak-{name}",
                    "checksums": {f"ermak_{name}.json.gz.gitBlob": sha},
                },
                "entries": entries,
            }
            subdir = {"equipment": "atlas/equipment", "knowledge": "technical-data/knowledge",
                      "diagnostics": "diagnostics/recommended", "schemes": "atlas/schemes"}[name]
            path = BASE / subdir / f"{name}-{number:02d}.pack.json"
            outputs[path] = json.dumps(pack, ensure_ascii=False, separators=(",", ":")) + "\n"
    return outputs


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--donor-dir", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=Path("."))
    args = parser.parse_args()
    outputs = build(args.donor_dir)
    for path, content in outputs.items():
        target = args.output_root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    print("ERMAK_STRUCTURED_PACKS", len(outputs), sum(len(json.loads(v)["entries"]) for v in outputs.values()))


if __name__ == "__main__":
    main()
