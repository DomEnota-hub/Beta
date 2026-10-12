#!/usr/bin/env python3
"""Pinned TEM2 Stage-2 source-object and variant-projection checks."""
import argparse
import hashlib
import json
from pathlib import Path

from migrate_tem2_stage2 import BLOB, DEST, ROOT, SOURCE, build

SHA = "8aeb1e1d5aa15b5bca661a9baf906174c95f6b4668d082125d2de6d35611c82b"
COUNTS = {"systems": (9, 18), "equipment": (36, 68),
          "schemes": (9, 17), "flows": (11, 21)}


def validate(root, donor_root=None):
    assert hashlib.sha256((root / DEST).read_bytes()).hexdigest() == SHA
    doc = json.loads((root / DEST).read_text())
    assert doc["sourcePath"] == SOURCE and doc["sourceBlobSha"] == BLOB
    assert doc["generatorGitBlob"] == "f8a8fcbacc9d4acabd921dd86e9f5cb1d1950fe8"
    assert doc["publicationStatus"] == "CANDIDATE"
    assert doc["actionDisposition"] == "INFORMATION_ONLY"
    ids = {}
    for path in (root / ROOT).rglob("*.pack.json"):
        for e in json.loads(path.read_text())["entries"]:
            ids[e["id"]] = e
    for kind, (objects, associations) in COUNTS.items():
        rows = doc["sourceObjects"][kind]
        assert len(rows) == len({x["sourceId"] for x in rows}) == objects
        assert sum(len(x["targets"]) for x in rows) == associations
        for row in rows:
            assert row["sourceObject"]
            assert len({x["variantId"] for x in row["targets"]}) == len(row["targets"])
            for target in row["targets"]:
                variant = target["variantId"]
                assert variant in ("tem2", "tem2u")
                e = ids[target["canonicalId"]]
                assert variant in e["applicability"]["variantIds"]
                assert e["sourceObject"]["object"]["id"] == target["sourceTargetId"]
    if donor_root:
        expected = json.dumps(build(donor_root, root), ensure_ascii=False,
                              separators=(",", ":")) + "\n"
        assert (root / DEST).read_text() == expected
    return sum(n for n, _ in COUNTS.values()), sum(n for _, n in COUNTS.values())


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--donor-root", type=Path)
    a = p.parse_args()
    print("TEM2_STAGE2_PASS", *validate(a.root, a.donor_root))
