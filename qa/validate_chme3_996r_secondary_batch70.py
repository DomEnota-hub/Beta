#!/usr/bin/env python3
"""CHME3 batch70: five distinct pinned 996/r-secondary candidates, safety gates and mutation QA.

The donor and its original research-only actions are never imported into runtime.
This validator compares preserved donor identity and metadata, NOT the undecoded gzip graph.
"""
import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "content-packs/diesel/chme3-family/"
DOC = "docs/locomotives/chme3/diagnostics_996r_detail_pass3.json"
PACK = BASE + "diagnostics/recommended/diagnostics-03.pack.json"
FILES = {
    321: BASE + "diagnostics/authoring/chme3-diag-321-rv2-kd2-not-engaging.research.json",
    322: BASE + "diagnostics/authoring/chme3-diag-322-even-controller-positions-rpm.research.json",
    323: BASE + "diagnostics/authoring/chme3-diag-323-ru5-start-first-position-no-traction.research.json",
    324: BASE + "diagnostics/authoring/chme3-diag-324-start-button-hold-only.research.json",
    325: BASE + "diagnostics/authoring/chme3-diag-325-main-loop-side-louvers-vpzh1.research.json",
}
REFS = {"DOC", "PACK", "SECONDARY", "HISTORICAL", "FIELD", "CURRENT_GAP"}
DISCREPANCIES = {
    "DONOR_vs_RESEARCH", "SECONDARY_996R_vs_PRIMARY", "HISTORICAL_1996_vs_CURRENT",
    "GZIP_vs_PINNED_JSON", "SERIAL_VARIANT", "FIELD_vs_AUTHORIZED", "SAFETY_GATE",
}
WARN = {
    "extendedHiddenByDefault": True, "readToEndRequired": True,
    "separateAcknowledgmentRequired": True, "grantsActionAuthority": False,
}
VIS = {
    "hiddenByDefault": True, "warningReadToEndRequired": True,
    "warningAcknowledgedRequired": True,
}
def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def graph(g, count):
    nodes = g["nodes"]
    assert len(nodes) == count
    by = {x["id"]: x for x in nodes}
    assert len(by) == count
    seen, todo = set(), [g["startNodeId"]]
    while todo:
        key = todo.pop()
        if key in seen:
            continue
        node = by[key]
        seen.add(key)
        assert node["sourceRefs"] and set(node["sourceRefs"]) <= REFS
        assert node["permittedAction"] is False and "procedureSteps" not in node
        assert node["type"] in ("QUESTION", "OBSERVATION_REPORT", "STOP")
        if node["type"] == "QUESTION":
            assert set(node["responses"]) == {"YES", "NO", "UNKNOWN"}
            assert by[node["responses"]["UNKNOWN"]]["type"] == "STOP"
            todo.extend(node["responses"].values())
        else:
            assert node["responses"] == {} and node["causeConfirmed"] is False
    assert seen == set(by)

