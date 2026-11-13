#!/usr/bin/env python3
"""Stage18 BV 007-009: pinned donor identity, independent graphs, source and fail-closed mutation QA."""
import argparse,copy,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
doc=json.loads((root/"docs/diagnostics/STAGE18_ERMAK_BV_BATCH3_2026-11-06.json").read_text())
pack=json.loads((root/"content-packs/electric/ermak/diagnostics/recommended/diagnostics-01.pack.json").read_text())
source={e["id"]:e["sourceObject"]["object"] for e in pack["entries"]}
ids=["ER-DIAG-007","ER-DIAG-008","ER-DIAG-009"]
pin="3176d6ee228f0ed4b78371f45209e10c1c724eff"
blob="c3a22c62db42308eb4b7ee44ff2da02f47686625"
def req(v,msg):
 if not v:raise AssertionError(msg)
def check(c):
 o=source[c["originalId"]]
 for a,b in (("title","title"),("symptom","symptom"),("sourceObjectStatus","status"),("sourceObjectApplicability","applicability"),("sourceObjectSystemIds","systemIds"),("sourceObjectEquipmentRefs","equipmentRefs"),("sourceObjectSourceRefs","sourceRefs")):req(c[a]==o[b],a)
 req(c["sourceObjectApplicability"]=={"families":["2ES5K","3ES5K"],"profiles":["base_early"],"lateProfiles":"REVALIDATION_REQUIRED"},"profile")
 req(c["sourceRecords"]["donor"]["commit"]==pin and c["sourceRecords"]["donor"]["blobSha"]==blob and c["sourceRecords"]["donor"]["objectId"]==c["originalId"],"pin")
 req(c["sourceRecords"]["manual"]["currentOperatingAuthority"] is False and c["sourceRecords"]["legacy"]["currentOperatingAuthority"] is False and c["sourceRecords"]["legacy"]["proceduresImported"] is False,"archival")
 req(c["sourceRecords"]["late"]["exactSerialVerified"] is False and c["sourceRecords"]["current"]["status"]=="UNKNOWN","modern")
 req(c["publicationStatus"]=="CANDIDATE" and c["exactInstalledVariant"]=="UNKNOWN" and c["unknownVariantDisposition"]=="BLOCKED","blocked")
 req(c["earlyMsud"]=="MSUD-N_HISTORICAL_ONLY" and c["lateMsud"]=="MSUD-015_REVALIDATION_REQUIRED","MSUD isolation")
 for k in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified","exactInstalledVariantConfirmed","substantiveSafetyReviewed"):req(c[k] is False,k)
 req(c["warningGate"]=={"default":"HIDDEN","warningReadToEnd":True,"warningAcknowledged":True,"warningGrantsActionAuthority":False},"warning")
 req(c["safePolicy"]=={"observationOnly":True,"onlyPreviouslyRecorded":True,"triState":["YES","NO","UNKNOWN"],"unknownMustStop":True,"unknownProfile":"BLOCKED","operationsAllowed":[]},"policy")
 req(c["deviceQA"]=="DEFERRED_TO_POST_RELEASE_DEVICE_QA","device")
 req(len(c["mustRemainDistinctFrom"])==2 and c["originalId"] not in c["mustRemainDistinctFrom"] and set(c["mustRemainDistinctFrom"])<=set(ids),"distinct")
 req(len(c["sourceConflicts"])==2 and all(x["resolution"] in ("NO_OPERATION_IMPORT","UNKNOWN/BLOCKED") for x in c["sourceConflicts"]),"conflicts")
 for v,count in (("SHORT",6),("DETAILED",12)):
  g=c["versions"][v];ns=g["nodes"];by={n["id"]:n for n in ns}
  req(len(ns)==count and len(by)==count and g["authoringStatus"]=="RESEARCH_DRAFT_BLOCKED" and g["operatingInstructionsIncluded"] is False,"graph")
  seen=set();stack=[g["startNodeId"]]
  while stack:
   nid=stack.pop();req(nid in by,"missing edge")
   if nid in seen:continue
   seen.add(nid);n=by[nid]
   req(n["recordedOnly"] is True and n["operationRequested"] is False and n["causeConfirmed"] is False,"unsafe node")
   req(n["sourceRefs"] and set(n["sourceRefs"])<=set(c["sourceRecords"]),"node provenance")
   if n["type"]=="QUESTION":
    req(set(n["responses"])=={"YES","NO","UNKNOWN"},"tri-state")
    req(by[n["responses"]["UNKNOWN"]]["type"]=="STOP","unknown bypass")
    stack.extend(n["responses"].values())
   else:req(n["type"] in ("STOP","OBSERVATION_REPORT") and not n["responses"],"leaf")
  req(seen==set(by),"unreachable")
 ex=c["informationExtensions"]
 req(len(ex)==5 and len({e["id"] for e in ex})==5,"extensions")
 req([e["version"] for e in ex]==["SHORT","SHORT","DETAILED","DETAILED","DETAILED"],"versions")
 req({e["sourceRefs"][0] for e in ex}=={"donor","manual","legacy","late"},"source approaches")
 for e in ex:
  req(len(e["sourceRefs"])==1 and e["sourceRefs"][0] in c["sourceRecords"] and e["locator"] and e["text"],"extension refs")
  req(e["warningRequired"] is True and e["visibility"]==c["warningGate"],"warning extension")
  req(e["actionAuthorityGranted"] is False and e["executable"] is False and e["operationalSteps"]==[],"extension actions")
  req(e["applicability"]=={"exactEquipmentProfileConfirmed":False,"modernSchemeConfirmed":False},"extension profile")
