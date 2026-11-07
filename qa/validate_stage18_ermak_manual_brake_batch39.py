#!/usr/bin/env python3
"""Stage18 batch39: donor identity, source/role/safety gates and negative mutations."""
import argparse,copy,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
DOC=json.loads((ROOT/"docs/diagnostics/STAGE18_ERMAK_MANUAL_BRAKE_BATCH39_2026-11-07.json").read_text(encoding="utf-8"))
PACK=json.loads((ROOT/"content-packs/electric/ermak/diagnostics/recommended/diagnostics-07.pack.json").read_text(encoding="utf-8"))
ORIG={e["id"]:e["sourceObject"]["object"] for e in PACK["entries"]}["ER-DIAG-121"]
FIELDS=[("originalId","id"),("title","title"),("symptom","symptom"),("sourceObjectStatus","status"),("sourceObjectApplicability","applicability"),("sourceObjectSystemIds","systemIds"),("sourceObjectEquipmentRefs","equipmentRefs"),("sourceObjectSourceRefs","sourceRefs")]
def require(v,msg):
 if not v:raise AssertionError(msg)
def check(c):
 for a,b in FIELDS:require(c[a]==ORIG[b],"donor mismatch "+a)
 require(c["sourceObjectStatus"]=="BASE_CONFIRMED" and c["profileApplicability"]==["base_early"] and c["lateProfileRule"]=="PROFILE_SOURCE_REQUIRED","profile")
 for k in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified","exactInstalledVariantConfirmed","substantiveSafetyReviewed"):require(c[k] is False,k)
 require(c["publicationStatus"]=="CANDIDATE" and c["exactInstalledVariant"]=="UNKNOWN" and c["unknownVariantDisposition"]=="BLOCKED","publication")
 require(c["deviceQA"]=="DEFERRED_TO_POST_RELEASE_DEVICE_QA","device")
 require(c["warningGate"]=={"default":"HIDDEN","warningReadToEnd":True,"warningAcknowledged":True,"warningGrantsActionAuthority":False},"warning")
 require(c["safePolicy"]=={"observationOnly":True,"onlyPreviouslyRecorded":True,"triState":["YES","NO","UNKNOWN"],"unknownMustStop":True,"unknownProfile":"BLOCKED","operationsAllowed":[],"activeFaultImmediateStop":True},"safe")
 r=c["sourceRecords"]
 require(r["donor"]["commit"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff" and r["donor"]["rawGzipIndependentlyDecoded"] is False and r["donor"]["objectId"]=="ER-DIAG-121","lineage")
 require(r["manufacturer"]["status"]=="HISTORICAL_DESIGN_ONLY_PROFILE_UNVERIFIED" and r["historical"]["status"]=="HISTORICAL_VARIANT_WARNING","archival")
 require(r["brakeRules"]["status"]=="EFFECTIVE_DATE_AND_STRUCTURE_CONFIRMED_CLAUSE_UNVERIFIED" and r["normative"]["status"]=="ACTION_AUTHORITY_UNKNOWN","normative")
 require(all(x["currentOperatingAuthority"] is False for x in r.values()),"source authority")
 require(len(c["sourceConflicts"])==5 and all(x["resolution"] in ("NO_CAUSE_INFERENCE","PROFILE_BLOCKED","SOURCE_AUTHORITY_BLOCKED") for x in c["sourceConflicts"]),"conflicts")
 require(all(x in c["mustRemainDistinctFrom"] for x in ("ER-DIAG-081","ER-DIAG-087","ER-DIAG-120")),"distinct")
 for mode,num in (("SHORT",8),("DETAILED",12)):
  g=c["versions"][mode];nodes=g["nodes"];m={x["id"]:x for x in nodes}
  require(len(nodes)==num and len(m)==num and g["startNodeId"]=="q-active","graph count")
  require(g["authoringStatus"]=="RESEARCH_DRAFT_BLOCKED" and g["operatingInstructionsIncluded"] is False,"graph status")
  visited=set();stack=[g["startNodeId"]]
  while stack:
   key=stack.pop()
   if key in visited:continue
   require(key in m,"dangling "+key);visited.add(key);v=m[key]
   require(v["recordedOnly"] is True and v["operationRequested"] is False and v["causeConfirmed"] is False,"node safety")
   require(v["sourceRefs"] and all(z in r for z in v["sourceRefs"]),"node provenance")
   if v["type"]=="QUESTION":require(set(v["responses"])=={"YES","NO","UNKNOWN"} and v["responses"]["UNKNOWN"]=="stop-unknown","tri-state")
   else:require(v["type"] in ("STOP","OBSERVATION_REPORT") and v["responses"]=={},"terminal")
   stack.extend(v["responses"].values())
  require(len(visited)==num,"unreachable")
  require(m["q-active"]["responses"]=={"YES":"stop-active","NO":"q-profile","UNKNOWN":"stop-unknown"},"active")
  require(m["q-profile"]["responses"]["NO"]=="stop-profile" and m["q-symptom"]["responses"]["NO"]=="stop-mismatch","profile")
  require(m["report-match"]["type"]=="OBSERVATION_REPORT" and "НЕ ИНСТРУКЦИЯ" in m["report-match"]["text"],"report")
  if mode=="DETAILED":
   for key in ("q-evidence","q-mode","q-provenance"):require(m[key]["responses"]["NO"]=="stop-unverified","unverified")
 require(len(c["informationExtensions"])==5 and [x["version"] for x in c["informationExtensions"]]==["SHORT","SHORT","DETAILED","DETAILED","DETAILED"],"extensions")
 require(len({x["id"] for x in c["informationExtensions"]})==5,"unique extensions")
 for x in c["informationExtensions"]:
  require(x["visibility"]==c["warningGate"] and x["warningRequired"] is True and x["executable"] is False and x["actionAuthorityGranted"] is False and x["operationalSteps"]==[],"extension gate")
  require(x["sourceRefs"] and all(z in r for z in x["sourceRefs"]),"extension sources")
  require(x["applicability"]=={"exactEquipmentProfileConfirmed":False,"modernSchemeConfirmed":False},"extension profile")
 require(len(c["independentCrosschecks"])==4 and all(x["verifiedAt"]=="2026-11-07" for x in c["independentCrosschecks"]),"crosschecks")
def negative(c):
 cases=[
 (["publicationStatus"],"PUBLISHED"),(["runtimeImport"],True),(["executable"],True),(["actionAuthorityGranted"],True),(["sourceAuthorityVerified"],True),(["exactInstalledVariantConfirmed"],True),(["substantiveSafetyReviewed"],True),
 (["exactInstalledVariant"],"KNOWN"),(["unknownVariantDisposition"],"ALLOWED"),(["sourceObjectStatus"],"PROFILE_REQUIRED"),(["sourceObjectApplicability","profiles"],["late"]),(["sourceObjectEquipmentRefs"],[]),(["sourceObjectSourceRefs"],[]),
 (["warningGate","default"],"VISIBLE"),(["warningGate","warningReadToEnd"],False),(["warningGate","warningAcknowledged"],False),(["warningGate","warningGrantsActionAuthority"],True),
 (["safePolicy","operationsAllowed"],["test-on-grade"]),(["safePolicy","onlyPreviouslyRecorded"],False),(["safePolicy","unknownMustStop"],False),(["safePolicy","activeFaultImmediateStop"],False),
 (["sourceRecords","brakeRules","status"],"AUTHORIZED"),(["sourceRecords","normative","status"],"AUTHORIZED"),(["sourceRecords","manufacturer","status"],"CURRENT"),(["sourceRecords","historical","status"],"CURRENT"),(["sourceRecords","donor","rawGzipIndependentlyDecoded"],True),(["sourceRecords","donor","commit"],"wrong"),
 (["sourceConflicts",0,"resolution"],"CAUSE_CONFIRMED"),(["mustRemainDistinctFrom"],[]),
 (["versions","SHORT","nodes",0,"responses","YES"],"report-match"),(["versions","SHORT","nodes",1,"responses","NO"],"q-symptom"),(["versions","SHORT","nodes",2,"responses","UNKNOWN"],"report-match"),
 (["versions","DETAILED","nodes",3,"responses","NO"],"report-match"),(["versions","DETAILED","nodes",4,"responses","NO"],"report-match"),(["versions","DETAILED","nodes",5,"responses","NO"],"report-match"),
 (["versions","DETAILED","nodes",5,"operationRequested"],True),(["versions","SHORT","nodes",0,"recordedOnly"],False),
 (["informationExtensions",0,"visibility","default"],"VISIBLE"),(["informationExtensions",0,"operationalSteps"],["release"]),(["informationExtensions",4,"actionAuthorityGranted"],True),
 (["independentCrosschecks",0,"verifiedAt"],"2020-01-01")
 ]
 for i,(path,val) in enumerate(cases):
  x=copy.deepcopy(c);p=x
  for key in path[:-1]:p=p[key]
  p[path[-1]]=val
  try:check(x)
  except (AssertionError,KeyError):continue
  raise AssertionError("negative escaped "+str(i))
 return len(cases)
def main():
 p=argparse.ArgumentParser();p.add_argument("--negative",action="store_true");args=p.parse_args()
 require(DOC["ledger"]["scenarioIds"]==["ER-DIAG-121"] and len(DOC["candidates"])==1,"ledger membership")
 require(DOC["ledger"]["runtimeImport"] is False and DOC["ledger"]["status"]=="CANDIDATE","ledger")
 check(DOC["candidates"][0]);print("STAGE18_BATCH39_PASS scenarios=1 SHORT=8 DETAILED=12 EXTENSIONS=5")
 if args.negative:print("STAGE18_BATCH39_NEGATIVE_PASS",negative(DOC["candidates"][0]))
if __name__=="__main__":main()
