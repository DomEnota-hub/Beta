#!/usr/bin/env python3
"""Batch64 CHME3: pinned provenance, graph reachability and negative safety QA."""
import argparse,copy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
INDEX="content-packs/diesel/chme3-family/migration/diagnostic-source-index.json"
PACK="content-packs/diesel/chme3-family/diagnostics/recommended/diagnostics-02.pack.json"
DOC="docs/locomotives/chme3/diagnostics_brake_aux_pass3.json"
REG="docs/diagnostics/DIAGNOSTIC_FINAL_DEVICE_QA_DEFERRED_2026-11-04.md"
FILES={"206":"content-packs/diesel/chme3-family/diagnostics/authoring/chme3-diag-206-cooling-shutters-fans.research.json","207":"content-packs/diesel/chme3-family/diagnostics/authoring/chme3-diag-207-pneumatic-control-apparatus.research.json","208":"content-packs/diesel/chme3-family/diagnostics/authoring/chme3-diag-208-sanding-system-no-feed.research.json"}
def load(p):return json.loads((ROOT/p).read_text(encoding="utf-8"))
def graph(g,count,refs):
    nodes=g["nodes"];assert len(nodes)==count
    by={x["id"]:x for x in nodes};assert len(by)==count
    todo=[g["startNodeId"]];seen=set()
    while todo:
        k=todo.pop();assert k in by
        if k in seen:continue
        seen.add(k);n=by[k]
        assert n["type"] in ("QUESTION","OBSERVATION_REPORT","STOP")
        assert n["permittedAction"] is False and n["sourceRefs"] and set(n["sourceRefs"])<=refs
        if n["type"]=="QUESTION":
            assert set(n["responses"])=={"YES","NO","UNKNOWN"}
            assert by[n["responses"]["UNKNOWN"]]["type"]=="STOP"
            todo.extend(n["responses"].values())
        else:assert n["responses"]=={} and n["causeConfirmed"] is False
    assert seen==set(by)
