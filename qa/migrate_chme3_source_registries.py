#!/usr/bin/env python3
"""Preserve pinned CHME3 source registries without resolving conflicting IDs."""
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

DEST = Path("content-packs/diesel/chme3-family/migration/source-registry-index.json")
PINS = {
    "docs/locomotives/chme3/acceptance_source_registry_addendum.json": "8ce0ae39a92f649fa2a34cda2d6c050f11b17769",
    "docs/locomotives/chme3/diagnostic_source_registry_addendum.json": "be74b1b6b3082a7962a30cf6e8a5c877be7cacac",
    "docs/locomotives/chme3/source_registry.json": "e4aa3273316358bcc2692a70768e6f067a7bd14c",
    "docs/locomotives/chme3/source_registry_addendum_atlas.json": "0530baec0f0180ef92c65943197579bf6f478c03",
    "docs/locomotives/diesel/chme3-family/chme3e/source_registry.json": "f95f8fa25a3331b7ad015da2c426bf1ceda3085f",
    "docs/locomotives/diesel/chme3-family/chme3e/source_registry_stage2.json": "ebd2cbd10543bc112ae141f3dfef52ed01dbcab0",
}


def blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def read_pinned(root, path, sha):
    raw = (root / path).read_bytes()
    if blob_sha(raw) != sha and raw.endswith(b"\n"):
        raw = raw[:-1]  # Retrieval added one transport newline to some donor files.
    assert blob_sha(raw) == sha, path
    return json.loads(raw)


def build(donor_root):
    documents = []
    occurrences = defaultdict(list)
    for path, sha in PINS.items():
        obj = read_pinned(donor_root, path, sha)
        assert isinstance(obj, dict) and isinstance(obj.get("sources"), list), path
        documents.append({"sourcePath": path, "sourceBlobSha": sha, "sourceObject": obj})
        for i, source in enumerate(obj["sources"]):
            assert isinstance(source.get("id"), str) and source["id"], (path, i)
            occurrences[source["id"]].append({"sourcePath": path, "sourcePointer": f"/sources/{i}"})
    duplicates = [{"sourceId": key, "occurrences": value} for key, value in sorted(occurrences.items()) if len(value) > 1]
    return {"schemaVersion": 1, "donorCommit": "3176d6ee228f0ed4b78371f45209e10c1c724eff",
            "publicationStatus": "CANDIDATE", "actionDisposition": "INFORMATION_ONLY",
            "runtimeImport": False, "sourceIdPolicy": "DOCUMENT_SCOPED_UNRESOLVED",
            "sourceRecordOccurrences": sum(map(len, occurrences.values())),
            "distinctSourceIds": len(occurrences), "duplicateSourceIds": duplicates,
            "documents": documents}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--donor-root", type=Path, required=True)
    p.add_argument("--output-root", type=Path, default=Path("."))
    a = p.parse_args()
    target = a.output_root / DEST
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build(a.donor_root), ensure_ascii=False, separators=(",", ":")) + "\n")
    print("CHME3_SOURCE_REGISTRIES", len(PINS))
