#!/usr/bin/env python3
"""Preserve original TEM2 catalog root fields outside the migrated entries."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = "app/src/main/assets/technical"
SOURCES = {
    "tem2_tem2_catalog.json": ("c7a94c1cd2687b84de4358b80773e3156c6b93d7",
                               "091e743e976673cea23ced0651cd43b3a5f86551855b7a0362f147268ff17b66", 122, "tem2-base"),
    "tem2_tem2u_catalog.json": ("766ac526fa4b86245704ed0252c2fdf3998a0e78",
                                "ee85603c5826579b4ed6232119bea68f801ee93bbee534002980e36e0c6dc4a8", 131, "tem2u-improved"),
}
TARGET = ROOT / "content-packs/diesel/tem2-family/migration/catalog-roots.candidate.json"


def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def project(donor):
    rows = []
    for name, (blob, root_sha, count, profile) in SOURCES.items():
        path = donor / SOURCE_DIR / name
        assert subprocess.check_output(["git", "hash-object", str(path)], text=True).strip() == blob
        source = json.loads(path.read_text())
        assert len(source["entries"]) == count
        root = {k: v for k, v in source.items() if k != "entries"}
        assert root == {"schemaVersion": 1, "profileId": profile} and digest(root) == root_sha
        rows.append({"sourcePath": f"{SOURCE_DIR}/{name}", "sourceBlobSha": blob,
                     "entryCountInExistingPacks": count, "sourceRootSha256": root_sha,
                     "sourceRootWithoutEntries": root})
    return {"schemaVersion": 1, "donorCommit": "3176d6ee228f0ed4b78371f45209e10c1c724eff",
            "modelOwner": "tem2-family", "publicationStatus": "CANDIDATE",
            "runtimeImport": False, "catalogs": rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("donor", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(project(args.donor), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        assert TARGET.read_text() == encoded
    else:
        TARGET.write_text(encoded)
    print("TEM2_CATALOG_ROOTS_PASS", 2, 253)


if __name__ == "__main__":
    main()
