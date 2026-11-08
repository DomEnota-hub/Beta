#!/usr/bin/env python3
"""Batch61: source-anchored CHME3 emergency start and charge candidates; negative QA."""
import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "content-packs/diesel/chme3-family/"
DOC = "docs/locomotives/chme3/diagnostics_electrical_control_pass3.json"
FILES = {
    106: BASE + "diagnostics/authoring/chme3-diag-106-start-circuit-not-released.research.json",
    107: BASE + "diagnostics/authoring/chme3-diag-107-battery-not-charging.research.json",
    108: BASE + "diagnostics/authoring/chme3-diag-108-charge-regulation-unstable.research.json",
}
REGISTRY = "docs/diagnostics/DIAGNOSTIC_FINAL_DEVICE_QA_DEFERRED_2026-11-04.md"

def read(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))

def graph(g, expected, refs):
    nodes = g["nodes"]
    assert len(nodes) == expected
    by_id = {n["id"]: n for n in nodes}
    assert len(by_id) == expected
    seen, todo = set(), [g["startNodeId"]]
    while todo:
        key = todo.pop()
        if key in seen:
            continue
        n = by_id[key]
        seen.add(key)
        assert n["permittedAction"] is False and "procedureSteps" not in n
        assert n["sourceRefs"] and set(n["sourceRefs"]) <= refs
        assert n["type"] in ("QUESTION", "OBSERVATION_REPORT", "STOP")
        if n["type"] == "QUESTION":
            assert set(n["responses"]) == {"YES", "NO", "UNKNOWN"}
            assert by_id[n["responses"]["UNKNOWN"]]["type"] == "STOP"
            todo.extend(n["responses"].values())
        else:
            assert n["responses"] == {} and n["causeConfirmed"] is False
    assert seen == set(by_id)

def check(c, number, index, pack):
    doc = next(x for x in index["documents"] if x["sourcePath"] == DOC)
    original = doc["sourceObject"]["scenarios"][number - 101]
    match = next(x for x in index["matches"] if x["sourceId"] == "CHME3-DIAG-%d" % number)
    entry = next(x for x in pack["entries"] if x["id"] == match["canonicalId"])
    d, a = c["donor"], c["applicability"]
    assert c["schemaVersion"] == "diagnostic-research-candidate/1" and c["batch"] == 61
    assert c["originalId"] == original["id"] == "CHME3-DIAG-%d" % number
    assert c["title"] == original["title"] == entry["title"]
    assert c["scenarioId"] == d["canonicalId"] == match["canonicalId"] == entry["id"]
    assert d["repository"] == "DomEnota-hub/Test-"
    assert d["commit"] == index["donorCommit"] == "3176d6ee228f0ed4b78371f45209e10c1c724eff"
    assert d["documentPath"] == DOC and d["documentPointer"] == match["sourcePointer"] == "/scenarios/%d" % (number - 101)
    assert d["documentBlob"] == doc["sourceBlobSha"] == "41d241cb0b58e5657ef0d6210e7b272d44df52d0"
    assert d["canonicalPack"] == match["canonicalPack"] == BASE + "diagnostics/recommended/diagnostics-01.pack.json"
    assert d["gzipBlob"] == entry["sourceObject"]["sourceBlobSha"] == "6a6068ad1ea54cb964b65a10ecf5c2425b2276e8"
    assert d["gzipIndependentlyDecoded"] is False and d["relation"] == "ID_TITLE_PROFILE_ONLY_NOT_GRAPH_EQUIVALENCE"
    for key in ("riskClass", "actionAuthority", "evidenceStatus", "evidenceRefs", "equipmentIds"):
        assert d[key] == original[key]
    assert original["profiles"] == ["ЧМЭ3", "ЧМЭ3Т", "ЧМЭ3Э"]
    assert set(a["possibleVariants"]) == set(entry["applicability"]["variantIds"]) == {"chme3", "chme3t", "chme3e"}
    assert a["confirmedVariant"] is None and a["installedSchemeVerified"] is False and a["unknownProfile"] == "BLOCKED"
    assert c["publicationStatus"] == entry["publicationStatus"] == "CANDIDATE"
    assert c["actionDisposition"] == original["actionAuthority"]
    for key in ("runtimeImport", "executable", "actionAuthorityGranted", "sourceAuthorityVerified", "humanSafetyReviewPassed"):
        assert c[key] is False
    assert c["warning"] == {"extendedHiddenByDefault": True, "readToEndRequired": True, "separateAcknowledgmentRequired": True, "grantsActionAuthority": False}
    assert c["safety"] and all(v is False for v in c["safety"].values())
    assert c["safety"]["mechanicalContactSeparation"] is False
    refs = {s["id"] for s in c["sources"]}
    assert len(refs) == len(c["sources"]) and {"DOC", "PACK", "N67", "FIELD", "LOCAL"} <= refs
    assert ("N148" if number == 106 else "N149") in refs
    assert len(c["sources"]) == 6
    for source in c["sources"]:
        assert source["currentVerified"] is False and source["installedProfileVerified"] is False
        assert source["authority"] in ("INFORMATION_ONLY", "HYPOTHESIS_ONLY")
    assert next(s for s in c["sources"] if s["id"] == "N67")["profiles"] == ["chme3t", "chme3e"]
    assert next(s for s in c["sources"] if s["id"] == ("N148" if number == 106 else "N149"))["profiles"] == ["chme3"]
    assert len(c["crossScenarioBoundaries"]) >= 3
    assert len({x["originalId"] for x in c["crossScenarioBoundaries"]}) == len(c["crossScenarioBoundaries"])
    assert len(c["sourceDiscrepancies"]) >= 2 and len(c["openGaps"]) >= 8
    assert c["deviceQA"] == {"status": "NOT_RUN_DEFERRED", "registry": REGISTRY}
    assert c["originalId"] in (ROOT / REGISTRY).read_text(encoding="utf-8")
    graph(c["versions"]["SHORT"], 8, refs)
    graph(c["versions"]["DETAILED"], 12, refs)
    for mode in ("SHORT", "DETAILED"):
        first = c["versions"][mode]["nodes"][0]
        assert first["responses"]["NO"] == first["responses"]["UNKNOWN"] == "stop-safety"
    if number == 106:
        assert d["riskClass"] == "EMERGENCY_ELECTRICAL" and d["actionAuthority"] == "SAFETY_GATE_REQUIRED"
        for mode in ("SHORT", "DETAILED"):
            nodes = {x["id"]: x for x in c["versions"][mode]["nodes"]}
            assert nodes["stop-active"]["type"] == "STOP"
            assert nodes["s2" if mode == "SHORT" else "d2"]["responses"]["NO"] == "stop-active"
    assert len(c["extensions"]) == 5
    assert len({x["id"] for x in c["extensions"]}) == 5
    for x in c["extensions"]:
        assert x["sourceId"] in refs and x["displayMode"] == "EXTENDED_ONLY"
        assert x["visibility"] == {"hiddenByDefault": True, "warningReadToEndRequired": True, "warningAcknowledgedRequired": True}
        assert x["actionDisposition"] == "INFORMATION_ONLY"
        assert x["executable"] is False and x["actionAuthorityGranted"] is False and x["procedureSteps"] == []
        graph({"startNodeId": x["nodes"][0]["id"], "nodes": x["nodes"]}, 4, refs)