def negatives(c):
 changes=[
  lambda x:x.update(publicationStatus="ACTIVE"),lambda x:x.update(runtimeImport=True),
  lambda x:x.update(executable=True),lambda x:x.update(actionAuthorityGranted=True),
  lambda x:x.update(sourceAuthorityVerified=True),lambda x:x.update(exactInstalledVariantConfirmed=True),
  lambda x:x.update(substantiveSafetyReviewed=True),lambda x:x.update(exactInstalledVariant="MSUD-015"),
  lambda x:x.update(unknownVariantDisposition="ALLOWED"),lambda x:x.update(lateMsud="MSUD-N_EQUIVALENT"),
  lambda x:x["sourceRecords"]["donor"].update(commit="bad"),
  lambda x:x["sourceRecords"]["donor"].update(blobSha="bad"),
  lambda x:x.update(title="fake"),lambda x:x["sourceObjectSystemIds"].append("FAKE"),
  lambda x:x["sourceObjectApplicability"].update(profiles=["late"]),
  lambda x:x["sourceRecords"]["legacy"].update(currentOperatingAuthority=True),
  lambda x:x["sourceRecords"]["legacy"].update(proceduresImported=True),
  lambda x:x["sourceRecords"]["late"].update(exactSerialVerified=True),
  lambda x:x["sourceRecords"]["current"].update(status="VERIFIED"),
  lambda x:x["safePolicy"]["operationsAllowed"].append("switch"),
  lambda x:x["safePolicy"].update(onlyPreviouslyRecorded=False),
  lambda x:x["safePolicy"].update(unknownMustStop=False),
  lambda x:x["warningGate"].update(warningReadToEnd=False),
  lambda x:x["warningGate"].update(warningGrantsActionAuthority=True),
  lambda x:x["versions"]["SHORT"]["nodes"][0].update(operationRequested=True),
  lambda x:x["versions"]["DETAILED"]["nodes"][0].update(recordedOnly=False),
  lambda x:x["versions"]["SHORT"]["nodes"][0]["responses"].update(UNKNOWN="report-focus"),
  lambda x:x["versions"]["DETAILED"]["nodes"][0]["responses"].pop("NO"),
  lambda x:x["versions"]["DETAILED"]["nodes"][1]["responses"].update(NO="report-focus"),
  lambda x:x["informationExtensions"][0].update(actionAuthorityGranted=True),
  lambda x:x["informationExtensions"].pop(),
  lambda x:x["informationExtensions"][0].update(sourceRefs=["FAKE"]),
  lambda x:x["informationExtensions"][0].update(warningRequired=False),
  lambda x:x.update(deviceQA="PASS")
 ]
 for i,change in enumerate(changes):
  t=copy.deepcopy(c);change(t)
  try:check(t)
  except (AssertionError,KeyError):continue
  raise AssertionError("escaped mutation "+str(i))
 return len(changes)
def main():
 a=argparse.ArgumentParser();a.add_argument("--negative",action="store_true");args=a.parse_args()
 req(doc["ledger"]["donorPinnedSha"]==pin and doc["ledger"]["donorGzipBlobSha"]==blob,"ledger pin")
 req(pack["manifest"]["checksums"]["ermak_diagnostics.json.gz.gitBlob"]==blob,"pack checksum")
 req(doc["ledger"]["scenarioIds"]==ids and len(doc["candidates"])==3,"ID count")
 req(len(set(ids))==3 and all(x["originalId"]==ids[i] for i,x in enumerate(doc["candidates"])),"order")
 total=0
 for c in doc["candidates"]:
  check(c)
  if args.negative:total+=negatives(c)
 print("STAGE18_ERMAK_BV_BATCH3_PASS: 3 IDs, 18 SHORT nodes, 36 DETAILED nodes, 15 extensions")
 if args.negative:print("STAGE18_ERMAK_BV_BATCH3_NEGATIVE_PASS:",total)
 print("CANDIDATE; runtime BLOCKED; device QA deferred")
if __name__=="__main__":main()
