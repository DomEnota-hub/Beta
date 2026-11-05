#!/usr/bin/env python3
"""Stage11 traction source-first: structural, provenance and negative mutation QA."""
import copy,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
d=json.loads((root/"docs/diagnostics/STAGE11_TRACTION_BATCH2_2026-11-05.json").read_text(encoding="utf-8"))
migration=json.loads((root/"content-packs/electric/vl80s/diagnostics/migration/diagnostics-source.candidate.json").read_text(encoding="utf-8"))
original={s["id"]:s for s in migration["sourceObject"]["scenarios"]}
ids=["ekg-position-mismatch","traction-one-section-low","traction-motor-overheat","traction-motor-flashover"]
def check(c):
 id=c["originalId"];assert id in ids
 assert c["title"]==original[id]["title"] and c["category"]==original[id]["category"]=="Тяга"
 assert c["scenarioId"]=="vl80s.diag."+id
 assert c["donorPinnedSha"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff"
 assert c["variantEvidence"]["disposition"]=="BLOCKED" and "UNKNOWN" in c["variantEvidence"]["unverifiedInstalledVariant"]
 assert c["donorOriginLayer"]=="GENERATED_SEED"
 assert c["exactInstalledVariant"]=="UNKNOWN" and c["unknownVariantDisposition"]=="BLOCKED"
 assert c["publicationStatus"]=="CANDIDATE" and c["deviceQA"]=="NOT_RUN_DEFERRED"
 assert all(c[k] is False for k in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified"))
 src=c["sourceRecords"];assert set(src)=={"donor","manual1990","textbook2006"}
 assert src["donor"]["blobSha"]=="090d448d0e9de20d002edf07361764e524298bf8"
 assert src["donor"]["sourcePointer"]=='Seed("'+id+'"'
 assert src["donor"]["seedLiteral"].startswith('Seed("'+id+'", "Тяга", "'+c["title"]+'"')
 assert c["donorOriginalQuestions"]==src["donor"]["originalQuestions"] and len(c["donorOriginalQuestions"])==3
 assert c["summary"]==original[id]["summary"]
 assert all(s not in c["title"].lower() for s in ("перемычк","обход защит"))
 assert all(x["currentOperatingAuthority"] is False and x["proceduresImported"] is False for x in src.values())
 for key in ("manual1990","textbook2006"):
  assert len(src[key]["verifiedLocators"])==2
  assert src[key]["modernRevisionVerified"] is False and src[key]["exactInstalledEquipmentVerified"] is False
 assert len(c["historicalEvidenceClaims"])==4
 for claim in c["historicalEvidenceClaims"]:
  assert claim["locator"] in src[claim["sourceId"]]["verifiedLocators"]
  assert claim["authorizesAction"] is False and claim["provesFaultCause"] is False
 assert c["extendedWarning"]=={"default":"HIDDEN","requiresReadToEnd":True,"requiresAcknowledgement":True,"consentResetsOnClose":True,"warningGrantsActionAuthority":False}
 safe=c["safety"]
 assert safe["observationOnly"] and safe["onlyPreviouslyRecorded"] and safe["unknownMustStop"]
 assert safe["triState"]==["YES","NO","UNKNOWN"] and safe["operationsAllowed"]==[]
 assert all(safe[k]=="NOT_APPROVED" for k in ("roleGate","sourceGate","safetyGate"))
 assert {"JUMPER","PROTECTION_BYPASS","HV_INTERVENTION","TEST_RESTART","LIVE_MEASUREMENT"}<=set(safe["prohibited"])
 for mode,n in (("SHORT",6),("DETAILED",12)):
  g=c["versions"][mode];nodes=g["nodes"];assert len(nodes)==n
  by={x["id"]:x for x in nodes};assert len(by)==n and g["startNodeId"]=="q1"
  seen=set();pending=["q1"]
  while pending:
   key=pending.pop();assert key in by
   if key in seen:continue
   seen.add(key);node=by[key]
   assert node["recordedOnly"] is True and node["operationRequested"] is False and node["causeConfirmed"] is False
   assert set(node["sourceRefs"])=={"donor","manual1990","textbook2006"}
   if node["type"]=="QUESTION":
    assert node["text"].startswith("По ранее записанным сведениям:")
    assert set(node["responses"])=={"YES","NO","UNKNOWN"}
    assert node["responses"]["UNKNOWN"]=="stop_unknown"
    pending.extend(node["responses"].values())
   else:assert node["type"] in ("STOP","OBSERVATION_REPORT") and not node["responses"]
  assert len(seen)==n
  assert sum(x["type"]=="QUESTION" for x in nodes)==(2 if mode=="SHORT" else 8)
  assert by["q1"]["responses"]["YES"]=="stop_danger"
  assert by["q2"]["responses"]["YES"] in ("report","q3")
  assert by["stop_unknown"]["type"]==by["stop_danger"]["type"]==by["stop_unresolved"]["type"]=="STOP"
  assert by["report"]["type"]=="OBSERVATION_REPORT" and "НЕ" in by["report"]["text"]
 ext=c["informationExtensions"];assert len(ext)==5 and len({x["id"] for x in ext})==5
 assert [x["version"] for x in ext]==["SHORT","SHORT","DETAILED","DETAILED","DETAILED"]
 assert len({x["text"] for x in ext})==5
 assert all(x["kind"]=="HISTORICAL_INFORMATION_ONLY" for x in ext)
 for x in ext:
  assert x["warningRequired"] is True and x["actionAuthorityGranted"] is False
  assert len(x["sourceRefs"])==1 and x["locator"] in src[x["sourceRefs"][0]]["verifiedLocators"]
assert [c["originalId"] for c in d["candidates"]]==ids
assert len(set(x["canonicalBoundary"] for x in d["candidates"]))==4
assert len(set(x["versions"]["DETAILED"]["nodes"][1]["text"] for x in d["candidates"]))==4
assert d["ledger"]["runtimeImport"] is False and d["ledger"]["actionAuthorityGranted"] is False
assert d["ledger"]["scenarioIds"]==[c["scenarioId"] for c in d["candidates"]]
mutations=0
for c in d["candidates"]:
 check(c)
 for key,val in (("publicationStatus","ACTIVE"),("runtimeImport",True),("executable",True),("actionAuthorityGranted",True),("sourceAuthorityVerified",True),("exactInstalledVariant","ASSUMED"),("unknownVariantDisposition","ALLOW"),("donorPinnedSha","BAD"),("donorOriginLayer","BAD")):
  x=copy.deepcopy(c);x[key]=val
  try:check(x)
  except AssertionError:mutations+=1
  else:raise AssertionError((c["originalId"],key))
 for key,val in (("requiresReadToEnd",False),("requiresAcknowledgement",False),("consentResetsOnClose",False),("warningGrantsActionAuthority",True)):
  x=copy.deepcopy(c);x["extendedWarning"][key]=val
  try:check(x)
  except AssertionError:mutations+=1
  else:raise AssertionError((c["originalId"],key))
 for key,val in (("roleGate","APPROVED"),("sourceGate","APPROVED"),("safetyGate","APPROVED"),("operationsAllowed",["TEST_RESTART"]),("unknownMustStop",False)):
  x=copy.deepcopy(c);x["safety"][key]=val
  try:check(x)
  except AssertionError:mutations+=1
  else:raise AssertionError((c["originalId"],key))
 for mode in ("SHORT","DETAILED"):
  for kind in ("unknown","operation","source","cause"):
   x=copy.deepcopy(c);node=x["versions"][mode]["nodes"][0]
   if kind=="unknown":node["responses"]["UNKNOWN"]="report"
   if kind=="operation":node["operationRequested"]=True
   if kind=="source":node["sourceRefs"]=[]
   if kind=="cause":node["causeConfirmed"]=True
   try:check(x)
   except AssertionError:mutations+=1
   else:raise AssertionError((c["originalId"],mode,kind))
 for key,val in (("warningRequired",False),("actionAuthorityGranted",True),("locator","BAD")):
  x=copy.deepcopy(c);x["informationExtensions"][0][key]=val
  try:check(x)
  except AssertionError:mutations+=1
  else:raise AssertionError((c["originalId"],key))
 for key in ("blobSha","sourcePointer","seedLiteral"):
  x=copy.deepcopy(c);x["sourceRecords"]["donor"][key]="BAD"
  try:check(x)
  except AssertionError:mutations+=1
  else:raise AssertionError((c["originalId"],key))
assert mutations==128,mutations
print("STAGE11_TRACTION_BATCH2_PASS",len(d["candidates"]),"NEGATIVE_MUTATIONS",mutations)
