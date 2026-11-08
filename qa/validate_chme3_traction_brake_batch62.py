#!/usr/bin/env python3
"""CHME3 batch62: pinned provenance, graphs, fail-closed and negative mutations."""
import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "content-packs/diesel/chme3-family/"
DOC = "docs/locomotives/chme3/diagnostics_electrical_control_pass3.json"
REG = "docs/diagnostics/DIAGNOSTIC_FINAL_DEVICE_QA_DEFERRED_2026-11-04.md"
FILES = {
  109: BASE + "diagnostics/authoring/chme3-diag-109-diesel-running-no-traction.research.json",
  110: BASE + "diagnostics/authoring/chme3-diag-110-chme3t-rheostatic-brake-failure.research.json",
}
def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))
def graph(g, count, refs):
    nodes = g["nodes"]
    assert len(nodes) == count
    by_id = {n["id"]: n for n in nodes}
    assert len(by_id) == len(nodes)
    seen, todo = set(), [g["startNodeId"]]
    while todo:
        node_id = todo.pop()
        assert node_id in by_id
        if node_id in seen:
            continue
        seen.add(node_id)
        n = by_id[node_id]
        assert n["type"] in ("QUESTION", "OBSERVATION_REPORT", "STOP")
        assert n["permittedAction"] is False and n["sourceRefs"]
        assert set(n["sourceRefs"]) <= refs
        if n["type"] == "QUESTION":
            assert set(n["responses"]) == {"YES", "NO", "UNKNOWN"}
            assert by_id[n["responses"]["UNKNOWN"]]["type"] == "STOP"
            todo.extend(n["responses"].values())
        else:
            assert n["responses"] == {} and n["causeConfirmed"] is False
    assert seen == set(by_id)
def check(c, n, idx, pack):
    doc = next(x for x in idx["documents"] if x["sourcePath"] == DOC)
    orig = doc["sourceObject"]["scenarios"][n-101]
    match = next(x for x in idx["matches"] if x["sourceId"] == "CHME3-DIAG-%d" % n)
    entry = next(x for x in pack["entries"] if x["id"] == match["canonicalId"])
    d, a = c["donor"], c["applicability"]
    assert c["schemaVersion"] == "diagnostic-research-candidate/1" and c["batch"] == 62
    assert c["originalId"] == orig["id"] == "CHME3-DIAG-%d" % n
    assert c["title"] == orig["title"] == entry["title"]
    assert c["scenarioId"] == d["canonicalId"] == match["canonicalId"] == entry["id"]
    assert d["repository"] == "DomEnota-hub/Test-" and d["commit"] == idx["donorCommit"] == "3176d6ee228f0ed4b78371f45209e10c1c724eff"
    assert d["documentPath"] == DOC and d["documentPointer"] == match["sourcePointer"] == "/scenarios/%d" % (n-101)
    assert d["documentBlob"] == doc["sourceBlobSha"] == "41d241cb0b58e5657ef0d6210e7b272d44df52d0"
    assert d["canonicalPack"] == match["canonicalPack"] == BASE + "diagnostics/recommended/diagnostics-02.pack.json"
    assert d["gzipBlob"] == entry["sourceObject"]["sourceBlobSha"] == "6a6068ad1ea54cb964b65a10ecf5c2425b2276e8"
    assert d["gzipIndependentlyDecoded"] is False and d["relation"] == "ID_TITLE_PROFILE_ONLY_NOT_GRAPH_EQUIVALENCE"
    for key in ("riskClass","actionAuthority","evidenceStatus","evidenceRefs","equipmentIds"):
        assert d[key] == orig[key]
    assert d["profileGate"] == orig.get("profileGate")
    variants = {"ЧМЭ3":"chme3","ЧМЭ3Т":"chme3t","ЧМЭ3Э":"chme3e"}
    assert a["possibleVariants"] == entry["applicability"]["variantIds"] == [variants[x] for x in orig["profiles"]]
    assert a["confirmedVariant"] is None and a["installedSchemeVerified"] is False and a["profileGateVerified"] is False and a["unknownProfile"] == "BLOCKED"
    if n == 110:
        assert orig["profiles"] == ["ЧМЭ3Т"] and d["profileGate"] == "chme3t-rheostatic"
        assert d["riskClass"] == "PROFILE_CRITICAL" and d["actionAuthority"] == "SOURCE_AND_PROFILE_REQUIRED"
        assert a["possibleVariants"] == ["chme3t"]
    else:
        assert d["riskClass"] == "ELEVATED_ELECTRICAL" and d["actionAuthority"] == "TRIAGE_ONLY_NO_REPAIR"
    assert c["publicationStatus"] == entry["publicationStatus"] == "CANDIDATE"
    assert c["actionDisposition"] == orig["actionAuthority"]
    for key in ("runtimeImport","executable","actionAuthorityGranted","sourceAuthorityVerified","humanSafetyReviewPassed"):
        assert c[key] is False
    assert c["warning"] == {"extendedHiddenByDefault":True,"readToEndRequired":True,"separateAcknowledgmentRequired":True,"grantsActionAuthority":False}
    assert c["safety"] and all(v is False for v in c["safety"].values())
    refs = {x["id"] for x in c["sources"]}
    assert len(refs) == len(c["sources"]) and {"DOC","PACK","FIELD"} <= refs
    assert ("N87" if n == 110 else "N74") in refs
    for s in c["sources"]:
        assert s["currentVerified"] is False and s["installedProfileVerified"] is False
        assert s["authority"] in ("INFORMATION_ONLY","HYPOTHESIS_ONLY")
        assert set(s["profiles"]) <= set(a["possibleVariants"])
    assert len(c["crossScenarioBoundaries"]) >= 3
    assert len({x["originalId"] for x in c["crossScenarioBoundaries"]}) == len(c["crossScenarioBoundaries"])
    assert len(c["sourceDiscrepancies"]) >= 2 and len(c["openGaps"]) >= 8
    assert c["deviceQA"] == {"status":"NOT_RUN_DEFERRED","registry":REG}
    assert c["originalId"] in (ROOT / REG).read_text(encoding="utf-8")
    graph(c["versions"]["SHORT"],8,refs)
    graph(c["versions"]["DETAILED"],12,refs)
    for mode in ("SHORT","DETAILED"):
        first = c["versions"][mode]["nodes"][0]
        assert first["responses"]["NO"] == first["responses"]["UNKNOWN"] == "stop-safety"
        if n == 110:
            second = c["versions"][mode]["nodes"][1]
            assert second["responses"]["NO"] == second["responses"]["UNKNOWN"] == "stop-profile"
    assert len(c["extensions"]) == 5
    assert len({e["id"] for e in c["extensions"]}) == 5
    for e in c["extensions"]:
        assert e["sourceId"] in refs and e["displayMode"] == "EXTENDED_ONLY"
        assert e["visibility"] == {"hiddenByDefault":True,"warningReadToEndRequired":True,"warningAcknowledgedRequired":True}
        assert e["actionDisposition"] == "INFORMATION_ONLY"
        assert e["executable"] is False and e["actionAuthorityGranted"] is False and e["procedureSteps"] == []
        graph({"startNodeId":e["nodes"][0]["id"],"nodes":e["nodes"]},4,refs)
