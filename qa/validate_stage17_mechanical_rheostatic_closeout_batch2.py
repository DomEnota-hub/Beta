#!/usr/bin/env python3
"""Stage17 mechanical/rheostatic candidate provenance and negative safety gates."""
import copy, json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
P=json.loads((R/"docs/diagnostics/STAGE17_MECHANICAL_RHEOSTATIC_CLOSEOUT_BATCH2_2026-11-05.json").read_text(encoding="utf-8"))
M=json.loads((R/"content-packs/electric/vl80s/diagnostics/migration/diagnostics-source.candidate.json").read_text(encoding="utf-8"))
S={x["id"]:x for x in M["sourceObject"]["scenarios"]}
IDS=["ext-coupler-damage","rheostatic-brake","rheostatic-resistor-overheat","rheostatic-rpt-trip"]
assert P["ledger"]["baseHead"]=="54447be4010adeab9c82983a31957899c9a0e49a"
assert P["ledger"]["donorPinnedSha"]==M["donorCommit"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff"
assert P["ledger"]["donorSnapshotBlobSha"]==M["sourceBlobSha"]
assert P["ledger"]["scenarioIds"]==["vl80s.diag."+x for x in IDS]
assert P["ledger"]["categorySourceCounts"]=={"Механическая часть":1,"Электрическое торможение":3}
assert {x["id"] for x in S.values() if x["category"] in ("Механическая часть","Электрическое торможение")}==set(IDS)
assert [x["originalId"] for x in P["candidates"]]==IDS
assert P["ledger"]["runtimeImport"] is False and P["ledger"]["negativeMutationCount"]==140
def check(c):
 s=S[c["originalId"]]
 assert c["scenarioId"]=="vl80s.diag."+s["id"]
 assert c["title"]==s["title"] and c["summary"]==s["summary"] and c["category"]==s["category"]
 assert c["donorOriginLayer"]==s["originLayer"] and c["donorQuestionCount"]==s["questionCount"]
 assert c["donorPinnedSha"]==M["donorCommit"]
 assert c["donorOriginalQuestions"] is None and c["originalQuestionTextVerified"] is False
 assert c["authoringProfileId"]=="vl80s-general" and c["exactInstalledVariant"]=="UNKNOWN"
 assert c["unknownVariantDisposition"]=="BLOCKED" and c["variantEvidence"]["disposition"]=="BLOCKED"
 assert len(c["canonicalBoundary"])>110 and len(c["sourceDiscrepancy"])>120
 assert c["publicationStatus"]=="CANDIDATE" and c["deviceQA"]=="NOT_RUN_DEFERRED"
 assert all(c[k] is False for k in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified"))
 rec=c["sourceRecords"]
 assert set(rec)=={"donor","manual1990","textbook2006","currentRequirements"}
 assert rec["donor"]["commit"]==M["donorCommit"] and rec["donor"]["blobSha"]==M["sourceBlobSha"]
 assert rec["donor"]["sourceMetadataSha"]==P["ledger"]["migrationBlobSha"]
 assert rec["donor"]["sourcePointer"]=="sourceObject.scenarios[id="+s["id"]+"]"
 assert rec["donor"]["sourceOriginLayer"]==s["originLayer"]
 assert rec["donor"]["sourceProfileIds"]==s["applicableVariantIds"]==["vl80s-general"]
 assert rec["donor"]["originalQuestionCount"]==s["questionCount"]
 assert rec["donor"]["originalQuestionTextVerified"] is False and rec["donor"]["proceduresImported"] is False
 assert rec["manual1990"]["year"]==1990 and len(rec["manual1990"]["verifiedLocators"])==4
 assert rec["manual1990"]["currentOperatingAuthority"] is False and rec["manual1990"]["proceduresImported"] is False
 assert rec["textbook2006"]["verifiedLocators"]==[] and rec["textbook2006"]["relevance"]=="NOT_VERIFIED_FOR_THIS_SPECIFIC_SYMPTOM"
 assert rec["currentRequirements"]["status"]=="UNKNOWN" and rec["currentRequirements"]["actionAuthorityGranted"] is False
 assert c["extendedWarning"]=={"default":"HIDDEN","requiresReadToEnd":True,"requiresAcknowledgement":True,"consentResetsOnClose":True,"warningGrantsActionAuthority":False}
 saf=c["safety"]
 assert saf["observationOnly"] and saf["onlyPreviouslyRecorded"] and saf["unknownMustStop"]
 assert saf["triState"]==["YES","NO","UNKNOWN"] and saf["operationsAllowed"]==[]
 assert {"JUMPER","PROTECTION_BYPASS","HV_INTERVENTION","REPAIR","BRAKE_RETRY","PROTECTION_RESET","UNCOUPLING","RESISTOR_ACCESS"}<=set(saf["prohibited"])
 assert all(saf[k]=="NOT_APPROVED" for k in ("roleGate","sourceGate","safetyGate"))
 for mode,n,q in (("SHORT",6,2),("DETAILED",12,8)):
  g=c["versions"][mode]; nodes={x["id"]:x for x in g["nodes"]}
  assert len(nodes)==len(g["nodes"])==n and g["startNodeId"]=="q1"
  assert sum(x["type"]=="QUESTION" for x in nodes.values())==q
  seen=set(); stack=["q1"]
  while stack:
   k=stack.pop()
   assert k in nodes
   if k in seen: continue
   seen.add(k); x=nodes[k]
   assert x["recordedOnly"] is True and x["operationRequested"] is False and x["causeConfirmed"] is False
   assert set(x["sourceRefs"])=={"donor","manual1990"}
   if x["type"]=="QUESTION":
    assert x["text"].startswith("По ранее записанным сведениям:")
    assert set(x["responses"])=={"YES","NO","UNKNOWN"} and x["responses"]["UNKNOWN"]=="stop_unknown"
    stack.extend(x["responses"].values())
   else: assert x["type"] in ("STOP","OBSERVATION_REPORT") and x["responses"]=={}
  assert len(seen)==n
  assert nodes["q1"]["responses"]["YES"]=="stop_danger"
  assert all(nodes[k]["type"]=="STOP" for k in ("stop_danger","stop_unknown","stop_unresolved"))
  assert nodes["report"]["type"]=="OBSERVATION_REPORT" and "НЕ" in nodes["report"]["text"]
 ex=c["informationExtensions"]
 assert len(ex)==len({x["id"] for x in ex})==len({x["text"] for x in ex})==5
 assert [x["version"] for x in ex]==["SHORT","SHORT","DETAILED","DETAILED","DETAILED"]
 for x in ex:
  assert x["kind"]=="HISTORICAL_INFORMATION_ONLY" and x["sourceRefs"]==["manual1990"]
  assert x["locator"] in rec["manual1990"]["verifiedLocators"]
  assert x["warningRequired"] is True and x["actionAuthorityGranted"] is False
 assert len(c["historicalEvidenceClaims"])==3
 assert all(x["proceduresImported"] is False for x in c["historicalEvidenceClaims"])
for c in P["candidates"]:check(c)
def must_fail(c):
 try:check(c)
 except (AssertionError,KeyError,TypeError,ValueError):return
 raise AssertionError("Unsafe mutation accepted: "+c["originalId"])
count=0
for c in P["candidates"]:
 for mode in ("SHORT","DETAILED"):
  for i in range(len(c["versions"][mode]["nodes"])):
   x=copy.deepcopy(c);x["versions"][mode]["nodes"][i]["operationRequested"]=True;must_fail(x);count+=1
 for i in range(5):
  x=copy.deepcopy(c);x["informationExtensions"][i]["actionAuthorityGranted"]=True;must_fail(x);count+=1
  x=copy.deepcopy(c);x["informationExtensions"][i]["warningRequired"]=False;must_fail(x);count+=1
 for k in ("runtimeImport","executable","actionAuthorityGranted"):
  x=copy.deepcopy(c);x[k]=True;must_fail(x);count+=1
 for k in ("roleGate","sourceGate","safetyGate"):
  x=copy.deepcopy(c);x["safety"][k]="APPROVED";must_fail(x);count+=1
 x=copy.deepcopy(c);x["safety"]["unknownMustStop"]=False;must_fail(x);count+=1
assert count==140,count
print("Stage17 closeout PASS: 4/4 donor IDs, 72 nodes, 20 extensions, 140 negative mutations; UNKNOWN/BLOCKED")
