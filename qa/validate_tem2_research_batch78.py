#!/usr/bin/env python3
"""Pinned TEM2/2U batch78 authoring identity, safety, graphs and mutation QA."""
import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "content-packs/diesel/tem2-family/diagnostics"
LINEAGE = json.loads((BASE / "stage3-source-lineage.json").read_text())
PACKS = [
    json.loads((BASE / f"recommended/diagnostics-0{i}.pack.json").read_text())
    for i in (1, 2)
]
FILES = {
    16: "tem2-diag-016-compressor-overpressure.research.json",
    17: "tem2-diag-017-compressor-low-output.research.json",
    18: "tem2-diag-018-brake-pressure-drift.research.json",
    19: "tem2-diag-019-independent-brake-no-apply.research.json",
    20: "tem2-diag-020-independent-brake-no-release.research.json",
}
REQUIRED_SOURCES = {"DOC", "PACK", "ARCHIVE", "FACTORY_U", "BRAKES_2026", "FIELD", "CURRENT_GAP"}
BLOCKED_VARIANTS = {"tem2t", "tem2um", "tem2a", "tem2um-1pd4a"}


def check(candidate, number):
    source = LINEAGE["scenarios"][number - 1]["sourceObject"]
    donor = candidate["donor"]
    app = candidate["applicability"]
    assert candidate["schemaVersion"] == "diagnostic-research-candidate/1"
    assert candidate["batch"] == 78
    assert candidate["originalId"] == source["id"] == f"TEM2-DIAG-{number:03d}"
    assert candidate["title"] == source["title"]
    assert donor["repository"] == "DomEnota-hub/Test-"
    assert donor["commit"] == "3176d6ee228f0ed4b78371f45209e10c1c724eff"
    assert donor["documentPath"] == "docs/locomotives/diesel/tem2-family/common/stage3_model.json"
    assert donor["documentPointer"] == f"/scenarios/{number - 1}"
    assert donor["documentBlob"] == "4234e401eb9d6ec03802669d0f74962cb23ea5c4"
    assert donor["lineageBlob"] == "24e617c3d5599cb96169f79d660200d6cd684fac"
    assert donor["canonicalPack"] == (
        "content-packs/diesel/tem2-family/diagnostics/recommended/"
        f"diagnostics-0{1 if number <= 14 else 2}.pack.json"
    )
    assert donor["originalGraphEquivalenceVerified"] is False
    for field in ("riskClass", "actionAuthority", "equipmentIds", "evidenceRefs", "schemeRefs"):
        assert donor[field] == source[field], (number, field)
    targets = LINEAGE["scenarios"][number - 1]["targets"]
    assert donor["targetMap"] == {t["variantId"]: t["canonicalId"] for t in targets}
    entries = [e for pack in PACKS for e in pack["entries"]
               if e["sourceObject"]["object"]["id"] == source["id"]]
    assert len(entries) == 1
    assert donor["sourceBlobShas"] == {
        e["id"]: e["sourceObject"]["sourceBlobSha"] for e in entries
    }
    for t in targets:
        assert any(e["id"] == t["canonicalId"]
                   and t["variantId"] in e["applicability"]["variantIds"]
                   for e in entries)
    assert app["possibleVariants"] == ["tem2", "tem2u"]
    assert app["profileIds"] == source["profileIds"]
    assert app["confirmedVariant"] is None
    assert app["installedSchemeVerified"] is False
    assert app["unknownProfile"] == "BLOCKED"
    assert set(app["excludedVariants"]) == BLOCKED_VARIANTS
    assert len(set(donor["targetMap"].values())) == 1
    assert all(x["authority"] == "INFORMATION_ONLY" for x in candidate["sources"][:5])
    assert candidate["sources"][4]["kind"] == "CURRENT_SECONDARY_IDENTITY_ONLY"
    assert candidate["publicationStatus"] == "CANDIDATE"
    assert candidate["actionDisposition"] == "TRIAGE_ONLY_NO_REPAIR"
    assert all(candidate[key] is False for key in (
        "runtimeImport", "executable", "actionAuthorityGranted",
        "sourceAuthorityVerified", "humanSafetyReviewPassed"
    ))
    assert len(candidate["safety"]) >= 16
    assert all(v is False for v in candidate["safety"].values())
    assert candidate["warning"] == {
        "extendedHiddenByDefault": True,
        "readToEndRequired": True,
        "separateAcknowledgmentRequired": True,
        "grantsActionAuthority": False,
    }
    assert candidate["deviceQA"]["status"] == "NOT_RUN_DEFERRED"
    assert candidate["deviceQA"]["emergencyInteractionRequired"] is False
    assert candidate["deviceQA"]["registry"] == (
        "docs/diagnostics/DIAGNOSTIC_FINAL_DEVICE_QA_DEFERRED_2026-11-04.md"
    )
    sources = candidate["sources"]
    assert {x["id"] for x in sources} == REQUIRED_SOURCES
    assert all(x["currentVerified"] is False
               and x["installedProfileVerified"] is False
               and x["authority"] in ("INFORMATION_ONLY", "HYPOTHESIS_ONLY")
               for x in sources)
    assert len(candidate["crossScenarioBoundaries"]) >= 3
    assert len(candidate["sourceDiscrepancies"]) >= 7
    assert len(candidate["openGaps"]) >= 8
    all_source_ids = {x["id"] for x in sources}
    assert set(candidate["versions"]) == {"SHORT", "DETAILED"}
    question_texts = {}
    for mode, expected_count, qcount in (("SHORT", 8, 3), ("DETAILED", 12, 5)):
        graph = candidate["versions"][mode]
        nodes = graph["nodes"]
        by_id = {n["id"]: n for n in nodes}
        assert len(nodes) == expected_count and len(by_id) == expected_count
        assert graph["startNodeId"] in by_id
        assert sum(n["type"] == "QUESTION" for n in nodes) == qcount
        assert sum(n["type"] == "STOP" for n in nodes) == 2
        assert all(n["permittedAction"] is False and n["sourceRefs"]
                   and set(n["sourceRefs"]) <= all_source_ids
                   and len(n["text"]) >= 20 for n in nodes)
        seen = set()
        todo = [graph["startNodeId"]]
        while todo:
            ident = todo.pop()
            assert ident in by_id
            if ident in seen:
                continue
            seen.add(ident)
            node = by_id[ident]
            if node["type"] == "QUESTION":
                assert set(node["responses"]) == {"YES", "NO", "UNKNOWN"}
                assert by_id[node["responses"]["UNKNOWN"]]["type"] == "STOP"
                todo.extend(node["responses"].values())
            else:
                assert node["type"] in ("STOP", "OBSERVATION_REPORT")
                assert node["responses"] == {}
                assert node["causeConfirmed"] is False
        assert seen == set(by_id), (number, mode, set(by_id) - seen)
        assert by_id[graph["startNodeId"]]["responses"]["NO"] == "stop-safety"
        assert by_id[graph["startNodeId"]]["responses"]["UNKNOWN"] == "stop-safety"
        assert "STOP" in by_id["stop-safety"]["text"]
        assert "STOP" in by_id["stop-unknown"]["text"]
        assert candidate["branchContracts"][mode] == {
            n["id"]: n["responses"] for n in nodes if n["type"] == "QUESTION"
        }
        question_texts[mode] = [n["text"] for n in nodes if n["type"] == "QUESTION"]
    assert question_texts["SHORT"][1:] == question_texts["DETAILED"][1:3]
    assert len(candidate["extensions"]) == 5
    assert len({e["title"] for e in candidate["extensions"]}) == 5
    for ext in candidate["extensions"]:
        assert ext["sourceId"] in all_source_ids
        assert ext["displayMode"] == "EXTENDED_ONLY"
        assert ext["actionDisposition"] == "INFORMATION_ONLY"
        assert ext["executable"] is False
        assert ext["actionAuthorityGranted"] is False
        assert ext["procedureSteps"] == []
        assert ext["visibility"] == {
            "hiddenByDefault": True,
            "warningReadToEndRequired": True,
            "warningAcknowledgedRequired": True,
        }
        nodes = ext["nodes"]
        assert len(nodes) == 4
        assert [x["type"] for x in nodes] == [
            "QUESTION", "OBSERVATION_REPORT", "OBSERVATION_REPORT", "STOP"
        ]
        assert set(nodes[0]["responses"]) == {"YES", "NO", "UNKNOWN"}
        assert nodes[0]["responses"]["UNKNOWN"] == nodes[3]["id"]
        assert all(x["permittedAction"] is False
                   and x["sourceRefs"] == [ext["sourceId"]] for x in nodes)


