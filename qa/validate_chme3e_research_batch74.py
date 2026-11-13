#!/usr/bin/env python3
"""Batch74 CHME3E 008-012 source, graph, safety and negative mutation QA."""
import argparse, copy, json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
BASE="content-packs/diesel/chme3-family/diagnostics/"
PACK=json.loads((R/(BASE+"recommended/diagnostics-04.pack.json")).read_text())
FILES=["content-packs/diesel/chme3-family/diagnostics/authoring/chme3e-diag-008-start-circuit-not-released.research.json","content-packs/diesel/chme3-family/diagnostics/authoring/chme3e-diag-009-generator-water-heating-no-warmup.research.json","content-packs/diesel/chme3-family/diagnostics/authoring/chme3e-diag-010-external-preheat-no-circulation.research.json","content-packs/diesel/chme3-family/diagnostics/authoring/chme3e-diag-011-portable-remote-command-missing.research.json","content-packs/diesel/chme3-family/diagnostics/authoring/chme3e-diag-012-electronic-speed-position-feedback-mismatch.research.json"]
PIN="e6ac2baebda3a9f545a5ff1612b0b24d3c58be6e"
EXPECTED={"8":{"evidenceRefs":["CHME3E-SRC-NOTIK-CH17"],"schemeRefs":["CHME3E-SCH-START-ELECTRONIC"],"riskClass":"EMERGENCY_ELECTRICAL","actionAuthority":"SAFETY_GATE_REQUIRED"},"9":{"evidenceRefs":["CHME3E-SRC-NOTIK-WATER-47","CHME3E-SRC-NOTIK-EQUIPMENT-67"],"schemeRefs":["CHME3E-SCH-PREHEAT-RUNNING"],"riskClass":"NORMAL_DIAGNOSTIC","actionAuthority":"TRIAGE_ONLY_NO_REPAIR"},"10":{"evidenceRefs":["CHME3E-SRC-NOTIK-WATER-47","CHME3E-SRC-NOTIK-EQUIPMENT-67"],"schemeRefs":["CHME3E-SCH-PREHEAT-EXTERNAL"],"riskClass":"HIGH_VOLTAGE_EXTERNAL_SUPPLY","actionAuthority":"SAFETY_GATE_REQUIRED"},"11":{"evidenceRefs":["CHME3E-SRC-NOTIK-ONE-PERSON-99","CHME3E-SRC-NOTIK-CH17"],"schemeRefs":["CHME3E-SCH-REMOTE-CONTROL"],"riskClass":"CONTROL_SYSTEM","actionAuthority":"TRIAGE_ONLY_NO_REPAIR"},"12":{"evidenceRefs":["CHME3E-SRC-NOTIK-EQUIPMENT-67","CHME3E-SRC-NOTIK-CH17"],"schemeRefs":["CHME3E-SCH-TRACTION-CONTROL"],"riskClass":"CONTROL_SYSTEM","actionAuthority":"TRIAGE_ONLY_NO_REPAIR"}}
def verify(c,e,num):
 o=e["sourceObject"]["object"];d=c["donor"];a=c["applicability"]
 assert c["schemaVersion"]=="diagnostic-research-candidate/1" and c["batch"]==74
 assert c["originalId"]==o["id"]==f"CHME3E-DIAG-{num:03d}"
 assert c["title"]==e["title"]==o["title"] and c["scenarioId"]==d["canonicalId"]==e["id"]
 assert d["commit"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff"
 assert d["documentBlob"]==PIN and d["documentPointer"]==f"/scenarios/{num-1}"
 assert d["documentPath"]=="docs/locomotives/diesel/chme3-family/chme3e/diagnostics_stage3.json"
 assert d["canonicalPack"]==BASE+"recommended/diagnostics-04.pack.json"
 assert d["gzipBlob"]==e["sourceObject"]["sourceBlobSha"] and not d["gzipIndependentlyDecoded"]
 assert d["riskClass"]==o["severity"]==EXPECTED[str(num)]["riskClass"]
 assert d["actionAuthority"]==EXPECTED[str(num)]["actionAuthority"]
 assert d["equipmentIds"]==o["equipmentRefs"] and d["evidenceRefs"]==EXPECTED[str(num)]["evidenceRefs"]
 assert d["schemeRefs"]==EXPECTED[str(num)]["schemeRefs"]
 assert a["possibleVariants"]==e["applicability"]["variantIds"]==["chme3e"]
 assert a["profileId"]=="chme3e-electronic" and a["confirmedVariant"] is None and not a["installedSchemeVerified"] and a["unknownProfile"]=="BLOCKED"
 assert c["publicationStatus"]=="CANDIDATE" and c["actionDisposition"]=="TRIAGE_ONLY_NO_REPAIR"
 assert all(c[k] is False for k in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified","humanSafetyReviewPassed"))
 assert len(c["safety"])>=16 and all(v is False for v in c["safety"].values())
 assert c["warning"]==dict(extendedHiddenByDefault=True,readToEndRequired=True,separateAcknowledgmentRequired=True,grantsActionAuthority=False)
 assert c["deviceQA"]["status"]=="NOT_RUN_DEFERRED"
 assert {s["id"] for s in c["sources"]}=={"DOC","PACK","HISTORICAL","FIELD","CURRENT_GAP"}
 assert all(not s["currentVerified"] and not s["installedProfileVerified"] and s["authority"] in ("INFORMATION_ONLY","HYPOTHESIS_ONLY") for s in c["sources"])
 assert len(c["sourceDiscrepancies"])>=7 and len(c["openGaps"])>=8 and len(c["crossScenarioBoundaries"])>=3
 for mode,sz in (("SHORT",8),("DETAILED",12)):
  g=c["versions"][mode];nodes=g["nodes"];ids=[n["id"] for n in nodes];m={n["id"]:n for n in nodes}
  assert len(nodes)==sz and len(ids)==len(m) and g["startNodeId"] in m
  seen=set();todo=[g["startNodeId"]]
  while todo:
   k=todo.pop()
   assert k in m
   if k in seen:continue
   seen.add(k);n=m[k]
   assert n["permittedAction"] is False and n["sourceRefs"]
   if n["type"]=="QUESTION":
    assert set(n["responses"])=={"YES","NO","UNKNOWN"} and m[n["responses"]["UNKNOWN"]]["type"]=="STOP"
    todo.extend(n["responses"].values())
   else:assert n["type"] in ("STOP","OBSERVATION_REPORT") and not n["responses"] and n["causeConfirmed"] is False
  assert seen==set(m)
  assert m[g["startNodeId"]]["responses"]["NO"]==m[g["startNodeId"]]["responses"]["UNKNOWN"]=="stop-safety"
  assert c["branchContracts"][mode]=={n["id"]:n["responses"] for n in nodes if n["type"]=="QUESTION"}
 assert len(c["extensions"])==5 and len({x["title"] for x in c["extensions"]})==5
 for ext in c["extensions"]:
  assert ext["displayMode"]=="EXTENDED_ONLY" and ext["actionDisposition"]=="INFORMATION_ONLY"
  assert not ext["executable"] and not ext["actionAuthorityGranted"] and not ext["procedureSteps"]
  assert ext["visibility"]==dict(hiddenByDefault=True,warningReadToEndRequired=True,warningAcknowledgedRequired=True)
  nodes=ext["nodes"];assert len(nodes)==4 and [n["type"] for n in nodes]==["QUESTION","OBSERVATION_REPORT","OBSERVATION_REPORT","STOP"]
  assert set(nodes[0]["responses"])=={"YES","NO","UNKNOWN"} and nodes[0]["responses"]["UNKNOWN"]==nodes[3]["id"]
  assert all(n["permittedAction"] is False for n in nodes)
 return True
def main():
 p=argparse.ArgumentParser();p.add_argument("--negative",action="store_true");args=p.parse_args();count=0
 for num,path in zip((8,9,10,11,12),FILES):
  c=json.loads((R/path).read_text());e=next(x for x in PACK["entries"] if x["sourceObject"]["object"]["id"]==f"CHME3E-DIAG-{num:03d}")
  verify(c,e,num)
  if args.negative:
   mutations=[
    lambda x:x.update(runtimeImport=True),lambda x:x.update(executable=True),lambda x:x.update(publicationStatus="PUBLISHED"),
    lambda x:x.update(actionAuthorityGranted=True),lambda x:x.update(sourceAuthorityVerified=True),lambda x:x.update(humanSafetyReviewPassed=True),
    lambda x:x["applicability"].update(unknownProfile="ALLOW"),lambda x:x["applicability"].update(possibleVariants=["chme3","chme3e"]),
    lambda x:x["warning"].update(readToEndRequired=False),lambda x:x["warning"].update(grantsActionAuthority=True),
    lambda x:x["safety"].update(temporaryJumper=True),lambda x:x["sources"][2].update(currentVerified=True),
    lambda x:x["donor"].update(commit="WRONG"),lambda x:x["donor"].update(documentBlob="WRONG"),
    lambda x:x["donor"].update(gzipIndependentlyDecoded=True),lambda x:x["donor"].update(riskClass="WRONG"),
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
   for mutation in mutations:
    z=copy.deepcopy(c);mutation(z)
    try:verify(z,e,num)
    except (AssertionError,KeyError,TypeError,IndexError):count+=1
    else:raise AssertionError(f"Mutation escaped {num}: {mutation}")
 print(f"CHME3E batch74 PASS: 5 scenarios, SHORT8 DETAILED12, 5 extensions each, negative checks {count}")
if __name__=="__main__":main()
