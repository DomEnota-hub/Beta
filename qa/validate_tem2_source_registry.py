#!/usr/bin/env python3
"""Pinned source-registry object fidelity and publication gate."""
import argparse
import hashlib
import json
from pathlib import Path

from migrate_tem2_source_registry import BLOB, DEST, META, build, source, variants

SHA = {DEST: "48153babfe4089a6d283f45c78df47ee073308f27c2e00902915c54ced5cee23",
       META: "b5c4cfeec8b2d1a7d0e21e8ca77c857f5aee337c8541ad8e616f73d7328da0a6"}


def validate(root, donor_root=None):
    for path, sha in SHA.items():
        assert hashlib.sha256((root / path).read_bytes()).hexdigest() == sha
    pack = json.loads((root / DEST).read_text())
    meta = json.loads((root / META).read_text())
    entries = pack["entries"]
    assert len(entries) == len({e["id"] for e in entries}) == 9
    assert pack["manifest"]["entries"] == [e["id"] for e in entries]
    assert pack["manifest"]["checksums"] == {"source_registry.json.gitBlob": BLOB}
    assert meta["sourceBlobSha"] == BLOB
    for e in entries:
        assert e["type"] == "SOURCE" and e["owner"] == {"kind": "MODEL", "modelId": "tem2-family"}
        assert e["applicability"]["modelIds"] == ["tem2-family"]
        assert e["applicability"]["variantIds"] == variants(e["sourceObject"]["object"])
        assert e["publicationStatus"] == "CANDIDATE"
        assert e["provenance"] == e["sourceStatus"] == "UNKNOWN"
        assert e["actionDisposition"] == "INFORMATION_ONLY"
        assert not e["links"] and not e["sourceRefs"]
        assert e["sourceObject"]["sourceBlobSha"] == BLOB
    if donor_root:
        original = source(donor_root)
        assert [e["sourceObject"]["object"] for e in entries] == original["sources"]
        assert meta["rootMetadata"] == {k: v for k, v in original.items() if k != "sources"}
        for path, content in build(donor_root).items():
            assert (root / path).read_text() == content
    return len(entries)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--donor-root", type=Path)
    a = p.parse_args()
    print("TEM2_SOURCE_REGISTRY_PASS", validate(a.root, a.donor_root))