def mutations():
    return [
        lambda x: x.update(runtimeImport=True),
        lambda x: x.update(executable=True),
        lambda x: x.update(publicationStatus="PUBLISHED"),
        lambda x: x.update(actionAuthorityGranted=True),
        lambda x: x.update(sourceAuthorityVerified=True),
        lambda x: x.update(humanSafetyReviewPassed=True),
        lambda x: x["applicability"].update(unknownProfile="ALLOW"),
        lambda x: x["applicability"].update(confirmedVariant="tem2"),
        lambda x: x["warning"].update(readToEndRequired=False),
        lambda x: x["warning"].update(grantsActionAuthority=True),
        lambda x: x["safety"].update(temporaryJumper=True),
        lambda x: x["sources"][2].update(currentVerified=True),
        lambda x: x["donor"].update(commit="WRONG"),
        lambda x: x["donor"].update(documentBlob="WRONG"),
        lambda x: x["donor"].update(originalGraphEquivalenceVerified=True),
        lambda x: x["donor"].update(riskClass="WRONG"),
        lambda x: x["donor"]["targetMap"].update(tem2="WRONG"),
        lambda x: x["donor"]["sourceBlobShas"].clear(),
        lambda x: x["versions"]["SHORT"]["nodes"][0]["responses"].update(UNKNOWN="obs-a"),
        lambda x: x["versions"]["DETAILED"]["nodes"][1]["responses"].update(UNKNOWN="obs-a"),
        lambda x: x["versions"]["SHORT"]["nodes"][0].update(permittedAction=True),
        lambda x: x["versions"]["SHORT"]["nodes"][0]["responses"].update(YES="missing"),
        lambda x: x["extensions"][0]["visibility"].update(hiddenByDefault=False),
        lambda x: x["extensions"][0].update(executable=True),
        lambda x: x["extensions"][0]["nodes"][0]["responses"].update(UNKNOWN="e1-yes"),
        lambda x: x["deviceQA"].update(status="PASS"),
        lambda x: x["versions"]["DETAILED"]["nodes"].pop(),
        lambda x: x["extensions"].pop(),
        lambda x: x["sources"].pop(),
        lambda x: x["sourceDiscrepancies"].clear(),
        lambda x: x["openGaps"].clear(),
        lambda x: x["versions"]["SHORT"]["nodes"][3].update(causeConfirmed=True),
        lambda x: x["extensions"][0].update(procedureSteps=["unsafe"]),
        lambda x: x["applicability"].update(profileIds=["tem2-base"]),
        lambda x: x["crossScenarioBoundaries"].clear(),
        lambda x: x["versions"]["SHORT"]["nodes"][0].update(text=""),
        lambda x: x["sources"][4].update(currentVerified=True),
        lambda x: x["warning"].update(separateAcknowledgmentRequired=False),
        lambda x: x["applicability"].update(installedSchemeVerified=True),
        lambda x: x["donor"].update(actionAuthority="WRONG"),
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative", action="store_true")
    args = parser.parse_args()
    checked = 0
    fingerprints = set()
    for number, filename in FILES.items():
        candidate = json.loads((BASE / "authoring" / filename).read_text())
        check(candidate, number)
        fingerprint = tuple(n["text"] for n in candidate["versions"]["DETAILED"]["nodes"]
                            if n["type"] == "QUESTION")
        assert fingerprint not in fingerprints, "Duplicated diagnostic graph"
        fingerprints.add(fingerprint)
        if args.negative:
            for index, mutate in enumerate(mutations(), 1):
                changed = copy.deepcopy(candidate)
                mutate(changed)
                try:
                    check(changed, number)
                except (AssertionError, KeyError, IndexError, TypeError):
                    checked += 1
                else:
                    raise AssertionError(f"Escaped mutation: {number}, index {index}")
    print(f"TEM2 batch78 PASS: 5 unique IDs, SHORT8/DETAILED12, "
          f"25 separate extensions, negative checks {checked}")


if __name__ == "__main__":
    main()
