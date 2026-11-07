#!/usr/bin/env python3
"""Stage7 compressor source-first candidates: structural/provenance only; no operational approval."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DONOR="3176d6ee228f0ed4b78371f45209e10c1c724eff"
BASE="docs/data-migration/diagnostic-corpus-analysis.json"
MIG="content-packs/electric/vl80s/diagnostics/migration/diagnostics-source.candidate.json"
LEDGER="docs/diagnostics/STAGE7_COMPRESSOR_SOURCE_FIRST_2026-11-04.json"
EXPECTED={
 "compressor-pressure":("DiagnosticRepository.kt","5f57ff2c98f02a04692e8553700ec8d23077d166",3),
 "compressor-long-run":("DiagnosticExtendedCatalog.kt","090d448d0e9de20d002edf07361764e524298bf8",4),
 "compressor-no-start":("DiagnosticExpansion.kt","7a222f1eca7be9438d8a8dbad937235dec83b7ff",3),
}
def require(ok,why):
 if not ok:raise ValueError(why)
def graph(nodes,start,source_ids):
 by={n["id"]:n for n in nodes}
 require(len(by)==len(nodes) and start in by,"graph identity")
 for n in nodes:
  require(n["operationRequested"] is False and n["causeConfirmed"] is False and
          len(n["sourceRefs"])==1 and n["sourceRefs"][0] in source_ids,"unauthorized graph content")
  if n["type"]=="QUESTION":
   edges=n["responses"]
   require(set(edges)=={"YES","NO","UNKNOWN"} and edges["YES"]!=edges["NO"],"tri-state or branch failure")
   require(all(dest in by for dest in edges.values()) and by[edges["UNKNOWN"]]["type"]=="STOP","unsafe UNKNOWN")
  else:
   require(n["type"] in {"STOP","OBSERVATION_REPORT"} and n["responses"]=={},"terminal failure")
 seen={start};queue=[start]
 while queue:
  for dest in by[queue.pop()]["responses"].values():
   if dest not in seen:seen.add(dest);queue.append(dest)
 require(seen==set(by),"unreachable nodes")
 require(any(n["type"]=="STOP" for n in nodes),"STOP absent")
def check(d,inventory,migration):
 require(d["schemaVersion"]=="diagnostic-stage7-compressor-source-first/1" and d["stage"]=="7/51","stage mismatch")
 sid=d["originalId"];require(sid in EXPECTED and d["scenarioId"]=="vl80s.diag."+sid,"canonical identity")
 layer,blob,count=EXPECTED[sid]
 row=next((r for r in inventory["rows"] if r["scenarioId"]==d["scenarioId"]),None)
 original=next((s for s in migration["scenarios"] if s["id"]==sid),None)
 require(row and original and original["originLayer"]==layer and original["title"]==d["title"] and original["summary"]==d["summary"],"source migration mismatch")
 require(row["graph"]["nodeCount"]==count and row["variantIds"]==["vl80s-general"] and
         all(row[k]=="NOT_AUTHORED" for k in ("shortVersion","detailedVersion","shortExtendedBranch","detailedExtendedBranch")),"original corpus not preserved")
 require(d["donorPinnedSha"]==DONOR and d["donorOriginLayer"]==layer and d["donorOriginalBlobSha"]==blob and d["donorGraphNodeCount"]==count,"donor drift")
 require(d["authoringProfileId"]=="vl80s-general" and
         set(d["mustRemainDistinctFrom"])=={
          "vl80s.diag."+x for x in (
           ["compressor-long-run","compressor-no-start","main-reservoir-leak"] if sid=="compressor-pressure" else
           ["compressor-pressure","compressor-no-start","feed-line-leak"] if sid=="compressor-long-run" else
           ["compressor-pressure","compressor-long-run","control-voltage-low"])},
         "variant or fault conflation")
 require((d["donorOriginalQuestions"]==[] and d["donorQuestionProvenance"]=="SEED_HAS_NO_EXPLICIT_QUESTIONS") if sid=="compressor-long-run" else
         (len(d["donorOriginalQuestions"])==3 and d["donorQuestionProvenance"]=="EXACT_PINNED_DONOR"),"donor questions")
 require(d["publicationStatus"]=="CANDIDATE" and d["runtimeImport"] is False and
         d["executable"] is False and d["actionAuthorityGranted"] is False and
         d["sourceAuthorityVerified"] is False and d["exactInstalledVariantConfirmed"] is False and
         d["substantiveSafetyReviewed"] is False,"unsafe candidate promotion")
 require(d["warningGate"]=={"default":"HIDDEN","extendedEnabled":True,"warningReadToEnd":True,
                            "warningAcknowledged":True,"warningGrantsActionAuthority":False},"warning bypass")
 require(d["safePolicy"]=={"observationOnly":True,"onlyPreviouslyRecorded":True,
                           "triState":["YES","NO","UNKNOWN"],"unknownMustStop":True,
                           "operationsAllowed":[],"unknownProfile":"BLOCKED"},"safety gate bypass")
 require(d["deviceQA"]=="DEFERRED_TO_POST_RELEASE_DEVICE_QA","device tests fabricated")
 sources=d["sourceRecords"]
 require(set(sources)=={"donor","manual1990","training"},"source records")
 donor=sources["donor"]
 require(donor["commit"]==DONOR and donor["blobSha"]==blob and donor["originalId"]==sid and
         donor["excerpt"]=={"category":original["category"],"title":original["title"],"summary":original["summary"]} and
         donor["currentOperatingAuthority"] is False and donor["proceduresImported"] is False,"donor misattribution")
 require(donor["sourcePointer"]==(
         'Seed("'+sid+'")' if sid=="compressor-long-run" else
         'expandedScenario(id = "'+sid+'")' if sid=="compressor-no-start" else
         'DiagnosticScenario(id = "'+sid+'")'),"wrong source location")
 manual=sources["manual1990"];training=sources["training"]
 require(manual["year"]==1990 and manual["isbn"]=="5-277-01048-3" and
         manual["url"]=="https://ru.djvu.online/file/wXVHhRmTUUuqq" and
         training["url"]=="https://lektsii.org/3-33450.html" and training["year"] is None and
         "АК-11БТЗ" in training["unresolvedDiscrepancy"] and "АК-11Б" in training["unresolvedDiscrepancy"],"historical/teaching identity")
 for source in (manual,training):
  require(source["sourceTextLocated"] is True and source["modernRevisionVerified"] is False and
          source["exactInstalledEquipmentVerified"] is False and source["currentOperatingAuthority"] is False and
          source["proceduresImported"] is False,"archive promoted")
 require(len(d["historicalEvidenceClaims"])==3 and
         {c["sourceId"] for c in d["historicalEvidenceClaims"]}=={"manual1990","training"},"evidence claim scope")
 for c in d["historicalEvidenceClaims"]:
  require(c["provesCurrentEquipment"] is False and c["provesFaultCause"] is False and
          c["authorizesAction"] is False and c["locator"] in sources[c["sourceId"]]["verifiedLocators"],"unverified claim promoted")
 versions=d["versions"];require(set(versions)=={"SHORT","DETAILED"},"missing versions")
 focuses=set();identities=set()
 for name,count,route_count in (("SHORT",6,2),("DETAILED",12,3)):
  version=versions[name]
  require(version["authoringStatus"]=="RESEARCH_DRAFT_BLOCKED" and
          version["independentTechnicalReview"]=="REQUIRED" and
          version["operatingInstructionsIncluded"] is False,"route approved without review")
  require(len(version["nodes"])==count and len(version["extendedRoutes"])==route_count,"route scope")
  graph(version["nodes"],version["startNodeId"],set(sources))
  for alt in version["extendedRoutes"]:
   require(alt["approachId"] not in identities and alt["approachFocus"] not in focuses,"duplicated approach")
   identities.add(alt["approachId"]);focuses.add(alt["approachFocus"])
   require(alt["version"]==name and alt["sourceId"] in sources and
           alt["sourcePointer"] and alt["approachSummary"] and
           alt["questionType"]=="ALREADY_RECORDED_FACT_ONLY","source route attribution")
   require(alt["publicationStatus"]=="CANDIDATE" and alt["actionDisposition"]=="INFORMATION_ONLY" and
           alt["executable"] is False and alt["actionAuthorityGranted"] is False and
           alt["operationalSteps"]==[] and alt["technicalClaimReview"]=="REQUIRES_EXPERT","archive action bypass")
   require(alt["applicability"]=={"profileId":"vl80s-general","exactEquipmentProfileConfirmed":False,"modernSchemeConfirmed":False},"variant gate")
   require(alt["visibility"]=={"default":"HIDDEN","extendedEnabled":True,"warningReadToEnd":True,
                               "warningAcknowledged":True,"warningGrantsActionAuthority":False},"extended gate")
   graph(alt["nodes"],alt["startNodeId"],set(sources))
  require([a["sourceId"] for a in version["extendedRoutes"]]==
          (["donor","manual1990"] if name=="SHORT" else ["donor","manual1990","training"]),"source approach mix")
 require(versions["SHORT"]["nodes"]!=versions["DETAILED"]["nodes"],"versions cloned")
 return sid
def main():
 ledger=json.loads((ROOT/LEDGER).read_text(encoding="utf-8"))
 inventory=json.loads((ROOT/BASE).read_text(encoding="utf-8"))
 migration=json.loads((ROOT/MIG).read_text(encoding="utf-8"))["sourceObject"]
 require(inventory["donorCommit"]==DONOR and inventory["uniqueScenarioCount"]==340 and inventory["preservedGraphNodes"]==3902,"baseline drift")
 require(ledger["schemaVersion"]=="stage7-compressor-substage/1" and ledger["stage7CurrentResearchCount"]==5 and
         ledger["stage7OriginalTarget"]==8 and ledger["stage7RemainingForTarget"]==3 and
         ledger["runtimeImport"] is False and ledger["actionAuthorityGranted"] is False and
         ledger["publicationStatus"]=="CANDIDATE" and ledger["deviceQA"]=="DEFERRED_TO_POST_RELEASE_DEVICE_QA","stage progress or publication")
 ids=[]
 for sid in EXPECTED:
  d=json.loads((ROOT/f"content-packs/electric/vl80s/diagnostics/authoring/stage7-{sid}.research.json").read_text(encoding="utf-8"))
  ids.append(check(d,inventory,migration))
 require(set(ledger["addedStage7Ids"])=={"vl80s.diag."+x for x in ids},"ledger mismatch")
 print("PASS Stage7 compressor research",ids)
if __name__=="__main__":main()
