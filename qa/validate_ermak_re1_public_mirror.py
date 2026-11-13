#!/usr/bin/env python3
"""Historical RE1 mirror is not an automatically verified Ermak diagnostic source."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = "docs/migration/ermak-re1-public-mirror-evidence.candidate.json"
AUDIT = "content-packs/electric/ermak/migration/source-audit.json"
TRIAGE = "docs/migration/stage1-source-link-triage.json"
DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
SOURCE_ID = "ER-AUDIT-MFR-RE1-PUBLIC"


def read(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def validate(evidence: dict, audit: dict, triage: dict) -> dict:
    assert all(x["donorCommit"] == DONOR for x in (evidence, audit, triage)), "donor SHA"
    assert evidence["schemaVersion"] == 1
    assert evidence["scope"] == "PUBLICATION_DISCOVERY_ONLY_NO_SOURCE_ID_RESOLUTION"
    assert evidence["targetSourceId"] == SOURCE_ID
    assert evidence["sourceAudit"] == AUDIT and evidence["triageLedger"] == TRIAGE
    ar = [x for x in audit["sourceReferences"] if x["sourceId"] == SOURCE_ID]
    lr = [x for x in triage["ermak"]["sourceIds"] if x["sourceId"] == SOURCE_ID]
    assert len(ar) == len(lr) == 1, "source must be unique"
    assert ar[0]["occurrences"] == lr[0]["occurrences"] == evidence["pinnedUnresolvedOccurrences"] == 56
    assert ar[0]["disposition"] == lr[0]["sourceDisposition"] == evidence["sourceDisposition"] == "SOURCE_GAP"
    assert lr[0]["reviewStatus"] == evidence["reviewStatus"] == "UNRESOLVED_QUARANTINED"
    assert lr[0]["runtimeImport"] is False
    pub = evidence["publication"]
    assert pub["documentId"] == "ИДМБ.661142.009РЭ1"
    assert pub["alternateDocumentId"] == "3ТС.001.012РЭ1"
    assert pub["thirdPartyIndexUrl"] == "https://www.rcit.su/techinfoV5.html"
    assert pub["thirdPartyTextUrl"] == "https://www.rcit.su/techinfoV51.html"
    assert pub["indexStatesValidOn"] == "2007-11-01"
    assert pub["describedControlSystem"] == "МСУД-Н"
    assert pub["candidateLocomotiveSeries"] == ["2ЭС5К", "3ЭС5К"]
    assert pub["provenanceClass"] == "THIRD_PARTY_MIRROR_OF_HISTORICAL_TECHNICAL_PUBLICATION"
    assert len(pub["relevantSections"]) == 2
    assert "МСУД-Н" in pub["relevantSections"][1]
    assert evidence["publicationStatus"] == "CANDIDATE"
    assert evidence["actionDisposition"] == "INFORMATION_ONLY"
    for key in (
        "runtimeImport", "sourceIdResolved", "originalDocumentMatchedToSourceId",
        "officialCurrentEditionVerified", "exactClausesMapped",
        "executionApplicabilityVerified", "msud015ApplicabilityVerified",
        "crewActionAuthorized",
    ):
        assert evidence[key] is False, "unsafe source promotion: " + key
    assert len(evidence["requiredEvidence"]) == 4
    return {"targetSourceId": SOURCE_ID, "unresolvedOccurrences": 56,
            "historicalControlSystem": "МСУД-Н", "runtimeImport": False,
            "sourceIdResolved": False}


if __name__ == "__main__":
    print(json.dumps(validate(read(EVIDENCE), read(AUDIT), read(TRIAGE)),
                     ensure_ascii=False, sort_keys=True))
