#!/usr/bin/env python3
"""Stage18 Ermak second three original IDs: graph, source, fail-closed and mutation QA."""
import argparse,copy,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
doc=json.loads((root/"docs/diagnostics/STAGE18_ERMAK_CONTROL_HV_BATCH2_2026-11-06.json").read_text())
pack=json.loads((root/"content-packs/electric/ermak/diagnostics/recommended/diagnostics-01.pack.json").read_text())
source={e["id"]:e for e in pack["entries"]}
ids=["ER-DIAG-004","ER-DIAG-005","ER-DIAG-006"]
pin="3176d6ee228f0ed4b78371f45209e10c1c724eff";blob="c3a22c62db42308eb4b7ee44ff2da02f47686625"
def req(x,s):
 if not x:raise AssertionError(s)
def check(c):
 o=source[c["originalId"]]["sourceObject"]["object"]
 req(c["title"]==o["title"] and c["symptom"]==o["symptom"],"source title/symptom")
 req(c["sourceObjectApplicability"]==o["applicability"] and c["sourceObjectSystemIds"]==o["systemIds"] and c["sourceObjectEquipmentRefs"]==o["equipmentRefs"],"donor identity")
 req(c["sourceObjectApplicability"]["profiles"]==["base_early"] and c["sourceObjectApplicability"]["lateProfiles"]=="REVALIDATION_REQUIRED","donor profile")
 req(c["sourceRecords"]["donor"]["commit"]==pin and c["sourceRecords"]["donor"]["blobSha"]==blob,"pin/blob")
 req(c["sourceRecords"]["legacy"]["currentOperatingAuthority"] is False and c["sourceRecords"]["legacy"]["proceduresImported"] is False,"superseded")
 req(c["sourceRecords"]["manual"]["currentOperatingAuthority"] is False and c["sourceRecords"]["late"]["exactSerialVerified"] is False,"source scope")
 req(c["sourceRecords"]["current"]["status"]=="UNKNOWN","modern authority")
 req(c["publicationStatus"]=="CANDIDATE" and c["exactInstalledVariant"]=="UNKNOWN" and c["unknownVariantDisposition"]=="BLOCKED","publication/profile")
 req(c["earlyMsud"]=="MSUD-N_HISTORICAL_ONLY" and c["lateMsud"]=="MSUD-015_REVALIDATION_REQUIRED","msud isolation")
 for k in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified","exactInstalledVariantConfirmed","substantiveSafetyReviewed"):req(c[k] is False,k)
 req(c["warningGate"]=={"default":"HIDDEN","warningReadToEnd":True,"warningAcknowledged":True,"warningGrantsActionAuthority":False},"warning")
 req(c["safePolicy"]=={"observationOnly":True,"onlyPreviouslyRecorded":True,"triState":["YES","NO","UNKNOWN"],"unknownMustStop":True,"unknownProfile":"BLOCKED","operationsAllowed":[]},"policy")
 req(c["deviceQA"]=="DEFERRED_TO_POST_RELEASE_DEVICE_QA","device")
 req(len(c["mustRemainDistinctFrom"])==2 and len(c["sourceConflicts"])==2,"distinct")
 for version,count in (("SHORT",6),("DETAILED",12)):
  g=c["versions"][version];ns=g["nodes"];by={n["id"]:n for n in ns}
  req(len(ns)==count and len(by)==count and g["operatingInstructionsIncluded"] is False and g["authoringStatus"]=="RESEARCH_DRAFT_BLOCKED","graph count")
  seen=set();stack=[g["startNodeId"]]
  while stack:
   nid=stack.pop();req(nid in by,"missing edge")
   if nid in seen:continue
   seen.add(nid);n=by[nid]
   req(n["recordedOnly"] is True and n["operationRequested"] is False and n["causeConfirmed"] is False,"unsafe node")
   req(n["sourceRefs"] and set(n["sourceRefs"])<=set(c["sourceRecords"]),"source ref")
   if n["type"]=="QUESTION":
    req(set(n["responses"])=={"YES","NO","UNKNOWN"},"tri-state")
    req(by[n["responses"]["UNKNOWN"]]["type"]=="STOP","UNKNOWN not STOP")
    stack.extend(n["responses"].values())
   else:req(n["type"] in {"STOP","OBSERVATION_REPORT"} and not n["responses"],"leaf")
  req(seen==set(by),"unreachable")
 ex=c["informationExtensions"]
 req(len(ex)==5 and len({e["id"] for e in ex})==5,"extensions")
 req([e["version"] for e in ex]==["SHORT","SHORT","DETAILED","DETAILED","DETAILED"],"extension versions")
 req({e["sourceRefs"][0] for e in ex}=={"donor","manual","legacy","late"},"source approaches")
 for e in ex:
  req(len(e["sourceRefs"])==1 and e["sourceRefs"][0] in c["sourceRecords"] and e["locator"] and e["text"],"extension source")
  req(e["warningRequired"] is True and e["visibility"]==c["warningGate"],"extension warning")
  req(e["actionAuthorityGranted"] is False and e["executable"] is False and e["operationalSteps"]==[],"extension action")
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
  lambda x:x["versions"]["DETAILED"]["nodes"][1]["responses"].update(YES="stop-profile"),
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
 req(doc["ledger"]["donorPinnedSha"]==pin and doc["ledger"]["donorGzipBlobSha"]==blob,"ledger")
 req(pack["manifest"]["checksums"]["ermak_diagnostics.json.gz.gitBlob"]==blob,"pack source")
 req(doc["ledger"]["scenarioIds"]==ids and len(doc["candidates"])==3,"IDs")
 total=0
 for c in doc["candidates"]:
  check(c)
  if args.negative:total+=negatives(c)
 print("STAGE18_ERMAK_BATCH2_PASS: 3 IDs, 18 SHORT nodes, 36 DETAILED nodes, 15 extensions")
 if args.negative:print("STAGE18_ERMAK_BATCH2_NEGATIVE_PASS:",total)
 print("CANDIDATE, runtime BLOCKED, device QA deferred")
if __name__=="__main__":main()
