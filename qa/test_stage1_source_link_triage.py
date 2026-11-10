#!/usr/bin/env python3
"""Regression tests for the per-target unresolved source-link triage."""
import copy
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from qa.validate_stage1_source_link_triage import ROOT, LEDGER, CHME, ERMAK, read, validate, verify_audit_blobs


class Stage1SourceLinkTriageTests(unittest.TestCase):
    def setUp(self):
        self.ledger = read(ROOT, LEDGER)
        self.chme = read(ROOT, CHME)
        self.ermak = read(ROOT, ERMAK)

    def check(self):
        return validate(self.ledger, self.chme, self.ermak)

    def test_baseline(self):
        result = self.check()
        self.assertEqual(result["chme3DistinctTargets"], 19)
        self.assertEqual(result["ermakUnresolvedIds"], 57)
        self.assertEqual(result["ermakSourceGapOccurrences"], 542)
        self.assertEqual(set(result["chme3CrossVariantTargets"]),
                         {"CHME3T-SCH-EDB", "CHME3T-EQ-EDB-CONTROL"})

    def test_chme_missing_target_fails(self):
        self.ledger["chme3"]["targetGroups"].pop()
        with self.assertRaises(AssertionError):
            self.check()

    def test_chme_wrong_target_count_fails(self):
        self.ledger["chme3"]["targetGroups"][0]["referenceCount"] += 1
        with self.assertRaises(AssertionError):
            self.check()

    def test_chme_wrong_variant_fails(self):
        self.ledger["chme3"]["targetGroups"][0]["variants"] = ["chme3"]
        with self.assertRaises(AssertionError):
            self.check()

    def test_chme_unmapped_scheme_cross_variant_cannot_be_silenced(self):
        scheme = next(x for x in self.ledger["chme3"]["targetGroups"]
                      if x["sourceTargetId"] == "CHME3T-SCH-EDB")
        scheme["variantApplicabilityUnverified"] = False
        with self.assertRaises(AssertionError):
            self.check()

    def test_chme_source_mapping_tamper_fails(self):
        self.chme["mappings"][0]["sourceId"] = self.ledger["chme3"]["targetGroups"][0]["sourceTargetId"]
        with self.assertRaises(AssertionError):
            self.check()

    def test_chme_unsafe_promotion_fails(self):
        self.ledger["chme3"]["targetGroups"][0]["runtimeImport"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_ermak_missing_id_fails(self):
        self.ledger["ermak"]["sourceIds"].pop()
        with self.assertRaises(AssertionError):
            self.check()

    def test_ermak_wrong_occurrences_fails(self):
        self.ledger["ermak"]["sourceIds"][0]["occurrences"] += 1
        with self.assertRaises(AssertionError):
            self.check()

    def test_ermak_ambiguous_auto_match_fails(self):
        target = next(x for x in self.ledger["ermak"]["sourceIds"]
                      if x["sourceDisposition"] == "AMBIGUOUS_SOURCE_ID")
        target["reviewStatus"] = "LINKED"
        with self.assertRaises(AssertionError):
            self.check()

    def test_ermak_registry_key_tamper_fails(self):
        self.ledger["ermak"]["sourceIds"][0]["registryKeys"] = ["invented"]
        with self.assertRaises(AssertionError):
            self.check()

    def test_exact_audit_git_blobs_are_verified(self):
        result = verify_audit_blobs(ROOT, self.ledger)
        self.assertEqual(result["chme3"], "0ba6617d293e101eddbe26da9b976eb8e5555bcf")
        self.assertEqual(result["ermak"], "f02a5e84d92552561852e61d1f8d7df0fd3508c5")

    def test_chme_variant_count_swap_with_unchanged_total_fails(self):
        group = next(g for g in self.ledger["chme3"]["targetGroups"]
                     if g["sourceTargetId"] == "CHME3-SCH-AIR")
        group["referenceCountsByVariant"]["chme3"] += 1
        group["referenceCountsByVariant"]["chme3t"] -= 1
        self.assertEqual(sum(group["referenceCountsByVariant"].values()), group["referenceCount"])
        with self.assertRaises(AssertionError):
            self.check()

    def test_chme_missing_variant_count_fails(self):
        group = self.ledger["chme3"]["targetGroups"][0]
        group["referenceCountsByVariant"].pop("chme3e")
        with self.assertRaises(AssertionError):
            self.check()

    def test_chme_audit_blob_identity_tamper_fails(self):
        self.ledger["chme3"]["sourceAuditGitBlob"] = "0" * 40
        with self.assertRaises(AssertionError):
            verify_audit_blobs(ROOT, self.ledger)

    def test_ermak_audit_blob_identity_tamper_fails(self):
        self.ledger["ermak"]["sourceAuditGitBlob"] = "0" * 40
        with self.assertRaises(AssertionError):
            verify_audit_blobs(ROOT, self.ledger)

    def test_audit_file_drift_with_same_unresolved_counts_fails(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            for relative in (CHME, ERMAK):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / relative).read_bytes())
            target = root / CHME
            target.write_bytes(target.read_bytes() + b"\n")
            with self.assertRaises(AssertionError):
                verify_audit_blobs(root, self.ledger)

    def test_wrong_donor_sha_fails(self):
        self.ledger["donorCommit"] = "unverified"
        with self.assertRaises(AssertionError):
            self.check()


if __name__ == "__main__":
    unittest.main()
