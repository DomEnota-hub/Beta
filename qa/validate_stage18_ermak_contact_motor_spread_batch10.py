#!/usr/bin/env python3
"""Stage18 Ermak emergency 033-035: source parity, fail-closed graph and negative mutation tests."""
import argparse, copy, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DOC=json.loads((ROOT/"docs/diagnostics/STAGE18_ERMAK_CONTACT_MOTOR_SPREAD_BATCH10_2026-11-06.json").read_text(encoding="utf-8"))
PACK=json.loads((ROOT/"content-packs/electric/ermak/diagnostics/recommended/diagnostics-02.pack.json").read_text(encoding="utf-8"))
SOURCE={e["id"]:e["sourceObject"]["object"] for e in PACK["entries"]}
IDS=["ER-DIAG-033","ER-DIAG-034","ER-DIAG-035"]
PIN="3176d6ee228f0ed4b78371f45209e10c1c724eff"
BLOB="c3a22c62db42308eb4b7ee44ff2da02f47686625"
def req(v,m):
    if not v: raise AssertionError(m)
def check(c):
    sid=c["originalId"];o=SOURCE[sid]
    for a,b in (("title","title"),("symptom","symptom"),("sourceObjectStatus","status"),("sourceObjectApplicability","applicability"),("sourceObjectSystemIds","systemIds"),("sourceObjectEquipmentRefs","equipmentRefs"),("sourceObjectSourceRefs","sourceRefs")):
        req(c[a]==o[b],sid+" donor "+a)
    req(c["families"]==o["applicability"]["families"] and c["profileApplicability"]==o["applicability"]["profiles"] and c["lateProfileRule"]==o["applicability"]["lateProfiles"],"profile parity")
    req(c["sourceObjectStatus"]=="CURRENT_RULE_CONFIRMED" and c["profileApplicability"]==["all_confirmed_profiles"],"original general rule status")
    r=c["sourceRecords"];d=r["donor"]
    req(d["commit"]==PIN and d["blobSha"]==BLOB and d["objectId"]==sid and d["proceduresImported"] is False and d["rawGzipIndependentlyDecoded"] is False,"donor provenance")
    req(set(r)=={"donor","emergency","fire","manual","variant"},"source set")
    req(all(v.get("currentOperatingAuthority") is False for v in r.values()),"source authority")
    req(r["emergency"]["exactRevisionVerified"] is False and r["fire"]["exactRevisionVerified"] is False,"source revision gate")
    req(c["publicationStatus"]=="CANDIDATE" and c["exactInstalledVariant"]=="UNKNOWN" and c["unknownVariantDisposition"]=="BLOCKED","publication")
    req(c["earlyMsud"]=="MSUD-N_ARCHIVAL_ONLY" and c["lateMsud"]=="MSUD-015_NOT_EQUIVALENT","MSUD distinction")
    for k in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified","exactInstalledVariantConfirmed","substantiveSafetyReviewed"):req(c[k] is False,k)
    w={"default":"HIDDEN","warningReadToEnd":True,"warningAcknowledged":True,"warningGrantsActionAuthority":False}
    req(c["warningGate"]==w,"warning")
    req(c["safePolicy"]=={"observationOnly":True,"onlyPreviouslyRecorded":True,"triState":["YES","NO","UNKNOWN"],"unknownMustStop":True,"unknownProfile":"BLOCKED","operationsAllowed":[],"activeEmergencyImmediateStop":True},"safe policy")
    req(c["deviceQA"]=="DEFERRED_TO_POST_RELEASE_DEVICE_QA","device QA")
    req(len(c["sourceConflicts"])==3 and c["sourceConflicts"][1]["resolution"]=="NO_OPERATION_IMPORT","conflicts")
    req(len(c["mustRemainDistinctFrom"])==2 and sid not in c["mustRemainDistinctFrom"],"distinctness")
    for mode,count in (("SHORT",6),("DETAILED",12)):
        g=c["versions"][mode];nodes=g["nodes"];by={n["id"]:n for n in nodes}
        req(len(nodes)==count and len(by)==count and g["authoringStatus"]=="RESEARCH_DRAFT_BLOCKED" and g["operatingInstructionsIncluded"] is False,"graph count/status")
        req(g["startNodeId"]=="q-emergency" and by["q-emergency"]["responses"]=={"YES":"stop-emergency","NO":("q-scope" if mode=="SHORT" else "q-profile"),"UNKNOWN":"stop-unknown"},"immediate emergency STOP")
        req(by["stop-emergency"]["type"]=="STOP" and by["stop-unknown"]["type"]=="STOP" and by["stop-mismatch"]["type"]=="STOP","emergency/unknown/mismatch terminal safety")
        seen=set();stack=[g["startNodeId"]]
        while stack:
            k=stack.pop();req(k in by,"dangling "+k)
            if k in seen:continue
            seen.add(k);n=by[k]
            req(n["recordedOnly"] is True and n["operationRequested"] is False and n["causeConfirmed"] is False,"unsafe node")
            req(n["sourceRefs"] and set(n["sourceRefs"])<=set(r),"source refs")
            if n["type"]=="QUESTION":
                req(set(n["responses"])=={"YES","NO","UNKNOWN"},"tri state")
                req(by[n["responses"]["UNKNOWN"]]["type"]=="STOP","UNKNOWN bypass")
                stack.extend(n["responses"].values())
            else:req(n["type"] in ("STOP","OBSERVATION_REPORT") and not n["responses"],"leaf")
        req(seen==set(by),"unreachable")
        if mode=="DETAILED":req(by["q-profile"]["responses"]["NO"]=="stop-profile" and by["stop-profile"]["type"]=="STOP","profile gate")
    ext=c["informationExtensions"]
    req(len(ext)==5 and len({x["id"] for x in ext})==5,"extensions")
    req([x["version"] for x in ext]==["SHORT","SHORT","DETAILED","DETAILED","DETAILED"],"extension modes")
    req({x["sourceRefs"][0] for x in ext}==set(r),"five distinct source extensions")
    for e in ext:
        req(len(e["sourceRefs"])==1 and e["sourceRefs"][0] in r and e["text"] and e["locator"],"extension provenance")
        req(e["visibility"]==w and e["warningRequired"] is True,"extension warning")
        req(e["actionAuthorityGranted"] is False and e["executable"] is False and e["operationalSteps"]==[],"extension operations")
        req(e["applicability"]=={"exactEquipmentProfileConfirmed":False,"modernSchemeConfirmed":False},"extension profile")
