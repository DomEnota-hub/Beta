#!/usr/bin/env python3
"""Negative and positive unit tests for pinned VL80S source parity helpers."""
import copy
import hashlib
import unittest

from qa.validate_vl80s_source_parity import assert_candidate, digest, git_blob


class Vl80sSourceParityTests(unittest.TestCase):
    def test_git_blob_is_not_plain_sha1(self):
        self.assertEqual(git_blob(b"hello"), hashlib.sha1(b"blob 5" + bytes([0]) + b"hello").hexdigest())
        self.assertNotEqual(git_blob(b"hello"), hashlib.sha1(b"hello").hexdigest())

    def test_object_digest_key_order_is_stable(self):
        self.assertEqual(digest({"a": [1, 2], "b": "Токоприёмник"}),
                         digest({"b": "Токоприёмник", "a": [1, 2]}))

    def test_candidate_rejects_runtime_promotion(self):
        valid = {"donorCommit": "3176d6ee228f0ed4b78371f45209e10c1c724eff",
                 "modelOwner": "vl80s", "publicationStatus": "CANDIDATE",
                 "runtimeImport": False}
        assert_candidate(valid)
        for key, value in (("publicationStatus", "ACTIVE"), ("runtimeImport", True),
                           ("modelOwner", "ermak"), ("donorCommit", "unverified")):
            unsafe = copy.deepcopy(valid)
            unsafe[key] = value
            with self.assertRaises(AssertionError):
                assert_candidate(unsafe)


if __name__ == "__main__":
    unittest.main()
