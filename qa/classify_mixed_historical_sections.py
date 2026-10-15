#!/usr/bin/env python3
"""Route each section of the five mixed historical documents for later review."""

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/data-migration"
INDEX = ROOT / "content-packs/locomotive-migration/migration/historical-section-index.candidate.json"
OUT = BASE / "mixed-historical-section-review.json"

# Explicit ordinal decisions, checked against source heading and section hashes.
# MIXED_REVIEW includes sections that mention multiple data/behavior phases.
DECISIONS = {
    "docs/integration/TEM2_APP_INTEGRATION_CHECKPOINT.md": [
        "SOURCE_CONTEXT", "MIXED_REVIEW", "INFORMATION_REVIEW", "QA_CONTEXT",
        "SEPARATE_UI_STAGE", "SOURCE_CONTEXT"],
    "docs/locomotives/chme3/DATA_CONTRACT.md": [
        "SOURCE_CONTEXT", "MIXED_REVIEW", "INFORMATION_REVIEW", "INFORMATION_REVIEW",
        "INFORMATION_REVIEW", "INFORMATION_REVIEW", "INFORMATION_REVIEW",
        "DIAGNOSTIC_STAGE", "INFORMATION_REVIEW", "ASSISTANT_STAGE", "MIXED_REVIEW"],
    "docs/locomotives/chme3/PASS_4_FINAL_CHECKPOINT.md": [
        "SOURCE_CONTEXT", "MIXED_REVIEW", "MIXED_REVIEW", "INFORMATION_REVIEW",
        "DIAGNOSTIC_STAGE", "INFORMATION_REVIEW", "INFORMATION_REVIEW",
        "ASSISTANT_STAGE", "QA_CONTEXT", "MIXED_REVIEW", "SOURCE_CONTEXT"],
    "docs/locomotives/chme3/README.md": [
        "SOURCE_CONTEXT", "MIXED_REVIEW", "MIXED_REVIEW"],
    "docs/locomotives/diesel/chme3-family/STAGE_4_FINAL_CHECKPOINT.md": [
        "SOURCE_CONTEXT", "MIXED_REVIEW", "INFORMATION_REVIEW", "INFORMATION_REVIEW",
        "INFORMATION_REVIEW", "DIAGNOSTIC_STAGE", "INFORMATION_REVIEW",
        "ASSISTANT_STAGE", "QA_CONTEXT", "MIXED_REVIEW", "SOURCE_CONTEXT"],
}


def project():
    phase = json.loads((BASE / "historical-document-phase-review.json").read_text())
    index = json.loads(INDEX.read_text())
    mixed = {r["sourcePath"]: r for r in phase["rows"]
             if r["phase"] == "MIXED_OBJECT_REVIEW"}
    sources = {d["sourcePath"]: d for d in index["documents"]}
    assert len(mixed) == 5 and set(mixed) == set(DECISIONS)
    rows = []
    for path, choices in DECISIONS.items():
        d = sources[path]
        assert len(choices) == len(d["sections"]) == mixed[path]["sectionCount"]
        assert d["sourceBlobSha"] == mixed[path]["sourceBlobSha"]
        for section, choice in zip(d["sections"], choices):
            rows.append({"sourcePath": path, "sourceBlobSha": d["sourceBlobSha"],
                         "sectionCandidateId": section["candidateId"],
                         "sourceTextSha256": section["sourceTextSha256"],
                         "heading": section["heading"], "ordinal": section["ordinal"],
                         "reviewPhase": choice, "finalObjectDisposition": None,
                         "publicationDecision": None})
    assert len(rows) == 42
    return {"schemaVersion": 1, "donorCommit": index["donorCommit"],
            "scope": "All 42 indexed sections in five mixed historical documents",
            "note": "Manual section-level work routing only. SOURCE_CONTEXT and QA_CONTEXT remain exact archived text; MIXED_REVIEW still needs assertion-level separation. No current source status or runtime permission inferred.",
            "phaseCounts": dict(sorted(Counter(r["reviewPhase"] for r in rows).items())),
            "rows": rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(project(), ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert OUT.read_text() == encoded
    else:
        OUT.write_text(encoded)
    print("MIXED_HISTORICAL_SECTION_REVIEW_PASS", project()["phaseCounts"])


if __name__ == "__main__":
    main()
