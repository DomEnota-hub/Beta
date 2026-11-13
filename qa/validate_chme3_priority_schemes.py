#!/usr/bin/env python3
"""Check 222 CHME3 priority scheme references against pinned donor objects.

Identity parity is NOT source authority. Never creates executable/runtime links.
"""
import hashlib
import json
from collections import Counter
from pathlib import Path

from qa.validate_stage1_source_link_triage import verify_audit_blobs

ROOT = Path(__file__).resolve().parents[1]
DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
EVIDENCE = "docs/migration/chme3-priority-scheme-evidence.candidate.json"
AUDIT = "content-packs/diesel/chme3-family/migration/source-audit.json"
RAW = "content-packs/diesel/chme3-family/migration/raw-target-evidence.candidate.json"
REMAINING = "content-packs/diesel/chme3-family/migration/remaining-document-source-index.json"
TRIAGE = "docs/migration/stage1-source-link-triage.json"
ORIGINAL_BLOB = "ec31051ec39e0053141d173729913e3abcabd1e5"
VARIANTS = {"chme3": "ЧМЭ3", "chme3t": "ЧМЭ3Т", "chme3e": "ЧМЭ3Э"}
COUNTS = {"CHME3-SCH-PNEUMATIC": 28, "CHME3-SCH-CONTROL": 24,
          "CHME3-SCH-TRACTION": 22}


def read(path, root=ROOT):
    return json.loads((root / path).read_text(encoding="utf-8"))


