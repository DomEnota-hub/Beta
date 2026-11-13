#!/usr/bin/env python3
"""Negative tests: catalog listings cannot authorize factory drawing links."""
import unittest
from qa.validate_chme3_public_drawing_leads import LEDGER, TRIAGE, read, validate


class CatalogLeadTests(unittest.TestCase):
    def setUp(self):
        self.ledger, self.triage = read(LEDGER), read(TRIAGE)

    def check(self):
        return validate(self.ledger, self.triage)

    def test_baseline(self):
        self.assertEqual(self.check()["candidateTargetLookups"], 6)

    def test_factory_claim(self):
        self.ledger["manufacturerAuthorityVerified"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_unverified_archive_cannot_be_marked_acquired(self):
        self.ledger["sourceFilesAcquired"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_runtime_promotion(self):
        self.ledger["leads"][0]["runtimeImport"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_invented_document_number(self):
        self.ledger["leads"][0]["documentNumber"] = "FABRICATED"
        with self.assertRaises(AssertionError):
            self.check()

    def test_invented_sheet(self):
        self.ledger["leads"][0]["sheetNumbers"] = [1]
        with self.assertRaises(AssertionError):
            self.check()

    def test_wrong_variant(self):
        self.ledger["leads"][0]["variant"] = "chme3e"
        with self.assertRaises(AssertionError):
            self.check()

    def test_cross_variant_search_target(self):
        self.ledger["leads"][1]["investigationTargetIds"].append("CHME3T-SCH-EDB")
        with self.assertRaises(AssertionError):
            self.check()

    def test_unknown_target(self):
        self.ledger["leads"][0]["investigationTargetIds"][0] = "UNMAPPED"
        with self.assertRaises(AssertionError):
            self.check()

    def test_archive_link_tamper(self):
        self.ledger["leads"][0]["catalogPage"] = "https://example.org/not-source"
        with self.assertRaises(AssertionError):
            self.check()

    def test_removed_provenance_gate(self):
        self.ledger["requiredBeforePromotion"].pop()
        with self.assertRaises(AssertionError):
            self.check()

    def test_quarantine_removed(self):
        self.triage["chme3"]["targetGroups"][3]["reviewStatus"] = "RESOLVED"
        with self.assertRaises(AssertionError):
            self.check()


if __name__ == "__main__":
    unittest.main()
