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


if __name__ == "__main__":
    unittest.main()
