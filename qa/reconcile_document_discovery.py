#!/usr/bin/env python3
"""Join provisional document discovery groups to exact 1,748-object maps."""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from validate_locomotive_document_coverage import MAPS, validate

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "docs/data-migration"
DESTINATION = DIRECTORY / "document-discovery-evidence.json"


def project():
    assert validate(ROOT) == 1748
    discovery = json.loads((DIRECTORY / "source-discovery-ledger.json").read_text())
    ledger = json.loads((DIRECTORY / "document-object-ledger.json").read_text())
    assert discovery["sourceCommit"] == ledger["donorCommit"]
    by_path = defaultdict(list)
    for row in ledger["rows"]:
        by_path[row["sourcePath"]].append(row)
    map_name_by_pointer = {}
    for name in MAPS:
        disposition = json.loads((DIRECTORY / name).read_text())
        for row in disposition["rows"]:
            map_name_by_pointer[row["sourcePath"], row["sourcePointer"]] = name

    source_groups = [row for row in discovery["rows"] if row["sourcePath"] in by_path]
    assert len(source_groups) == 128 and len({row["sourcePath"] for row in source_groups}) == 70
    result = []
    joined_objects = set()
    for group in source_groups:
        name = group["sourceObjectId"]
        assert group["disposition"] == "PENDING_MAPPING"
        assert all(row["sourceBlobSha"] == group["sourceArtifactGitBlob"]
                   for row in by_path[group["sourcePath"]])
        if name == "$":
            matched = by_path[group["sourcePath"]]
            assert group["sourceCount"] == 1
            assert len(matched) in (24, 34)
            scope = "WHOLE_FILE_GROUP"
        else:
            assert name.endswith("[*]")
            prefix = "/" + name[:-3] + "/"
            matched = [row for row in by_path[group["sourcePath"]]
                       if row["sourcePointer"].startswith(prefix) and
                       len(row["sourcePointer"].split("/")) == 3]
            assert len(matched) == group["sourceCount"], (group["sourcePath"], name)
            scope = "TOP_LEVEL_ARRAY_ELEMENTS"
        sources = Counter(map_name_by_pointer[group["sourcePath"], row["sourcePointer"]]
                          for row in matched)
        for row in matched:
            key = group["sourcePath"], row["sourcePointer"]
            assert key not in joined_objects
            joined_objects.add(key)
        result.append({
            "sourcePath": group["sourcePath"],
            "sourceObjectId": name,
            "sourceArtifactGitBlob": group["sourceArtifactGitBlob"],
            "sourceCount": group["sourceCount"],
            "discoveryDisposition": group["disposition"],
            "joinScope": scope,
            "matchedObjectLedgerRows": len(matched),
            "dispositionMapRows": dict(sorted(sources.items())),
            "publicationDecision": None,
        })
    assert sum(row["joinScope"] == "WHOLE_FILE_GROUP" for row in result) == 2
    assert len(joined_objects) == sum(row["matchedObjectLedgerRows"] for row in result) == 1123
    return {
        "schemaVersion": 1,
        "donorCommit": ledger["donorCommit"],
        "scope": "70 documentary source files / 128 discovered groups",
        "note": "Exact group-to-object evidence: these 128 discovery groups cover 1,123 object rows; the other 625 root/metadata object rows in the 1,748-row ledger have separate exact dispositions but were never enumerated as discovery groups. No discovery disposition or publication status is changed.",
        "rows": result,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(project(), ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert DESTINATION.read_text() == encoded
    else:
        DESTINATION.write_text(encoded)
    print("DOCUMENT_DISCOVERY_EVIDENCE_PASS", 70, 128)


if __name__ == "__main__":
    main()
