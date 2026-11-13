#!/usr/bin/env python3
"""Pin seven extended-emergency source datasets/contracts without runtime promotion."""

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "content-packs/locomotive-migration/migration"
OUT = BASE / "extended-stage-documents.candidate.json"
NAMES = {
    "extended_emergency_stage1_inventory.json": ("candidates", 19),
    "extended_emergency_stage1_sources.json": ("sources", 7),
    "extended_emergency_stage2_candidates.tsv": ("tsv", 77),
    "extended_emergency_stage2_discovery.tsv": ("tsv", 92),
    "extended_emergency_stage2_sources.tsv": ("tsv", 29),
    "extended_emergency_stage3_assistant_contract.json": ("contract", None),
    "extended_emergency_stage3_runtime_contract.json": ("contract", None),
}


def project():
    ledger = json.loads((ROOT / "docs/data-migration/source-discovery-ledger.json").read_text())
    rows = {r["sourcePath"]: r for r in ledger["rows"]}
    entries = []
    for name, (kind, expected) in NAMES.items():
        path = "docs/integration/" + name
        row = rows[path]
        raw = (BASE / "source-assets" / name).read_bytes()
        sha = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        assert sha == row["sourceArtifactGitBlob"] and len(raw) == row["sourceBytes"]
        if kind == "tsv":
            records = list(csv.DictReader(io.StringIO(raw.decode("utf-8")), delimiter="\t"))
            count = len(records)
        else:
            document = json.loads(raw)
            assert isinstance(document, dict)
            count = len(document[kind]) if kind != "contract" else None
        assert expected == count
        entries.append({"sourcePath": path, "sourceBlobSha": sha, "sourceBytes": len(raw),
                        "sourceSha256": hashlib.sha256(raw).hexdigest(),
                        "sourceAsset": "content-packs/locomotive-migration/migration/source-assets/" + name,
                        "sourceObjectId": row["sourceObjectId"], "observedRecordCount": count})
    return {"schemaVersion": 1, "donorCommit": ledger["sourceCommit"],
            "publicationStatus": "CANDIDATE", "runtimeImport": False,
            "actionDisposition": "INFORMATION_ONLY",
            "sourceNote": "Exact historical source bytes; Stage1/2 IDs and Stage3 contracts are not implicitly joined to later projections or granted current authority.",
            "documents": entries}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(project(), ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert OUT.read_text() == encoded
    else:
        OUT.write_text(encoded)
    print("EXTENDED_STAGE_DOCUMENTS_PASS 7 19 7 77 92 29")


if __name__ == "__main__":
    main()
