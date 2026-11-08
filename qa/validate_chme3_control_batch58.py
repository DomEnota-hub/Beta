#!/usr/bin/env python3
"""CHME3 batch58: exact pinned lineage, 2x8/12 graphs, 5 extensions each, negative gates."""
import argparse, copy, json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
B="content-packs/diesel/chme3-family/"
D="docs/locomotives/chme3/diagnostics_electrical_control_pass3.json"
P={101:B+"diagnostics/authoring/chme3-diag-101-control-contactor-not-engaging.research.json",102:B+"diagnostics/authoring/chme3-diag-102-ru5-not-engaging.research.json"}
def read(p): return json.loads((R/p).read_text(encoding="utf-8"))
def graph(g,refs):
    nodes=g["nodes"]; m={n["id"]:n for n in nodes}; assert len(m)==len(nodes)
    seen=set(); todo=[g["startNodeId"]]
    while todo:
        k=todo.pop()
        if k in seen: continue
        n=m[k]; seen.add(k)
        assert n["permittedAction"] is False and n["sourceRefs"] and set(n["sourceRefs"])<=refs
        assert "procedureSteps" not in n
        assert n["type"] in ("QUESTION","STOP","OBSERVATION_REPORT")
        if n["type"]=="QUESTION":
            assert set(n["responses"])=={"YES","NO","UNKNOWN"}
            assert m[n["responses"]["UNKNOWN"]]["type"]=="STOP"
            todo.extend(n["responses"].values())
        else: assert n["responses"]=={} and n["causeConfirmed"] is False
    assert seen==set(m)
