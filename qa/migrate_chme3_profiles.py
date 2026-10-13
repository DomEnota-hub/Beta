#!/usr/bin/env python3
"""Preserve CHME3 family/profile source documents without activating their rules."""
import argparse
import hashlib
import json
from pathlib import Path

DEST = Path("content-packs/diesel/chme3-family/migration/profile-source-index.json")
PINS = {
    "docs/locomotives/chme3/profiles.json": "d8dc20124563c54756d53955c853c52839a64de9",
    "docs/locomotives/diesel/chme3-family/family_manifest.json": "791c42a64df0d23ee0327746132c59f9c60fc080",
    "docs/locomotives/diesel/chme3-family/chme3e/profile.json": "39743600eb4ff4d043380df5f75cff5641b37eaa",
    "docs/locomotives/diesel/chme3-family/chme3e/inheritance.json": "c8f56386499b9f232645bf5ebd4f8f6c3a4e563b",
}
VARIANTS = {"chme3-base": "chme3", "chme3t-rheostatic": "chme3t", "chme3e-electronic": "chme3e"}


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
    legacy, manifest, electronic, inheritance = [d["sourceObject"] for d in docs]
    assert legacy["familyId"] == manifest["familyId"] == electronic["familyId"] == "chme3-family"
    assert manifest["canonicalLayers"]["variants"] == VARIANTS
    assert {p["id"] for p in legacy["profiles"]} == set(VARIANTS)
    assert {p["profileId"] for p in manifest["profiles"]} == set(VARIANTS)
    assert electronic["profileId"] == inheritance["profileId"] == "chme3e-electronic"
    assert "CHME3-SYS-EDB" in inheritance["hardExclusions"]
    assert manifest["integrationBoundary"]["androidRuntimeIntegrated"] is False
    return {"schemaVersion": 1, "donorCommit": "3176d6ee228f0ed4b78371f45209e10c1c724eff",
            "publicationStatus": "CANDIDATE", "actionDisposition": "INFORMATION_ONLY",
            "runtimeImport": False, "profileBindings": VARIANTS, "documents": docs}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--donor-root", type=Path, required=True)
    p.add_argument("--output-root", type=Path, default=Path("."))
    a = p.parse_args()
    target = a.output_root / DEST
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build(a.donor_root), ensure_ascii=False, separators=(",", ":")) + "\n")
    print("CHME3_PROFILE_SOURCES", len(PINS))
