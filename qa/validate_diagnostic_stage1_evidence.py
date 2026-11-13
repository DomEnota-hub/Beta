#!/usr/bin/env python3
"""Guard donor identity, variant applicability and extended safety at Stage 1.

Structural evidence validation only: NEVER author or approve any actions.
"""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
EXTENDED = {
    "chme3-family": "content-packs/diesel/chme3-family/diagnostics/extended/source-candidates.candidate.json",
    "tem2-family": "content-packs/diesel/tem2-family/diagnostics/extended/source-candidates.candidate.json",
}
PROFILE = {
    "chme3-family": "content-packs/diesel/chme3-family/migration/profile-source-index.json",
    "tem2-family": "content-packs/diesel/tem2-family/migration/profile-source-index.json",
}


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def ensure(condition, description):
    if not condition:
        raise AssertionError(description)


def classify(row, supported):
    versions = set(row["variantIds"])
    if row["extendedRecords"] and versions.isdisjoint(supported):
        return "CANDIDATE_PROFILE_DISJOINT"
    if row["extendedRecords"] and not versions.issubset(supported):
        return "CANDIDATE_PARTIAL_VARIANT"
    if row["extendedRecords"]:
        return "CANDIDATE_PROFILE_MATCH_EXACT"
    if row["extendedSourceStatus"] == "DONOR_REPORTS_NO_ADDITIONAL_METHOD":
        return "NO_ADDITIONAL_METHOD"
    return "NO_SCENARIO_EXTENDED_SOURCE"


def main():
    d = read("docs/data-migration/diagnostic-corpus-analysis.json")
    rows = d["rows"]
    ensure(d["donorCommit"] == DONOR, "Wrong pinned donor")
    ensure(len(rows) == d["uniqueScenarioCount"] == 340, "Scenario count mismatch")
    ensure(len({r["scenarioId"] for r in rows}) == len(rows), "Duplicate scenario ID")
    ensure(Counter(r["modelId"] for r in rows) == {
        "vl80s": 103, "ermak": 136, "chme3-family": 68, "tem2-family": 33,
    }, "Model boundaries changed")
    ensure(sum(r["graph"]["nodeCount"] for r in rows) == d["preservedGraphNodes"] == 3902,
           "Graph node total changed")
    ensure(all(not r["graph"]["invalidTargets"] and not r["graph"]["unreachableNodeIds"]
               for r in rows), "Invalid or unreachable graph target")
    candidates, bindings = {}, {}
    for model, path in EXTENDED.items():
        source = read(path)
        ensure(source["donorCommit"] == DONOR and
               source["publicationStatus"] == "CANDIDATE" and
               source["runtimeImport"] is False and
               source["actionAuthorityGranted"] is False and
               source["requiresWarnedExtendedMode"] is True,
               model + ": unsafe candidate authority")
        candidates[model] = {r["sourcePointer"]: r for r in source["rows"]}
        ensure(len(candidates[model]) == len(source["rows"]), model + ": duplicate pointer")
        bindings[model] = read(PROFILE[model])["profileBindings"]
    counts = Counter()
    for row in rows:
        key, model = row["scenarioId"], row["modelId"]
        ensure(row["graph"]["nodeCount"] > 0, key + ": empty graph")
        expected_status = "RUNTIME_GRAPH_PRESERVED" if model == "vl80s" else "CANDIDATE"
        ensure(row["publicationStatus"] == expected_status, key + ": publication status changed")
        variants = set()
        if model in EXTENDED:
            sources = candidates[model]
            if row["extendedRoutePointer"]:
                path, pointer = row["extendedRoutePointer"].split("#", 1)
                ensure(path == EXTENDED[model] and pointer in sources,
                       key + ": extended route pointer invalid")
                source_route = sources[pointer]["sourceObject"]
                ensure(source_route["standardScenarioId"] == row["sourceScenarioId"],
                       key + ": wrong donor scenario linked")
                expected_evidence = ("DONOR_CANDIDATE_RECORD" if
                                     source_route["hasExpandedEvidence"] else
                                     "DONOR_REPORTS_NO_ADDITIONAL_METHOD")
                ensure(row["extendedSourceStatus"] == expected_evidence,
                       key + ": donor claim changed")
            for evidence in row["extendedRecords"]:
                path, pointer = evidence["sourcePointer"].split("#", 1)
                ensure(path == EXTENDED[model] and pointer in sources,
                       key + ": evidence pointer invalid")
                source = sources[pointer]["sourceObject"]
                ensure(source["candidateId"] == evidence["candidateId"] and
                       source["standardScenarioId"] == row["sourceScenarioId"] and
                       sorted(source["profiles"]) == sorted(evidence["profiles"]) and
                       source["actionDisposition"] == evidence["actionDisposition"],
                       key + ": source evidence mismatch")
                ensure(source["actionDisposition"] in ("INFORMATION_ONLY", "PROHIBITED"),
                       key + ": unsupported executable action")
                safety = source["runtimeSafety"]
                ensure(safety["executable"] is False and
                       safety["currentAuthorityVerified"] is False and
                       safety["runtimeAuthorityUpgradeAllowed"] is False,
                       key + ": donor candidate elevated to runtime action")
                for profile in evidence["profiles"]:
                    ensure(profile in bindings[model], key + ": unknown extended profile")
                    variants.add(bindings[model][profile])
            ensure(set(row["extendedRecordVariantIds"]) == variants,
                   key + ": profile mapping lost")
            ensure(set(row["entryVariantsWithoutExtendedRecord"]) ==
                   set(row["variantIds"]) - variants,
                   key + ": unsubstantiated variant assigned")
        else:
            ensure(not row["extendedRecords"], key + ": unreviewed extension added")
        category = classify(row, variants)
        ensure(category == row["reviewClass"], key + ": incorrect source class")
        counts[category] += 1
    ensure(dict(counts) == d["reviewClassCounts"], "Extended-source totals changed")
    by_id = {r["scenarioId"]: r for r in rows}
    samples = {
        "chme3.diagnostics.chme3-diag-110": "CANDIDATE_PROFILE_MATCH_EXACT",
        "tem2.diagnostics.tem2-diag-002.tem2u": "CANDIDATE_PROFILE_DISJOINT",
        "tem2.diagnostics.tem2-diag-024.tem2": "CANDIDATE_PROFILE_MATCH_EXACT",
        "tem2.diagnostics.tem2-diag-024.tem2u": "CANDIDATE_PROFILE_MATCH_EXACT",
    }
    for key, classification in samples.items():
        ensure(by_id[key]["reviewClass"] == classification, key + ": trial guard changed")
    print("DIAGNOSTIC_STAGE1_EVIDENCE_GATE_PASS", len(rows), d["preservedGraphNodes"],
          dict(sorted(counts.items())))


if __name__ == "__main__":
    main()
