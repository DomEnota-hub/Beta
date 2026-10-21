#!/usr/bin/env python3
"""Join the provisional donor discovery rows to bounded, existing evidence."""

import argparse
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "docs/data-migration"
OUTPUT = DIRECTORY / "discovery-outcome-crosswalk.json"


def read(name):
    return json.loads((DIRECTORY / name).read_text())


def load_ledger():
    return read("source-discovery-ledger.json")


def indexed(name):
    data = read(name)
    return {(r["sourcePath"], r["sourceObjectId"]): r for r in data["rows"]}


def project(ledger=None):
    ledger = ledger if ledger is not None else load_ledger()
    names = ("technical-discovery-evidence.json", "document-discovery-evidence.json",
             "remaining-pending-mapping-evidence.json", "pending-extraction-review.json")
    sources = {name: indexed(name) for name in names}
    assert [len(sources[name]) for name in names] == [70, 128, 8, 254]
    original = ledger["rows"]
    assert len(original) == 837
    by_path = {}
    for row in original:
        by_path.setdefault(row["sourcePath"], []).append(row)
    results = []
    visited = {name: set() for name in names}
    for row in original:
        key = row["sourcePath"], row["sourceObjectId"]
        disposition = row["disposition"]
        evidence = []
        alias = None
        if disposition == "PENDING_MAPPING":
            matches = [(name, rows[key]) for name, rows in sources.items()
                       if name in names[:3] and key in rows]
            assert len(matches) == 1, key
            name, match = matches[0]
            visited[name].add(key)
            assert match["sourceArtifactGitBlob"] == row["sourceArtifactGitBlob"], key
            evidence = ["docs/data-migration/" + name]
            if name == names[0]:
                evidence += match["evidencePaths"]
                phase = match["phase"]
                status = {"INFORMATION": "SOURCE_PRESERVED_SEMANTIC_GATE",
                          "DIAGNOSTIC_SOURCE": "SOURCE_PRESERVED_NEXT_PHASE",
                          "SEPARATE_UI": "SEPARATE_UI_PHASE"}[phase]
                gate = {"INFORMATION": "OBJECT_SEMANTICS_SOURCE_AND_APPLICABILITY",
                        "DIAGNOSTIC_SOURCE": "DIAGNOSTIC_CARD_AND_EXECUTION_REVIEW",
                        "SEPARATE_UI": "VISUAL_DESIGN_AND_DISPLAY_CONTRACT"}[phase]
            elif name == names[1]:
                maps = match["dispositionMapRows"]
                assert sum(maps.values()) == match["matchedObjectLedgerRows"]
                evidence += ["docs/data-migration/" + path for path in maps]
                status, gate = "DOCUMENT_OBJECTS_MAPPED", "CANONICAL_SEMANTICS_AND_SOURCE_AUTHORITY"
            else:
                evidence += match["evidencePaths"]
                kind = match["evidenceKind"]
                if kind == "STRUCTURAL_PARITY_ACCESS_POLICY_OPEN":
                    status, gate = "EXCLUDED_BY_USER_SCOPE", "EXAM_ACCESS_AND_HOSTING_DECISION"
                elif kind == "ARCHIVE_MEMBER_REVIEW_ONLY":
                    status, gate = "ARCHIVE_MEMBER_REVIEWED", "ARCHIVE_MEMBER_OBJECT_SEMANTICS"
                else:
                    assert kind == "EXACT_BLOB_ALIAS_TO_NON_RUNTIME_SOURCE_SNAPSHOT"
                    status, gate = "SOURCE_PRESERVED_NEXT_PHASE", "PANTOGRAPH_REFERENCE_REVIEW"
        elif disposition == "PENDING_EXTRACTION":
            name = names[3]
            assert key in sources[name], key
            match = sources[name][key]
            visited[name].add(key)
            assert match["sourceArtifactGitBlob"] == row["sourceArtifactGitBlob"], key
            evidence = ["docs/data-migration/" + name] + match["evidencePaths"]
            status = "SOURCE_REVIEWED_SEMANTIC_GATE"
            gate = match["remainingGate"]
            assert gate and match["finalObjectDisposition"] is None
        elif disposition == "DUPLICATE_SOURCE_MIRROR":
            assert row["sourcePath"].startswith("patch/")
            alias = row["sourcePath"].removeprefix("patch/")
            assert any(other["sourceArtifactGitBlob"] == row["sourceArtifactGitBlob"]
                       for other in by_path.get(alias, [])), key
            status, gate = "EXACT_SOURCE_MIRROR", "FOLLOW_PRIMARY_SOURCE_OBJECTS"
        else:
            assert disposition == "DEFERRED_SCOPE", key
            status, gate = "FUNCTIONAL_OR_TEST_SOURCE", "FUNCTIONAL_OR_TEST_STAGE_REVIEW"
        for path in evidence:
            assert (ROOT / path).is_file(), (key, path)
        results.append({
            "sourcePath": key[0], "sourceObjectId": key[1],
            "sourceArtifactGitBlob": row["sourceArtifactGitBlob"],
            "discoveryDisposition": disposition, "stageOneStatus": status,
            "evidencePaths": evidence, "aliasOf": alias, "remainingGate": gate,
            "runtimePermissionGranted": False,
        })
    assert all(visited[name] == set(sources[name]) for name in names)
    counts = dict(sorted(Counter(r["discoveryDisposition"] for r in results).items()))
    statuses = dict(sorted(Counter(r["stageOneStatus"] for r in results).items()))
    return {
        "schemaVersion": 1, "donorCommit": ledger["sourceCommit"],
        "scope": "837 provisional source-file/field-group discovery rows; object-level disposition maps remain authoritative",
        "note": "This crosswalk reconciles discovery to existing evidence and named gates. A source snapshot, mirrored file, or historical claim is not an approved canonical action or a complete semantic transfer. No old ledger status or runtime index changes.",
        "countsByDiscoveryDisposition": counts, "countsByStageOneStatus": statuses,
        "rows": results,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(project(), ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert OUTPUT.read_text() == encoded
    else:
        OUTPUT.write_text(encoded)
    print("DISCOVERY_OUTCOMES_PASS 837")


if __name__ == "__main__":
    main()
