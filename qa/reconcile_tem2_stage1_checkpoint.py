#!/usr/bin/env python3
"""Guard the bounded relation for the historical TEM2/TEM2U Stage 1 checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELATION_PATH = ROOT / "docs/data-migration/tem2-stage1-checkpoint-relations.json"
HISTORICAL_PATH = ROOT / "content-packs/locomotive-migration/migration/historical-documents.candidate.json"
PROFILE_INDEX_PATH = ROOT / "content-packs/diesel/tem2-family/migration/profile-source-index.json"
SOURCE_PACK_PATH = ROOT / "content-packs/diesel/tem2-family/sources/registry.pack.json"


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
    for phrase in ("STAGE_1_FOUNDATION_COMPLETE", "FOUNDATION_ONLY_NOT_READY_FOR_APP_INTEGRATION", "fail-closed", "Stage 2 не начинается автоматически"):
        assert phrase in checkpoint_text, phrase

    profile_index = load(PROFILE_INDEX_PATH)
    profiles = [document(profile_index, path)["sourceObject"] for path in relation["profilePaths"]]
    assert [profile["profileId"] for profile in profiles] == relation["profileIds"]
    for profile in profiles:
        assert profile["stage"] == "STAGE_1_FOUNDATION_COMPLETE"
        assert profile["completedStages"] == ["FOUNDATION"]
        assert profile["integrationState"] == "FOUNDATION_ONLY_NOT_READY_FOR_APP_INTEGRATION"
        assert profile["profileRules"]["unknownExecutionPolicy"] == "Fail closed for variant-dependent operational actions."

    contract = document(profile_index, "docs/locomotives/diesel/tem2-family/common/profile_contract.json")["sourceObject"]
    assert list(contract["explicitAdjacentVariantExclusions"]) == relation["adjacentVariantExclusionKeys"]
    assert contract["integrationDefaults"]["failClosedOnUnknownExecution"] is True
    assert contract["integrationDefaults"]["actualEquipmentOverridesNumberHint"] is True

    sources = load(SOURCE_PACK_PATH)["entries"]
    assert len(sources) == relation["sourceCount"]
    source_objects = {entry["sourceObject"]["object"]["id"]: entry["sourceObject"]["object"] for entry in sources}
    assert [source_id for source_id, source in source_objects.items() if source.get("currentness") == "CURRENT_CONFIRMED"] == relation["currentConfirmedSourceIds"]
    for source_id, authority in relation["currentConfirmedAuthorities"].items():
        assert source_objects[source_id]["authorityForAction"] == authority

    print("TEM2_STAGE1_CHECKPOINT_PASS 2 9 2 4")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args()
    check()
