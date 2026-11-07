#!/usr/bin/env python3
"""Guard the bounded relation for the historical CHME3E Stage 1 checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELATION_PATH = ROOT / "docs/data-migration/chme3e-stage1-checkpoint-relations.json"
HISTORICAL_PATH = ROOT / "content-packs/locomotive-migration/migration/historical-documents.candidate.json"
PROFILE_INDEX_PATH = ROOT / "content-packs/diesel/chme3-family/migration/profile-source-index.json"
SOURCE_INDEX_PATH = ROOT / "content-packs/diesel/chme3-family/migration/source-registry-index.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def document(index: dict, source_path: str) -> dict:
    matches = [item for item in index["documents"] if item["sourcePath"] == source_path]
    if len(matches) != 1:
        raise AssertionError(f"expected one preserved document for {source_path}, got {len(matches)}")
    return matches[0]


def check() -> None:
    relation = load(RELATION_PATH)
    assert relation["publicationStatus"] == "CANDIDATE"
    assert relation["runtimeImport"] is False
    assert relation["currentAuthorityVerified"] is False
    assert relation["actionAuthorityGranted"] is False

    historical = document(load(HISTORICAL_PATH), relation["checkpoint"]["path"])
    checkpoint_text = historical["exactSourceText"]
    assert historical["sourceBlobSha"] == relation["checkpoint"]["blobSha"]
    assert hashlib.sha256(checkpoint_text.encode("utf-8")).hexdigest() == relation["checkpoint"]["textSha256"]
    for phrase in (
        "дополнительное электронное управление",
        "устройство прогрева дизеля",
        "отсутствуют реостатный тормоз",
        "CHME3T-EDB runtime actions",
        "не как достаточное доказательство фактического исполнения",
        "NO` / `NO_BY_ITSELF",
    ):
        assert phrase in checkpoint_text, phrase

    profile_index = load(PROFILE_INDEX_PATH)
    profile = document(profile_index, relation["profile"]["path"])
    inheritance = document(profile_index, relation["inheritance"]["path"])
    assert profile["sourceBlobSha"] == relation["profile"]["blobSha"]
    assert inheritance["sourceBlobSha"] == relation["inheritance"]["blobSha"]
    profile_object = profile["sourceObject"]
    inheritance_object = inheritance["sourceObject"]
    assert profile_object["profileId"] == relation["profile"]["profileId"]
    assert profile_object["variantTraits"] == relation["profileTraits"]
    assert profile_object["explicitExclusions"][1:4] == [
        "CHME3T braking resistor bank",
        "CHME3T braking resistor cooling",
        "CHME3T EDB runtime actions",
    ]
    for equipment_id in relation["chme3tOnlyEquipmentIds"]:
        assert equipment_id in inheritance_object["hardExclusions"]
    assert relation["hardExclusion"] in inheritance_object["hardExclusions"]

    source_index = load(SOURCE_INDEX_PATH)
    registry = document(source_index, "docs/locomotives/diesel/chme3-family/chme3e/source_registry.json")
    sources = {source["id"]: source for source in registry["sourceObject"]["sources"]}
    assert list(sources) == relation["sourceIds"]
    assert sources["CHME3E-SRC-FLEET-RANGES-REFERENCE"]["authorityForAction"] == "NO"
    for source_id in relation["sourceIds"][:-1]:
        assert sources[source_id]["authorityForAction"] == "NO_BY_ITSELF"

    print("CHME3E_STAGE1_CHECKPOINT_PASS 4 3 3 4")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args()
    check()
