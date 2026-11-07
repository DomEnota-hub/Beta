#!/usr/bin/env python3
"""Stage7 source-first research preflight. Does NOT authorize locomotive operations."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
BLOB = "090d448d0e9de20d002edf07361764e524298bf8"
PATHS = {
 "vl80s.diag.gv-air-loss": "content-packs/electric/vl80s/diagnostics/authoring/stage7-gv-air-loss.research.json",
 "vl80s.diag.ekg-position-mismatch": "content-packs/electric/vl80s/diagnostics/authoring/stage7-ekg-position-mismatch.research.json",
}
DISTINCT = {
 "vl80s.diag.gv-air-loss": {"vl80s.diag.gv-no-open", "vl80s.diag.gv-no-close"},
 "vl80s.diag.ekg-position-mismatch": {"vl80s.diag.ekg-stuck", "vl80s.diag.ekg-slow-transition"},
}
CLAIMS = {
 "vl80s.diag.gv-air-loss": {"S7-GV-1990-01", "S7-GV-1990-02"},
 "vl80s.diag.ekg-position-mismatch": {"S7-EKG-1990-01", "S7-EKG-1990-02"},
}
def require(ok, message):
 if not ok: raise ValueError(message)
def graph(nodes, start, source):
 by = {n["id"]:n for n in nodes}
 require(len(by)==len(nodes) and start in by, "duplicate or invalid graph start")
 for n in nodes:
  require(n["sourceRefs"]==[source] and n["operationRequested"] is False, "unattributed operation")
  if n["type"]=="QUESTION":
   edges=n["responses"]
   require(set(edges)=={"YES","NO","UNKNOWN"} and edges["YES"]!=edges["NO"],"not tri-state")
   require(all(t in by for t in edges.values()) and by[edges["UNKNOWN"]]["type"]=="STOP","UNKNOWN does not STOP")
  else:
   require(n["type"] in {"OBSERVATION_REPORT","STOP"} and n["responses"]=={} and n["causeConfirmed"] is False,"false cause")
 seen={start}; pending=[start]
 while pending:
  for dest in by[pending.pop()]["responses"].values():
   if dest not in seen: seen.add(dest); pending.append(dest)
 require(len(seen)==len(nodes),"unreachable node")
def check(d, inventory):
 require(d["schemaVersion"]=="diagnostic-stage7-source-first/1" and d["stage"]=="7/51","wrong stage")
 sid=d["scenarioId"]
 require(sid in PATHS and d["originalId"]==sid.split("vl80s.diag.")[1],"wrong canonical identity")
 require(set(d["mustRemainDistinctFrom"])==DISTINCT[sid] and sid not in d["mustRemainDistinctFrom"],"conflated symptoms")
 require(d["donorPinnedSha"]==DONOR and d["donorBlobSha"]==BLOB and d["donorLayer"]=="DiagnosticExtendedCatalog.kt","donor drift")
 require(d["authoringProfileId"]=="vl80s-general","profile drift")
 require(d["publicationStatus"]=="CANDIDATE" and d["runtimeImport"] is False and d["executable"] is False and d["actionAuthorityGranted"] is False and d["observationOnly"] is True,"candidate published")
 require(all(d[k] is False for k in ("sourceAuthorityVerified","exactInstalledVariantConfirmed","technicalClaimsReviewed","substantiveSafetyReviewed")),"forged review")
 require(d["warningGate"]=={"default":"HIDDEN","extendedEnabled":True,"warningReadToEnd":True,"warningAcknowledged":True,"warningGrantsActionAuthority":False},"warning bypass")
 row=next((r for r in inventory["rows"] if r["scenarioId"]==sid),None)
 require(row and row["sourceScenarioId"]==d["originalId"] and row["variantIds"]==["vl80s-general"] and row["graph"]["nodeCount"]==3 and all(row[k]=="NOT_AUTHORED" for k in ("shortVersion","detailedVersion","shortExtendedBranch","detailedExtendedBranch")),"canonical corpus changed")
 donor=d["sourceRecords"]["donorSeed"]
 require(donor["commit"]==DONOR and donor["blobSha"]==BLOB and donor["sourcePointer"]=='Seed("'+d["originalId"]+'")' and donor["excerptFields"]["summary"]==d["reportedSummary"] and donor["excerptFields"]["danger"]==d["reportedDanger"],"donor seed misquoted")
 require(all(donor[k] is False for k in ("currentActionAuthorityVerified","exactInstalledEquipmentVerified","operationalProcedureImported")),"donor promoted")
 manual=d["sourceRecords"]["manual1990"]
 require(manual["publishedYear"]==1990 and manual["isbn"]=="5-277-01048-3" and manual["sourceTextLocated"] is True and manual["url"]=="https://ru.djvu.online/file/wXVHhRmTUUuqq","historical source missing")
 require(all(manual[k] is False for k in ("currentActionAuthorityVerified","exactInstalledEquipmentVerified","completeModernEditionValidated","operationalProcedureImported")),"historical source promoted")
 claims=d["historicalClaims"]
 require({c["claimId"] for c in claims}==CLAIMS[sid] and len(claims)==2,"historical claim IDs changed")
 for c in claims:
  require(c["sourceId"]=="manual1990" and c["sourcePointer"] in manual["verifiedLocators"] and c["historicalTextLocated"] is True and bool(c["claim"]),"unbound historical claim")
  require(c["provesCurrentEquipment"] is False and c["provesFaultCause"] is False and c["authorizesAction"] is False and c["operationalSteps"]==[],"historical claim promoted")
 require(set(d["versions"])=={"SHORT","DETAILED"},"missing versions")
 counts={}; identities=set(); focuses=set()
 for version in ("SHORT","DETAILED"):
  route=d["versions"][version]
  require(route["authoringStatus"]=="RESEARCH_DRAFT_BLOCKED" and route["independentTechnicalReview"]=="REQUIRED" and route["operatingInstructionsIncluded"] is False,"route prematurely approved")
  graph(route["nodes"],route["startNodeId"],"donorSeed")
  counts[version]=len(route["nodes"])
  alts=route["extendedRoutes"]
  require(len(alts)==(2 if version=="SHORT" else 3),"source variations missing")
  require([a["sourceId"] for a in alts]==(["donorSeed","manual1990"] if version=="SHORT" else ["donorSeed","manual1990","manual1990"]),"wrong alternative provenance")
  for a in alts:
   require(a["approachId"] not in identities and a["approachFocus"] not in focuses,"duplicated approach")
   identities.add(a["approachId"]); focuses.add(a["approachFocus"])
   require(a["publicationStatus"]=="CANDIDATE" and a["actionDisposition"]=="INFORMATION_ONLY" and a["executable"] is False and a["actionAuthorityGranted"] is False and a["operationalSteps"]==[] and a["technicalClaimReview"]=="REQUIRES_EXPERT","unsafe alternative")
   require(a["applicability"]["profileId"]=="vl80s-general" and a["applicability"]["exactEquipmentProfileConfirmed"] is False and bool(a["applicability"]["limitation"]),"forged installed equipment")
   require(a["visibility"]=={"extendedEnabled":True,"warningReadToEnd":True,"warningAcknowledged":True},"extended warning bypass")
   require(a["sourcePointer"] and bool(a["approachSummary"]),"source context missing")
   if a["sourceId"]=="manual1990":
    require(a["claimId"] in CLAIMS[sid] and a["sourcePointer"] in manual["verifiedLocators"],"unbound historical branch")
   else:
    require(a["sourcePointer"]==donor["sourcePointer"],"wrong donor source")
   graph(a["nodes"],a["startNodeId"],a["sourceId"])
 require(counts["SHORT"]==6 and counts["DETAILED"]==12,"unexpected authored question scope")
 return counts
def main():
 inventory=json.loads((ROOT/"docs/data-migration/diagnostic-corpus-analysis.json").read_text(encoding="utf-8"))
 require(inventory["uniqueScenarioCount"]==340 and inventory["preservedGraphNodes"]==3902 and inventory["donorCommit"]==DONOR,"baseline drift")
 result={sid:check(json.loads((ROOT/path).read_text(encoding="utf-8")),inventory) for sid,path in PATHS.items()}
 print("PASS Stage7 source-only research",result)
if __name__=="__main__": main()
