#!/usr/bin/env python3
"""Account for the eight pending-mapping groups outside technical/document sets."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "docs/data-migration"
DESTINATION = DIRECTORY / "remaining-pending-mapping-evidence.json"
SNAPSHOT_PATH = "content-packs/electric/vl80s/diagnostics/migration/pantograph-reference-source.candidate.json"


def project():
    discovery = json.loads((DIRECTORY / "source-discovery-ledger.json").read_text())
    technical = json.loads((DIRECTORY / "technical-discovery-evidence.json").read_text())
    documentary = json.loads((DIRECTORY / "document-discovery-evidence.json").read_text())
    accounted = {(r["sourcePath"], r["sourceObjectId"])
                 for overlay in (technical, documentary) for r in overlay["rows"]}
    pending = [r for r in discovery["rows"] if r["disposition"] == "PENDING_MAPPING"]
    assert len(pending) == 206 and len(accounted) == 198
    rest = [r for r in pending if (r["sourcePath"], r["sourceObjectId"]) not in accounted]
    assert len(rest) == 8

    archive = json.loads((DIRECTORY / "legacy-zip-discovery-overlay.json").read_text())
    members = {m["memberDiscoveryPath"]: m for m in archive["members"]
               if m["memberDiscoveryPath"]}
    reference = json.loads((ROOT / SNAPSHOT_PATH).read_text())
    assert reference["sourceBlobSha"] == "2256a734d3cd929012629ab1cfbeeddccef96933"
    assert reference["runtimeImport"] is False
    result = []
    for row in rest:
        path, group = row["sourcePath"], row["sourceObjectId"]
        if path.startswith("RailBrakeCalculator.zip!"):
            member = members[path]
            assert archive["archiveGitBlobSha"] == row["sourceArtifactGitBlob"]
            assert member["sourceFileReview"] == "ARCHIVE_ONLY_REVIEWED"
            assert member["finalObjectDisposition"] is None and member["runtimeImport"] is False
            evidence = "ARCHIVE_MEMBER_REVIEW_ONLY"
            evidence_paths = ["docs/data-migration/legacy-zip-discovery-overlay.json",
                              member["reviewDocument"]]
            additional = {"memberGitBlobSha": member["memberGitBlobSha"]}
        elif path == "app/src/main/assets/exam_questions.json":
            assert group == "questions[*]" and row["sourceCount"] == 329
            evidence = "STRUCTURAL_PARITY_ACCESS_POLICY_OPEN"
            evidence_paths = ["docs/data-migration/LEGACY_ZIP_ARCHIVE_ONLY_REVIEW_2026-10-13.md"]
            additional = {}
        else:
            assert path == "docs/reference_packs/vl80s/pantograph-no-rise/reference_pack.json"
            assert row["sourceArtifactGitBlob"] == reference["sourceBlobSha"]
            assert group.endswith("[*]")
            field = group[:-3]
            assert len(reference["sourceObject"][field]) == row["sourceCount"]
            evidence = "EXACT_BLOB_ALIAS_TO_NON_RUNTIME_SOURCE_SNAPSHOT"
            evidence_paths = [SNAPSHOT_PATH]
            additional = {}
        assert all((ROOT / evidence_path).is_file() for evidence_path in evidence_paths)
        result.append({
            "sourcePath": path,
            "sourceObjectId": group,
            "sourceArtifactGitBlob": row["sourceArtifactGitBlob"],
            "sourceCount": row["sourceCount"],
            "discoveryDisposition": row["disposition"],
            "evidenceKind": evidence,
            "evidencePaths": evidence_paths,
            **additional,
            "publicationDecision": None,
        })
    assert sum(r["evidenceKind"] == "ARCHIVE_MEMBER_REVIEW_ONLY" for r in result) == 3
    assert sum(r["evidenceKind"] == "EXACT_BLOB_ALIAS_TO_NON_RUNTIME_SOURCE_SNAPSHOT"
               for r in result) == 4
    assert len(accounted | {(r["sourcePath"], r["sourceObjectId"]) for r in result}) == 206
    return {"schemaVersion": 1, "donorCommit": discovery["sourceCommit"],
            "scope": "Final eight of 206 provisional pending-mapping discovery groups",
            "note": "Evidence classification only; archive semantics and exam access remain open. No source text, discovery status or publication decision is changed.",
            "rows": result}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(project(), ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert DESTINATION.read_text() == encoded
    else:
        DESTINATION.write_text(encoded)
    print("PENDING_MAPPING_EVIDENCE_PASS", 70, 128, 8)


if __name__ == "__main__":
    main()
