#!/usr/bin/env python3
"""Verify complete extended candidate preservation and warned display boundary."""

import json
from collections import Counter

from migrate_extended_emergency_source import (
    DESTINATIONS, METADATA, ROOT, ROOT_SHA256, SOURCE_PATH, SOURCE_SHA, digest,
)

overlay = json.loads((ROOT / "docs/data-migration/extended-emergency-source-dispositions.json").read_text())
expected = {row["sourcePointer"]: row for row in overlay["rows"]}
assert len(expected) == 169
metadata = json.loads(METADATA.read_text())
assert metadata["sourcePath"] == SOURCE_PATH and metadata["sourceBlobSha"] == SOURCE_SHA
assert metadata["sourceRootSha256"] == digest(metadata["sourceRootWithoutRoutesAndRecords"]) == ROOT_SHA256
assert metadata["publicationStatus"] == "CANDIDATE" and metadata["runtimeImport"] is False
seen = set()
dispositions = Counter()
routes = {}
records = {}
allowed_profiles = {
    "chme3-family": {"chme3-base", "chme3t-rheostatic", "chme3e-electronic"},
    "tem2-family": {"tem2-base", "tem2u-improved"},
}
for owner, path in DESTINATIONS.items():
    inventory = json.loads(path.read_text())
    assert inventory["modelOwnerGuess"] == owner
    assert inventory["sourcePath"] == SOURCE_PATH and inventory["sourceBlobSha"] == SOURCE_SHA
    assert inventory["publicationStatus"] == "CANDIDATE" and inventory["runtimeImport"] is False
    assert inventory["requiresWarnedExtendedMode"] is True
    assert inventory["actionAuthorityGranted"] is False
    for row in inventory["rows"]:
        pointer = row["sourcePointer"]
        assert pointer in expected and pointer not in seen
        original = expected[pointer]
        assert original["ownerGuess"] == owner
        assert row["sourceId"] == original["sourceId"]
        assert row["sourceObjectSha256"] == original["sourceObjectSha256"] == digest(row["sourceObject"])
        assert row["canonicalId"] is None
        if pointer.startswith("/records/"):
            dispositions[original["actionDisposition"]] += 1
            obj = row["sourceObject"]
            assert obj["actionDisposition"] == original["actionDisposition"]
            assert obj["candidateId"] not in records
            assert set(obj["profiles"]) and set(obj["profiles"]) <= allowed_profiles[owner]
            assert obj["runtimeSafety"] == {
                "currentAuthorityVerified": False,
                "exactProfileOnly": True,
                "executable": False,
                "procedureVisible": False,
                "runtimeAuthorityUpgradeAllowed": False,
            }
            assert obj["sources"] and all(
                source["title"] and source["provenanceLabel"] and source["statusLabel"]
                for source in obj["sources"])
            records[obj["candidateId"]] = (owner, obj)
        else:
            obj = row["sourceObject"]
            assert obj["standardScenarioId"] not in routes
            routes[obj["standardScenarioId"]] = (owner, obj)
        seen.add(pointer)
    assert len(inventory["rows"]) == {"chme3-family": 122, "tem2-family": 47}[owner]
assert seen == set(expected)
assert dispositions == {"INFORMATION_ONLY": 49, "PROHIBITED": 28}
assert len(routes) == 92 and len(records) == 77
record_scenarios = Counter(obj["standardScenarioId"] for _, obj in records.values())
assert Counter(record_scenarios.values()) == {1: 75, 2: 1}
for scenario_id, (owner, route) in routes.items():
    assert route["hasExpandedEvidence"] == (scenario_id in record_scenarios)
    assert route["discoveryStatus"] == (
        "FOUND" if scenario_id in record_scenarios else "NO_ADDITIONAL_METHOD_FOUND")
for owner, record in records.values():
    assert routes[record["standardScenarioId"]][0] == owner
print("EXTENDED_EMERGENCY_SOURCE_PASS", 92, 77, dict(dispositions))
