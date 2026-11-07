#!/usr/bin/env python3
"""Stage18 safety systems batch30: donor identity, route, source and negative gates."""
import argparse,copy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/"docs/diagnostics/STAGE18_ERMAK_SAFETY_BATCH30_2026-11-07.json").read_text(encoding="utf-8"))
P=json.loads((ROOT/"content-packs/electric/ermak/diagnostics/recommended/diagnostics-05.pack.json").read_text(encoding="utf-8"))
IDS=["ER-DIAG-093","ER-DIAG-094","ER-DIAG-095","ER-DIAG-096","ER-DIAG-097"]
SRC={x["id"]:x["sourceObject"]["object"] for x in P["entries"] if x["id"] in IDS}
SK={"donor","manufacturer","official","training","normative","safety"}
def req(x,m):
 if not x:raise AssertionError(m)
def graph(g,mode):
 nodes={n["id"]:n for n in g["nodes"]}
 req(len(nodes)==len(g["nodes"])==(8 if mode=="SHORT" else 12),"node count")
 req(g["startNodeId"]=="q-active" and g["authoringStatus"]=="RESEARCH_DRAFT_BLOCKED" and g["operatingInstructionsIncluded"] is False,"graph status")
 req(nodes["q-active"]["responses"]=={"YES":"stop-active","NO":"q-profile","UNKNOWN":"stop-unknown"},"active")
 req(nodes["q-profile"]["responses"]=={"YES":"q-symptom","NO":"stop-profile","UNKNOWN":"stop-unknown"},"profile")
 req(nodes["q-symptom"]["responses"]=={"YES":("q-evidence" if mode=="DETAILED" else "report-match"),"NO":"stop-mismatch","UNKNOWN":"stop-unknown"},"symptom")
 if mode=="DETAILED":
  for a,b in (("q-evidence","q-separation"),("q-separation","q-provenance"),("q-provenance","report-match")):
   req(nodes[a]["responses"]=={"YES":b,"NO":"stop-unverified","UNKNOWN":"stop-unknown"},"detailed fail-closed")
 seen=set()
 def walk(k):
  req(k in nodes,"dangling"); 
  if k in seen:return
  seen.add(k);n=nodes[k]
  req(bool(n["text"]) and n["recordedOnly"] is True and n["operationRequested"] is False and n["causeConfirmed"] is False,"unsafe node")
  req(bool(n["sourceRefs"]) and set(n["sourceRefs"])<=SK,"source refs")
  if n["type"]=="QUESTION":
   req(set(n["responses"])=={"YES","NO","UNKNOWN"} and n["responses"]["UNKNOWN"]=="stop-unknown","tri-state")
   for dest in n["responses"].values():walk(dest)
  else:req(n["type"] in {"STOP","OBSERVATION_REPORT"} and not n["responses"],"terminal")
 walk(g["startNodeId"]);req(len(seen)==len(nodes),"unreachable")