def check(c,n,idx,pack):
    doc=next(x for x in idx["documents"] if x["sourcePath"]==DOC)
    orig=doc["sourceObject"]["scenarios"][n-201]
    m=next(x for x in idx["matches"] if x["sourceId"]=="CHME3-DIAG-%d"%n)
    e=next(x for x in pack["entries"] if x["id"]==m["canonicalId"])
    z=c["donor"];a=c["applicability"]
    assert c["schemaVersion"]=="diagnostic-research-candidate/1" and c["batch"]==64
    assert c["originalId"]==orig["id"]=="CHME3-DIAG-%d"%n
    assert c["title"]==orig["title"]==e["title"]
    assert c["scenarioId"]==z["canonicalId"]==m["canonicalId"]==e["id"]
    assert z["repository"]=="DomEnota-hub/Test-" and z["commit"]==idx["donorCommit"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff"
    assert z["documentPath"]==DOC and z["documentPointer"]==m["sourcePointer"]=="/scenarios/%d"%(n-201)
    assert z["documentBlob"]==doc["sourceBlobSha"]=="1094688cc2e633fab21b6f989cc902f7a34d19d2"
    assert z["canonicalPack"]==m["canonicalPack"]==PACK
    assert z["gzipBlob"]==e["sourceObject"]["sourceBlobSha"]=="6a6068ad1ea54cb964b65a10ecf5c2425b2276e8"
    assert z["gzipIndependentlyDecoded"] is False and z["relation"]=="ID_TITLE_PROFILE_ONLY_NOT_GRAPH_EQUIVALENCE"
    for key in ("riskClass","actionAuthority","evidenceStatus","evidenceRefs","equipmentIds"):assert z[key]==orig[key]
    assert z["profileGate"]==orig.get("profileGate")
    assert a=={"possibleVariants":["chme3","chme3t","chme3e"],"confirmedVariant":None,"installedSchemeVerified":False,"unknownProfile":"BLOCKED","profileGateVerified":False}
    assert c["publicationStatus"]==e["publicationStatus"]=="CANDIDATE" and c["actionDisposition"]==orig["actionAuthority"]
    for key in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified","humanSafetyReviewPassed"):assert c[key] is False
    assert c["warning"]=={"extendedHiddenByDefault":True,"readToEndRequired":True,"separateAcknowledgmentRequired":True,"grantsActionAuthority":False}
    assert len(c["safety"])>=20 and all(v is False for v in c["safety"].values())
    refs={s["id"] for s in c["sources"]}
    assert refs==({"DOC","PACK","HIST","FIELD","SECONDARY"} if n==206 else {"DOC","PACK","HIST","FIELD"})
    for s in c["sources"]:
        assert s["authority"] in ("INFORMATION_ONLY","HYPOTHESIS_ONLY")
        assert s["currentVerified"] is False and s["installedProfileVerified"] is False
        assert set(s["profiles"])<=set(a["possibleVariants"])
    assert len(c["crossScenarioBoundaries"])==3 and len({x["originalId"] for x in c["crossScenarioBoundaries"]})==3
    assert all(x["originalId"]!=c["originalId"] for x in c["crossScenarioBoundaries"])
    assert len(c["sourceDiscrepancies"])>=4 and len(c["openGaps"])>=12
    assert c["deviceQA"]=={"status":"NOT_RUN_DEFERRED","registry":REG}
    assert c["originalId"] in (ROOT/REG).read_text(encoding="utf-8")
    graph(c["versions"]["SHORT"],8,refs);graph(c["versions"]["DETAILED"],12,refs)
    for mode in ("SHORT","DETAILED"):
        first=c["versions"][mode]["nodes"][0]
        assert first["responses"]["NO"]==first["responses"]["UNKNOWN"]=="stop-safety"
    assert len(c["extensions"])==5 and len({x["id"] for x in c["extensions"]})==5
    for e in c["extensions"]:
        assert e["sourceId"] in refs and e["displayMode"]=="EXTENDED_ONLY"
        assert e["visibility"]=={"hiddenByDefault":True,"warningReadToEndRequired":True,"warningAcknowledgedRequired":True}
        assert e["actionDisposition"]=="INFORMATION_ONLY" and e["executable"] is False and e["actionAuthorityGranted"] is False and e["procedureSteps"]==[]
        graph({"startNodeId":e["nodes"][0]["id"],"nodes":e["nodes"]},4,refs)
def negative(c,n,idx,pack):
    muts=[
      lambda x:x.update(runtimeImport=True),lambda x:x.update(executable=True),
      lambda x:x.update(publicationStatus="PUBLISHED"),lambda x:x.update(actionAuthorityGranted=True),
      lambda x:x.update(sourceAuthorityVerified=True),lambda x:x.update(humanSafetyReviewPassed=True),
      lambda x:x.update(actionDisposition="REPAIR"),lambda x:x["applicability"].update(confirmedVariant="chme3"),
      lambda x:x["applicability"].update(installedSchemeVerified=True),lambda x:x["applicability"].update(profileGateVerified=True),
      lambda x:x["applicability"].update(unknownProfile="ALLOW"),lambda x:x["donor"].update(commit="HEAD"),
      lambda x:x["donor"].update(documentBlob="bad"),lambda x:x["donor"].update(documentPointer="/scenarios/0"),
      lambda x:x["donor"].update(gzipIndependentlyDecoded=True),lambda x:x["donor"].update(evidenceRefs=[]),
      lambda x:x["donor"].update(equipmentIds=[]),lambda x:x["donor"].update(riskClass="NORMAL"),
      lambda x:x["warning"].update(extendedHiddenByDefault=False),lambda x:x["warning"].update(readToEndRequired=False),
      lambda x:x["warning"].update(separateAcknowledgmentRequired=False),lambda x:x["warning"].update(grantsActionAuthority=True),
      lambda x:x["safety"].update(valveMechanicalFixation=True),lambda x:x["safety"].update(temporaryJumper=True),
      lambda x:x["versions"]["SHORT"]["nodes"][0]["responses"].update(UNKNOWN="s2"),
      lambda x:x["versions"]["DETAILED"]["nodes"][0].update(permittedAction=True),
      lambda x:x["extensions"][0]["visibility"].update(warningAcknowledgedRequired=False),
      lambda x:x["extensions"][1].update(executable=True),lambda x:x["extensions"][2].update(procedureSteps=["force"]),
      lambda x:x["sources"][0].update(currentVerified=True),lambda x:x["sources"][0].update(installedProfileVerified=True),
      lambda x:x["crossScenarioBoundaries"].pop(),lambda x:x["sourceDiscrepancies"].clear(),
      lambda x:x["deviceQA"].update(status="PASS"),
      lambda x:x["extensions"][3]["nodes"][0]["responses"].update(UNKNOWN=x["extensions"][3]["nodes"][1]["id"]),
      lambda x:x["versions"]["DETAILED"]["nodes"][4]["responses"].update(YES="missing")
    ]
    count=0
    for i,f in enumerate(muts):
        altered=copy.deepcopy(c);f(altered)
        try:check(altered,n,idx,pack)
        except (AssertionError,KeyError,TypeError):count+=1;continue
        raise AssertionError("unsafe mutation %d/%d"%(n,i))
    return count
def main():
    p=argparse.ArgumentParser();p.add_argument("--negative",action="store_true");a=p.parse_args()
    idx=load(INDEX);pack=load(PACK);count=0
    for n,path in FILES.items():
        c=load(path);check(c,int(n),idx,pack)
        if a.negative:count+=negative(c,int(n),idx,pack)
    print("CHME3_BATCH64_PASS SCENARIOS",len(FILES),"NEGATIVE",count)
if __name__=="__main__":main()
