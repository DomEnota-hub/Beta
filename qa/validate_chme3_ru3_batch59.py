#!/usr/bin/env python3
"""Batch59: pinned CHME3-DIAG-103 RU3 provenance, graph safety, negative mutations."""
import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "content-packs/diesel/chme3-family/"
DOC = "docs/locomotives/chme3/diagnostics_electrical_control_pass3.json"
CANDIDATE = BASE + "diagnostics/authoring/chme3-diag-103-ru3-position-five.research.json"

def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def graph(g, count, refs):
    nodes = g["nodes"]
    assert len(nodes) == count
    by_id = {n["id"]: n for n in nodes}
    assert len(by_id) == count
    visited, todo = set(), [g["startNodeId"]]
    while todo:
        nid = todo.pop()
        if nid in visited:
            continue
        n = by_id[nid]
        visited.add(nid)
        assert n["permittedAction"] is False
        assert n["sourceRefs"] and set(n["sourceRefs"]) <= refs
        assert "procedureSteps" not in n
        assert n["type"] in ("QUESTION", "OBSERVATION_REPORT", "STOP")
        if n["type"] == "QUESTION":
            assert set(n["responses"]) == {"YES", "NO", "UNKNOWN"}
            assert by_id[n["responses"]["UNKNOWN"]]["type"] == "STOP"
            todo.extend(n["responses"].values())
        else:
            assert n["responses"] == {}
            assert n["causeConfirmed"] is False
    assert visited == set(by_id)

def check(c, idx, pack):
    source_doc = next(d for d in idx["documents"] if d["sourcePath"] == DOC)
    original = source_doc["sourceObject"]["scenarios"][2]
    match = next(x for x in idx["matches"] if x["sourceId"] == "CHME3-DIAG-103")
    entry = next(x for x in pack["entries"] if x["id"] == match["canonicalId"])
    donor, app = c["donor"], c["applicability"]
    assert c["schemaVersion"] == "diagnostic-research-candidate/1"
    assert c["batch"] == 59
    assert c["originalId"] == original["id"] == "CHME3-DIAG-103"
    assert c["title"] == original["title"] == entry["title"]
    assert c["scenarioId"] == donor["canonicalId"] == match["canonicalId"] == entry["id"]
    assert donor["repository"] == "DomEnota-hub/Test-"
    assert donor["commit"] == idx["donorCommit"] == "3176d6ee228f0ed4b78371f45209e10c1c724eff"
    assert donor["documentPath"] == DOC
    assert donor["documentPointer"] == match["sourcePointer"] == "/scenarios/2"
    assert donor["documentBlob"] == source_doc["sourceBlobSha"] == "41d241cb0b58e5657ef0d6210e7b272d44df52d0"
    assert donor["canonicalPack"] == match["canonicalPack"] == BASE + "diagnostics/recommended/diagnostics-01.pack.json"
    assert donor["gzipBlob"] == entry["sourceObject"]["sourceBlobSha"] == "6a6068ad1ea54cb964b65a10ecf5c2425b2276e8"
    assert donor["gzipIndependentlyDecoded"] is False
    assert donor["relation"] == "ID_TITLE_PROFILE_ONLY_NOT_GRAPH_EQUIVALENCE"
    for key in ("riskClass", "actionAuthority", "evidenceStatus", "evidenceRefs", "equipmentIds"):
        assert donor[key] == original[key]
    assert original["profiles"] == ["ЧМЭ3", "ЧМЭ3Т", "ЧМЭ3Э"]
    assert set(app["possibleVariants"]) == set(entry["applicability"]["variantIds"]) == {"chme3", "chme3t", "chme3e"}
    assert app["confirmedVariant"] is None and app["installedSchemeVerified"] is False
    assert app["unknownProfile"] == "BLOCKED"
    assert c["publicationStatus"] == entry["publicationStatus"] == "CANDIDATE"
    assert c["actionDisposition"] == original["actionAuthority"] == "SOURCE_AND_PROFILE_REQUIRED"
    for key in ("runtimeImport", "executable", "actionAuthorityGranted", "sourceAuthorityVerified", "humanSafetyReviewPassed"):
        assert c[key] is False
    assert c["warning"] == {
        "extendedHiddenByDefault": True, "readToEndRequired": True,
        "separateAcknowledgmentRequired": True, "grantsActionAuthority": False,
    }
    assert c["safety"] and all(v is False for v in c["safety"].values())
    refs = {s["id"] for s in c["sources"]}
    assert len(refs) == len(c["sources"]) and {"DOC", "PACK", "N74", "N67", "SECONDARY", "LOCAL"} <= refs
    for s in c["sources"]:
        assert s["currentVerified"] is False and s["installedProfileVerified"] is False
        assert s["authority"] in ("INFORMATION_ONLY", "HYPOTHESIS_ONLY")
    assert next(s for s in c["sources"] if s["id"] == "N74")["profiles"] == ["chme3"]
    assert set(next(s for s in c["sources"] if s["id"] == "N67")["profiles"]) == {"chme3t", "chme3e"}
    assert next(s for s in c["sources"] if s["id"] == "SECONDARY")["authority"] == "HYPOTHESIS_ONLY"
    assert len(c["sourceDiscrepancies"]) == 2
    assert "оборотов" in c["sourceDiscrepancies"][0] and "возбуждением" in c["sourceDiscrepancies"][0]
    assert len(c["openGaps"]) >= 9 and c["deviceQA"]["status"] == "NOT_RUN_DEFERRED"
    assert len(c["crossScenarioBoundaries"]) == 4
    assert len({x["originalId"] for x in c["crossScenarioBoundaries"]}) == 4
    assert {"CHME3-DIAG-102", "CHME3-DIAG-104"} <= {x["originalId"] for x in c["crossScenarioBoundaries"]}
    graph(c["versions"]["SHORT"], 8, refs)
    graph(c["versions"]["DETAILED"], 12, refs)
    for mode in ("SHORT", "DETAILED"):
        first = c["versions"][mode]["nodes"][0]
        assert first["responses"]["NO"] == first["responses"]["UNKNOWN"] == "stop-safety"
    assert len(c["extensions"]) == 5
    assert len({x["id"] for x in c["extensions"]}) == 5
    for x in c["extensions"]:
        assert x["sourceId"] in refs and x["displayMode"] == "EXTENDED_ONLY"
        assert x["visibility"] == {
            "hiddenByDefault": True, "warningReadToEndRequired": True,
            "warningAcknowledgedRequired": True,
        }
        assert x["actionDisposition"] == "INFORMATION_ONLY"
        assert x["executable"] is False and x["actionAuthorityGranted"] is False
        assert x["procedureSteps"] == []
        graph({"startNodeId": x["nodes"][0]["id"], "nodes": x["nodes"]}, 4, refs)

