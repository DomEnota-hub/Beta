#!/usr/bin/env python3
"""Preserve VL80S equipment catalog context omitted by the 89 record packs."""

import argparse
import gzip
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = "app/src/main/assets/technical/vl80s_equipment.json.gz"
SOURCE_SHA = "a6d00459e18ca428601b4a0cd32ee95a7d1551e7"
CONTEXT_SHA = "0598c404b8ae0f92da37763d85cd2c9d9cca31ef8db86aec687c3ace608fe9d8"
ZONE_IDS = ("VL-ZONE-CAB-001", "VL-ZONE-HV-001", "VL-ZONE-HV-002")
TARGET = ROOT / "content-packs/electric/vl80s/migration/equipment-context.candidate.json"


def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def project(source):
    assert len(source["records"]) == 89
    context = {k: v for k, v in source.items() if k != "records"}
    assert digest(context) == CONTEXT_SHA
    assert tuple(z["id"] for z in context["zones"]) == ZONE_IDS
    return {
        "schemaVersion": 1,
        "donorCommit": "3176d6ee228f0ed4b78371f45209e10c1c724eff",
        "sourcePath": SOURCE_PATH,
        "sourceBlobSha": SOURCE_SHA,
        "modelOwner": "vl80s",
        "publicationStatus": "CANDIDATE",
        "runtimeImport": False,
        "recordCountPreservedInEquipmentPacks": 89,
        "sourceRootSha256": CONTEXT_SHA,
        "sourceRootWithoutRecords": context,
        "note": "Original catalog status and source claims are donor data, not current approval.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("donor", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = args.donor / SOURCE_PATH
    assert subprocess.check_output(["git", "hash-object", str(path)], text=True).strip() == SOURCE_SHA
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        source = json.load(stream)
    encoded = json.dumps(project(source), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        assert TARGET.read_text() == encoded
    else:
        TARGET.write_text(encoded)
    print("VL80S_EQUIPMENT_CONTEXT_PASS", 89, len(source["zones"]))


if __name__ == "__main__":
    main()
