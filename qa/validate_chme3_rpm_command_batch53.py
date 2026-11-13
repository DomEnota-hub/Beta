#!/usr/bin/env python3
"""Batch53: exact pinned donor, graph safety and negative tests for CHME3 004/005."""
import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "content-packs/diesel/chme3-family/"
INDEX = BASE + "migration/diagnostic-source-index.json"
PACK = BASE + "diagnostics/recommended/diagnostics-01.pack.json"
PATHS = {
    4: BASE + "diagnostics/authoring/chme3-diag-004-no-rpm-rise-by-positions.research.json",
    5: BASE + "diagnostics/authoring/chme3-diag-005-rpm-not-decreasing.research.json",
}
PIN = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
DOC = "docs/locomotives/chme3/diagnostics_powerplant_pass3.json"
PROFILE = {"chme3", "chme3t", "chme3e"}
SOURCES = {4: {"DOC", "PACK", "N38", "INDEX", "FIELD"}, 5: {"DOC", "PACK", "N38", "FIELD"}}
BOUNDS = {
    4: {"CHME3-DIAG-003", "CHME3-DIAG-005", "CHME3-DIAG-006", "CHME3-DIAG-008"},
    5: {"CHME3-DIAG-002", "CHME3-DIAG-003", "CHME3-DIAG-004"},
}


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def graph(v, refs, safe_start=False):
    nodes = v["nodes"]
    byid = {x["id"]: x for x in nodes}
    assert len(byid) == len(nodes) and v["startNodeId"] in byid
    seen, todo = set(), [v["startNodeId"]]
    while todo:
        key = todo.pop()
        node = byid[key]
        if key in seen:
            continue
        seen.add(key)
        assert node["type"] in {"QUESTION", "OBSERVATION_REPORT", "STOP"}
        assert node["permittedAction"] is False
        assert node["sourceRefs"] and set(node["sourceRefs"]) <= refs
        assert "procedureSteps" not in node
        if node["type"] == "QUESTION":
            assert set(node["responses"]) == {"YES", "NO", "UNKNOWN"}
            assert byid[node["responses"]["UNKNOWN"]]["type"] == "STOP"
        else:
            assert node["responses"] == {}
            assert node["causeConfirmed"] is False
        todo.extend(node["responses"].values())
    assert seen == set(byid)
    if safe_start:
        first = byid[v["startNodeId"]]
        assert first["responses"]["NO"] == first["responses"]["UNKNOWN"] == "stop-safety"
        assert byid["stop-safety"]["type"] == "STOP"


def check(c, num, index, pack):
    sid = f"CHME3-DIAG-{num:03d}"
    assert c["schemaVersion"] == "diagnostic-research-candidate/1"
    assert c["batch"] == 53 and c["originalId"] == sid
    assert c["scenarioId"] == f"chme3.diagnostics.chme3-diag-{num:03d}"
    d = c["donor"]
    assert d["repository"] == "DomEnota-hub/Test-"
    assert d["commit"] == index["donorCommit"] == PIN
    assert d["documentPath"] == DOC and d["documentPointer"] == f"/scenarios/{num - 1}"
    assert d["documentBlob"] == "63988703bb795e82f40335a756b8b9bd3cad8e0a"
    assert d["gzipBlob"] == "6a6068ad1ea54cb964b65a10ecf5c2425b2276e8"
    assert d["gzipIndependentlyDecoded"] is False
    assert d["relation"] == "ID_TITLE_PROFILE_ONLY_NOT_GRAPH_EQUIVALENCE"
    doc = next(x for x in index["documents"] if x["sourcePath"] == DOC)
    assert doc["sourceBlobSha"] == d["documentBlob"]
    source = doc["sourceObject"]["scenarios"][num - 1]
    assert source["id"] == sid and source["title"] == c["title"]
    assert source["profiles"] == ["ЧМЭ3", "ЧМЭ3Т", "ЧМЭ3Э"]
    for key in ("riskClass", "actionAuthority", "evidenceStatus", "evidenceRefs", "equipmentIds"):
        assert source[key] == d[key]
    assert d["riskClass"] == ("NORMAL_DIAGNOSTIC" if num == 4 else "ELEVATED")
    assert d["actionAuthority"] == ("SOURCE_AND_PROFILE_REQUIRED" if num == 4 else "TRIAGE_ONLY_NO_REPAIR")
    match = next(x for x in index["matches"] if x["sourceId"] == sid)
    assert match["sourcePointer"] == d["documentPointer"]
    assert match["canonicalId"] == c["scenarioId"] and match["canonicalPack"] == d["canonicalPack"] == PACK
    entry = next(x for x in pack["entries"] if x["id"] == c["scenarioId"])
    assert entry["title"] == c["title"] and entry["publicationStatus"] == "CANDIDATE"
    assert entry["sourceObject"]["sourceBlobSha"] == d["gzipBlob"]
    assert entry["sourceObject"]["object"]["severity"] == d["riskClass"]
    assert set(entry["applicability"]["variantIds"]) == set(c["applicability"]["possibleVariants"]) == PROFILE
    assert c["applicability"]["confirmedVariant"] is None
    assert c["applicability"]["installedSchemeVerified"] is False
    assert c["applicability"]["unknownProfile"] == "BLOCKED"
    assert c["publicationStatus"] == "CANDIDATE" and c["actionDisposition"] == "TRIAGE_ONLY_NO_REPAIR"
    for key in ("runtimeImport", "executable", "actionAuthorityGranted", "sourceAuthorityVerified", "humanSafetyReviewPassed"):
        assert c[key] is False
    assert c["warning"] == {
        "extendedHiddenByDefault": True, "readToEndRequired": True,
        "separateAcknowledgmentRequired": True, "grantsActionAuthority": False
    }
    assert c["safety"] and all(x is False for x in c["safety"].values())
    assert {x["originalId"] for x in c["crossScenarioBoundaries"]} == BOUNDS[num]
    assert len(c["openGaps"]) >= 6
    refs = {x["id"] for x in c["sources"]}
    assert len(refs) == len(c["sources"]) and refs == SOURCES[num]
    assert all(x["currentVerified"] is False and x["installedProfileVerified"] is False for x in c["sources"])
    assert all(x["authority"] != "ACTION_AUTHORIZED" for x in c["sources"])
    assert next(x for x in c["sources"] if x["id"] == "N38")["kind"] == "HISTORICAL_TRAINING"
    assert next(x for x in c["sources"] if x["id"] == "FIELD")["authority"] == "HYPOTHESIS_ONLY"
    if num == 4:
        assert next(x for x in c["sources"] if x["id"] == "INDEX")["authority"] == "REFERENCE_ONLY_NOT_PROCEDURE"
    else:
        assert c["emergency"] == {
            "sourceBound": True, "activeOrUncertainOverspeed": "STOP_NO_PROCEDURE",
            "currentEmergencyInstructionVerified": False, "roleAuthorized": False,
            "profileSafetyGatePassed": False, "emergencyActionAuthorized": False
        }
    assert len(c["versions"]["SHORT"]["nodes"]) == 8
    assert len(c["versions"]["DETAILED"]["nodes"]) == 12
    for version in c["versions"].values():
        graph(version, refs, safe_start=True)
    assert len(c["extensions"]) == 5 and len({x["id"] for x in c["extensions"]}) == 5
    for ext in c["extensions"]:
        assert ext["sourceId"] in refs
        assert ext["displayMode"] == "EXTENDED_ONLY"
        assert ext["visibility"] == {
            "hiddenByDefault": True, "warningReadToEndRequired": True,
            "warningAcknowledgedRequired": True
        }
        assert ext["actionDisposition"] == "INFORMATION_ONLY"
        assert ext["executable"] is False and ext["actionAuthorityGranted"] is False
        assert ext["procedureSteps"] == []
        graph({"startNodeId": ext["nodes"][0]["id"], "nodes": ext["nodes"]}, refs)


