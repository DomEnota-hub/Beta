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
    require(route["extendedRoutes"]==[] and route["extendedSourceStatus"]=="UNBOUND"
            and bool(route["extendedSourceGapReason"]), "extended gap silently inherited")
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
    require(record["canonicalDonorCommit"]==DONOR and
            record["canonicalDonorBlob"]==inventory_row["donorBlob"] and
            record["canonicalDonorPath"]==inventory_row["donorPath"], "untracked donor source")
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