def negative(c,n,idx,pack):
    mutations = [
      lambda x: x.update(runtimeImport=True),
      lambda x: x.update(executable=True),
      lambda x: x.update(publicationStatus="PUBLISHED"),
      lambda x: x.update(actionAuthorityGranted=True),
      lambda x: x.update(sourceAuthorityVerified=True),
      lambda x: x.update(humanSafetyReviewPassed=True),
      lambda x: x["applicability"].update(confirmedVariant="chme3t"),
      lambda x: x["applicability"].update(installedSchemeVerified=True),
      lambda x: x["applicability"].update(profileGateVerified=True),
      lambda x: x["applicability"].update(unknownProfile="ALLOW"),
      lambda x: x["donor"].update(commit="HEAD"),
      lambda x: x["donor"].update(documentPointer="/scenarios/0"),
      lambda x: x["donor"].update(documentBlob="wrong"),
      lambda x: x["donor"].update(gzipIndependentlyDecoded=True),
      lambda x: x["donor"].update(equipmentIds=[]),
      lambda x: x["donor"].update(evidenceRefs=[]),
      lambda x: x["donor"].update(riskClass="LOW"),
      lambda x: x["donor"].update(actionAuthority="AUTHORIZED"),
      lambda x: x["warning"].update(extendedHiddenByDefault=False),
      lambda x: x["warning"].update(readToEndRequired=False),
      lambda x: x["warning"].update(separateAcknowledgmentRequired=False),
      lambda x: x["warning"].update(grantsActionAuthority=True),
      lambda x: x["safety"].update(temporaryJumper=True),
      lambda x: x["safety"].update(highVoltageIntervention=True),
      lambda x: x["safety"].update(protectionReset=True),
      lambda x: x["versions"]["SHORT"]["nodes"][0]["responses"].update(UNKNOWN="s2"),
      lambda x: x["versions"]["DETAILED"]["nodes"][0].update(permittedAction=True),
      lambda x: x["extensions"][0]["visibility"].update(warningAcknowledgedRequired=False),
      lambda x: x["extensions"][1].update(executable=True),
      lambda x: x["extensions"][2].update(procedureSteps=["force contactor"]),
      lambda x: x["sources"][0].update(currentVerified=True),
      lambda x: x["sources"][0].update(installedProfileVerified=True),
      lambda x: x["crossScenarioBoundaries"].pop(),
      lambda x: x["sourceDiscrepancies"].pop(),
      lambda x: x["sources"][-1].update(id="DOC"),
      lambda x: x["deviceQA"].update(status="PASS"),
      lambda x: x["extensions"][3]["nodes"][0]["responses"].update(UNKNOWN=x["extensions"][3]["nodes"][1]["id"]),
    ]
    if n == 110:
        mutations += [
          lambda x: x["applicability"].update(possibleVariants=["chme3","chme3t"]),
          lambda x: x["donor"].update(profileGate=None),
          lambda x: x["versions"]["SHORT"]["nodes"][1]["responses"].update(UNKNOWN="s3"),
          lambda x: x["versions"]["DETAILED"]["nodes"][1]["responses"].update(NO="d3"),
        ]
    count=0
    for i,mutate in enumerate(mutations):
        altered=copy.deepcopy(c)
        mutate(altered)
        try:
            check(altered,n,idx,pack)
        except (AssertionError,KeyError):
            count+=1
            continue
        raise AssertionError("unsafe mutation accepted %d for %d" % (i,n))
    return count
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--negative",action="store_true")
    args=p.parse_args()
    idx=read(BASE+"migration/diagnostic-source-index.json")
    pack=read(BASE+"diagnostics/recommended/diagnostics-02.pack.json")
    count=0
    for n,path in FILES.items():
        c=read(path)
        check(c,n,idx,pack)
        if args.negative:
            count+=negative(c,n,idx,pack)
    print("CHME3_BATCH62_PASS SCENARIOS",len(FILES),"NEGATIVE",count)
if __name__ == "__main__":
    main()
