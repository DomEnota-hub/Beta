#!/usr/bin/env python3
"""Batch73 pinned CHME3E source/profile/safety/graph and negative mutation QA."""
import argparse,copy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
BASE="content-packs/diesel/chme3-family/diagnostics/"
PACKS={3:json.loads((R/(BASE+"recommended/diagnostics-03.pack.json")).read_text()),4:json.loads((R/(BASE+"recommended/diagnostics-04.pack.json")).read_text())}
FILES=["content-packs/diesel/chme3-family/diagnostics/authoring/chme3e-diag-003-dtg-dng-feedback-discrepancy.research.json","content-packs/diesel/chme3-family/diagnostics/authoring/chme3e-diag-004-gc40p-regulator.research.json","content-packs/diesel/chme3-family/diagnostics/authoring/chme3e-diag-005-field-weakening-absent.research.json","content-packs/diesel/chme3-family/diagnostics/authoring/chme3e-diag-006-field-weakening-wrong-stage.research.json","content-packs/diesel/chme3-family/diagnostics/authoring/chme3e-diag-007-oil-priming-no-cranking.research.json"]
PIN="e6ac2baebda3a9f545a5ff1612b0b24d3c58be6e"
EXPECTED={"3":{"evidenceRefs":["CHME3E-SRC-NOTIK-FIELD-WEAKENING-96","CHME3E-SRC-NOTIK-CH17"],"schemeRefs":["CHME3E-SCH-TRACTION-CONTROL"],"profileId":"chme3e-electronic","pack":3},"4":{"evidenceRefs":["CHME3E-SRC-NOTIK-EQUIPMENT-67","CHME3E-SRC-NOTIK-ONE-PERSON-99"],"schemeRefs":["CHME3E-SCH-TRACTION-CONTROL","CHME3E-SCH-REMOTE-CONTROL"],"profileId":"chme3e-electronic","pack":3},"5":{"evidenceRefs":["CHME3E-SRC-NOTIK-FIELD-WEAKENING-96"],"schemeRefs":["CHME3E-SCH-FIELD-WEAKENING"],"profileId":"chme3e-electronic","pack":4},"6":{"evidenceRefs":["CHME3E-SRC-NOTIK-FIELD-WEAKENING-96"],"schemeRefs":["CHME3E-SCH-FIELD-WEAKENING"],"profileId":"chme3e-electronic","pack":4},"7":{"evidenceRefs":["CHME3E-SRC-NOTIK-EQUIPMENT-67","CHME3E-SRC-NOTIK-CH17"],"schemeRefs":["CHME3E-SCH-START-ELECTRONIC"],"profileId":"chme3e-electronic","pack":4}}
def verify(c,entry,num):
 d=c["donor"]; a=c["applicability"]
 assert c["schemaVersion"]=="diagnostic-research-candidate/1" and c["batch"]==73
 assert c["originalId"]==entry["sourceObject"]["object"]["id"]==f"CHME3E-DIAG-{num:03d}"
 assert c["title"]==entry["title"]==entry["sourceObject"]["object"]["title"]
 assert c["scenarioId"]==d["canonicalId"]==entry["id"]
 assert d["commit"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff" and d["documentBlob"]==PIN
 assert d["documentPointer"]==f"/scenarios/{num-1}" and d["documentPath"].endswith("/chme3e/diagnostics_stage3.json")
 assert d["riskClass"]==entry["sourceObject"]["object"]["severity"]
 assert d["equipmentIds"]==entry["sourceObject"]["object"]["equipmentRefs"]
 assert d["evidenceRefs"]==EXPECTED[str(num)]["evidenceRefs"] and d["schemeRefs"]==EXPECTED[str(num)]["schemeRefs"] and a["profileId"]==EXPECTED[str(num)]["profileId"] and d["canonicalPack"].endswith(f"diagnostics-0{EXPECTED[str(num)]['pack']}.pack.json")
 assert d["gzipBlob"]==entry["sourceObject"]["sourceBlobSha"] and not d["gzipIndependentlyDecoded"]
 assert a["possibleVariants"]==entry["applicability"]["variantIds"]==["chme3e"]
 assert a["confirmedVariant"] is None and not a["installedSchemeVerified"] and a["unknownProfile"]=="BLOCKED"
 assert c["publicationStatus"]=="CANDIDATE" and c["actionDisposition"]=="TRIAGE_ONLY_NO_REPAIR"
 assert all(c[k] is False for k in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified","humanSafetyReviewPassed"))
 assert all(v is False for v in c["safety"].values()) and len(c["safety"])>=16
 w=c["warning"]
 assert w==dict(extendedHiddenByDefault=True,readToEndRequired=True,separateAcknowledgmentRequired=True,grantsActionAuthority=False)
 assert c["deviceQA"]["status"]=="NOT_RUN_DEFERRED"
 assert {s["id"] for s in c["sources"]}=={"DOC","PACK","HISTORICAL","FIELD","CURRENT_GAP"}
 assert all(not s["currentVerified"] and not s["installedProfileVerified"] for s in c["sources"])
 assert all(s["authority"] in ("INFORMATION_ONLY","HYPOTHESIS_ONLY") for s in c["sources"])
 assert len(c["sourceDiscrepancies"])>=6 and len(c["openGaps"])>=7 and len(c["crossScenarioBoundaries"])>=2
 for mode,n in (("SHORT",8),("DETAILED",12)):
  g=c["versions"][mode];nodes=g["nodes"];ids=[x["id"] for x in nodes]
  assert len(nodes)==n and len(ids)==len(set(ids)) and g["startNodeId"] in ids
  lookup={x["id"]:x for x in nodes};reach=set();todo=[g["startNodeId"]]
  while todo:
   key=todo.pop()
   assert key in lookup
   if key in reach:continue
   reach.add(key);node=lookup[key]
   assert node["permittedAction"] is False and node["sourceRefs"]
   if node["type"]=="QUESTION":
    rs=node["responses"];assert set(rs)=={"YES","NO","UNKNOWN"}
    assert lookup[rs["UNKNOWN"]]["type"]=="STOP"
    todo.extend(rs.values())
   else:
    assert node["type"] in ("STOP","OBSERVATION_REPORT") and not node["responses"] and node["causeConfirmed"] is False
  assert reach==set(ids)
  assert lookup[g["startNodeId"]]["responses"]["NO"]==lookup[g["startNodeId"]]["responses"]["UNKNOWN"]=="stop-safety"
  assert c["branchContracts"][mode]=={x["id"]:x["responses"] for x in nodes if x["type"]=="QUESTION"}
 assert len(c["extensions"])==5 and len({x["title"] for x in c["extensions"]})==5
 for e in c["extensions"]:
  assert e["displayMode"]=="EXTENDED_ONLY" and e["actionDisposition"]=="INFORMATION_ONLY" and not e["executable"] and not e["actionAuthorityGranted"] and not e["procedureSteps"]
  assert e["visibility"]==dict(hiddenByDefault=True,warningReadToEndRequired=True,warningAcknowledgedRequired=True)
  assert len(e["nodes"])==4 and [n["type"] for n in e["nodes"]]==["QUESTION","OBSERVATION_REPORT","OBSERVATION_REPORT","STOP"]
  assert set(e["nodes"][0]["responses"])=={"YES","NO","UNKNOWN"} and e["nodes"][0]["responses"]["UNKNOWN"]==e["nodes"][3]["id"]
  assert all(n["permittedAction"] is False for n in e["nodes"])
 return True
def main():
 p=argparse.ArgumentParser();p.add_argument("--negative",action="store_true");args=p.parse_args()
 total=0
 for num,path in enumerate(FILES,3):
  c=json.loads((R/path).read_text());entry=next(x for x in PACKS[EXPECTED[str(num)]["pack"]]["entries"] if x["sourceObject"]["object"]["id"]==f"CHME3E-DIAG-{num:03d}")
  verify(c,entry,num)
  if args.negative:
   mutations=[
    lambda x:x.update(runtimeImport=True),lambda x:x.update(executable=True),
    lambda x:x.update(publicationStatus="PUBLISHED"),lambda x:x.update(actionAuthorityGranted=True),
    lambda x:x.update(sourceAuthorityVerified=True),lambda x:x.update(humanSafetyReviewPassed=True),
    lambda x:x["applicability"].update(unknownProfile="ALLOW"),
    lambda x:x["applicability"].update(possibleVariants=["chme3","chme3e"]),
    lambda x:x["warning"].update(readToEndRequired=False),
    lambda x:x["warning"].update(grantsActionAuthority=True),
    lambda x:x["safety"].update(temporaryJumper=True),
    lambda x:x["sources"][2].update(currentVerified=True),
    lambda x:x["donor"].update(commit="WRONG"),
    lambda x:x["donor"].update(documentBlob="WRONG"),
    lambda x:x["donor"].update(gzipIndependentlyDecoded=True),
    lambda x:x["versions"]["SHORT"]["nodes"][0]["responses"].update(UNKNOWN="obs-a"),
    lambda x:x["versions"]["DETAILED"]["nodes"][1]["responses"].update(UNKNOWN="obs-a"),
    lambda x:x["versions"]["SHORT"]["nodes"][0].update(permittedAction=True),
    lambda x:x["versions"]["SHORT"]["nodes"][0]["responses"].update(YES="missing"),
    lambda x:x["extensions"][0]["visibility"].update(hiddenByDefault=False),
    lambda x:x["extensions"][0].update(executable=True),
    lambda x:x["extensions"][0]["nodes"][0]["responses"].update(UNKNOWN="e1-yes"),
    lambda x:x["deviceQA"].update(status="PASS"),
    lambda x:x["versions"]["DETAILED"]["nodes"].pop(),
    lambda x:x["extensions"].pop(),
    lambda x:x["sources"].pop(),
    lambda x:x["sourceDiscrepancies"].clear(),
    lambda x:x["openGaps"].clear(),
    lambda x:x["versions"]["SHORT"]["nodes"][3].update(causeConfirmed=True),
    lambda x:x["extensions"][0].update(procedureSteps=["unsafe"])
   ]
   for mutate in mutations:
    copyc=copy.deepcopy(c);mutate(copyc)
    try:verify(copyc,entry,num)
    except (AssertionError,KeyError,TypeError,IndexError):total+=1
    else:raise AssertionError("Mutation not detected "+str(num)+" "+str(mutate))
 print("CHME3E batch73 PASS:",len(FILES),"scenarios; 8/12 nodes; 5 extensions each; negative checks:",total)
if __name__=="__main__":main()
