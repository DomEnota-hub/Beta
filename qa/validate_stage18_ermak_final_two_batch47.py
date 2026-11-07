#!/usr/bin/env python3
"""Stage18 Ermak batch47: pinned donor parity, graph safety and negative mutation gates."""
import argparse,copy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
D=json.loads((R/"docs/diagnostics/STAGE18_ERMAK_FINAL_TWO_BATCH47_2026-11-07.json").read_text(encoding="utf-8"))
P=json.loads((R/"content-packs/electric/ermak/diagnostics/recommended/diagnostics-07.pack.json").read_text(encoding="utf-8"))
O={e["id"]:e["sourceObject"]["object"] for e in P["entries"]}
IDS=["ER-DIAG-135","ER-DIAG-136"]
FIELDS=[("originalId","id"),("title","title"),("symptom","symptom"),("sourceObjectStatus","status"),("sourceObjectApplicability","applicability"),("sourceObjectSystemIds","systemIds"),("sourceObjectEquipmentRefs","equipmentRefs"),("sourceObjectSourceRefs","sourceRefs")]
def req(v,msg):
 if not v:raise AssertionError(msg)
def check(c):
 i=c["originalId"];req(i in IDS,"id")
 for a,b in FIELDS:req(c[a]==O[i][b],"donor "+a)
 req(c["sourceObjectStatus"]=="BASE_CONFIRMED","donor status")
 req(c["sourceObjectApplicability"]["lateProfiles"]==("AS_LISTED" if i==IDS[0] else "PROFILE_SOURCE_REQUIRED"),"late source")
 req(c["profileApplicability"]==["base_early"] and c["lateProfileRule"]==O[i]["applicability"]["lateProfiles"],"profile")
 req(c["earlyMsud"]=="ARCHIVAL_MSUD_N_ONLY" and c["lateMsud"]=="NOT_ASSUMED","msud")
 for k in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified","exactInstalledVariantConfirmed","substantiveSafetyReviewed"):req(c[k] is False,"blocked "+k)
 req(c["publicationStatus"]=="CANDIDATE" and c["exactInstalledVariant"]=="UNKNOWN" and c["unknownVariantDisposition"]=="BLOCKED","candidate")
 req(c["deviceQA"]=="DEFERRED_TO_POST_RELEASE_DEVICE_QA","device")
 req(c["warningGate"]=={"default":"HIDDEN","warningReadToEnd":True,"warningAcknowledged":True,"warningGrantsActionAuthority":False},"warning")
 req(c["safePolicy"]=={"observationOnly":True,"onlyPreviouslyRecorded":True,"triState":["YES","NO","UNKNOWN"],"unknownMustStop":True,"unknownProfile":"BLOCKED","operationsAllowed":[],"activeFaultImmediateStop":True},"safety")
 s=c["sourceRecords"];req(set(s)==({"donor","re1","re4","rule996","rule2580","safety"} if i==IDS[0] else {"donor","re1","training","rule996","rule2580","safety"}),"sources")
 d=s["donor"];req(d["commit"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff" and d["blobSha"]=="c3a22c62db42308eb4b7ee44ff2da02f47686625","pin")
 req(d["objectId"]==i and d["rawGzipIndependentlyDecoded"] is False,"raw")
 req(all(x["currentOperatingAuthority"] is False for x in s.values()),"authority")
 req(len(c["sourceConflicts"])==6 and all(x["resolution"] in ("NO_CAUSE_INFERENCE","PROFILE_BLOCKED","SOURCE_AUTHORITY_BLOCKED") for x in c["sourceConflicts"]),"conflicts")
 req(len(c["mustRemainDistinctFrom"])==5 and (IDS[1] if i==IDS[0] else IDS[0]) in c["mustRemainDistinctFrom"],"distinct")
 for mode,count in (("SHORT",8),("DETAILED",12)):
  g=c["versions"][mode];n=g["nodes"];m={x["id"]:x for x in n}
  req(len(n)==count and len(m)==count and g["startNodeId"]=="q-active","count")
  req(g["authoringStatus"]=="RESEARCH_DRAFT_BLOCKED" and g["operatingInstructionsIncluded"] is False,"graph")
  seen=set();stack=["q-active"]
  while stack:
   k=stack.pop()
   if k in seen:continue
   req(k in m,"dangling");seen.add(k);x=m[k]
   req(x["recordedOnly"] is True and x["operationRequested"] is False and x["causeConfirmed"] is False,"node safe")
   req(x["sourceRefs"] and set(x["sourceRefs"])<=set(s),"node refs")
   if x["type"]=="QUESTION":
    req(set(x["responses"])=={"YES","NO","UNKNOWN"} and x["responses"]["UNKNOWN"]=="stop-unknown","tristate")
    stack.extend(x["responses"].values())
   else:req(x["type"] in ("STOP","OBSERVATION_REPORT") and x["responses"]=={},"terminal")
  req(len(seen)==count,"reachability")
  req(m["q-active"]["responses"]=={"YES":"stop-active","NO":"q-profile","UNKNOWN":"stop-unknown"},"active")
  req(m["q-profile"]["responses"]["NO"]=="stop-profile" and m["q-symptom"]["responses"]["NO"]=="stop-mismatch","profile/mismatch")
  req(m["report-match"]["type"]=="OBSERVATION_REPORT" and "НЕ ИНСТРУКЦИЯ" in m["report-match"]["text"],"report")
  if mode=="DETAILED":
   for k in ("q-evidence","q-mode","q-provenance"):req(m[k]["responses"]["NO"]=="stop-unverified","evidence")
 e=c["informationExtensions"]
 req(len(e)==5 and [x["version"] for x in e]==["SHORT","SHORT","DETAILED","DETAILED","DETAILED"] and len({x["id"] for x in e})==5,"extensions")
 for x in e:
  req(x["visibility"]==c["warningGate"] and x["warningRequired"] is True and x["executable"] is False and x["actionAuthorityGranted"] is False and x["operationalSteps"]==[],"extension safe")
  req(x["sourceRefs"] and set(x["sourceRefs"])<=set(s) and x["applicability"]=={"exactEquipmentProfileConfirmed":False,"modernSchemeConfirmed":False},"extension refs")
 req(len(c["independentCrosschecks"])==4 and all(x["verifiedAt"]=="2026-11-07" for x in c["independentCrosschecks"]),"crosschecks")
 req(any(x["confidence"]=="UNVERIFIED_NORMATIVE_REFERENCE" for x in c["independentCrosschecks"]),"norms")
 req(any(x["confidence"]=="PROJECTED_FIELDS_ONLY" for x in c["independentCrosschecks"]),"donor provenance")
 if i==IDS[1]:req(any(x["confidence"]=="HISTORICAL_TRAINING_NOT_AUTHORITY" for x in c["independentCrosschecks"]),"historical")
def negative(c):
 cases=[
 (["publicationStatus"],"PUBLISHED"),(["runtimeImport"],True),(["executable"],True),(["actionAuthorityGranted"],True),
 (["sourceAuthorityVerified"],True),(["exactInstalledVariantConfirmed"],True),(["substantiveSafetyReviewed"],True),
 (["exactInstalledVariant"],"KNOWN"),(["unknownVariantDisposition"],"ALLOWED"),(["sourceObjectStatus"],"PROFILE_REQUIRED"),
 (["sourceObjectApplicability","lateProfiles"],"AS_LISTED" if c["originalId"]==IDS[1] else "PROFILE_SOURCE_REQUIRED"),
 (["lateProfileRule"],"AS_LISTED" if c["originalId"]==IDS[1] else "PROFILE_SOURCE_REQUIRED"),
 (["sourceObjectSystemIds"],[]),(["sourceObjectEquipmentRefs"],[]),(["sourceObjectSourceRefs"],[]),
 (["warningGate","default"],"VISIBLE"),(["warningGate","warningReadToEnd"],False),(["warningGate","warningAcknowledged"],False),
 (["warningGate","warningGrantsActionAuthority"],True),(["safePolicy","operationsAllowed"],["repair"]),
 (["safePolicy","onlyPreviouslyRecorded"],False),(["safePolicy","unknownMustStop"],False),(["safePolicy","activeFaultImmediateStop"],False),
 (["sourceRecords","re1","currentOperatingAuthority"],True),(["sourceRecords","rule996","currentOperatingAuthority"],True),
 (["sourceRecords","donor","rawGzipIndependentlyDecoded"],True),(["sourceRecords","donor","commit"],"wrong"),
 (["sourceRecords","donor","blobSha"],"wrong"),(["sourceConflicts",0,"resolution"],"CAUSE_CONFIRMED"),
 (["mustRemainDistinctFrom"],[]),(["versions","SHORT","nodes",0,"responses","YES"],"report-match"),
 (["versions","SHORT","nodes",1,"responses","NO"],"report-match"),
 (["versions","SHORT","nodes",2,"responses","UNKNOWN"],"report-match"),
 (["versions","DETAILED","nodes",3,"responses","NO"],"report-match"),
 (["versions","DETAILED","nodes",4,"responses","NO"],"report-match"),
 (["versions","DETAILED","nodes",5,"responses","NO"],"report-match"),
 (["versions","DETAILED","nodes",5,"operationRequested"],True),(["versions","SHORT","nodes",0,"recordedOnly"],False),
 (["informationExtensions",0,"visibility","default"],"VISIBLE"),(["informationExtensions",0,"operationalSteps"],["test"]),
 (["informationExtensions",4,"actionAuthorityGranted"],True),(["independentCrosschecks",0,"verifiedAt"],"2020-01-01"),
 (["lateMsud"],"ASSUMED_015")
 ]
 for idx,(path,v) in enumerate(cases):
  m=copy.deepcopy(c);t=m
  for k in path[:-1]:t=t[k]
  t[path[-1]]=v
  try:check(m)
  except (AssertionError,KeyError):continue
  raise AssertionError("negative escaped "+str(idx))
 return len(cases)
if __name__=="__main__":
 a=argparse.ArgumentParser();a.add_argument("--negative",action="store_true");z=a.parse_args()
 req(D["ledger"]["scenarioIds"]==IDS and len(D["candidates"])==2,"membership")
 req(D["ledger"]["status"]=="CANDIDATE" and D["ledger"]["runtimeImport"] is False and D["ledger"]["actionAuthorityGranted"] is False,"ledger")
 req(D["ledger"]["sourceCatalogCount"]==136,"source catalog")
 for c in D["candidates"]:check(c)
 print("STAGE18_BATCH47_PASS scenarios=2 SHORT=16 DETAILED=24 EXTENSIONS=10")
 if z.negative:print("STAGE18_BATCH47_NEGATIVE_PASS",sum(negative(c) for c in D["candidates"]))