def negative(c, num, index, pack):
    mutations = [
        lambda x: x.update(runtimeImport=True),
        lambda x: x.update(executable=True),
        lambda x: x.update(actionAuthorityGranted=True),
        lambda x: x.update(sourceAuthorityVerified=True),
        lambda x: x.update(humanSafetyReviewPassed=True),
        lambda x: x.update(publicationStatus="PUBLISHED"),
        lambda x: x["applicability"].update(confirmedVariant="chme3"),
        lambda x: x["applicability"].update(unknownProfile="ALLOW"),
        lambda x: x["applicability"].update(installedSchemeVerified=True),
        lambda x: x["donor"].update(commit="HEAD"),
        lambda x: x["donor"].update(documentPointer="/scenarios/0"),
        lambda x: x["donor"].update(documentBlob="fake"),
        lambda x: x["donor"].update(gzipIndependentlyDecoded=True),
        lambda x: x["donor"].update(riskClass="EMERGENCY_STOP"),
        lambda x: x["donor"].update(actionAuthority="CAB_ONLY"),
        lambda x: x["donor"].update(evidenceRefs=[]),
        lambda x: x["warning"].update(extendedHiddenByDefault=False),
        lambda x: x["warning"].update(readToEndRequired=False),
        lambda x: x["warning"].update(separateAcknowledgmentRequired=False),
        lambda x: x["warning"].update(grantsActionAuthority=True),
        lambda x: x["safety"].update(bypassProtection=True),
        lambda x: x["safety"].update(newStartAttempts=True),
        lambda x: x["versions"]["SHORT"]["nodes"][0]["responses"].update(UNKNOWN="s2"),
        lambda x: x["versions"]["DETAILED"]["nodes"][0].update(permittedAction=True),
        lambda x: x["versions"]["DETAILED"]["nodes"][-1].update(causeConfirmed=True),
        lambda x: x["extensions"][0]["visibility"].update(warningAcknowledgedRequired=False),
        lambda x: x["extensions"][1].update(executable=True),
        lambda x: x["extensions"][2].update(procedureSteps=["danger"]),
        lambda x: x["sources"][-1].update(authority="ACTION_AUTHORIZED"),
        lambda x: x["crossScenarioBoundaries"].pop(),
        lambda x: x["sources"][-1].update(id="DOC"),
    ]
    if num == 5:
        mutations.extend([
            lambda x: x["emergency"].update(sourceBound=False),
            lambda x: x["emergency"].update(emergencyActionAuthorized=True),
            lambda x: x["versions"]["DETAILED"]["nodes"][0]["responses"].update(NO="d2"),
        ])
    for i, mutate in enumerate(mutations, 1):
        candidate = copy.deepcopy(c)
        mutate(candidate)
        try:
            check(candidate, num, index, pack)
        except (AssertionError, KeyError, StopIteration):
            continue
        raise AssertionError(f"negative escaped: {num}/{i}")
    return len(mutations)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative", action="store_true")
    args = parser.parse_args()
    index, pack = read(INDEX), read(PACK)
    for num, path in PATHS.items():
        candidate = read(path)
        check(candidate, num, index, pack)
        print(f"CHME3_{num:03d}_PASS")
        if args.negative:
            print(f"CHME3_{num:03d}_NEGATIVE_PASS {negative(candidate, num, index, pack)}")
