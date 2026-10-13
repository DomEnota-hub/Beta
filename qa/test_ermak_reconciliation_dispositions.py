"""Fail-closed checks for resolved identities over immutable Ermak source packs."""
import copy
import unittest
from pathlib import Path

import validate_ermak_system_link_reconciliation as reconciliation


ROOT = Path(__file__).resolve().parents[1]


class ErmakResolutionTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(hasattr(reconciliation, "load_resolution"), "resolution loader is missing")
        self.assertTrue(hasattr(reconciliation, "validate_resolution"), "resolution validator is missing")

    def test_same_dissertation_but_distinct_historical_records(self):
        result = reconciliation.validate_resolution(ROOT)
        records = result["sourceRecords"]
        r41 = [x for x in records if x["legacySourceId"] == "ER-SRC-041"]
        r39 = [x for x in records if x["legacySourceId"] == "ER-SRC-039"]
        self.assertEqual(len(r41), 2)
        self.assertEqual(len({x["bibliographicWorkId"] for x in r41}), 1)
        self.assertEqual(len({x["publicationId"] for x in r41}), 1)
        self.assertEqual(len({x["publicationId"] for x in r39}), 2)
        self.assertEqual(len({x["originalUrl"] for x in r39}), 2)

    def test_colliding_039_cannot_be_merged(self):
        data = reconciliation.load_resolution(ROOT)
        first, second = [x for x in data["sourceRecords"] if x["legacySourceId"] == "ER-SRC-039"]
        broken = copy.deepcopy(data)
        next(x for x in broken["sourceRecords"] if x["sourceEntryId"] == second["sourceEntryId"])["publicationId"] = first["publicationId"]
        with self.assertRaises(AssertionError):
            reconciliation.validate_resolution(ROOT, broken)
        broken = copy.deepcopy(data)
        next(x for x in broken["sourceRecords"] if x["sourceEntryId"] == second["sourceEntryId"])["bibliographicWorkId"] = first["bibliographicWorkId"]
        with self.assertRaises(AssertionError):
            reconciliation.validate_resolution(ROOT, broken)

    def test_original_record_and_common_041_identity_are_immutable(self):
        data = reconciliation.load_resolution(ROOT)
        broken = copy.deepcopy(data)
        broken["sourceRecords"][0]["originalDocument"] = "invented description"
        with self.assertRaises(AssertionError):
            reconciliation.validate_resolution(ROOT, broken)
        broken = copy.deepcopy(data)
        next(x for x in broken["sourceRecords"] if x["sourceEntryId"] == "ermak.source.dp011_rgups_data")["bibliographicWorkId"] = "ermak.work.tass10_training"
        with self.assertRaises(AssertionError):
            reconciliation.validate_resolution(ROOT, broken)

    def test_unknown_source_ids_stay_unresolved(self):
        data = reconciliation.load_resolution(ROOT)
        self.assertEqual([x["sourceId"] for x in data["unresolvedSourceIds"]],
                         ["ER-SRC-001", "ER-SRC-017", "ER-SRC-018", "ER-SRC-020", "ER-SRC-021"])
        broken = copy.deepcopy(data)
        broken["unresolvedSourceIds"][0]["disposition"] = "LINKED"
        with self.assertRaises(AssertionError):
            reconciliation.validate_resolution(ROOT, broken)

    def test_evidence_and_diagnostic_gap_cannot_be_activated(self):
        data = reconciliation.load_resolution(ROOT)
        self.assertFalse(data["runtimeImport"])
        self.assertFalse(data["technicalEvidence"]["universalRelationActive"])
        self.assertFalse(data["diagnosticGap"]["autoAddToStage7"])
        broken = copy.deepcopy(data)
        broken["technicalEvidence"]["universalRelationActive"] = True
        with self.assertRaises(AssertionError):
            reconciliation.validate_resolution(ROOT, broken)
        broken = copy.deepcopy(data)
        broken["diagnosticGap"]["autoAddToStage7"] = True
        with self.assertRaises(AssertionError):
            reconciliation.validate_resolution(ROOT, broken)


if __name__ == "__main__":
    unittest.main()
