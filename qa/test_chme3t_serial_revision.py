#!/usr/bin/env python3
"""Negative checks for CHME3T 6245 historical electrical revision evidence."""
import unittest

from qa.validate_chme3t_serial_revision import (
    EVIDENCE, AUDIT, TRIAGE, PRIORITY, REMAINING, read, validate,
)


class SerialRevisionTests(unittest.TestCase):
    def setUp(self):
        self.e, self.a, self.t, self.p, self.r = [
            read(path) for path in (EVIDENCE, AUDIT, TRIAGE, PRIORITY, REMAINING)]

    def check(self):
        return validate(self.e, self.a, self.t, self.p, self.r)

    def test_baseline(self):
        result = self.check()
        self.assertEqual(result["chme3tElectricalEdgesProtected"], 54)
        self.assertFalse(result["runtimeImport"])

    def test_serial_boundary_tamper(self):
        self.e["source"]["revisionSignal"]["electricalCircuitChangesFromSerial"] = 6244
        with self.assertRaises(AssertionError):
            self.check()

    def test_serial_boundary_as_string(self):
        self.e["source"]["revisionSignal"]["electricalCircuitChangesFromSerial"] = "6245"
        with self.assertRaises(AssertionError):
            self.check()

    def test_manufacturer_authority_claim(self):
        self.e["manufacturerAuthorityVerified"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_serial_applicability_claim(self):
        self.e["serialApplicabilityVerified"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_current_normative_claim(self):
        self.e["currentNormativeAuthorityVerified"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_crew_action_claim(self):
        self.e["crewActionAuthorized"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_runtime_promotion(self):
        self.e["runtimeImport"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_wrong_variant(self):
        self.e["source"]["revisionSignal"]["model"] = "chme3e"
        with self.assertRaises(AssertionError):
            self.check()

    def test_missing_modernization_gate(self):
        self.e["requiredBeforeRuntime"].pop(0)
        with self.assertRaises(AssertionError):
            self.check()

    def test_source_identity_tamper(self):
        self.e["source"]["id"] = "OTHER-SOURCE"
        with self.assertRaises(AssertionError):
            self.check()

    def test_reference_count_tamper(self):
        self.e["affectedTargets"][0]["chme3tUnresolvedReferences"] += 1
        with self.assertRaises(AssertionError):
            self.check()

    def test_missing_original_book_reference(self):
        self.p["targetEvidence"][1]["originalEvidenceRefs"] = []
        with self.assertRaises(AssertionError):
            self.check()

    def test_audit_variant_edge_missing(self):
        self.a["unresolvedReferences"] = [
            r for r in self.a["unresolvedReferences"]
            if not (r["variant"] == "chme3t" and
                    r["sourceTargetId"] == "CHME3T-SCH-EDB")]
        with self.assertRaises(AssertionError):
            self.check()

    def test_quarantine_removed(self):
        self.t["chme3"]["targetGroups"] = [
            dict(g, reviewStatus="RESOLVED") if g["sourceTargetId"] == "CHME3-SCH-CONTROL"
            else g for g in self.t["chme3"]["targetGroups"]]
        with self.assertRaises(AssertionError):
            self.check()

    def test_edb_cross_variant_not_blocked(self):
        self.r["expectedCrossVariantConflicts"] = 0
        with self.assertRaises(AssertionError):
            self.check()

    def test_blocked_action_removed(self):
        self.e["blockedActions"].pop()
        with self.assertRaises(AssertionError):
            self.check()


    def test_component_evidence_baseline(self):
        self.assertEqual(len(self.e["historicalComponentDifferences"]), 2)
        self.check()

    def test_brake_selector_contact_count_tamper(self):
        self.e["historicalComponentDifferences"][0]["from6245"]["powerFingers"] = 25
        with self.assertRaises(AssertionError):
            self.check()

    def test_brake_selector_side_tamper(self):
        self.e["historicalComponentDifferences"][0]["before6245"]["relativeToReverser"] = "RIGHT"
        with self.assertRaises(AssertionError):
            self.check()

    def test_regulator_board_count_tamper(self):
        self.e["historicalComponentDifferences"][1]["from6245"]["electronicBoards"] = 49
        with self.assertRaises(AssertionError):
            self.check()

    def test_regulator_early_batch_scope_cannot_be_generalized(self):
        self.e["historicalComponentDifferences"][1]["earlyBatchesOnlyNotAllPre6245"] = False
        with self.assertRaises(AssertionError):
            self.check()

    def test_secondary_evidence_cannot_be_called_factory_verified(self):
        self.e["historicalComponentDifferences"][0]["factoryDrawingVerified"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_component_evidence_cannot_enter_runtime(self):
        self.e["historicalComponentDifferences"][1]["runtimeImport"] = True
        with self.assertRaises(AssertionError):
            self.check()

    def test_component_evidence_source_cannot_be_replaced_silently(self):
        self.e["historicalComponentDifferences"][0]["historicalSourceUrl"] = "https://example.org"
        with self.assertRaises(AssertionError):
            self.check()


if __name__ == "__main__":
    unittest.main()