def negative(c):
    changes=[
        lambda x:x.update(publicationStatus="ACTIVE"),
        lambda x:x.update(runtimeImport=True),
        lambda x:x.update(executable=True),
        lambda x:x.update(actionAuthorityGranted=True),
        lambda x:x.update(sourceAuthorityVerified=True),
        lambda x:x.update(exactInstalledVariantConfirmed=True),
        lambda x:x.update(substantiveSafetyReviewed=True),
        lambda x:x.update(exactInstalledVariant="MSUD-015"),
        lambda x:x.update(unknownVariantDisposition="ALLOWED"),
        lambda x:x.update(earlyMsud="MSUD-015"),
        lambda x:x["sourceRecords"]["donor"].update(commit="bad"),
        lambda x:x["sourceRecords"]["donor"].update(blobSha="bad"),
        lambda x:x["sourceRecords"]["donor"].update(rawGzipIndependentlyDecoded=True),
        lambda x:x.update(title="bad"),
        lambda x:x.update(sourceObjectStatus="BASE_CONFIRMED"),
        lambda x:x["sourceObjectSystemIds"].append("FAKE"),
        lambda x:x["sourceObjectApplicability"].update(profiles=["base_early"]),
        lambda x:x["sourceRecords"]["emergency"].update(exactRevisionVerified=True),
        lambda x:x["sourceRecords"]["fire"].update(currentOperatingAuthority=True),
        lambda x:x["safePolicy"]["operationsAllowed"].append("switch"),
        lambda x:x["safePolicy"].update(onlyPreviouslyRecorded=False),
        lambda x:x["safePolicy"].update(activeEmergencyImmediateStop=False),
        lambda x:x["warningGate"].update(warningReadToEnd=False),
        lambda x:x["warningGate"].update(warningGrantsActionAuthority=True),
        lambda x:x["versions"]["SHORT"]["nodes"][0]["responses"].update(YES="q-scope"),
        lambda x:x["versions"]["SHORT"]["nodes"][0]["responses"].update(UNKNOWN="q-scope"),
        lambda x:x["versions"]["DETAILED"]["nodes"][0]["responses"].update(YES="q-profile"),
        lambda x:x["versions"]["DETAILED"]["nodes"][0].update(operationRequested=True),
        lambda x:x["versions"]["DETAILED"]["nodes"][1]["responses"].update(NO="q-scope"),
        lambda x:x["versions"]["DETAILED"]["nodes"][2]["responses"].pop("UNKNOWN"),
        lambda x:x["versions"]["SHORT"]["nodes"][1].update(recordedOnly=False),
        lambda x:x["informationExtensions"][0].update(actionAuthorityGranted=True),
        lambda x:x["informationExtensions"][0].update(sourceRefs=["FAKE"]),
        lambda x:x["informationExtensions"][0].update(warningRequired=False),
        lambda x:x["informationExtensions"].pop(),
        lambda x:x.update(deviceQA="PASS"),
        lambda x:x["sourceConflicts"][1].update(resolution="OPERATIONS_ALLOWED"),
        lambda x:x["mustRemainDistinctFrom"].append(x["originalId"]),
        lambda x:x["versions"]["DETAILED"]["nodes"][4]["responses"].update(UNKNOWN="q-evidence"),
        lambda x:x["versions"]["SHORT"]["nodes"][2].update(type="OBSERVATION_REPORT")
    ]
    for i,fn in enumerate(changes):
        v=copy.deepcopy(c);fn(v)
        try:check(v)
        except (AssertionError,KeyError):continue
        raise AssertionError("escaped negative mutation %d %s"%(i,c["originalId"]))
    return len(changes)
def main():
    p=argparse.ArgumentParser();p.add_argument("--negative",action="store_true");a=p.parse_args()
    l=DOC["ledger"]
    req(l["donorPinnedSha"]==PIN and l["donorGzipBlobSha"]==BLOB and l["sourceCatalogCount"]==136,"ledger donor")
    req(PACK["manifest"]["checksums"]["ermak_diagnostics.json.gz.gitBlob"]==BLOB,"donor blob")
    req(l["scenarioIds"]==IDS and [x["originalId"] for x in DOC["candidates"]]==IDS,"unique ordered IDs")
    req(l["status"]=="CANDIDATE" and l["runtimeImport"] is False and l["actionAuthorityGranted"] is False,"ledger gates")
    req(len({x["hazardCategory"] for x in DOC["candidates"]})==3,"independent hazards")
    count=0
    for c in DOC["candidates"]:
        check(c)
        if a.negative:count+=negative(c)
    print("STAGE18_BATCH10_PASS: 3 exact source IDs, 18 SHORT nodes, 36 DETAILED nodes, 15 information extensions")
    if a.negative:print("STAGE18_BATCH10_NEGATIVE_PASS:",count)
    print("CANDIDATE; no runtime; source/role/safety gates blocked; device QA deferred")
if __name__=="__main__":main()
