#!/usr/bin/env python3
"""Batch40: source identity, HV fail-closed graphs, warning and negative mutations."""
import argparse,copy,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
DOC=json.loads((ROOT/"docs/diagnostics/STAGE18_ERMAK_HV_INTERLOCKS_BATCH40_2026-11-07.json").read_text(encoding="utf-8"))
PACK=json.loads((ROOT/"content-packs/electric/ermak/diagnostics/recommended/diagnostics-07.pack.json").read_text(encoding="utf-8"))
ORIG={e["id"]:e["sourceObject"]["object"] for e in PACK["entries"]}["ER-DIAG-122"]
FIELDS=[("originalId","id"),("title","title"),("symptom","symptom"),("sourceObjectStatus","status"),("sourceObjectApplicability","applicability"),("sourceObjectSystemIds","systemIds"),("sourceObjectEquipmentRefs","equipmentRefs"),("sourceObjectSourceRefs","sourceRefs")]
def req(v,msg):
 if not v:raise AssertionError(msg)
def check(c):
 for a,b in FIELDS:req(c[a]==ORIG[b],"donor "+a)
 req(c["sourceObjectStatus"]=="BASE_CONFIRMED" and c["profileApplicability"]==["base_early"] and c["lateProfileRule"]=="PROFILE_SOURCE_REQUIRED","profile")
 for k in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified","exactInstalledVariantConfirmed","substantiveSafetyReviewed"):req(c[k] is False,k)
 req(c["publicationStatus"]=="CANDIDATE" and c["exactInstalledVariant"]=="UNKNOWN" and c["unknownVariantDisposition"]=="BLOCKED","candidate")
 req(c["deviceQA"]=="DEFERRED_TO_POST_RELEASE_DEVICE_QA","device")
 req(c["warningGate"]=={"default":"HIDDEN","warningReadToEnd":True,"warningAcknowledged":True,"warningGrantsActionAuthority":False},"warning")
 req(c["safePolicy"]=={"observationOnly":True,"onlyPreviouslyRecorded":True,"triState":["YES","NO","UNKNOWN"],"unknownMustStop":True,"unknownProfile":"BLOCKED","operationsAllowed":[],"activeFaultImmediateStop":True},"safe")
 r=c["sourceRecords"]
 req(r["donor"]["commit"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff" and r["donor"]["objectId"]=="ER-DIAG-122" and r["donor"]["rawGzipIndependentlyDecoded"] is False,"lineage")
 req(r["manufacturer"]["status"]=="HISTORICAL_CIRCUIT_DESCRIPTION_PROFILE_UNVERIFIED" and r["procedure"]["status"]=="CURRENT_CLAUSE_AND_ROLE_UNVERIFIED" and r["emergency"]["status"]=="CURRENT_CLAUSE_AND_ROLE_UNVERIFIED","source authority")
 req(all(x["currentOperatingAuthority"] is False for x in r.values()),"authority")
 req(len(c["sourceConflicts"])==6 and all(x["resolution"] in ("NO_CAUSE_INFERENCE","PROFILE_BLOCKED","SOURCE_AUTHORITY_BLOCKED") for x in c["sourceConflicts"]),"conflicts")
 req(all(z in c["mustRemainDistinctFrom"] for z in ("ER-DIAG-001","ER-DIAG-115","ER-DIAG-116")),"distinct")
 for mode,count in (("SHORT",8),("DETAILED",12)):
  g=c["versions"][mode];nodes=g["nodes"];m={x["id"]:x for x in nodes}
  req(len(nodes)==count and len(m)==count and g["startNodeId"]=="q-active","graph count")
  req(g["authoringStatus"]=="RESEARCH_DRAFT_BLOCKED" and g["operatingInstructionsIncluded"] is False,"graph status")
  seen=set();stack=[g["startNodeId"]]
  while stack:
   k=stack.pop()
   if k in seen:continue
   req(k in m,"dangling "+k);seen.add(k);v=m[k]
   req(v["recordedOnly"] is True and v["operationRequested"] is False and v["causeConfirmed"] is False,"node safety")
   req(v["sourceRefs"] and all(z in r for z in v["sourceRefs"]),"node provenance")
   if v["type"]=="QUESTION":req(set(v["responses"])=={"YES","NO","UNKNOWN"} and v["responses"]["UNKNOWN"]=="stop-unknown","tri-state")
   else:req(v["type"] in ("STOP","OBSERVATION_REPORT") and v["responses"]=={},"terminal")
   stack.extend(v["responses"].values())
  req(len(seen)==count,"unreachable")
  req(m["q-active"]["responses"]=={"YES":"stop-active","NO":"q-profile","UNKNOWN":"stop-unknown"},"active")
  req(m["q-profile"]["responses"]["NO"]=="stop-profile" and m["q-symptom"]["responses"]["NO"]=="stop-mismatch","profile")
  req(m["report-match"]["type"]=="OBSERVATION_REPORT" and "НЕ ИНСТРУКЦИЯ" in m["report-match"]["text"],"report")
  if mode=="DETAILED":
   for k in ("q-evidence","q-mode","q-provenance"):req(m[k]["responses"]["NO"]=="stop-unverified","unverified")
 req(len(c["informationExtensions"])==5 and [x["version"] for x in c["informationExtensions"]]==["SHORT","SHORT","DETAILED","DETAILED","DETAILED"],"extensions")
 req(len({x["id"] for x in c["informationExtensions"]})==5,"extension IDs")
 for x in c["informationExtensions"]:
  req(x["visibility"]==c["warningGate"] and x["warningRequired"] is True and x["executable"] is False and x["actionAuthorityGranted"] is False and x["operationalSteps"]==[],"extension gate")
  req(x["sourceRefs"] and all(z in r for z in x["sourceRefs"]),"extension source")
  req(x["applicability"]=={"exactEquipmentProfileConfirmed":False,"modernSchemeConfirmed":False},"extension profile")
 req(len(c["independentCrosschecks"])==4 and all(x["verifiedAt"]=="2026-11-07" for x in c["independentCrosschecks"]),"crosscheck")
def negative(c):
 cases=[
 (["publicationStatus"],"PUBLISHED"),(["runtimeImport"],True),(["executable"],True),(["actionAuthorityGranted"],True),(["sourceAuthorityVerified"],True),(["exactInstalledVariantConfirmed"],True),(["substantiveSafetyReviewed"],True),
 (["exactInstalledVariant"],"KNOWN"),(["unknownVariantDisposition"],"ALLOWED"),(["sourceObjectStatus"],"PROFILE_REQUIRED"),(["sourceObjectApplicability","profiles"],["late"]),(["sourceObjectEquipmentRefs"],[]),(["sourceObjectSourceRefs"],[]),
 (["warningGate","default"],"VISIBLE"),(["warningGate","warningReadToEnd"],False),(["warningGate","warningAcknowledged"],False),(["warningGate","warningGrantsActionAuthority"],True),
 (["safePolicy","operationsAllowed"],["bypass"]),(["safePolicy","onlyPreviouslyRecorded"],False),(["safePolicy","unknownMustStop"],False),(["safePolicy","activeFaultImmediateStop"],False),
 (["sourceRecords","manufacturer","status"],"CURRENT"),(["sourceRecords","procedure","status"],"AUTHORIZED"),(["sourceRecords","emergency","status"],"AUTHORIZED"),(["sourceRecords","donor","rawGzipIndependentlyDecoded"],True),(["sourceRecords","donor","commit"],"wrong"),
 (["sourceConflicts",0,"resolution"],"CAUSE_CONFIRMED"),(["mustRemainDistinctFrom"],[]),
 (["versions","SHORT","nodes",0,"responses","YES"],"report-match"),(["versions","SHORT","nodes",1,"responses","NO"],"q-symptom"),(["versions","SHORT","nodes",2,"responses","UNKNOWN"],"report-match"),
 (["versions","DETAILED","nodes",3,"responses","NO"],"report-match"),(["versions","DETAILED","nodes",4,"responses","NO"],"report-match"),(["versions","DETAILED","nodes",5,"responses","NO"],"report-match"),
 (["versions","DETAILED","nodes",5,"operationRequested"],True),(["versions","SHORT","nodes",0,"recordedOnly"],False),
 (["informationExtensions",0,"visibility","default"],"VISIBLE"),(["informationExtensions",0,"operationalSteps"],["bypass"]),(["informationExtensions",4,"actionAuthorityGranted"],True),
 (["independentCrosschecks",0,"verifiedAt"],"2020-01-01")
 ]
 for i,(path,value) in enumerate(cases):
  x=copy.deepcopy(c);p=x
  for key in path[:-1]:p=p[key]
  p[path[-1]]=value
  try:check(x)
  except (AssertionError,KeyError):continue
  raise AssertionError("negative escaped "+str(i))
 return len(cases)
def main():
 p=argparse.ArgumentParser();p.add_argument("--negative",action="store_true");args=p.parse_args()
 req(DOC["ledger"]["scenarioIds"]==["ER-DIAG-122"] and len(DOC["candidates"])==1,"membership")
 req(DOC["ledger"]["runtimeImport"] is False and DOC["ledger"]["status"]=="CANDIDATE","ledger")
 check(DOC["candidates"][0]);print("STAGE18_BATCH40_PASS scenarios=1 SHORT=8 DETAILED=12 EXTENSIONS=5")
 if args.negative:print("STAGE18_BATCH40_NEGATIVE_PASS",negative(DOC["candidates"][0]))
if __name__=="__main__":main()
