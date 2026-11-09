#!/usr/bin/env python3
"""Regression tests for the per-target unresolved source-link triage."""
import copy
import unittest

from qa.validate_stage1_source_link_triage import ROOT, LEDGER, CHME, ERMAK, read, validate


class Stage1SourceLinkTriageTests(unittest.TestCase):
    def setUp(self):
        self.ledger = read(ROOT, LEDGER)
        self.chme = read(ROOT, CHME)
        self.ermak = read(ROOT, ERMAK)

    def check(self):
        return validate(self.ledger, self.chme, self.ermak)

    def test_baseline(self):
        result = self.check()
        self.assertEqual(result["chme3DistinctTargets"], 19)
        self.assertEqual(result["ermakUnresolvedIds"], 57)
        self.assertEqual(result["ermakSourceGapOccurrences"], 542)
        self.assertEqual(set(result["chme3CrossVariantTargets"]),
                         {"CHME3T-SCH-EDB", "CHME3T-EQ-EDB-CONTROL"})

    def test_chme_missing_target_fails(self):
        self.ledger["chme3"]["targetGroups"].pop()
        with self.assertRaises(AssertionError):
            self.check()

    def test_chme_wrong_target_count_fails(self):
        self.ledger["chme3"]["targetGroups"][0]["referenceCount"] += 1
        with self.assertRaises(AssertionError):
            self.check()

    def test_chme_wrong_variant_fails(self):
        self.ledger["chme3"]["targetGroups"][0]["variants"] = ["chme3"]
        with self.assertRaises(AssertionError):
            self.check()

    def test_chme_unmapped_scheme_cross_variant_cannot_be_silenced(self):
        scheme = next(x for x in self.ledger["chme3"]["targetGroups"]
                      if x["sourceTargetId"] == "CHME3T-SCH-EDB")
        scheme["variantApplicabilityUnverified"] = False
        with self.assertRaises(AssertionError):
            self.check()

    def test_chme_source_mapping_tamper_fails(self):
        self.chme["mappings"][0]["sourceId"] = self.ledger["chme3"]["targetGroups"][0]["sourceTargetId"]
        with self.assertRaises(AssertionError):
            self.check()

    def test_chme_unsafe_promotion_fails(self):
        self.ledger["chme3"]["targetGroups"][0]["runtimeImport"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_ermak_missing_id_fails(self):
        self.ledger["ermak"]["sourceIds"].pop()
        with self.assertRaises(AssertionError):
            self.check()

    def test_ermak_wrong_occurrences_fails(self):
        self.ledger["ermak"]["sourceIds"][0]["occurrences"] += 1
        with self.assertRaises(AssertionError):
            self.check()

    def test_ermak_ambiguous_auto_match_fails(self):
        target = next(x for x in self.ledger["ermak"]["sourceIds"]
                      if x["sourceDisposition"] == "AMBIGUOUS_SOURCE_ID")
        target["reviewStatus"] = "LINKED"
        with self.assertRaises(AssertionError):
            self.check()

    def test_ermak_registry_key_tamper_fails(self):
        self.ledger["ermak"]["sourceIds"][0]["registryKeys"] = ["invented"]
        with self.assertRaises(AssertionError):
            self.check()

    def test_wrong_donor_sha_fails(self):
        self.ledger["donorCommit"] = "unverified"
        with self.assertRaises(AssertionError):
            self.check()


if __name__ == "__main__":
    unittest.main()
