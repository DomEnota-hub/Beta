#!/usr/bin/env python3
"""Stage6 preflight: canonical scenario distinctness and exact source layers."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P="docs/diagnostics/STAGE6_SYMPTOM_SEPARATION_RESEARCH.json"
def require(cond,msg):
    if not cond:raise ValueError(msg)
def check(d,inventory,overlay):
    require(d["stage"]=="6/51" and d["status"]=="SOURCE_COMPARISON_STARTED_NOT_AUTHORED"
            and d["publicationStatus"]=="CANDIDATE" and d["runtimeImport"] is False
            and d["actionAuthorityGranted"] is False,"premature Stage6 publication")
    require(d["donorCommit"]==inventory["donorCommit"]
            and d["baseline"]=={"scenarios":340,"preservedGraphNodes":3902},
            "donor corpus drift")
    require(d["sourceKotlin"]["base"]["blob"]=="5f57ff2c98f02a04692e8553700ec8d23077d166"
            and d["sourceKotlin"]["extendedSeeds"]["blob"]=="090d448d0e9de20d002edf07361764e524298bf8",
            "pinned original layer changed")
    rows={x["scenarioId"]:x for x in inventory["rows"]}
    src={"vl80s.diag."+x["id"]:x for x in overlay["scenarios"]}
    expected={"GV_COMMAND_DIRECTION":("vl80s.diag.gv-no-close","vl80s.diag.gv-no-open"),
              "EKG_TRANSITION_STATE":("vl80s.diag.ekg-stuck","vl80s.diag.ekg-slow-transition")}
    require(len(d["groups"])==2 and {x["groupId"] for x in d["groups"]}==set(expected),
            "pair identities changed")
    for group in d["groups"]:
        pair=expected[group["groupId"]]
        require((group["baselineScenario"]["scenarioId"],
                 group["contrastingScenario"]["scenarioId"])==pair,
                "not two distinct canonical scenarios")
        for part,layer in (("baselineScenario","DiagnosticRepository.kt"),
                           ("contrastingScenario","DiagnosticExtendedCatalog.kt")):
            item=group[part];row=rows[item["scenarioId"]];origin=src[item["scenarioId"]]
            require(item["originalId"]==row["sourceScenarioId"]==origin["id"]
                    and item["sourceLayer"]==origin["originLayer"]==layer
                    and item["title"]==origin["title"]
                    and item["summary"]==origin["summary"]
                    and item["variantIds"]==row["variantIds"]
                    and item["canonicalGraphNodeCount"]==row["graph"]["nodeCount"],
                    "original source scenario mismatch")
            require(all(row[k]=="NOT_AUTHORED" for k in
                   ("shortVersion","detailedVersion","shortExtendedBranch","detailedExtendedBranch")),
                   "premature version promotion")
        require(group["symptomCodes"]["baseline"]!=group["symptomCodes"]["contrast"]
                and bool(group["reasonToKeepDistinct"])
                and group["contrastIsSeparateCanonicalScenarioNotAnExtension"] is True,
                "distinct failure types merged")
        require(group["publicationStatus"]=="CANDIDATE"
                and group["runtimeImport"] is False
                and group["actionAuthorityGranted"] is False
                and group["exactInstalledEquipmentVerified"] is False
                and group["sourceAuthorityVerified"] is False
                and group["technicalClaimsReviewed"] is False
                and group["operationalSteps"]==[]
                and group["stage6AuthoredVersions"]==[],
                "unsupported runtime actions or authoring")
    return len(d["groups"])
if __name__=="__main__":
    d=json.loads((ROOT/P).read_text(encoding="utf-8"))
    inv=json.loads((ROOT/"docs/data-migration/diagnostic-corpus-analysis.json").read_text(encoding="utf-8"))
    ov=json.loads((ROOT/"content-packs/electric/vl80s/diagnostics/migration/diagnostics-source.candidate.json").read_text(encoding="utf-8"))["sourceObject"]
    print("PASS Stage6 distinct source records (NO publication):",check(d,inv,ov))
