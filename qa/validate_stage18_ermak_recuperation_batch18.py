#!/usr/bin/env python3
"""Stage18 batch18: source-bound recuperation and negative fail-closed tests."""
import argparse,copy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/"docs/diagnostics/STAGE18_ERMAK_RECUPERATION_BATCH18_2026-11-06.json").read_text(encoding="utf-8"))
PACK=json.loads((ROOT/"content-packs/electric/ermak/diagnostics/recommended/diagnostics-03.pack.json").read_text(encoding="utf-8"))
IDS=["ER-DIAG-057","ER-DIAG-058"]
SRC={e["id"]:e["sourceObject"]["object"] for e in PACK["entries"] if e["id"] in IDS}
PIN="3176d6ee228f0ed4b78371f45209e10c1c724eff"
BLOB="c3a22c62db42308eb4b7ee44ff2da02f47686625"
W={"default":"HIDDEN","warningReadToEnd":True,"warningAcknowledged":True,"warningGrantsActionAuthority":False}
HAZ={"ER-DIAG-057":"REGEN_NOT_ESTABLISHED","ER-DIAG-058":"REGEN_UNCOMMANDED_DROPOUT"}
FIELDS={"title":"title","symptom":"symptom","sourceObjectStatus":"status","sourceObjectApplicability":"applicability","sourceObjectSystemIds":"systemIds","sourceObjectEquipmentRefs":"equipmentRefs","sourceObjectSourceRefs":"sourceRefs"}
def req(v,m):
 if not v: raise AssertionError(m)
