#!/usr/bin/env python3
"""Validate every trial donor claim anchor against pinned source snapshots.

Source/bibliographic presence and review statuses DO NOT authorize railway actions.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DONOR="3176d6ee228f0ed4b78371f45209e10c1c724eff"
LEDGER=ROOT/"docs/diagnostics/DIAGNOSTIC_AUTHORING_STAGE2_CLAIM_LEDGER.json"

def read(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))

def check(ok,msg):
    if not ok: raise AssertionError(msg)

def main():
    d=read(LEDGER.relative_to(ROOT))
    check(d["donorCommit"]==DONOR and d["publicationStatus"]=="CANDIDATE"
          and d["runtimeImport"] is False and d["actionAuthorityGranted"] is False,
          "Unsafe or unpinned research ledger")
    snap=d["sourceSnapshots"]
    for name,record in snap.items():
        if name=="chme3tStage3Doc":
            continue  # Read-only donor Stage-3 path, not a Beta file
        b=read(record["betaPath"])
        if name=="chme3tRuntime":
            check("entries" in b and "manifest" in b,
                  "CHME3T source is not a canonical model pack")
            continue  # Model pack has its own manifest and sourceObject wrappers
        check(b["donorCommit"]==DONOR and b["sourcePath"]==record["donorPath"]
              and b["sourceBlobSha"]==record["donorBlob"] and
              b["runtimeImport"] is False and b["actionAuthorityGranted"] is False,
              name+": provenance / candidate gate changed")
    framework=read(snap["vl80sFramework"]["betaPath"])["sourceObject"]["modules"]
    module=next(x for x in framework if x["scenarioId"]=="pantograph-no-rise")
    refpack=read(snap["vl80sReference"]["betaPath"])["sourceObject"]
    pack=read(snap["chme3tRuntime"]["betaPath"])["entries"]
    scenario=next(x for x in pack if x["sourceObject"]["object"]["id"]=="CHME3-DIAG-110")
    donor_graph=scenario["sourceObject"]["object"]["graph"]
    check(scenario["publicationStatus"]=="CANDIDATE" and
          scenario["applicability"]["variantIds"]==["chme3t"] and
          scenario["sourceObject"]["sourceBlobSha"]==snap["chme3tRuntime"]["donorBlob"],
          "CHME3T profile or snapshot changed")
    sup=read(snap["chme3tSupplement"]["betaPath"])
    ext=next(x["sourceObject"] for x in sup["rows"]
             if x["sourceId"]=="EXT2-CHME3-DIAG-110" and
             x["sourcePointer"].startswith("/records/"))
    check(ext["standardScenarioId"]=="CHME3-DIAG-110" and
          ext["profiles"]==["chme3t-rheostatic"] and
          ext["actionDisposition"]=="INFORMATION_ONLY" and
          ext["runtimeSafety"]["executable"] is False and
          ext["runtimeSafety"]["currentAuthorityVerified"] is False,
          "CHME3T extended evidence became executable or cross-profile")
    expected={
       "vl80s.diag.pantograph-no-rise":(
         {"FRAMEWORK_NODE":{x["id"] for x in module["nodes"]},
          "REFERENCE_ENTRY":{x["id"] for x in refpack["entries"]}},
         "vl80s-general"),
       "chme3.diagnostics.chme3-diag-110":(
         {"DONOR_GRAPH_NODE":{x["id"] for x in donor_graph["nodes"]},
          "EXTENDED_SOURCE_CANDIDATE":{"EXT2-CHME3-DIAG-110"}},
         "chme3t-rheostatic")
    }
    check(len(d["trials"])==2,"Expected two proof-of-process scenarios")
    check(set(x["scenarioId"] for x in d["trials"])==set(expected),
          "Scenario identities changed")
    check(len(d["externalSourceChecks"])==4,"External observations changed; review required")
    id_to_source={x["id"]:x for x in refpack["sourceRegistry"]}
    ext_sources={x["sourceRef"]:x for x in ext["sources"]}
    seen=set()
    for o in d["externalSourceChecks"]:
        check(o["id"] not in seen and o["limitation"] and
              o["check"] not in ("CURRENT_RULE_VERIFIED","ACTION_AUTHORIZED"),
              "External citation treated as action authority")
        seen.add(o["id"])
        ref=o["linkedRegistrySource"]
        if ref in id_to_source:
            check(id_to_source[ref]["url"]==o["url"], "Pantograph source URL mismatch")
        else:
            check(ref in ext_sources and ext_sources[ref]["url"]==o["url"],
                  "Extended source URL mismatch")
    check(next(x for x in d["externalSourceChecks"] if
               x["id"]=="external-roof-s12-document-mismatch")["check"]=="SOURCE_ROLE_MISMATCH",
          "Cross-profession safety reference mismatch concealed")
    for scenario in d["trials"]:
        sid=scenario["scenarioId"]; exp,profile=expected[sid]
        check(scenario["exactProfile"]==profile and len(scenario["sourceGaps"])>0,
              sid+": exact profile or missing-source state lost")
        versions=scenario["versions"]
        check(versions=={"short":"NOT_AUTHORED","detailed":"NOT_AUTHORED",
              "shortExtended":"UNBOUND","detailedExtended":"UNBOUND"},
              sid+": fabricated completed routes")
        got={}
        for x in scenario["anchors"]:
            check(x["decision"]=="RESEARCH_ONLY_NO_EXECUTABLE_AUTHORITY" and
                  x["status"] not in ("APPROVED","CURRENT_RULE_VERIFIED","EXECUTABLE")
                  and x["comment"],sid+": unauthorized claim status")
            got.setdefault(x["kind"],set())
            check(x["id"] not in got[x["kind"]],sid+": duplicate claim anchor")
            got[x["kind"]].add(x["id"])
            if x["kind"]=="REFERENCE_ENTRY":
                src=next(i for i in refpack["entries"] if i["id"]==x["id"])
                check(x["sourceRefs"]==src["sourceRefs"] and
                      x["classification"]==src["classification"] and
                      x["donorQuality"]==src["qualityControl"]["reviewStatus"],
                      sid+": donor provenance/quality overwritten")
                check(set(x["sourceRefs"])<={z["id"] for z in refpack["sourceRegistry"]},
                      sid+": unknown cited reference")
            if x["kind"]=="EXTENDED_SOURCE_CANDIDATE":
                check(x["sourceRefs"]==[s["sourceRef"] for s in ext["sources"]]
                      and x["donorActionDisposition"]=="INFORMATION_ONLY",
                      "CHME3T candidate material reclassified")
        check(got==exp, sid+": a donor node or claim source missing/added")
        check(sum(map(len,got.values()))==scenario["sourceEntryCount"]+scenario["donorGraphNodeCount"],
              sid+": review inventory dimension drift")
    print("DIAGNOSTIC_STAGE2_CLAIM_LEDGER_PASS",
          len(d["trials"]),sum(len(s["anchors"]) for s in d["trials"]),
          len(d["externalSourceChecks"]),"external observations; no content published")

if __name__=="__main__":
    main()
