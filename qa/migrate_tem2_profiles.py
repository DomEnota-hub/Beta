#!/usr/bin/env python3
"""Preserve pinned TEM2 family/profile contracts as closed source evidence."""
import hashlib
import json
from pathlib import Path

ROOT = Path("content-packs/diesel/tem2-family")
DEST = ROOT / "migration/profile-source-index.json"
PINS = {
    "docs/locomotives/diesel/tem2-family/family_manifest.json": "f1cfe2a201a7afac4f696722f3ed5334b9723859",
    "docs/locomotives/diesel/tem2-family/common/profile_contract.json": "5e64bd7acf1a245754ebb6f2810c678f3b81fc44",
    "docs/locomotives/diesel/tem2-family/tem2/profile.json": "8b89b5b4ebe44edc80ebfe243d3fb31eed5c7a3f",
    "docs/locomotives/diesel/tem2-family/tem2u/profile.json": "ed4af8c94e4be9f0ac9571f5dd5e052123ddf00a",
}
VARIANTS = {"tem2-base": "tem2", "tem2u-improved": "tem2u"}


def read(donor_root, path, sha):
    raw = (donor_root / path).read_bytes()
    digest = lambda b: hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()
    if digest(raw) != sha and raw.endswith(b"\n"):
        raw = raw[:-1]
    assert digest(raw) == sha, path
    return json.loads(raw)


def build(donor_root):
    docs = [{"sourcePath": path, "sourceBlobSha": sha,
             "sourceObject": read(donor_root, path, sha)} for path, sha in PINS.items()]
    manifest, contract, tem2, tem2u = [x["sourceObject"] for x in docs]
    assert manifest["familyId"] == contract["familyId"] == tem2["familyId"] == tem2u["familyId"] == "tem2-family"
    assert manifest["canonicalLayers"]["variants"] == VARIANTS
    assert {x["profileId"] for x in manifest["profiles"]} == set(VARIANTS)
    assert tem2["profileId"] == "tem2-base" and tem2u["profileId"] == "tem2u-improved"
    assert contract["integrationDefaults"]["failClosedOnUnknownExecution"] is True
    assert set(tem2["explicitExclusions"]) and set(tem2u["explicitExclusions"])
    return {"schemaVersion": 1, "donorCommit": "3176d6ee228f0ed4b78371f45209e10c1c724eff",
            "publicationStatus": "CANDIDATE", "actionDisposition": "INFORMATION_ONLY",
            "runtimeImport": False, "profileBindings": VARIANTS, "documents": docs}


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--donor-root", type=Path, required=True)
    p.add_argument("--output-root", type=Path, default=Path("."))
    a = p.parse_args()
    target = a.output_root / DEST
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build(a.donor_root), ensure_ascii=False,
                                 separators=(",", ":")) + "\n")
    print("TEM2_PROFILE_SOURCES", 4)
