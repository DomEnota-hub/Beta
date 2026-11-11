#!/usr/bin/env python3
"""Check actual packaged VL80S candidate summary coverage, not action approval.

The Kotlin DiagnosticReferenceCatalog is read-only. This gate confirms its
underlying pinned runtime and candidate content packs intersect meaningfully.
It must NOT publish checks, action sequences, or research-only materials.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "content-packs" / "electric" / "vl80s" / "diagnostics"
DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    index = load(BASE / "index.json")
    runtime = load(ROOT / "content-packs" / index["executableFlow"])
    assert index["modelId"] == runtime["modelId"] == "vl80s"
    assert runtime["sourceSnapshot"]["commit"] == DONOR, "donor snapshot changed"
    scenarios = runtime["scenarios"]
    assert runtime["scenarioCount"] == len(scenarios), "scenario count mismatch"
    by_id = {}
    for relative in index["recommendedPacks"]:
        pack = load(ROOT / "content-packs" / relative)
        assert pack["manifest"]["modelIds"] == ["vl80s"], relative
        for entry in pack["entries"]:
            key = entry["id"]
            assert key not in by_id, f"duplicate candidate: {key}"
            by_id[key] = entry

    matched = []
    for scenario in scenarios:
        entry = by_id.get(scenario["id"])
        if entry is None or entry["publicationStatus"] != "CANDIDATE":
            continue
        if entry["layer"] != "STANDARD" or scenario["profileId"] != "vl80s":
            continue
        assert entry["type"] == "DIAGNOSTIC_SCENARIO", scenario["id"]
        assert entry["owner"] == {"kind": "MODEL", "modelId": "vl80s"}
        assert "vl80s" in entry["applicability"]["modelIds"]
        assert entry["title"].strip() and entry["summary"].strip()
        assert scenario["title"].strip() and scenario["summary"].strip()
        matched.append(scenario["id"])

    assert matched, "no real donor diagnostic descriptions would be visible"
    assert len(matched) == len(set(matched)), "duplicate preview"
    print(
        "POST15_GROUP2_REFERENCE_PARITY_PASS",
        f"read_only_candidates={len(matched)}",
        f"runtime_scenarios={len(scenarios)}",
        f"registry_entries={len(by_id)}",
        "executable_candidates=0",
    )


if __name__ == "__main__":
    main()