def check(c, n, index, pack):
    assert n in FILES
    source = next(x for x in index["documents"] if x["sourcePath"] == DOC)
    original = source["sourceObject"]["scenarios"][n - 321]
    match = next(x for x in index["matches"] if x["sourceId"] == original["id"])
    entry = next(x for x in pack["entries"] if x["id"] == match["canonicalId"])
    donor, appl = c["donor"], c["applicability"]
    assert c["schemaVersion"] == "diagnostic-research-candidate/1" and c["batch"] == 70
    assert c["originalId"] == original["id"] == f"CHME3-DIAG-{n}"
    assert c["title"] == original["title"] == entry["title"]
    assert c["scenarioId"] == donor["canonicalId"] == match["canonicalId"] == entry["id"]
    assert donor["repository"] == "DomEnota-hub/Test-"
    assert donor["commit"] == index["donorCommit"] == "3176d6ee228f0ed4b78371f45209e10c1c724eff"
    assert donor["documentPath"] == match["sourcePath"] == DOC
    assert donor["documentPointer"] == match["sourcePointer"] == f"/scenarios/{n-321}"
    assert donor["documentBlob"] == source["sourceBlobSha"] == "f29c287c2eae1fb60e0cac61cab098fa8cae3c0f"
    assert donor["canonicalPack"] == match["canonicalPack"] == PACK
    assert donor["gzipBlob"] == entry["sourceObject"]["sourceBlobSha"] == "6a6068ad1ea54cb964b65a10ecf5c2425b2276e8"
    assert donor["gzipIndependentlyDecoded"] is False
    assert donor["relation"] == "ID_TITLE_PROFILE_ONLY_NOT_GRAPH_EQUIVALENCE"
    for key in ("riskClass", "actionAuthority", "evidenceStatus", "evidenceRefs", "equipmentIds"):
        assert donor[key] == original[key]
    assert original["profiles"] == ["ЧМЭ3", "ЧМЭ3Т", "ЧМЭ3Э"]
    assert set(appl["possibleVariants"]) == set(entry["applicability"]["variantIds"]) == {"chme3", "chme3t", "chme3e"}
    assert appl["confirmedVariant"] is None and appl["installedSchemeVerified"] is False
    assert appl["unknownProfile"] == "BLOCKED"
    assert c["publicationStatus"] == entry["publicationStatus"] == "CANDIDATE"
    assert c["actionDisposition"] == original["actionAuthority"] == "SOURCE_AND_PROFILE_REQUIRED"
    for key in ("runtimeImport", "executable", "actionAuthorityGranted", "sourceAuthorityVerified", "humanSafetyReviewPassed"):
        assert c[key] is False
    assert c["warning"] == WARN
    assert len(c["safety"]) >= 16 and all(value is False for value in c["safety"].values())
    sources = c["sources"]
    assert len(sources) == len(REFS) and {x["id"] for x in sources} == REFS
    assert next(x for x in sources if x["id"] == "SECONDARY")["kind"] == "SECONDARY_996R_UNVERIFIED_PRIMARY"
    assert next(x for x in sources if x["id"] == "SECONDARY")["ref"] == original["evidenceRefs"][0]
    assert next(x for x in sources if x["id"] == "HISTORICAL")["kind"] == "HISTORICAL_TRAINING"
    assert all(x["currentVerified"] is False and x["installedProfileVerified"] is False for x in sources)
    assert all(x["authority"] in ("INFORMATION_ONLY", "HYPOTHESIS_ONLY") for x in sources)
    assert len(c["sourceDiscrepancies"]) == len(DISCREPANCIES)
    assert {x["source"] for x in c["sourceDiscrepancies"]} == DISCREPANCIES
    assert all(x["status"] not in ("VERIFIED", "APPROVED") for x in c["sourceDiscrepancies"])
    assert len(c["openGaps"]) >= 12
    boundaries = c["crossScenarioBoundaries"]
    assert len(boundaries) == 4 and len({x["originalId"] for x in boundaries}) == 4
    assert c["originalId"] not in {x["originalId"] for x in boundaries}
    ids = {x["sourceId"] for x in index["matches"]}
    assert all(x["originalId"] in ids and x["boundary"] for x in boundaries)
    assert c["deviceQA"] == {
        "status": "NOT_RUN_DEFERRED",
        "registry": "docs/diagnostics/DIAGNOSTIC_FINAL_DEVICE_QA_DEFERRED_2026-11-04.md",
    }
    assert c["secondaryRiskNote"] and "runtime" not in c["secondaryRiskNote"].lower()
    for mode, count in (("SHORT", 8), ("DETAILED", 12)):
        g = c["versions"][mode]
        graph(g, count)
        first = g["nodes"][0]
        assert first["responses"]["NO"] == first["responses"]["UNKNOWN"] == "stop-safety"
        assert first["responses"]["YES"] == ("s2" if mode == "SHORT" else "d2")
        contracts = c["branchContracts"][mode]
        assert set(contracts) == {x["id"] for x in g["nodes"] if x["type"] == "QUESTION"}
        for node in g["nodes"]:
            if node["type"] == "QUESTION":
                assert contracts[node["id"]] == node["responses"]
    assert c["versions"]["SHORT"]["nodes"][2]["responses"] == {
        "YES": "obs-b", "NO": "obs-c", "UNKNOWN": "stop-unknown"
    }
    assert c["versions"]["DETAILED"]["nodes"][2]["responses"] == {
        "YES": "obs-b", "NO": "d4", "UNKNOWN": "stop-unknown"
    }
    assert c["versions"]["DETAILED"]["nodes"][3]["responses"] == {
        "YES": "obs-d", "NO": "d5", "UNKNOWN": "stop-unknown"
    }
    assert c["versions"]["DETAILED"]["nodes"][4]["responses"] == {
        "YES": "obs-e", "NO": "obs-c", "UNKNOWN": "stop-unknown"
    }
    exts = c["extensions"]
    assert len(exts) == 5 and len({x["id"] for x in exts}) == 5
    assert len({x["title"] for x in exts}) == 5
    for ext in exts:
        assert ext["sourceId"] == "SECONDARY" and ext["sourceStatus"] == "SECONDARY_996R_NOT_PRIMARY"
        assert ext["displayMode"] == "EXTENDED_ONLY" and ext["visibility"] == VIS
        assert ext["actionDisposition"] == "INFORMATION_ONLY"
        assert ext["executable"] is False and ext["actionAuthorityGranted"] is False
        assert ext["procedureSteps"] == []
        graph({"startNodeId": ext["nodes"][0]["id"], "nodes": ext["nodes"]}, 4)
    # No original research-only unsafe procedure text or exact jumper wiring copied into candidate.
    assert "202 и 261" not in json.dumps(c, ensure_ascii=False)
    assert "208 и 247" not in json.dumps(c, ensure_ascii=False)

