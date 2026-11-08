#!/usr/bin/env python3
"""CHME3 batch68: pinned donor parity, fail-closed graph and mutation QA."""
import argparse, copy, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE="content-packs/diesel/chme3-family/"
DOC="docs/locomotives/chme3/diagnostics_extended_pass3.json"
PACKS=["content-packs/diesel/chme3-family/diagnostics/recommended/diagnostics-03.pack.json"]
FILES={313: BASE+"diagnostics/authoring/chme3-diag-313-oil-pressure-hot-drop.research.json",314: BASE+"diagnostics/authoring/chme3-diag-314-diesel-oil-overheat.research.json",315: BASE+"diagnostics/authoring/chme3-diag-315-coolant-loss-leak.research.json",316: BASE+"diagnostics/authoring/chme3-diag-316-cooling-fan-not-rotating.research.json",317: BASE+"diagnostics/authoring/chme3-diag-317-compressor-overheat-knock-oil.research.json"}
def read(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))
def graph(g,count,refs):
    nodes=g["nodes"]; assert len(nodes)==count
    by={x["id"]:x for x in nodes}; assert len(by)==count
    seen=set(); stack=[g["startNodeId"]]
    while stack:
        k=stack.pop()
        if k in seen: continue
        x=by[k]; seen.add(k)
        assert x["permittedAction"] is False and x["sourceRefs"] and set(x["sourceRefs"])<=refs
        assert "procedureSteps" not in x
        assert x["type"] in ("QUESTION","OBSERVATION_REPORT","STOP")
        if x["type"]=="QUESTION":
            assert set(x["responses"])=={"YES","NO","UNKNOWN"}
            assert by[x["responses"]["UNKNOWN"]]["type"]=="STOP"
            stack.extend(x["responses"].values())
        else:
            assert x["responses"]=={} and x["causeConfirmed"] is False
    assert seen==set(by)
