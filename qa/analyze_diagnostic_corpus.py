#!/usr/bin/env python3
"""Inventory the pinned diagnostic corpus without authoring or approving new routes."""
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
OUTPUT = ROOT / "docs/data-migration/diagnostic-corpus-analysis.json"
FAMILIES = {
    "ermak": "electric/ermak",
    "chme3-family": "diesel/chme3-family",
    "tem2-family": "diesel/tem2-family",
    "vl80s": "electric/vl80s",
}
EXTENDED = {
    "chme3-family": "content-packs/diesel/chme3-family/diagnostics/extended/source-candidates.candidate.json",
    "tem2-family": "content-packs/diesel/tem2-family/diagnostics/extended/source-candidates.candidate.json",
}


def read(path, root=ROOT):
    return json.loads((root / path).read_text())


def source_ids(refs):
    return sorted({r.get("sourceId") for r in refs if isinstance(r, dict) and r.get("sourceId")})


def graph_facts(graph):
    nodes = graph["nodes"]
    by_id = {node["id"]: node for node in nodes}
    assert len(by_id) == len(nodes) and graph["startNodeId"] in by_id
    targets = [target for node in nodes for target in (
        [node.get("nextNodeId"), node.get("uncertainNextNodeId")]
        + [choice.get("nextNodeId") for choice in node.get("choices", [])]
    ) if target and target != "__end__"]
    invalid = sorted(set(targets) - set(by_id))
    seen = {graph["startNodeId"]}
    queue = list(seen)
    while queue:
        node = by_id[queue.pop()]
        for target in ([node.get("nextNodeId"), node.get("uncertainNextNodeId")]
                       + [choice.get("nextNodeId") for choice in node.get("choices", [])]):
            if target in by_id and target not in seen:
                seen.add(target)
                queue.append(target)
    return {
        "nodeCount": len(nodes), "nodeTypes": dict(sorted(Counter(n["type"] for n in nodes).items())),
        "invalidTargets": invalid, "unreachableNodeIds": sorted(set(by_id) - seen),
    }


def vl80s_graph_facts(scenario):
    questions = scenario["questions"]
    by_key = {q["key"]: q for q in questions}
    assert len(by_key) == len(questions) and scenario["startQuestionKey"] in by_key
    targets = [v["nextQuestionKey"] for q in questions for v in q["responses"].values()]
    seen = {scenario["startQuestionKey"]}
    queue = list(seen)
    while queue:
        for response in by_key[queue.pop()]["responses"].values():
            target = response["nextQuestionKey"]
            if target in by_key and target not in seen:
                seen.add(target)
                queue.append(target)
    return {
        "nodeCount": len(questions), "nodeTypes": {"question": len(questions)},
        "invalidTargets": sorted(set(targets) - set(by_key) - {"__end__"}),
        "unreachableNodeIds": sorted(set(by_key) - seen),
    }


def extended_index(root=ROOT):
    index = {}
    for model, path in EXTENDED.items():
        data = read(path, root)
        assert data["donorCommit"] == DONOR and data["runtimeImport"] is False
        routes = {r["sourceId"]: r for r in data["rows"]
                  if r["sourcePointer"].startswith("/scenarioRouting/")}
        records = defaultdict(list)
        for record in data["rows"]:
            if record["sourcePointer"].startswith("/records/"):
                records[record["sourceObject"]["standardScenarioId"]].append(record)
        assert len(routes) == (68 if model == "chme3-family" else 24)
        index[model] = (path, routes, records)
    return index


