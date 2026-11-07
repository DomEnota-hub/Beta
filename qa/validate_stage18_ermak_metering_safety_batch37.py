#!/usr/bin/env python3
"""Ermak batch37 donor parity, graph and negative fail-closed QA."""
import argparse,copy,json,pathlib
R=pathlib.Path(__file__).resolve().parents[1]
D=json.loads((R/"docs/diagnostics/STAGE18_ERMAK_METERING_SAFETY_BATCH37_2026-11-07.json").read_text(encoding="utf-8"))
P=json.loads((R/"content-packs/electric/ermak/diagnostics/recommended/diagnostics-06.pack.json").read_text(encoding="utf-8"))
SRC={x["id"]:x["sourceObject"]["object"] for x in P["entries"]}
IDS=["ER-DIAG-117","ER-DIAG-118","ER-DIAG-119"]
FIELDS=[("originalId","id"),("title","title"),("symptom","symptom"),("sourceObjectStatus","status"),("sourceObjectApplicability","applicability"),("sourceObjectSystemIds","systemIds"),("sourceObjectEquipmentRefs","equipmentRefs"),("sourceObjectSourceRefs","sourceRefs")]
def req(x,msg):
 if not x:raise AssertionError(msg)
def check(c):
 id=c["originalId"];o=SRC[id]
 for a,b in FIELDS:req(c[a]==o[b],id+" donor "+a)
 for k in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified","exactInstalledVariantConfirmed","substantiveSafetyReviewed"):req(c[k] is False,k)
 req(c["publicationStatus"]=="CANDIDATE" and c["exactInstalledVariant"]=="UNKNOWN" and c["unknownVariantDisposition"]=="BLOCKED","publication/profile")
 req(c["profileApplicability"]==o["applicability"]["profiles"] and c["lateProfileRule"]==o["applicability"]["lateProfiles"],"profile parity")
 req(c["sourceObjectStatus"]==("BASE_CONFIRMED" if id==IDS[0] else "PROFILE_REQUIRED"),"status")
 req(id not in c["mustRemainDistinctFrom"] and len(c["mustRemainDistinctFrom"])>=3,"distinct")
 w=c["warningGate"];req(w=={"default":"HIDDEN","warningReadToEnd":True,"warningAcknowledged":True,"warningGrantsActionAuthority":False},"warning")
 s=c["safePolicy"];req(s["observationOnly"] is True and s["onlyPreviouslyRecorded"] is True and s["triState"]==["YES","NO","UNKNOWN"] and s["unknownMustStop"] is True and s["unknownProfile"]=="BLOCKED" and s["operationsAllowed"]==[] and s["activeFaultImmediateStop"] is True,"safe")
 req(c["deviceQA"]=="DEFERRED_TO_POST_RELEASE_DEVICE_QA","device")
 r=c["sourceRecords"];req(r["donor"]["commit"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff" and r["donor"]["packBlobSha"]=="5d016e774bf72c618f50aa01d213a9995ab9d441" and r["donor"]["rawGzipIndependentlyDecoded"] is False,"donor pin")
 req(all(x["currentOperatingAuthority"] is False for x in r.values()),"source authority")
 req(r["normative"]["status"]=="ACTION_AUTHORITY_UNKNOWN" and r["official"]["status"]=="DOCUMENT_EXISTS_CURRENT_CLAUSE_NOT_VERIFIED","normative gate")
 req(len(c["sourceConflicts"])==5 and all(x["resolution"] in ("NO_CAUSE_INFERENCE","PROFILE_BLOCKED","SOURCE_AUTHORITY_BLOCKED") for x in c["sourceConflicts"]),"conflicts")
 for mode,count in (("SHORT",8),("DETAILED",12)):
  g=c["versions"][mode];nodes=g["nodes"];m={n["id"]:n for n in nodes}
  req(len(nodes)==count and len(m)==count and g["startNodeId"]=="q-active","nodes")
  req(g["authoringStatus"]=="RESEARCH_DRAFT_BLOCKED" and g["operatingInstructionsIncluded"] is False,"graph gate")
  seen=set();stack=["q-active"]
  while stack:
   key=stack.pop()
   if key in seen:continue
   req(key in m,"dangling");seen.add(key);n=m[key]
   req(n["recordedOnly"] is True and n["operationRequested"] is False and n["causeConfirmed"] is False,"node safe")
   req(n["sourceRefs"] and all(x in r for x in n["sourceRefs"]),"node source")
   if n["type"]=="QUESTION":req(set(n["responses"])=={"YES","NO","UNKNOWN"} and n["responses"]["UNKNOWN"]=="stop-unknown","tri")
   else:req(n["type"] in ("STOP","OBSERVATION_REPORT") and n["responses"]=={},"terminal")
   stack.extend(n["responses"].values())
  req(len(seen)==count,"reachability")
  req(m["q-active"]["responses"]=={"YES":"stop-active","NO":"q-profile","UNKNOWN":"stop-unknown"},"active")
  req(m["q-profile"]["responses"]["NO"]=="stop-profile" and m["q-symptom"]["responses"]["NO"]=="stop-mismatch","profile/mismatch")
  req(m["report-match"]["type"]=="OBSERVATION_REPORT" and "НЕ ИНСТРУКЦИЯ" in m["report-match"]["text"],"report")
  if mode=="DETAILED":
   for q in ("q-evidence","q-differential","q-provenance"):req(m[q]["responses"]["NO"]=="stop-unverified","negative evidence")
 req(len(c["informationExtensions"])==5 and [x["version"] for x in c["informationExtensions"]]==["SHORT","SHORT","DETAILED","DETAILED","DETAILED"],"extensions")
 req(len(set(x["id"] for x in c["informationExtensions"]))==5,"extension identity")
 for x in c["informationExtensions"]:
  req(x["visibility"]==w and x["warningRequired"] is True and x["executable"] is False and x["actionAuthorityGranted"] is False and x["operationalSteps"]==[],"extension gate")
  req(x["sourceRefs"] and all(z in r for z in x["sourceRefs"]),"extension source")
  req(x["applicability"]=={"exactEquipmentProfileConfirmed":False,"modernSchemeConfirmed":False},"extension profile")
 req(len(c["independentCrosschecks"])==3 and all(x["verifiedAt"]=="2026-11-07" for x in c["independentCrosschecks"]),"crosschecks")
def negative(c):
 changes=[
 (["publicationStatus"],"PUBLISHED"),(["runtimeImport"],True),(["executable"],True),(["actionAuthorityGranted"],True),
 (["sourceAuthorityVerified"],True),(["exactInstalledVariantConfirmed"],True),(["substantiveSafetyReviewed"],True),
 (["exactInstalledVariant"],"KNOWN"),(["unknownVariantDisposition"],"ALLOWED"),(["sourceObjectStatus"],"WRONG"),
 (["sourceObjectSystemIds"],[]),(["sourceObjectEquipmentRefs"],[]),(["sourceObjectSourceRefs"],[]),
 (["warningGate","default"],"VISIBLE"),(["warningGate","warningReadToEnd"],False),(["warningGate","warningAcknowledged"],False),(["warningGate","warningGrantsActionAuthority"],True),
 (["safePolicy","onlyPreviouslyRecorded"],False),(["safePolicy","operationsAllowed"],["bypass"]),(["safePolicy","unknownMustStop"],False),(["safePolicy","activeFaultImmediateStop"],False),
 (["sourceRecords","donor","commit"],"bad"),(["sourceRecords","donor","rawGzipIndependentlyDecoded"],True),
 (["sourceRecords","official","currentOperatingAuthority"],True),(["sourceRecords","normative","status"],"AUTHORIZED"),
 (["sourceConflicts",0,"resolution"],"CAUSE_CONFIRMED"),(["mustRemainDistinctFrom"],[c["originalId"]]),
 (["versions","SHORT","nodes",0,"responses","YES"],"report-match"),(["versions","SHORT","nodes",1,"responses","NO"],"q-symptom"),(["versions","SHORT","nodes",2,"responses","UNKNOWN"],"report-match"),
 (["versions","DETAILED","nodes",3,"responses","NO"],"report-match"),(["versions","DETAILED","nodes",4,"responses","NO"],"report-match"),(["versions","DETAILED","nodes",5,"responses","NO"],"report-match"),
 (["versions","DETAILED","nodes",5,"operationRequested"],True),(["versions","SHORT","nodes",0,"recordedOnly"],False),
 (["informationExtensions",0,"visibility","default"],"VISIBLE"),(["informationExtensions",0,"operationalSteps"],["reset"]),(["informationExtensions",4,"actionAuthorityGranted"],True),
 (["independentCrosschecks",0,"verifiedAt"],"2020-01-01")
 ]
 for i,(path,value) in enumerate(changes):
  x=copy.deepcopy(c);p=x
  for key in path[:-1]:p=p[key]
  p[path[-1]]=value
  try:check(x)
  except (AssertionError,KeyError):continue
  raise AssertionError("escaped negative "+c["originalId"]+" "+str(i))
 return len(changes)
def main():
 a=argparse.ArgumentParser();a.add_argument("--negative",action="store_true");args=a.parse_args()
 l=D["ledger"];req(l["scenarioIds"]==IDS and [c["originalId"] for c in D["candidates"]]==IDS,"membership")
 req(l["donorPinnedSha"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff" and l["status"]=="CANDIDATE" and l["runtimeImport"] is False,"ledger")
 req(len(set(c["hazardCategory"] for c in D["candidates"]))==3,"hazards")
 for c in D["candidates"]:check(c)
 for mode in ("SHORT","DETAILED"):req(len(set(c["versions"][mode]["nodes"][2]["text"] for c in D["candidates"]))==3,"symptom uniqueness")
 print("STAGE18_BATCH37_PASS scenarios=3 SHORT=24 DETAILED=36 EXTENSIONS=15")
 if args.negative:print("STAGE18_BATCH37_NEGATIVE_PASS",sum(negative(c) for c in D["candidates"]))
if __name__=="__main__":main()
