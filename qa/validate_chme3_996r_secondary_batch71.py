#!/usr/bin/env python3
"""Pinned CHME3-DIAG-326, batch71 source, graph, safety and negative QA."""
import argparse,copy,json
from pathlib import Path
from validate_chme3_996r_secondary_batch70 import graph,REFS,WARN,VIS,DISCREPANCIES
ROOT=Path(__file__).resolve().parents[1]
BASE="content-packs/diesel/chme3-family/"
DOC="docs/locomotives/chme3/diagnostics_996r_detail_pass3.json"
PACK=BASE+"diagnostics/recommended/diagnostics-03.pack.json"
PATH="content-packs/diesel/chme3-family/diagnostics/authoring/chme3-diag-326-ru3-om-contacts-fifth-position.research.json"
def read(p):return json.loads((ROOT/p).read_text(encoding="utf-8"))
def check(c,index,pack):
    source=next(x for x in index["documents"] if x["sourcePath"]==DOC)
    original=source["sourceObject"]["scenarios"][5]
    match=next(x for x in index["matches"] if x["sourceId"]=="CHME3-DIAG-326")
    entry=next(x for x in pack["entries"] if x["id"]==match["canonicalId"])
    d=c["donor"];a=c["applicability"]
    assert c["schemaVersion"]=="diagnostic-research-candidate/1" and c["batch"]==71
    assert c["originalId"]==original["id"]=="CHME3-DIAG-326"
    assert c["title"]==original["title"]==entry["title"]
    assert c["scenarioId"]==d["canonicalId"]==match["canonicalId"]==entry["id"]
    assert d["repository"]=="DomEnota-hub/Test-" and d["commit"]==index["donorCommit"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff"
    assert d["documentPath"]==match["sourcePath"]==DOC and d["documentPointer"]==match["sourcePointer"]=="/scenarios/5"
    assert d["documentBlob"]==source["sourceBlobSha"]=="f29c287c2eae1fb60e0cac61cab098fa8cae3c0f"
    assert d["canonicalPack"]==match["canonicalPack"]==PACK
    assert d["gzipBlob"]==entry["sourceObject"]["sourceBlobSha"]=="6a6068ad1ea54cb964b65a10ecf5c2425b2276e8"
    assert d["gzipIndependentlyDecoded"] is False and d["relation"]=="ID_TITLE_PROFILE_ONLY_NOT_GRAPH_EQUIVALENCE"
    for key in ("riskClass","actionAuthority","evidenceStatus","evidenceRefs","equipmentIds"):
        assert d[key]==original[key]
    assert original["profiles"]==["ЧМЭ3","ЧМЭ3Т","ЧМЭ3Э"]
    assert set(a["possibleVariants"])==set(entry["applicability"]["variantIds"])=={"chme3","chme3t","chme3e"}
    assert a["confirmedVariant"] is None and a["installedSchemeVerified"] is False and a["unknownProfile"]=="BLOCKED"
    assert c["publicationStatus"]=="CANDIDATE" and c["actionDisposition"]==original["actionAuthority"]=="SOURCE_AND_PROFILE_REQUIRED"
    for key in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified","humanSafetyReviewPassed"):
        assert c[key] is False
    assert c["warning"]==WARN and len(c["safety"])>=16 and all(v is False for v in c["safety"].values())
    assert len(c["sources"])==len(REFS) and {s["id"] for s in c["sources"]}==REFS
    assert next(s for s in c["sources"] if s["id"]=="SECONDARY")["kind"]=="SECONDARY_996R_UNVERIFIED_PRIMARY"
    assert next(s for s in c["sources"] if s["id"]=="SECONDARY")["ref"]==original["evidenceRefs"][0]
    assert all(not s["currentVerified"] and not s["installedProfileVerified"] for s in c["sources"])
    assert all(s["authority"] in ("INFORMATION_ONLY","HYPOTHESIS_ONLY") for s in c["sources"])
    assert {x["source"] for x in c["sourceDiscrepancies"]}==DISCREPANCIES
    assert all(x["status"] not in ("VERIFIED","APPROVED") for x in c["sourceDiscrepancies"])
    assert len(c["openGaps"])>=14 and "первичный" in c["secondaryRiskNote"]
    assert {x["originalId"] for x in c["crossScenarioBoundaries"]}=={"CHME3-DIAG-004","CHME3-DIAG-103","CHME3-DIAG-322","CHME3-DIAG-323"}
    assert all(x["boundary"] for x in c["crossScenarioBoundaries"])
    assert c["deviceQA"]=={"status":"NOT_RUN_DEFERRED","registry":"docs/diagnostics/DIAGNOSTIC_FINAL_DEVICE_QA_DEFERRED_2026-11-04.md"}
    for mode,count in (("SHORT",8),("DETAILED",12)):
        g=c["versions"][mode];graph(g,count)
        first=g["nodes"][0]
        assert first["responses"]["NO"]==first["responses"]["UNKNOWN"]=="stop-safety"
        assert first["responses"]["YES"]==("s2" if mode=="SHORT" else "d2")
        assert "5-й позиции" in g["nodes"][1]["text"] and "РУ3" in g["nodes"][2]["text"]
        assert c["branchContracts"][mode]=={n["id"]:n["responses"] for n in g["nodes"] if n["type"]=="QUESTION"}
    assert c["versions"]["SHORT"]["nodes"][2]["responses"]=={"YES":"obs-b","NO":"obs-c","UNKNOWN":"stop-unknown"}
    assert c["versions"]["DETAILED"]["nodes"][2]["responses"]=={"YES":"obs-b","NO":"d4","UNKNOWN":"stop-unknown"}
    assert c["versions"]["DETAILED"]["nodes"][3]["responses"]=={"YES":"obs-d","NO":"d5","UNKNOWN":"stop-unknown"}
    assert c["versions"]["DETAILED"]["nodes"][4]["responses"]=={"YES":"obs-e","NO":"obs-c","UNKNOWN":"stop-unknown"}
    exts=c["extensions"]
    assert len(exts)==5 and len({e["title"] for e in exts})==5
    assert "ОМ12/ОМ22/ОМ32: вторичная гипотеза" in {e["title"] for e in exts}
    for e in exts:
        assert e["sourceId"]=="SECONDARY" and e["sourceStatus"]=="SECONDARY_996R_NOT_PRIMARY"
        assert e["displayMode"]=="EXTENDED_ONLY" and e["visibility"]==VIS
        assert e["actionDisposition"]=="INFORMATION_ONLY" and e["executable"] is False and e["actionAuthorityGranted"] is False and e["procedureSteps"]==[]
        graph({"startNodeId":e["nodes"][0]["id"],"nodes":e["nodes"]},4)
def negative(c,index,pack):
    m=[
        lambda x:x.update(runtimeImport=True),lambda x:x.update(executable=True),lambda x:x.update(publicationStatus="PUBLISHED"),
        lambda x:x.update(actionAuthorityGranted=True),lambda x:x.update(sourceAuthorityVerified=True),lambda x:x.update(humanSafetyReviewPassed=True),
        lambda x:x["applicability"].update(confirmedVariant="chme3"),lambda x:x["applicability"].update(installedSchemeVerified=True),
        lambda x:x["applicability"].update(unknownProfile="ALLOW"),lambda x:x["donor"].update(commit="HEAD"),
        lambda x:x["donor"].update(documentBlob="bad"),lambda x:x["donor"].update(documentPointer="/scenarios/4"),
        lambda x:x["donor"].update(gzipIndependentlyDecoded=True),lambda x:x["donor"].update(riskClass="LOW"),
        lambda x:x["donor"].update(evidenceStatus="CURRENT_APPROVED"),lambda x:x["donor"].update(equipmentIds=[]),
        lambda x:x["donor"].update(evidenceRefs=[]),lambda x:x["warning"].update(extendedHiddenByDefault=False),
        lambda x:x["warning"].update(readToEndRequired=False),lambda x:x["warning"].update(separateAcknowledgmentRequired=False),
        lambda x:x["warning"].update(grantsActionAuthority=True),lambda x:x["safety"].update(temporaryJumper=True),
        lambda x:x["safety"].update(relayForcedEnergization=True),
        lambda x:x["versions"]["SHORT"]["nodes"][0]["responses"].update(UNKNOWN="s2"),
        lambda x:x["versions"]["SHORT"]["nodes"][0]["responses"].update(NO="s2"),
        lambda x:x["versions"]["SHORT"]["nodes"][2]["responses"].update(YES="obs-c"),
        lambda x:x["versions"]["DETAILED"]["nodes"][2]["responses"].update(NO="obs-c"),
        lambda x:x["versions"]["DETAILED"]["nodes"][3]["responses"].update(YES="obs-c"),
        lambda x:x["versions"]["DETAILED"]["nodes"][4]["responses"].update(UNKNOWN="obs-c"),
        lambda x:x["versions"]["DETAILED"]["nodes"][0].update(permittedAction=True),
        lambda x:x["versions"]["SHORT"]["nodes"][1].update(text="Неизвестная позиция"),
        lambda x:x["versions"]["DETAILED"]["nodes"][2].update(text="Неизвестное реле"),
        lambda x:x["extensions"][0]["visibility"].update(warningAcknowledgedRequired=False),
        lambda x:x["extensions"][1].update(executable=True),lambda x:x["extensions"][2].update(procedureSteps=["unsafe"]),
        lambda x:x["extensions"][3]["nodes"][0]["responses"].update(UNKNOWN="e4-yes"),
        lambda x:x["extensions"][4]["nodes"][1].update(causeConfirmed=True),
        lambda x:x["sources"][0].update(currentVerified=True),lambda x:x["sources"][2].update(authority="ACTION_AUTHORIZED"),
        lambda x:x["sourceDiscrepancies"].pop(),lambda x:x["crossScenarioBoundaries"].pop(),
        lambda x:x["openGaps"].clear(),lambda x:x["deviceQA"].update(status="PASS"),
        lambda x:x["extensions"].pop(),lambda x:x["versions"]["DETAILED"]["nodes"].pop(),
        lambda x:x["branchContracts"]["SHORT"]["s3"].update(YES="obs-c")
    ]
    for i,mutate in enumerate(m):
        y=copy.deepcopy(c);mutate(y)
        try:check(y,index,pack)
        except (AssertionError,KeyError,IndexError):continue
        raise AssertionError(f"Unsafe mutation accepted: {i}")
    return len(m)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--negative",action="store_true");args=p.parse_args()
    c=read(PATH);idx=read(BASE+"migration/diagnostic-source-index.json");pack=read(PACK)
    check(c,idx,pack);n=negative(c,idx,pack) if args.negative else 0
    print("CHME3_BATCH71_PASS SCENARIOS 1 NEGATIVE",n)
