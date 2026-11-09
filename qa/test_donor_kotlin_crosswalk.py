#!/usr/bin/env python3
"""Regression tests for fail-closed pinned Kotlin source accounting."""
import copy
import json
import unittest

from qa.validate_donor_kotlin_crosswalk import MANIFEST, ROOT, validate


class DonorKotlinCrosswalkTest(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.tree = {
            "truncated": False,
            "tree": [
                {"type": "blob", "path": row["sourcePath"], "sha": row["donorBlobSha"]}
                for row in self.manifest["sources"]
            ],
        }

    def test_complete_baseline(self):
        result = validate(ROOT, self.manifest, self.tree)
        self.assertEqual(result["donorKotlinSources"], 74)
        self.assertGreater(result["statusCounts"]["NOT_MIGRATED"], 0)

    def test_missing_source_fails(self):
        self.tree["tree"].pop()
        with self.assertRaises(AssertionError):
            validate(ROOT, self.manifest, self.tree)

    def test_modified_source_sha_fails(self):
        self.tree["tree"][0]["sha"] = "0" * 40
        with self.assertRaises(AssertionError):
            validate(ROOT, self.manifest, self.tree)

    def test_unproven_migration_fails(self):
        self.manifest["sources"][0]["status"] = "MIGRATED"
        self.manifest["sources"][0]["userJourneyVerified"] = True
        with self.assertRaises(AssertionError):
            validate(ROOT, self.manifest, self.tree)

    def test_missing_target_fails(self):
        row = next(r for r in self.manifest["sources"] if r["targetPaths"])
        row["targetPaths"] = ["feature-history/src/main/kotlin/ru/railbrake/calculator/history/Nonexistent.kt"]
        with self.assertRaises(AssertionError):
            validate(ROOT, self.manifest, self.tree)

    def test_duplicate_source_fails(self):
        self.manifest["sources"][1] = copy.deepcopy(self.manifest["sources"][0])
        with self.assertRaises(AssertionError):
            validate(ROOT, self.manifest, self.tree)

    def test_incomplete_git_tree_fails(self):
        self.tree["truncated"] = True
        with self.assertRaises(AssertionError):
            validate(ROOT, self.manifest, self.tree)

    def test_path_escape_fails(self):
        row = next(r for r in self.manifest["sources"] if r["targetPaths"])
        row["targetPaths"] = ["../outside/src/main/Untrusted.kt"]
        with self.assertRaises(AssertionError):
            validate(ROOT, self.manifest, self.tree)


if __name__ == "__main__":
    unittest.main()
