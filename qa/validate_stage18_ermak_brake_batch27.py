#!/usr/bin/env python3
"""Stage18 batch27: five independent brake scenarios, donor identity, graph and negative safety QA."""
import argparse, copy, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/"docs/diagnostics/STAGE18_ERMAK_BRAKE_BATCH27_2026-11-07.json").read_text(encoding="utf-8"))
P=json.loads((ROOT/"content-packs/electric/ermak/diagnostics/recommended/diagnostics-05.pack.json").read_text(encoding="utf-8"))
IDS=["ER-DIAG-081","ER-DIAG-082","ER-DIAG-083","ER-DIAG-084","ER-DIAG-085"]
SRC={x["id"]:x["sourceObject"]["object"] for x in P["entries"] if x["id"] in IDS}
HAZ=["RELEASE_NOT_ACHIEVED_VS_RESIDUAL_PRESSURE_MECHANICS","SINGLE_BOGIE_NO_TC_PRESSURE_VS_GENERAL_BRAKE_FAILURE","RESIDUAL_TC_PRESSURE_AFTER_RELEASE_VS_BROAD_NO_RELEASE","UNCOMMANDED_BRAKING_VS_TRAIN_LINE_EPK_SUBSTITUTION","DIRECT_BRAKE_NO_EFFECT_VS_AUTOMATIC_CHANNEL"]
SK={"donor","manufacturer","subsystem","operational","training","normative","safety"}
WARN={"default":"HIDDEN","warningReadToEnd":True,"warningAcknowledged":True,"warningGrantsActionAuthority":False}
POL={"observationOnly":True,"onlyPreviouslyRecorded":True,"triState":["YES","NO","UNKNOWN"],"unknownMustStop":True,"unknownProfile":"BLOCKED","operationsAllowed":[],"activeFaultImmediateStop":True}
def req(ok,msg):
 if not ok: raise AssertionError(msg)
def graph(g,mode):
 nodes={x["id"]:x for x in g["nodes"]}
 req(len(nodes)==len(g["nodes"])==(8 if mode=="SHORT" else 12),"node count")
 req(g["startNodeId"]=="q-active" and g["authoringStatus"]=="RESEARCH_DRAFT_BLOCKED" and g["operatingInstructionsIncluded"] is False,"graph policy")
 req(nodes["q-active"]["responses"]=={"YES":"stop-active","NO":"q-profile","UNKNOWN":"stop-unknown"},"active")
 req(nodes["q-profile"]["responses"]=={"YES":"q-symptom","NO":"stop-profile","UNKNOWN":"stop-unknown"},"profile")
 req(nodes["q-symptom"]["responses"]=={"YES":("q-evidence" if mode=="DETAILED" else "report-match"),"NO":"stop-mismatch","UNKNOWN":"stop-unknown"},"symptom")
 if mode=="DETAILED":
  for a,b in (("q-evidence","q-separation"),("q-separation","q-provenance"),("q-provenance","report-match")):
   req(nodes[a]["responses"]=={"YES":b,"NO":"stop-unverified","UNKNOWN":"stop-unknown"},"evidence")
 seen=set()
 def walk(key):
  req(key in nodes,"dangling")
  if key in seen:return
  seen.add(key);x=nodes[key]
  req(bool(x["text"]) and x["recordedOnly"] is True and x["operationRequested"] is False and x["causeConfirmed"] is False,"unsafe node")
  req(bool(x["sourceRefs"]) and set(x["sourceRefs"])<=SK,"unknown source")
  if x["type"]=="QUESTION":
   req(set(x["responses"])=={"YES","NO","UNKNOWN"} and x["responses"]["UNKNOWN"]=="stop-unknown","unknown not closed")
   for v in x["responses"].values():walk(v)
  else:req(x["type"] in ("STOP","OBSERVATION_REPORT") and x["responses"]=={},"unsafe terminal")
 walk(g["startNodeId"]);req(len(seen)==len(nodes),"unreachable")
