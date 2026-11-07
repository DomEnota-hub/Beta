#!/usr/bin/env python3
"""Preserve all pending donor docs as exact non-runtime historical source text."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/data-migration/source-discovery-ledger.json"
OUTPUT = ROOT / "content-packs/locomotive-migration/migration/historical-documents.candidate.json"
DONOR = ROOT.parent / "test-donor"


def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def review(source=None):
    ledger = json.loads(LEDGER.read_text())
    paths = [r for r in ledger["rows"] if r["disposition"] == "PENDING_EXTRACTION"
             and r["sourcePath"].startswith("docs/")]
    assert len(paths) == 50
    if source is None:
        saved = json.loads(OUTPUT.read_text())
        assert saved["donorCommit"] == ledger["sourceCommit"]
        assert saved["runtimeImport"] is False and saved["publicationStatus"] == "CANDIDATE"
        contents = {r["sourcePath"]: r for r in saved["documents"]}
    else:
        contents = {}
    assert source is not None or set(contents) == {r["sourcePath"] for r in paths}
    documents = []
    for row in paths:
        path = row["sourcePath"]
        if source is None:
            item = contents[path]
            raw = item["exactSourceText"].encode("utf-8")
        else:
            raw = subprocess.check_output(["git", "-C", str(source), "show",
                                           ledger["sourceCommit"] + ":" + path])
        assert len(raw) == row["sourceBytes"] and blob(raw) == row["sourceArtifactGitBlob"], path
        documents.append({"sourcePath": path, "sourceBlobSha": row["sourceArtifactGitBlob"],
                          "sourceObjectId": row["sourceObjectId"],
                          "sourceBytes": len(raw), "exactSourceText": raw.decode("utf-8")})
    assert sum(r["sourceBytes"] for r in documents) == 476439
    return {"schemaVersion": 1, "donorCommit": ledger["sourceCommit"],
            "publicationStatus": "CANDIDATE", "runtimeImport": False,
            "sourceInterpretation": "HISTORICAL_DOCUMENTS_ONLY_NO_CURRENT_ACTION_AUTHORITY",
            "note": "Whole donor text is preserved to avoid losing source notes and contracts. Historical checkpoints, restricted material, and outdated normative claims are not imported into UI or approved as instructions.",
            "documentCount": 50, "documents": documents}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate", action="store_true")
    args = parser.parse_args()
    if args.generate:
        assert DONOR.is_dir()
        result = review(DONOR)
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
    else:
        result = review()
    print("PENDING_DOCUMENT_SOURCES_PASS", result["documentCount"])


if __name__ == "__main__":
    main()
