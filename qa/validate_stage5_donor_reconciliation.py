#!/usr/bin/env python3
"""Pin direct donor Kotlin scenario questions, reveal authoring coverage gaps.
Does not attest exact runtime topology nor authorize operating actions.
"""
import gzip,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MANIFEST="docs/diagnostics/STAGE5_DONOR_KOTLIN_RECONCILIATION.json"
DONOR="3176d6ee228f0ed4b78371f45209e10c1c724eff"
DONOR_BLOB="5f57ff2c98f02a04692e8553700ec8d23077d166"
def require(b,why):
    if not b: raise ValueError(why)
def check(m):
    require(m["donorCommit"]==DONOR and m["donorKotlinBlobSha"]==DONOR_BLOB,
            "untraceable donor source")
    require(m["runtimeImport"] is False and m["actionAuthorityGranted"] is False and
            m["technicalAcceptance"]=="BLOCKED" and
            m["runtimeGraphProvenance"]=="NOT_VERIFIED_AGAINST_FULL_RUNTIME_GRAPH",
            "false source approval")
    require(len(m["items"])==2 and
            {x["scenarioId"] for x in m["items"]}==
            {"vl80s.diag.gv-no-close","vl80s.diag.ekg-stuck"},
            "mismatched donor scenarios")
    coverage={}
    for item in m["items"]:
        require(item["donorStoredGraphNodeCount"]==5 and
                item["fullFiveNodeRuntimeGraphCompared"] is False and
                item["publicationStatus"]=="CANDIDATE" and
                item["actionAuthorityGranted"] is False,"false donor/graph approval")
        questions=item["donorQuestions"]
        require(len(questions)==3 and
                [q["question"] for q in questions]==
                [q["question"] for q in item["questionReconciliation"]],
                "original decision question identity lost")
        require(all(q["yesInterpretation"] and q["noInterpretation"] for q in questions),
                "donor interpretation missing")
        for group in ("donorDangerSigns","donorStopConditions","donorProhibited",
                      "donorReportFields"):
            require(item[group] and all(isinstance(x,str) and x.strip()
                    for x in item[group]),"missing donor safety context: "+group)
        name=item["scenarioId"].split(".")[-1]
        path=("content-packs/electric/vl80s/diagnostics/authoring/"
              "stage5-"+name+".research.json.gz")
        with gzip.open(ROOT/path,"rt",encoding="utf-8") as f: draft=json.load(f)
        require(draft["scenarioId"]==item["scenarioId"] and
                draft["donorPinnedSha"]==DONOR and draft["runtimeImport"] is False,
                "research draft mismatch/activation")
        ids={v+":"+n["id"] for v in ("short","detailed") for n in draft[v]["nodes"]}
        for q in item["questionReconciliation"]:
            require(q["coverage"] in ("NOT_COVERED","PARTIAL_NOT_EQUIVALENT") and
                    q["independentSafetyReviewRequired"] is True and bool(q["gap"]),
                    "unreviewed gap promoted to complete")
            require(all(ref in ids for ref in q["draftNodes"]),
                    "invented candidate node mapping")
            require(q["coverage"]!="NOT_COVERED" or not q["draftNodes"],
                    "uncovered question falsely mapped")
        coverage[item["scenarioId"]]={q["coverage"] for q in item["questionReconciliation"]}
    return coverage
if __name__=="__main__":
    m=json.loads((ROOT/MANIFEST).read_text(encoding="utf-8"))
    print("PASS direct donor Kotlin comparison (not runtime graph):",check(m))
