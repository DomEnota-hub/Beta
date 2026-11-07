#!/usr/bin/env python3
"""Guard the bounded relation for the historical CHME3E Stage 2 checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELATION_PATH = ROOT / "docs/data-migration/chme3e-stage2-checkpoint-relations.json"
HISTORICAL_PATH = ROOT / "content-packs/locomotive-migration/migration/historical-documents.candidate.json"
INDICES = (
    ROOT / "content-packs/diesel/chme3-family/migration/atlas-source-index.json",
    ROOT / "content-packs/diesel/chme3-family/migration/remaining-document-source-index.json",
    ROOT / "content-packs/diesel/chme3-family/migration/source-registry-index.json",
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def document(indices: tuple[dict, ...], source_path: str) -> dict:
    matches = [item for index in indices for item in index["documents"] if item["sourcePath"] == source_path]
    if len(matches) != 1:
        raise AssertionError(f"expected one preserved document for {source_path}, got {len(matches)}")
    return matches[0]


def strings(value: object) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return set().union(*(strings(item) for item in value))
    if isinstance(value, dict):
        return set().union(*(strings(item) for item in value.values()))
    return set()


def check() -> None:
    relation = load(RELATION_PATH)
    assert relation["publicationStatus"] == "CANDIDATE"
    assert relation["runtimeImport"] is False
    assert relation["currentAuthorityVerified"] is False
    assert relation["actionAuthorityGranted"] is False

    historical = load(HISTORICAL_PATH)
    checkpoint = document((historical,), relation["checkpoint"]["path"])
    checkpoint_text = checkpoint["exactSourceText"]
    assert checkpoint["sourceBlobSha"] == relation["checkpoint"]["blobSha"]
    assert hashlib.sha256(checkpoint_text.encode("utf-8")).hexdigest() == relation["checkpoint"]["textSha256"]
    for phrase in ("33 профильных Atlas-ID", "6 профильных функциональных схем", "29 машиночитаемых схемных обозначений", "не дают сами по себе полномочий"):
        assert phrase in checkpoint_text, phrase

    indices = tuple(load(path) for path in INDICES)
    source_paths = relation["sourcePaths"]
    atlas = document(indices, source_paths["atlasVariant"])["sourceObject"]
    electronic_cards = document(indices, source_paths["atlasCardsElectronic"])["sourceObject"]
    preheat_cards = document(indices, source_paths["atlasCardsPreheatRemote"])["sourceObject"]
    schemes = document(indices, source_paths["schemes"])["sourceObject"]
    designations = document(indices, source_paths["designations"])["sourceObject"]
    stage2_sources = document(indices, source_paths["stage2Sources"])["sourceObject"]

    counts = relation["counts"]
    assert len(atlas["systems"]) == counts["profileSystems"]
    assert len(atlas["equipment"]) == counts["profileAtlasIds"]
    cards = electronic_cards["records"] + preheat_cards["records"]
    assert len(cards) == counts["profileAtlasCards"]
    assert {item["id"] for item in cards} == {item["id"] for item in atlas["equipment"]}
    assert all(item["applicability"] == ["ЧМЭ3Э"] for item in atlas["equipment"])

    assert [item["id"] for item in schemes["records"]] == relation["profileSchemeIds"]
    assert len(schemes["records"]) == counts["profileSchemes"]
    external_preheat = next(item for item in schemes["records"] if item["id"] == "CHME3E-SCH-PREHEAT-EXTERNAL")
    assert external_preheat["actionAuthority"] == "INFORMATION_ONLY"
    assert external_preheat["safetyNote"] == relation["externalPreheatSafetyNote"]
    assert len(designations["electrical"]) == counts["schemeDesignations"]
    assert len(stage2_sources["sources"]) == counts["stage2SourceRecords"]
    assert len(stage2_sources["sources"]) + 4 == counts["combinedStage1And2SourceRecords"]

    active_values = strings(atlas) | strings(electronic_cards) | strings(preheat_cards) | strings(schemes)
    for forbidden_id in relation["forbiddenChme3tIds"]:
        assert forbidden_id not in active_values, forbidden_id

    print("CHME3E_STAGE2_CHECKPOINT_PASS 3 33 33 6 29 5")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args()
    check()
