#!/usr/bin/env python3
"""Guard the bounded, non-runtime relation for historical CHME3 Stage 2 interactivity."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def historical_document(path: str) -> dict:
    archive = load("content-packs/locomotive-migration/migration/historical-documents.candidate.json")
    matches = [document for document in archive["documents"] if document["sourcePath"] == path]
    assert len(matches) == 1, matches
    return matches[0]


def check() -> None:
    relation = load("docs/data-migration/chme3-interactive-stage2-checkpoint-relations.json")
    assert relation["publicationStatus"] == "CANDIDATE"
    assert relation["runtimeImport"] is False
    assert relation["currentAuthorityVerified"] is False
    assert relation["actionAuthorityGranted"] is False
    assert relation["historicalRuntimeClaimsDisposition"] == (
        "NOT_REIFIED_NO_BOUNDED_INTERACTIVE_RUNTIME_SOURCE"
    )

    checkpoint = historical_document(relation["checkpoint"]["path"])
    assert checkpoint["sourceBlobSha"] == relation["checkpoint"]["blobSha"]
    text = checkpoint["exactSourceText"]
    assert hashlib.sha256(text.encode("utf-8")).hexdigest() == relation["checkpoint"]["textSha256"]
    for phrase in (
        "SEMANTIC_CANVAS",
        "SOURCE_OVERLAY",
        "38 views, 261 hotspot, 215 directed edges",
        "ещё не integration-ready",
    ):
        assert phrase in text, phrase

    source_index = load(relation["profileSourceIndex"])
    assert source_index["publicationStatus"] == "CANDIDATE"
    assert source_index["runtimeImport"] is False
    assert source_index["actionDisposition"] == "INFORMATION_ONLY"
    assert list(source_index["profileBindings"]) == relation["profileIds"]

    manifest = next(
        document["sourceObject"]
        for document in source_index["documents"]
        if document["sourcePath"].endswith("family_manifest.json")
    )
    assert manifest["integrationBoundary"]["androidRuntimeIntegrated"] is False
    assert manifest["integrationBoundary"]["assistantEngineMerged"] is False
    assert manifest["inheritancePolicy"]["unknownExecution"] == (
        "When actual equipment or modernization is unknown, variant-dependent actions fail closed."
    )

    pair_pack = load(relation["sourcePairPack"])
    entries = pair_pack["entries"]
    counts = Counter()
    typed_counts = Counter()
    for entry in entries:
        assert entry["publicationStatus"] == "CANDIDATE"
        assert entry["actionDisposition"] == "INFORMATION_ONLY"
        source_object = entry["sourceObject"]["object"]
        for profile_id in source_object["applicability"]["profileIds"]:
            if profile_id in relation["profileIds"]:
                counts[profile_id] += 1
                typed_counts[(profile_id, entry["id"].split(".")[2])] += 1

    expected_entries = {
        profile_id: pair_count * 2
        for profile_id, pair_count in relation["preservedFunctionalPairCounts"].items()
    }
    assert dict(counts) == expected_entries
    for profile_id, pair_count in relation["preservedFunctionalPairCounts"].items():
        assert typed_counts[(profile_id, "sequence")] == pair_count
        assert typed_counts[(profile_id, "layout")] == pair_count

    assert relation["historicalRuntimeClaims"] == {
        "historicalEffectiveViews": 38,
        "historicalHotspots": 261,
        "historicalDirectedEdges": 215,
    }
    print("CHME3_INTERACTIVE_STAGE2_CHECKPOINT_PASS 3 29 38 261 215")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        check()


if __name__ == "__main__":
    main()
