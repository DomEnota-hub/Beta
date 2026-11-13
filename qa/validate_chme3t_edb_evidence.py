#!/usr/bin/env python3
"""Fail-closed CHME3T EDB historical evidence gate; never authorizes runtime actions."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = "docs/migration/chme3t-edb-historical-evidence.candidate.json"
TRIAGE = "docs/migration/stage1-source-link-triage.json"
RAW = "content-packs/diesel/chme3-family/migration/raw-target-evidence.candidate.json"
DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
TARGETS = {"CHME3T-EQ-EDB-CONTROL", "CHME3T-SCH-EDB"}
URL = "https://www.booksite.ru/tyaga/1989/1989_3.pdf"
SOURCE_ID = "CHME3T-ETT-1989-03-NOTIK-EDB"
ALLOWED_DOCUMENTS = {
    "content-packs/diesel/chme3-family/migration/atlas-source-index.json",
    "content-packs/diesel/chme3-family/migration/remaining-document-source-index.json",
}


def read(path, root=ROOT):
    return json.loads((root / path).read_text(encoding="utf-8"))


def digest(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def pointer_value(document, pointer):
    assert pointer.startswith("/documents/"), pointer
    node = document
    for token in pointer.split("/")[1:]:
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(node, list):
            assert token.isdecimal()
            node = node[int(token)]
        else:
            node = node[token]
    return node


def validate(evidence, triage, raw, documents):
    assert all(item["donorCommit"] == DONOR for item in (evidence, triage, raw))
    assert evidence["schemaVersion"] == 1
    assert evidence["scope"] == "HISTORICAL_TECHNICAL_EVIDENCE_ONLY"
    assert evidence["publicationStatus"] == "CANDIDATE"
    assert evidence["runtimeImport"] is False
    assert evidence["actionDisposition"] == "INFORMATION_ONLY"
    for key in ("manufacturerAuthorityVerified", "currentNormativeAuthorityVerified",
                "installedEquipmentVerified", "variantApplicabilityVerified"):
        assert evidence[key] is False, key
    assert evidence["reviewStatus"] == "HISTORICAL_EVIDENCE_LOCATED_PENDING_MANUFACTURER_CONFIRMATION"
    assert evidence["approvalNeeded"] == "MANUFACTURER_SCHEME_AND_VARIANT_INSTALLATION_EVIDENCE"

    source = evidence["source"]
    assert source["id"] == SOURCE_ID
    assert source["url"] == URL
    assert source["author"] == "З. Х. Нотик"
    assert source["year"] == 1989 and source["issue"] == 3
    assert source["evidenceType"] == "HISTORICAL_TECHNICAL_PERIODICAL_NOT_FACTORY_MANUAL"
    assert source["sourceScope"] == ["chme3t"]
    assert sorted(source["notAutomaticallyApplicableTo"]) == ["chme3", "chme3e"]
    assert source["printedPages"] == [21, 22, 23, 24, 25]
    assert "рис. 14" in source["verifiedLocator"]
    assert len(source["limitations"]) >= 4
    manual = evidence["supplementalTechnicalManual"]
    assert manual["id"] == "CHME3-IO-2004-EDB-SECTION"
    assert manual["editionDate"] == "2004-12-31"
    assert manual["url"] == "https://y-pad.tv/wp-content/uploads/2021/11/Rukovodstvo_TO_TR_CHME3.pdf"
    assert manual["editionStatus"] == "ORIGINAL_2004_EDITION_LOCATED_CURRENTNESS_NOT_VERIFIED"
    assert manual["officialMaintenanceDocument"] is True
    assert manual["manufacturerManual"] is False
    assert manual["currentEditionVerified"] is False
    assert manual["installedEquipmentVerified"] is False
    assert manual["crewActionAuthority"] is False
    assert manual["repairOperationsNotForCrew"] is True
    assert manual["verifiedFor"] == ["chme3t"]
    assert sorted(manual["notAutomaticallyApplicableTo"]) == ["chme3", "chme3e"]
    assert {(item["section"], item["printedPage"]) for item in manual["locators"]} == {
        ("3.3.4", 56), ("3.3.5", 57), ("7.3.7", 79)}
    assert set(source["claimsSupported"]) == {
        "CHME3T_RHEOSTATIC_BRAKING_HISTORICAL_CIRCUIT_EXISTS",
        "CHME3T_BRAKING_CONTROL_CONTACTORS_DESCRIBED",
    }

    assert raw["publicationStatus"] == "CANDIDATE" and raw["runtimeImport"] is False
    assert raw["counts"] == {
        "TARGET_PRESERVED_VARIANT_COMPATIBLE": 602,
        "CROSS_VARIANT_TARGET_NOT_LINKED": 8,
    }
    assert evidence["crossVariantConflictsExpected"] == len(raw["crossVariantConflicts"]) == 8
    assert evidence["originalUnresolvedChme3References"] == 610
    assert evidence["remainingUnresolvedChme3References"] == 610
    for conflict in raw["crossVariantConflicts"]:
        assert conflict["rawTargetId"] in TARGETS
        assert conflict["sourceVariant"] in ("chme3", "chme3e")
        assert conflict["runtimeLinkCreated"] is False

    rows = evidence["targetEvidence"]
    assert len(rows) == len(TARGETS)
    assert {row["targetId"] for row in rows} == TARGETS
    triage_rows = {x["sourceTargetId"]: x for x in triage["chme3"]["targetGroups"]}
    assert triage["chme3"]["unresolvedReferenceCount"] == 610
    for row in rows:
        target = row["targetId"]
        group = triage_rows[target]
        assert group["reviewStatus"] == "UNRESOLVED_QUARANTINED"
        assert group["runtimeImport"] is False
        assert group["variantApplicabilityUnverified"] is True
        assert row["unresolvedReferenceCount"] == group["referenceCount"]
        assert row["unresolvedVariants"] == group["variants"]
        assert row["sourceLinkResolved"] is False
        assert row["variantApplicabilityVerified"] is False
        assert row["runtimeImport"] is False
        expected = raw["targets"][target]
        pointers = row["preservedDonorObjectPointers"]
        assert len(pointers) == len(expected)
        assert pointers == [
            {key: obj[key] for key in ("evidencePath", "sourceObjectSha256", "applicability")}
            for obj in expected
        ]
        for item in pointers:
            assert item["applicability"] == ["ЧМЭ3Т"], target
            path, sep, pointer = item["evidencePath"].partition("#")
            assert sep and path in ALLOWED_DOCUMENTS
            assert path in documents, path
            obj = pointer_value(documents[path], pointer)
            assert obj["id"] == target
            assert obj["applicability"] == ["ЧМЭ3Т"]
            assert digest(obj) == item["sourceObjectSha256"]
    return {"historicalEvidenceCandidates": len(rows), "sourceObjectPointersVerified": sum(
        len(row["preservedDonorObjectPointers"]) for row in rows),
        "crossVariantConflictsStillBlocked": 8, "chme3UnresolvedReferences": 610,
        "runtimeImport": False}


def main():
    documents = {path: read(path) for path in ALLOWED_DOCUMENTS}
    result = validate(read(EVIDENCE), read(TRIAGE), read(RAW), documents)
    assert not (ROOT / "content-packs/diesel/chme3-family/runtime-index.json").exists()
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
