#!/usr/bin/env python3
"""Negative regression tests for historical CHME3T EDB source boundaries."""
import unittest

from qa.validate_chme3t_edb_evidence import (
    ALLOWED_DOCUMENTS, EVIDENCE, RAW, TRIAGE, read, validate,
)


class Chme3tEdbEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.evidence = read(EVIDENCE)
        self.triage = read(TRIAGE)
        self.raw = read(RAW)
        self.documents = {path: read(path) for path in ALLOWED_DOCUMENTS}

    def check(self):
        return validate(self.evidence, self.triage, self.raw, self.documents)

    def test_historical_evidence_preserved_not_published(self):
        result = self.check()
        self.assertEqual(result["sourceObjectPointersVerified"], 3)
        self.assertEqual(result["crossVariantConflictsStillBlocked"], 8)
        self.assertFalse(result["runtimeImport"])

    def test_old_edition_must_not_be_marked_current(self):
        self.evidence["supplementalTechnicalManual"]["currentEditionVerified"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_repair_text_must_not_authorize_crew(self):
        self.evidence["supplementalTechnicalManual"]["crewActionAuthority"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_official_manual_must_not_expand_variant_scope(self):
        self.evidence["supplementalTechnicalManual"]["verifiedFor"].append("chme3e")
        with self.assertRaises(AssertionError):
            self.check()

    def test_official_manual_locator_must_not_change_silently(self):
        self.evidence["supplementalTechnicalManual"]["locators"][0]["section"] = "3.3.6"
        with self.assertRaises(AssertionError):
            self.check()

    def test_must_not_authorize_runtime(self):
        self.evidence["runtimeImport"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_must_not_claim_manufacturer_authority(self):
        self.evidence["manufacturerAuthorityVerified"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_must_not_expand_scope_to_chme3e(self):
        self.evidence["source"]["sourceScope"].append("chme3e")
        with self.assertRaises(AssertionError):
            self.check()

    def test_must_not_expand_scope_to_chme3(self):
        self.evidence["source"]["notAutomaticallyApplicableTo"] = ["chme3e"]
        with self.assertRaises(AssertionError):
            self.check()

    def test_historical_source_page_range_cannot_drift(self):
        self.evidence["source"]["printedPages"] = [21, 22, 23, 24]
        with self.assertRaises(AssertionError):
            self.check()

    def test_historical_source_identity_cannot_be_replaced_silently(self):
        self.evidence["source"]["url"] = "https://example.org/unverified.pdf"
        with self.assertRaises(AssertionError):
            self.check()

    def test_missing_original_source_object_fails(self):
        self.evidence["targetEvidence"][0]["preservedDonorObjectPointers"].pop()
        with self.assertRaises(AssertionError):
            self.check()

    def test_original_source_object_hash_tamper_fails(self):
        self.evidence["targetEvidence"][0]["preservedDonorObjectPointers"][0]["sourceObjectSha256"] = "0" * 64
        with self.assertRaises(AssertionError):
            self.check()

    def test_cross_variant_conflict_must_remain_blocked(self):
        self.raw["crossVariantConflicts"][0]["runtimeLinkCreated"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_cross_variant_conflict_cannot_disappear(self):
        self.raw["crossVariantConflicts"].pop()
        with self.assertRaises(AssertionError):
            self.check()

    def test_pinned_source_document_cannot_change_silently(self):
        path = "content-packs/diesel/chme3-family/migration/atlas-source-index.json"
        obj = self.documents[path]["documents"][0]["sourceObject"]["records"][13]
        obj["name"] = "tampered"
        with self.assertRaises(AssertionError):
            self.check()

    def test_unresolved_reference_cannot_be_marked_resolved(self):
        self.evidence["targetEvidence"][0]["sourceLinkResolved"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_variant_specific_donor_evidence_cannot_be_broadened(self):
        self.evidence["targetEvidence"][0]["preservedDonorObjectPointers"][0]["applicability"] = ["ЧМЭ3", "ЧМЭ3Т"]
        with self.assertRaises(AssertionError):
            self.check()


if __name__ == "__main__":
    unittest.main()
