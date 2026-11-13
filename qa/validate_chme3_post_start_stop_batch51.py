#!/usr/bin/env python3
"""CHME3-DIAG-002 source-bound research-only graph, safety and negative gate."""
import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
C = "content-packs/diesel/chme3-family/diagnostics/authoring/chme3-diag-002-post-start-stop.research.json"
I = "content-packs/diesel/chme3-family/migration/diagnostic-source-index.json"
K = "content-packs/diesel/chme3-family/diagnostics/recommended/diagnostics-01.pack.json"
PIN = "3176d6ee228f0ed4b78371f45209e10c1c724eff"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def graph(nodes, start, source_ids):
    lookup = {n["id"]: n for n in nodes}
    assert len(lookup) == len(nodes) and start in lookup
    seen, todo = set(), [start]
    while todo:
        key = todo.pop()
        assert key in lookup
        if key in seen:
            continue
        seen.add(key)
        n = lookup[key]
        assert n["type"] in ("QUESTION", "OBSERVATION_REPORT", "STOP")
        assert n["permittedAction"] is False
        assert n["sourceRefs"] and set(n["sourceRefs"]) <= source_ids
        if n["type"] == "QUESTION":
            assert set(n["responses"]) == {"YES", "NO", "UNKNOWN"}
            assert lookup[n["responses"]["UNKNOWN"]]["type"] == "STOP"
        else:
            assert n["responses"] == {}
            assert n["causeConfirmed"] is False
        todo.extend(n["responses"].values())
    assert seen == set(lookup)


def check(c, index, pack):
    assert c["schemaVersion"] == "diagnostic-research-candidate/1"
    assert c["originalId"] == "CHME3-DIAG-002"
    assert c["scenarioId"] == "chme3.diagnostics.chme3-diag-002"
    donor = c["donor"]
    assert donor["repository"] == "DomEnota-hub/Test-"
    assert donor["commit"] == index["donorCommit"] == PIN
    assert donor["documentPath"] == "docs/locomotives/chme3/diagnostics_powerplant_pass3.json"
    assert donor["documentPointer"] == "/scenarios/1"
    assert donor["documentBlob"] == "63988703bb795e82f40335a756b8b9bd3cad8e0a"
    assert donor["gzipIndependentlyDecoded"] is False
    assert donor["relation"] == "ID_TITLE_PROFILE_ONLY_NOT_GRAPH_EQUIVALENCE"
    document = next(x for x in index["documents"] if x["sourcePath"] == donor["documentPath"])
    assert document["sourceBlobSha"] == donor["documentBlob"]
    source = document["sourceObject"]["scenarios"][1]
    assert (source["id"], source["title"], source["riskClass"]) == (c["originalId"], c["title"], donor["riskClass"])
    assert source["profiles"] == ["ЧМЭ3", "ЧМЭ3Т", "ЧМЭ3Э"]
    assert source["equipmentIds"] == donor["equipmentIds"]
    assert source["evidenceRefs"] == donor["evidenceRefs"]
    assert source["evidenceStatus"] == donor["evidenceStatus"] == "FIELD_PRACTICE_WITH_CASE_DATA"
    match = next(x for x in index["matches"] if x["sourceId"] == c["originalId"])
    assert match["sourcePointer"] == donor["documentPointer"]
    assert (match["canonicalId"], match["canonicalPack"]) == (c["scenarioId"], donor["canonicalPack"])
    entry = next(x for x in pack["entries"] if x["id"] == c["scenarioId"])
    assert entry["title"] == c["title"] and entry["publicationStatus"] == "CANDIDATE"
    assert donor["gzipBlob"] == entry["sourceObject"]["sourceBlobSha"]
    assert set(entry["applicability"]["variantIds"]) == set(c["applicability"]["possibleVariants"]) == {"chme3", "chme3t", "chme3e"}
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
    assert {x["originalId"] for x in c["crossScenarioBoundaries"]} == {
        "CHME3-DIAG-001", "CHME3-DIAG-003", "CHME3-DIAG-006"
    }
    sources = c["sources"]
    source_ids = {x["id"] for x in sources}
    assert source_ids == {"DOC", "PACK", "N38", "N15", "FIELD"}
    assert all(x["currentVerified"] is False and x["installedProfileVerified"] is False for x in sources)
    assert all(x["authority"] != "ACTION_AUTHORIZED" for x in sources)
    assert next(x for x in sources if x["id"] == "FIELD")["authority"] == "HYPOTHESIS_ONLY"
    assert next(x for x in sources if x["id"] == "N38")["kind"] == "HISTORICAL_TRAINING"
    assert len(c["versions"]["SHORT"]["nodes"]) == 8
    assert len(c["versions"]["DETAILED"]["nodes"]) == 12
    for version in ("SHORT", "DETAILED"):
        v = c["versions"][version]
        graph(v["nodes"], v["startNodeId"], source_ids)
    assert len(c["extensions"]) == 5
    assert {e["id"] for e in c["extensions"]} == {"timing", "fuel", "governor", "oil", "field"}
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


def negatives(c, index, pack):
    mutations = [
        lambda x: x.update(runtimeImport=True),
        lambda x: x.update(executable=True),
        lambda x: x.update(actionAuthorityGranted=True),
        lambda x: x.update(sourceAuthorityVerified=True),
        lambda x: x.update(humanSafetyReviewPassed=True),
        lambda x: x.update(publicationStatus="PUBLISHED"),
        lambda x: x["applicability"].update(confirmedVariant="chme3e"),
        lambda x: x["applicability"].update(unknownProfile="ALLOW"),
        lambda x: x["donor"].update(commit="HEAD"),
        lambda x: x["donor"].update(documentPointer="/scenarios/0"),
        lambda x: x["donor"].update(evidenceRefs=[]),
        lambda x: x["warning"].update(readToEndRequired=False),
        lambda x: x["warning"].update(grantsActionAuthority=True),
        lambda x: x["safety"].update(protectionReset=True),
        lambda x: x["versions"]["SHORT"]["nodes"][0]["responses"].update(UNKNOWN="s3"),
        lambda x: x["versions"]["DETAILED"]["nodes"][0]["responses"].update(YES="absent"),
        lambda x: x["versions"]["SHORT"]["nodes"][1].update(permittedAction=True),
        lambda x: x["versions"]["DETAILED"]["nodes"][3].update(causeConfirmed=True),
        lambda x: x["extensions"][0].update(executable=True),
        lambda x: x["extensions"][1]["visibility"].update(warningAcknowledgedRequired=False),
        lambda x: x["extensions"][2].update(procedureSteps=["danger"]),
        lambda x: x["sources"][-1].update(authority="ACTION_AUTHORIZED"),
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
    print("CHME3_002_PASS")
    if args.negative:
        print("CHME3_002_NEGATIVE_PASS", negatives(c, i, k))
