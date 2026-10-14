#!/usr/bin/env python3
"""Pin complete diagnostic reference sources as non-runtime candidates."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_BASE = "app/src/main/assets/technical"
SOURCES = {
    "extended_emergency_policy.json": (
        "60f132caa0364b01ee746ab3531aa8f36718ef0b",
        "4be5e4ddfc56b529a12668f65d7659340e584b6a2fbb39f9e82ef0447d35142f",
        "content-packs/locomotive-migration/extended-emergency-policy-source.candidate.json",
    ),
    "diagnostic_framework_v2.json": (
        "ab2ecd3f58256a1d4d260dc17ec334ee8fe4d12d",
        "e83f3cade0242fa668a65a453a5f60da65fafc9024b433e4b51fc8b84cc7c4ee",
        "content-packs/electric/vl80s/diagnostics/migration/framework-source.candidate.json",
    ),
    "vl80s_pantograph_reference_pack.json": (
        "2256a734d3cd929012629ab1cfbeeddccef96933",
        "de950e2bb35321bdfdf09a959b37eeb367a4a2d0bc116f5b062f4744d6123f67",
        "content-packs/electric/vl80s/diagnostics/migration/pantograph-reference-source.candidate.json",
    ),
}


def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def project(donor):
    result = {}
    for name, (blob, object_hash, destination) in SOURCES.items():
        source_path = f"{SOURCE_BASE}/{name}"
        path = donor / source_path
        assert subprocess.check_output(["git", "hash-object", str(path)], text=True).strip() == blob
        obj = json.loads(path.read_text())
        assert digest(obj) == object_hash
        result[ROOT / destination] = {
            "schemaVersion": 1,
            "donorCommit": "3176d6ee228f0ed4b78371f45209e10c1c724eff",
            "sourcePath": source_path,
            "sourceBlobSha": blob,
            "sourceObjectSha256": object_hash,
            "publicationStatus": "CANDIDATE",
            "runtimeImport": False,
            "actionAuthorityGranted": False,
            "sourceObject": obj,
        }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("donor", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for path, obj in project(args.donor).items():
        encoded = json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n"
        if args.check:
            assert path.read_text() == encoded, path
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(encoded)
    print("DIAGNOSTIC_REFERENCE_SOURCE_PASS", len(SOURCES))


if __name__ == "__main__":
    main()
