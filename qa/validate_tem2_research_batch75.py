#!/usr/bin/env python3
"""TEM2 batch75 pinned identity, profile, graph, safety, negative QA."""
import argparse,copy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
B="content-packs/diesel/tem2-family/diagnostics/"
L=json.loads((R/(B+"stage3-source-lineage.json")).read_text())
P=json.loads((R/(B+"recommended/diagnostics-01.pack.json")).read_text())
FILES=["content-packs/diesel/tem2-family/diagnostics/authoring/tem2-diag-001-no-crank.research.json","content-packs/diesel/tem2-family/diagnostics/authoring/tem2-diag-002-slow-crank-no-start.research.json","content-packs/diesel/tem2-family/diagnostics/authoring/tem2-diag-003-starts-then-stalls.research.json"]
def check(c,n):
 s=L["scenarios"][n-1]["sourceObject"];d=c["donor"];a=c["applicability"]
 assert c["batch"]==75 and c["schemaVersion"]=="diagnostic-research-candidate/1"
 assert c["originalId"]==s["id"]==f"TEM2-DIAG-{n:03d}" and c["title"]==s["title"]
 assert d["commit"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff" and d["documentBlob"]=="4234e401eb9d6ec03802669d0f74962cb23ea5c4"
 assert d["documentPointer"]==f"/scenarios/{n-1}" and not d["originalGraphEquivalenceVerified"]
 assert d["equipmentIds"]==s["equipmentIds"] and d["evidenceRefs"]==s["evidenceRefs"] and d["schemeRefs"]==s["schemeRefs"]
 assert d["riskClass"]==s["riskClass"] and d["actionAuthority"]==s["actionAuthority"]
 assert d["targetMap"]=={t["variantId"]:t["canonicalId"] for t in L["scenarios"][n-1]["targets"]}
 es=[e for e in P["entries"] if e["sourceObject"]["object"]["id"]==s["id"]]
 assert len(es)==(1 if n==1 else 2)
 assert d["sourceBlobShas"]=={e["id"]:e["sourceObject"]["sourceBlobSha"] for e in es}
 for t in L["scenarios"][n-1]["targets"]:
  assert any(e["id"]==t["canonicalId"] and t["variantId"] in e["applicability"]["variantIds"] for e in es)
 assert a["possibleVariants"]==["tem2","tem2u"] and a["profileIds"]==s["profileIds"]
 assert a["confirmedVariant"] is None and not a["installedSchemeVerified"] and a["unknownProfile"]=="BLOCKED"
 assert set(a["excludedVariants"])=={"tem2t","tem2um","tem2a","tem2um-1pd4a"}
 assert c["publicationStatus"]=="CANDIDATE" and c["actionDisposition"]=="TRIAGE_ONLY_NO_REPAIR"
 assert all(c[k] is False for k in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified","humanSafetyReviewPassed"))
 assert len(c["safety"])>=16 and all(v is False for v in c["safety"].values())
 assert c["warning"]==dict(extendedHiddenByDefault=True,readToEndRequired=True,separateAcknowledgmentRequired=True,grantsActionAuthority=False)
 assert c["deviceQA"]["status"]=="NOT_RUN_DEFERRED"
 assert {x["id"] for x in c["sources"]}=={"DOC","PACK","ARCHIVE","FACTORY_U","FIELD","CURRENT_GAP"}
 assert all(not x["currentVerified"] and not x["installedProfileVerified"] and x["authority"] in ("INFORMATION_ONLY","HYPOTHESIS_ONLY") for x in c["sources"])
 assert len(c["crossScenarioBoundaries"])>=3 and len(c["sourceDiscrepancies"])>=7 and len(c["openGaps"])>=8
 for mode,count in (("SHORT",8),("DETAILED",12)):
  g=c["versions"][mode];nodes=g["nodes"];m={x["id"]:x for x in nodes}
  assert len(nodes)==count and len(m)==count and g["startNodeId"] in m
  seen=set();todo=[g["startNodeId"]]
  while todo:
   k=todo.pop();assert k in m
   if k in seen:continue
   seen.add(k);x=m[k];assert not x["permittedAction"] and x["sourceRefs"]
   if x["type"]=="QUESTION":
    assert set(x["responses"])=={"YES","NO","UNKNOWN"} and m[x["responses"]["UNKNOWN"]]["type"]=="STOP"
    todo.extend(x["responses"].values())
   else:assert x["type"] in ("STOP","OBSERVATION_REPORT") and not x["responses"] and x["causeConfirmed"] is False
  assert seen==set(m)
  assert m[g["startNodeId"]]["responses"]["NO"]==m[g["startNodeId"]]["responses"]["UNKNOWN"]=="stop-safety"
  assert c["branchContracts"][mode]=={x["id"]:x["responses"] for x in nodes if x["type"]=="QUESTION"}
 assert len(c["extensions"])==5 and len({x["title"] for x in c["extensions"]})==5
 for e in c["extensions"]:
  assert e["displayMode"]=="EXTENDED_ONLY" and e["actionDisposition"]=="INFORMATION_ONLY"
  assert not e["executable"] and not e["actionAuthorityGranted"] and not e["procedureSteps"]
  assert e["visibility"]==dict(hiddenByDefault=True,warningReadToEndRequired=True,warningAcknowledgedRequired=True)
  x=e["nodes"];assert len(x)==4 and [v["type"] for v in x]==["QUESTION","OBSERVATION_REPORT","OBSERVATION_REPORT","STOP"]
  assert set(x[0]["responses"])=={"YES","NO","UNKNOWN"} and x[0]["responses"]["UNKNOWN"]==x[3]["id"]
  assert all(not v["permittedAction"] for v in x)
def main():
 p=argparse.ArgumentParser();p.add_argument("--negative",action="store_true");args=p.parse_args();checks=0
 for n,path in enumerate(FILES,1):
  c=json.loads((R/path).read_text());check(c,n)
  if args.negative:
   mutations=[
    lambda x:x.update(runtimeImport=True),lambda x:x.update(executable=True),lambda x:x.update(publicationStatus="PUBLISHED"),
    lambda x:x.update(actionAuthorityGranted=True),lambda x:x.update(sourceAuthorityVerified=True),lambda x:x.update(humanSafetyReviewPassed=True),
    lambda x:x["applicability"].update(unknownProfile="ALLOW"),lambda x:x["applicability"].update(confirmedVariant="tem2"),
    lambda x:x["warning"].update(readToEndRequired=False),lambda x:x["warning"].update(grantsActionAuthority=True),
    lambda x:x["safety"].update(temporaryJumper=True),lambda x:x["sources"][2].update(currentVerified=True),
    lambda x:x["donor"].update(commit="WRONG"),lambda x:x["donor"].update(documentBlob="WRONG"),
    lambda x:x["donor"].update(originalGraphEquivalenceVerified=True),lambda x:x["donor"].update(riskClass="WRONG"),
    lambda x:x["donor"]["targetMap"].update(tem2="WRONG"),lambda x:x["donor"]["sourceBlobShas"].clear(),
    lambda x:x["versions"]["SHORT"]["nodes"][0]["responses"].update(UNKNOWN="obs-a"),
    lambda x:x["versions"]["DETAILED"]["nodes"][1]["responses"].update(UNKNOWN="obs-a"),
    lambda x:x["versions"]["SHORT"]["nodes"][0].update(permittedAction=True),
    lambda x:x["versions"]["SHORT"]["nodes"][0]["responses"].update(YES="missing"),
    lambda x:x["extensions"][0]["visibility"].update(hiddenByDefault=False),
    lambda x:x["extensions"][0].update(executable=True),
    lambda x:x["extensions"][0]["nodes"][0]["responses"].update(UNKNOWN="e1-yes"),
    lambda x:x["deviceQA"].update(status="PASS"),lambda x:x["versions"]["DETAILED"]["nodes"].pop(),
    lambda x:x["extensions"].pop(),lambda x:x["sources"].pop(),
    lambda x:x["sourceDiscrepancies"].clear(),lambda x:x["openGaps"].clear(),
    lambda x:x["versions"]["SHORT"]["nodes"][3].update(causeConfirmed=True),
    lambda x:x["extensions"][0].update(procedureSteps=["unsafe"])
   ]
   for mut in mutations:
    z=copy.deepcopy(c);mut(z)
    try:check(z,n)
    except (AssertionError,KeyError,TypeError,IndexError):checks+=1
    else:raise AssertionError(f"Escaped mutation {n}")
 print(f"TEM2 batch75 PASS: 3 original scenarios, SHORT8 DETAILED12, 5 extensions each, negative checks {checks}")
if __name__=="__main__":main()
