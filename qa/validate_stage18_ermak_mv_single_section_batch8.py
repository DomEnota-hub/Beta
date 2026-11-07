#!/usr/bin/env python3
"""Pinned donor, graph, provenance, fail-closed and mutation QA for Ermak batch8."""
import argparse,copy,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
doc=json.loads((root/"docs/diagnostics/STAGE18_ERMAK_MV_SINGLE_SECTION_BATCH8_2026-11-06.json").read_text())
packs=[json.loads((root/p).read_text()) for p in ("content-packs/electric/ermak/diagnostics/recommended/diagnostics-01.pack.json","content-packs/electric/ermak/diagnostics/recommended/diagnostics-02.pack.json")]
source={e["id"]:e["sourceObject"]["object"] for p in packs for e in p["entries"]}
ids=["ER-DIAG-028","ER-DIAG-029"]
pin="3176d6ee228f0ed4b78371f45209e10c1c724eff";blob="c3a22c62db42308eb4b7ee44ff2da02f47686625"
def req(v,msg):
 if not v:raise AssertionError(msg)
def check(c):
 o=source[c["originalId"]]
 for a,b in (("title","title"),("symptom","symptom"),("sourceObjectStatus","status"),("sourceObjectApplicability","applicability"),("sourceObjectSystemIds","systemIds"),("sourceObjectEquipmentRefs","equipmentRefs"),("sourceObjectSourceRefs","sourceRefs")):req(c[a]==o[b],a)
 req(c["families"]==o["applicability"]["families"],"families")
 req(c["sourceRecords"]["donor"]["commit"]==pin and c["sourceRecords"]["donor"]["blobSha"]==blob and c["sourceRecords"]["donor"]["objectId"]==c["originalId"],"donor")
 req(c["sourceRecords"]["manual"]["currentOperatingAuthority"] is False and c["sourceRecords"]["legacy"]["proceduresImported"] is False and c["sourceRecords"]["legacy"]["currentOperatingAuthority"] is False,"legacy")
 req(c["sourceRecords"]["ventilation"]["currentOperatingAuthority"] is False and c["sourceRecords"]["ventilation"]["exactSerialVerified"] is False and c["sourceRecords"]["ventilation"]["title"]=="ИДМБ.661142.009РЭ2","ventilation")
 req(c["sourceRecords"]["late"]["exactSerialVerified"] is False and c["sourceRecords"]["current"]["status"]=="UNKNOWN","modern")
 req(c["publicationStatus"]=="CANDIDATE" and c["exactInstalledVariant"]=="UNKNOWN" and c["unknownVariantDisposition"]=="BLOCKED","blocked")
 req(c["earlyMsud"]=="MSUD-N_HISTORICAL_ONLY" and c["lateMsud"]=="MSUD-015_REVALIDATION_REQUIRED","msud")
 for k in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified","exactInstalledVariantConfirmed","substantiveSafetyReviewed"):req(c[k] is False,k)
 req(c["warningGate"]=={"default":"HIDDEN","warningReadToEnd":True,"warningAcknowledged":True,"warningGrantsActionAuthority":False},"warning")
 req(c["safePolicy"]=={"observationOnly":True,"onlyPreviouslyRecorded":True,"triState":["YES","NO","UNKNOWN"],"unknownMustStop":True,"unknownProfile":"BLOCKED","operationsAllowed":[]},"policy")
 req(c["deviceQA"]=="DEFERRED_TO_POST_RELEASE_DEVICE_QA","device")
 req(c["sourceRecords"]["legacy"]["locator"].startswith("№671р п. ") and "восстановление" in c["sourceRecords"]["legacy"]["locator"],"historical procedures excluded")
 req(len(c["mustRemainDistinctFrom"])==2 and c["originalId"] not in c["mustRemainDistinctFrom"] and all(x in source for x in c["mustRemainDistinctFrom"]),"distinct")
 req(len(c["sourceConflicts"])==3 and {x["resolution"] for x in c["sourceConflicts"]}=={"NO_OPERATION_IMPORT","UNKNOWN/BLOCKED"},"conflicts")
 for v,count in (("SHORT",6),("DETAILED",12)):
  g=c["versions"][v];ns=g["nodes"];by={n["id"]:n for n in ns}
  req(len(ns)==count and len(by)==count and g["authoringStatus"]=="RESEARCH_DRAFT_BLOCKED" and g["operatingInstructionsIncluded"] is False,"graph")
  seen=set();stack=[g["startNodeId"]]
  while stack:
   k=stack.pop();req(k in by,"dangling")
   if k in seen:continue
   seen.add(k);n=by[k]
   req(n["recordedOnly"] is True and n["operationRequested"] is False and n["causeConfirmed"] is False,"unsafe node")
   req(n["sourceRefs"] and set(n["sourceRefs"])<=set(c["sourceRecords"]),"provenance")
   if n["type"]=="QUESTION":
    req(set(n["responses"])=={"YES","NO","UNKNOWN"},"tri-state")
    req(by[n["responses"]["UNKNOWN"]]["type"]=="STOP","unknown bypass")
    stack.extend(n["responses"].values())
   else:req(n["type"] in ("STOP","OBSERVATION_REPORT") and not n["responses"],"leaf")
  req(seen==set(by),"unreachable")
  if v=="DETAILED":req(by["q-variant"]["responses"]["NO"]=="stop-profile","profile")
 ex=c["informationExtensions"]
 req(len(ex)==5 and len({e["id"] for e in ex})==5,"extensions")
 req([e["version"] for e in ex]==["SHORT","SHORT","DETAILED","DETAILED","DETAILED"],"extension versions")
 req({e["sourceRefs"][0] for e in ex}=={"donor","manual","legacy","ventilation","late"},"extension sources")
 for e in ex:
  req(len(e["sourceRefs"])==1 and e["sourceRefs"][0] in c["sourceRecords"] and e["locator"] and e["text"],"refs")
  req(e["warningRequired"] is True and e["visibility"]==c["warningGate"],"warning extension")
  req(e["actionAuthorityGranted"] is False and e["executable"] is False and e["operationalSteps"]==[],"extension actions")
  req(e["applicability"]=={"exactEquipmentProfileConfirmed":False,"modernSchemeConfirmed":False},"extension applicability")
