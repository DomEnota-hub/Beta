#!/usr/bin/env python3
"""Check third-party CHME3 drawing catalog leads without granting source authority."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = "docs/migration/chme3-public-drawing-leads.candidate.json"
TRIAGE = "docs/migration/stage1-source-link-triage.json"
DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
EXPECTED = {
    "CHME3T-2012-GIF-ARCHIVE": (
        "chme3t",
        "https://lokomotivishim.ucoz.ru/load/skhemy_teplovoza/chmeh3_v_s/chmeh3t_skhemy_ehlektricheskie/163-1-0-1802",
        {"CHME3-SCH-CONTROL", "CHME3-SCH-TRACTION", "CHME3T-SCH-EDB"}),
    "CHME3E-2012-GIF-ARCHIVE": (
        "chme3e",
        "https://lokomotivishim.ucoz.ru/load/skhemy_teplovoza/chmeh3_v_s/chmeh3eh_skhema_ehlektricheskaja/163-1-0-1803",
        {"CHME3-SCH-CONTROL", "CHME3-SCH-TRACTION", "CHME3E-SCH-TRACTION-CONTROL"}),
}
GATES = [
    "ACQUIRE_AND_HASH_ORIGINAL_DOCUMENT",
    "IDENTIFY_ISSUER_DOCUMENT_NUMBER_REVISION_AND_SHEET",
    "VERIFY_VARIANT_SERIAL_AND_MODERNIZATION_APPLICABILITY",
    "VERIFY_ACTION_AUTHORITY_AND_SAFETY_GATE",
]


def read(path, root=ROOT):
    return json.loads((root / path).read_text(encoding="utf-8"))


def validate(ledger, triage):
    assert ledger["schemaVersion"] == 1
    assert ledger["donorCommit"] == triage["donorCommit"] == DONOR
    assert ledger["scope"] == "PUBLIC_ARCHIVE_CATALOG_LEADS_NOT_FACTORY_SOURCE_AUTHORITY"
    assert ledger["publicationStatus"] == "CANDIDATE"
    assert ledger["sourceLinkStatus"] == "UNRESOLVED_QUARANTINED"
    for key in ("runtimeImport", "manufacturerAuthorityVerified",
                "exactDocumentRevisionVerified", "unitApplicabilityVerified",
                "crewActionAuthorized", "sourceFilesAcquired"):
        assert ledger[key] is False, key
    assert ledger["requiredBeforePromotion"] == GATES
    assert ledger["originalUnresolvedChme3References"] == 610
    assert ledger["remainingUnresolvedChme3References"] == 610
    assert triage["chme3"]["unresolvedReferenceCount"] == 610
    assert triage["runtimeImport"] is False
    groups = {g["sourceTargetId"]: g for g in triage["chme3"]["targetGroups"]}
    assert len(groups) == 19
    leads = ledger["leads"]
    assert len(leads) == len(EXPECTED)
    assert {x["id"] for x in leads} == set(EXPECTED)
    for lead in leads:
        variant, url, targets = EXPECTED[lead["id"]]
        assert lead["variant"] == variant
        assert lead["catalogPage"] == url
        assert lead["catalogDate"] == "2012-07-31"
        assert lead["advertisedFormat"] == "RAR_GIF"
        assert lead["status"] == "CATALOG_ENTRY_ONLY_NOT_DOWNLOADED"
        assert set(lead["investigationTargetIds"]) == targets
        assert len(lead["investigationTargetIds"]) == len(targets)
        for target in targets:
            assert target in groups
            assert groups[target]["referenceCountsByVariant"].get(variant, 0) > 0
            assert groups[target]["reviewStatus"] == "UNRESOLVED_QUARANTINED"
            assert groups[target]["runtimeImport"] is False
        for field in ("originalArchiveSha256", "issuer", "documentNumber",
                      "revision", "serialApplicability"):
            assert lead[field] is None, (lead["id"], field)
        assert lead["sheetNumbers"] == []
        for field in ("manufacturerAuthorityVerified", "crewActionAuthorized", "runtimeImport"):
            assert lead[field] is False, (lead["id"], field)
    return {"catalogLeads": len(leads), "candidateTargetLookups": sum(
        len(x["investigationTargetIds"]) for x in leads),
        "unresolvedChme3": 610, "runtimeImport": False}


if __name__ == "__main__":
    print(json.dumps(validate(read(LEDGER), read(TRIAGE)), sort_keys=True))