def check(c):
 i=c["originalId"];req(i in IDS and c["scenarioId"]=="ermak.diag."+i,"id")
 s=SRC[i]
 for a,b in (("title","title"),("symptom","symptom"),("sourceObjectStatus","status"),("sourceObjectApplicability","applicability"),("sourceObjectSystemIds","systemIds"),("sourceObjectEquipmentRefs","equipmentRefs"),("sourceObjectSourceRefs","sourceRefs")):req(c[a]==s[b],"donor "+a)
 a=s["applicability"]
 req(c["families"]==a["families"] and c["profileApplicability"]==a["profiles"] and c["lateProfileRule"]==a["lateProfiles"],"applicability")
 req(c["sourceObjectStatus"] in {"BASE_CONFIRMED","PROFILE_REQUIRED"},"donor status")
 req(c["exactInstalledVariant"]=="UNKNOWN" and c["unknownVariantDisposition"]=="BLOCKED","variant")
 req(c["earlyMsud"]=="MSUD_N_NOT_ASSUMED" and c["lateMsud"]=="MSUD-015_NOT_EQUIVALENT","MSUD")
 req(c["publicationStatus"]=="CANDIDATE" and c["runtimeImport"] is False and c["executable"] is False and c["deviceQA"]=="DEFERRED_TO_POST_RELEASE_DEVICE_QA","runtime")
 for k in ("actionAuthorityGranted","sourceAuthorityVerified","exactInstalledVariantConfirmed","substantiveSafetyReviewed"):req(c[k] is False,k)
 req(c["warningGate"]=={"default":"HIDDEN","warningReadToEnd":True,"warningAcknowledged":True,"warningGrantsActionAuthority":False},"warning")
 req(c["safePolicy"]=={"observationOnly":True,"onlyPreviouslyRecorded":True,"triState":["YES","NO","UNKNOWN"],"unknownMustStop":True,"unknownProfile":"BLOCKED","operationsAllowed":[],"activeFaultImmediateStop":True},"policy")
 req(len(c["mustRemainDistinctFrom"])==len(set(c["mustRemainDistinctFrom"]))==5 and i not in c["mustRemainDistinctFrom"],"distinct")
 r=c["sourceRecords"];req(set(r)==SK and all(x["currentOperatingAuthority"] is False for x in r.values()),"source")
 d=r["donor"];req(d["commit"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff" and d["blobSha"]=="c3a22c62db42308eb4b7ee44ff2da02f47686625" and d["packBlobSha"]==D["ledger"]["preservedPackBlobSha"] and d["objectId"]==i and d["rawGzipIndependentlyDecoded"] is False,"donor pin")
 req(r["normative"]["status"]=="ACTION_AUTHORITY_UNKNOWN" and r["official"]["status"]=="PRODUCT_SCOPE_NOT_INSTALLED_PROFILE","authority")
 req([x["resolution"] for x in c["sourceConflicts"]]==["NO_CAUSE_INFERENCE","PROFILE_BLOCKED","SOURCE_AUTHORITY_BLOCKED"],"conflict")
 req(set(c["versions"])=={"SHORT","DETAILED"},"versions")
 for m in ("SHORT","DETAILED"):graph(c["versions"][m],m)
 ex=c["informationExtensions"];req(len(ex)==len({x["id"] for x in ex})==5,"extensions")
 req([x["version"] for x in ex]==["SHORT","SHORT","DETAILED","DETAILED","DETAILED"],"extension modes")
 for j,x in enumerate(ex,1):
  req(x["id"]==i+"-INFO-"+str(j) and x["title"] and x["text"] and x["locator"] and set(x["sourceRefs"])<=SK,"extension fields")
  req(x["visibility"]==c["warningGate"] and x["warningRequired"] is True and x["executable"] is False and x["actionAuthorityGranted"] is False and x["operationalSteps"]==[],"extension safety")
  req(x["applicability"]=={"exactEquipmentProfileConfirmed":False,"modernSchemeConfirmed":False},"extension profile")
 req(len(c["independentCrosschecks"])==3 and all(x["verifiedAt"]=="2026-11-07" and x["status"]!="CURRENT_OPERATIONAL" for x in c["independentCrosschecks"]),"crosschecks")
def neg(c):
 tests=[
 (["title"],"fabricated"),(["symptom"],"fabricated"),(["sourceObjectStatus"],"ACTIVE"),(["sourceObjectApplicability"],{}),(["sourceObjectSystemIds"],[]),(["sourceObjectEquipmentRefs"],[]),(["sourceObjectSourceRefs"],[]),
 (["families"],["3ES5K"]),(["profileApplicability"],["all"]),(["lateProfileRule"],"AS_LISTED"),
 (["exactInstalledVariant"],"confirmed"),(["unknownVariantDisposition"],"ALLOW"),(["earlyMsud"],"MSUD-015"),(["lateMsud"],"MSUD-N"),
 (["publicationStatus"],"ACTIVE"),(["runtimeImport"],True),(["executable"],True),(["actionAuthorityGranted"],True),(["sourceAuthorityVerified"],True),(["exactInstalledVariantConfirmed"],True),(["substantiveSafetyReviewed"],True),(["deviceQA"],"PASS"),
 (["warningGate","default"],"VISIBLE"),(["warningGate","warningReadToEnd"],False),(["warningGate","warningAcknowledged"],False),(["warningGate","warningGrantsActionAuthority"],True),
 (["safePolicy","operationsAllowed"],["reset"]),(["safePolicy","onlyPreviouslyRecorded"],False),(["safePolicy","activeFaultImmediateStop"],False),
 (["sourceRecords","donor","commit"],"other"),(["sourceRecords","donor","blobSha"],"other"),(["sourceRecords","donor","rawGzipIndependentlyDecoded"],True),
 (["sourceRecords","official","currentOperatingAuthority"],True),(["sourceRecords","official","status"],"CURRENT_OPERATIONAL"),(["sourceRecords","normative","status"],"CREW_AUTHORIZED"),
 (["sourceConflicts",0,"resolution"],"CAUSE_CONFIRMED"),(["mustRemainDistinctFrom"],[c["originalId"]]),
 (["versions","SHORT","nodes",0,"responses","YES"],"report-match"),(["versions","SHORT","nodes",1,"responses","NO"],"q-symptom"),(["versions","SHORT","nodes",2,"responses","UNKNOWN"],"report-match"),
 (["versions","DETAILED","nodes",3,"responses","NO"],"q-separation"),(["versions","DETAILED","nodes",4,"responses","UNKNOWN"],"q-provenance"),(["versions","DETAILED","nodes",5,"operationRequested"],True),
 (["versions","SHORT","nodes",0,"recordedOnly"],False),(["informationExtensions",0,"sourceRefs"],["invalid"]),(["informationExtensions",0,"warningRequired"],False),
 (["informationExtensions",0,"operationalSteps"],["bypass"]),(["informationExtensions",0,"visibility","warningAcknowledged"],False),
 (["informationExtensions",4,"actionAuthorityGranted"],True),(["independentCrosschecks",0,"verifiedAt"],"2020-01-01")
 ]
 for ix,(path,val) in enumerate(tests):
  t=copy.deepcopy(c);v=t
  for k in path[:-1]:v=v[k]
  v[path[-1]]=val
  try:check(t)
  except (AssertionError,KeyError):continue
  raise AssertionError("negative mutation escaped "+c["originalId"]+" "+str(ix))
 return len(tests)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--negative",action="store_true");args=ap.parse_args()
 l=D["ledger"];req(l["scenarioIds"]==IDS and [x["originalId"] for x in D["candidates"]]==IDS,"membership")
 req(l["donorPinnedSha"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff" and l["donorGzipBlobSha"]=="c3a22c62db42308eb4b7ee44ff2da02f47686625" and l["preservedPackBlobSha"]=="69945cc0e6c5c316911ffab1489da9dfd3e8ba9a" and P["manifest"]["checksums"]["ermak_diagnostics.json.gz.gitBlob"]=="c3a22c62db42308eb4b7ee44ff2da02f47686625","pin")
 req(l["status"]=="CANDIDATE" and l["runtimeImport"] is False and l["actionAuthorityGranted"] is False,"ledger")
 req(len(SRC)==5 and len({x["hazardCategory"] for x in D["candidates"]})==5,"unique hazards")
 for c in D["candidates"]:check(c)
 for mode in ("SHORT","DETAILED"):
  req(len({c["versions"][mode]["nodes"][2]["text"] for c in D["candidates"]})==5,"scenario symptom distinct")
 req(len({c["versions"]["DETAILED"]["nodes"][3]["text"] for c in D["candidates"]})==5,"scenario evidence distinct")
 print("STAGE18_BATCH30_PASS 5 scenarios SHORT=40 DETAILED=60 EXTENSIONS=25")
 if args.negative:print("STAGE18_BATCH30_NEGATIVE_PASS",sum(neg(c) for c in D["candidates"]))
if __name__=="__main__":main()