def negative(c, n, index, pack):
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
        lambda x: x["donor"].update(documentBlob="bad"),
        lambda x: x["donor"].update(documentPointer="/scenarios/0" if n != 321 else "/scenarios/1"),
        lambda x: x["donor"].update(gzipIndependentlyDecoded=True),
        lambda x: x["donor"].update(evidenceStatus="CURRENT_APPROVED"),
        lambda x: x["donor"].update(riskClass="LOW"),
        lambda x: x["donor"].update(equipmentIds=[]),
        lambda x: x["donor"].update(evidenceRefs=[]),
        lambda x: x["warning"].update(extendedHiddenByDefault=False),
        lambda x: x["warning"].update(readToEndRequired=False),
        lambda x: x["warning"].update(separateAcknowledgmentRequired=False),
        lambda x: x["warning"].update(grantsActionAuthority=True),
        lambda x: x["safety"].update(temporaryJumper=True),
        lambda x: x["safety"].update(manualContactorOperation=True),
        lambda x: x["safety"].update(mechanicalFixation=True),
        lambda x: x["versions"]["SHORT"]["nodes"][0]["responses"].update(UNKNOWN="s2"),
        lambda x: x["versions"]["SHORT"]["nodes"][0]["responses"].update(NO="s2"),
        lambda x: x["versions"]["DETAILED"]["nodes"][0].update(permittedAction=True),
        lambda x: x["versions"]["DETAILED"]["nodes"][1]["responses"].update(UNKNOWN="d3"),
        lambda x: x["versions"]["SHORT"]["nodes"][2]["responses"].update(YES="obs-c"),
        lambda x: x["versions"]["DETAILED"]["nodes"][3]["responses"].update(YES="obs-c"),
        lambda x: x["extensions"][0]["visibility"].update(warningAcknowledgedRequired=False),
        lambda x: x["extensions"][1].update(executable=True),
        lambda x: x["extensions"][2].update(procedureSteps=["unsafe"]),
        lambda x: x["extensions"][3]["nodes"][0]["responses"].update(UNKNOWN=x["extensions"][3]["nodes"][1]["id"]),
        lambda x: x["sources"][0].update(currentVerified=True),
        lambda x: x["sources"][0].update(installedProfileVerified=True),
        lambda x: x["sources"][2].update(kind="PRIMARY_CURRENT"),
        lambda x: x["sources"][2].update(authority="ACTION_AUTHORIZED"),
        lambda x: x["crossScenarioBoundaries"].pop(),
        lambda x: x["sourceDiscrepancies"].pop(),
        lambda x: x["openGaps"].clear(),
        lambda x: x["deviceQA"].update(status="PASS"),
        lambda x: x["versions"]["DETAILED"]["nodes"].pop(),
        lambda x: x["extensions"].pop(),
        lambda x: x["branchContracts"]["SHORT"]["s3"].update(YES="obs-c"),
        lambda x: x["versions"]["DETAILED"]["nodes"][2]["responses"].update(NO="obs-c"),
        lambda x: x["extensions"][4]["nodes"][1].update(causeConfirmed=True),
    ]
    for i, mutate in enumerate(mutations):
        y = copy.deepcopy(c)
        mutate(y)
        try:
            check(y, n, index, pack)
        except (AssertionError, KeyError, IndexError):
            continue
        raise AssertionError(f"Unsafe mutation accepted for {n}: {i}")
    return len(mutations)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative", action="store_true")
    args = parser.parse_args()
    index = read(BASE + "migration/diagnostic-source-index.json")
    pack = read(PACK)
    count = 0
    for n, path in FILES.items():
        candidate = read(path)
        check(candidate, n, index, pack)
        if args.negative:
            count += negative(candidate, n, index, pack)
        print("CHME3_BATCH70_SCENARIO_PASS", n)
    print("CHME3_BATCH70_PASS", "SCENARIOS", len(FILES), "NEGATIVE", count)

if __name__ == "__main__":
    main()
