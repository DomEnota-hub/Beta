#!/usr/bin/env python3
"""Negative regressions for the 388 non-priority CHME3 source edges."""
import unittest

from qa.validate_chme3_remaining_schemes import (
    EVIDENCE, AUDIT, RAW, REMAINING, ATLAS, TRIAGE, read, validate,
)


class RemainingSchemeTests(unittest.TestCase):
    def setUp(self):
        self.evidence, self.audit, self.raw, self.remaining, self.atlas, self.triage = [
            read(p) for p in (EVIDENCE, AUDIT, RAW, REMAINING, ATLAS, TRIAGE)]

    def check(self):
        return validate(self.evidence, self.audit, self.raw,
                        self.remaining, self.atlas, self.triage)

    def row(self, target):
        return next(r for r in self.evidence["targetEvidence"] if r["targetId"] == target)

    def test_baseline_388_edges(self):
        result = self.check()
        self.assertEqual(result["sourceEdgesCrossChecked"], 388)
        self.assertEqual(result["remainingTargets"], 16)
        self.assertEqual(result["crossVariantConflictsBlocked"], 8)
        self.assertFalse(result["runtimeImport"])

    def test_target_removed(self):
        self.evidence["targetEvidence"].pop()
        with self.assertRaises(AssertionError): self.check()

    def test_target_duplicated(self):
        self.evidence["targetEvidence"].append(self.evidence["targetEvidence"][0].copy())
        with self.assertRaises(AssertionError): self.check()

    def test_target_count_drift(self):
        self.evidence["targetEvidence"][0]["unresolvedReferenceCount"] += 1
        with self.assertRaises(AssertionError): self.check()

    def test_variant_swap_same_total(self):
        counts = self.row("CHME3-SCH-AIR")["referenceCountsByVariant"]
        counts["chme3"] += 1
        counts["chme3e"] -= 1
        with self.assertRaises(AssertionError): self.check()

    def test_object_digest_changed(self):
        self.evidence["targetEvidence"][0]["sourceObjects"][0]["sourceObjectSha256"] = "0" * 64
        with self.assertRaises(AssertionError): self.check()

    def test_original_document_blob_changed(self):
        self.remaining["documents"][3]["sourceBlobSha"] = "0" * 40
        with self.assertRaises(AssertionError): self.check()

    def test_wrong_pointer(self):
        self.row("CHME3-SCH-AIR")["sourceObjects"][0]["evidencePath"] = (
            "content-packs/diesel/chme3-family/migration/remaining-document-source-index.json#/documents/3/sourceObject/records/5")
        with self.assertRaises(AssertionError): self.check()

    def test_original_object_mutation(self):
        self.remaining["documents"][3]["sourceObject"]["records"][4]["title"] = "changed"
        with self.assertRaises(AssertionError): self.check()

    def test_source_edge_removed(self):
        group = next(g for g in self.raw["sourceGroups"]
                     if "CHME3-SCH-AIR" in g["rawTargetIds"])
        group["rawTargetIds"].remove("CHME3-SCH-AIR")
        with self.assertRaises(AssertionError): self.check()

    def test_source_edge_fabricated(self):
        group = next(g for g in self.raw["sourceGroups"]
                     if "CHME3-SCH-AIR" not in g["rawTargetIds"])
        group["rawTargetIds"].append("CHME3-SCH-AIR")
        with self.assertRaises(AssertionError): self.check()

    def test_mapping_removed(self):
        ref = next(r for r in self.audit["unresolvedReferences"]
                   if r["sourceTargetId"] == "CHME3-SCH-AIR")
        self.audit["mappings"] = [m for m in self.audit["mappings"]
                                  if (m["canonicalId"], m["variant"]) != (ref["source"], ref["variant"])]
        with self.assertRaises(AssertionError): self.check()

    def test_variant_only_scope_expanded(self):
        self.remaining["documents"][16]["sourceObject"]["records"][0]["applicability"].append("ЧМЭ3Т")
        with self.assertRaises(AssertionError): self.check()

    def test_cross_variant_conflict_removed(self):
        self.raw["crossVariantConflicts"].pop()
        with self.assertRaises(AssertionError): self.check()

    def test_cross_variant_conflict_relabelled(self):
        self.raw["crossVariantConflicts"][0]["sourceVariant"] = "chme3t"
        with self.assertRaises(AssertionError): self.check()

    def test_unsafe_action_promotion(self):
        self.remaining["documents"][3]["sourceObject"]["records"][4]["actionAuthority"] = "CREW_REPAIR"
        with self.assertRaises(AssertionError): self.check()

    def test_fake_manufacturer_approval(self):
        self.evidence["manufacturerAuthorityVerified"] = True
        with self.assertRaises(AssertionError): self.check()

    def test_runtime_publication_rejected(self):
        self.evidence["runtimeImport"] = True
        with self.assertRaises(AssertionError): self.check()

    def test_donor_evidence_ref_mutation(self):
        self.remaining["documents"][16]["sourceObject"]["records"][0]["evidenceRefs"] = []
        with self.assertRaises(AssertionError): self.check()

    def test_secondary_edb_object_missing(self):
        self.row("CHME3T-EQ-EDB-CONTROL")["sourceObjects"].pop()
        with self.assertRaises(AssertionError): self.check()

    def test_edb_profile_gate_mutation(self):
        self.remaining["documents"][3]["sourceObject"]["records"][9]["actionAuthority"] = "INFORMATION_ONLY"
        with self.assertRaises(AssertionError): self.check()


if __name__ == "__main__":
    unittest.main()
