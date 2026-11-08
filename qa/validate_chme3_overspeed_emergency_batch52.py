#!/usr/bin/env python3
"""CHME3-DIAG-003: emergency-source-bound research candidate and negative QA."""
import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
C = "content-packs/diesel/chme3-family/diagnostics/authoring/chme3-diag-003-overspeed-emergency.research.json"
I = "content-packs/diesel/chme3-family/migration/diagnostic-source-index.json"
K = "content-packs/diesel/chme3-family/diagnostics/recommended/diagnostics-01.pack.json"
PIN = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
PROFILES = {"chme3", "chme3t", "chme3e"}


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def graph(nodes, start, sources, emergency=False):
    by_id = {n["id"]: n for n in nodes}
    assert len(by_id) == len(nodes) and start in by_id
    reached, todo = set(), [start]
    while todo:
        key = todo.pop()
        assert key in by_id
        if key in reached:
            continue
        reached.add(key)
        node = by_id[key]
        assert node["type"] in ("QUESTION", "OBSERVATION_REPORT", "STOP")
        assert node["permittedAction"] is False
        assert node["sourceRefs"] and set(node["sourceRefs"]) <= sources
        assert "procedureSteps" not in node
        if node["type"] == "QUESTION":
            assert set(node["responses"]) == {"YES", "NO", "UNKNOWN"}
            assert by_id[node["responses"]["UNKNOWN"]]["type"] == "STOP"
        else:
            assert node["responses"] == {}
            assert node["causeConfirmed"] is False
        if emergency and node["id"] == "emergency":
            assert node["type"] == "STOP"
            assert "не публикуется" in node["text"]
        todo.extend(node["responses"].values())
    assert reached == set(by_id)
    if emergency:
        assert by_id["emergency"]["type"] == "STOP"
        assert by_id[start]["responses"]["YES"] == "emergency"
        assert by_id[start]["responses"]["UNKNOWN"] == "emergency"


def check(c, index, pack):
    assert c["schemaVersion"] == "diagnostic-research-candidate/1"
    assert c["originalId"] == "CHME3-DIAG-003"
    assert c["scenarioId"] == "chme3.diagnostics.chme3-diag-003"
    assert c["batch"] == 52
    d = c["donor"]
    assert d["repository"] == "DomEnota-hub/Test-"
    assert d["commit"] == index["donorCommit"] == PIN
    assert d["documentPath"] == "docs/locomotives/chme3/diagnostics_powerplant_pass3.json"
    assert d["documentPointer"] == "/scenarios/2"
    assert d["documentBlob"] == "63988703bb795e82f40335a756b8b9bd3cad8e0a"
    assert d["relation"] == "ID_TITLE_PROFILE_ONLY_NOT_GRAPH_EQUIVALENCE"
    assert d["gzipIndependentlyDecoded"] is False
    document = next(x for x in index["documents"] if x["sourcePath"] == d["documentPath"])
    assert document["sourceBlobSha"] == d["documentBlob"]
    source = document["sourceObject"]["scenarios"][2]
    assert (source["id"], source["title"], source["riskClass"]) == (c["originalId"], c["title"], d["riskClass"])
    assert source["riskClass"] == "EMERGENCY_STOP"
    assert source["actionAuthority"] == d["actionAuthority"] == "SAFETY_GATE_REQUIRED"
    assert source["evidenceStatus"] == d["evidenceStatus"] == "LEGACY_CAUSE_MODEL_PRIMARY_ACTION_PENDING"
    assert source["profiles"] == ["ЧМЭ3", "ЧМЭ3Т", "ЧМЭ3Э"]
    assert source["equipmentIds"] == d["equipmentIds"]
    assert source["evidenceRefs"] == d["evidenceRefs"]
    match = next(x for x in index["matches"] if x["sourceId"] == c["originalId"])
    assert match["sourcePointer"] == d["documentPointer"]
    assert (match["canonicalId"], match["canonicalPack"]) == (c["scenarioId"], d["canonicalPack"])
    entry = next(x for x in pack["entries"] if x["id"] == c["scenarioId"])
    assert entry["title"] == c["title"] and entry["publicationStatus"] == "CANDIDATE"
    assert d["gzipBlob"] == entry["sourceObject"]["sourceBlobSha"]
    assert entry["sourceObject"]["object"]["severity"] == "EMERGENCY_STOP"
    assert set(entry["applicability"]["variantIds"]) == set(c["applicability"]["possibleVariants"]) == PROFILES
    assert c["applicability"]["confirmedVariant"] is None
    assert c["applicability"]["installedSchemeVerified"] is False
    assert c["applicability"]["unknownProfile"] == "BLOCKED"
    assert c["publicationStatus"] == "CANDIDATE"
    assert c["actionDisposition"] == "TRIAGE_ONLY_NO_REPAIR"
    for flag in ("runtimeImport", "executable", "actionAuthorityGranted", "sourceAuthorityVerified", "humanSafetyReviewPassed"):
        assert c[flag] is False
    assert c["warning"] == {
        "extendedHiddenByDefault": True, "readToEndRequired": True,
        "separateAcknowledgmentRequired": True, "grantsActionAuthority": False
    }
    assert c["safety"] and all(value is False for value in c["safety"].values())
    assert c["emergency"] == {
        "sourceBound": True,
        "currentEmergencyInstructionVerified": False,
        "exactProcedureVerified": False,
        "roleAuthorized": False,
        "profileSafetyGatePassed": False,
        "emergencyActionAuthorized": False,
        "activeEventDisposition": "STOP_AND_REFER_TO_CURRENT_AUTHORIZED_EMERGENCY_PROCEDURE",
        "historicalThresholdApplicable": False
    }
    assert {x["originalId"] for x in c["crossScenarioBoundaries"]} == {
        "CHME3-DIAG-002", "CHME3-DIAG-004", "CHME3-DIAG-005"
    }
    sources = c["sources"]
    source_ids = {x["id"] for x in sources}
    assert len(sources) == len(source_ids)
    assert source_ids == {"DOC", "PACK", "N39", "N38", "N38T", "INDEX", "FIELD"}
    assert all(x["currentVerified"] is False and x["installedProfileVerified"] is False for x in sources)
    assert all(x["authority"] != "ACTION_AUTHORIZED" for x in sources)
    assert next(x for x in sources if x["id"] == "INDEX")["authority"] == "REFERENCE_ONLY_NOT_PROCEDURE"
    assert next(x for x in sources if x["id"] == "N39")["kind"] == "HISTORICAL_TRAINING"
    assert set(next(x for x in sources if x["id"] == "N38T")["profiles"]) == {"chme3t", "chme3e"}
    assert len(c["versions"]["SHORT"]["nodes"]) == 8
    assert len(c["versions"]["DETAILED"]["nodes"]) == 12
    for version in ("SHORT", "DETAILED"):
        v = c["versions"][version]
        graph(v["nodes"], v["startNodeId"], source_ids, emergency=True)
    assert len(c["extensions"]) == 5
    assert {e["id"] for e in c["extensions"]} == {"event", "limiter", "governor", "variants", "norm"}
    for e in c["extensions"]:
        assert e["sourceId"] in source_ids
        assert e["displayMode"] == "EXTENDED_ONLY"
        assert e["visibility"] == {
            "hiddenByDefault": True,
            "warningReadToEndRequired": True,
            "warningAcknowledgedRequired": True,
        }
        assert e["actionDisposition"] == "INFORMATION_ONLY"
        assert e["executable"] is False and e["actionAuthorityGranted"] is False
        assert e["procedureSteps"] == []
        graph(e["nodes"], e["nodes"][0]["id"], source_ids)
    assert len(c["openGaps"]) >= 6


