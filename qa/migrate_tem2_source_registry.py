#!/usr/bin/env python3
"""Preserve TEM2/TEM2U source-registry records as unpublished source entries."""
import hashlib
import json
from pathlib import Path

SOURCE = "docs/locomotives/diesel/tem2-family/common/source_registry.json"
BLOB = "160a2531a67bdb1c6fff1fb532fc3df6044d67a6"
DEST = Path("content-packs/diesel/tem2-family/sources/registry.pack.json")
META = Path("content-packs/diesel/tem2-family/sources/registry-metadata.json")


def source(donor_root):
    raw = (donor_root / SOURCE).read_bytes()
    digest = lambda b: hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()
    if digest(raw) != BLOB and raw.endswith(b"\n"):
        raw = raw[:-1]
    assert digest(raw) == BLOB
    return json.loads(raw)


def variants(record):
    labels = set(record["applicability"])
    selected = []
    if "ТЭМ2" in labels or "LOCOMOTIVES_GENERAL" in labels or "LOCOMOTIVES_RZD_MAINTENANCE" in labels:
        selected.append("tem2")
    if "ТЭМ2У" in labels or "LOCOMOTIVES_GENERAL" in labels or "LOCOMOTIVES_RZD_MAINTENANCE" in labels:
        selected.append("tem2u")
    assert selected
    return selected


def build(donor_root):
    doc = source(donor_root)
    entries = []
    for record in doc["sources"]:
        entries.append({"id": "tem2.source." + record["id"].lower(), "type": "SOURCE",
                        "owner": {"kind": "MODEL", "modelId": "tem2-family"},
                        "applicability": {"modelIds": ["tem2-family"],
                                          "variantIds": variants(record)},
                        "layer": "STANDARD", "publicationStatus": "CANDIDATE",
                        "provenance": "UNKNOWN", "sourceStatus": "UNKNOWN",
                        "actionDisposition": "INFORMATION_ONLY", "title": record["title"],
                        "summary": record.get("purpose", ""), "sourceRefs": [], "links": [],
                        "sourceObject": {"sourcePath": SOURCE, "sourceBlobSha": BLOB,
                                         "object": record}})
    manifest = {"schemaVersion": 1, "packId": "tem2-family.sources.registry",
                "packVersion": "0.1.0", "family": "DIESEL", "modelIds": ["tem2-family"],
                "variantIds": ["tem2", "tem2u"], "locale": "ru-RU",
                "entries": [e["id"] for e in entries], "requiresRuntime": "1.1.0",
                "sourceCatalogVersion": "test-3176d6ee-tem2-source-registry",
                "checksums": {"source_registry.json.gitBlob": BLOB}}
    meta = {"sourcePath": SOURCE, "sourceBlobSha": BLOB,
            "rootMetadata": {k: v for k, v in doc.items() if k != "sources"},
            "publicationStatus": "CANDIDATE", "actionDisposition": "INFORMATION_ONLY"}
    return {DEST: json.dumps({"manifest": manifest, "entries": entries},
                             ensure_ascii=False, separators=(",", ":")) + "\n",
            META: json.dumps(meta, ensure_ascii=False, separators=(",", ":")) + "\n"}


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--donor-root", type=Path, required=True)
    p.add_argument("--output-root", type=Path, default=Path("."))
    args = p.parse_args()
    for path, content in build(args.donor_root).items():
        target = args.output_root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    print("TEM2_SOURCE_REGISTRY", 9)
