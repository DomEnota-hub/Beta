#!/usr/bin/env python3
"""Verify the other 388 CHME3 source edges; identity is never source authority."""
import json
from collections import Counter
from pathlib import Path

from qa.validate_chme3_priority_schemes import (
    ROOT, DONOR, AUDIT, RAW, REMAINING, TRIAGE, read, object_digest, pointer_value,
)
from qa.validate_stage1_source_link_triage import verify_audit_blobs

EVIDENCE = "docs/migration/chme3-remaining-scheme-evidence.candidate.json"
ATLAS = "content-packs/diesel/chme3-family/migration/atlas-source-index.json"
PRIORITY = {"CHME3-SCH-PNEUMATIC", "CHME3-SCH-CONTROL", "CHME3-SCH-TRACTION"}
VARIANT_NAMES = {"chme3": "ЧМЭ3", "chme3t": "ЧМЭ3Т", "chme3e": "ЧМЭ3Э"}
ALLOWED_BLOBS = {
    "docs/locomotives/chme3/atlas_schemes_extension.json": "9070839292255a28be68043d851d8f89e47948cc",
    "docs/locomotives/chme3/atlas_schemes_functional.json": "ec31051ec39e0053141d173729913e3abcabd1e5",
    "docs/locomotives/diesel/chme3-family/chme3e/schemes_variant.json": "77ecbdd591e5271b78ad4f8e63a3af950e190cc6",
    "docs/locomotives/chme3/atlas_cards_electric_brake.json": "50a11507ad7b28033f2accb345233feae1250fb8",
    "docs/locomotives/chme3/atlas_index.json": "6274dbcbbfdfdd775a44c8dfc5b9af1fc6ca134d",
}


