#!/usr/bin/env python3
"""Stage18 batch41: two independent donor identities, fail-closed graphs and negative mutations."""
import argparse,copy,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
DOC=json.loads((ROOT/"docs/diagnostics/STAGE18_ERMAK_CAB_SIGNALS_BATCH41_2026-11-07.json").read_text(encoding="utf-8"))
PACK=json.loads((ROOT/"content-packs/electric/ermak/diagnostics/recommended/diagnostics-07.pack.json").read_text(encoding="utf-8"))
ORIG={e["id"]:e["sourceObject"]["object"] for e in PACK["entries"]}
FIELDS=[("originalId","id"),("title","title"),("symptom","symptom"),("sourceObjectStatus","status"),("sourceObjectApplicability","applicability"),("sourceObjectSystemIds","systemIds"),("sourceObjectEquipmentRefs","equipmentRefs"),("sourceObjectSourceRefs","sourceRefs")]
def req(cond,msg):
 if not cond: raise AssertionError(msg)
def check(c):
 o=ORIG[c["originalId"]]
 for a,b in FIELDS:req(c[a]==o[b],"donor "+a)
 req(c["sourceObjectStatus"]=="BASE_CONFIRMED" and c["profileApplicability"]==["base_early"] and c["lateProfileRule"]=="PROFILE_SOURCE_REQUIRED","profile")
 for k in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified","exactInstalledVariantConfirmed","substantiveSafetyReviewed"):req(c[k] is False,k)
 req(c["publicationStatus"]=="CANDIDATE" and c["exactInstalledVariant"]=="UNKNOWN" and c["unknownVariantDisposition"]=="BLOCKED","candidate")
 req(c["deviceQA"]=="DEFERRED_TO_POST_RELEASE_DEVICE_QA","device")
 req(c["warningGate"]=={"default":"HIDDEN","warningReadToEnd":True,"warningAcknowledged":True,"warningGrantsActionAuthority":False},"warning")
 req(c["safePolicy"]=={"observationOnly":True,"onlyPreviouslyRecorded":True,"triState":["YES","NO","UNKNOWN"],"unknownMustStop":True,"unknownProfile":"BLOCKED","operationsAllowed":[],"activeFaultImmediateStop":True},"safety")
 r=c["sourceRecords"];req(set(r)=={"donor","re1","re2","re5","safety"},"source set")
 req(r["donor"]["commit"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff" and r["donor"]["objectId"]==c["originalId"] and r["donor"]["rawGzipIndependentlyDecoded"] is False,"lineage")
 req(all(z["currentOperatingAuthority"] is False for z in r.values()),"source authority")
 req(len(c["sourceConflicts"])==6 and all(z["resolution"] in ("NO_CAUSE_INFERENCE","PROFILE_BLOCKED","SOURCE_AUTHORITY_BLOCKED") for z in c["sourceConflicts"]),"conflicts")
 req(len(c["mustRemainDistinctFrom"])>=6,"distinct")
 for mode,count in (("SHORT",8),("DETAILED",12)):
  g=c["versions"][mode];nodes=g["nodes"];m={x["id"]:x for x in nodes}
  req(len(nodes)==count and len(m)==count and g["startNodeId"]=="q-active","count")
  req(g["authoringStatus"]=="RESEARCH_DRAFT_BLOCKED" and g["operatingInstructionsIncluded"] is False,"graph status")
  seen=set();stack=[g["startNodeId"]]
  while stack:
   key=stack.pop()
   if key in seen:continue
   req(key in m,"dangling");seen.add(key);v=m[key]
   req(v["recordedOnly"] is True and v["operationRequested"] is False and v["causeConfirmed"] is False,"node safety")
   req(v["sourceRefs"] and all(z in r for z in v["sourceRefs"]),"node sources")
   if v["type"]=="QUESTION":
    req(set(v["responses"])=={"YES","NO","UNKNOWN"} and v["responses"]["UNKNOWN"]=="stop-unknown","tri-state")
    stack.extend(v["responses"].values())
   else:req(v["type"] in ("STOP","OBSERVATION_REPORT") and v["responses"]=={},"terminal")
  req(len(seen)==count,"reachability")
  req(m["q-active"]["responses"]=={"YES":"stop-active","NO":"q-profile","UNKNOWN":"stop-unknown"},"active")
  req(m["q-profile"]["responses"]["NO"]=="stop-profile" and m["q-symptom"]["responses"]["NO"]=="stop-mismatch","profile gate")
  req(m["report-match"]["type"]=="OBSERVATION_REPORT" and "НЕ ИНСТРУКЦИЯ" in m["report-match"]["text"],"report")
  if mode=="DETAILED":
   for key in ("q-evidence","q-mode","q-provenance"):req(m[key]["responses"]["NO"]=="stop-unverified","unverified")
 req(len(c["informationExtensions"])==5 and [x["version"] for x in c["informationExtensions"]]==["SHORT","SHORT","DETAILED","DETAILED","DETAILED"],"extensions")
 req(len({x["id"] for x in c["informationExtensions"]})==5,"extension IDs")
 for x in c["informationExtensions"]:
  req(x["visibility"]==c["warningGate"] and x["warningRequired"] is True and x["executable"] is False and x["actionAuthorityGranted"] is False and x["operationalSteps"]==[],"extension gate")
  req(x["sourceRefs"] and all(z in r for z in x["sourceRefs"]),"extension sources")
  req(x["applicability"]=={"exactEquipmentProfileConfirmed":False,"modernSchemeConfirmed":False},"extension profile")
 req(len(c["independentCrosschecks"])==4 and all(x["verifiedAt"]=="2026-11-07" for x in c["independentCrosschecks"]),"crosschecks")
def negative(c):
 cases=[
 (["publicationStatus"],"PUBLISHED"),(["runtimeImport"],True),(["executable"],True),(["actionAuthorityGranted"],True),(["sourceAuthorityVerified"],True),(["exactInstalledVariantConfirmed"],True),(["substantiveSafetyReviewed"],True),
 (["exactInstalledVariant"],"KNOWN"),(["unknownVariantDisposition"],"ALLOWED"),(["sourceObjectStatus"],"PROFILE_REQUIRED"),(["sourceObjectApplicability","profiles"],["late"]),(["sourceObjectEquipmentRefs"],[]),(["sourceObjectSourceRefs"],[]),
 (["warningGate","default"],"VISIBLE"),(["warningGate","warningReadToEnd"],False),(["warningGate","warningAcknowledged"],False),(["warningGate","warningGrantsActionAuthority"],True),
 (["safePolicy","operationsAllowed"],["override"]),(["safePolicy","onlyPreviouslyRecorded"],False),(["safePolicy","unknownMustStop"],False),(["safePolicy","activeFaultImmediateStop"],False),
 (["sourceRecords","re1","currentOperatingAuthority"],True),(["sourceRecords","re5","currentOperatingAuthority"],True),(["sourceRecords","donor","rawGzipIndependentlyDecoded"],True),(["sourceRecords","donor","commit"],"wrong"),
 (["sourceConflicts",0,"resolution"],"CAUSE_CONFIRMED"),(["mustRemainDistinctFrom"],[]),
 (["versions","SHORT","nodes",0,"responses","YES"],"report-match"),(["versions","SHORT","nodes",1,"responses","NO"],"q-symptom"),(["versions","SHORT","nodes",2,"responses","UNKNOWN"],"report-match"),
 (["versions","DETAILED","nodes",3,"responses","NO"],"report-match"),(["versions","DETAILED","nodes",4,"responses","NO"],"report-match"),(["versions","DETAILED","nodes",5,"responses","NO"],"report-match"),
 (["versions","DETAILED","nodes",5,"operationRequested"],True),(["versions","SHORT","nodes",0,"recordedOnly"],False),
 (["informationExtensions",0,"visibility","default"],"VISIBLE"),(["informationExtensions",0,"operationalSteps"],["repair"]),(["informationExtensions",4,"actionAuthorityGranted"],True),
 (["independentCrosschecks",0,"verifiedAt"],"2020-01-01")]
 for i,(path,value) in enumerate(cases):
  x=copy.deepcopy(c);p=x
  for k in path[:-1]:p=p[k]
  p[path[-1]]=value
  try:check(x)
  except (AssertionError,KeyError):continue
  raise AssertionError("negative escaped "+str(i))
 return len(cases)
def main():
 p=argparse.ArgumentParser();p.add_argument("--negative",action="store_true");args=p.parse_args()
 req(DOC["ledger"]["scenarioIds"]==["ER-DIAG-123","ER-DIAG-124"] and len(DOC["candidates"])==2,"membership")
 req(DOC["ledger"]["status"]=="CANDIDATE" and DOC["ledger"]["runtimeImport"] is False,"ledger")
 for c in DOC["candidates"]:check(c)
 req(DOC["candidates"][0]["originalId"] in DOC["candidates"][1]["mustRemainDistinctFrom"] and DOC["candidates"][1]["originalId"] in DOC["candidates"][0]["mustRemainDistinctFrom"],"separation")
 print("STAGE18_BATCH41_PASS scenarios=2 SHORT=16 DETAILED=24 EXTENSIONS=10")
 if args.negative:print("STAGE18_BATCH41_NEGATIVE_PASS",sum(negative(c) for c in DOC["candidates"]))
if __name__=="__main__":main()
