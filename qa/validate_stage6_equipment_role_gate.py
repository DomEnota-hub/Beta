#!/usr/bin/env python3
"""Fail-closed Stage 6 proof-of-installed-equipment and crew-vs-repair role review."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE_PATH = ROOT / "docs/diagnostics/STAGE6_EQUIPMENT_AND_ROLE_GATE_2026-11-04.json"
LEDGER_PATH = ROOT / "docs/diagnostics/STAGE6_HISTORICAL_CLAIM_LEDGER_2026-11-04.json"
ROUTES = {
    "vl80s.diag.gv-no-open":
       "content-packs/electric/vl80s/diagnostics/authoring/stage6-gv-no-open.research.json",
    "vl80s.diag.ekg-slow-transition":
       "content-packs/electric/vl80s/diagnostics/authoring/stage6-ekg-slow-transition.research.json",
}
EXPECTED_CLAIMS = {
    "vl80s.diag.gv-no-open": {"S6-GV-1990-01", "S6-GV-1990-02"},
    "vl80s.diag.ekg-slow-transition": {"S6-EKG-1990-01", "S6-EKG-2005-01"},
}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def check(gate, ledger, routes):
    require(gate["schemaVersion"] == "diagnostic-stage6-equipment-and-role-gate/1"
            and gate["stage"] == "6/51", "wrong source-gate schema")
    require(gate["donorCommit"] == "3176d6ee228f0ed4b78371f45209e10c1c724eff",
            "donor commit drift")
    require(gate["status"] ==
            "SOURCE_SCOPE_REVIEWED_AS_BUILT_EQUIPMENT_AND_CURRENT_AUTHORITY_NOT_VERIFIED"
            and gate["stageReviewStatus"] == "BLOCKED_PENDING_PROFILE_SOURCE_ROLE_AND_UI",
            "source-specific authority falsely approved")
    require(gate["runtimeImport"] is False and gate["executable"] is False
            and gate["actionAuthorityGranted"] is False, "runtime promotion")
    policy = gate["crossCuttingPolicy"]
    expected_policy = (
        "sourcePublicationIsNotProofOfInstalledVariant",
        "historicalFactoryNumberIsNotProofOfInstalledDevice",
        "localDepotInstructionsStillRequired",
        "maintenanceSafetyDocumentIsNotCrewRepairAuthorization",
        "warningAcknowledgementDoesNotGrantActionAuthority",
        "currentFactoryDiagramsRequiredForEquipmentSpecificInstruction",
        "researchVisibilityDoesNotAuthorizeOperatingSteps",
        "noNewOperationsRequested",
    )
    require(all(policy.get(key) is True for key in expected_policy),
            "variant/role policy weakened")
    require(all(value is False for value in gate["currentAuthorityGate"].values()),
            "current approval inferred from an old book")
    require(gate["historicalInformationalVisibility"] ==
            {"offByDefault": True, "warningReadToEndRequired": True,
             "warningAcknowledgedRequired": True, "actionAuthorityGranted": False},
            "warning/read gate bypass")
    src = gate["sources"]
    require(set(src) == {"manual1990","scheme2005","crewSafety2024","maintenanceSafety2025"},
            "incorrect bibliography or regulatory categories")
    manual = src["manual1990"]
    require(manual["identity"]["year"] == 1990 and
            manual["identity"]["isbn"] == "5-277-01048-3" and
            manual["role"] == "HISTORICAL_OPERATION_AND_MAINTENANCE_MANUAL",
            "incorrect archival manual identity")
    scheme = src["scheme2005"]
    require(scheme["identity"]["year"] == 2005
            and scheme["identity"]["isbn"] == "5-89035-204-0"
            and scheme["identity"]["printedScanTitle"] !=
                scheme["identity"]["publisherCatalogTitle"]
            and scheme["bibliographicTitleDiscrepancy"] ==
                "SOURCE_CATALOG_SAYS_VL80_WHILE_PRINTED_SCAN_SAYS_VL80S_MAINTAIN_BOTH_VARIANTS",
            "lost publisher/scanned edition distinction")
    crew = src["crewSafety2024"]
    maintenance = src["maintenanceSafety2025"]
    require(crew["identity"]["number"] == "ИОТ РЖД-4100612-ЦТ-273-2022"
            and crew["identity"]["publicVerifiedRevision"] ==
                "Распоряжение от 23.12.2024 №3228/р"
            and crew["role"] == "LOCOMOTIVE_CREW_SAFETY_REQUIREMENTS"
            and crew["localDepotInstructionsChecked"] is False
            and crew["crewRepairProcedureAuthorized"] is False,
            "crew rules incorrectly applied")
    require(maintenance["identity"]["number"] == "ПОТ РЖД-4100612-ЦТР-342-2025"
            and maintenance["role"] == "MAINTENANCE_AND_REPAIR_WORKER_REQUIREMENTS"
            and maintenance["verifiedCrewOperationAuthority"] is False,
            "TO/TR rules confer no automatic locomotive crew permission")
    for source in src.values():
        require(source["url"].startswith("https://"), "invalid bibliography URL")
        require(source["grantsActionAuthority"] is False,
                "source identity is not a procedure permit")
    require(manual["provesCurrentEdition"] is False and
            manual["provesInstalledEquipment"] is False and
            scheme["provesCurrentEdition"] is False and
            scheme["provesInstalledEquipment"] is False and
            crew["completeCurrentApplicabilityVerified"] is False and
            maintenance["completeCurrentApplicabilityVerified"] is False,
            "modern equipment or current standards invented")
    require({item["scenarioId"] for item in gate["cases"]} == set(ROUTES)
            and len(gate["cases"]) == 2, "cross-series scenario ID drift")
    known_claims = {x["claimId"] for x in ledger["claims"]}
    require(known_claims == set().union(*EXPECTED_CLAIMS.values()), "claim ledger altered")
    for item in gate["cases"]:
        scenario = item["scenarioId"]
        require(item["originalId"] == scenario.removeprefix("vl80s.diag."),
                "original seeded ID changed")
        require(set(item["historicalClaimIds"]) == EXPECTED_CLAIMS[scenario],
                "claim identity provenance lost")
        require(item["matchedHistoricalComponentFaultProven"] is False
                and item["historicalHypothesesInformationOnly"] is True,
                "component failure inferred from archival description")
        require(item["installedPositionIndicator"] == "UNKNOWN_NOT_INFERRED"
                and item["installedProtectionRelay"] == "UNKNOWN_NOT_INFERRED"
                if scenario.endswith("ekg-slow-transition") else
                item["installedSwitchType"] == "UNKNOWN_NOT_INFERRED",
                "installed gear was assumed")
        require(item["verifiedSerialNumber"] is None
                and item["verifiedAsBuiltDiagram"] is None
                and item["verifiedEquipmentMarking"] is None,
                "unknown machine fabricated")
        require(len(item["requiredEvidence"]) >= 4
                and all(bool(x) for x in item["requiredEvidence"]),
                "profile verification requirements discarded")
        draft = routes[scenario]
        require(draft["scenarioId"] == scenario
                and draft["runtimeImport"] is False
                and draft["publicationStatus"] == "CANDIDATE"
                and draft["actionAuthorityGranted"] is False,
                "source gate disconnected from research-only scenario")
        mapped = {a.get("claimId") for a in draft["versions"]["DETAILED"]["extendedRoutes"]
                  if a.get("claimId")}
        require(mapped == EXPECTED_CLAIMS[scenario],
                "specific historical claim IDs not mapped to DETAILED")
    ekg = next(x for x in gate["cases"] if x["scenarioId"].endswith("ekg-slow-transition"))
    variant = ekg["indicatorHistoricalTransition"]
    require(variant["documentedFactoryNumberLowerBound"] == 1897
            and variant["documentedModelFromNumber"] == "УП-1"
            and variant["previousModelMentioned"] == "УП-5"
            and variant["explicitlyInterchangeable"] is True
            and variant["factoryNumberIsInstalledEquipmentProof"] is False
            and variant["automaticIndicatorModelAssignment"] is False,
            "historical serial threshold misread as installed equipment")
    require(ekg["relayHistoricalReference"]["name"] == "204"
            and ekg["relayHistoricalReference"]["bindingToCurrentInstalledScheme"] ==
                "NOT_VERIFIED", "historic relay assigned to modern locomotive")
    gv = next(x for x in gate["cases"] if x["scenarioId"].endswith("gv-no-open"))
    require(gv["historicalEquipmentReference"]["type"] == "ВОВ-25А-10/400УХЛ1"
            and gv["observedFaultVsSourceFault"] ==
                "DIFFERENT_DESCRIPTIONS_REQUIRE_CAUSAL_AND_EQUIPMENT_REVIEW",
            "GV source table falsely treated as installed switch diagnosis")
    require(ledger["stageTechnicalAcceptance"] == "BLOCKED"
            and ledger["runtimeImport"] is False,
            "historical source ledger promoted")
    return {"cases": len(gate["cases"]), "historicalClaims": len(known_claims),
            "roles": [crew["role"], maintenance["role"]]}

if __name__ == "__main__":
    j = json.loads(GATE_PATH.read_text(encoding="utf-8"))
    l = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    routes = {k: json.loads((ROOT/p).read_text(encoding="utf-8")) for k,p in ROUTES.items()}
    print("PASS Stage 6 installed-equipment/crew-role fail-closed gate:", check(j,l,routes))