def negative(c, idx, pack):
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
        lambda x: x["warning"].update(extendedHiddenByDefault=False),
        lambda x: x["warning"].update(readToEndRequired=False),
        lambda x: x["warning"].update(separateAcknowledgmentRequired=False),
        lambda x: x["warning"].update(grantsActionAuthority=True),
        lambda x: x["safety"].update(temporaryJumper=True),
        lambda x: x["safety"].update(liveElectricalMeasurements=True),
        lambda x: x["versions"]["SHORT"]["nodes"][0]["responses"].update(UNKNOWN="s2"),
        lambda x: x["versions"]["DETAILED"]["nodes"][0].update(permittedAction=True),
        lambda x: x["versions"]["DETAILED"]["nodes"][1]["responses"].update(UNKNOWN="d3"),
        lambda x: x["extensions"][0]["visibility"].update(warningAcknowledgedRequired=False),
        lambda x: x["extensions"][1].update(executable=True),
        lambda x: x["extensions"][2].update(procedureSteps=["unsafe"]),
        lambda x: x["sources"][0].update(currentVerified=True),
        lambda x: x["crossScenarioBoundaries"].pop(),
        lambda x: x["sources"][-1].update(id="DOC"),
        lambda x: x["sourceDiscrepancies"].pop(),
        lambda x: x["sources"][2].update(profiles=["chme3", "chme3t", "chme3e"]),
    ]
    for i, mutate in enumerate(mutations):
        modified = copy.deepcopy(c)
        mutate(modified)
        try:
            check(modified, idx, pack)
        except (AssertionError, KeyError):
            continue
        raise AssertionError("unsafe mutation accepted: %d" % i)
    return len(mutations)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--negative", action="store_true")
    args = ap.parse_args()
    idx = read(BASE + "migration/diagnostic-source-index.json")
    pack = read(BASE + "diagnostics/recommended/diagnostics-01.pack.json")
    c = read(CANDIDATE)
    check(c, idx, pack)
    total = negative(c, idx, pack) if args.negative else 0
    print("CHME3_BATCH59_RU3_PASS", "SCENARIOS", 1, "NEGATIVE", total)

if __name__ == "__main__":
    main()
