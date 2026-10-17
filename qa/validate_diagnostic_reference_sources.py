#!/usr/bin/env python3
"""Check complete source snapshots and distinct display/action boundaries."""

import json

from migrate_diagnostic_reference_sources import ROOT, SOURCES, digest

snapshots = {}
for name, (blob, object_hash, destination) in SOURCES.items():
    inventory = json.loads((ROOT / destination).read_text())
    assert inventory["sourcePath"] == f"app/src/main/assets/technical/{name}"
    assert inventory["sourceBlobSha"] == blob
    assert inventory["sourceObjectSha256"] == object_hash == digest(inventory["sourceObject"])
    assert inventory["publicationStatus"] == "CANDIDATE"
    assert inventory["runtimeImport"] is False and inventory["actionAuthorityGranted"] is False
    snapshots[name] = inventory["sourceObject"]

policy = snapshots["extended_emergency_policy.json"]
assert policy["defaultEnabled"] is False
assert policy["runtimeContract"]["standardModeMayEnterExtendedBranch"] is False
assert policy["runtimeContract"]["extendedModeMayUpgradeAuthority"] is False
assert policy["runtimeContract"]["prohibitedStepNeverExecutable"] is True
assert {row["id"] for row in policy["actionDispositions"]} == {
    "INFORMATION_ONLY", "CONDITIONAL_ACTION", "PROHIBITED"}

framework = snapshots["diagnostic_framework_v2.json"]
reference = snapshots["vl80s_pantograph_reference_pack.json"]
assert len(framework["modules"]) == 1
module = framework["modules"][0]
assert (module["scenarioId"], module["profileId"]) == (
    reference["scenarioId"], reference["profileId"])
assert module["referencePackAsset"] == "technical/vl80s_pantograph_reference_pack.json"
assert len(module["nodes"]) == 8
assert len(reference["sourceRegistry"]) == 12
assert len(reference["entries"]) == len({row["id"] for row in reference["entries"]}) == 19
assert reference["productionStatus"] == "REFERENCE_ONLY_PENDING_HUMAN_REVIEW"
assert reference["visibilityContract"]["restrictedGate"] == "EXTENDED_EMERGENCY_SEPARATE_CONSENT"
print("DIAGNOSTIC_REFERENCE_SOURCE_PASS", 1, 8, 12, 19)
