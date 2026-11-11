"""Negative and positive tests for the Stage 15 built-APK integration gate."""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from check_stage15_integration_apk import ApkAuditError, check_apk


ROOT = Path(__file__).resolve().parent.parent
PACK_ROOT = ROOT / "content-packs"
INDEX = json.loads((PACK_ROOT / "electric/vl80s/runtime-index.json").read_text(encoding="utf-8"))


class Stage15ApkIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.apk = Path(self.tmp.name) / "fixture.apk"

    def build(self, *, omit=(), modify=None, extra=None):
        omit = set(omit)
        modify = modify or {}
        extra = extra or {}
        paths = [
            "electric/vl80s/runtime-index.json",
            INDEX["profileCatalog"],
            *INDEX["featureIndexes"].values(),
            *(p for p in INDEX["packs"] if "/recommended/" not in p and "/extended/" not in p),
            "common/knowledge/articles.pack.json",
            "common/safety/articles.pack.json",
            "common/first-aid/topics.pack.json",
            "crew-reference/summaries.json",
        ]
        with ZipFile(self.apk, "w", compression=ZIP_DEFLATED) as apk:
            apk.writestr("AndroidManifest.xml", b"fixture")
            apk.writestr("classes.dex", b"fixture")
            for relative in paths:
                asset = "assets/" + relative
                if asset in omit:
                    continue
                source = (PACK_ROOT / relative).read_bytes()
                if asset in modify:
                    obj = json.loads(source)
                    modify[asset](obj)
                    source = json.dumps(obj, ensure_ascii=False).encode("utf-8")
                apk.writestr(asset, source)
            for name, data in extra.items():
                apk.writestr(name, data)
        return self.apk

    def test_valid_pinned_reference_baseline(self):
        self.assertEqual(
            {"vl80s_core_packs": 28, "common_references": 66,
             "family_previews": 84, "forbidden_assets": 0},
            check_apk(self.build()),
        )

    def test_family_reference_duplicates_are_rejected(self):
        def duplicate(doc):
            doc["entries"][1]["id"] = doc["entries"][0]["id"]
        with self.assertRaisesRegex(ApkAuditError, "Duplicate family reference"):
            check_apk(self.build(modify={"assets/crew-reference/summaries.json": duplicate}))

    def test_family_reference_wrong_model_count_is_rejected(self):
        def wrong_count(doc):
            doc["entries"][1]["modelId"] = "tem2"
        with self.assertRaisesRegex(ApkAuditError, "per-model count"):
            check_apk(self.build(modify={"assets/crew-reference/summaries.json": wrong_count}))

    def test_missing_published_vl80s_pack_is_rejected(self):
        missing = "assets/" + next(
            p for p in INDEX["packs"] if "/recommended/" not in p and "/extended/" not in p
        )
        with self.assertRaisesRegex(ApkAuditError, "referenced core asset absent"):
            check_apk(self.build(omit={missing}))

    def test_research_or_unverified_voice_asset_is_rejected(self):
        with self.assertRaisesRegex(ApkAuditError, "Unreviewed/research/voice"):
            check_apk(self.build(extra={"assets/assistant_voice/silero_vad.onnx": b"unverified"}))

    def test_family_preview_cannot_gain_procedural_steps(self):
        def inject_steps(doc):
            doc["entries"][0]["steps"] = ["unreviewed action"]
        with self.assertRaisesRegex(ApkAuditError, "Executable/empty family preview"):
            check_apk(self.build(modify={"assets/crew-reference/summaries.json": inject_steps}))

    def test_common_reference_cannot_be_silently_promoted(self):
        def promote(doc):
            doc["entries"][0]["publicationStatus"] = "ACTIVE"
        with self.assertRaisesRegex(ApkAuditError, "silently promoted"):
            check_apk(self.build(modify={"assets/common/first-aid/topics.pack.json": promote}))

    def test_unverified_family_scope_cannot_claim_execution(self):
        def claim(doc):
            doc["entries"][0]["executionId"] = "2es5k_msud_n"
        with self.assertRaisesRegex(ApkAuditError, "silently asserted"):
            check_apk(self.build(modify={"assets/crew-reference/summaries.json": claim}))


if __name__ == "__main__":
    unittest.main()