def negatives(c, index, pack):
    mutations = [
        lambda x: x.update(runtimeImport=True),
        lambda x: x.update(executable=True),
        lambda x: x.update(actionAuthorityGranted=True),
        lambda x: x.update(sourceAuthorityVerified=True),
        lambda x: x.update(humanSafetyReviewPassed=True),
        lambda x: x.update(publicationStatus="PUBLISHED"),
        lambda x: x["applicability"].update(confirmedVariant="chme3"),
        lambda x: x["applicability"].update(unknownProfile="ALLOW"),
        lambda x: x["donor"].update(commit="HEAD"),
        lambda x: x["donor"].update(documentPointer="/scenarios/1"),
        lambda x: x["donor"].update(riskClass="NORMAL_DIAGNOSTIC"),
        lambda x: x["donor"].update(actionAuthority="CAB_ONLY"),
        lambda x: x["donor"].update(evidenceRefs=[]),
        lambda x: x["warning"].update(readToEndRequired=False),
        lambda x: x["warning"].update(grantsActionAuthority=True),
        lambda x: x["safety"].update(protectionReset=True),
        lambda x: x["emergency"].update(exactProcedureVerified=True),
        lambda x: x["emergency"].update(emergencyActionAuthorized=True),
        lambda x: x["emergency"].update(historicalThresholdApplicable=True),
        lambda x: x["emergency"].update(sourceBound=False),
        lambda x: x["versions"]["SHORT"]["nodes"][0]["responses"].update(UNKNOWN="s2"),
        lambda x: x["versions"]["DETAILED"]["nodes"][0]["responses"].update(YES="d2"),
        lambda x: x["versions"]["SHORT"]["nodes"][6].update(type="OBSERVATION_REPORT"),
        lambda x: x["versions"]["DETAILED"]["nodes"][1].update(permittedAction=True),
        lambda x: x["versions"]["DETAILED"]["nodes"][3].update(causeConfirmed=True),
        lambda x: x["extensions"][0].update(executable=True),
        lambda x: x["extensions"][1]["visibility"].update(warningAcknowledgedRequired=False),
        lambda x: x["extensions"][2].update(procedureSteps=["danger"]),
        lambda x: x["sources"][5].update(authority="ACTION_AUTHORIZED"),
        lambda x: x["crossScenarioBoundaries"].pop(),
    ]
    for n, mutate in enumerate(mutations, 1):
        candidate = copy.deepcopy(c)
        mutate(candidate)
        try:
            check(candidate, index, pack)
        except (AssertionError, KeyError, StopIteration):
            continue
        raise AssertionError(f"negative mutation escaped: {n}")
    return len(mutations)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative", action="store_true")
    args = parser.parse_args()
    c, i, k = load(C), load(I), load(K)
    check(c, i, k)
    print("CHME3_003_EMERGENCY_BOUND_PASS")
    if args.negative:
        print("CHME3_003_NEGATIVE_PASS", negatives(c, i, k))
