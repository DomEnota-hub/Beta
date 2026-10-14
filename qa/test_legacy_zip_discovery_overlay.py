import json
import unittest
from pathlib import Path

from build_legacy_zip_discovery_overlay import build_overlay


ROOT = Path(__file__).resolve().parents[1]


class LegacyZipDiscoveryOverlayTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "docs/data-migration/legacy-zip-member-manifest.json").read_text())
        cls.ledger = json.loads((ROOT / "docs/data-migration/source-discovery-ledger.json").read_text())

    def test_all_members_keep_identity_and_no_runtime_promotion(self):
        overlay = build_overlay(self.manifest, self.ledger)
        self.assertEqual(60, len(overlay["members"]))
        self.assertEqual({"exactAlias": 14, "changedCounterpart": 33, "archiveOnly": 13}, overlay["counts"])
        self.assertEqual(
            {(row["path"], row["gitBlobSha"]) for row in self.manifest["members"]},
            {(row["memberPath"], row["memberGitBlobSha"]) for row in overlay["members"]},
        )
        self.assertTrue(all(row["runtimeImport"] is False for row in overlay["members"]))
        self.assertTrue(all(row["finalObjectDisposition"] is None for row in overlay["members"]))

    def test_archive_only_members_do_not_acquire_an_invented_tree_row(self):
        overlay = build_overlay(self.manifest, self.ledger)
        history = next(row for row in overlay["members"] if row["memberPath"].endswith("/HistoryRepository.kt"))
        self.assertEqual("ARCHIVE_ONLY_REVIEWED", history["sourceFileReview"])
        self.assertIsNone(history["counterpartDiscoveryPath"])
        self.assertEqual("RailBrakeCalculator.zip", history["containerDiscoveryPath"])
        self.assertEqual(
            "RailBrakeCalculator.zip!RailBrakeCalculator/app/src/main/java/ru/railbrake/calculator/data/HistoryRepository.kt",
            history["memberDiscoveryPath"],
        )
        self.assertEqual(3, sum(row["memberDiscoveryPath"] is not None for row in overlay["members"]))

    def test_rejects_wrong_counterpart_blob(self):
        ledger = json.loads(json.dumps(self.ledger))
        row = next(x for x in ledger["rows"] if x["sourcePath"] == "app/src/main/java/ru/railbrake/calculator/MainActivity.kt")
        row["sourceArtifactGitBlob"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "counterpart blob"):
            build_overlay(self.manifest, ledger)

    def test_rejects_a_missing_member(self):
        manifest = json.loads(json.dumps(self.manifest))
        manifest["members"].pop()
        with self.assertRaisesRegex(ValueError, "60 members"):
            build_overlay(manifest, self.ledger)


if __name__ == "__main__":
    unittest.main()
