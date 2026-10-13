#!/usr/bin/env python3
"""Fail closed on unsupported CHME3 acceptance profile or requiredness claims."""
import argparse
import json
from pathlib import Path

from build_chme3_acceptance_applicability import OUTPUT, VARIANTS, build


def validate(root):
    actual = json.loads((root / OUTPUT).read_text())
    assert actual == build(root)
    assert actual["scope"] == "SOURCE_REVIEW_ONLY_NO_RUNTIME_IMPORT"
    assert actual["runtimeImport"] is False and actual["publicationStatus"] == "CANDIDATE"
    assert actual["actionDisposition"] == "INFORMATION_ONLY"
    assert actual["requirednessPolicy"] == "NO_NETWORK_OR_LOCAL_TO1_MANDATORY_ASSIGNMENT_WITHOUT_APPROVED_WORK_LIST"
    assert len(actual["rows"]) == 20
    seen = set()
    for i, row in enumerate(actual["rows"], 1):
        assert row["itemId"] == f"CHME3-REQ-{i:02d}" and row["itemId"] not in seen
        seen.add(row["itemId"])
        assert row["legacySourcePhase"] == "MANDATORY_CHECK"  # Source preserved, not activated.
        assert set(row["cells"]) == {v for v, _ in VARIANTS}
        assert len(row["sourceRegistryEvidence"]) == len(row["sourceRefs"])
        for equipment in row["equipmentEvidence"]:
            assert len(equipment["sourceOccurrences"]) == 2
            assert {x["role"] for x in equipment["sourceOccurrences"]} == {"INDEX", "CARD"}
            assert all(x["applicability"] == ["ЧМЭ3", "ЧМЭ3Т", "ЧМЭ3Э"]
                       for x in equipment["sourceOccurrences"])
        for variant, series in VARIANTS:
            cell = row["cells"][variant]
            assert cell["series"] == series and cell["actualUnitVerificationRequired"] is True
            assert cell["requiredness"] == "UNDETERMINED_APPROVED_LOCAL_TO1_LIST_MISSING"
            assert cell["sourceRefs"] == row["sourceRefs"]
            assert cell["equipmentIds"] == [e["id"] for e in row["equipmentEvidence"]]
            assert cell["reason"] and cell["safetyBoundary"]
            assert cell["technicalApplicability"] in {
                "ATLAS_SUPPORTED_ACTUAL_EQUIPMENT_UNVERIFIED",
                "TOPIC_SUPPORTED_ACTUAL_SCOPE_UNVERIFIED",
                "VARIANT_METHOD_REQUIRES_PRIMARY_CHECK"}
            assert "CHME3T-EQ-BRAKE-RESISTORS" not in cell["equipmentIds"]
    assert sum(len(r["cells"]) for r in actual["rows"]) == 60
    return len(actual["rows"])


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path("."))
    a = p.parse_args()
    print("CHME3_ACCEPTANCE_MATRIX_PASS", validate(a.root), 60)
