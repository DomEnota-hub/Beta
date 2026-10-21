#!/usr/bin/env python3
"""Prepublication Stage 4 pilot review. Never activates locomotive instructions."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PILOTS={
 "vl80s.diag.pantograph-no-rise":
 "content-packs/electric/vl80s/diagnostics/authoring/stage4-pantograph.research.json",
 "chme3.diagnostics.chme3-diag-110":
 "content-packs/diesel/chme3-family/diagnostics/authoring/stage4-rheostatic.research.json",
}
DONOR="3176d6ee228f0ed4b78371f45209e10c1c724eff"

def require(condition, label):
    if not condition:
        raise ValueError(label)

def load(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))

def check_graph(route, anchors, sources):
    require(route["authoringStatus"]=="RESEARCH_DRAFT_BLOCKED", "premature approval")
    nodes=route["nodes"]
    by={n["id"]:n for n in nodes}
    require(len(nodes)==len(by) and route["startNodeId"] in by, "invalid graph IDs")
    terminals=set()
    reverse={name:set() for name in by}
    for node in nodes:
        require(node.get("permittedAction") is False, "operation in research graph")
        require(node["donorAnchors"] and set(node["donorAnchors"])<=anchors,
                "node lacks exact donor anchor")
        require(node["sourceRefs"] and set(node["sourceRefs"])<=sources,
                "source reference not declared")
        if node["type"]=="QUESTION":
            require(set(node["responses"])=={"YES","NO","UNKNOWN"}, "incomplete branch")
            require(node["responses"]["YES"]!=node["responses"]["NO"],
                    "YES/NO is not discriminating")
            require(all(target in by for target in node["responses"].values()), "broken target")
            require(by[node["responses"]["UNKNOWN"]]["type"]=="STOP",
                    "unknown must stop without inferring cause")
            for target in node["responses"].values(): reverse[target].add(node["id"])
        else:
            require(node["type"] in ("STOP","OBSERVATION_REPORT"), "invalid terminal")
            require(node["responses"]=={} and node.get("causeConfirmed") is False,
                    "terminal contains unjustified diagnosis")
            terminals.add(node["id"])
    reached={route["startNodeId"]}
    todo=list(reached)
    while todo:
        for target in by[todo.pop()]["responses"].values():
            if target not in reached: reached.add(target);todo.append(target)
    require(reached==set(by), "unreachable pilot node")
    can_end=set(terminals);todo=list(terminals)
    while todo:
        for previous in reverse[todo.pop()]:
            if previous not in can_end: can_end.add(previous);todo.append(previous)
    require(can_end==set(by), "non-terminating pilot graph")
    return len(nodes)

def check_pilot(record, inventory_row, stage2):
    require(record["scenarioId"]==inventory_row["scenarioId"], "wrong scenario")
    require(record["originalId"]==inventory_row["sourceScenarioId"], "donor identity mismatch")
    # VL80S canonical inventory preserves DiagnosticRepository.scenarios, while
    # this pilot intentionally authors against the separately pinned Framework v2
    # reference snapshot from the Stage 2 ledger. Both source identities matter.
    if record["modelId"]=="vl80s":
        expected=stage2["sourceSnapshots"]["vl80sFramework"]
        donor_path=expected["donorPath"]
        donor_blob=expected["donorBlob"]
        require(inventory_row["donorPath"]=="DiagnosticRepository.scenarios",
                "VL80S canonical runtime provenance changed")
    else:
        donor_path=inventory_row["donorPath"]
        donor_blob=inventory_row["donorBlob"]
    require(record["canonicalDonorCommit"]==DONOR and
            record["canonicalDonorBlob"]==donor_blob and
            record["canonicalDonorPath"]==donor_path, "untracked donor source")
    require(record["publicationStatus"]=="CANDIDATE" and
            record["runtimeImport"] is False and
            record["actionAuthorityGranted"] is False and
            record["executable"] is False, "unsafe pilot activation")
    for key in ("exactInstalledProfileConfirmed","installedEquipmentConfirmed",
                "sourceAuthorityVerified","technicalClaimsReviewed","substantiveReviewed"):
        require(record[key] is False, "false claim of approval: "+key)
    require(all(x=="BLOCKED" for k,x in record["acceptance"].items()
                if k in ("sourceCurrency","exactProfile","equipment",
                         "roleActionAuthority","humanSafetyReview","publication")),
            "pilot acceptance promoted")
    trial=next(t for t in stage2["trials"] if t["scenarioId"]==record["scenarioId"])
    anchor_set={a["id"] for a in trial["anchors"]}
    require(set(record["stage2AnchorRefs"])<=anchor_set, "stage 2 anchor mismatch")
    src={s["id"] for s in record["sources"]}
    require(len(src)==len(record["sources"]), "duplicate source")
    require(all(not s.get("currentRevisionVerified",False)
                for s in record["sources"]), "unverified source promoted")
    versions=record["versionDrafts"]
    require(set(versions)=={"SHORT","DETAILED"}, "version set")
    counts={k:check_graph(v,anchor_set,src) for k,v in versions.items()}
    require(record["schemaVersion"]=="diagnostic-authoring-pilot/2",
            "pilot alternative format not migrated")
    warning=record["extendedWarningContract"]
    require(warning=={"offByDefault":True,"readToEndRequired":True,
                     "acknowledgementRequired":True,"acknowledgementGrantsActionAuthority":False},
            "expanded warning is not sufficient")
    for name,v in versions.items():
        if v["extendedSourceStatus"]=="UNBOUND":
            require(v["extendedRoutes"]==[] and bool(v["extendedSourceGapReason"]),
                    "missing evidence gap")
        else:
            require(v["extendedSourceStatus"]=="HISTORICAL_INFORMATION_BOUND"
                    and v["extendedSourceGapReason"] is None and bool(v["extendedRoutes"]),
                    "historical evidence incorrectly marked unbound")
        ids=set()
        focuses=set()
        graph_signatures=set()
        for a in v["extendedRoutes"]:
            require(a["approachId"] not in ids and bool(a["approachId"]), "merged/duplicate approach")
            ids.add(a["approachId"])
            require(a["sourceId"] in src and bool(a["sourcePointer"]), "source provenance missing")
            require(a["alternativeGroup"] and bool(a["approachSummary"]) and
                    bool(a["approachFocus"]) and a["approachFocus"] not in focuses,
                    "alternative focus missing or duplicated")
            focuses.add(a["approachFocus"])
            require(a["displayMode"]=="EXTENDED_ONLY" and
                    a["visibility"]=={"extendedEnabledRequired":True,
                     "warningReadToEndRequired":True,"warningAcknowledgedRequired":True},
                    "unverified source exposed without warning")
            require(a["actionDisposition"]=="INFORMATION_ONLY" and
                    a["operationalInstructionsIncluded"] is False and
                    a["procedureSteps"]==[] and a["executable"] is False and
                    a["actionAuthorityGranted"] is False and
                    a["humanSafetyReviewPassed"] is False,
                    "historical alternative became operational")
            require(a["applicability"]["profileId"]==record["authoringProfileId"] and
                    a["applicability"]["installedVariantConfirmed"] is False and
                    bool(a["applicability"]["limitation"]), "unqualified profile applicability")
            require(a["authoringStatus"]=="RESEARCH_EXTENDED_INFORMATION_ONLY", "extended approval")
            # A second approach cannot silently reuse the same exact graph.
            signature=json.dumps(a["nodes"],sort_keys=True,ensure_ascii=False)
            require(signature not in graph_signatures, "duplicate source approach graph")
            graph_signatures.add(signature)
            # The same structural rules apply to each historical reading route.
            check_graph({**a, "authoringStatus":"RESEARCH_DRAFT_BLOCKED"},anchor_set,src)
    require([a["approachId"] for a in versions["SHORT"]["extendedRoutes"]]!=
            [a["approachId"] for a in versions["DETAILED"]["extendedRoutes"]],
            "extended versions silently share one route")
    require([v["nodes"] for v in versions.values()][0]!=
            [v["nodes"] for v in versions.values()][1], "copied SHORT/DETAILED")
    return counts

def main():
    inventory=load("docs/data-migration/diagnostic-corpus-analysis.json")
    stage2=load("docs/diagnostics/DIAGNOSTIC_AUTHORING_STAGE2_CLAIM_LEDGER.json")
    require(len(inventory["rows"])==340 and inventory["preservedGraphNodes"]==3902,
            "base diagnostic corpus changed")
    require(all(all(row[k]=="NOT_AUTHORED" for k in
                ("shortVersion","detailedVersion","shortExtendedBranch","detailedExtendedBranch"))
                for row in inventory["rows"]), "premature corpus promotion")
    by_id={r["scenarioId"]:r for r in inventory["rows"]}
    result={}
    for scenario,path in PILOTS.items():
        result[scenario]=check_pilot(load(path),by_id[scenario],stage2)
    print("PASS Stage4 research-only pilot graphs. NO executable route or publication:",result)
    return result

if __name__=="__main__":
    main()
