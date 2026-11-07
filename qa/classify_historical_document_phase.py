#!/usr/bin/env python3
"""Make the phase boundary of 50 exact historical source documents explicit."""

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "content-packs/locomotive-migration/migration/historical-section-index.candidate.json"
OUT = ROOT / "docs/data-migration/historical-document-phase-review.json"

INFORMATION = {
    "docs/acceptance-audit-beta48.md", "docs/acceptance-audit-beta50.md",
    "docs/first-aid-audit-beta49.md",
    "docs/integration/PACKAGE_B_STEPWISE_FLOWS_CHECKPOINT.md",
    "docs/integration/TEM2_STAGE2_ATLAS_CHECKPOINT.md",
    "docs/integration/TEM2_STAGE4_FINAL_CHECKPOINT.md",
    "docs/locomotives/chme3/ATLAS_PASS_2_CHECKPOINT.md",
    "docs/locomotives/chme3/ATLAS_PASS_2_SOURCE_NOTES.md",
    "docs/locomotives/diesel/chme3-family/INTERACTIVE_STAGE_2_CHECKPOINT.md",
    "docs/locomotives/diesel/chme3-family/chme3e/STAGE_1_CHECKPOINT.md",
    "docs/locomotives/diesel/chme3-family/chme3e/STAGE_2_CHECKPOINT.md",
    "docs/locomotives/diesel/tem2-family/STAGE_1_CHECKPOINT.md",
}
UI = {
    "docs/beta50-1-ux-closure.md",
    "docs/dev14-emulator-qa-handoff-2026-09-24.md",
    "docs/dev14-read-only-ui-audit-2026-09-24.md",
    "docs/integration/PACKAGE_C_LAYOUT_INTERACTION_PALETTE_CHECKPOINT.md",
}
MIXED = {
    "docs/integration/TEM2_APP_INTEGRATION_CHECKPOINT.md",
    "docs/locomotives/chme3/DATA_CONTRACT.md",
    "docs/locomotives/chme3/PASS_4_FINAL_CHECKPOINT.md",
    "docs/locomotives/chme3/README.md",
    "docs/locomotives/diesel/chme3-family/STAGE_4_FINAL_CHECKPOINT.md",
}
DIAGNOSTIC = {
    *["docs/" + name for name in (
        "ERMAK_COMPLETED41_SOURCE_REAUDIT_2026-09-26.md",
        "ERMAK_LEGACY_BATCH_A_AUDIT_2026-09-26.md",
        "ERMAK_MSUD_BATCH8_037_048_AUDIT_2026-09-26.md",
        "ERMAK_RECUPERATION_BATCH9_057_064_AUDIT_2026-09-26.md",
        "ERMAK_SAFETY_BATCH7_089_097_AUDIT_2026-09-26.md")],
    "docs/diagnostics/LOCOMOTIVE_DIAGNOSTIC_RUNTIME_CONTRACT_V2.md",
    *["docs/integration/EXTENDED_EMERGENCY_STAGE" + str(i) + "_CHECKPOINT.md"
      for i in range(5)],
    *["docs/integration/extended_emergency_" + name for name in (
        "stage1_inventory.json", "stage1_sources.json",
        "stage2_candidates.tsv", "stage2_discovery.tsv", "stage2_sources.tsv",
        "stage3_assistant_contract.json", "stage3_runtime_contract.json")],
    "docs/integration/TEM2_STAGE3_DIAGNOSTICS_CHECKPOINT.md",
    "docs/locomotives/chme3/DIAGNOSTICS_PASS_3_CHECKPOINT.md",
    "docs/locomotives/diesel/chme3-family/STAGE_3_DIAGNOSTICS_CHECKPOINT.md",
    *["docs/reference_packs/vl80s/pantograph-no-rise/" + name for name in (
        "IMPLEMENTATION_STATUS.md", "INTEGRATION_NOTES.md", "QA_ACCEPTANCE.md",
        "README.md", "SOURCE_MATRIX.md", "validate_reference_pack.py")],
    "docs/vl80s-diagnostic-audit-2026-09-26.md",
    "docs/vl80s-diagnostic-step-review-2026-09-26.md",
}


def project():
    index = json.loads(INDEX.read_text())
    groups = {"INFORMATION_REVIEW": INFORMATION, "DIAGNOSTIC_STAGE": DIAGNOSTIC,
              "SEPARATE_UI_STAGE": UI, "MIXED_OBJECT_REVIEW": MIXED}
    paths = {d["sourcePath"] for d in index["documents"]}
    assert len(paths) == 50
    assert set.union(*groups.values()) == paths
    assert sum(len(g) for g in groups.values()) == len(paths)  # no overlap
    phase_by_path = {path: phase for phase, members in groups.items() for path in members}
    rows = [{"sourcePath": d["sourcePath"], "sourceBlobSha": d["sourceBlobSha"],
             "sourceTextSha256": d["sourceTextSha256"], "sectionCount": len(d["sections"]),
             "phase": phase_by_path[d["sourcePath"]], "finalObjectDisposition": None,
             "publicationDecision": None}
            for d in index["documents"]]
    counts = Counter(r["phase"] for r in rows)
    return {"schemaVersion": 1, "donorCommit": index["donorCommit"],
            "scope": "Planning boundary for 50 exact source documents and their 351 sections",
            "note": "A document phase is not an object disposition. Mixed documents need section-level routing. Historical claims remain source text without current authority; this phase map never activates diagnostic or visual behavior.",
            "phaseCounts": dict(sorted(counts.items())), "rows": rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(project(), ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert OUT.read_text() == encoded
    else:
        OUT.write_text(encoded)
    print("HISTORICAL_PHASE_REVIEW_PASS", project()["phaseCounts"])


if __name__ == "__main__":
    main()
