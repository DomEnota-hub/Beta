#!/usr/bin/env python3
"""CHME3 batch60: pinned source parity, closed safety gates and mutation QA."""
import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "content-packs/diesel/chme3-family/"
DOC = "docs/locomotives/chme3/diagnostics_electrical_control_pass3.json"
FILES = {
    104: BASE + "diagnostics/authoring/chme3-diag-104-train-contactor-isolation.research.json",
    105: BASE + "diagnostics/authoring/chme3-diag-105-field-weakening-transition.research.json",
}

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

def check(c, n, idx, pack):
    original_doc = next(d for d in idx["documents"] if d["sourcePath"] == DOC)
    original = original_doc["sourceObject"]["scenarios"][n - 101]
    match = next(m for m in idx["matches"] if m["sourceId"] == "CHME3-DIAG-%d" % n)
    entry = next(e for e in pack["entries"] if e["id"] == match["canonicalId"])
    d, a = c["donor"], c["applicability"]
    assert c["schemaVersion"] == "diagnostic-research-candidate/1"
    assert c["batch"] == 60
    assert c["originalId"] == original["id"] == "CHME3-DIAG-%d" % n
    assert c["title"] == original["title"] == entry["title"]
    assert c["scenarioId"] == d["canonicalId"] == match["canonicalId"] == entry["id"]
    assert d["repository"] == "DomEnota-hub/Test-"
    assert d["commit"] == idx["donorCommit"] == "3176d6ee228f0ed4b78371f45209e10c1c724eff"
    assert d["documentPath"] == DOC
    assert d["documentPointer"] == match["sourcePointer"] == "/scenarios/%d" % (n - 101)
    assert d["documentBlob"] == original_doc["sourceBlobSha"] == "41d241cb0b58e5657ef0d6210e7b272d44df52d0"
    assert d["canonicalPack"] == match["canonicalPack"] == BASE + "diagnostics/recommended/diagnostics-01.pack.json"
    assert d["gzipBlob"] == entry["sourceObject"]["sourceBlobSha"] == "6a6068ad1ea54cb964b65a10ecf5c2425b2276e8"
    assert d["gzipIndependentlyDecoded"] is False
    assert d["relation"] == "ID_TITLE_PROFILE_ONLY_NOT_GRAPH_EQUIVALENCE"
    for key in ("riskClass", "actionAuthority", "evidenceStatus", "evidenceRefs", "equipmentIds"):
        assert d[key] == original[key]
    assert original["profiles"] == ["ЧМЭ3", "ЧМЭ3Т", "ЧМЭ3Э"]
    assert set(a["possibleVariants"]) == set(entry["applicability"]["variantIds"]) == {"chme3", "chme3t", "chme3e"}
    assert a["confirmedVariant"] is None and a["installedSchemeVerified"] is False
    assert a["unknownProfile"] == "BLOCKED"
    assert c["publicationStatus"] == entry["publicationStatus"] == "CANDIDATE"
    assert c["actionDisposition"] == original["actionAuthority"] == "SOURCE_AND_PROFILE_REQUIRED"
    for key in ("runtimeImport", "executable", "actionAuthorityGranted", "sourceAuthorityVerified", "humanSafetyReviewPassed"):
        assert c[key] is False
    assert c["warning"] == {
        "extendedHiddenByDefault": True,
        "readToEndRequired": True,
        "separateAcknowledgmentRequired": True,
        "grantsActionAuthority": False,
    }
    assert c["safety"] and all(v is False for v in c["safety"].values())
    refs = {s["id"] for s in c["sources"]}
    assert len(refs) == len(c["sources"]) and {"DOC", "PACK", "N61", "N67"} <= refs
    assert len(c["sources"]) >= 6
    for s in c["sources"]:
        assert s["currentVerified"] is False and s["installedProfileVerified"] is False
        assert s["authority"] in ("INFORMATION_ONLY", "HYPOTHESIS_ONLY")
    assert next(s for s in c["sources"] if s["id"] == "N61")["profiles"] == ["chme3"]
    assert set(next(s for s in c["sources"] if s["id"] == "N67")["profiles"]) == {"chme3t", "chme3e"}
    if n == 105:
        assert next(s for s in c["sources"] if s["id"] == "N74")["profiles"] == ["chme3"]
        assert next(s for s in c["sources"] if s["id"] == "N96")["profiles"] == ["chme3e"]
        assert next(s for s in c["sources"] if s["id"] == "SECONDARY")["authority"] == "HYPOTHESIS_ONLY"
    else:
        assert next(s for s in c["sources"] if s["id"] == "INDEX")["authority"] == "HYPOTHESIS_ONLY"
    assert len(c["crossScenarioBoundaries"]) >= 3
    assert len({x["originalId"] for x in c["crossScenarioBoundaries"]}) == len(c["crossScenarioBoundaries"])
    assert len(c["sourceDiscrepancies"]) == 2
    assert len(c["openGaps"]) >= 8
    assert c["deviceQA"]["status"] == "NOT_RUN_DEFERRED"
    assert c["deviceQA"]["registry"] == "docs/diagnostics/DIAGNOSTIC_FINAL_DEVICE_QA_DEFERRED_2026-11-04.md"
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
            "hiddenByDefault": True,
            "warningReadToEndRequired": True,
            "warningAcknowledgedRequired": True,
        }
        assert x["actionDisposition"] == "INFORMATION_ONLY"
        assert x["executable"] is False and x["actionAuthorityGranted"] is False
        assert x["procedureSteps"] == []
        graph({"startNodeId": x["nodes"][0]["id"], "nodes": x["nodes"]}, 4, refs)

def negative(c, n, idx, pack):
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
        lambda x: x["donor"].update(documentPointer="/scenarios/2"),
        lambda x: x["donor"].update(documentBlob="bad"),
        lambda x: x["donor"].update(gzipIndependentlyDecoded=True),
        lambda x: x["donor"].update(equipmentIds=[]),
        lambda x: x["donor"].update(evidenceRefs=[]),
        lambda x: x["donor"].update(riskClass="NORMAL_DIAGNOSTIC"),
        lambda x: x["warning"].update(extendedHiddenByDefault=False),
        lambda x: x["warning"].update(readToEndRequired=False),
        lambda x: x["warning"].update(separateAcknowledgmentRequired=False),
        lambda x: x["warning"].update(grantsActionAuthority=True),
        lambda x: x["safety"].update(temporaryJumper=True),
        lambda x: x["safety"].update(highVoltageIntervention=True),
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
    # Every mutation must be rejected; a silent pass is a safety regression.
    for i, change in enumerate(mutations):
        altered = copy.deepcopy(c)
        change(altered)
        try:
            check(altered, n, idx, pack)
        except (AssertionError, KeyError):
            continue
        raise AssertionError("unsafe mutation accepted: %d for %d" % (i, n))
    return len(mutations)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--negative", action="store_true")
    args = ap.parse_args()
    idx = read(BASE + "migration/diagnostic-source-index.json")
    pack = read(BASE + "diagnostics/recommended/diagnostics-01.pack.json")
    count = 0
    for n, path in FILES.items():
        candidate = read(path)
        check(candidate, n, idx, pack)
        if args.negative:
            count += negative(candidate, n, idx, pack)
    print("CHME3_BATCH60_PASS", "SCENARIOS", len(FILES), "NEGATIVE", count)

if __name__ == "__main__":
    main()
