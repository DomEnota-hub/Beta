#!/usr/bin/env python3
"""Preserve the shared family layout manifest without assigning single-family ownership."""
import argparse
import hashlib
import json
from pathlib import Path

SOURCE = "docs/locomotives/manifests/locomotive_families.json"
SHA = "ea44f500c6c7e0673a39f789695dfc303794f460"
DEST = Path("content-packs/locomotive-migration/shared-family-manifest-source.json")


def build(donor_root):
    raw = (donor_root / SOURCE).read_bytes()
    digest = lambda b: hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()
    if digest(raw) != SHA and raw.endswith(b"\n"):
        raw = raw[:-1]
    assert digest(raw) == SHA
    source = json.loads(raw)
    assert {f["familyId"] for f in source["families"]} == {"chme3-family", "tem2-family"}
    return {"schemaVersion": 1, "donorCommit": "3176d6ee228f0ed4b78371f45209e10c1c724eff",
            "sourcePath": SOURCE, "sourceBlobSha": SHA, "sourceObject": source,
            "owner": "MIXED_REVIEW_REQUIRED", "publicationStatus": "CANDIDATE",
            "actionDisposition": "INFORMATION_ONLY", "runtimeImport": False}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--donor-root", type=Path, required=True)
    p.add_argument("--output-root", type=Path, default=Path("."))
    a = p.parse_args()
    target = a.output_root / DEST
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build(a.donor_root), ensure_ascii=False, separators=(",", ":")) + "\n")
    print("LOCOMOTIVE_FAMILY_MANIFEST_SOURCE_PASS")
