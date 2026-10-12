#!/usr/bin/env python3
"""Pinned Stage-4 acceptance object and route fidelity gate."""
import argparse
import hashlib
import json
from pathlib import Path

from migrate_tem2_acceptance import BLOB, ROOT, SOURCE, build, read_source

PACK = ROOT / "acceptance/items-stage4.pack.json"
ROUTES = ROOT / "acceptance/routes-stage4.json"
EXPECTED_SHA256 = {
    "items-stage4.pack.json": "715e97ca53418a26f00a44aeb401b203918e0d4ca47ee6cdf7a021b19e4632eb",
    "routes-stage4.json": "a2aac0d329c119c425bf7f7087096225ca15e03e86f3d3fb1f73d282c70b2a22",
}


def validate(root, donor_root=None):
    pack_bytes = (root / PACK).read_bytes()
    route_bytes = (root / ROUTES).read_bytes()
    for path, raw in ((PACK, pack_bytes), (ROUTES, route_bytes)):
        assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256[path.name]
    pack, routes = json.loads(pack_bytes), json.loads(route_bytes)
    entries = pack["entries"]
    assert len(entries) == 16 and len({e["id"] for e in entries}) == 16
    assert pack["manifest"]["entries"] == [e["id"] for e in entries]
    assert pack["manifest"]["checksums"] == {"stage4_acceptance.json.gitBlob": BLOB}
    assert routes["donorGitBlob"] == BLOB and routes["sourcePath"] == SOURCE
    assert len(routes["routes"]) == 2
    assert len(routes["unresolvedItemReferences"]) == 2
    assert {x["sourceTargetId"] for x in routes["unresolvedItemReferences"]} == {
        "TEM2-EQ-DIESEL", "TEM2U-EQ-DIESEL"}
    ids = {}
    for path in (root / ROOT).rglob("*.pack.json"):
        for entry in json.loads(path.read_text())["entries"]:
            ids[entry["id"]] = entry
    link_count = 0
    for e in entries:
        assert e["type"] == "ACCEPTANCE_ITEM"
        assert e["owner"] == {"kind": "MODEL", "modelId": "tem2-family"}
        assert e["applicability"]["modelIds"] == ["tem2-family"]
        assert e["publicationStatus"] == "CANDIDATE"
        assert e["provenance"] == e["sourceStatus"] == "UNKNOWN"
        assert e["actionDisposition"] == "INFORMATION_ONLY"
        assert e["sourceObject"]["sourceBlobSha"] == BLOB
        assert all(isinstance(ref, str) for ref in e["sourceRefs"])
        for link in e["links"]:
            link_count += 1
            target = ids[link["targetId"]]
            variant, = link["applicability"]["variantIds"]
            assert variant in e["applicability"]["variantIds"]
            assert variant in target["applicability"]["variantIds"]
            assert link["type"] == {"DIAGNOSTIC_SCENARIO": "RELATED_SCENARIO"}.get(
                target["type"], target["type"])
    assert link_count == 80
    if donor_root:
        source = read_source(donor_root)
        assert [e["sourceObject"]["object"] for e in entries] == [
            *source["coreChecks"], *source["profileChecks"]]
        assert [r["sourceObject"] for r in routes["routes"]] == source["routes"]
        assert routes["rootMetadata"] == {k: v for k, v in source.items()
                                            if k not in ("coreChecks", "profileChecks", "routes")}
        for path, content in build(donor_root, root).items():
            assert (root / path).read_text() == content
    return len(entries), len(routes["routes"]), link_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--donor-root", type=Path)
    args = parser.parse_args()
    print("TEM2_ACCEPTANCE_PASS", *validate(args.root, args.donor_root))
