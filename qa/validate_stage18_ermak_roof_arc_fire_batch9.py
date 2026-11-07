#!/usr/bin/env python3
"""Stage18 Ermak emergency 030-032: pinned-source parity, graph and negative safety QA."""
import argparse, copy, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DOC=json.loads((ROOT/"docs/diagnostics/STAGE18_ERMAK_ROOF_ARC_FIRE_BATCH9_2026-11-06.json").read_text(encoding="utf-8"))
PACK=json.loads((ROOT/"content-packs/electric/ermak/diagnostics/recommended/diagnostics-02.pack.json").read_text(encoding="utf-8"))
SOURCE={e["id"]:e["sourceObject"]["object"] for e in PACK["entries"]}
IDS=["ER-DIAG-030","ER-DIAG-031","ER-DIAG-032"]
PIN="3176d6ee228f0ed4b78371f45209e10c1c724eff"
BLOB="c3a22c62db42308eb4b7ee44ff2da02f47686625"
def req(value, message):
    if not value: raise AssertionError(message)
def check(c):
    sid=c["originalId"]; o=SOURCE[sid]
    for a,b in (("title","title"),("symptom","symptom"),("sourceObjectStatus","status"),("sourceObjectApplicability","applicability"),("sourceObjectSystemIds","systemIds"),("sourceObjectEquipmentRefs","equipmentRefs"),("sourceObjectSourceRefs","sourceRefs")):
        req(c[a]==o[b],sid+" donor "+a)
    req(c["families"]==o["applicability"]["families"] and c["profileApplicability"]==o["applicability"]["profiles"] and c["lateProfileRule"]==o["applicability"]["lateProfiles"],"profile parity")
    r=c["sourceRecords"];d=r["donor"]
    req(d["commit"]==PIN and d["blobSha"]==BLOB and d["objectId"]==sid and d["proceduresImported"] is False and d["rawGzipIndependentlyDecoded"] is False,"donor provenance")
    req(sid!="ER-DIAG-030" or ("legacy" in r and "п.30" in r["legacy"]["locator"] and r["legacy"]["proceduresImported"] is False),"historical roof")
    req(sid=="ER-DIAG-030" or "legacy" not in r,"no invented 671r fire item")
    req(all(v.get("currentOperatingAuthority") is False for v in r.values()),"source authority")
    req(r["emergency"]["exactRevisionVerified"] is False and r["fire"]["exactRevisionVerified"] is False,"revision gate")
    req(c["publicationStatus"]=="CANDIDATE" and c["exactInstalledVariant"]=="UNKNOWN" and c["unknownVariantDisposition"]=="BLOCKED","publication")
    req(c["earlyMsud"]=="MSUD-N_ARCHIVAL_ONLY" and c["lateMsud"]=="MSUD-015_NOT_EQUIVALENT","MSUD split")
    for k in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified","exactInstalledVariantConfirmed","substantiveSafetyReviewed"): req(c[k] is False,k)
    w={"default":"HIDDEN","warningReadToEnd":True,"warningAcknowledged":True,"warningGrantsActionAuthority":False}
    req(c["warningGate"]==w,"warning gate")
    req(c["safePolicy"]=={"observationOnly":True,"onlyPreviouslyRecorded":True,"triState":["YES","NO","UNKNOWN"],"unknownMustStop":True,"unknownProfile":"BLOCKED","operationsAllowed":[],"activeEmergencyImmediateStop":True},"safe policy")
    req(c["deviceQA"]=="DEFERRED_TO_POST_RELEASE_DEVICE_QA","device QA")
    req(len(c["sourceConflicts"])==3 and c["sourceConflicts"][0]["resolution"]=="NO_OPERATION_IMPORT","source conflicts")
    req(sid not in c["mustRemainDistinctFrom"] and len(c["mustRemainDistinctFrom"])==2,"scenario isolation")
    for name,ncount in (("SHORT",6),("DETAILED",12)):
        g=c["versions"][name]; nodes=g["nodes"]; by={n["id"]:n for n in nodes}
        req(len(nodes)==ncount and len(by)==ncount and g["authoringStatus"]=="RESEARCH_DRAFT_BLOCKED" and g["operatingInstructionsIncluded"] is False,"graph length")
        start=by[g["startNodeId"]]
        req(start["id"]=="q-emergency" and start["responses"]=={"YES":"stop-emergency","NO":("q-scope" if name=="SHORT" else "q-profile"),"UNKNOWN":"stop-unknown"},"immediate emergency STOP")
        req(by["stop-emergency"]["type"]=="STOP" and by["stop-unknown"]["type"]=="STOP","emergency leaves")
        seen=set(); stack=[g["startNodeId"]]
        while stack:
            k=stack.pop(); req(k in by,"dangling "+k)
            if k in seen: continue
            seen.add(k); n=by[k]
            req(n["recordedOnly"] is True and n["operationRequested"] is False and n["causeConfirmed"] is False,"unsafe node")
            req(n["sourceRefs"] and set(n["sourceRefs"])<=set(r),"source reference")
            if n["type"]=="QUESTION":
                req(set(n["responses"])=={"YES","NO","UNKNOWN"},"tri-state")
                req(by[n["responses"]["UNKNOWN"]]["type"]=="STOP","UNKNOWN bypass")
                stack.extend(n["responses"].values())
            else: req(n["type"] in ("STOP","OBSERVATION_REPORT") and not n["responses"],"leaf")
        req(seen==set(by),"unreachable")
        if name=="DETAILED": req(by["q-profile"]["responses"]["NO"]=="stop-profile" and by["stop-profile"]["type"]=="STOP","profile fail-closed")
    ext=c["informationExtensions"]
    req(len(ext)==5 and len({x["id"] for x in ext})==5,"extension count")
    req([x["version"] for x in ext]==["SHORT","SHORT","DETAILED","DETAILED","DETAILED"],"extension layers")
    req({x["sourceRefs"][0] for x in ext}==({"donor","legacy","manual","emergency","variant"} if sid=="ER-DIAG-030" else {"donor","fire","manual","emergency","variant"}),"independent extensions")
    for e in ext:
        req(len(e["sourceRefs"])==1 and e["sourceRefs"][0] in r and e["text"] and e["locator"],"extension provenance")
        req(e["visibility"]==w and e["warningRequired"] is True,"extension warning")
        req(e["actionAuthorityGranted"] is False and e["executable"] is False and e["operationalSteps"]==[],"extension operation")
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
        lambda x:x.update(sourceObjectStatus="bad"),
        lambda x:x["sourceObjectSystemIds"].append("FAKE"),
        lambda x:x["sourceObjectApplicability"].update(profiles=["late"]),
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
    ]
    for i,f in enumerate(changes):
        v=copy.deepcopy(c); f(v)
        try: check(v)
        except (AssertionError,KeyError): continue
        raise AssertionError("escaped mutation %s for %s"%(i,c["originalId"]))
    return len(changes)
