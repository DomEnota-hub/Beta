#!/usr/bin/env python3
"""Fail-closed stage-1 structural handoff gate; never certifies runtime content."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
HANDOFF = "docs/migration/stage1-structural-handoff.json"

def read(root, relative):
    return json.loads((root / relative).read_text(encoding="utf-8"))

def validate(handoff, assets, kotlin, triage, root):
    assert handoff["schemaVersion"] == 1
    assert handoff["stage"] == 1 and handoff["handoffToStage"] == 2
    assert handoff["status"] == "STRUCTURAL_INVENTORY_COMPLETE_AUTHORITY_PENDING"
    assert handoff["runtimePublicationApproved"] is False
    assert handoff["donorCommit"] == DONOR
    assert handoff["branch"] == "audit/information-block-gaps-20261014"
    assert assets["donor"]["commit"] == kotlin["donor"]["commit"] == triage["donorCommit"] == DONOR

    scope = handoff["verifiedScope"]
    assert scope["donorAssets"]["ledger"] == "docs/migration/donor-asset-crosswalk.json"
    assert scope["donorMainKotlin"]["ledger"] == "docs/migration/donor-kotlin-crosswalk.json"
    assert scope["sourceLinks"]["ledger"] == "docs/migration/stage1-source-link-triage.json"
    assert len(assets["assets"]) == scope["donorAssets"]["count"] == 36
    assert len(kotlin["sources"]) == scope["donorMainKotlin"]["count"] == 74
    assert len({a["sourcePath"] for a in assets["assets"]}) == 36
    assert len({s["sourcePath"] for s in kotlin["sources"]}) == 74
    assert all(a["runtimePublication"] == "NOT_PROVEN" and a["evidenceWorkflow"]
               for a in assets["assets"])
    assert all(s["status"] in {"PARTIAL", "CONTRACT_ONLY", "NOT_MIGRATED"}
               and s["userJourneyVerified"] is False for s in kotlin["sources"])

    links = scope["sourceLinks"]
    assert triage["scope"] == "SOURCE_IDENTITY_TRIAGE_ONLY"
    assert triage["runtimeImport"] is False
    assert triage["actionDisposition"] == "INFORMATION_ONLY"
    assert links["chme3Unresolved"] == triage["chme3"]["unresolvedReferenceCount"] == 610
    assert links["chme3Targets"] == len(triage["chme3"]["targetGroups"]) == 19
    assert links["ermakUnresolvedOccurrences"] == triage["ermak"]["unresolvedOccurrenceCount"] == 548
    assert links["ermakSourceIds"] == len(triage["ermak"]["sourceIds"]) == 57
    assert all(x["reviewStatus"] == "UNRESOLVED_QUARANTINED" and x["runtimeImport"] is False
               for x in triage["chme3"]["targetGroups"] + triage["ermak"]["sourceIds"])
    assert not (root / "content-packs/diesel/chme3-family/runtime-index.json").exists()
    assert not (root / "content-packs/electric/ermak/runtime-index.json").exists()

    backlog = handoff["openBacklog"]
    expected = {"SRC-CHME3-610": 610, "SRC-ERMAK-548": 548,
                "SRC-ER-DIAG-136": 1, "SRC-EXAM-329": 329,
                "MIG-HISTORY": 1, "SRC-CHME3T-6245": 1}
    assert {x["id"]: x["count"] for x in backlog} == expected
    assert all(x["owner"] and x["requiredEvidence"] and
               x["blocksIndependentShellWork"] is False for x in backlog)
    assert all(x["blocksRuntimePublication"] is True for x in backlog
               if x["id"] != "MIG-HISTORY")
    assert "NOT certified" in handoff["handoffPolicy"]
    return {"stage": 1, "status": handoff["status"],
            "donorAssets": 36, "donorKotlin": 74,
            "chme3Quarantined": 610, "ermakQuarantinedOccurrences": 548,
            "openBacklog": len(backlog), "nextStage": 2,
            "runtimePublicationApproved": False}

def main():
    handoff = read(ROOT, HANDOFF)
    result = validate(handoff,
                      read(ROOT, handoff["verifiedScope"]["donorAssets"]["ledger"]),
                      read(ROOT, handoff["verifiedScope"]["donorMainKotlin"]["ledger"]),
                      read(ROOT, handoff["verifiedScope"]["sourceLinks"]["ledger"]),
                      ROOT)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))

if __name__ == "__main__":
    main()
