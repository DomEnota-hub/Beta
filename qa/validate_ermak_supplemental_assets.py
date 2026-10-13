#!/usr/bin/env python3
"""Verify pinned Ermak source assets without granting their historical links authority."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

from migrate_ermak_supplemental_assets import DEST, audit_links, build


def compare_canonical_ids(indexes: dict, canonical: dict) -> dict:
    equipment = set(indexes["byEquipment"])
    diagnostics = set(indexes["byDiagnostic"])
    schemes = set(indexes["byScheme"])
    knowledge = {id_ for group in indexes.values() for obj in group.values()
                 for id_ in obj.get("knowledgeIds", [])}
    knowledge.update(obj["equipmentArticleId"] for obj in indexes["byEquipment"].values())
    return {
        "missingEquipmentTargets": sorted(equipment - canonical["equipment"]),
        "missingKnowledgeTargets": sorted(knowledge - canonical["knowledge"]),
        "missingDiagnosticTargets": sorted(diagnostics - canonical["diagnostics"]),
        "missingSchemeTargets": sorted(schemes - canonical["schemes"]),
        "unreferencedKnowledgeIds": sorted(canonical["knowledge"] - knowledge),
        "missingDiagnosticIndexIds": sorted(canonical["diagnostics"] - diagnostics),
        "extraEquipmentIndexIds": sorted(canonical["equipment"] - equipment),
        "extraSchemeIndexIds": sorted(canonical["schemes"] - schemes),
        "knowledgeReferenceIds": len(knowledge),
    }


def canonical_entries(root: Path, relative: str) -> list:
    paths = sorted((root / relative).glob("*.pack.json"))
    assert paths, relative
    entries = [entry for path in paths
               for entry in json.loads(path.read_text(encoding="utf-8"))["entries"]]
    ids = [entry["id"] for entry in entries]
    assert len(ids) == len(set(ids)), relative + " duplicate canonical ID"
    assert all(entry["publicationStatus"] == "CANDIDATE" for entry in entries)
    return entries


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
    links_path = root / index["assets"][0]["destinationPath"]
    links = json.loads(gzip.decompress(links_path.read_bytes()))
    assert index["sourceGraphAudit"] == audit_links(links)
    assert index["sourceGraphAudit"]["reciprocalDiagnosticSchemePairs"] == 523
    assert index["sourceGraphAudit"]["unresolvedInternalReferences"] == []
    if check_canonical:
        paths = {
            "equipment": "content-packs/electric/ermak/atlas/equipment",
            "knowledge": "content-packs/electric/ermak/technical-data/knowledge",
            "diagnostics": "content-packs/electric/ermak/diagnostics/recommended",
            "schemes": "content-packs/electric/ermak/atlas/schemes",
        }
        canonical = {kind: {e["id"] for e in canonical_entries(root, path)}
                     for kind, path in paths.items()}
        assert {kind: len(ids) for kind, ids in canonical.items()} == {
            "equipment": 111, "knowledge": 138, "diagnostics": 136, "schemes": 22}
        result = compare_canonical_ids(links["indexes"], canonical)
        assert result == {
            "missingEquipmentTargets": [], "missingKnowledgeTargets": [],
            "missingDiagnosticTargets": [], "missingSchemeTargets": [],
            "unreferencedKnowledgeIds": [],
            "missingDiagnosticIndexIds": index["missingDiagnosticLinkIds"],
            "extraEquipmentIndexIds": [], "extraSchemeIndexIds": [],
            "knowledgeReferenceIds": 138,
        }, result
        source_map = json.loads(gzip.decompress(
            (root / index["assets"][1]["destinationPath"]).read_bytes()))
        assert {s["id"] for s in source_map["systems"]} == set(links["indexes"]["bySystem"])
    return len(index["assets"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--source-only", action="store_true")
    args = parser.parse_args()
    print("ERMAK_SUPPLEMENTAL_ASSETS_PASS", validate(args.root, not args.source_only))
