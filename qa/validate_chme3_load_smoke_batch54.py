#!/usr/bin/env python3
"""Batch54: pinned donor identity, graphs, source gates and negative tests."""
import argparse,copy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];B="content-packs/diesel/chme3-family/"
P={6:B+"diagnostics/authoring/chme3-diag-006-load-rpm-sag.research.json",7:B+"diagnostics/authoring/chme3-diag-007-black-exhaust.research.json"}
D="docs/locomotives/chme3/diagnostics_powerplant_pass3.json"
def read(p):return json.loads((R/p).read_text(encoding="utf-8"))
def graph(v,refs):
 n=v["nodes"];m={x["id"]:x for x in n};assert len(m)==len(n)
 todo=[v["startNodeId"]];seen=set()
 while todo:
  k=todo.pop()
  if k in seen:continue
  x=m[k];seen.add(k)
  assert x["type"] in {"QUESTION","OBSERVATION_REPORT","STOP"}
  assert x["permittedAction"] is False and x["sourceRefs"] and set(x["sourceRefs"])<=refs
  assert "procedureSteps" not in x
  if x["type"]=="QUESTION":
   assert set(x["responses"])=={"YES","NO","UNKNOWN"} and m[x["responses"]["UNKNOWN"]]["type"]=="STOP"
  else:assert x["responses"]=={} and x["causeConfirmed"] is False
  todo.extend(x["responses"].values())
 assert seen==set(m)
def check(c,num,idx,pack):
 sid=f"CHME3-DIAG-{num:03d}";d=c["donor"]
 doc=next(x for x in idx["documents"] if x["sourcePath"]==D);src=doc["sourceObject"]["scenarios"][num-1]
 mat=next(x for x in idx["matches"] if x["sourceId"]==sid)
 entry=next(x for x in pack["entries"] if x["id"]==mat["canonicalId"])
 assert c["schemaVersion"]=="diagnostic-research-candidate/1" and c["batch"]==54
 assert c["originalId"]==src["id"]==sid and c["title"]==src["title"]==entry["title"]
 assert c["scenarioId"]==d["canonicalId"]==mat["canonicalId"]==entry["id"]
 assert d["commit"]==idx["donorCommit"]=="3176d6ee228f0ed4b78371f45209e10c1c724eff"
 assert d["repository"]=="DomEnota-hub/Test-" and d["documentPath"]==D and d["documentPointer"]==mat["sourcePointer"]==f"/scenarios/{num-1}"
 assert d["documentBlob"]==doc["sourceBlobSha"]=="63988703bb795e82f40335a756b8b9bd3cad8e0a"
 assert d["gzipBlob"]==entry["sourceObject"]["sourceBlobSha"]=="6a6068ad1ea54cb964b65a10ecf5c2425b2276e8"
 assert d["gzipIndependentlyDecoded"] is False and d["relation"]=="ID_TITLE_PROFILE_ONLY_NOT_GRAPH_EQUIVALENCE"
 for k in ("riskClass","actionAuthority","evidenceStatus","evidenceRefs","equipmentIds"):assert d[k]==src[k]
 assert d["riskClass"]=="NORMAL_DIAGNOSTIC" and d["actionAuthority"]=="TRIAGE_ONLY_NO_REPAIR"
 assert src["profiles"]==["ЧМЭ3","ЧМЭ3Т","ЧМЭ3Э"]
 assert set(c["applicability"]["possibleVariants"])==set(entry["applicability"]["variantIds"])=={"chme3","chme3t","chme3e"}
 assert c["applicability"]["confirmedVariant"] is None and c["applicability"]["unknownProfile"]=="BLOCKED" and c["applicability"]["installedSchemeVerified"] is False
 assert c["publicationStatus"]==entry["publicationStatus"]=="CANDIDATE" and c["actionDisposition"]=="TRIAGE_ONLY_NO_REPAIR"
 for k in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified","humanSafetyReviewPassed"):assert c[k] is False
 assert c["warning"]=={"extendedHiddenByDefault":True,"readToEndRequired":True,"separateAcknowledgmentRequired":True,"grantsActionAuthority":False}
 assert all(x is False for x in c["safety"].values())
 refs={x["id"] for x in c["sources"]};assert len(refs)==len(c["sources"])==6
 assert all(x["currentVerified"] is False and x["installedProfileVerified"] is False and x["authority"]!="ACTION_AUTHORIZED" for x in c["sources"])
 assert next(x for x in c["sources"] if x["id"]=="FIELD")["authority"]=="HYPOTHESIS_ONLY"
 assert len(c["crossScenarioBoundaries"])== (6 if num==6 else 4) and len(c["openGaps"])>=7
 for key,n in (("SHORT",8),("DETAILED",12)):
  v=c["versions"][key];assert len(v["nodes"])==n
  graph(v,refs);assert v["nodes"][0]["responses"]["NO"]==v["nodes"][0]["responses"]["UNKNOWN"]=="stop-safety"
 assert len(c["extensions"])==5 and len({x["id"] for x in c["extensions"]})==5
 for x in c["extensions"]:
  assert x["sourceId"] in refs and x["displayMode"]=="EXTENDED_ONLY"
  assert x["visibility"]=={"hiddenByDefault":True,"warningReadToEndRequired":True,"warningAcknowledgedRequired":True}
  assert x["actionDisposition"]=="INFORMATION_ONLY" and x["executable"] is False and x["actionAuthorityGranted"] is False and x["procedureSteps"]==[]
  assert len(x["nodes"])==4;graph({"startNodeId":x["nodes"][0]["id"],"nodes":x["nodes"]},refs)
