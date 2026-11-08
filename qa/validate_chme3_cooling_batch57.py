#!/usr/bin/env python3
"""Batch 57: CHME3 cooling candidates, donor identity, fail-closed graphs, negative mutations."""
import argparse
import copy
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
B = "content-packs/diesel/chme3-family/"
D = "docs/locomotives/chme3/diagnostics_powerplant_pass3.json"
P = {12: B + "diagnostics/authoring/chme3-diag-012-water-overheat.research.json"}

def read(path):
    return json.loads((R / path).read_text(encoding="utf-8"))

def graph(v, refs):
    nodes = v["nodes"]
    m = {x["id"]: x for x in nodes}
    assert len(m) == len(nodes)
    todo = [v["startNodeId"]]
    seen = set()
    while todo:
        key = todo.pop()
        if key in seen:
            continue
        x = m[key]
        seen.add(key)
        assert x["type"] in ("QUESTION", "OBSERVATION_REPORT", "STOP")
        assert x["permittedAction"] is False
        assert x["sourceRefs"] and set(x["sourceRefs"]) <= refs
        assert "procedureSteps" not in x
        if x["type"] == "QUESTION":
            assert set(x["responses"]) == {"YES", "NO", "UNKNOWN"}
            assert m[x["responses"]["UNKNOWN"]]["type"] == "STOP"
            todo.extend(x["responses"].values())
        else:
            assert x["responses"] == {} and x["causeConfirmed"] is False
    assert seen == set(m), "unreachable graph nodes"

def check(c, num, idx, pack):
    sid = f"CHME3-DIAG-{num:03d}"
    d = c["donor"]
    doc = next(x for x in idx["documents"] if x["sourcePath"] == D)
    src = doc["sourceObject"]["scenarios"][num-1]
    match = next(x for x in idx["matches"] if x["sourceId"] == sid)
    entry = next(x for x in pack["entries"] if x["id"] == match["canonicalId"])
    assert c["schemaVersion"] == "diagnostic-research-candidate/1" and c["batch"] == 57
    assert c["originalId"] == src["id"] == sid
    assert c["title"] == src["title"] == entry["title"]
    assert c["scenarioId"] == d["canonicalId"] == match["canonicalId"] == entry["id"]
    assert d["repository"] == "DomEnota-hub/Test-"
    assert d["commit"] == idx["donorCommit"] == "3176d6ee228f0ed4b78371f45209e10c1c724eff"
    assert d["documentPath"] == D and d["documentPointer"] == match["sourcePointer"] == f"/scenarios/{num-1}"
    assert d["documentBlob"] == doc["sourceBlobSha"] == "63988703bb795e82f40335a756b8b9bd3cad8e0a"
    assert d["canonicalPack"] == "content-packs/diesel/chme3-family/diagnostics/recommended/diagnostics-01.pack.json"
    assert d["gzipBlob"] == entry["sourceObject"]["sourceBlobSha"] == "6a6068ad1ea54cb964b65a10ecf5c2425b2276e8"
    assert d["gzipIndependentlyDecoded"] is False
    assert d["relation"] == "ID_TITLE_PROFILE_ONLY_NOT_GRAPH_EQUIVALENCE"
    for k in ("riskClass", "actionAuthority", "evidenceStatus", "evidenceRefs", "equipmentIds"):
        assert d[k] == src[k]
    assert src["profiles"] == ["ЧМЭ3", "ЧМЭ3Т", "ЧМЭ3Э"]
    assert d["riskClass"] == "ELEVATED" and d["actionAuthority"] == "SOURCE_AND_PROFILE_REQUIRED"
    assert set(c["applicability"]["possibleVariants"]) == set(entry["applicability"]["variantIds"]) == {"chme3", "chme3t", "chme3e"}
    assert c["applicability"]["confirmedVariant"] is None
    assert c["applicability"]["installedSchemeVerified"] is False
    assert c["applicability"]["unknownProfile"] == "BLOCKED"
    assert c["publicationStatus"] == entry["publicationStatus"] == "CANDIDATE"
    assert c["actionDisposition"] == "SOURCE_AND_PROFILE_REQUIRED"
    for k in ("runtimeImport", "executable", "actionAuthorityGranted", "sourceAuthorityVerified", "humanSafetyReviewPassed"):
        assert c[k] is False
    assert c["warning"] == {
        "extendedHiddenByDefault": True, "readToEndRequired": True,
        "separateAcknowledgmentRequired": True, "grantsActionAuthority": False
    }
    assert c["safety"] and all(x is False for x in c["safety"].values())
    refs = {x["id"] for x in c["sources"]}
    assert len(refs) == len(c["sources"]) and {"DOC", "PACK", "N47", "N53", "N56", "SECONDARY996", "FIELD"} <= refs
    assert all(x["currentVerified"] is False and x["installedProfileVerified"] is False and x["authority"] != "ACTION_AUTHORIZED" for x in c["sources"])
    assert any(x["kind"] == "HISTORICAL_FIELD_PRACTICE" and x["authority"] == "HYPOTHESIS_ONLY" for x in c["sources"])
    assert len(c["crossScenarioBoundaries"]) >= 4
    assert len({x["originalId"] for x in c["crossScenarioBoundaries"]}) == len(c["crossScenarioBoundaries"])
    assert len(c["openGaps"]) >= 10
    for key, count in (("SHORT", 8), ("DETAILED", 12)):
        v = c["versions"][key]
        assert len(v["nodes"]) == count
        graph(v, refs)
        assert v["nodes"][0]["responses"]["NO"] == v["nodes"][0]["responses"]["UNKNOWN"] == "stop-safety"
    assert len(c["extensions"]) == 5 and len({x["id"] for x in c["extensions"]}) == 5
    for ext in c["extensions"]:
        assert ext["sourceId"] in refs
        assert ext["displayMode"] == "EXTENDED_ONLY"
        assert ext["visibility"] == {
            "hiddenByDefault": True, "warningReadToEndRequired": True, "warningAcknowledgedRequired": True
        }
        assert ext["actionDisposition"] == "INFORMATION_ONLY"
        assert ext["executable"] is False and ext["actionAuthorityGranted"] is False
        assert ext["procedureSteps"] == []
        assert len(ext["nodes"]) == 4
        graph({"startNodeId": ext["nodes"][0]["id"], "nodes": ext["nodes"]}, refs)
    assert "CHME3-DIAG-011" in {x["originalId"] for x in c["crossScenarioBoundaries"]}
    assert next(x for x in c["sources"] if x["id"]=="SECONDARY996")["authority"]=="HYPOTHESIS_ONLY"

