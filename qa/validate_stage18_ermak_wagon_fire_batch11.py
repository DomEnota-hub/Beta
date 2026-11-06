#!/usr/bin/env python3
"""ER-DIAG-036: exact pinned projection, graph, emergency fail-closed and mutation gates."""
import argparse,copy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DOC=json.loads((ROOT/"docs/diagnostics/STAGE18_ERMAK_WAGON_FIRE_BATCH11_2026-11-06.json").read_text(encoding="utf-8"))
PACK=json.loads((ROOT/"content-packs/electric/ermak/diagnostics/recommended/diagnostics-02.pack.json").read_text(encoding="utf-8"))
ID="ER-DIAG-036"
SRC=next(e["sourceObject"]["object"] for e in PACK["entries"] if e["id"]==ID)
def req(v,m):
    if not v: raise AssertionError(m)
def check(c):
    req(c["originalId"]==ID and c["scenarioId"]=="ermak.diag."+ID,"id")
    for a,b in (("title","title"),("symptom","symptom"),("sourceObjectStatus","status"),("sourceObjectApplicability","applicability"),("sourceObjectSystemIds","systemIds"),("sourceObjectEquipmentRefs","equipmentRefs"),("sourceObjectSourceRefs","sourceRefs")):
        req(c[a]==SRC[b],"pinned "+a)
    req(c["families"]==SRC["applicability"]["families"] and c["profileApplicability"]==SRC["applicability"]["profiles"] and c["lateProfileRule"]==SRC["applicability"]["lateProfiles"],"applicability")
    req(c["sourceObjectStatus"]=="CURRENT_RULE_CONFIRMED","donor status, not operational authority")
    req(c["hazardCategory"]=="WAGON_FIRE_CARGO_UNKNOWN","wagon scope")
    req(set(c["mustRemainDistinctFrom"])=={"ER-DIAG-032","ER-DIAG-035","ER-DIAG-127"},"not locomotive fire")
    r=c["sourceRecords"]
    req(set(r)=={"donor","emergency","fire","cargo","variant"},"source set")
    req(r["donor"]["commit"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff" and r["donor"]["blobSha"]=="c3a22c62db42308eb4b7ee44ff2da02f47686625" and r["donor"]["objectId"]==ID,"pin")
    req(r["donor"]["rawGzipIndependentlyDecoded"] is False and r["donor"]["proceduresImported"] is False,"donor limitations")
    req(all(x.get("currentOperatingAuthority") is False for x in r.values()),"source authority")
    req(r["emergency"]["exactRevisionVerified"] is False and r["fire"]["exactRevisionVerified"] is False and r["cargo"]["exactCargoCardVerified"] is False,"missing source gate")
    req(c["publicationStatus"]=="CANDIDATE" and c["exactInstalledVariant"]=="UNKNOWN" and c["unknownVariantDisposition"]=="BLOCKED","publication/profile")
    req(c["earlyMsud"]=="MSUD-N_ARCHIVAL_ONLY" and c["lateMsud"]=="MSUD-015_NOT_EQUIVALENT","variant")
    for k in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified","exactInstalledVariantConfirmed","substantiveSafetyReviewed"):req(c[k] is False,k)
    w={"default":"HIDDEN","warningReadToEnd":True,"warningAcknowledged":True,"warningGrantsActionAuthority":False}
    req(c["warningGate"]==w,"warning")
    req(c["safePolicy"]=={"observationOnly":True,"onlyPreviouslyRecorded":True,"triState":["YES","NO","UNKNOWN"],"unknownMustStop":True,"unknownProfile":"BLOCKED","operationsAllowed":[],"activeEmergencyImmediateStop":True},"safe policy")
    req(c["deviceQA"]=="DEFERRED_TO_POST_RELEASE_DEVICE_QA","device")
    req([x["resolution"] for x in c["sourceConflicts"]]==["SOURCE_AUTHORITY_BLOCKED","NO_OPERATION_IMPORT","UNKNOWN/BLOCKED"],"conflicts")
    for mode,count in (("SHORT",6),("DETAILED",12)):
        g=c["versions"][mode];nodes=g["nodes"];by={x["id"]:x for x in nodes}
        req(len(nodes)==len(by)==count and g["authoringStatus"]=="RESEARCH_DRAFT_BLOCKED" and g["operatingInstructionsIncluded"] is False,"graph count")
        req(g["startNodeId"]=="q-emergency" and by["q-emergency"]["responses"]=={"YES":"stop-emergency","NO":"q-scope" if mode=="SHORT" else "q-profile","UNKNOWN":"stop-unknown"},"emergency STOP")
        req(by["stop-emergency"]["type"]==by["stop-unknown"]["type"]=="STOP","STOP type")
        seen=set();stack=[g["startNodeId"]]
        while stack:
            k=stack.pop();req(k in by,"dangling")
            if k in seen:continue
            seen.add(k);n=by[k]
            req(n["recordedOnly"] is True and n["operationRequested"] is False and n["causeConfirmed"] is False,"unsafe node")
            req(n["sourceRefs"] and set(n["sourceRefs"])<=set(r),"source refs")
            if n["type"]=="QUESTION":
                req(set(n["responses"])=={"YES","NO","UNKNOWN"},"tri-state")
                req(by[n["responses"]["UNKNOWN"]]["type"]=="STOP","UNKNOWN bypass")
                stack.extend(n["responses"].values())
            else:req(n["type"] in ("STOP","OBSERVATION_REPORT") and n["responses"]=={},"leaf")
        req(seen==set(by),"unreachable")
        if mode=="DETAILED":
            req(by["q-profile"]["responses"]["NO"]=="stop-profile" and by["stop-profile"]["type"]=="STOP","profile")
            req(by["q-cargo"]["responses"]["NO"]=="report-unconfirmed" and by["report-unconfirmed"]["type"]=="STOP","cargo")
    ext=c["informationExtensions"]
    req(len(ext)==5 and len({x["id"] for x in ext})==5,"extensions")
    req([x["version"] for x in ext]==["SHORT","SHORT","DETAILED","DETAILED","DETAILED"],"extension modes")
    req({x["sourceRefs"][0] for x in ext}==set(r),"extension provenance")
    for e in ext:
        req(len(e["sourceRefs"])==1 and e["sourceRefs"][0] in r and e["text"] and e["locator"],"extension source")
        req(e["visibility"]==w and e["warningRequired"] is True,"extension warning")
        req(e["actionAuthorityGranted"] is False and e["executable"] is False and e["operationalSteps"]==[],"extension safety")
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
        lambda x:x.update(hazardCategory="LOCOMOTIVE_FIRE"),
        lambda x:x.update(title="wrong"),
        lambda x:x.update(sourceObjectStatus="ARCHIVAL"),
        lambda x:x["sourceObjectSystemIds"].append("FAKE"),
        lambda x:x["sourceObjectApplicability"].update(profiles=["base_early"]),
        lambda x:x["sourceRecords"]["donor"].update(commit="bad"),
        lambda x:x["sourceRecords"]["donor"].update(blobSha="bad"),
        lambda x:x["sourceRecords"]["donor"].update(rawGzipIndependentlyDecoded=True),
        lambda x:x["sourceRecords"]["cargo"].update(exactCargoCardVerified=True),
        lambda x:x["sourceRecords"]["emergency"].update(exactRevisionVerified=True),
        lambda x:x["sourceRecords"]["fire"].update(currentOperatingAuthority=True),
        lambda x:x["safePolicy"]["operationsAllowed"].append("uncouple"),
        lambda x:x["safePolicy"].update(onlyPreviouslyRecorded=False),
        lambda x:x["safePolicy"].update(activeEmergencyImmediateStop=False),
        lambda x:x["warningGate"].update(warningReadToEnd=False),
        lambda x:x["warningGate"].update(warningGrantsActionAuthority=True),
        lambda x:x["versions"]["SHORT"]["nodes"][0]["responses"].update(YES="q-scope"),
        lambda x:x["versions"]["SHORT"]["nodes"][0]["responses"].update(UNKNOWN="q-scope"),
        lambda x:x["versions"]["DETAILED"]["nodes"][0]["responses"].update(YES="q-profile"),
        lambda x:x["versions"]["DETAILED"]["nodes"][1]["responses"].update(NO="q-scope"),
        lambda x:x["versions"]["DETAILED"]["nodes"][4]["responses"].update(UNKNOWN="q-evidence"),
        lambda x:x["versions"]["DETAILED"]["nodes"][4]["responses"].update(NO="q-evidence"),
        lambda x:x["versions"]["DETAILED"]["nodes"][4].update(operationRequested=True),
        lambda x:x["versions"]["SHORT"]["nodes"][1].update(recordedOnly=False),
        lambda x:x["informationExtensions"][0].update(actionAuthorityGranted=True),
        lambda x:x["informationExtensions"][0].update(sourceRefs=["FAKE"]),
        lambda x:x["informationExtensions"][0].update(warningRequired=False),
        lambda x:x["informationExtensions"].pop(),
        lambda x:x.update(deviceQA="PASS"),
        lambda x:x["sourceConflicts"][1].update(resolution="OPERATIONS_ALLOWED"),
        lambda x:x["mustRemainDistinctFrom"].append(ID)
    ]
    for i,fn in enumerate(changes):
        v=copy.deepcopy(c);fn(v)
        try:check(v)
        except (AssertionError,KeyError):continue
        raise AssertionError("escaped negative mutation %d"%i)
    return len(changes)
def main():
    a=argparse.ArgumentParser();a.add_argument("--negative",action="store_true");args=a.parse_args()
    l=DOC["ledger"];req(l["scenarioIds"]==[ID] and l["status"]=="CANDIDATE" and l["runtimeImport"] is False,"ledger")
    req(l["donorPinnedSha"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff" and l["donorGzipBlobSha"]=="c3a22c62db42308eb4b7ee44ff2da02f47686625","pin")
    req(PACK["manifest"]["checksums"]["ermak_diagnostics.json.gz.gitBlob"]==l["donorGzipBlobSha"],"blob")
    req(len(DOC["candidates"])==1,"candidate count")
    check(DOC["candidates"][0])
    print("STAGE18_BATCH11_PASS: ER-DIAG-036 exact source, SHORT 6, DETAILED 12, five expansions, cargo-card BLOCKED")
    if args.negative:print("STAGE18_BATCH11_NEGATIVE_PASS:",negative(DOC["candidates"][0]))
if __name__=="__main__":main()