def main():
    p=argparse.ArgumentParser();p.add_argument("--negative",action="store_true");a=p.parse_args()
    l=DOC["ledger"]
    req(l["donorPinnedSha"]==PIN and l["donorGzipBlobSha"]==BLOB and l["sourceCatalogCount"]==136,"ledger")
    req(PACK["manifest"]["checksums"]["ermak_diagnostics.json.gz.gitBlob"]==BLOB,"donor pack")
    req(l["scenarioIds"]==IDS and [c["originalId"] for c in DOC["candidates"]]==IDS,"unique ordered IDs")
    req(l["runtimeImport"] is False and l["actionAuthorityGranted"] is False and l["status"]=="CANDIDATE","ledger publication")
    req([SOURCE[i]["sourceRefs"][0]["locator"] for i in IDS]==["таблица, п. 30","раздел 19, пп. 19.1–19.8","раздел 19, пп. 19.1–19.8"],"source locators")
    req(len({c["hazardCategory"] for c in DOC["candidates"]})==3,"hazard distinction")
    total=0
    for c in DOC["candidates"]:
        check(c)
        if a.negative: total+=negative(c)
    print("STAGE18_BATCH9_PASS: 3 donor IDs, 18 SHORT nodes, 36 DETAILED nodes, 15 extensions")
    if a.negative: print("STAGE18_BATCH9_NEGATIVE_PASS:",total)
    print("CANDIDATE, no runtime, device QA deferred")
if __name__=="__main__":main()