def neg(c,n,i,p):
 mutations=[lambda x:x.update(runtimeImport=True),lambda x:x.update(executable=True),lambda x:x.update(publicationStatus="PUBLISHED"),lambda x:x.update(actionAuthorityGranted=True),lambda x:x.update(sourceAuthorityVerified=True),lambda x:x.update(humanSafetyReviewPassed=True),lambda x:x["applicability"].update(confirmedVariant="chme3"),lambda x:x["applicability"].update(unknownProfile="ALLOW"),lambda x:x["applicability"].update(installedSchemeVerified=True),lambda x:x["donor"].update(commit="HEAD"),lambda x:x["donor"].update(documentPointer="/scenarios/0"),lambda x:x["donor"].update(gzipIndependentlyDecoded=True),lambda x:x["donor"].update(equipmentIds=[]),lambda x:x["donor"].update(evidenceRefs=[]),lambda x:x["warning"].update(extendedHiddenByDefault=False),lambda x:x["warning"].update(readToEndRequired=False),lambda x:x["warning"].update(separateAcknowledgmentRequired=False),lambda x:x["warning"].update(grantsActionAuthority=True),lambda x:x["safety"].update(underLoadTesting=True),lambda x:x["safety"].update(bypassProtection=True),lambda x:x["versions"]["SHORT"]["nodes"][0]["responses"].update(UNKNOWN="s2"),lambda x:x["versions"]["DETAILED"]["nodes"][0].update(permittedAction=True),lambda x:x["extensions"][0]["visibility"].update(warningAcknowledgedRequired=False),lambda x:x["extensions"][1].update(executable=True),lambda x:x["extensions"][2].update(procedureSteps=["unsafe"]),lambda x:x["sources"][-1].update(authority="ACTION_AUTHORIZED"),lambda x:x["crossScenarioBoundaries"].pop(),lambda x:x["sources"][-1].update(id="DOC")]
 for j,fn in enumerate(mutations):
  x=copy.deepcopy(c);fn(x)
  try:check(x,n,i,p)
  except (AssertionError,KeyError):continue
  raise AssertionError(f"unsafe mutation accepted {n}/{j}")
 return len(mutations)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--negative",action="store_true");a=ap.parse_args()
 i=read(B+"migration/diagnostic-source-index.json");p=read(B+"diagnostics/recommended/diagnostics-01.pack.json");total=0
 for n,f in P.items():
  c=read(f);check(c,n,i,p);total+=neg(c,n,i,p) if a.negative else 0
  print("CHME3_BATCH54_SCENARIO_PASS",n)
 print("CHME3_BATCH54_PASS",len(P),"NEGATIVE",total)
if __name__=="__main__":main()
