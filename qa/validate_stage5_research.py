#!/usr/bin/env python3
"""Stage 5 drafts: structural and provenance preflight, not normative clearance."""
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [
    "content-packs/electric/vl80s/diagnostics/authoring/stage5-gv-no-close.research.json.gz",
    "content-packs/electric/vl80s/diagnostics/authoring/stage5-ekg-stuck.research.json.gz",
]
DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
INVENTORY = "docs/data-migration/diagnostic-corpus-analysis.json"
DOSSIER = "docs/diagnostics/DIAGNOSTIC_AUTHORING_STAGE5_SOURCE_VARIATION.json"

def require(ok, msg):
    if not ok:
        raise ValueError(msg)

def load(path):
    with gzip.open(ROOT / path, "rt", encoding="utf-8") as file:
        return json.load(file)

def graph_check(nodes, start, source_ids):
    ids = [n["id"] for n in nodes]
    require(len(ids) == len(set(ids)) and start in ids, "duplicate IDs / no start")
    by_id = {n["id"]: n for n in nodes}
    require(any(n["type"] == "STOP" for n in nodes), "STOP missing")
    terminal = set()
    reverse = {id: set() for id in ids}
    for node in nodes:
        require(node["operationRequested"] is False, "forbidden operational step")
        require(node["sourceRefs"] and set(node["sourceRefs"]) <= source_ids,
                "invalid source provenance")
        if node["type"] == "QUESTION":
            edges = node["responses"]
            require(set(edges) == {"YES", "NO", "UNKNOWN"}, "incomplete answer triplet")
            require(edges["YES"] != edges["NO"], "nondiscriminating branch")
            require(all(x in by_id for x in edges.values()), "invalid graph target")
            require(by_id[edges["UNKNOWN"]]["type"] == "STOP", "UNKNOWN cannot advance")
            for target in edges.values():
                reverse[target].add(node["id"])
        else:
            require(node["type"] in {"STOP", "OBSERVATION_REPORT"}, "invalid leaf")
            require(node["responses"] == {} and node["causeConfirmed"] is False,
                    "invented confirmed fault")
            terminal.add(node["id"])
    seen = {start}
    todo = [start]
    while todo:
        for target in by_id[todo.pop()]["responses"].values():
            if target not in seen:
                seen.add(target)
                todo.append(target)
    require(seen == set(ids), "unreachable diagnostic node")
    can_end = set(terminal)
    todo = list(terminal)
    while todo:
        for previous in reverse[todo.pop()]:
            if previous not in can_end:
                can_end.add(previous)
                todo.append(previous)
    require(can_end == set(ids), "graph contains a nonterminating region")

