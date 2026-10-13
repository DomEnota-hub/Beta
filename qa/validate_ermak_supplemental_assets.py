#!/usr/bin/env python3
"""Verify pinned Ermak source assets without granting their historical links authority."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

from migrate_ermak_supplemental_assets import DEST, build


def validate(root: Path, check_canonical: bool = True) -> int:
    actual = (root / DEST).read_text(encoding="utf-8")
    expected = json.dumps(build(root), ensure_ascii=False, separators=(",", ":")) + "\n"
    assert actual == expected, "supplemental asset index differs from pinned sources"
    index = json.loads(actual)
    assert index["publicationStatus"] == "CANDIDATE"
    assert index["actionDisposition"] == "INFORMATION_ONLY"
    assert index["runtimeImport"] is False
    assert index["canonicalMappingStatus"] == "PENDING_OBJECT_RECONCILIATION"
    assert index["missingDiagnosticLinkIds"] == ["ER-DIAG-136"]
    if check_canonical:
        pack_dir = root / "content-packs/electric/ermak/diagnostics/recommended"
        ids = [entry["id"] for path in sorted(pack_dir.glob("*.pack.json"))
               for entry in json.loads(path.read_text(encoding="utf-8"))["entries"]]
        assert len(ids) == 136 and len(set(ids)) == 136, "canonical diagnostic count/IDs"
        source_path = root / index["assets"][0]["destinationPath"]
        links = json.loads(gzip.decompress(source_path.read_bytes()))
        linked_ids = set(links["indexes"]["byDiagnostic"])
        assert sorted(set(ids) - linked_ids) == index["missingDiagnosticLinkIds"]
        assert not linked_ids - set(ids), "unknown linked diagnostic"
        assert all(e["publicationStatus"] == "CANDIDATE"
                   for path in sorted(pack_dir.glob("*.pack.json"))
                   for e in json.loads(path.read_text(encoding="utf-8"))["entries"])
    return len(index["assets"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--source-only", action="store_true")
    args = parser.parse_args()
    print("ERMAK_SUPPLEMENTAL_ASSETS_PASS", validate(args.root, not args.source_only))
