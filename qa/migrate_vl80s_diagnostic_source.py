#!/usr/bin/env python3
"""Preserve the complete pinned VL80S diagnostic source outside runtime."""

import argparse
import gzip
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = "app/src/main/assets/technical/vl80s_diagnostics.json.gz"
SOURCE_BLOB = "6ffdfdabf2f467dcdc4958768905f2b675ac0c26"
SOURCE_JSON_SHA256 = "e524170d904cd8bf115952ceb156106e0e1fe3ec0a95aad73b6e506c0f90893d"
DESTINATION = ROOT / "content-packs/electric/vl80s/diagnostics/migration/diagnostics-source.candidate.json"


def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def project(donor):
    path = donor / SOURCE_PATH
    assert subprocess.check_output(["git", "hash-object", str(path)], text=True).strip() == SOURCE_BLOB
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        source = json.load(stream)
    assert digest(source) == SOURCE_JSON_SHA256
    assert (len(source["scenarios"]), len(source["edges"]),
            len(source["acceptanceHintCorrections"]),
            len(source["integrationExceptions"])) == (103, 1181, 7, 2)
    return {
        "schemaVersion": 1,
        "donorCommit": "3176d6ee228f0ed4b78371f45209e10c1c724eff",
        "sourcePath": SOURCE_PATH,
        "sourceBlobSha": SOURCE_BLOB,
        "sourceObjectSha256": SOURCE_JSON_SHA256,
        "modelOwner": "vl80s",
        "publicationStatus": "CANDIDATE",
        "runtimeImport": False,
        "actionAuthorityGranted": False,
        "sourceObject": source,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("donor", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(project(args.donor), ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert DESTINATION.read_text() == encoded
    else:
        DESTINATION.parent.mkdir(parents=True, exist_ok=True)
        DESTINATION.write_text(encoded)
    print("VL80S_DIAGNOSTIC_SOURCE_PASS", 103, 1181, 7, 2)


if __name__ == "__main__":
    main()