def check(c):
 ident=c["originalId"];req(ident in IDS and c["scenarioId"]=="ermak.diag."+ident,"identity")
 s=SRC[ident]
 for dest,key in FIELDS.items():req(c[dest]==s[key],"donor "+dest)
 req(c["families"]==s["applicability"]["families"] and c["profileApplicability"]==s["applicability"]["profiles"] and c["lateProfileRule"]==s["applicability"]["lateProfiles"],"profile exact")
 req(c["hazardCategory"]==HAZ[ident] and c["sourceObjectStatus"]=="BASE_CONFIRMED","hazard")
 req(c["authoringProfileId"]=="ermak-msud-n-early-traction-research-only" and c["earlyMsud"]=="MSUD-N_PROFILE_DEPENDENT" and c["lateMsud"]=="MSUD-015_NOT_EQUIVALENT","msud")
 req(c["exactInstalledVariant"]=="UNKNOWN" and c["unknownVariantDisposition"]=="BLOCKED","unknown profile")
 req(c["publicationStatus"]=="CANDIDATE" and c["runtimeImport"] is False and c["deviceQA"]=="DEFERRED_TO_POST_RELEASE_DEVICE_QA","publication")
 for k in ("executable","actionAuthorityGranted","sourceAuthorityVerified","exactInstalledVariantConfirmed","substantiveSafetyReviewed"):req(c[k] is False,k)
 req(c["warningGate"]==W and c["safePolicy"]=={"observationOnly":True,"onlyPreviouslyRecorded":True,"triState":["YES","NO","UNKNOWN"],"unknownMustStop":True,"unknownProfile":"BLOCKED","operationsAllowed":[],"activeFaultImmediateStop":True},"safety")
 req(len(c["mustRemainDistinctFrom"])==len(set(c["mustRemainDistinctFrom"]))==3 and ident not in c["mustRemainDistinctFrom"],"distinct")
 req([x["resolution"] for x in c["sourceConflicts"]]==["NO_CAUSE_INFERENCE","PROFILE_BLOCKED","SOURCE_AUTHORITY_BLOCKED"],"conflicts")
 refs=c["sourceRecords"];req(set(refs)=={"donor","manufacturer","equipment","maintenance","normative","memo","practice","safety"},"source classes")
 req(refs["donor"]["commit"]==PIN and refs["donor"]["blobSha"]==BLOB and refs["donor"]["objectId"]==ident and refs["donor"]["rawGzipIndependentlyDecoded"] is False,"pin")
 req(refs["manufacturer"]["sourceKind"]=="MANUFACTURER_ARCHIVAL_PUBLIC_2007" and refs["equipment"]["status"]=="PROFILE_DEPENDENT" and refs["maintenance"]["status"]=="MAINTENANCE_NOT_CREW_AUTHORITY","archive")
 req(refs["normative"]["status"]=="CURRENT_COMPLETENESS_UNKNOWN" and refs["memo"]["sourceKind"]=="HISTORICAL_TRAINING_PUBLIC" and refs["practice"]["status"]=="UNRESOLVED_NO_AUTHORITY","sources")
 req(all(v["currentOperatingAuthority"] is False for v in refs.values()),"authority")
 for mode,count in (("SHORT",8),("DETAILED",12)):
  g=c["versions"][mode];req(g["startNodeId"]=="q-active" and g["authoringStatus"]=="RESEARCH_DRAFT_BLOCKED" and g["operatingInstructionsIncluded"] is False,"graph gate")
  nodes={n["id"]:n for n in g["nodes"]};req(len(nodes)==len(g["nodes"])==count,"nodes")
  seen=set()
  def walk(k):
   req(k in nodes,"dangling "+k)
   if k in seen:return
   seen.add(k);n=nodes[k]
   req(n["recordedOnly"] is True and n["operationRequested"] is False and n["causeConfirmed"] is False,"no actions")
   req(set(n["sourceRefs"]).issubset(refs),"node sources")
   if n["type"]=="QUESTION":
    req(set(n["responses"])=={"YES","NO","UNKNOWN"} and n["responses"]["UNKNOWN"]=="stop-unknown","tri state")
    for nxt in n["responses"].values():walk(nxt)
   else:req(n["type"] in ("STOP","OBSERVATION_REPORT") and n["responses"]=={},"leaf")
  walk("q-active");req(len(seen)==count,"unreachable")
  req(nodes["q-active"]["responses"]["YES"]=="stop-active" and nodes["q-profile"]["responses"]["NO"]=="stop-profile" and nodes["q-symptom"]["responses"]["NO"]=="stop-mismatch","critical stops")
  if mode=="DETAILED":
   for k in ("q-evidence","q-separation","q-provenance"):req(nodes[k]["responses"]["NO"]=="stop-unverified","evidence stop")
 ex=c["informationExtensions"];req(len(ex)==len(set(x["id"] for x in ex))==5,"extensions")
 req([x["version"] for x in ex]==["SHORT","SHORT","DETAILED","DETAILED","DETAILED"],"extension versions")
 req([x["sourceRefs"] for x in ex]==[["donor"],["manufacturer"],["memo","practice"],["normative"],["safety","equipment","maintenance"]],"extension sources")
 for i,x in enumerate(ex,1):
  req(x["id"]==ident+"-INFO-"+str(i) and x["text"] and x["locator"],"extension identity")
  req(x["visibility"]==W and x["warningRequired"] is True and x["executable"] is False and x["actionAuthorityGranted"] is False and x["operationalSteps"]==[],"extension gate")
  req(x["applicability"]=={"exactEquipmentProfileConfirmed":False,"modernSchemeConfirmed":False},"extension profile")
 req(len(c["independentCrosschecks"])==3 and all(x["verifiedAt"]=="2026-11-06" for x in c["independentCrosschecks"]),"crosschecks")
