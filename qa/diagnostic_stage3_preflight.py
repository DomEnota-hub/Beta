#!/usr/bin/env python3
"""Stage 3 authoring preflight: candidate evidence stays non-operational.

This is NOT a railway normative validator. Fixtures are synthetic.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
VERSIONS = ("shortVersion", "detailedVersion", "shortExtendedBranch", "detailedExtendedBranch")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def validate_claim(claim):
    """Return REVIEW_REQUIRED or BLOCKED_SOURCE, never operational permission."""
    require(claim.get("publicationStatus") == "CANDIDATE", "authoring must stay candidate")
    require(claim.get("runtimeImport") is False, "authoring must not import runtime")
    require(claim.get("actionAuthorityGranted") is False, "authoring cannot grant actions")
    require(isinstance(claim.get("claimId"), str) and bool(claim["claimId"].strip()),
            "claim identity required")

    state = claim.get("evidenceState")
    require(state in ("UNBOUND", "SOURCE_BACKED_DRAFT"), "explicit evidence state required")
    if state == "UNBOUND":
        require(claim.get("source") is None, "unbound claim cannot masquerade as source-backed")
        require(bool(claim.get("sourceGapReason")), "unbound claim requires a source gap")
        require(claim.get("actionDisposition") != "CONDITIONAL_ACTION",
                "source gap cannot offer a conditional action")
        return "BLOCKED_SOURCE"

    src = claim.get("source")
    require(isinstance(src, dict), "source-backed draft requires source")
    required_text = (
        "sourceId", "documentRevision", "clauseOrPage", "documentRole",
        "sourceProfileId", "sourceEquipmentId", "relation",
    )
    for field in required_text:
        require(isinstance(src.get(field), str) and bool(src[field].strip()),
                "missing source field: " + field)
    for field in ("exactProfileId", "installedEquipmentId", "userRole"):
        require(isinstance(claim.get(field), str) and bool(claim[field].strip()),
                "missing claim field: " + field)
    require(claim.get("actionDisposition") in
            ("INFORMATION_ONLY", "CONDITIONAL_ACTION", "PROHIBITED"),
            "unknown action disposition")

    # Direct, current source + exact profile/equipment/role are all necessary.
    # Successful preflight can only send a claim to independent human review.
    if (src["relation"] != "CLAUSE_VERIFIED"
            or src["documentRole"] != claim["userRole"]
            or src["sourceProfileId"] != claim["exactProfileId"]
            or src["sourceEquipmentId"] != claim["installedEquipmentId"]
            or not src.get("currentRevisionVerified", False)
            or not src.get("sourceAuthorityVerified", False)
            or not claim.get("installedEquipmentConfirmed", False)
            or claim["actionDisposition"] == "PROHIBITED"):
        return "BLOCKED_SOURCE"
    return "REVIEW_REQUIRED"


def validate_preserved_baseline(root=ROOT):
    def read(path):
        return json.loads((root / path).read_text(encoding="utf-8"))

    inventory = read("docs/data-migration/diagnostic-corpus-analysis.json")
    ledger = read("docs/diagnostics/DIAGNOSTIC_AUTHORING_STAGE2_CLAIM_LEDGER.json")
    rows = inventory["rows"]
    require(inventory["donorCommit"] == DONOR, "inventory donor SHA changed")
    require(len(rows) == inventory["uniqueScenarioCount"] == 340, "340 scenario identities changed")
    require(sum(r["graph"]["nodeCount"] for r in rows) == 3902, "preserved nodes changed")
    require(len({r["scenarioId"] for r in rows}) == 340, "duplicate canonical IDs")
    require(all(all(r[k] == "NOT_AUTHORED" for k in VERSIONS) for r in rows),
            "candidate version promoted without authoring/approval")
    require(ledger["donorCommit"] == DONOR, "claim ledger donor SHA changed")
    require(ledger["publicationStatus"] == "CANDIDATE"
            and ledger["runtimeImport"] is False
            and ledger["actionAuthorityGranted"] is False, "pilot ledger promoted")
    require(len(ledger["trials"]) == 2, "pilot trial set changed")
    anchors = [a for trial in ledger["trials"] for a in trial["anchors"]]
    require(len(anchors) == 52, "52 pilot anchors changed")
    require(all(a["decision"] == "RESEARCH_ONLY_NO_EXECUTABLE_AUTHORITY"
                for a in anchors), "donor anchor promoted")
    require(any(x["check"] == "SOURCE_ROLE_MISMATCH"
                for x in ledger["externalSourceChecks"]), "known role mismatch erased")
    return {"scenarios": 340, "nodes": 3902, "pilotAnchors": 52, "publication": "BLOCKED"}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    result = validate_preserved_baseline()
    print("PASS Stage 3 authoring baseline; operational publication remains BLOCKED:", result)