def negative(c):
 changes=[
 lambda x:x.update(publicationStatus="ACTIVE"),lambda x:x.update(runtimeImport=True),
 lambda x:x.update(executable=True),lambda x:x.update(actionAuthorityGranted=True),
 lambda x:x.update(sourceAuthorityVerified=True),lambda x:x.update(exactInstalledVariantConfirmed=True),
 lambda x:x.update(substantiveSafetyReviewed=True),lambda x:x.update(exactInstalledVariant="MSUD-015"),
 lambda x:x.update(unknownVariantDisposition="ALLOWED"),lambda x:x.update(lateMsud="MSUD-N_EQUIVALENT"),
 lambda x:x["sourceRecords"]["donor"].update(commit="bad"),lambda x:x["sourceRecords"]["donor"].update(blobSha="bad"),
 lambda x:x.update(title="bad"),lambda x:x["sourceObjectSystemIds"].append("FAKE"),
 lambda x:x["sourceObjectApplicability"].update(profiles=["late"]),
 lambda x:x["sourceRecords"]["legacy"].update(currentOperatingAuthority=True),
 lambda x:x["sourceRecords"]["legacy"].update(proceduresImported=True),
 lambda x:x["sourceRecords"]["ventilation"].update(exactSerialVerified=True),
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
 for i,f in enumerate(changes):
  y=copy.deepcopy(c);f(y)
  try:check(y)
  except (AssertionError,KeyError):continue
  raise AssertionError("escaped mutation "+str(i))
 return len(changes)
def main():
 p=argparse.ArgumentParser();p.add_argument("--negative",action="store_true");a=p.parse_args()
 req(doc["ledger"]["donorPinnedSha"]==pin and doc["ledger"]["donorGzipBlobSha"]==blob,"pin")
 for pack in packs:req(pack["manifest"]["checksums"]["ermak_diagnostics.json.gz.gitBlob"]==blob,"checksum")
 req(doc["ledger"]["batchBoundary"].startswith("028-029 only") and doc["ledger"]["runtimeImport"] is False,"boundary")
 req(doc["ledger"]["scenarioIds"]==ids and [x["originalId"] for x in doc["candidates"]]==ids,"IDs")
 req([source[x]["sourceRefs"][0]["locator"] for x in ids]==["таблица, п. 28","таблица, п. 29"],"source locator")
 req(all(c["families"]==["2ES5K","3ES5K"] for c in doc["candidates"]),"family isolation")
 req(len({c["versions"]["DETAILED"]["nodes"][2]["text"] for c in doc["candidates"]})==2,"distinct")
 req(len({c["versions"]["DETAILED"]["nodes"][3]["text"] for c in doc["candidates"]})==2,"evidence")
 req([c["sourceRecords"]["legacy"]["locator"].split(":")[0] for c in doc["candidates"]]==["№671р п. 28","№671р п. 29"],"legacy section")
 req(all("вспышка" not in c["title"].lower() and "пожар" not in c["title"].lower() for c in doc["candidates"]),"hazard split")
 total=0
 for c in doc["candidates"]:
  check(c)
  if a.negative:total+=negative(c)
 print("STAGE18_BATCH8_PASS: 2 IDs, 12 SHORT nodes, 24 DETAILED nodes, 10 extensions")
 if a.negative:print("STAGE18_BATCH8_NEGATIVE_PASS:",total)
 print("CANDIDATE, runtime BLOCKED, device QA deferred")
if __name__=="__main__":main()
