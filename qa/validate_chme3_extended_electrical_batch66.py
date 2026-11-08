#!/usr/bin/env python3
"""CHME3 batch66: pinned donor parity, fail-closed graph and mutation QA."""
import argparse, copy, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE="content-packs/diesel/chme3-family/"
DOC="docs/locomotives/chme3/diagnostics_extended_pass3.json"
PACK="content-packs/diesel/chme3-family/diagnostics/recommended/diagnostics-02.pack.json"
FILES={304: BASE+"diagnostics/authoring/chme3-diag-304-reverser-not-moving.research.json",305: BASE+"diagnostics/authoring/chme3-diag-305-one-direction-only.research.json",306: BASE+"diagnostics/authoring/chme3-diag-306-contactors-relays-chatter.research.json",307: BASE+"diagnostics/authoring/chme3-diag-307-battery-start-sag.research.json"}
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
def check(c,n,idx,pack):
    d=c["donor"]; a=c["applicability"]
    source=next(x for x in idx["documents"] if x["sourcePath"]==DOC)
    o=source["sourceObject"]["scenarios"][n-301]
    m=next(x for x in idx["matches"] if x["sourceId"]==o["id"])
    p=next(x for x in pack["entries"] if x["id"]==m["canonicalId"])
    assert c["schemaVersion"]=="diagnostic-research-candidate/1" and c["batch"]==66
    assert c["originalId"]==o["id"]==f"CHME3-DIAG-{n}"
    assert c["title"]==o["title"]==p["title"]
    assert c["scenarioId"]==d["canonicalId"]==m["canonicalId"]==p["id"]
    assert d["repository"]=="DomEnota-hub/Test-" and d["commit"]==idx["donorCommit"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff"
    assert d["documentPath"]==DOC and d["documentPointer"]==m["sourcePointer"]==f"/scenarios/{n-301}"
    assert d["documentBlob"]==source["sourceBlobSha"]=="9fa23a5c9e3da49fb025fb55245227314f6020da"
    assert d["canonicalPack"]==m["canonicalPack"]==PACK
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
    assert len(refs)==len(c["sources"]) and {"DOC","PACK","N65","N67","N68","LOCAL","FIELD"}<=refs
    for s in c["sources"]:
        assert s["currentVerified"] is False and s["installedProfileVerified"] is False
        assert s["authority"] in ("INFORMATION_ONLY","HYPOTHESIS_ONLY")
    assert len(c["crossScenarioBoundaries"])>=3 and len({x["originalId"] for x in c["crossScenarioBoundaries"]})==len(c["crossScenarioBoundaries"])
    assert len(c["sourceDiscrepancies"])>=3 and len(c["openGaps"])>=10
    assert c["deviceQA"]=={"status":"NOT_RUN_DEFERRED","registry":"docs/diagnostics/DIAGNOSTIC_FINAL_DEVICE_QA_DEFERRED_2026-11-04.md"}
    graph(c["versions"]["SHORT"],8,refs);graph(c["versions"]["DETAILED"],12,refs)
    for mode in ("SHORT","DETAILED"):
        first=c["versions"][mode]["nodes"][0]
        assert first["responses"]["NO"]==first["responses"]["UNKNOWN"]=="stop-safety"
    assert len(c["extensions"])==5 and len({x["id"] for x in c["extensions"]})==5
    for x in c["extensions"]:
        assert x["sourceId"] in refs and x["displayMode"]=="EXTENDED_ONLY"
        assert x["visibility"]=={"hiddenByDefault":True,"warningReadToEndRequired":True,"warningAcknowledgedRequired":True}
        assert x["actionDisposition"]=="INFORMATION_ONLY" and x["executable"] is False and x["actionAuthorityGranted"] is False and x["procedureSteps"]==[]
        graph({"startNodeId":x["nodes"][0]["id"],"nodes":x["nodes"]},4,refs)
def negative(c,n,idx,pack):
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
        lambda x:x["donor"].update(riskClass="NORMAL_DIAGNOSTIC"),
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
        lambda x:x["extensions"].pop()
    ]
    for i,mut in enumerate(muts):
        y=copy.deepcopy(c);mut(y)
        try: check(y,n,idx,pack)
        except (AssertionError,KeyError,IndexError): continue
        raise AssertionError(f"unsafe mutation accepted {n} #{i}")
    return len(muts)
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--negative",action="store_true");args=ap.parse_args()
    idx=read(BASE+"migration/diagnostic-source-index.json");pack=read(PACK)
    total=0
    for n,p in FILES.items():
        c=read(p);check(c,n,idx,pack)
        if args.negative: total+=negative(c,n,idx,pack)
    print("CHME3_BATCH66_PASS","SCENARIOS",len(FILES),"NEGATIVE",total)
if __name__=="__main__":main()
