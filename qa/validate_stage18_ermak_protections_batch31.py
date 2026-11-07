#!/usr/bin/env python3
"""Stage18 batch31: independent source fields, safety, graph and negative mutations."""
import argparse,copy,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
D=json.loads((ROOT/"docs/diagnostics/STAGE18_ERMAK_PROTECTIONS_BATCH31_2026-11-07.json").read_text())
P5=json.loads((ROOT/"content-packs/electric/ermak/diagnostics/recommended/diagnostics-05.pack.json").read_text())
P6=json.loads((ROOT/"content-packs/electric/ermak/diagnostics/recommended/diagnostics-06.pack.json").read_text())
SRC={e["id"]:e["sourceObject"]["object"] for e in P5["entries"]+P6["entries"]}
IDS=["ER-DIAG-098","ER-DIAG-099","ER-DIAG-100","ER-DIAG-101","ER-DIAG-102"]
FIELDS=[("originalId","id"),("title","title"),("symptom","symptom"),("sourceObjectStatus","status"),("sourceObjectApplicability","applicability"),("sourceObjectSystemIds","systemIds"),("sourceObjectEquipmentRefs","equipmentRefs"),("sourceObjectSourceRefs","sourceRefs")]
def req(v,msg):
 if not v: raise AssertionError(msg)