def object_digest(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def pointer_value(root, pointer):
    assert pointer.startswith("/documents/"), pointer
    current = root
    for part in pointer.split("/")[1:]:
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            assert part.isdecimal(), pointer
            current = current[int(part)]
        else:
            current = current[part]
    return current


def validate(evidence, audit, raw, remaining, triage):
    assert all(doc["donorCommit"] == DONOR
               for doc in (evidence, audit, raw, remaining, triage))
    assert evidence["schemaVersion"] == 1
    assert evidence["scope"] == "PINNED_DONOR_SCHEME_IDENTITY_ONLY"
    assert evidence["publicationStatus"] == "CANDIDATE"
    assert evidence["runtimeImport"] is False
    assert evidence["actionDisposition"] == "INFORMATION_ONLY"
    assert evidence["sourceLinkStatus"] == "UNRESOLVED_QUARANTINED"
    assert all(evidence[k] is False for k in (
        "manufacturerAuthorityVerified", "currentNormativeAuthorityVerified",
        "variantInstallationVerified"))
    assert evidence["sourceAudit"] == AUDIT and evidence["rawEvidence"] == RAW
    assert evidence["originalDocumentSnapshot"] == REMAINING
    assert evidence["originalDocumentPath"] == "docs/locomotives/chme3/atlas_schemes_functional.json"
    assert evidence["originalDocumentGitBlob"] == ORIGINAL_BLOB
    assert evidence["originalDocumentKind"] == "DONOR_AUTHORED_TRAINING_REFERENCE_NOT_MANUFACTURER_SCHEME"
    assert evidence["blockedActions"] == [
        "DO_NOT_CREATE_RUNTIME_LINKS",
        "DO_NOT_ASSUME_COMMON_SCHEME_IS_VARIANT_APPROVED",
        "DO_NOT_PROMOTE_TRAINING_REFERENCE_TO_MANUFACTURER_AUTHORITY",
        "DO_NOT_ISSUE_CREW_REPAIR_ACTIONS",
    ]
    assert raw["publicationStatus"] == "CANDIDATE" and raw["runtimeImport"] is False
    assert raw["counts"] == {"TARGET_PRESERVED_VARIANT_COMPATIBLE": 602,
                              "CROSS_VARIANT_TARGET_NOT_LINKED": 8}
    assert len(raw["crossVariantConflicts"]) == 8
    assert all(x["runtimeLinkCreated"] is False for x in raw["crossVariantConflicts"])
    assert triage["runtimeImport"] is False and triage["actionDisposition"] == "INFORMATION_ONLY"
    assert triage["chme3"]["unresolvedReferenceCount"] == len(audit["unresolvedReferences"]) == 610

    original = [doc for doc in remaining["documents"]
                if doc["sourcePath"] == evidence["originalDocumentPath"]]
    assert len(original) == 1
    assert original[0]["sourceBlobSha"] == ORIGINAL_BLOB
    assert "не заменяют" in original[0]["sourceObject"]["disclaimer"]
    original_document = original[0]["sourceObject"]
    rows = evidence["targetEvidence"]
    assert len(rows) == len(COUNTS) == len({r["targetId"] for r in rows})
    assert {r["targetId"] for r in rows} == set(COUNTS)
    groups = {g["sourceTargetId"]: g for g in triage["chme3"]["targetGroups"]}
    assert len(groups) == 19
    mapping_pairs = {(m["canonicalId"], m["variant"]) for m in audit["mappings"]}
    per_variant = Counter()
    checked_edges = 0

    for row in rows:
        target = row["targetId"]
        per_model = {variant: COUNTS[target] for variant in sorted(VARIANTS)}
        assert row["referenceCountsByVariant"] == per_model, target
        assert row["unresolvedReferenceCount"] == 3 * COUNTS[target], target
        group = groups[target]
        assert group["referenceCount"] == row["unresolvedReferenceCount"]
        assert group["referenceCountsByVariant"] == per_model
        assert group["reviewStatus"] == "UNRESOLVED_QUARANTINED"
        assert group["runtimeImport"] is False
        assert group["variantApplicabilityUnverified"] is False
        assert group["requiredEvidence"] == "PINNED_VARIANT_SPECIFIC_SCHEME_OR_EQUIPMENT_SOURCE"

        preserved = raw["targets"][target]
        assert len(preserved) == 1, target
        pointer = row["originalObjectPointer"]
        expected_path = REMAINING + "#" + pointer
        assert preserved[0]["evidencePath"] == expected_path
        assert preserved[0]["sourceObjectSha256"] == row["originalObjectSha256"]
        obj = pointer_value(remaining, pointer)
        assert obj in original_document["records"], target
        assert obj["id"] == target
        assert obj["applicability"] == list(VARIANTS.values())
        assert preserved[0]["applicability"] == obj["applicability"]
        assert obj["evidenceStatus"] == "TRAINING_REFERENCE"
        assert obj["actionAuthority"] == "INFORMATION_ONLY"
        assert obj["evidenceRefs"] == row["originalEvidenceRefs"]
        assert len(obj["evidenceRefs"]) >= 2
        assert object_digest(obj) == row["originalObjectSha256"], target

        expected_edges = Counter(
            (ref["source"], ref["variant"], ref["sourceTargetId"])
            for ref in audit["unresolvedReferences"] if ref["sourceTargetId"] == target)
        raw_edges = Counter(
            (group["sourceEntryId"], group["sourceVariant"], target)
            for group in raw["sourceGroups"] if target in group["rawTargetIds"])
        assert expected_edges == raw_edges, target
        assert len(expected_edges) == row["unresolvedReferenceCount"], target
        assert all(count == 1 for count in expected_edges.values()), target
        for source, variant, _ in expected_edges:
            assert variant in VARIANTS, variant
            assert (source, variant) in mapping_pairs, (source, variant)
            per_variant[variant] += 1
            checked_edges += 1
    assert checked_edges == evidence["expectedTotalUnresolvedReferences"] == 222
    assert dict(sorted(per_variant.items())) == evidence["expectedPerVariantUnresolvedReferences"]
    assert per_variant == {"chme3": 74, "chme3e": 74, "chme3t": 74}
    return {"priorityTargets": len(rows), "unresolvedReferencesCrossChecked": checked_edges,
            "perVariant": dict(sorted(per_variant.items())),
            "originalObjectDigestsVerified": len(rows),
            "manufacturerAuthorityVerified": False, "runtimeImport": False}


def main():
    evidence, audit, raw, remaining, triage = [
        read(p) for p in (EVIDENCE, AUDIT, RAW, REMAINING, TRIAGE)]
    verified = verify_audit_blobs(ROOT, triage)
    assert verified["chme3"] == "0ba6617d293e101eddbe26da9b976eb8e5555bcf"
    result = validate(evidence, audit, raw, remaining, triage)
    assert not (ROOT / "content-packs/diesel/chme3-family/runtime-index.json").exists()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
