#!/usr/bin/env python3
"""Route exact, nonempty source lines in the ten mixed historical sections."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/data-migration"
INDEX = ROOT / "content-packs/locomotive-migration/migration/historical-section-index.candidate.json"
DOCUMENTS = ROOT / "content-packs/locomotive-migration/migration/historical-documents.candidate.json"
OUT = BASE / "mixed-historical-assertion-review.json"

# Each numbered source line is assigned once. The document header is excluded.
# These are routing decisions about archived assertions, not current truth claims.
DECISIONS = {
    ("docs/integration/TEM2_APP_INTEGRATION_CHECKPOINT.md", 1): {
        "SOURCE_CONTEXT": [13, 14, 19, 20, 21], "FUNCTIONAL_STAGE": [15],
        "DIAGNOSTIC_STAGE": [16], "ASSISTANT_STAGE": [17], "UI_STAGE": [18]},
    ("docs/locomotives/chme3/DATA_CONTRACT.md", 1): {
        "SOURCE_CONTEXT": [5], "SAFETY_POLICY_CONTEXT": [7]},
    ("docs/locomotives/chme3/DATA_CONTRACT.md", 10): {
        "SOURCE_CONTEXT": [136], "INFORMATION_EVIDENCE_REVIEW": [138, 139],
        "DIAGNOSTIC_STAGE": [140, 141], "ACCEPTANCE_REVIEW": [142],
        "ASSISTANT_STAGE": [143], "QA_CONTEXT": [144, 145]},
    ("docs/locomotives/chme3/PASS_4_FINAL_CHECKPOINT.md", 1): {
        "SOURCE_CONTEXT": [10, 12]},
    ("docs/locomotives/chme3/PASS_4_FINAL_CHECKPOINT.md", 2): {
        "QA_CONTEXT": [16], "INFORMATION_EVIDENCE_REVIEW": [18, 19, 20, 21, 22, 23, 24],
        "DIAGNOSTIC_STAGE": [25, 26, 30, 31], "ACCEPTANCE_REVIEW": [27, 28, 29]},
    ("docs/locomotives/chme3/PASS_4_FINAL_CHECKPOINT.md", 9): {
        "UI_STAGE": [102], "SOURCE_CONTEXT": [103], "SAFETY_POLICY_CONTEXT": [104, 105, 106, 107]},
    ("docs/locomotives/chme3/README.md", 1): {
        "SOURCE_CONTEXT": [7, 9, 11, 12, 13, 15], "ASSISTANT_STAGE": [14]},
    ("docs/locomotives/chme3/README.md", 2): {
        "SOURCE_CONTEXT": [25], "INFORMATION_EVIDENCE_REVIEW": [19],
        "SAFETY_POLICY_CONTEXT": [20], "DIAGNOSTIC_STAGE": [21],
        "ACCEPTANCE_REVIEW": [22], "QA_CONTEXT": [23]},
    ("docs/locomotives/diesel/chme3-family/STAGE_4_FINAL_CHECKPOINT.md", 1): {
        "SOURCE_CONTEXT": [10, 12]},
    ("docs/locomotives/diesel/chme3-family/STAGE_4_FINAL_CHECKPOINT.md", 9): {
        "FUNCTIONAL_STAGE": [141, 142], "ASSISTANT_STAGE": [143],
        "UI_STAGE": [144, 145], "SOURCE_CONTEXT": [146]},
}


def project():
    review = json.loads((BASE / "mixed-historical-section-review.json").read_text())
    index = json.loads(INDEX.read_text())
    documents = json.loads(DOCUMENTS.read_text())
    doc_by_path = {d["sourcePath"]: d for d in documents["documents"]}
    section_by_id = {s["candidateId"]: s for d in index["documents"] for s in d["sections"]}
    mixed = [r for r in review["rows"] if r["reviewPhase"] == "MIXED_REVIEW"]
    assert len(mixed) == 10 and {(r["sourcePath"], r["ordinal"]) for r in mixed} == set(DECISIONS)
    rows = []
    for r in mixed:
        key = r["sourcePath"], r["ordinal"]
        section = section_by_id[r["sectionCandidateId"]]
        source = doc_by_path[r["sourcePath"]]
        assert r["sourceBlobSha"] == source["sourceBlobSha"]
        lines = source["exactSourceText"].splitlines(keepends=True)
        covered = set()
        for phase, line_numbers in DECISIONS[key].items():
            for number in line_numbers:
                assert number not in covered and section["startLine"] < number < section["endLineExclusive"]
                covered.add(number)
                value = lines[number - 1].rstrip("\r\n")
                assert value.strip() and not value.lstrip().startswith("#")
                rows.append({"sourcePath": r["sourcePath"], "sourceBlobSha": r["sourceBlobSha"],
                             "sectionCandidateId": r["sectionCandidateId"],
                             "sourceTextSha256": section["sourceTextSha256"],
                             "line": number, "textSha256": hashlib.sha256(value.encode()).hexdigest(),
                             "reviewPhase": phase, "finalObjectDisposition": None,
                             "publicationDecision": None})
        expected = {number for number in range(section["startLine"] + 1, section["endLineExclusive"])
                    if lines[number - 1].strip()}
        assert covered == expected, (key, sorted(expected - covered), sorted(covered - expected))
    return {"schemaVersion": 1, "donorCommit": index["donorCommit"],
            "scope": "Every nonempty assertion line of the ten previously mixed historical sections",
            "note": "Historical project claims and policy statements are routed by exact line; this does not certify their present accuracy, finish object-level disposition or grant runtime/action authority.",
            "sectionCount": len(mixed), "assertionLineCount": len(rows),
            "phaseCounts": dict(sorted(Counter(r["reviewPhase"] for r in rows).items())),
            "rows": rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = project()
    encoded = json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert OUT.read_text() == encoded
    else:
        OUT.write_text(encoded)
    print("MIXED_HISTORICAL_ASSERTION_REVIEW_PASS", result["assertionLineCount"], result["phaseCounts"])


if __name__ == "__main__":
    main()
