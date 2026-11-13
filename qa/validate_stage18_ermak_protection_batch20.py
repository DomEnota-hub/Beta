#!/usr/bin/env python3
"""Ermak stage18 batch20: independent donor parity, graph and negative safety gates."""
import argparse,copy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
D=json.loads((R/"docs/diagnostics/STAGE18_ERMAK_PROTECTION_BATCH20_2026-11-06.json").read_text(encoding="utf-8"))
P=json.loads((R/"content-packs/electric/ermak/diagnostics/recommended/diagnostics-04.pack.json").read_text(encoding="utf-8"))
IDS=["ER-DIAG-061","ER-DIAG-062","ER-DIAG-063","ER-DIAG-064"]
SRC={e["id"]:e["sourceObject"]["object"] for e in P["entries"] if e["id"] in IDS}
HAZ=["REGEN_EXCITATION_PROTECTION","REGEN_BALLAST_RESISTOR_PROTECTION","REGEN_WHEEL_SLIDE","REGEN_TC_INDICATION_STUCK"]
WARN={"default":"HIDDEN","warningReadToEnd":True,"warningAcknowledged":True,"warningGrantsActionAuthority":False}
POL={"observationOnly":True,"onlyPreviouslyRecorded":True,"triState":["YES","NO","UNKNOWN"],"unknownMustStop":True,"unknownProfile":"BLOCKED","operationsAllowed":[],"activeFaultImmediateStop":True}
SK={"donor","manufacturer","ventilation","maintenance","memo","practice","normative","brakeRules2026","maintenance3508","safety"}
def req(v,msg):
 if not v:raise AssertionError(msg)
def graph(g,mode):
 n={x["id"]:x for x in g["nodes"]}
 req(len(n)==len(g["nodes"])==(8 if mode=="SHORT" else 12),"nodes")
 req(g["startNodeId"]=="q-active" and g["authoringStatus"]=="RESEARCH_DRAFT_BLOCKED" and g["operatingInstructionsIncluded"] is False,"graph status")
 req(n["q-active"]["responses"]=={"YES":"stop-active","NO":"q-profile","UNKNOWN":"stop-unknown"},"active")
 req(n["q-profile"]["responses"]=={"YES":"q-symptom","NO":"stop-profile","UNKNOWN":"stop-unknown"},"profile")
 req(n["q-symptom"]["responses"]=={"YES":"q-evidence" if mode=="DETAILED" else "report-match","NO":"stop-mismatch","UNKNOWN":"stop-unknown"},"symptom")
 if mode=="DETAILED":
  for a,b in (("q-evidence","q-separation"),("q-separation","q-provenance"),("q-provenance","report-match")):req(n[a]["responses"]=={"YES":b,"NO":"stop-unverified","UNKNOWN":"stop-unknown"},"evidence")
 seen=set()
 def walk(k):
  req(k in n,"dangling "+k)
  if k in seen:return
  seen.add(k);x=n[k]
  req(x["text"] and x["recordedOnly"] is True and x["operationRequested"] is False and x["causeConfirmed"] is False,"action")
  req(x["sourceRefs"] and set(x["sourceRefs"])<=SK,"source")
  if x["type"]=="QUESTION":
   req(set(x["responses"])=={"YES","NO","UNKNOWN"} and x["responses"]["UNKNOWN"]=="stop-unknown","unknown")
   for y in x["responses"].values():walk(y)
  else:req(x["type"] in ("STOP","OBSERVATION_REPORT") and x["responses"]=={},"terminal")
 walk("q-active");req(len(seen)==len(n),"unreachable")
