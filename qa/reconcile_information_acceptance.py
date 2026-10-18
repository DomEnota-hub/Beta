#!/usr/bin/env python3
"""Check the boundaries of the data-first acceptance inventory.

Counts here describe source accounting, not operational publication or UI import.
"""

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs/data-migration"


def rows(name):
    return json.loads((AUDIT / name).read_text())["rows"]


def key(row):
    return (row["sourcePath"], row["sourceObjectId"], row["sourceArtifactGitBlob"])


def check():
    discovery = rows("source-discovery-ledger.json")
    counts = Counter(row["disposition"] for row in discovery)
    assert counts == {"PENDING_MAPPING": 206, "PENDING_EXTRACTION": 254,
                      "DEFERRED_SCOPE": 208, "DUPLICATE_SOURCE_MIRROR": 169}
    assert len(discovery) == len({key(row) for row in discovery}) == 837

    mapped = [*rows("technical-discovery-evidence.json"),
              *rows("document-discovery-evidence.json"),
              *rows("remaining-pending-mapping-evidence.json")]
    assert len(mapped) == 206
    assert {key(row) for row in mapped} == {
        key(row) for row in discovery if row["disposition"] == "PENDING_MAPPING"}
    extraction = rows("pending-extraction-review.json")
    assert len(extraction) == 254
    assert {key(row) for row in extraction} == {
        key(row) for row in discovery if row["disposition"] == "PENDING_EXTRACTION"}
    assert all(row["remainingGate"] and row["finalObjectDisposition"] is None
               for row in extraction)

    objects = rows("document-object-ledger.json")
    assert len(objects) == 1748
    # The exact 13-map, pointer/hash/destination bijection is verified by the
    # independent qa/validate_locomotive_document_coverage.py gate.
    references = json.loads((ROOT / "content-packs/common/knowledge/migration/embedded-reference-cards.candidate.json").read_text())["entries"]
    assert len(references) == 18
    assert all(not item["runtimeImport"] and not item["actionAuthorityGranted"]
               and item["requiresWarnedExtendedMode"] for item in references)
    historical = json.loads((ROOT / "content-packs/locomotive-migration/migration/historical-section-index.candidate.json").read_text())
    assert historical["documentCount"] == len(historical["documents"]) == 50
    assert historical["sectionCount"] == sum(len(d["sections"]) for d in historical["documents"]) == 351
    assert not historical["runtimeImport"] and not historical["actionAuthorityGranted"]
    phases = json.loads((AUDIT / "historical-document-phase-review.json").read_text())
    assert phases["phaseCounts"] == {"DIAGNOSTIC_STAGE": 29, "INFORMATION_REVIEW": 12,
                                     "MIXED_OBJECT_REVIEW": 5, "SEPARATE_UI_STAGE": 4}
    assert {d["sourcePath"] for d in historical["documents"]} == {
        d["sourcePath"] for d in phases["rows"]}
    mixed = json.loads((AUDIT / "mixed-historical-section-review.json").read_text())
    assert mixed["phaseCounts"] == {
        "ASSISTANT_STAGE": 3, "DIAGNOSTIC_STAGE": 3, "INFORMATION_REVIEW": 14,
        "MIXED_REVIEW": 10, "QA_CONTEXT": 3, "SEPARATE_UI_STAGE": 1,
        "SOURCE_CONTEXT": 8}
    assert len(mixed["rows"]) == 42
    assertions = json.loads((AUDIT / "mixed-historical-assertion-review.json").read_text())
    assert assertions["sectionCount"] == 10
    assert assertions["assertionLineCount"] == len(assertions["rows"]) == 64
    assert assertions["phaseCounts"] == {
        "ACCEPTANCE_REVIEW": 5, "ASSISTANT_STAGE": 4, "DIAGNOSTIC_STAGE": 8,
        "FUNCTIONAL_STAGE": 3, "INFORMATION_EVIDENCE_REVIEW": 10,
        "QA_CONTEXT": 4, "SAFETY_POLICY_CONTEXT": 6, "SOURCE_CONTEXT": 20,
        "UI_STAGE": 4}
    acceptance_audits = json.loads((AUDIT / "historical-acceptance-audit-relations.json").read_text())
    assert len(acceptance_audits["audits"]) == 2
    assert [len(s["requiredIds"]) for s in acceptance_audits["preservedItemSets"]] == [15, 18]
    assert [len(s["expandedIds"]) for s in acceptance_audits["preservedItemSets"]] == [66, 111]
    assert not acceptance_audits["currentRequirednessVerified"]
    vl_required = json.loads((ROOT / "content-packs/electric/vl80s/acceptance/migration/kotlin-required.candidate.json").read_text())
    assert len(vl_required["requiredChecks"]) == 15
    assert len(vl_required["expandedRouteIdsFromSource"]) == 7
    assert not vl_required["currentRequirednessVerified"] and not vl_required["runtimeImport"]
    package_b = json.loads((AUDIT / "package-b-checkpoint-relations.json").read_text())
    assert (package_b["sequenceCount"], package_b["stepCount"], package_b["layoutCount"]) == (55, 145, 55)
    assert not package_b["runtimeImport"] and not package_b["actionAuthorityGranted"]
    replay = json.loads((AUDIT / "family-generator-replay.json").read_text())
    assert len(replay["outputs"]) == 26
    assert len({r["donorBlobSha"] for r in replay["outputs"]}) == 13
    assert not replay["runtimeImport"] and not replay["currentAuthorityVerified"]
    tem2_history = json.loads((AUDIT / "tem2-information-checkpoint-relations.json").read_text())
    assert len(tem2_history["checkpoints"]) == 2
    assert tem2_history["sourceObjectCounts"] == {"systems": 9, "equipment": 36,
            "schemes": 9, "flows": 11, "flowNodes": 42, "coreChecks": 14,
            "profileChecks": 2, "routes": 2}
    assert not tem2_history["runtimeImport"] and not tem2_history["actionAuthorityGranted"]
    chme3_history = json.loads((AUDIT / "chme3-legacy-atlas-checkpoint-relations.json").read_text())
    assert chme3_history["counts"] == {"sourceRecords": 16, "systems": 13,
            "equipment": 70, "detailCards": 70, "functionalSchemes": 12,
            "schemeDesignations": 24}
    assert len(chme3_history["distinctEquipmentIds"]) == 2
    assert not chme3_history["runtimeImport"] and not chme3_history["actionAuthorityGranted"]
    normal_source = json.loads((ROOT / "content-packs/electric/vl80s/technical-data/migration/kotlin-normal-values.candidate.json").read_text())
    assert len(normal_source["rows"]) == 6
    assert all(not x["currentAuthorityVerified"] for x in normal_source["rows"])
    assert not normal_source["runtimeImport"] and not normal_source["actionAuthorityGranted"]
    raw = json.loads((ROOT / "content-packs/diesel/chme3-family/migration/raw-target-evidence.candidate.json").read_text())
    # Its detailed source/variant/object hash checks live in reconcile_chme3_raw_targets.
    assert raw["runtimeImport"] is False
    print("INFORMATION_ACCEPTANCE_ACCOUNTING_PASS 837 206 254 1748 18 351")


if __name__ == "__main__":
    check()
