#!/usr/bin/env python3
"""Check 996/р bibliographic evidence without resolving a diagnostic source ID.

The 2024 amendment is not the original date of order 996/р. This check
intentionally preserves every source gap until official text, amendment status,
exact clause, series and execution have been reviewed.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = "docs/migration/ermak-996r-edition-evidence.candidate.json"
AUDIT = "content-packs/electric/ermak/migration/source-audit.json"
TRIAGE = "docs/migration/stage1-source-link-triage.json"
DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
SOURCE_ID = "ER-AUDIT-NORM-996R-2024"


def load(root: Path, name: str) -> dict:
    return json.loads((root / name).read_text(encoding="utf-8"))


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def validate(evidence: dict, audit: dict, triage: dict) -> dict:
    require(all(d["donorCommit"] == DONOR for d in (evidence, audit, triage)),
            "donor SHA drift")
    require(evidence["schemaVersion"] == 1, "schema drift")
    require(evidence["scope"] == "BIBLIOGRAPHIC_IDENTITY_ONLY_NOT_OPERATIONAL_AUTHORITY",
            "scope must remain bibliographic")
    require(evidence["targetSourceId"] == SOURCE_ID, "target identity drift")
    require(evidence["sourceAudit"] == AUDIT and evidence["triageLedger"] == TRIAGE,
            "unrecognized source registries")
    matches = [r for r in audit["sourceReferences"] if r["sourceId"] == SOURCE_ID]
    ledger = [r for r in triage["ermak"]["sourceIds"] if r["sourceId"] == SOURCE_ID]
    require(len(matches) == len(ledger) == 1, "source must be unique in both ledgers")
    require(matches[0]["disposition"] == ledger[0]["sourceDisposition"] ==
            evidence["sourceDisposition"] == "SOURCE_GAP", "gap was silently resolved")
    require(matches[0]["occurrences"] == ledger[0]["occurrences"] ==
            evidence["pinnedUnresolvedOccurrences"] == 57, "occurrence count drift")
    require(ledger[0]["reviewStatus"] == "UNRESOLVED_QUARANTINED" and
            ledger[0]["runtimeImport"] is False, "source ledger promoted")
    require(evidence["originalDocument"]["orderNumber"] == "996/р" and
            evidence["originalDocument"]["orderDate"] == "2022-04-12", "original order identity drift")
    require(evidence["knownAmendment"]["orderNumber"] == "592/р" and
            evidence["knownAmendment"]["orderDate"] == "2024-03-05", "amendment identity drift")
    locator = evidence["evidenceLocator"]
    require(locator["kind"] == "SECONDARY_PUBLISHER_CATALOG_BIBLIOGRAPHIC_ENTRY" and
            locator["url"].startswith("https://urizdat.ru/books/"), "bibliography provenance drift")
    require(evidence["publicationStatus"] == "CANDIDATE" and
            evidence["actionDisposition"] == "INFORMATION_ONLY", "unsafe disposition")
    for key in ("runtimeImport", "currentEditionVerified", "officialFullTextVerified",
                "perSeriesClauseVerified", "applicabilityToExecutionVerified",
                "sourceIdResolved", "crewActionAuthorized"):
        require(evidence[key] is False, "unverified authority or publication: " + key)
    return {"sourceId": SOURCE_ID, "unresolvedOccurrences": 57,
            "originalOrder": "996/р (2022-04-12)", "amendment": "592/р (2024-03-05)",
            "runtimeImport": False, "sourceResolved": False}


if __name__ == "__main__":
    print(json.dumps(validate(load(ROOT, EVIDENCE), load(ROOT, AUDIT),
                              load(ROOT, TRIAGE)), ensure_ascii=False, sort_keys=True))