def negative(c):
 changes=[
 (["publicationStatus"],"ACTIVE"),(["runtimeImport"],True),(["executable"],True),(["actionAuthorityGranted"],True),(["sourceAuthorityVerified"],True),
 (["exactInstalledVariantConfirmed"],True),(["substantiveSafetyReviewed"],True),(["exactInstalledVariant"],"MSUD-N"),(["unknownVariantDisposition"],"ALLOWED"),
 (["authoringProfileId"],"ermak-all"),(["earlyMsud"],"MSUD-015"),(["lateMsud"],"MSUD-N"),(["hazardCategory"],"OTHER"),(["title"],"WRONG"),(["symptom"],"WRONG"),
 (["sourceObjectStatus"],"EVOLUTION_CONFIRMED"),(["sourceObjectApplicability"],{}),(["sourceObjectSystemIds"],[]),(["sourceObjectEquipmentRefs"],[]),(["sourceObjectSourceRefs"],[]),
 (["families"],["2ES5K"]),(["profileApplicability"],["msud_015_extended"]),(["lateProfileRule"],"AS_LISTED"),(["sourceRecords","donor","commit"],"BAD"),
 (["sourceRecords","donor","blobSha"],"BAD"),(["sourceRecords","donor","rawGzipIndependentlyDecoded"],True),
 (["sourceRecords","manufacturer","currentOperatingAuthority"],True),(["sourceRecords","manufacturer","sourceKind"],"NORMATIVE"),
 (["sourceRecords","equipment","status"],"CURRENT"),(["sourceRecords","maintenance","status"],"CREW_AUTHORIZED"),
 (["sourceRecords","normative","status"],"VERIFIED_CURRENT"),(["sourceRecords","memo","sourceKind"],"NORMATIVE"),(["sourceRecords","practice","status"],"VERIFIED"),
 (["warningGate","warningReadToEnd"],False),(["warningGate","warningGrantsActionAuthority"],True),(["safePolicy","operationsAllowed"],["reset"]),
 (["safePolicy","onlyPreviouslyRecorded"],False),(["safePolicy","activeFaultImmediateStop"],False),
 (["versions","SHORT","nodes",0,"responses","YES"],"report-match"),(["versions","SHORT","nodes",1,"responses","NO"],"q-symptom"),
 (["versions","SHORT","nodes",2,"responses","UNKNOWN"],"report-match"),(["versions","DETAILED","nodes",3,"responses","NO"],"q-separation"),
 (["versions","DETAILED","nodes",4,"responses","UNKNOWN"],"q-provenance"),(["versions","DETAILED","nodes",5,"operationRequested"],True),
 (["informationExtensions",0,"sourceRefs"],["unverified"]),(["informationExtensions",0,"warningRequired"],False),
 (["informationExtensions",0,"operationalSteps"],["test"]),(["informationExtensions",0,"visibility","warningAcknowledged"],False),
 (["informationExtensions",4,"actionAuthorityGranted"],True),(["deviceQA"],"PASS"),(["sourceConflicts",2,"resolution"],"SOURCE_AUTHORITY_GRANTED"),
 (["mustRemainDistinctFrom"],[c["originalId"]])]
 for i,(path,value) in enumerate(changes):
  t=copy.deepcopy(c);o=t
  for k in path[:-1]:o=o[k]
  o[path[-1]]=value
  try:check(t)
  except (AssertionError,KeyError):continue
  raise AssertionError("negative escaped "+c["originalId"]+" "+str(i))
 return len(changes)
def main():
 p=argparse.ArgumentParser();p.add_argument("--negative",action="store_true");a=p.parse_args()
 l=DATA["ledger"];req(l["scenarioIds"]==IDS and [c["originalId"] for c in DATA["candidates"]]==IDS,"membership")
 req(l["donorPinnedSha"]==PIN and l["donorGzipBlobSha"]==BLOB and PACK["manifest"]["checksums"]["ermak_diagnostics.json.gz.gitBlob"]==BLOB,"pin")
 req(l["status"]=="CANDIDATE" and l["runtimeImport"] is False and l["actionAuthorityGranted"] is False,"ledger")
 for c in DATA["candidates"]:check(c)
 req(len({c["hazardCategory"] for c in DATA["candidates"]})==2,"distinct hazards")
 req(len({c["versions"]["DETAILED"]["nodes"][3]["text"] for c in DATA["candidates"]})==2,"distinct evidence")
 print("STAGE18_BATCH18_PASS 2 SHORT=8 DETAILED=12 EXTENSIONS=5")
 if a.negative:print("STAGE18_BATCH18_NEGATIVE_PASS",sum(negative(c) for c in DATA["candidates"]))
if __name__=="__main__":main()
