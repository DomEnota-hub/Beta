"""Regression coverage for the 996/р vs 592/р identity boundary."""
import copy
import unittest

from qa.validate_ermak_996r_edition import (
    ROOT, EVIDENCE, AUDIT, TRIAGE, load, validate,
)


class Ermak996rEditionTests(unittest.TestCase):
    def setUp(self):
        self.evidence = load(ROOT, EVIDENCE)
        self.audit = load(ROOT, AUDIT)
        self.triage = load(ROOT, TRIAGE)

    def check(self):
        return validate(self.evidence, self.audit, self.triage)

    def test_original_order_and_amendment_are_distinct(self):
        result = self.check()
        self.assertEqual(result["unresolvedOccurrences"], 57)
        self.assertEqual(result["originalOrder"], "996/р (2022-04-12)")
        self.assertEqual(result["amendment"], "592/р (2024-03-05)")
        self.assertFalse(result["sourceResolved"])

    def test_amendment_cannot_replace_original_order_date(self):
        self.evidence["originalDocument"]["orderDate"] = "2024-03-05"
        with self.assertRaises(AssertionError):
            self.check()

    def test_bibliography_cannot_claim_current_edition(self):
        self.evidence["currentEditionVerified"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_secondary_catalog_cannot_claim_official_text(self):
        self.evidence["officialFullTextVerified"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_unverified_clause_cannot_become_crew_action(self):
        self.evidence["crewActionAuthorized"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_source_gap_must_not_be_auto_resolved(self):
        self.evidence["sourceIdResolved"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_wrong_source_id_is_rejected(self):
        self.evidence["targetSourceId"] = "ER-AUDIT-NORM-2580R-2025"
        with self.assertRaises(AssertionError):
            self.check()

    def test_occurrence_drift_is_rejected(self):
        self.evidence["pinnedUnresolvedOccurrences"] = 56
        with self.assertRaises(AssertionError):
            self.check()

    def test_runtime_promotion_is_rejected(self):
        self.evidence["runtimeImport"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_triage_promotion_is_rejected(self):
        match = next(r for r in self.triage["ermak"]["sourceIds"]
                     if r["sourceId"] == self.evidence["targetSourceId"])
        match["reviewStatus"] = "LINKED"
        with self.assertRaises(AssertionError):
            self.check()


if __name__ == "__main__":
    unittest.main()
