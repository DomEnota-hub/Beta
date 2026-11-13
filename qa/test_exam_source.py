#!/usr/bin/env python3
import unittest

from qa.audit_exam_source import derive_embedded_key


class ExamCodecSourceTests(unittest.TestCase):
    def test_key_parts_are_xored_not_concatenated(self):
        a = ", ".join(["-1"] * 32)
        b = ", ".join(["1"] * 32)
        source = ("private val keyPartA = byteArrayOf(" + a + ")\n" +
                  "private val keyPartB = byteArrayOf(" + b + ")")
        self.assertEqual(derive_embedded_key(source), bytes([254] * 32))

    def test_missing_key_is_rejected(self):
        with self.assertRaises(AssertionError):
            derive_embedded_key("no embedded key")

    def test_wrong_key_length_is_rejected(self):
        source = "private val keyPartA = byteArrayOf(1)\nprivate val keyPartB = byteArrayOf(2)"
        with self.assertRaises(AssertionError):
            derive_embedded_key(source)


    def test_metadata_only_index_never_contains_question_or_answer(self):
        import hashlib
        import json
        from qa.audit_exam_source import build_candidate_metadata_index
        ids = ["VL80S-EXAM-1", "VL80S-EXAM-2"]
        summary = {
            "questionCount": 2, "assetBlobSha": "opaque-source",
            "decoderBlobSha": "opaque-decoder",
            "questionIdSetSha256": hashlib.sha256(
                json.dumps(sorted(ids), ensure_ascii=False).encode()).hexdigest(),
            "diagnosticIdsMissingFromVl80sSource": [],
            "equipmentIdsMissingFromVl80sCanonicalOrLegacy": [],
        }
        root = {"questions": [
            {"id": ids[0], "question": "SECRET QUESTION", "correctAnswer": "SECRET ANSWER",
             "diagnosticScenarioIds": ["VL-DIAG-1"], "equipmentIds": [],
             "requiresImage": False},
            {"id": ids[1], "question": "OTHER SECRET", "correctAnswer": "OTHER ANSWER",
             "diagnosticScenarioIds": [], "equipmentIds": ["VL-EQ-1"],
             "requiresImage": True},
        ]}
        candidate = build_candidate_metadata_index(root, summary)
        self.assertEqual(len(candidate["records"]), 2)
        self.assertFalse(candidate["runtimeImport"])
        self.assertFalse(candidate["sourceRightsVerified"])
        self.assertFalse(candidate["containsQuestionOrAnswerText"])
        self.assertNotIn("SECRET", json.dumps(candidate))
        self.assertNotIn("question", json.dumps(candidate["records"]).lower())
        return root, summary

    def test_metadata_rejects_duplicate_ids(self):
        from qa.audit_exam_source import build_candidate_metadata_index
        root, summary = self.test_metadata_only_index_never_contains_question_or_answer()
        root["questions"][1]["id"] = root["questions"][0]["id"]
        with self.assertRaises(AssertionError):
            build_candidate_metadata_index(root, summary)

    def test_metadata_rejects_question_text_as_id(self):
        from qa.audit_exam_source import build_candidate_metadata_index
        root, summary = self.test_metadata_only_index_never_contains_question_or_answer()
        root["questions"][0]["id"] = "Question text with spaces"
        with self.assertRaises(AssertionError):
            build_candidate_metadata_index(root, summary)

    def test_metadata_rejects_prose_as_reference(self):
        from qa.audit_exam_source import build_candidate_metadata_index
        root, summary = self.test_metadata_only_index_never_contains_question_or_answer()
        root["questions"][0]["diagnosticScenarioIds"] = ["unsafe text reference"]
        with self.assertRaises(AssertionError):
            build_candidate_metadata_index(root, summary)

    def test_metadata_rejects_nonboolean_image_flag(self):
        from qa.audit_exam_source import build_candidate_metadata_index
        root, summary = self.test_metadata_only_index_never_contains_question_or_answer()
        root["questions"][0]["requiresImage"] = "false"
        with self.assertRaises(AssertionError):
            build_candidate_metadata_index(root, summary)

    def test_metadata_rejects_unknown_crosslinks(self):
        from qa.audit_exam_source import build_candidate_metadata_index
        root, summary = self.test_metadata_only_index_never_contains_question_or_answer()
        summary["diagnosticIdsMissingFromVl80sSource"] = ["VL-DIAG-1"]
        with self.assertRaises(AssertionError):
            build_candidate_metadata_index(root, summary)


if __name__ == "__main__":
    unittest.main()