def validate(d):
    require(d["schemaVersion"] == "diagnostic-research-stage5/2", "old draft format")
    require(d["publicationStatus"] == "CANDIDATE" and d["runtimeImport"] is False
            and d["executable"] is False and d["actionAuthorityGranted"] is False,
            "draft published as active")
    require(d["betaHeadReverified"] is False, "historical offline audit overwritten")
    require(d["sourceAuthorityVerified"] is False and d["substantiveSafetyReviewed"] is False
            and d["exactInstalledVariantConfirmed"] is False, "false authority assertion")
    require(d["safetyNoOperations"] is True, "unsafe operation gate changed")
    require(d["historicalVisibility"] == {"default": "HIDDEN", "extendedEnabled": True,
            "warningReadToEnd": True, "warningAcknowledged": True,
            "actionPermissionGrantedByWarning": False}, "warning contract degraded")
    require(d["donorPinnedSha"] == DONOR
            and d["baselineSource"] == "DiagnosticRepository.scenarios", "donor drift")
    audit = d["integrationAudit"]
    require(audit["verifiedBaseGitHead"] == "849922427b3a0bab66468c1bd2a27b12e3989a37"
            and audit["donorCorpusScenarioCount"] == 340
            and audit["donorCorpusNodes"] == 3902
            and audit["actualRuntimeGraphCompared"] is False
            and audit["researchDraftOnly"] is True, "integration falsely claims approval")
    sources = d["sourceRecords"]
    require(bool(sources), "empty bibliography")
    for key, source in sources.items():
        require(source["id"] == key and source["url"].startswith("https://")
                and bool(source["section"]), "invalid source identity")
        require(source["authorityForCurrentLocomotive"] is False
                and source["safeToExecuteHistoricalProcedures"] is False
                and source["proceduralTextImported"] is False,
                "historical source promoted to action")
    focus = set()
    approaches = set()
    for version in ("short", "detailed"):
        group_focus = set()
        route = d[version]
        require(route["status"] == "RESEARCH_DRAFT_BLOCKED", "premature version acceptance")
        graph_check(route["nodes"], route["startNodeId"], set(sources))
        require(bool(route["extendedRoutes"]), "lost historical alternatives")
        for alt in route["extendedRoutes"]:
            require(alt["approachId"] not in approaches, "duplicate approach ID")
            approaches.add(alt["approachId"])
            require(alt["sourceId"] in sources and alt["version"] == version.upper(),
                    "wrong source or version")
            require(sources[alt["sourceId"]]["usableForScenario"] is True,
                    "source unrelated to this scenario")
            require(alt["actionDisposition"] == "INFORMATION_ONLY"
                    and alt["publicationStatus"] == "CANDIDATE"
                    and alt["executable"] is False
                    and alt["operationalSteps"] == [], "historical procedure imported")
            require(alt["technicalClaimReview"] == "REQUIRES_EXPERT", "invented claim review")
            require(alt["visibility"] == {"extendedEnabled": True,
                    "warningReadToEnd": True, "warningAcknowledged": True},
                    "warning bypass")
            require(alt["applicability"]["exactEquipmentProfileConfirmed"] is False,
                    "unverified variant allowed")
            graph_check(alt["nodes"], alt["startNodeId"], set(sources))
            require(all(alt["sourceId"] in n["sourceRefs"] for n in alt["nodes"]),
                    "branch/source mismatch")
            require(alt["approachFocus"] not in group_focus,
                    "two URLs substituted for method diversity")
            group_focus.add(alt["approachFocus"])
            focus.add(alt["approachFocus"])
        require(len(group_focus) >= 2, "independent historical approaches missing")
    require(d["short"]["nodes"] != d["detailed"]["nodes"], "SHORT copied into DETAILED")
    require(len(focus) >= 3, "methods not varied")
    if d["scenarioId"] == "vl80s.diag.gv-no-close":
        require(sources["gv2018"]["usableForScenario"] is False
                and sources["gv2018"]["claimScopeStatus"] == "SOURCE_SECTION_MISMATCH_UNRESOLVED",
                "2018 GV provenance error restored")
    elif d["scenarioId"] == "vl80s.diag.ekg-stuck":
        require(sources["ekgdepot"]["claimScopeStatus"] == "EXACT_LOCAL_CLAUSE_UNVERIFIED",
                "Bataisk local instruction wrongly verified")
    else:
        raise ValueError("unexpected Stage 5 scenario ID")
    return len(d["short"]["nodes"]), len(d["detailed"]["nodes"]), len(approaches)

def check_canonical(d, inventory, dossier):
    require(inventory["donorCommit"] == DONOR
            and inventory["uniqueScenarioCount"] == 340
            and inventory["preservedGraphNodes"] == 3902, "baseline corpus changed")
    row = next((r for r in inventory["rows"] if r["scenarioId"] == d["scenarioId"]), None)
    require(row and row["sourceScenarioId"] == d["originalId"]
            and row["donorPath"] == d["baselineSource"]
            and row["graph"]["nodeCount"] == d["baselineNodesReportedPreviously"],
            "canonical scenario/source mismatched")
    require(row["variantIds"] == d["otherVariantIds"], "variant list changed")
    require(all(row[k] == "NOT_AUTHORED" for k in (
            "shortVersion", "detailedVersion", "shortExtendedBranch",
            "detailedExtendedBranch")), "runtime corpus accidentally promoted")
    require(dossier["workStatus"] == "FIRST_PAIR_DISCOVERY_ONLY_NOT_STAGE_COMPLETE"
            and dossier["donorCommit"] == DONOR, "Stage 5 dossier overwritten")
    require(any(r["scenarioId"] == d["scenarioId"] for r in dossier["scenarios"]),
            "source dossier lacks scenario")
    require(dossier["integratedResearchReview"]["runtimeImport"] is False,
            "source audit improperly attached to runtime")

def visible_alternatives(d, version, actual_profile, enabled, read_to_end, acknowledged):
    # Research selection semantics, not wired to Android UI.
    if not all((enabled, read_to_end, acknowledged)):
        return []
    if actual_profile != d["authoringProfileId"]:
        return []
    return d[version]["extendedRoutes"]

def main():
    inventory = json.loads((ROOT / INVENTORY).read_text(encoding="utf-8"))
    dossier = json.loads((ROOT / DOSSIER).read_text(encoding="utf-8"))
    result = {}
    for path in PATTERNS:
        d = load(path)
        check_canonical(d, inventory, dossier)
        result[d["scenarioId"]] = validate(d)
    print("PASS Stage5 research-only, runtime UNCHANGED:", result)

if __name__ == "__main__":
    main()
