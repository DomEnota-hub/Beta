#!/usr/bin/env python3
"""Historical CHME3T serial boundary gate; no runtime source authorization."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = "docs/migration/chme3t-serial-revision-evidence.candidate.json"
AUDIT = "content-packs/diesel/chme3-family/migration/source-audit.json"
TRIAGE = "docs/migration/stage1-source-link-triage.json"
PRIORITY = "docs/migration/chme3-priority-scheme-evidence.candidate.json"
REMAINING = "docs/migration/chme3-remaining-scheme-evidence.candidate.json"
DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
EXPECTED = {"CHME3-SCH-CONTROL": 24, "CHME3-SCH-TRACTION": 22,
            "CHME3T-SCH-EDB": 8}
BLOCKED = [
    "DO_NOT_INFER_APPLICABILITY_FROM_SERIES_ONLY",
    "DO_NOT_ASSUME_6245_BOUNDARY_IS_CURRENT_FACTORY_AUTHORITY",
    "DO_NOT_PROMOTE_SHARED_TRAINING_SCHEMES",
    "DO_NOT_ISSUE_CREW_REPAIR_ACTIONS",
    "DO_NOT_CREATE_RUNTIME_LINKS",
]


def read(path, root=ROOT):
    return json.loads((root / path).read_text(encoding="utf-8"))


def validate(evidence, audit, triage, priority, remaining):
    assert all(x["donorCommit"] == DONOR
               for x in (evidence, audit, triage, priority, remaining))
    assert evidence["schemaVersion"] == 1
    assert evidence["scope"] == "HISTORICAL_CHME3T_SERIAL_ELECTRICAL_REVISION_RISK_ONLY"
    assert evidence["publicationStatus"] == "CANDIDATE"
    assert evidence["sourceLinkStatus"] == "UNRESOLVED_QUARANTINED"
    assert evidence["actionDisposition"] == "INFORMATION_ONLY"
    for field in ("runtimeImport", "manufacturerAuthorityVerified",
                  "currentNormativeAuthorityVerified", "variantInstallationVerified",
                  "serialApplicabilityVerified", "crewActionAuthorized"):
        assert evidence[field] is False, field
    assert evidence["blockedActions"] == BLOCKED
    assert evidence["requiredBeforeRuntime"] == [
        "CONFIRM_EXACT_CHME3T_UNIT_SERIAL_AND_MODERNIZATION",
        "OBTAIN_APPLICABLE_MANUFACTURER_DRAWING_AND_REVISION",
        "VERIFY_EXACT_SHEET_AND_EQUIPMENT_INSTALLATION",
        "REVIEW_CREW_AUTHORITY_AND_SAFETY_GATE",
    ]
    source = evidence["source"]
    assert source["id"] == "CHME3-SRC-NOTIK-1996"
    assert source["year"] == 1996 and source["pages"] == 444
    assert source["evidenceKind"] == "HISTORICAL_SECONDARY_TECHNICAL_BOOK_NOT_FACTORY_DRAWING"
    assert source["url"] == "https://pomogala.ru/books_4_teplovoz/notik_chme3_96.html"
    assert source["bibliographyCrossCheck"] == "https://dntb-centr.ru/b/424"
    assert len(source["locators"]) == 4
    assert "№6245" in source["locators"][0]
    revision = source["revisionSignal"]
    assert revision["model"] == "chme3t"
    assert type(revision["electricalCircuitChangesFromSerial"]) is int
    assert revision["electricalCircuitChangesFromSerial"] == 6245
    assert revision["applicability"] == "HISTORICAL_PUBLICATION_CLAIM_ONLY"
    assert revision["originalFactoryRevisionVerified"] is False
    assert revision["modernizationsExcludedFromInference"] is True
    assert evidence["originalUnresolvedChme3References"] == 610
    assert evidence["remainingUnresolvedChme3References"] == 610
    assert evidence["crossVariantEDBConflictsStillBlocked"] == 8
    assert len(audit["unresolvedReferences"]) == triage["chme3"]["unresolvedReferenceCount"] == 610
    assert triage["runtimeImport"] is False
    assert priority["runtimeImport"] is False and remaining["runtimeImport"] is False
    assert priority["manufacturerAuthorityVerified"] is False
    assert remaining["manufacturerAuthorityVerified"] is False
    assert remaining["expectedCrossVariantConflicts"] == 8
    assert {row["targetId"]: row["chme3tUnresolvedReferences"]
            for row in evidence["affectedTargets"]} == EXPECTED
    assert len(evidence["affectedTargets"]) == len(EXPECTED)
    assert evidence["expectedAffectedChme3tReferences"] == sum(EXPECTED.values()) == 54
    groups = {g["sourceTargetId"]: g for g in triage["chme3"]["targetGroups"]}
    priority_rows = {r["targetId"]: r for r in priority["targetEvidence"]}
    remaining_rows = {r["targetId"]: r for r in remaining["targetEvidence"]}
    for target, count in EXPECTED.items():
        actual = Counter(r["sourceTargetId"] for r in audit["unresolvedReferences"]
                         if r["variant"] == "chme3t")
        assert actual[target] == count, target
        group = groups[target]
        assert group["referenceCountsByVariant"]["chme3t"] == count
        assert group["reviewStatus"] == "UNRESOLVED_QUARANTINED"
        assert group["runtimeImport"] is False
        if target in priority_rows:
            assert "CHME3-SRC-NOTIK-1996" in priority_rows[target]["originalEvidenceRefs"]
        else:
            assert target in remaining_rows
            assert any("CHME3-SRC-NOTIK-1996" in obj["originalEvidenceRefs"]
                       for obj in remaining_rows[target]["sourceObjects"])
    assert "CHME3T-EQ-EDB-CONTROL" in remaining_rows
    assert remaining_rows["CHME3T-EQ-EDB-CONTROL"]["variantMismatch"] is True
    return {"historicalBoundary": 6245, "chme3tElectricalEdgesProtected": 54,
            "unresolvedChme3": 610, "runtimeImport": False}


def main():
    evidence, audit, triage, priority, remaining = [
        read(path) for path in (EVIDENCE, AUDIT, TRIAGE, PRIORITY, REMAINING)]
    result = validate(evidence, audit, triage, priority, remaining)
    assert not (ROOT / "content-packs/diesel/chme3-family/runtime-index.json").exists()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
