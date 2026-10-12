#!/usr/bin/env python3
"""Check pinned TEM2 Stage-3 source lineage and candidate research entries."""
import argparse
import hashlib
import json
from pathlib import Path

from migrate_tem2_stage3 import BLOB, LINEAGE, PROFILE, SOURCE, SOURCES, build

SHA = {LINEAGE: "718a195b578907a6052d90fbbc6d5b2c68c6d8f43a434193e39b826cd105b62c",
       SOURCES: "b67da6b99170b7025cfc0fa6ec90e1810d98660297eb39cd1e3207931601772a"}


def validate(root, donor_root=None):
    for path, sha in SHA.items():
        assert hashlib.sha256((root / path).read_bytes()).hexdigest() == sha
    lineage = json.loads((root / LINEAGE).read_text())
    pack = json.loads((root / SOURCES).read_text())
    assert lineage["sourceBlobSha"] == BLOB and lineage["sourcePath"] == SOURCE
    assert lineage["generatorGitBlob"] == "f8a8fcbacc9d4acabd921dd86e9f5cb1d1950fe8"
    assert lineage["publicationStatus"] == "CANDIDATE"
    assert lineage["actionDisposition"] == "INFORMATION_ONLY"
    records = lineage["scenarios"]
    assert len(records) == len({x["sourceObject"]["id"] for x in records}) == 24
    assert sum(len(x["targets"]) for x in records) == 46
    canonical = {}
    for path in (root / "content-packs/diesel/tem2-family/diagnostics/recommended").glob("*.pack.json"):
        for entry in json.loads(path.read_text())["entries"]:
            canonical[entry["id"]] = entry
    for item in records:
        src = item["sourceObject"]
        graph = src["runtimeGraph"]
        node_ids = {n["id"] for n in graph["nodes"]}
        assert len(node_ids) == len(graph["nodes"]) and graph["startNodeId"] in node_ids
        for node in graph["nodes"]:
            for edge in node.get("choices", []):
                assert edge["nextNodeId"] in node_ids
            if "uncertainNextNodeId" in node:
                assert node["uncertainNextNodeId"] in node_ids
            if "nextNodeId" in node:
                assert node["nextNodeId"] in node_ids
        assert {x["variantId"] for x in item["targets"]} == {PROFILE[p] for p in src["profileIds"]}
        for target in item["targets"]:
            assert target["projectionVerified"] is True
            entry = canonical[target["canonicalId"]]
            assert entry["sourceObject"]["object"]["id"] == src["id"]
            assert target["variantId"] in entry["applicability"]["variantIds"]
    entries = pack["entries"]
    assert len(entries) == 3 and pack["manifest"]["entries"] == [x["id"] for x in entries]
    assert pack["manifest"]["checksums"] == {"stage3_model.json.gitBlob": BLOB}
    for e in entries:
        assert e["type"] == "SOURCE" and e["owner"] == {"kind": "MODEL", "modelId": "tem2-family"}
        assert e["applicability"] == {"modelIds": ["tem2-family"], "variantIds": ["tem2"]}
        assert e["publicationStatus"] == "CANDIDATE"
        assert e["provenance"] == e["sourceStatus"] == "UNKNOWN"
        assert e["actionDisposition"] == "INFORMATION_ONLY"
        assert isinstance(e["summary"], str)
        assert e["sourceObject"]["sourceBlobSha"] == BLOB
    if donor_root:
        for path, content in build(donor_root, root).items():
            assert (root / path).read_text() == content
    return len(records), sum(len(x["targets"]) for x in records), len(entries)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--donor-root", type=Path)
    a = p.parse_args()
    print("TEM2_STAGE3_PASS", *validate(a.root, a.donor_root))