def analyze(root=ROOT):
    extended = extended_index(root)
    profile_bindings = {
        model: read("content-packs/" + FAMILIES[model] + "/migration/profile-source-index.json", root)["profileBindings"]
        for model in EXTENDED
    }
    chme_sources = read("content-packs/diesel/chme3-family/migration/diagnostic-source-index.json", root)
    source_matches = defaultdict(list)
    for item in chme_sources["matches"]:
        source_matches[item["canonicalId"]].append({
            "sourcePath": item["sourcePath"], "sourcePointer": item["sourcePointer"],
            "relation": item["relation"],
        })
    tem2_lineage = read("content-packs/diesel/tem2-family/diagnostics/stage3-source-lineage.json", root)
    tem2_ids = {item["sourceObject"]["id"] for item in tem2_lineage["scenarios"]}
    assert len(tem2_ids) == 24

    rows = []
    for model, directory in FAMILIES.items():
        for pack in sorted((root / "content-packs" / directory / "diagnostics/recommended").glob("*.pack.json")):
            for entry in read(pack.relative_to(root), root)["entries"]:
                assert entry["owner"]["modelId"] == model
                if model == "vl80s":
                    continue  # the complete 103-route runtime source is inventoried below
                snapshot = entry["sourceObject"]
                original = snapshot["object"]
                refs = original.get("sourceRefs", [])
                source_ref_ids = source_ids(refs)
                issues = []
                if model == "ermak":
                    for ref in source_ref_ids:
                        if ref in {"ER-SRC-001", "ER-SRC-017", "ER-SRC-018", "ER-SRC-020", "ER-SRC-021"}:
                            issues.append("UNDEFINED_ERMAK_SOURCE_NUMBER:" + ref)
                        if ref == "ER-SRC-039":
                            issues.append("AMBIGUOUS_ERMAK_SOURCE_ID:ER-SRC-039")
                    if original["id"] == "ER-DIAG-136":
                        issues.append("ABSENT_FROM_ERMAK_STAGE7_INDEX")
                extended_status = "NO_PINNED_EXTENDED_ROUTING"
                route_pointer = None
                record_refs = []
                if model in extended:
                    extended_path, routes, records = extended[model]
                    route = routes.get(original["id"])
                    if route:
                        route_pointer = extended_path + "#" + route["sourcePointer"]
                        state = route["sourceObject"]
                        extended_status = ("DONOR_CANDIDATE_RECORD" if state["hasExpandedEvidence"]
                                           else "DONOR_REPORTS_NO_ADDITIONAL_METHOD")
                        record_refs = [{
                            "candidateId": r["sourceId"],
                            "sourcePointer": extended_path + "#" + r["sourcePointer"],
                            "profiles": r["sourceObject"].get("profiles", []),
                            "actionDisposition": r["sourceObject"]["actionDisposition"],
                        } for r in records.get(original["id"], [])]
                        assert bool(record_refs) == bool(state["hasExpandedEvidence"]), original["id"]
                    else:
                        issues.append("NO_DONOR_EXTENDED_ROUTING_FOR_SOURCE_ID")
                candidate_variants = sorted({profile_bindings[model][profile]
                    for record in record_refs for profile in record["profiles"]}) if model in extended else []
                entry_variants = entry["applicability"].get("variantIds", [])
                if record_refs and not set(candidate_variants) & set(entry_variants):
                    issues.append("EXTENDED_RECORD_PROFILE_DISJOINT_FROM_ENTRY")
                elif record_refs and set(entry_variants) - set(candidate_variants):
                    issues.append("EXTENDED_RECORD_COVERS_ONLY_SOME_ENTRY_VARIANTS")
                review_class = (
                    "CANDIDATE_PROFILE_DISJOINT" if "EXTENDED_RECORD_PROFILE_DISJOINT_FROM_ENTRY" in issues
                    else "CANDIDATE_PARTIAL_VARIANT" if "EXTENDED_RECORD_COVERS_ONLY_SOME_ENTRY_VARIANTS" in issues
                    else "CANDIDATE_PROFILE_MATCH_EXACT" if record_refs
                    else "NO_ADDITIONAL_METHOD" if extended_status == "DONOR_REPORTS_NO_ADDITIONAL_METHOD"
                    else "NO_SCENARIO_EXTENDED_SOURCE"
                )
                row = {
                    "scenarioId": entry["id"], "modelId": model, "sourceScenarioId": original["id"],
                    "packPath": str(pack.relative_to(root)),
                    "donorPath": snapshot["sourcePath"], "donorBlob": snapshot["sourceBlobSha"],
                    "variantIds": entry_variants,
                    "sourceApplicability": original.get("applicability"),
                    "graph": graph_facts(original["graph"]),
                    "sourceRefIds": source_ref_ids, "sourceRefCount": len(refs),
                    "extendedSourceStatus": extended_status,
                    "extendedRoutePointer": route_pointer, "extendedRecords": record_refs,
                    "extendedRecordVariantIds": candidate_variants,
                    "entryVariantsWithoutExtendedRecord": sorted(set(entry_variants) - set(candidate_variants)),
                    "otherSourceRelations": source_matches.get(entry["id"], []) if model == "chme3-family" else [],
                    "tem2Stage3Lineage": original["id"] in tem2_ids if model == "tem2-family" else None,
                    "sourceIssues": sorted(issues),
                    "reviewClass": review_class,
                    "shortVersion": "NOT_AUTHORED", "detailedVersion": "NOT_AUTHORED",
                    "shortExtendedBranch": "NOT_AUTHORED", "detailedExtendedBranch": "NOT_AUTHORED",
                    "publicationStatus": entry["publicationStatus"],
                }
                rows.append(row)

    runtime_path = "content-packs/electric/vl80s/diagnostics/runtime/executable-flow.json"
    runtime = read(runtime_path, root)
    assert runtime["sourceSnapshot"]["commit"] == DONOR
    recommended = {entry["id"] for pack in (root / "content-packs/electric/vl80s/diagnostics/recommended").glob("*.pack.json")
                   for entry in read(pack.relative_to(root), root)["entries"]}
    extended_pack = {entry["id"] for pack in (root / "content-packs/electric/vl80s/diagnostics/extended").rglob("*.pack.json")
                     for entry in read(pack.relative_to(root), root)["entries"]}
    runtime_ids = {scenario["id"] for scenario in runtime["scenarios"]}
    assert len(runtime_ids) == 103 and recommended.isdisjoint(extended_pack)
    assert recommended | extended_pack == runtime_ids and len(recommended) == 44 and len(extended_pack) == 59
    framework = read("content-packs/electric/vl80s/diagnostics/migration/framework-source.candidate.json", root)
    framework_ids = {module["scenarioId"] for module in framework["sourceObject"]["modules"]}
    for scenario in runtime["scenarios"]:
        graph = vl80s_graph_facts(scenario)
        rows.append({
            "scenarioId": scenario["id"], "modelId": "vl80s",
            "sourceScenarioId": scenario["legacyId"], "packPath": runtime_path,
            "donorPath": "DiagnosticRepository.scenarios",
            "donorBlob": None, "variantIds": scenario["applicableVariantIds"],
            "sourceApplicability": scenario.get("applicability"), "graph": graph,
            "sourceRefIds": [], "sourceRefCount": 0,
            "sourceNotePresent": bool(scenario.get("sourceNote")),
            "recommendedPackMembership": scenario["id"] in recommended,
            "extendedPackMembership": scenario["id"] in extended_pack,
            "frameworkV2Module": scenario["legacyId"] in framework_ids,
            "extendedSourceStatus": "NO_SCENARIO_SPECIFIC_EXTENDED_BRANCH_SOURCE",
            "extendedRoutePointer": None, "extendedRecords": [],
            "extendedRecordVariantIds": [], "entryVariantsWithoutExtendedRecord": scenario["applicableVariantIds"],
            "otherSourceRelations": [], "tem2Stage3Lineage": None, "sourceIssues": [],
            "reviewClass": "NO_SCENARIO_EXTENDED_SOURCE",
            "shortVersion": "NOT_AUTHORED", "detailedVersion": "NOT_AUTHORED",
            "shortExtendedBranch": "NOT_AUTHORED", "detailedExtendedBranch": "NOT_AUTHORED",
            "publicationStatus": "RUNTIME_GRAPH_PRESERVED",
        })

    rows.sort(key=lambda r: (r["modelId"], r["scenarioId"]))
    assert len(rows) == 340 and len({r["scenarioId"] for r in rows}) == len(rows)
    counts = Counter(r["modelId"] for r in rows)
    assert counts == {"ermak": 136, "chme3-family": 68, "tem2-family": 33, "vl80s": 103}
    assert all(not r["graph"]["invalidTargets"] and not r["graph"]["unreachableNodeIds"] for r in rows)
    statuses = {model: dict(sorted(Counter(r["extendedSourceStatus"] for r in rows
                                    if r["modelId"] == model).items())) for model in FAMILIES}
    assert statuses == {
        "ermak": {"NO_PINNED_EXTENDED_ROUTING": 136},
        "chme3-family": {"DONOR_CANDIDATE_RECORD": 54, "DONOR_REPORTS_NO_ADDITIONAL_METHOD": 14},
        "tem2-family": {"DONOR_CANDIDATE_RECORD": 31, "DONOR_REPORTS_NO_ADDITIONAL_METHOD": 2},
        "vl80s": {"NO_SCENARIO_SPECIFIC_EXTENDED_BRANCH_SOURCE": 103},
    }
    issue_counts = Counter(issue for row in rows for issue in row["sourceIssues"])
    assert issue_counts["EXTENDED_RECORD_PROFILE_DISJOINT_FROM_ENTRY"] == 8
    assert issue_counts["EXTENDED_RECORD_COVERS_ONLY_SOME_ENTRY_VARIANTS"] == 66
    assert issue_counts["ABSENT_FROM_ERMAK_STAGE7_INDEX"] == 1
    classes = Counter(row["reviewClass"] for row in rows)
    assert classes == {
        "CANDIDATE_PROFILE_MATCH_EXACT": 11, "CANDIDATE_PARTIAL_VARIANT": 66,
        "CANDIDATE_PROFILE_DISJOINT": 8, "NO_ADDITIONAL_METHOD": 16,
        "NO_SCENARIO_EXTENDED_SOURCE": 239,
    }
    return {
        "schemaVersion": 1, "donorCommit": DONOR,
        "scope": "Pinned donor diagnostic scenarios in Beta; source relations are evidence, not publication or current action authority",
        "uniqueScenarioCount": len(rows), "countsByModel": dict(sorted(counts.items())),
        "preservedGraphNodes": sum(r["graph"]["nodeCount"] for r in rows),
        "extendedSourceStatusByModel": statuses,
        "sourceIssueCounts": dict(sorted(issue_counts.items())),
        "reviewClassCounts": dict(sorted(classes.items())),
        "unwrittenVersionRoutes": 2 * len(rows), "unwrittenVersionExtendedBranches": 2 * len(rows),
        "notes": [
            "VL80S's 59 EXTENDED pack entries are original scenarios, not extended branches of the 44 STANDARD pack entries.",
            "CHME3 documentary source relations are ID/title matches only; original graph entries have no sourceRefs field.",
            "TEM2 donor extended records are keyed by original scenario ID; a record's profile cannot be inherited by every variant projection.",
            "A donor record with no additional method is an evidence gap, not permission to fabricate a branch.",
            "Graph reachability and target validity do not establish semantic usefulness, current authority or profile applicability.",
        ],
        "rows": rows,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = analyze()
    rendered = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    if args.check:
        assert OUTPUT.read_text() == rendered, "diagnostic corpus analysis drifted; review and regenerate"
    else:
        OUTPUT.write_text(rendered)
    print("DIAGNOSTIC_CORPUS_ANALYSIS_PASS", payload["uniqueScenarioCount"], payload["preservedGraphNodes"])