def negative(c, num, idx, pack):
    mutations = [
        lambda x: x.update(runtimeImport=True),
        lambda x: x.update(executable=True),
        lambda x: x.update(publicationStatus="PUBLISHED"),
        lambda x: x.update(actionAuthorityGranted=True),
        lambda x: x.update(sourceAuthorityVerified=True),
        lambda x: x.update(humanSafetyReviewPassed=True),
        lambda x: x["applicability"].update(confirmedVariant="chme3"),
        lambda x: x["applicability"].update(installedSchemeVerified=True),
        lambda x: x["applicability"].update(unknownProfile="ALLOW"),
        lambda x: x["donor"].update(commit="HEAD"),
        lambda x: x["donor"].update(documentPointer="/scenarios/0"),
        lambda x: x["donor"].update(gzipIndependentlyDecoded=True),
        lambda x: x["donor"].update(equipmentIds=[]),
        lambda x: x["donor"].update(evidenceRefs=[]),
        lambda x: x["warning"].update(extendedHiddenByDefault=False),
        lambda x: x["warning"].update(readToEndRequired=False),
        lambda x: x["warning"].update(separateAcknowledgmentRequired=False),
        lambda x: x["warning"].update(grantsActionAuthority=True),
        lambda x: x["safety"].update(underLoadTesting=True),
        lambda x: x["safety"].update(openingHotCoolingCircuit=True),
        lambda x: x["safety"].update(manualLouverFixation=True),
        lambda x: x["versions"]["SHORT"]["nodes"][0]["responses"].update(UNKNOWN="s2"),
        lambda x: x["versions"]["DETAILED"]["nodes"][0].update(permittedAction=True),
        lambda x: x["extensions"][0]["visibility"].update(warningAcknowledgedRequired=False),
        lambda x: x["extensions"][1].update(executable=True),
        lambda x: x["extensions"][2].update(procedureSteps=["unsafe"]),
        lambda x: x["sources"][-1].update(authority="ACTION_AUTHORIZED"),
        lambda x: x["crossScenarioBoundaries"].pop(),
        lambda x: x["sources"][-1].update(id="DOC"),
        lambda x: x["versions"]["DETAILED"]["nodes"][1]["responses"].update(UNKNOWN="d3"),
    ]
    for j, mutate in enumerate(mutations):
        test = copy.deepcopy(c)
        mutate(test)
        try:
            check(test, num, idx, pack)
        except (AssertionError, KeyError):
            continue
        raise AssertionError(f"unsafe mutation accepted: {num}/{j}")
    return len(mutations)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative", action="store_true")
    args = parser.parse_args()
    idx = read(B + "migration/diagnostic-source-index.json")
    pack = read(B + "diagnostics/recommended/diagnostics-01.pack.json")
    count = 0
    for num, path in P.items():
        c = read(path)
        check(c, num, idx, pack)
        count += negative(c, num, idx, pack) if args.negative else 0
        print("CHME3_BATCH57_SCENARIO_PASS", num)
    print("CHME3_BATCH57_PASS", len(P), "NEGATIVE", count)

if __name__ == "__main__":
    main()
