#!/usr/bin/env python3
"""Negative regression tests for the Ermak RE1 public-mirror source gap."""
import copy
import unittest

from qa.validate_ermak_re1_public_mirror import EVIDENCE, AUDIT, TRIAGE, read, validate


class ErmakRe1PublicMirrorTests(unittest.TestCase):
    def setUp(self):
        self.evidence, self.audit, self.triage = (
            read(EVIDENCE), read(AUDIT), read(TRIAGE))

    def check(self):
        return validate(self.evidence, self.audit, self.triage)

    def test_baseline(self):
        self.assertEqual(self.check()["unresolvedOccurrences"], 56)

    def test_source_id_drift(self):
        self.evidence["targetSourceId"] = "ER-SRC-039"
        with self.assertRaises(AssertionError):
            self.check()

    def test_unverified_publication_identity(self):
        self.evidence["originalDocumentMatchedToSourceId"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_fake_current_edition(self):
        self.evidence["officialCurrentEditionVerified"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_wrong_msud_profile(self):
        self.evidence["publication"]["describedControlSystem"] = "МСУД-015"
        with self.assertRaises(AssertionError):
            self.check()

    def test_msud015_not_implicitly_applicable(self):
        self.evidence["msud015ApplicabilityVerified"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_runtime_promotion(self):
        self.evidence["runtimeImport"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_crew_action_promotion(self):
        self.evidence["crewActionAuthorized"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_occurrence_drift(self):
        self.evidence["pinnedUnresolvedOccurrences"] = 55
        with self.assertRaises(AssertionError):
            self.check()

    def test_ledger_promotion(self):
        x = next(x for x in self.triage["ermak"]["sourceIds"]
                 if x["sourceId"] == self.evidence["targetSourceId"])
        x["runtimeImport"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_wrong_mirror_locator(self):
        self.evidence["publication"]["thirdPartyTextUrl"] = "https://invalid.example"
        with self.assertRaises(AssertionError):
            self.check()

    def test_unverified_clause_mapping(self):
        self.evidence["exactClausesMapped"] = True
        with self.assertRaises(AssertionError):
            self.check()


if __name__ == "__main__":
    unittest.main()
