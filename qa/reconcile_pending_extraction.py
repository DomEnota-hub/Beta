#!/usr/bin/env python3
"""Triage all provisional extraction files without granting final dispositions."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "docs/data-migration"
OUTPUT = DIRECTORY / "pending-extraction-evidence.json"


def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def evidence():
    return {
        "app/src/main/java/ru/railbrake/calculator/core/KnowledgeRepository.kt":
            ("PINNED_SOURCE_AND_PARTIAL_CONTENT_PROJECTION", [
                "content-packs/electric/vl80s/migration/source-assets/KnowledgeRepository.kt",
                "content-packs/common/knowledge/articles.pack.json",
                "content-packs/common/safety/articles.pack.json",
                "qa/validate_vl80s_legacy_knowledge.py"]),
        "app/src/main/java/ru/railbrake/calculator/core/KnowledgeFirstWave.kt":
            ("COMMON_CONTENT_PROJECTION", ["content-packs/common/knowledge/articles.pack.json",
                                           "content-packs/common/safety/articles.pack.json",
                                           "qa/validate_common_knowledge.py"]),
        "app/src/main/java/ru/railbrake/calculator/ui/FirstAidScreen.kt":
            ("COMMON_CONTENT_PROJECTION", ["content-packs/common/first-aid/topics.pack.json",
                                           "qa/validate_common_first_aid.py"]),
        "app/src/main/java/ru/railbrake/calculator/core/TechnicalPresentation.kt":
            ("EXACT_PINNED_SOURCE_AND_VOCABULARY", [
                "content-packs/locomotive-migration/source-assets/TechnicalPresentation.kt",
                "content-packs/locomotive-migration/technical-presentation-vocabulary.candidate.json",
                "qa/migrate_technical_presentation.py"]),
        "app/src/main/java/ru/railbrake/calculator/core/Vl80sNormalValues.kt":
            ("SIX_NORMAL_PARAMETERS_PROJECTED", [
                "content-packs/electric/vl80s/technical-data/normal-values.pack.json",
                "qa/validate_vl80s_normal_values.py"]),
    }


def classify(path):
    if path.startswith("app/src/main/java/"):
        return "KOTLIN_CONTENT_OR_BEHAVIOR_REVIEW"
    if path.startswith(".github/scripts/") or path.startswith("tools/"):
        return "GENERATOR_EMBEDDED_CONTENT_REVIEW"
    if path.startswith("docs/"):
        return "DOCUMENT_OR_STRUCTURED_SOURCE_REVIEW"
    if path.startswith("patch/app/"):
        return "EFFECTIVE_PATCH_CODE_REVIEW"
    if path.startswith("qa/") or path.startswith("app/qa/"):
        return "QA_GENERATOR_OR_VALIDATOR_REVIEW"
    if path.endswith((".apk", ".zip")):
        return "BINARY_OR_ARCHIVE_COMPOSITION_REVIEW"
    return "PROJECT_CONTEXT_OR_BUILD_REVIEW"


def project():
    ledger = json.loads((DIRECTORY / "source-discovery-ledger.json").read_text())
    pending = [r for r in ledger["rows"] if r["disposition"] == "PENDING_EXTRACTION"]
    assert len(pending) == 254 and len({r["sourcePath"] for r in pending}) == 254
    wrappers = json.loads((DIRECTORY / "diagnostic-kotlin-wrapper-dispositions.json").read_text())
    generators = json.loads((DIRECTORY / "ermak-generator-dispositions.json").read_text())
    existing = {r["sourcePath"]: (r["sourceBlobSha"], filename)
                for filename, source in (("diagnostic-kotlin-wrapper-dispositions.json", wrappers),
                                         ("ermak-generator-dispositions.json", generators))
                for r in source["rows"]}
    explicit = evidence()
    assert len(existing) == 6 and len(explicit) == 5
    result = []
    for row in pending:
        path = row["sourcePath"]
        assert row["sourceObjectId"] in ("source-file", "source-document", "archive-container")
        if path in explicit:
            kind, paths = explicit[path]
            status = "SOURCE_OR_CONTENT_EVIDENCE_PRESENT_REMAINDER_OPEN"
        elif path in existing:
            sha, filename = existing[path]
            assert sha == row["sourceArtifactGitBlob"]
            kind, paths = "FILE_LEVEL_DISPOSITION_EXISTS", ["docs/data-migration/" + filename]
            status = "SOURCE_FILE_REVIEWED_SEMANTIC_CONTENT_OPEN"
        else:
            kind, paths = classify(path), []
            status = "SOURCE_CONTENT_REVIEW_OPEN"
        for destination in paths:
            assert (ROOT / destination).is_file(), destination
        if path.endswith("KnowledgeRepository.kt") or path.endswith("TechnicalPresentation.kt"):
            assert git_blob((ROOT / paths[0]).read_bytes()) == row["sourceArtifactGitBlob"]
        result.append({
            "sourcePath": path,
            "sourceObjectId": row["sourceObjectId"],
            "sourceArtifactGitBlob": row["sourceArtifactGitBlob"],
            "sourceBytes": row["sourceBytes"],
            "discoveryDisposition": row["disposition"],
            "reviewTrack": classify(path),
            "evidenceKind": kind,
            "evidencePaths": paths,
            "reviewStatus": status,
            "finalObjectDisposition": None,
            "publicationDecision": None,
        })
    counts = dict(sorted(Counter(r["reviewTrack"] for r in result).items()))
    return {"schemaVersion": 1, "donorCommit": ledger["sourceCommit"],
            "scope": "254 source-file rows provisionally pending extraction",
            "note": "File-level triage is not object extraction or semantic parity. Scripts and QA generators may embed source content; no provisional ledger status, runtime import, or publication decision changes.",
            "countsByReviewTrack": counts, "rows": result}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(project(), ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert OUTPUT.read_text() == encoded
    else:
        OUTPUT.write_text(encoded)
    print("PENDING_EXTRACTION_TRIAGE_PASS 254")


if __name__ == "__main__":
    main()
