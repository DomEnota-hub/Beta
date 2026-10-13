#!/usr/bin/env python3
"""Preserve pinned CHME3 acceptance documents as non-executable source evidence."""
import argparse
import hashlib
import json
from pathlib import Path

DEST = Path("content-packs/diesel/chme3-family/migration/acceptance-source-index.json")
PINS = {
    "docs/locomotives/chme3/acceptance_contract_pass4.json": "13bdf5229e30fbbcb9577c3c22404eb27640241d",
    "docs/locomotives/chme3/acceptance_required_pass4.json": "dbb7765f32bc0b8161be9ca3e2e636fd42cc7f4f",
    "docs/locomotives/diesel/chme3-family/common/acceptance_stage4_manifest.json": "00249bd42ad936b6d77c558a6a8d08a9ff310a75",
    "docs/locomotives/diesel/chme3-family/chme3e/acceptance_stage4.json": "7b0929e9a2bae6e1600d4df9dbd0bd1206bc1f89",
}


def read_pinned(root, path, sha):
    raw = (root / path).read_bytes()
    digest = lambda b: hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()
    if digest(raw) != sha and raw.endswith(b"\n"):
        raw = raw[:-1]
    assert digest(raw) == sha, path
    return json.loads(raw)


def build(donor_root):
    docs = [{"sourcePath": path, "sourceBlobSha": sha,
             "sourceObject": read_pinned(donor_root, path, sha)} for path, sha in PINS.items()]
    contract, required, manifest, electronic = [d["sourceObject"] for d in docs]
    assert len(required["items"]) == 21 and len(electronic["profileExtendedChecks"]) == 4
    assert len(contract["routes"]) == 7
    assert manifest["familyId"] == electronic["familyId"] == "chme3-family"
    assert electronic["profileId"] == "chme3e-electronic"
    required_ids = [x["id"] for x in required["items"]]
    extended_ids = [x["id"] for x in electronic["profileExtendedChecks"]]
    assert len(set(required_ids)) == len(required_ids)
    assert len(set(extended_ids)) == len(extended_ids)
    assert set(required_ids).isdisjoint(extended_ids)
    return {"schemaVersion": 1, "donorCommit": "3176d6ee228f0ed4b78371f45209e10c1c724eff",
            "publicationStatus": "CANDIDATE", "actionDisposition": "INFORMATION_ONLY",
            "runtimeImport": False, "documents": docs}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--donor-root", type=Path, required=True)
    p.add_argument("--output-root", type=Path, default=Path("."))
    a = p.parse_args()
    target = a.output_root / DEST
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build(a.donor_root), ensure_ascii=False, separators=(",", ":")) + "\n")
    print("CHME3_ACCEPTANCE_SOURCES", len(PINS))