def check(c,n,idx,packs):
    d=c["donor"]; a=c["applicability"]
    source=next(x for x in idx["documents"] if x["sourcePath"]==DOC)
    o=source["sourceObject"]["scenarios"][n-301]
    m=next(x for x in idx["matches"] if x["sourceId"]==o["id"])
    p=next(x for x in packs[m["canonicalPack"]]["entries"] if x["id"]==m["canonicalId"])
    assert c["schemaVersion"]=="diagnostic-research-candidate/1" and c["batch"]==68
    assert c["originalId"]==o["id"]==f"CHME3-DIAG-{n}"
    assert c["title"]==o["title"]==p["title"]
    assert c["scenarioId"]==d["canonicalId"]==m["canonicalId"]==p["id"]
    assert d["repository"]=="DomEnota-hub/Test-" and d["commit"]==idx["donorCommit"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff"
    assert d["documentPath"]==DOC and d["documentPointer"]==m["sourcePointer"]==f"/scenarios/{n-301}"
    assert d["documentBlob"]==source["sourceBlobSha"]=="9fa23a5c9e3da49fb025fb55245227314f6020da"
    assert d["canonicalPack"]==m["canonicalPack"]==m["canonicalPack"]
    assert d["gzipBlob"]==p["sourceObject"]["sourceBlobSha"]=="6a6068ad1ea54cb964b65a10ecf5c2425b2276e8"
    assert d["gzipIndependentlyDecoded"] is False and d["relation"]=="ID_TITLE_PROFILE_ONLY_NOT_GRAPH_EQUIVALENCE"
    for k in ("riskClass","actionAuthority","evidenceStatus","evidenceRefs","equipmentIds"): assert d[k]==o[k]
    assert o["profiles"]==["ЧМЭ3","ЧМЭ3Т","ЧМЭ3Э"]
    assert set(a["possibleVariants"])==set(p["applicability"]["variantIds"])=={"chme3","chme3t","chme3e"}
    assert a["confirmedVariant"] is None and a["installedSchemeVerified"] is False and a["unknownProfile"]=="BLOCKED"
    assert c["publicationStatus"]==p["publicationStatus"]=="CANDIDATE"
    assert c["actionDisposition"]==o["actionAuthority"]
    for k in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified","humanSafetyReviewPassed"): assert c[k] is False
    assert c["warning"]=={"extendedHiddenByDefault":True,"readToEndRequired":True,"separateAcknowledgmentRequired":True,"grantsActionAuthority":False}
    assert len(c["safety"])>=12 and all(v is False for v in c["safety"].values())
    refs={s["id"] for s in c["sources"]}
    assert len(refs)==len(c["sources"]) and {"DOC","PACK","LOCAL","FIELD"}<=refs and len([s for s in c["sources"] if s["kind"]=="HISTORICAL_TRAINING"])>=2
    for s in c["sources"]:
        assert s["currentVerified"] is False and s["installedProfileVerified"] is False
        assert s["authority"] in ("INFORMATION_ONLY","HYPOTHESIS_ONLY")
    assert len(c["crossScenarioBoundaries"])>=3 and len({x["originalId"] for x in c["crossScenarioBoundaries"]})==len(c["crossScenarioBoundaries"])
    assert len(c["sourceDiscrepancies"])>=6 and len(c["openGaps"])>=10
    assert c["deviceQA"]=={"status":"NOT_RUN_DEFERRED","registry":"docs/diagnostics/DIAGNOSTIC_FINAL_DEVICE_QA_DEFERRED_2026-11-04.md"}
    graph(c["versions"]["SHORT"],8,refs);graph(c["versions"]["DETAILED"],12,refs)
    assert set(c["branchContracts"])=={"SHORT","DETAILED"}
    for mode,contracts in c["branchContracts"].items():
        by={node["id"]:node for node in c["versions"][mode]["nodes"]}
        for node_id,expected in contracts.items():
            assert by[node_id]["type"]=="QUESTION" and by[node_id]["responses"]==expected
    assert c["versions"]["SHORT"]["nodes"][2]["responses"]=={"YES":"obs-b","NO":"obs-c","UNKNOWN":"stop-unknown"}
    expected={"d3":("d4","obs-c"),"d4":("d5","obs-b")} if n==316 else {"d3":("obs-b","d4"),"d4":("obs-c","d5")}
    for node_id,(yes,no) in expected.items():
        node=next(z for z in c["versions"]["DETAILED"]["nodes"] if z["id"]==node_id)
        assert node["responses"]=={"YES":yes,"NO":no,"UNKNOWN":"stop-unknown"}
    for mode in ("SHORT","DETAILED"):
        first=c["versions"][mode]["nodes"][0]
        assert first["responses"]["NO"]==first["responses"]["UNKNOWN"]=="stop-safety"
    assert len(c["extensions"])==5 and len({x["id"] for x in c["extensions"]})==5
    for x in c["extensions"]:
        assert x["sourceId"] in refs and x["displayMode"]=="EXTENDED_ONLY"
        assert x["visibility"]=={"hiddenByDefault":True,"warningReadToEndRequired":True,"warningAcknowledgedRequired":True}
        assert x["actionDisposition"]=="INFORMATION_ONLY" and x["executable"] is False and x["actionAuthorityGranted"] is False and x["procedureSteps"]==[]
        graph({"startNodeId":x["nodes"][0]["id"],"nodes":x["nodes"]},4,refs)
def negative(c,n,idx,packs):
    muts=[
        lambda x:x.update(runtimeImport=True),
        lambda x:x.update(executable=True),
        lambda x:x.update(publicationStatus="PUBLISHED"),
        lambda x:x.update(actionAuthorityGranted=True),
        lambda x:x.update(sourceAuthorityVerified=True),
        lambda x:x.update(humanSafetyReviewPassed=True),
        lambda x:x["applicability"].update(confirmedVariant="chme3"),
        lambda x:x["applicability"].update(installedSchemeVerified=True),
        lambda x:x["applicability"].update(unknownProfile="ALLOW"),
        lambda x:x["donor"].update(commit="HEAD"),
        lambda x:x["donor"].update(documentPointer="/scenarios/99"),
        lambda x:x["donor"].update(documentBlob="bad"),
        lambda x:x["donor"].update(gzipIndependentlyDecoded=True),
        lambda x:x["donor"].update(equipmentIds=[]),
        lambda x:x["donor"].update(evidenceRefs=[]),
        lambda x:x["donor"].update(riskClass="INVALID_RISK"),
        lambda x:x["donor"].update(actionAuthority="ALLOW_REPAIR"),
        lambda x:x["warning"].update(extendedHiddenByDefault=False),
        lambda x:x["warning"].update(readToEndRequired=False),
        lambda x:x["warning"].update(separateAcknowledgmentRequired=False),
        lambda x:x["warning"].update(grantsActionAuthority=True),
        lambda x:x["safety"].update(temporaryJumper=True),
        lambda x:x["safety"].update(highVoltageIntervention=True),
        lambda x:x["safety"].update(protectionReset=True),
        lambda x:x["versions"]["SHORT"]["nodes"][0]["responses"].update(UNKNOWN="s2"),
        lambda x:x["versions"]["SHORT"]["nodes"][0]["responses"].update(NO="s2"),
        lambda x:x["versions"]["DETAILED"]["nodes"][0].update(permittedAction=True),
        lambda x:x["versions"]["DETAILED"]["nodes"][1]["responses"].update(UNKNOWN="d3"),
        lambda x:x["extensions"][0]["visibility"].update(warningAcknowledgedRequired=False),
        lambda x:x["extensions"][1].update(executable=True),
        lambda x:x["extensions"][2].update(procedureSteps=["unsafe"]),
        lambda x:x["extensions"][3]["nodes"][0]["responses"].update(UNKNOWN=x["extensions"][3]["nodes"][1]["id"]),
        lambda x:x["sources"][0].update(currentVerified=True),
        lambda x:x["sources"][0].update(installedProfileVerified=True),
        lambda x:x["sources"][-1].update(id="DOC"),
        lambda x:x["crossScenarioBoundaries"].pop(),
        lambda x:x["sourceDiscrepancies"].pop(),
        lambda x:x["deviceQA"].update(status="PASS"),
        lambda x:x["versions"]["DETAILED"]["nodes"].pop(),
        lambda x:x["extensions"].pop(),
        lambda x:x["branchContracts"]["SHORT"]["s3"].update(YES="obs-c"),
        lambda x:x["versions"]["SHORT"]["nodes"][2]["responses"].update(YES="obs-c"),
        lambda x:x["versions"]["DETAILED"]["nodes"][2]["responses"].update(YES="obs-e")
    ]
    for i,mut in enumerate(muts):
        y=copy.deepcopy(c);mut(y)
        try: check(y,n,idx,packs)
        except (AssertionError,KeyError,IndexError): continue
        raise AssertionError(f"unsafe mutation accepted {n} #{i}")
    return len(muts)
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--negative",action="store_true");args=ap.parse_args()
    idx=read(BASE+"migration/diagnostic-source-index.json");packs={p:read(p) for p in PACKS}
    total=0
    for n,p in FILES.items():
        c=read(p);check(c,n,idx,packs)
        if args.negative: total+=negative(c,n,idx,packs)
    print("CHME3_BATCH68_PASS","SCENARIOS",len(FILES),"NEGATIVE",total)
if __name__=="__main__":main()
