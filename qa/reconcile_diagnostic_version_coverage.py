#!/usr/bin/env python3
"""Account for diagnostic versions without deriving routes from display depth."""
import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/data-migration/diagnostic-version-coverage.json"
DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
PACKS = {
    "ermak": "electric/ermak",
    "chme3-family": "diesel/chme3-family",
    "tem2-family": "diesel/tem2-family",
    "vl80s": "electric/vl80s",
}


def project(root=ROOT):
    rows = []
    for model, directory in PACKS.items():
        paths = sorted((root / "content-packs" / directory / "diagnostics/recommended").glob("*.pack.json"))
        for path in paths:
            for entry in json.loads(path.read_text())["entries"]:
                assert entry["type"] == "DIAGNOSTIC_SCENARIO"
                assert entry["owner"]["modelId"] == model
                assert entry["publicationStatus"] == "CANDIDATE"
                source = entry.get("sourceObject", {})
                original = source.get("object", {})
                if source:
                    assert len(source["sourceBlobSha"]) == 40
                    assert original["id"]
                # A source graph is one route, not two independently reviewed
                # versions. A display projection and a depth setting are not routes.
                assert not any(key in original for key in ("shortRoute", "detailedRoute"))
                rows.append({
                    "modelId": model,
                    "entryId": entry["id"],
                    "packPath": str(path.relative_to(root)),
                    "donorPath": source.get("sourcePath"),
                    "donorBlob": source.get("sourceBlobSha"),
                    "originalId": original.get("id"),
                    "preservedGraph": bool(original.get("graph")),
                    "shortVersion": "UNAUTHORED",
                    "detailedVersion": "UNAUTHORED",
                    "shortExtendedBranch": "UNBOUND",
                    "detailedExtendedBranch": "UNBOUND",
                    "runtimePublished": False,
                })

    # VL80S has a separate executable source and many scenarios without a
    # recommended pack entry. Keep both identities, never count them as two versions.
    runtime_path = "content-packs/electric/vl80s/diagnostics/runtime/executable-flow.json"
    runtime = json.loads((root / runtime_path).read_text())
    assert runtime["sourceSnapshot"]["commit"] == DONOR
    assert runtime["scenarioCount"] == len(runtime["scenarios"])
    recommended_vl80s = {row["entryId"] for row in rows if row["modelId"] == "vl80s"}
    runtime_vl80s = {scenario["id"] for scenario in runtime["scenarios"]}
    assert len(runtime_vl80s) == 103 and recommended_vl80s <= runtime_vl80s
    for scenario in runtime["scenarios"]:
        rows.append({
            "modelId": "vl80s", "entryId": None,
            "packPath": runtime_path,
            "donorPath": "DiagnosticRepository.scenarios",
            "donorBlob": None,
            "originalId": scenario["id"],
            "preservedGraph": True,
            "shortVersion": "UNAUTHORED",
            "detailedVersion": "UNAUTHORED",
            "shortExtendedBranch": "UNBOUND",
            "detailedExtendedBranch": "UNBOUND",
            "runtimePublished": True,
        })
    identities = [(row["modelId"], row["packPath"], row["entryId"] or row["originalId"])
                  for row in rows]
    assert len(identities) == len(set(identities))
    counts = Counter(row["modelId"] for row in rows)
    assert counts == {"ermak": 136, "chme3-family": 68, "tem2-family": 33, "vl80s": 147}
    return {
        "schemaVersion": 1, "donorCommit": DONOR,
        "scope": "Candidate recommended entries plus the distinct VL80S executable source; identities may overlap",
        "countsByModel": dict(sorted(counts.items())),
        "uniqueScenarioCount": len(rows) - len(recommended_vl80s),
        "requiredVersionSpecificExtendedBranches": 2 * (len(rows) - len(recommended_vl80s)),
        "vl80sRecommendedAlsoInRuntime": len(recommended_vl80s),
        "note": "A preserved graph, depth projection or extended source candidate is not a reviewed short/detailed route. No action authority or runtime promotion follows from this inventory.",
        "rows": sorted(rows, key=lambda row: (row["modelId"], row["entryId"] or "", row["originalId"] or "")),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = json.dumps(project(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    if args.check:
        assert OUTPUT.read_text() == result, "diagnostic version coverage changed; review the source and regenerate"
    else:
        OUTPUT.write_text(result)
    print("DIAGNOSTIC_VERSION_COVERAGE_PASS", len(json.loads(result)["rows"]))