def check(c):
 o=SRC[c["originalId"]]
 for a,b in FIELDS:req(c[a]==o[b],c["originalId"]+" donor "+a)
 req(c["publicationStatus"]=="CANDIDATE" and c["runtimeImport"] is False and c["executable"] is False and c["actionAuthorityGranted"] is False,"publication")
 req(c["sourceAuthorityVerified"] is False and c["exactInstalledVariantConfirmed"] is False and c["substantiveSafetyReviewed"] is False,"gates")
 req(c["exactInstalledVariant"]=="UNKNOWN" and c["unknownVariantDisposition"]=="BLOCKED","profile")
 req(c["sourceObjectStatus"]==o["status"] and c["lateProfileRule"]==o["applicability"]["lateProfiles"],"source status")
 w=c["warningGate"]
 req(w=={"default":"HIDDEN","warningReadToEnd":True,"warningAcknowledged":True,"warningGrantsActionAuthority":False},"warning")
 s=c["safePolicy"]
 req(s["observationOnly"] is True and s["onlyPreviouslyRecorded"] is True and s["triState"]==["YES","NO","UNKNOWN"] and s["unknownMustStop"] is True and s["unknownProfile"]=="BLOCKED" and s["operationsAllowed"]==[] and s["activeFaultImmediateStop"] is True,"safety")
 req(c["deviceQA"]=="DEFERRED_TO_POST_RELEASE_DEVICE_QA","device")
 req(c["sourceRecords"]["donor"]["commit"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff" and c["sourceRecords"]["donor"]["blobSha"]=="c3a22c62db42308eb4b7ee44ff2da02f47686625" and c["sourceRecords"]["donor"]["rawGzipIndependentlyDecoded"] is False,"donor pin")
 req(all(x["currentOperatingAuthority"] is False for x in c["sourceRecords"].values()),"source authority")
 req(c["sourceRecords"]["normative"]["status"]=="ACTION_AUTHORITY_UNKNOWN","normative")
 req(len(c["sourceConflicts"])==3 and all(x["resolution"] in ("NO_CAUSE_INFERENCE","PROFILE_BLOCKED","SOURCE_AUTHORITY_BLOCKED") for x in c["sourceConflicts"]),"conflicts")
 req(len(c["mustRemainDistinctFrom"])>=3 and c["originalId"] not in c["mustRemainDistinctFrom"],"distinct")
 for mode,count in (("SHORT",8),("DETAILED",12)):
  g=c["versions"][mode];ns=g["nodes"];mp={n["id"]:n for n in ns}
  req(len(ns)==count and len(mp)==count and g["startNodeId"]=="q-active","graph count")
  req(g["authoringStatus"]=="RESEARCH_DRAFT_BLOCKED" and g["operatingInstructionsIncluded"] is False,"graph authority")
  visited=set();stack=[g["startNodeId"]]
  while stack:
   k=stack.pop()
   if k in visited:continue
   req(k in mp,"dangling");visited.add(k);n=mp[k]
   req(n["recordedOnly"] is True and n["operationRequested"] is False and n["causeConfirmed"] is False,"node safety")
   req(n["sourceRefs"] and all(x in c["sourceRecords"] for x in n["sourceRefs"]),"node source")
   if n["type"]=="QUESTION":
    req(set(n["responses"])=={"YES","NO","UNKNOWN"} and n["responses"]["UNKNOWN"]=="stop-unknown","tri-state")
   else:req(n["type"] in ("STOP","OBSERVATION_REPORT") and n["responses"]=={},"terminal")
   stack.extend(n["responses"].values())
  req(len(visited)==count,"unreachable")
  req(mp["q-active"]["responses"]=={"YES":"stop-active","NO":"q-profile","UNKNOWN":"stop-unknown"},"active")
  req(mp["q-profile"]["responses"]["NO"]=="stop-profile","profile block")
  req(mp["stop-unknown"]["type"]=="STOP" and mp["stop-profile"]["type"]=="STOP" and mp["stop-active"]["type"]=="STOP","stops")
  req(mp["report-match"]["type"]=="OBSERVATION_REPORT" and "НЕ ИНСТРУКЦИЯ" in mp["report-match"]["text"],"report")
 req(len(c["informationExtensions"])==5 and [e["version"] for e in c["informationExtensions"]]==["SHORT","SHORT","DETAILED","DETAILED","DETAILED"],"extensions")
 for e in c["informationExtensions"]:
  req(e["visibility"]==w and e["warningRequired"] is True and e["executable"] is False and e["actionAuthorityGranted"] is False and e["operationalSteps"]==[],"extension gates")
  req(e["sourceRefs"] and all(x in c["sourceRecords"] for x in e["sourceRefs"]),"extension provenance")
  req(e["applicability"]=={"exactEquipmentProfileConfirmed":False,"modernSchemeConfirmed":False},"extension applicability")
 req(len(c["independentCrosschecks"])==3 and all(x["verifiedAt"]=="2026-11-07" for x in c["independentCrosschecks"]),"crosschecks")
def negatives(c):
 mutations=[
 (["publicationStatus"],"PUBLISHED"),(["runtimeImport"],True),(["executable"],True),(["actionAuthorityGranted"],True),
 (["sourceAuthorityVerified"],True),(["exactInstalledVariantConfirmed"],True),(["substantiveSafetyReviewed"],True),
 (["exactInstalledVariant"],"KNOWN"),(["unknownVariantDisposition"],"ALLOWED"),(["sourceObjectStatus"],"PROFILE_REQUIRED"),
 (["sourceObjectSystemIds"],[]),(["warningGate","default"],"VISIBLE"),(["warningGate","warningReadToEnd"],False),
 (["warningGate","warningAcknowledged"],False),(["warningGate","warningGrantsActionAuthority"],True),
 (["safePolicy","onlyPreviouslyRecorded"],False),(["safePolicy","operationsAllowed"],["bypass"]),
 (["safePolicy","activeFaultImmediateStop"],False),(["safePolicy","unknownMustStop"],False),
 (["sourceRecords","donor","commit"],"other"),(["sourceRecords","donor","rawGzipIndependentlyDecoded"],True),
 (["sourceRecords","normative","status"],"CREW_AUTHORIZED"),(["sourceRecords","official","currentOperatingAuthority"],True),
 (["sourceConflicts",0,"resolution"],"CAUSE_CONFIRMED"),(["mustRemainDistinctFrom"],[c["originalId"]]),
 (["versions","SHORT","nodes",0,"responses","YES"],"report-match"),
 (["versions","SHORT","nodes",1,"responses","NO"],"q-symptom"),
 (["versions","SHORT","nodes",2,"responses","UNKNOWN"],"report-match"),
 (["versions","DETAILED","nodes",3,"responses","NO"],"q-differential"),
 (["versions","DETAILED","nodes",4,"responses","UNKNOWN"],"q-provenance"),
 (["versions","DETAILED","nodes",5,"operationRequested"],True),
 (["versions","SHORT","nodes",0,"recordedOnly"],False),
 (["informationExtensions",0,"visibility","default"],"VISIBLE"),
 (["informationExtensions",0,"operationalSteps"],["reset"]),
 (["informationExtensions",4,"actionAuthorityGranted"],True),
 (["independentCrosschecks",0,"verifiedAt"],"2020-01-01")
 ]
 for idx,(path,value) in enumerate(mutations):
  x=copy.deepcopy(c);p=x
  for k in path[:-1]:p=p[k]
  p[path[-1]]=value
  try:check(x)
  except (AssertionError,KeyError):continue
  raise AssertionError("negative escaped "+c["originalId"]+" "+str(idx))
 return len(mutations)
def main():
 a=argparse.ArgumentParser();a.add_argument("--negative",action="store_true");args=a.parse_args()
 l=D["ledger"];req(l["scenarioIds"]==IDS and [x["originalId"] for x in D["candidates"]]==IDS,"membership")
 req(l["donorPinnedSha"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff" and l["donorGzipBlobSha"]=="c3a22c62db42308eb4b7ee44ff2da02f47686625" and l["status"]=="CANDIDATE" and l["runtimeImport"] is False and l["actionAuthorityGranted"] is False,"ledger")
 req(len(SRC)>=5 and len(set(x["hazardCategory"] for x in D["candidates"]))==5,"uniqueness")
 for c in D["candidates"]:check(c)
 for mode in ("SHORT","DETAILED"):req(len({c["versions"][mode]["nodes"][2]["text"] for c in D["candidates"]})==5,"distinct symptoms")
 print("STAGE18_BATCH31_PASS scenarios=5 SHORT=40 DETAILED=60 EXTENSIONS=25")
 if args.negative:print("STAGE18_BATCH31_NEGATIVE_PASS",sum(negatives(c) for c in D["candidates"]))
if __name__=="__main__":main()