def validate(evidence, audit, raw, remaining, atlas, triage):
    assert all(x["donorCommit"] == DONOR for x in (evidence, audit, raw, remaining, atlas, triage))
    assert evidence["schemaVersion"] == 1
    assert evidence["scope"] == "PINNED_DONOR_REMAINING_SCHEME_IDENTITY_ONLY"
    assert evidence["publicationStatus"] == "CANDIDATE"
    assert evidence["runtimeImport"] is False
    assert evidence["actionDisposition"] == "INFORMATION_ONLY"
    assert evidence["sourceLinkStatus"] == "UNRESOLVED_QUARANTINED"
    assert all(evidence[key] is False for key in (
        "manufacturerAuthorityVerified", "currentNormativeAuthorityVerified", "variantInstallationVerified"))
    assert evidence["sourceAudit"] == AUDIT
    assert evidence["rawEvidence"] == RAW
    assert evidence["remainingDocumentIndex"] == REMAINING
    assert evidence["atlasSourceIndex"] == ATLAS
    assert evidence["triage"] == TRIAGE
    assert evidence["excludedPriorityTargets"] == sorted(PRIORITY)
    assert evidence["blockedActions"] == [
        "DO_NOT_CREATE_RUNTIME_LINKS",
        "DO_NOT_ASSUME_DONOR_APPLICABILITY_IS_MANUFACTURER_APPROVAL",
        "DO_NOT_PROMOTE_TRAINING_REFERENCE_TO_MANUFACTURER_AUTHORITY",
        "DO_NOT_ISSUE_CREW_REPAIR_ACTIONS",
    ]
    assert raw["publicationStatus"] == "CANDIDATE" and raw["runtimeImport"] is False
    assert raw["counts"] == {"TARGET_PRESERVED_VARIANT_COMPATIBLE": 602,
                             "CROSS_VARIANT_TARGET_NOT_LINKED": 8}
    assert triage["runtimeImport"] is False and triage["actionDisposition"] == "INFORMATION_ONLY"
    assert len(audit["unresolvedReferences"]) == triage["chme3"]["unresolvedReferenceCount"] == 610
    assert len(raw["targets"]) == len(triage["chme3"]["targetGroups"]) == 19

    rows = evidence["targetEvidence"]
    expected_ids = set(raw["targets"]) - PRIORITY
    assert len(rows) == evidence["expectedRemainingTargets"] == len(expected_ids) == 16
    assert {r["targetId"] for r in rows} == expected_ids
    groups = {g["sourceTargetId"]: g for g in triage["chme3"]["targetGroups"]}
    assert len(groups) == 19
    mapping_pairs = {(m["canonicalId"], m["variant"]) for m in audit["mappings"]}
    total = 0
    per_variant = Counter()
    cross_variant = Counter()

    for row in rows:
        target = row["targetId"]
        group = groups[target]
        assert group["reviewStatus"] == "UNRESOLVED_QUARANTINED"
        assert group["runtimeImport"] is False
        assert group["requiredEvidence"] in (
            "PINNED_VARIANT_SPECIFIC_SCHEME_OR_EQUIPMENT_SOURCE",
            "EXPLICIT_VARIANT_APPLICABILITY_AND_ORIGINAL_SOURCE",
        )
        assert group["referenceCount"] == row["unresolvedReferenceCount"]
        assert group["referenceCountsByVariant"] == row["referenceCountsByVariant"]
        assert group["variantApplicabilityUnverified"] is row["variantApplicabilityUnverified"]
        assert group["variantMismatch"] is row["variantMismatch"]
        preserved = raw["targets"][target]
        assert len(row["sourceObjects"]) == len(preserved) >= 1
        applicability = set()
        for obj_row, raw_row in zip(row["sourceObjects"], preserved):
            assert obj_row["evidencePath"] == raw_row["evidencePath"]
            assert obj_row["sourceObjectSha256"] == raw_row["sourceObjectSha256"]
            path, pointer = obj_row["evidencePath"].split("#", 1)
            assert path in (REMAINING, ATLAS)
            snapshot = remaining if path == REMAINING else atlas
            obj = pointer_value(snapshot, pointer)
            index = int(pointer.split("/")[2])
            doc = snapshot["documents"][index]
            assert doc["sourcePath"] in ALLOWED_BLOBS
            assert doc["sourceBlobSha"] == obj_row["sourceDocumentBlob"] == ALLOWED_BLOBS[doc["sourcePath"]]
            assert obj["id"] == target
            assert object_digest(obj) == obj_row["sourceObjectSha256"]
            assert obj["applicability"] == obj_row["applicability"] == raw_row["applicability"]
            assert obj.get("evidenceRefs", []) == obj_row["originalEvidenceRefs"]
            assert obj.get("actionAuthority") == obj_row["originalActionAuthority"]
            assert obj.get("evidenceStatus") == obj_row["originalEvidenceStatus"]
            assert obj.get("actionAuthority") in (None, "INFORMATION_ONLY", "REQUIRES_PROFILE_CHECK")
            assert obj.get("evidenceStatus") in (None, "TRAINING_REFERENCE")
            applicability.update(obj["applicability"])

        expected = Counter((r["source"], r["variant"], r["sourceTargetId"])
                           for r in audit["unresolvedReferences"] if r["sourceTargetId"] == target)
        observed = Counter((g["sourceEntryId"], g["sourceVariant"], target)
                           for g in raw["sourceGroups"] if target in g["rawTargetIds"])
        assert expected == observed, target
        assert len(expected) == row["unresolvedReferenceCount"]
        assert all(n == 1 for n in expected.values())
        actual_variants = Counter(variant for _, variant, _ in expected)
        assert dict(sorted(actual_variants.items())) == row["referenceCountsByVariant"]
        for source, variant, _ in expected:
            assert variant in VARIANT_NAMES
            assert (source, variant) in mapping_pairs
            if VARIANT_NAMES[variant] not in applicability:
                cross_variant[(source, variant, target)] += 1
            per_variant[variant] += 1
            total += 1

    original_conflicts = Counter(
        (x["sourceEntryId"], x["sourceVariant"], x["rawTargetId"])
        for x in raw["crossVariantConflicts"])
    assert cross_variant == original_conflicts
    assert sum(cross_variant.values()) == evidence["expectedCrossVariantConflicts"] == 8
    assert total == evidence["expectedRemainingUnresolvedReferences"] == 388
    assert dict(sorted(per_variant.items())) == evidence["expectedPerVariantUnresolvedReferences"]
    assert per_variant == {"chme3": 100, "chme3e": 184, "chme3t": 104}
    return {"remainingTargets": len(rows), "sourceEdgesCrossChecked": total,
            "perVariant": dict(sorted(per_variant.items())),
            "crossVariantConflictsBlocked": sum(cross_variant.values()),
            "sourceObjectsVerified": sum(len(r["sourceObjects"]) for r in rows),
            "manufacturerAuthorityVerified": False, "runtimeImport": False}


def main():
    evidence, audit, raw, remaining, atlas, triage = [
        read(p) for p in (EVIDENCE, AUDIT, RAW, REMAINING, ATLAS, TRIAGE)]
    verified = verify_audit_blobs(ROOT, triage)
    assert verified["chme3"] == "0ba6617d293e101eddbe26da9b976eb8e5555bcf"
    assert not (ROOT / "content-packs/diesel/chme3-family/runtime-index.json").exists()
    print(json.dumps(validate(evidence, audit, raw, remaining, atlas, triage),
                     ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
