#!/usr/bin/env python3
"""Exercise source-link target checking with the real pinned link index."""
import gzip
import json
import unittest
from pathlib import Path

from validate_ermak_supplemental_assets import compare_canonical_ids


class ErmakLinkIdAuditTest(unittest.TestCase):
    def test_missing_knowledge_target_is_reported_without_creating_an_alias(self):
        path = Path("content-packs/electric/ermak/migration/source-assets/ermak_links.json.gz")
        indexes = json.loads(gzip.decompress(path.read_bytes()))["indexes"]
        knowledge = {id_ for group in indexes.values() for obj in group.values()
                     for id_ in obj.get("knowledgeIds", [])}
        knowledge.update(obj["equipmentArticleId"] for obj in indexes["byEquipment"].values())
        victim = sorted(knowledge)[0]
        canonical = {
            "equipment": set(indexes["byEquipment"]),
            "knowledge": knowledge - {victim},
            "diagnostics": set(indexes["byDiagnostic"]) | {"ER-DIAG-136"},
            "schemes": set(indexes["byScheme"]),
        }
        result = compare_canonical_ids(indexes, canonical)
        self.assertEqual(result["missingKnowledgeTargets"], [victim])
        self.assertEqual(result["missingDiagnosticIndexIds"], ["ER-DIAG-136"])


if __name__ == "__main__":
    unittest.main()
