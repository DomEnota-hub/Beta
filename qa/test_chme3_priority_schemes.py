#!/usr/bin/env python3
"""Negative regression tests for the CHME3 222-edge non-runtime scheme audit."""
import copy
import unittest

from qa.validate_chme3_priority_schemes import (
    AUDIT, EVIDENCE, RAW, REMAINING, TRIAGE, read, validate,
)


class PrioritySchemeTests(unittest.TestCase):
    def setUp(self):
        self.evidence, self.audit, self.raw, self.remaining, self.triage = [
            read(p) for p in (EVIDENCE, AUDIT, RAW, REMAINING, TRIAGE)]

    def check(self):
        return validate(self.evidence, self.audit, self.raw, self.remaining, self.triage)

    def test_baseline_222_edges(self):
        result = self.check()
        self.assertEqual(result["unresolvedReferencesCrossChecked"], 222)
        self.assertEqual(result["perVariant"], {"chme3": 74, "chme3e": 74, "chme3t": 74})
        self.assertFalse(result["runtimeImport"])

    def test_missing_priority_target_rejected(self):
        self.evidence["targetEvidence"].pop()
        with self.assertRaises(AssertionError):
            self.check()

    def test_reference_count_drift_rejected(self):
        self.evidence["targetEvidence"][0]["unresolvedReferenceCount"] += 1
        with self.assertRaises(AssertionError):
            self.check()

    def test_variant_swap_preserving_total_rejected(self):
        counts = self.evidence["targetEvidence"][0]["referenceCountsByVariant"]
        counts["chme3"] += 1
        counts["chme3t"] -= 1
        with self.assertRaises(AssertionError):
            self.check()

    def test_original_object_hash_tamper_rejected(self):
        self.evidence["targetEvidence"][0]["originalObjectSha256"] = "0" * 64
        with self.assertRaises(AssertionError):
            self.check()

    def test_original_document_blob_tamper_rejected(self):
        self.remaining["documents"][3]["sourceBlobSha"] = "0" * 40
        with self.assertRaises(AssertionError):
            self.check()

    def test_original_scheme_field_change_rejected(self):
        self.remaining["documents"][3]["sourceObject"]["records"][6]["title"] = "changed"
        with self.assertRaises(AssertionError):
            self.check()

    def test_training_source_promoted_to_manufacturer_rejected(self):
        self.remaining["documents"][3]["sourceObject"]["records"][6]["evidenceStatus"] = "VERIFIED"
        with self.assertRaises(AssertionError):
            self.check()

    def test_crew_action_promotion_rejected(self):
        self.remaining["documents"][3]["sourceObject"]["records"][6]["actionAuthority"] = "CREW_REPAIR"
        with self.assertRaises(AssertionError):
            self.check()

    def test_raw_source_edge_removed_rejected(self):
        item = next(x for x in self.raw["sourceGroups"]
                    if "CHME3-SCH-PNEUMATIC" in x["rawTargetIds"])
        item["rawTargetIds"].remove("CHME3-SCH-PNEUMATIC")
        with self.assertRaises(AssertionError):
            self.check()

    def test_raw_source_edge_fabricated_rejected(self):
        item = next(x for x in self.raw["sourceGroups"]
                    if "CHME3-SCH-PNEUMATIC" not in x["rawTargetIds"])
        item["rawTargetIds"].append("CHME3-SCH-PNEUMATIC")
        with self.assertRaises(AssertionError):
            self.check()

    def test_source_mapping_disappears_rejected(self):
        ref = next(x for x in self.audit["unresolvedReferences"]
                   if x["sourceTargetId"] == "CHME3-SCH-PNEUMATIC")
        self.audit["mappings"] = [
            x for x in self.audit["mappings"]
            if (x["canonicalId"], x["variant"]) != (ref["source"], ref["variant"])]
        with self.assertRaises(AssertionError):
            self.check()

    def test_donor_source_reference_change_rejected(self):
        self.remaining["documents"][3]["sourceObject"]["records"][6]["evidenceRefs"] = []
        with self.assertRaises(AssertionError):
            self.check()

    def test_runtime_import_rejected(self):
        self.evidence["runtimeImport"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_false_manufacturer_approval_rejected(self):
        self.evidence["manufacturerAuthorityVerified"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_variant_installation_approval_rejected(self):
        self.evidence["variantInstallationVerified"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_wrong_original_pointer_rejected(self):
        self.evidence["targetEvidence"][0]["originalObjectPointer"] = "/documents/3/sourceObject/records/7"
        with self.assertRaises(AssertionError):
            self.check()


if __name__ == "__main__":
    unittest.main()
