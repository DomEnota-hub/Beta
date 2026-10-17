#!/usr/bin/env python3
"""Preserve original VL80S electrical and pneumatic source catalogs."""

import argparse
import gzip
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = "app/src/main/assets/technical"
SOURCES = {
    "vl80s_electrical.json.gz": ("6891068a9aeb92d6a33c445e1c7284f9a4c21ff9",
                                 "d73f8e7c8e84b51f763f11dd7b71392a91a756f2376e045b70b6487f6ac70963"),
    "vl80s_pneumatic.json.gz": ("6adafce6307445d881a2f7cebde4837230431129",
                                "b59007b11fbd5da0b39d0d3ceed3517193b246d15bcd05ff76e104181d4c5570"),
    "vl80s_electrical_variants.json.gz": ("f9f7956f871cbb04d38b8315e1b902372d5f3f7b",
                                          "cd66e68cd79eb2f38554653bc6e4d764d7d617dff33d10318aca7bad04f6d58f"),
    "vl80s_pneumatic_variants.json.gz": ("3899e9e653f17c7b26e2c3d97a8852d4537a2537",
                                         "ad50bd417c5c59af393745da85bad255b9ccd5f73f8cc142a32bfc339f3d40ee"),
    "vl80s_variants.json.gz": ("9a35df3df98173e7baa3edc05e4457c8f5eed6ea",
                                "e9fa48dea275c183bfe6f5445a50585a9916d61c6655ee5dc9d4e5c9286274b4"),
}
DESTINATION = ROOT / "content-packs/electric/vl80s/migration/scheme-source-catalogs.candidate.json"


def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def project(donor):
    sources = []
    for name, (blob, expected_hash) in SOURCES.items():
        path = donor / SOURCE_DIR / name
        assert subprocess.check_output(["git", "hash-object", str(path)], text=True).strip() == blob
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            obj = json.load(stream)
        assert digest(obj) == expected_hash
        if name == "vl80s_electrical.json.gz":
            assert (len(obj["baseSchemes"]), len(obj["schemeIndex"]), len(obj["modeOverlays"])) == (8, 8, 8)
        elif name == "vl80s_pneumatic.json.gz":
            assert (len(obj["views"]), len(obj["states"]), len(obj["referenceBenchmarks"])) == (8, 13, 5)
        elif name == "vl80s_electrical_variants.json.gz":
            assert (len(obj["variantOverlays"]), len(obj["candidateVariantFragments"])) == (8, 2)
        elif name == "vl80s_pneumatic_variants.json.gz":
            assert len(obj["stateApplicability"]) == 13
        else:
            assert (len(obj["physicalBuckets"]), len(obj["nonMergeRules"])) == (9, 6)
        sources.append({"sourcePath": f"{SOURCE_DIR}/{name}", "sourceBlobSha": blob,
                        "sourceObjectSha256": expected_hash, "sourceObject": obj})
    return {"schemaVersion": 1,
            "donorCommit": "3176d6ee228f0ed4b78371f45209e10c1c724eff",
            "modelOwner": "vl80s", "publicationStatus": "CANDIDATE", "runtimeImport": False,
            "sources": sources,
            "note": "Complete original catalogs for lossless comparison; donor FINAL labels are not current authority or action permission."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("donor", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(project(args.donor), ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert DESTINATION.read_text() == encoded
    else:
        DESTINATION.write_text(encoded)
    print("VL80S_SCHEME_SOURCES_PASS", 5, 5)


if __name__ == "__main__":
    main()
