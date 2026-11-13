"""Synthetic negative authoring fixtures; no actual locomotive instructions."""
import copy
import unittest

from diagnostic_stage3_preflight import validate_claim, validate_preserved_baseline


def backed():
    return {
        "claimId": "synthetic-claim", "publicationStatus": "CANDIDATE",
        "runtimeImport": False, "actionAuthorityGranted": False,
        "evidenceState": "SOURCE_BACKED_DRAFT", "exactProfileId": "profile-a",
        "installedEquipmentId": "equipment-a", "installedEquipmentConfirmed": True,
        "userRole": "synthetic-authorized-role", "actionDisposition": "CONDITIONAL_ACTION",
        "source": {
            "sourceId": "synthetic-document", "documentRevision": "synthetic-revision",
            "clauseOrPage": "synthetic-clause", "documentRole": "synthetic-authorized-role",
            "sourceProfileId": "profile-a", "sourceEquipmentId": "equipment-a",
            "relation": "CLAUSE_VERIFIED", "currentRevisionVerified": True,
            "sourceAuthorityVerified": True,
        },
    }


class DiagnosticStage3PreflightTest(unittest.TestCase):
    def test_baseline_has_no_unauthorized_version_or_action(self):
        self.assertEqual(validate_preserved_baseline()["publication"], "BLOCKED")

    def test_synthetic_all_evidence_only_reaches_human_review(self):
        self.assertEqual(validate_claim(backed()), "REVIEW_REQUIRED")

    def test_unbound_source_gap_blocks_action(self):
        c = backed()
        c.update(evidenceState="UNBOUND", source=None,
                 sourceGapReason="Not documented", actionDisposition="INFORMATION_ONLY")
        self.assertEqual(validate_claim(c), "BLOCKED_SOURCE")

    def test_source_gap_cannot_claim_conditional_action(self):
        c = backed()
        c.update(evidenceState="UNBOUND", source=None, sourceGapReason="Missing")
        with self.assertRaises(ValueError):
            validate_claim(c)

    def test_title_or_id_match_not_claim_authority(self):
        c = backed()
        c["source"]["relation"] = "ID_AND_TITLE_MATCH_ONLY"
        self.assertEqual(validate_claim(c), "BLOCKED_SOURCE")

    def test_outdated_source_blocks(self):
        c = backed()
        c["source"]["currentRevisionVerified"] = False
        self.assertEqual(validate_claim(c), "BLOCKED_SOURCE")

    def test_profession_mismatch_blocks(self):
        c = backed()
        c["source"]["documentRole"] = "different-profession"
        self.assertEqual(validate_claim(c), "BLOCKED_SOURCE")

    def test_profile_mismatch_blocks(self):
        c = backed()
        c["source"]["sourceProfileId"] = "neighbor-variant"
        self.assertEqual(validate_claim(c), "BLOCKED_SOURCE")

    def test_installed_equipment_mismatch_blocks(self):
        c = backed()
        c["source"]["sourceEquipmentId"] = "different-hardware"
        self.assertEqual(validate_claim(c), "BLOCKED_SOURCE")

    def test_absent_equipment_confirmation_blocks(self):
        c = backed()
        c["installedEquipmentConfirmed"] = False
        self.assertEqual(validate_claim(c), "BLOCKED_SOURCE")

    def test_unverified_source_authority_blocks(self):
        c = backed()
        c["source"]["sourceAuthorityVerified"] = False
        self.assertEqual(validate_claim(c), "BLOCKED_SOURCE")

    def test_historical_or_prohibited_action_blocks(self):
        c = backed()
        c["actionDisposition"] = "PROHIBITED"
        self.assertEqual(validate_claim(c), "BLOCKED_SOURCE")

    def test_missing_clause_fails_before_review(self):
        c = backed()
        c["source"]["clauseOrPage"] = ""
        with self.assertRaisesRegex(ValueError, "clauseOrPage"):
            validate_claim(c)

    def test_warning_cannot_override_missing_authority(self):
        c = backed()
        c["source"]["sourceAuthorityVerified"] = False
        c["warningAcknowledged"] = True
        c["extendedEnabled"] = True
        self.assertEqual(validate_claim(c), "BLOCKED_SOURCE")

    def test_attempted_publication_promote_fails(self):
        c = backed()
        c["publicationStatus"] = "ACTIVE"
        with self.assertRaises(ValueError):
            validate_claim(c)

    def test_attempted_runtime_import_fails(self):
        c = backed()
        c["runtimeImport"] = True
        with self.assertRaises(ValueError):
            validate_claim(c)


if __name__ == "__main__":
    unittest.main()