def check(c):
 i=c["originalId"];req(i in IDS and c["scenarioId"]=="ermak.diag."+i,"id")
 s=SRC[i]
 for a,b in (("title","title"),("symptom","symptom"),("sourceObjectStatus","status"),("sourceObjectApplicability","applicability"),("sourceObjectSystemIds","systemIds"),("sourceObjectEquipmentRefs","equipmentRefs"),("sourceObjectSourceRefs","sourceRefs")):req(c[a]==s[b],"donor "+a)
 req(c["hazardCategory"]==HAZ[IDS.index(i)] and c["sourceObjectStatus"]=="BASE_CONFIRMED","hazard")
 req(c["families"]==s["applicability"]["families"] and c["profileApplicability"]==s["applicability"]["profiles"] and c["lateProfileRule"]==s["applicability"]["lateProfiles"],"profile")
 req(c["authoringProfileId"]=="ermak-msud-n-early-traction-research-only" and c["earlyMsud"]=="MSUD-N_PROFILE_DEPENDENT" and c["lateMsud"]=="MSUD-015_NOT_EQUIVALENT","MSUD")
 req(c["exactInstalledVariant"]=="UNKNOWN" and c["unknownVariantDisposition"]=="BLOCKED","unknown profile")
 req(c["publicationStatus"]=="CANDIDATE" and c["runtimeImport"] is False and c["executable"] is False and c["deviceQA"]=="DEFERRED_TO_POST_RELEASE_DEVICE_QA","publication")
 for k in ("actionAuthorityGranted","sourceAuthorityVerified","exactInstalledVariantConfirmed","substantiveSafetyReviewed"):req(c[k] is False,k)
 req(c["warningGate"]==WARN and c["safePolicy"]==POL,"safety")
 req(len(c["mustRemainDistinctFrom"])==len(set(c["mustRemainDistinctFrom"]))==3 and i not in c["mustRemainDistinctFrom"],"distinct")
 req(set(c["sourceRecords"])==SK,"source records")
 r=c["sourceRecords"];req(r["donor"]["commit"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff" and r["donor"]["blobSha"]=="c3a22c62db42308eb4b7ee44ff2da02f47686625" and r["donor"]["objectId"]==i and r["donor"]["rawGzipIndependentlyDecoded"] is False,"pin")
 req(r["manufacturer"]["status"]=="ARCHIVAL_VARIANT_DEPENDENT" and r["memo"]["status"]=="HISTORICAL_NOT_OPERATIONAL" and r["practice"]["status"]=="UNRESOLVED_NO_AUTHORITY","source trust")
 req(r["brakeRules2026"]["status"]=="DOCUMENT_IDENTIFIED_SPECIFIC_AUTHORITY_UNVERIFIED" and r["maintenance3508"]["status"]=="MAINTENANCE_SCOPE_NOT_CREW_AUTHORITY","normative")
 req(all(x["currentOperatingAuthority"] is False for x in r.values()),"authority")
 req([x["resolution"] for x in c["sourceConflicts"]]==["NO_CAUSE_INFERENCE","PROFILE_BLOCKED","SOURCE_AUTHORITY_BLOCKED"],"conflicts")
 req(set(c["versions"])=={"SHORT","DETAILED"},"versions")
 for m in ("SHORT","DETAILED"):graph(c["versions"][m],m)
 ex=c["informationExtensions"];req(len(ex)==len({x["id"] for x in ex})==5,"extensions")
 req([x["version"] for x in ex]==["SHORT","SHORT","DETAILED","DETAILED","DETAILED"],"extension versions")
 req([x["sourceRefs"] for x in ex][:4]==[["donor"],["manufacturer"],["memo","practice"],["normative","brakeRules2026","maintenance3508"]],"extension sources")
 for j,x in enumerate(ex,1):
  req(x["id"]==i+"-INFO-"+str(j) and x["title"] and x["text"] and x["locator"],"extension id")
  req(x["visibility"]==WARN and x["warningRequired"] is True and x["executable"] is False and x["actionAuthorityGranted"] is False and x["operationalSteps"]==[],"extension safety")
  req(x["applicability"]=={"exactEquipmentProfileConfirmed":False,"modernSchemeConfirmed":False} and set(x["sourceRefs"])<=SK,"extension profile")
 req(len(c["independentCrosschecks"])==3 and all(x["verifiedAt"]=="2026-11-06" for x in c["independentCrosschecks"]),"crosscheck")
def neg(c):
 tests=[
 (["title"],"wrong"),(["symptom"],"wrong"),(["hazardCategory"],"wrong"),(["sourceObjectStatus"],"EVOLUTION_CONFIRMED"),(["sourceObjectApplicability"],{}),(["sourceObjectSystemIds"],[]),(["sourceObjectEquipmentRefs"],[]),(["sourceObjectSourceRefs"],[]),(["families"],["2ES5K"]),(["profileApplicability"],["msud_015_extended"]),(["lateProfileRule"],"ALL"),(["authoringProfileId"],"all"),(["earlyMsud"],"MSUD-015"),(["lateMsud"],"MSUD-N"),(["exactInstalledVariant"],"base_early"),(["unknownVariantDisposition"],"ALLOWED"),(["publicationStatus"],"ACTIVE"),(["runtimeImport"],True),(["executable"],True),(["actionAuthorityGranted"],True),(["sourceAuthorityVerified"],True),(["exactInstalledVariantConfirmed"],True),(["substantiveSafetyReviewed"],True),(["deviceQA"],"PASS"),(["warningGate","default"],"VISIBLE"),(["warningGate","warningReadToEnd"],False),(["warningGate","warningAcknowledged"],False),(["warningGate","warningGrantsActionAuthority"],True),(["safePolicy","operationsAllowed"],["reset"]),(["safePolicy","onlyPreviouslyRecorded"],False),(["safePolicy","activeFaultImmediateStop"],False),(["sourceRecords","donor","commit"],"wrong"),(["sourceRecords","donor","blobSha"],"wrong"),(["sourceRecords","donor","rawGzipIndependentlyDecoded"],True),(["sourceRecords","manufacturer","status"],"CURRENT"),(["sourceRecords","memo","status"],"CURRENT"),(["sourceRecords","practice","status"],"VERIFIED"),(["sourceRecords","brakeRules2026","status"],"CREW_AUTHORIZED"),(["sourceRecords","maintenance3508","status"],"CREW_AUTHORIZED"),(["sourceRecords","safety","currentOperatingAuthority"],True),(["sourceConflicts",0,"resolution"],"CAUSE_CONFIRMED"),(["mustRemainDistinctFrom"],[c["originalId"]]),(["versions","SHORT","nodes",0,"responses","YES"],"report-match"),(["versions","SHORT","nodes",1,"responses","NO"],"q-symptom"),(["versions","SHORT","nodes",2,"responses","UNKNOWN"],"report-match"),(["versions","DETAILED","nodes",3,"responses","NO"],"q-separation"),(["versions","DETAILED","nodes",4,"responses","UNKNOWN"],"q-provenance"),(["versions","DETAILED","nodes",5,"operationRequested"],True),(["versions","SHORT","nodes",0,"recordedOnly"],False),(["informationExtensions",0,"sourceRefs"],["unknown"]),(["informationExtensions",0,"warningRequired"],False),(["informationExtensions",0,"operationalSteps"],["reset"]),(["informationExtensions",0,"visibility","warningAcknowledged"],False),(["informationExtensions",4,"actionAuthorityGranted"],True),(["independentCrosschecks",0,"verifiedAt"],"2024-01-01")]
 for j,(path,v) in enumerate(tests):
  t=copy.deepcopy(c);x=t
  for p in path[:-1]:x=x[p]
  x[path[-1]]=v
  try:check(t)
  except (AssertionError,KeyError):continue
  raise AssertionError("mutation escaped "+c["originalId"]+" "+str(j))
 return len(tests)
def main():
 p=argparse.ArgumentParser();p.add_argument("--negative",action="store_true");a=p.parse_args()
 l=D["ledger"];req(l["scenarioIds"]==IDS and [c["originalId"] for c in D["candidates"]]==IDS,"membership")
 req(l["donorPinnedSha"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff" and l["donorGzipBlobSha"]=="c3a22c62db42308eb4b7ee44ff2da02f47686625" and P["manifest"]["checksums"]["ermak_diagnostics.json.gz.gitBlob"]=="c3a22c62db42308eb4b7ee44ff2da02f47686625","pin")
 req(l["status"]=="CANDIDATE" and l["runtimeImport"] is False and l["actionAuthorityGranted"] is False,"ledger")
 for c in D["candidates"]:check(c)
 req(len({c["hazardCategory"] for c in D["candidates"]})==4 and len({c["versions"]["DETAILED"]["nodes"][3]["text"] for c in D["candidates"]})==4,"independence")
 print("STAGE18_BATCH20_PASS 4 scenarios SHORT=8 DETAILED=12 EXTENSIONS=5")
 if a.negative:print("STAGE18_BATCH20_NEGATIVE_PASS",sum(neg(c) for c in D["candidates"]))
if __name__=="__main__":main()