def check(c):
 i=c["originalId"];req(i in IDS and c["scenarioId"]=="ermak.diag."+i,"identity")
 s=SRC[i]
 for a,b in (("title","title"),("symptom","symptom"),("sourceObjectStatus","status"),("sourceObjectApplicability","applicability"),("sourceObjectSystemIds","systemIds"),("sourceObjectEquipmentRefs","equipmentRefs"),("sourceObjectSourceRefs","sourceRefs")):req(c[a]==s[b],"donor "+a)
 req(c["hazardCategory"]==HAZ[IDS.index(i)],"hazard")
 req(c["families"]==s["applicability"]["families"] and c["profileApplicability"]==s["applicability"]["profiles"] and c["lateProfileRule"]==s["applicability"]["lateProfiles"],"profile parity")
 req(c["authoringProfileId"]==("ermak-brake-profile-required-research-only" if s["status"]=="PROFILE_REQUIRED" else "ermak-msud-n-early-brake-research-only"),"authoring profile")
 req(c["earlyMsud"]==("MSUD_N_NOT_ASSUMED" if s["status"]=="PROFILE_REQUIRED" else "MSUD-N_PROFILE_DEPENDENT") and c["lateMsud"]=="MSUD-015_NOT_EQUIVALENT","MSUD")
 req(c["exactInstalledVariant"]=="UNKNOWN" and c["unknownVariantDisposition"]=="BLOCKED","variant")
 req(c["publicationStatus"]=="CANDIDATE" and c["runtimeImport"] is False and c["executable"] is False and c["deviceQA"]=="DEFERRED_TO_POST_RELEASE_DEVICE_QA","runtime")
 for k in ("actionAuthorityGranted","sourceAuthorityVerified","exactInstalledVariantConfirmed","substantiveSafetyReviewed"):req(c[k] is False,k)
 req(c["warningGate"]==WARN and c["safePolicy"]==POL,"safety policy")
 req(len(c["mustRemainDistinctFrom"])==len(set(c["mustRemainDistinctFrom"]))==3 and i not in c["mustRemainDistinctFrom"],"distinct")
 req(set(c["sourceRecords"])==SK and all(x["currentOperatingAuthority"] is False for x in c["sourceRecords"].values()),"source roles")
 r=c["sourceRecords"];d=r["donor"]
 req(d["commit"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff" and d["blobSha"]=="c3a22c62db42308eb4b7ee44ff2da02f47686625" and d["objectId"]==i,"donor pin")
 req(d["packBlobSha"]==D["ledger"]["preservedPackBlobSha"] and d["rawGzipIndependentlyDecoded"] is False and d["status"]=="PROJECTED_FIELDS_MATCH_RAW_PARITY_NOT_RECHECKED","donor honesty")
 req(r["normative"]["status"]=="EFFECTIVE_DATE_CONFIRMED_ACTION_AUTHORITY_UNKNOWN" and r["training"]["status"]=="HISTORICAL_NOT_OPERATIONAL","source status")
 req([x["resolution"] for x in c["sourceConflicts"]]==["NO_CAUSE_INFERENCE","PROFILE_BLOCKED","SOURCE_AUTHORITY_BLOCKED"],"conflict")
 req(set(c["versions"])=={"SHORT","DETAILED"},"versions")
 for m in ("SHORT","DETAILED"):graph(c["versions"][m],m)
 ex=c["informationExtensions"];req(len(ex)==len({x["id"] for x in ex})==5,"extensions")
 req([x["version"] for x in ex]==["SHORT","SHORT","DETAILED","DETAILED","DETAILED"],"extension modes")
 req([x["sourceRefs"] for x in ex]==[["donor"],["manufacturer","subsystem"],["training"],["normative","operational"],["safety","manufacturer"]],"extension sources")
 for j,x in enumerate(ex,1):
  req(x["id"]==i+"-INFO-"+str(j) and x["title"] and x["text"] and x["locator"],"extension identity")
  req(x["visibility"]==WARN and x["warningRequired"] is True and x["executable"] is False and x["actionAuthorityGranted"] is False and x["operationalSteps"]==[],"extension safety")
  req(x["applicability"]=={"exactEquipmentProfileConfirmed":False,"modernSchemeConfirmed":False},"extension applicability")
 req(len(c["independentCrosschecks"])==3 and all(x["verifiedAt"]=="2026-11-07" and x["status"]!="CURRENT_OPERATIONAL" for x in c["independentCrosschecks"]),"crosscheck")
def neg(c):
 mutations=[
 (["title"],"fake"),(["symptom"],"fake"),(["sourceObjectStatus"],"ACTIVE"),(["sourceObjectApplicability"],{}),(["sourceObjectSystemIds"],[]),(["sourceObjectEquipmentRefs"],[]),(["sourceObjectSourceRefs"],[]),
 (["families"],["2ES5K"]),(["profileApplicability"],["late"]),(["lateProfileRule"],"ALL"),(["authoringProfileId"],"other"),(["earlyMsud"],"MSUD-015"),(["lateMsud"],"MSUD-N"),
 (["exactInstalledVariant"],"verified"),(["unknownVariantDisposition"],"ALLOWED"),(["publicationStatus"],"ACTIVE"),(["runtimeImport"],True),(["executable"],True),(["actionAuthorityGranted"],True),
 (["sourceAuthorityVerified"],True),(["exactInstalledVariantConfirmed"],True),(["substantiveSafetyReviewed"],True),(["deviceQA"],"PASS"),
 (["warningGate","default"],"VISIBLE"),(["warningGate","warningReadToEnd"],False),(["warningGate","warningAcknowledged"],False),(["warningGate","warningGrantsActionAuthority"],True),
 (["safePolicy","operationsAllowed"],["reset"]),(["safePolicy","onlyPreviouslyRecorded"],False),(["safePolicy","activeFaultImmediateStop"],False),
 (["sourceRecords","donor","commit"],"bad"),(["sourceRecords","donor","blobSha"],"bad"),(["sourceRecords","donor","rawGzipIndependentlyDecoded"],True),
 (["sourceRecords","manufacturer","currentOperatingAuthority"],True),(["sourceRecords","training","status"],"CURRENT"),(["sourceRecords","normative","status"],"CREW_AUTHORIZED"),
 (["sourceConflicts",0,"resolution"],"CAUSE_CONFIRMED"),(["mustRemainDistinctFrom"],[c["originalId"]]),
 (["versions","SHORT","nodes",0,"responses","YES"],"report-match"),(["versions","SHORT","nodes",1,"responses","NO"],"q-symptom"),(["versions","SHORT","nodes",2,"responses","UNKNOWN"],"report-match"),
 (["versions","DETAILED","nodes",3,"responses","NO"],"q-separation"),(["versions","DETAILED","nodes",4,"responses","UNKNOWN"],"q-provenance"),(["versions","DETAILED","nodes",5,"operationRequested"],True),
 (["versions","SHORT","nodes",0,"recordedOnly"],False),(["informationExtensions",0,"sourceRefs"],["unknown"]),(["informationExtensions",0,"warningRequired"],False),
 (["informationExtensions",0,"operationalSteps"],["reset"]),(["informationExtensions",0,"visibility","warningAcknowledged"],False),
 (["informationExtensions",4,"actionAuthorityGranted"],True),(["independentCrosschecks",0,"verifiedAt"],"2024-01-01")
 ]
 for j,(path,value) in enumerate(mutations):
  t=copy.deepcopy(c);x=t
  for p in path[:-1]:x=x[p]
  x[path[-1]]=value
  try:check(t)
  except (AssertionError,KeyError):continue
  raise AssertionError("mutation escaped "+c["originalId"]+" "+str(j))
 return len(mutations)
def main():
 p=argparse.ArgumentParser();p.add_argument("--negative",action="store_true");a=p.parse_args()
 l=D["ledger"]
 req(l["scenarioIds"]==IDS and [x["originalId"] for x in D["candidates"]]==IDS,"membership")
 req(l["donorPinnedSha"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff" and l["donorGzipBlobSha"]=="c3a22c62db42308eb4b7ee44ff2da02f47686625" and P["manifest"]["checksums"]["ermak_diagnostics.json.gz.gitBlob"]=="c3a22c62db42308eb4b7ee44ff2da02f47686625","pin")
 req(l["status"]=="CANDIDATE" and l["runtimeImport"] is False and l["actionAuthorityGranted"] is False,"ledger")
 req(len(SRC)==5 and len(set(HAZ))==5,"unique source ids and hazards")
 for c in D["candidates"]:check(c)
 req(len({c["versions"]["DETAILED"]["nodes"][3]["text"] for c in D["candidates"]})==5,"scenario evidence distinct")
 req(len({c["versions"]["DETAILED"]["nodes"][4]["text"] for c in D["candidates"]})==5,"scenario discrimination distinct")
 print("STAGE18_BATCH27_PASS 5 scenarios SHORT=40 DETAILED=60 EXTENSIONS=25")
 if a.negative:print("STAGE18_BATCH27_NEGATIVE_PASS",sum(neg(c) for c in D["candidates"]))
if __name__=="__main__":main()
