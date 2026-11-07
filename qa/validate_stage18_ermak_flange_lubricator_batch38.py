#!/usr/bin/env python3
"""Stage18 batch38: exact donor identity, fail-closed graphs, negative mutations."""
import argparse, copy, json, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
DOC=json.loads((ROOT/"docs/diagnostics/STAGE18_ERMAK_FLANGE_LUBRICATOR_BATCH38_2026-11-07.json").read_text(encoding="utf-8"))
PACK=json.loads((ROOT/"content-packs/electric/ermak/diagnostics/recommended/diagnostics-06.pack.json").read_text(encoding="utf-8"))
ORIG={e["id"]:e["sourceObject"]["object"] for e in PACK["entries"]}["ER-DIAG-120"]
FIELDS=[("originalId","id"),("title","title"),("symptom","symptom"),("sourceObjectStatus","status"),("sourceObjectApplicability","applicability"),("sourceObjectSystemIds","systemIds"),("sourceObjectEquipmentRefs","equipmentRefs"),("sourceObjectSourceRefs","sourceRefs")]
def require(x,msg):
 if not x: raise AssertionError(msg)
def check(c):
 for a,b in FIELDS: require(c[a]==ORIG[b],"donor mismatch "+a)
 require(c["originalId"]=="ER-DIAG-120" and c["sourceObjectStatus"]=="PROFILE_REQUIRED","identity")
 require(c["profileApplicability"]==ORIG["applicability"]["profiles"] and c["lateProfileRule"]==ORIG["applicability"]["lateProfiles"],"profiles")
 for k in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified","exactInstalledVariantConfirmed","substantiveSafetyReviewed"): require(c[k] is False,k)
 require(c["publicationStatus"]=="CANDIDATE" and c["exactInstalledVariant"]=="UNKNOWN" and c["unknownVariantDisposition"]=="BLOCKED","publication")
 require(c["deviceQA"]=="DEFERRED_TO_POST_RELEASE_DEVICE_QA","device")
 require(c["warningGate"]=={"default":"HIDDEN","warningReadToEnd":True,"warningAcknowledged":True,"warningGrantsActionAuthority":False},"warning")
 s=c["safePolicy"]; require(s=={"observationOnly":True,"onlyPreviouslyRecorded":True,"triState":["YES","NO","UNKNOWN"],"unknownMustStop":True,"unknownProfile":"BLOCKED","operationsAllowed":[],"activeFaultImmediateStop":True},"safe")
 r=c["sourceRecords"]
 require(r["donor"]["commit"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff" and r["donor"]["packBlobSha"]=="5d016e774bf72c618f50aa01d213a9995ab9d441" and r["donor"]["rawGzipIndependentlyDecoded"] is False,"donor lineage")
 require(r["manufacturerSpecific"]["status"]=="MISSING_BLOCKS_PROFILE_AND_ACTIONS" and not r["manufacturerSpecific"]["url"],"missing manual")
 require(r["normative"]["status"]=="ACTION_AUTHORITY_UNKNOWN","normative")
 require(all(v["currentOperatingAuthority"] is False for v in r.values()),"authority")
 require(len(c["sourceConflicts"])==5 and all(v["resolution"] in ("PROFILE_BLOCKED","SOURCE_AUTHORITY_BLOCKED","NO_CAUSE_INFERENCE") for v in c["sourceConflicts"]),"conflicts")
 require("ER-DIAG-103" in c["mustRemainDistinctFrom"] and "ER-DIAG-121" in c["mustRemainDistinctFrom"],"distinct")
 for mode,n in (("SHORT",8),("DETAILED",12)):
  g=c["versions"][mode];nodes=g["nodes"];m={x["id"]:x for x in nodes}
  require(len(nodes)==n and len(m)==n and g["startNodeId"]=="q-active","graph cardinality")
  require(g["authoringStatus"]=="RESEARCH_DRAFT_BLOCKED" and g["operatingInstructionsIncluded"] is False,"graph publication")
  visited=set();stack=[g["startNodeId"]]
  while stack:
   key=stack.pop()
   if key in visited:continue
   require(key in m,"dangling "+key);visited.add(key);v=m[key]
   require(v["recordedOnly"] is True and v["operationRequested"] is False and v["causeConfirmed"] is False,"node safety")
   require(v["sourceRefs"] and all(z in r for z in v["sourceRefs"]),"node provenance")
   if v["type"]=="QUESTION":
    require(set(v["responses"])=={"YES","NO","UNKNOWN"} and v["responses"]["UNKNOWN"]=="stop-unknown","tri-state")
   else: require(v["type"] in ("STOP","OBSERVATION_REPORT") and v["responses"]=={},"terminal")
   stack.extend(v["responses"].values())
  require(len(visited)==n,"unreachable nodes")
  require(m["q-active"]["responses"]=={"YES":"stop-active","NO":"q-profile","UNKNOWN":"stop-unknown"},"active stop")
  require(m["q-profile"]["responses"]["NO"]=="stop-profile" and m["q-symptom"]["responses"]["NO"]=="stop-mismatch","profile mismatch")
  require(m["report-match"]["type"]=="OBSERVATION_REPORT" and "НЕ ИНСТРУКЦИЯ" in m["report-match"]["text"],"report")
  if mode=="DETAILED":
   for key in ("q-evidence","q-differential","q-provenance"):require(m[key]["responses"]["NO"]=="stop-unverified","unverified")
 require(len(c["informationExtensions"])==5 and [x["version"] for x in c["informationExtensions"]]==["SHORT","SHORT","DETAILED","DETAILED","DETAILED"],"extensions")
 require(len({x["id"] for x in c["informationExtensions"]})==5,"unique extensions")
 for x in c["informationExtensions"]:
  require(x["visibility"]==c["warningGate"] and x["warningRequired"] is True and x["executable"] is False and x["actionAuthorityGranted"] is False and x["operationalSteps"]==[],"extension gate")
  require(x["sourceRefs"] and all(z in r for z in x["sourceRefs"]),"extension sources")
  require(x["applicability"]=={"exactEquipmentProfileConfirmed":False,"modernSchemeConfirmed":False},"extension applicability")
 require(len(c["independentCrosschecks"])==3 and all(x["verifiedAt"]=="2026-11-07" for x in c["independentCrosschecks"]),"crosschecks")
def negative(c):
 cases=[
 (["publicationStatus"],"PUBLISHED"),(["runtimeImport"],True),(["executable"],True),(["actionAuthorityGranted"],True),(["sourceAuthorityVerified"],True),(["exactInstalledVariantConfirmed"],True),(["substantiveSafetyReviewed"],True),
 (["exactInstalledVariant"],"KNOWN"),(["unknownVariantDisposition"],"ALLOWED"),(["sourceObjectStatus"],"BASE_CONFIRMED"),(["sourceObjectSystemIds"],[]),(["sourceObjectEquipmentRefs"],[]),(["sourceObjectSourceRefs"],[]),
 (["warningGate","default"],"VISIBLE"),(["warningGate","warningReadToEnd"],False),(["warningGate","warningAcknowledged"],False),(["warningGate","warningGrantsActionAuthority"],True),
 (["safePolicy","operationsAllowed"],["toggle-U30"]),(["safePolicy","onlyPreviouslyRecorded"],False),(["safePolicy","unknownMustStop"],False),(["safePolicy","activeFaultImmediateStop"],False),
 (["sourceRecords","manufacturerSpecific","status"],"VERIFIED"),(["sourceRecords","manufacturerSpecific","url"],"https://example.com/fake"),(["sourceRecords","normative","status"],"AUTHORIZED"),(["sourceRecords","training","currentOperatingAuthority"],True),
 (["sourceRecords","donor","commit"],"wrong"),(["sourceRecords","donor","rawGzipIndependentlyDecoded"],True),(["sourceConflicts",0,"resolution"],"CAUSE_CONFIRMED"),(["mustRemainDistinctFrom"],[]),
 (["versions","SHORT","nodes",0,"responses","YES"],"report-match"),(["versions","SHORT","nodes",1,"responses","NO"],"q-symptom"),(["versions","SHORT","nodes",2,"responses","UNKNOWN"],"report-match"),
 (["versions","DETAILED","nodes",3,"responses","NO"],"report-match"),(["versions","DETAILED","nodes",4,"responses","NO"],"report-match"),(["versions","DETAILED","nodes",5,"responses","NO"],"report-match"),
 (["versions","DETAILED","nodes",5,"operationRequested"],True),(["versions","SHORT","nodes",0,"recordedOnly"],False),
 (["informationExtensions",0,"visibility","default"],"VISIBLE"),(["informationExtensions",0,"operationalSteps"],["open-valve"]),(["informationExtensions",4,"actionAuthorityGranted"],True),
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
 require(DOC["ledger"]["scenarioIds"]==["ER-DIAG-120"] and len(DOC["candidates"])==1,"ledger membership")
 require(DOC["ledger"]["runtimeImport"] is False and DOC["ledger"]["status"]=="CANDIDATE","ledger status")
 c=DOC["candidates"][0];check(c)
 print("STAGE18_BATCH38_PASS scenarios=1 SHORT=8 DETAILED=12 EXTENSIONS=5")
 if args.negative:print("STAGE18_BATCH38_NEGATIVE_PASS",negative(c))
if __name__=="__main__":main()
