"""Join the pinned donor ZIP manifest to the provisional source discovery ledger.

This is source-file accounting. It never decides content authority or runtime import.
"""

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/data-migration/legacy-zip-member-manifest.json"
LEDGER = ROOT / "docs/data-migration/source-discovery-ledger.json"
OUTPUT = ROOT / "docs/data-migration/legacy-zip-discovery-overlay.json"
REVIEW = "docs/data-migration/LEGACY_ZIP_ARCHIVE_ONLY_REVIEW_2026-10-13.md"


def build_overlay(manifest, ledger):
    if manifest["donorCommit"] != ledger["sourceCommit"]:
        raise ValueError("source commit differs between manifest and discovery ledger")
    if len(manifest["members"]) != 60:
        raise ValueError("expected 60 members")

    paths = {row["sourcePath"]: row for row in ledger["rows"]}
    zip_row = paths.get("RailBrakeCalculator.zip")
    if not zip_row or zip_row["sourceArtifactGitBlob"] != manifest["archive"]["gitBlobSha"]:
        raise ValueError("archive container blob differs from discovery ledger")

    seen = set()
    members = []
    counts = {"exactAlias": 0, "changedCounterpart": 0, "archiveOnly": 0}
    for member in manifest["members"]:
        path = member["path"]
        if path in seen:
            raise ValueError(f"duplicate ZIP member: {path}")
        seen.add(path)
        counterpart_path = path if path in paths else f"patch/{path}" if f"patch/{path}" in paths else None
        counterpart = paths[counterpart_path] if counterpart_path else None
        if counterpart:
            expected = member["samePathDonorBlob"] if counterpart_path == path else member["pinnedPatchBlob"]
            if expected != counterpart["sourceArtifactGitBlob"]:
                raise ValueError(f"counterpart blob mismatch: {path}")
            if member["comparison"] == "EXACT_BLOB_IN_PINNED_TREE":
                if member["gitBlobSha"] != expected:
                    raise ValueError(f"exact alias blob mismatch: {path}")
                review = "EXACT_BLOB_ALIAS"
                counts["exactAlias"] += 1
            else:
                review = "CHANGED_COUNTERPART_REVIEWED"
                counts["changedCounterpart"] += 1
        else:
            if member["samePathDonorBlob"] or member["pinnedPatchBlob"]:
                raise ValueError(f"missing counterpart discovery row: {path}")
            review = "ARCHIVE_ONLY_REVIEWED"
            counts["archiveOnly"] += 1

        member_discovery_path = f"RailBrakeCalculator.zip!RailBrakeCalculator/{path}"
        if member_discovery_path not in paths:
            member_discovery_path = None
        elif paths[member_discovery_path]["sourceArtifactGitBlob"] != zip_row["sourceArtifactGitBlob"]:
            raise ValueError(f"embedded member discovery blob mismatch: {path}")

        members.append({
            "memberPath": path,
            "memberGitBlobSha": member["gitBlobSha"],
            "containerDiscoveryPath": "RailBrakeCalculator.zip",
            "memberDiscoveryPath": member_discovery_path,
            "counterpartDiscoveryPath": counterpart_path,
            "counterpartGitBlobSha": counterpart["sourceArtifactGitBlob"] if counterpart else None,
            "sourceFileReview": review,
            "reviewDocument": REVIEW,
            "finalObjectDisposition": None,
            "runtimeImport": False,
        })

    if counts != {"exactAlias": 14, "changedCounterpart": 33, "archiveOnly": 13}:
        raise ValueError(f"unexpected comparison groups: {counts}")
    return {
        "schemaVersion": 1,
        "status": "SOURCE_FILE_REVIEW_ONLY",
        "sourceCommit": manifest["donorCommit"],
        "archivePath": manifest["archive"]["sourcePath"],
        "archiveGitBlobSha": manifest["archive"]["gitBlobSha"],
        "manifestPath": MANIFEST.relative_to(ROOT).as_posix(),
        "discoveryLedgerPath": LEDGER.relative_to(ROOT).as_posix(),
        "counts": counts,
        "members": members,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-output", action="store_true")
    args = parser.parse_args()
    overlay = build_overlay(json.loads(MANIFEST.read_text()), json.loads(LEDGER.read_text()))
    rendered = json.dumps(overlay, ensure_ascii=False, indent=2) + "\n"
    if args.verify_output:
        if not OUTPUT.exists() or OUTPUT.read_text() != rendered:
            raise SystemExit("ZIP discovery overlay differs from pinned inputs")
    else:
        OUTPUT.write_text(rendered)
    print("LEGACY_ZIP_DISCOVERY_PASS", len(overlay["members"]), overlay["counts"])


if __name__ == "__main__":
    main()
