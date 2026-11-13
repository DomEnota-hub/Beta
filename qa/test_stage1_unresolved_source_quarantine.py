#!/usr/bin/env python3
import copy
import tempfile
import unittest
from pathlib import Path

from qa.validate_stage1_unresolved_source_quarantine import ROOT, read, validate


class Stage1SourceQuarantineTest(unittest.TestCase):
    def setUp(self):
        self.chme3 = read(ROOT, "content-packs/diesel/chme3-family/migration/source-audit.json")
        self.ermak = read(ROOT, "content-packs/electric/ermak/migration/source-audit.json")
        self.identity = read(ROOT, "content-packs/electric/ermak/migration/source-identity-resolution.json")

    def check(self, root=ROOT):
        return validate(root, self.chme3, self.ermak, self.identity)

    def test_quarantine_baseline(self):
        result = self.check()
        self.assertEqual(result["chme3QuarantinedReferences"], 610)
        self.assertEqual(result["ermakSourceGapOccurrences"], 542)

    def test_missing_chme3_link_without_evidence_fails(self):
        self.chme3["unresolvedReferences"].pop()
        with self.assertRaises(AssertionError):
            self.check()

    def test_duplicate_chme3_reference_fails(self):
        self.chme3["unresolvedReferences"][0] = copy.deepcopy(self.chme3["unresolvedReferences"][1])
        with self.assertRaises(AssertionError):
            self.check()

    def test_unverified_ermak_auto_match_fails(self):
        self.identity["unresolvedSourceIds"][0]["automaticMatch"] = "ALLOWED"
        with self.assertRaises(AssertionError):
            self.check()

    def test_missing_diagnostic_auto_link_fails(self):
        self.identity["diagnosticGap"]["autoAddToStage7"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_candidate_promotion_fails(self):
        self.identity["runtimeImport"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_new_runtime_index_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "content-packs/electric/ermak/runtime-index.json"
            target.parent.mkdir(parents=True)
            target.write_text('{"packs":[]}')
            with self.assertRaises(AssertionError):
                self.check(root)


if __name__ == "__main__":
    unittest.main()
