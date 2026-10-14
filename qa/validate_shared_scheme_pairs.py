#!/usr/bin/env python3
"""Verify the 110 preserved source objects against their pinned disposition."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "docs/data-migration/shared-scheme-flow-layout-dispositions.json"
PACKS = {
    "ermak": ROOT / "content-packs/electric/ermak/atlas/shared-scheme-pairs.candidate.pack.json",
    "chme3-family": ROOT / "content-packs/diesel/chme3-family/atlas/shared-scheme-pairs.candidate.pack.json",
}


def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


overlay = json.loads(OVERLAY.read_text())
metadata = json.loads((ROOT / "content-packs/locomotive-migration/shared-scheme-source-metadata.candidate.json").read_text())
assert metadata["donorCommit"] == overlay["donorCommit"]
assert metadata["publicationStatus"] == "CANDIDATE" and metadata["runtimeImport"] is False
assert [(s["sourcePath"], s["sourceBlobSha"]) for s in metadata["sources"]] == [
    (s["sourcePath"], s["sourceBlobSha"]) for s in overlay["sources"]]
for source in metadata["sources"]:
    assert digest(source["metadata"]) == source["metadataSha256"]
assert [digest(gap) for gap in metadata["sources"][0]["metadata"]["researchGaps"]] == overlay["researchGapSha256"]
expected = {(r["sequenceId"], kind): r[f"{kind}Sha256"]
            for r in overlay["rows"] for kind in ("sequence", "layout")}
actual = {}
for model, path in PACKS.items():
    pack = json.loads(path.read_text())
    assert pack["manifest"]["entries"] == [e["id"] for e in pack["entries"]]
    assert pack["manifest"]["modelIds"] == [model]
    for entry in pack["entries"]:
        source = entry["sourceObject"]
        obj = source["object"]
        kind = "sequence" if "steps" in obj else "layout"
        sid = obj["id"] if kind == "sequence" else obj["sequenceId"]
        key = sid, kind
        assert key not in actual, key
        assert source["sourcePath"] == "app/src/main/assets/technical/" + (
            "stepwise_scheme_flows.json" if kind == "sequence" else "scheme_layout_metadata.json")
        assert source["sourceBlobSha"] == next(
            s["sourceBlobSha"] for s in overlay["sources"] if s["sourcePath"] == source["sourcePath"])
        assert entry["publicationStatus"] == "CANDIDATE"
        assert entry["actionDisposition"] == "INFORMATION_ONLY"
        assert entry["owner"] == {"kind": "MODEL", "modelId": model}
        assert not entry["links"] and not entry["sourceRefs"]
        actual[key] = digest(obj)
assert actual == expected, (set(expected) - set(actual), set(actual) - set(expected))
assert len(actual) == 110
print("SHARED_SCHEME_PAIRS_PASS", len(actual))
