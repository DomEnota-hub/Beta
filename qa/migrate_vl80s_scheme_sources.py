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
        if name.startswith("vl80s_electrical"):
            assert (len(obj["baseSchemes"]), len(obj["schemeIndex"]), len(obj["modeOverlays"])) == (8, 8, 8)
        else:
            assert (len(obj["views"]), len(obj["states"]), len(obj["referenceBenchmarks"])) == (8, 13, 5)
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
    print("VL80S_SCHEME_SOURCES_PASS", 2, 5)


if __name__ == "__main__":
    main()
