import copy
import unittest

from qa import reconcile_discovery_outcomes as outcomes


class DiscoveryOutcomesTest(unittest.TestCase):
    def test_every_discovery_row_has_bounded_evidence_or_named_gate(self):
        result = outcomes.project()
        self.assertEqual(837, len(result["rows"]))
        self.assertEqual(
            {"PENDING_MAPPING": 206, "PENDING_EXTRACTION": 254,
             "DUPLICATE_SOURCE_MIRROR": 169, "DEFERRED_SCOPE": 208},
            result["countsByDiscoveryDisposition"],
        )
        self.assertEqual(837, len({(row["sourcePath"], row["sourceObjectId"])
                                   for row in result["rows"]}))
        self.assertTrue(all(row["evidencePaths"] or row["remainingGate"]
                            for row in result["rows"]))
        self.assertTrue(all(row["runtimePermissionGranted"] is False for row in result["rows"]))

        rows = {(row["sourcePath"], row["sourceObjectId"]): row
                for row in result["rows"]}
        exam = rows[("app/src/main/assets/exam_questions.json", "questions[*]")]
        self.assertEqual("EXCLUDED_BY_USER_SCOPE", exam["stageOneStatus"])
        technical = rows[("app/src/main/assets/technical/extended_emergency_runtime.json",
                          "records[*]")]
        self.assertEqual("SOURCE_PRESERVED_NEXT_PHASE", technical["stageOneStatus"])
        embedded = rows[("app/src/main/java/ru/railbrake/calculator/core/TechnicalDataRepository.kt",
                         "source-file")]
        self.assertEqual("SOURCE_REVIEWED_SEMANTIC_GATE", embedded["stageOneStatus"])
        mirror = rows[("patch/app/src/main/assets/exam_questions.json", "exact-mirror")]
        self.assertEqual("app/src/main/assets/exam_questions.json", mirror["aliasOf"])

    def test_blob_mismatch_cannot_become_an_evidence_match(self):
        ledger = copy.deepcopy(outcomes.load_ledger())
        row = next(row for row in ledger["rows"]
                   if row["sourcePath"] == "app/src/main/assets/technical/extended_emergency_runtime.json")
        row["sourceArtifactGitBlob"] = "0" * 40
        with self.assertRaises(AssertionError):
            outcomes.project(ledger)


if __name__ == "__main__":
    unittest.main()