def negative(c, number, idx, pack):
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
        lambda x: x["donor"].update(documentPointer="/scenarios/1"),
        lambda x: x["donor"].update(documentBlob="bad"),
        lambda x: x["donor"].update(gzipIndependentlyDecoded=True),
        lambda x: x["donor"].update(equipmentIds=[]),
        lambda x: x["donor"].update(evidenceRefs=[]),
        lambda x: x["donor"].update(riskClass="UNSAFE"),
        lambda x: x["donor"].update(actionAuthority="TRIAGE_ONLY_NO_REPAIR" if number == 106 else "SAFETY_GATE_REQUIRED"),
        lambda x: x["warning"].update(extendedHiddenByDefault=False),
        lambda x: x["warning"].update(readToEndRequired=False),
        lambda x: x["warning"].update(separateAcknowledgmentRequired=False),
        lambda x: x["warning"].update(grantsActionAuthority=True),
        lambda x: x["safety"].update(temporaryJumper=True),
        lambda x: x["safety"].update(mechanicalContactSeparation=True),
        lambda x: x["safety"].update(highVoltageIntervention=True),
        lambda x: x["safety"].update(batteryExternalCharging=True),
        lambda x: x["versions"]["SHORT"]["nodes"][0]["responses"].update(UNKNOWN="s2"),
        lambda x: x["versions"]["DETAILED"]["nodes"][0].update(permittedAction=True),
        lambda x: x["versions"]["DETAILED"]["nodes"][1]["responses"].update(UNKNOWN="d3"),
        lambda x: x["extensions"][0]["visibility"].update(warningAcknowledgedRequired=False),
        lambda x: x["extensions"][1].update(executable=True),
        lambda x: x["extensions"][2].update(procedureSteps=["unsafe"]),
        lambda x: x["sources"][0].update(currentVerified=True),
        lambda x: x["sources"][0].update(installedProfileVerified=True),
        lambda x: x["crossScenarioBoundaries"].pop(),
        lambda x: x["sourceDiscrepancies"].pop(),
        lambda x: x["sources"][-1].update(id="DOC"),
        lambda x: x["deviceQA"].update(status="PASS"),
        lambda x: x["extensions"][3]["nodes"][0]["responses"].update(UNKNOWN=x["extensions"][3]["nodes"][1]["id"]),
    ]
    if number == 106:
        mutations += [
            lambda x: x["versions"]["SHORT"]["nodes"][1]["responses"].update(NO="s3"),
            lambda x: x["versions"]["DETAILED"]["nodes"][1]["responses"].update(NO="d3"),
        ]
    for i, change in enumerate(mutations):
        changed = copy.deepcopy(c)
        change(changed)
        try:
            check(changed, number, idx, pack)
        except (AssertionError, KeyError):
            continue
        raise AssertionError("unsafe mutation accepted: %d for %d" % (i, number))
    return len(mutations)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative", action="store_true")
    args = parser.parse_args()
    idx = read(BASE + "migration/diagnostic-source-index.json")
    pack = read(BASE + "diagnostics/recommended/diagnostics-01.pack.json")
    count = 0
    for number, path in FILES.items():
        c = read(path)
        check(c, number, idx, pack)
        if args.negative:
            count += negative(c, number, idx, pack)
    print("CHME3_BATCH61_PASS", "SCENARIOS", len(FILES), "NEGATIVE", count)

if __name__ == "__main__":
    main()