def check(c,num,idx,pack):
    sid="CHME3-DIAG-%03d"%num
    doc=next(x for x in idx["documents"] if x["sourcePath"]==D)
    original=next(x for x in doc["sourceObject"]["scenarios"] if x["id"]==sid)
    pos=doc["sourceObject"]["scenarios"].index(original)
    match=next(x for x in idx["matches"] if x["sourceId"]==sid)
    entry=next(x for x in pack["entries"] if x["id"]==match["canonicalId"])
    d=c["donor"]; a=c["applicability"]
    assert c["schemaVersion"]=="diagnostic-research-candidate/1" and c["batch"]==58
    assert c["originalId"]==sid and c["title"]==original["title"]==entry["title"]
    assert c["scenarioId"]==d["canonicalId"]==match["canonicalId"]==entry["id"]
    assert d["repository"]=="DomEnota-hub/Test-" and d["commit"]==idx["donorCommit"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff"
    assert d["documentPath"]==D and d["documentPointer"]==match["sourcePointer"]=="/scenarios/%d"%pos
    assert d["documentBlob"]==doc["sourceBlobSha"]=="41d241cb0b58e5657ef0d6210e7b272d44df52d0"
    assert d["canonicalPack"]==B+"diagnostics/recommended/diagnostics-01.pack.json"
    assert d["gzipBlob"]==entry["sourceObject"]["sourceBlobSha"]=="6a6068ad1ea54cb964b65a10ecf5c2425b2276e8"
    assert d["gzipIndependentlyDecoded"] is False and d["relation"]=="ID_TITLE_PROFILE_ONLY_NOT_GRAPH_EQUIVALENCE"
    for k in ("riskClass","actionAuthority","evidenceStatus","evidenceRefs","equipmentIds"): assert d[k]==original[k]
    assert original["profiles"]==["ЧМЭ3","ЧМЭ3Т","ЧМЭ3Э"]
    assert set(a["possibleVariants"])==set(entry["applicability"]["variantIds"])=={"chme3","chme3t","chme3e"}
    assert a["confirmedVariant"] is None and a["installedSchemeVerified"] is False and a["unknownProfile"]=="BLOCKED"
    assert c["publicationStatus"]==entry["publicationStatus"]=="CANDIDATE" and c["actionDisposition"]==original["actionAuthority"]
    for k in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified","humanSafetyReviewPassed"): assert c[k] is False
    assert c["warning"]=={"extendedHiddenByDefault":True,"readToEndRequired":True,"separateAcknowledgmentRequired":True,"grantsActionAuthority":False}
    assert c["safety"] and all(v is False for v in c["safety"].values())
    refs={x["id"] for x in c["sources"]}
    assert len(refs)==len(c["sources"]) and {"DOC","PACK","N68","N67","LOCAL"}<=refs
    assert all(x["currentVerified"] is False and x["installedProfileVerified"] is False and x["authority"]!="ACTION_AUTHORIZED" for x in c["sources"])
    assert any(x["authority"]=="HYPOTHESIS_ONLY" for x in c["sources"])
    assert len(c["crossScenarioBoundaries"])==4 and len({x["originalId"] for x in c["crossScenarioBoundaries"]})==4
    assert len(c["openGaps"])>=10 and c["deviceQA"]["status"]=="NOT_RUN_DEFERRED"
    for mode,count in (("SHORT",8),("DETAILED",12)):
        g=c["versions"][mode]; assert len(g["nodes"])==count
        graph(g,refs)
        assert g["nodes"][0]["responses"]["NO"]==g["nodes"][0]["responses"]["UNKNOWN"]=="stop-safety"
    assert len(c["extensions"])==5 and len({x["id"] for x in c["extensions"]})==5
    for e in c["extensions"]:
        assert e["sourceId"] in refs and e["displayMode"]=="EXTENDED_ONLY"
        assert e["visibility"]=={"hiddenByDefault":True,"warningReadToEndRequired":True,"warningAcknowledgedRequired":True}
        assert e["actionDisposition"]=="INFORMATION_ONLY" and e["executable"] is False and e["actionAuthorityGranted"] is False
        assert e["procedureSteps"]==[] and len(e["nodes"])==4
        graph({"startNodeId":e["nodes"][0]["id"],"nodes":e["nodes"]},refs)
    assert ("CHME3-DIAG-102" if num==101 else "CHME3-DIAG-101") in {x["originalId"] for x in c["crossScenarioBoundaries"]}
    if num==102: assert next(x for x in c["sources"] if x["id"]=="SECONDARY")["authority"]=="HYPOTHESIS_ONLY"
def negative(c,num,idx,pack):
    muts=[
        lambda x:x.update(runtimeImport=True),lambda x:x.update(executable=True),lambda x:x.update(publicationStatus="PUBLISHED"),
        lambda x:x.update(actionAuthorityGranted=True),lambda x:x.update(sourceAuthorityVerified=True),lambda x:x.update(humanSafetyReviewPassed=True),
        lambda x:x["applicability"].update(confirmedVariant="chme3"),lambda x:x["applicability"].update(installedSchemeVerified=True),
        lambda x:x["applicability"].update(unknownProfile="ALLOW"),lambda x:x["donor"].update(commit="HEAD"),
        lambda x:x["donor"].update(documentPointer="/scenarios/7"),lambda x:x["donor"].update(documentBlob="bad"),
        lambda x:x["donor"].update(gzipIndependentlyDecoded=True),lambda x:x["donor"].update(equipmentIds=[]),
        lambda x:x["donor"].update(evidenceRefs=[]),lambda x:x["warning"].update(extendedHiddenByDefault=False),
        lambda x:x["warning"].update(readToEndRequired=False),lambda x:x["warning"].update(separateAcknowledgmentRequired=False),
        lambda x:x["warning"].update(grantsActionAuthority=True),lambda x:x["safety"].update(temporaryJumper=True),
        lambda x:x["safety"].update(liveElectricalMeasurements=True),lambda x:x["versions"]["SHORT"]["nodes"][0]["responses"].update(UNKNOWN="s2"),
        lambda x:x["versions"]["DETAILED"]["nodes"][0].update(permittedAction=True),
        lambda x:x["versions"]["DETAILED"]["nodes"][1]["responses"].update(UNKNOWN="d3"),
        lambda x:x["extensions"][0]["visibility"].update(warningAcknowledgedRequired=False),
        lambda x:x["extensions"][1].update(executable=True),lambda x:x["extensions"][2].update(procedureSteps=["unsafe"]),
        lambda x:x["sources"][-1].update(authority="ACTION_AUTHORIZED"),lambda x:x["crossScenarioBoundaries"].pop(),
        lambda x:x["sources"][-1].update(id="DOC")]
    for i,f in enumerate(muts):
        x=copy.deepcopy(c);f(x)
        try:check(x,num,idx,pack)
        except (AssertionError,KeyError):continue
        raise AssertionError("unsafe mutation accepted %d/%d"%(num,i))
    return len(muts)
def main():
    p=argparse.ArgumentParser();p.add_argument("--negative",action="store_true");args=p.parse_args()
    idx=read(B+"migration/diagnostic-source-index.json");pack=read(B+"diagnostics/recommended/diagnostics-01.pack.json")
    total=0
    for num,path in P.items():
        c=read(path);check(c,num,idx,pack)
        if args.negative:total+=negative(c,num,idx,pack)
        print("CHME3_BATCH58_SCENARIO_PASS",num)
    print("CHME3_BATCH58_PASS",len(P),"NEGATIVE",total)
if __name__=="__main__":main()
