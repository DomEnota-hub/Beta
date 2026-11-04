#!/usr/bin/env python3
"""Validate non-operational Stage 6 contrasting routes. Content approval is separate."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PATHS={
"vl80s.diag.gv-no-open":"content-packs/electric/vl80s/diagnostics/authoring/stage6-gv-no-open.research.json",
"vl80s.diag.ekg-slow-transition":"content-packs/electric/vl80s/diagnostics/authoring/stage6-ekg-slow-transition.research.json",
}
def require(ok,msg):
 if not ok:raise ValueError(msg)
def graph(nodes,start):
 by={n["id"]:n for n in nodes}
 require(len(by)==len(nodes) and start in by,"duplicate/invalid start")
 for n in nodes:
  require(n["sourceRefs"]==["donorSeed"] and n["operationRequested"] is False,"unattributed operation")
  if n["type"]=="QUESTION":
   r=n["responses"]
   require(set(r)=={"YES","NO","UNKNOWN"} and r["YES"]!=r["NO"],"not tri-state")
   require(all(k in by for k in r.values()) and by[r["UNKNOWN"]]["type"]=="STOP","bad edges/UNKNOWN")
  else:
   require(n["type"] in {"STOP","OBSERVATION_REPORT"} and n["responses"]=={}
           and n["causeConfirmed"] is False,"false confirmed fault")
 seen={start};todo=[start]
 while todo:
  for dst in by[todo.pop()]["responses"].values():
   if dst not in seen:
    seen.add(dst);todo.append(dst)
 require(len(seen)==len(nodes),"unreachable nodes")
def check(d,inventory):
 require(d["schemaVersion"]=="diagnostic-stage6-contrasting-research/1"
         and d["stage"]=="6/51"
         and d["donorPinnedSha"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff"
         and d["donorBlobSha"]=="090d448d0e9de20d002edf07361764e524298bf8"
         and d["donorLayer"]=="DiagnosticExtendedCatalog.kt","donor drift")
 require(d["scenarioId"] in PATHS and d["originalId"]==d["scenarioId"].split("vl80s.diag.")[1],"identity drift")
 require(d["authoringProfileId"]=="vl80s-general"
         and d["sourceAuthorityVerified"] is False
         and d["exactInstalledVariantConfirmed"] is False
         and d["technicalClaimsReviewed"] is False
         and d["substantiveSafetyReviewed"] is False,"forged technical clearance")
 require(d["publicationStatus"]=="CANDIDATE" and d["runtimeImport"] is False
         and d["actionAuthorityGranted"] is False and d["executable"] is False
         and d["observationOnly"] is True and d["contrastIsDistinctCanonicalScenario"] is True,
         "unreviewed draft published")
 require(d["warningGate"]=={"default":"HIDDEN","extendedEnabled":True,
         "warningReadToEnd":True,"warningAcknowledged":True,"warningGrantsActionAuthority":False},
         "warning bypass")
 source=d["sourceRecords"]["donorSeed"]
 require(source["sourcePointer"]=='Seed("'+d["originalId"]+'")'
         and source["blobSha"]==d["donorBlobSha"]
         and source["currentActionAuthorityVerified"] is False
         and source["exactInstalledEquipmentVerified"] is False
         and source["operationalProcedureImported"] is False
         and source["excerptFields"]["summary"]==d["reportedSummary"]
         and source["excerptFields"]["danger"]==d["reportedDanger"],"source misrepresented")
 row=next((x for x in inventory["rows"] if x["scenarioId"]==d["scenarioId"]),None)
 require(row and row["sourceScenarioId"]==d["originalId"]
         and row["variantIds"]==["vl80s-general"]
         and all(row[k]=="NOT_AUTHORED" for k in
         ("shortVersion","detailedVersion","shortExtendedBranch","detailedExtendedBranch")),
         "canonical corpus was rewritten")
 require(set(d["versions"])=={"SHORT","DETAILED"},"missing version")
 approaches=set();focus=set();counts={}
 for kind in ("SHORT","DETAILED"):
  route=d["versions"][kind]
  require(route["authoringStatus"]=="RESEARCH_DRAFT_BLOCKED" and
          route["independentTechnicalReview"]=="REQUIRED" and
          route["operatingInstructionsIncluded"] is False,"route prematurely accepted")
  graph(route["nodes"],route["startNodeId"])
  counts[kind]=len(route["nodes"])
  require(len(route["extendedRoutes"])==(2 if kind=="SHORT" else 3),"missing variation")
  for alt in route["extendedRoutes"]:
   require(alt["sourceId"]=="donorSeed"
           and alt["sourcePointer"]=='Seed("'+d["originalId"]+'")'
           and alt["origin"]=="PINNED_DONOR_OFFLINE_REFERENCE","source gap")
   require(alt["approachId"] not in approaches and alt["approachFocus"] not in focus,
           "duplicate method")
   approaches.add(alt["approachId"]);focus.add(alt["approachFocus"])
   require(alt["publicationStatus"]=="CANDIDATE"
           and alt["actionDisposition"]=="INFORMATION_ONLY" and alt["executable"] is False
           and alt["actionAuthorityGranted"] is False and alt["operationalSteps"]==[]
           and alt["technicalClaimReview"]=="REQUIRES_EXPERT","historical operation")
   require(alt["applicability"]["profileId"]=="vl80s-general"
           and alt["applicability"]["exactEquipmentProfileConfirmed"] is False
           and bool(alt["applicability"]["limitation"]),"incorrect machine profile")
   require(alt["visibility"]=={"extendedEnabled":True,"warningReadToEnd":True,
           "warningAcknowledged":True},"warning bypass")
   graph(alt["nodes"],alt["startNodeId"])
 require(counts["SHORT"]<counts["DETAILED"],"versions are not distinct")
 return counts
if __name__=="__main__":
 inv=json.loads((ROOT/"docs/data-migration/diagnostic-corpus-analysis.json").read_text(encoding="utf-8"))
 require(inv["uniqueScenarioCount"]==340 and inv["preservedGraphNodes"]==3902
         and inv["donorCommit"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff","corpus changed")
 print("PASS stage6 nonoperational research:",{id:check(json.loads((ROOT/path).read_text(encoding="utf-8")),inv) for id,path in PATHS.items()})
