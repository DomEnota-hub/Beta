#!/usr/bin/env python3
"""Keep the complete pinned VL80S acceptance source beside projected cards."""

import argparse
import gzip
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = "app/src/main/assets/technical/vl80s_acceptance.json.gz"
SOURCE_SHA = "5174e8fa343bb4d5b61d4f541d4dffec2708127d"
OBJECT_SHA256 = "71695dbfa01f51d663acd38f91bf354e3684b10c2a02fbd068aeebd253b975e4"
DESTINATION = ROOT / "content-packs/electric/vl80s/migration/acceptance-source.candidate.json"


def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def project(obj):
    assert digest(obj) == OBJECT_SHA256
    assert len(obj["items"]) == 66 and len(obj["routes"]) == 7
    assert len(obj["zones"]) == 9 and len(obj["gates"]) == 3
    assert len(obj["designPrinciples"]) == 6 and len(obj["sources"]) == 6
    return {
        "schemaVersion": 1,
        "donorCommit": "3176d6ee228f0ed4b78371f45209e10c1c724eff",
        "sourcePath": SOURCE_PATH,
        "sourceBlobSha": SOURCE_SHA,
        "sourceObjectSha256": OBJECT_SHA256,
        "modelOwner": "vl80s",
        "publicationStatus": "CANDIDATE",
        "runtimeImport": False,
        "sourceObject": obj,
        "note": "Exact original candidate source. Donor FINAL is historical text, not current approval or permission to perform work.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("donor", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = args.donor / SOURCE_PATH
    assert subprocess.check_output(["git", "hash-object", str(path)], text=True).strip() == SOURCE_SHA
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        obj = json.load(stream)
    encoded = json.dumps(project(obj), ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert DESTINATION.read_text() == encoded
    else:
        DESTINATION.write_text(encoded)
    print("VL80S_ACCEPTANCE_SOURCE_PASS", 66, 7, 9)


if __name__ == "__main__":
    main()
