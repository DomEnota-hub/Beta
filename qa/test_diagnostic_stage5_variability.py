"""Fail-closed fixtures for Stage5 method-divergence research."""
import copy
import json
import unittest
from pathlib import Path
from validate_diagnostic_stage5_variability import check, PATH, ROOT

class SourceVarietyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document=json.loads((ROOT/PATH).read_text(encoding="utf-8"))
        cls.inventory=json.loads((ROOT/"docs/data-migration/diagnostic-corpus-analysis.json").read_text(encoding="utf-8"))
    def reject(self,mutate):
        doc=copy.deepcopy(self.document)
        mutate(doc)
        with self.assertRaises(ValueError):
            check(doc,self.inventory)
    def test_valid_source_candidates_do_not_approve_procedures(self):
        self.assertEqual(check(self.document,self.inventory)["scenarios"],2)
    def test_duplicate_diagnostic_focus_is_not_variety(self):
        def m(d):
            a=d["scenarios"][1]["alternativeSourceCandidates"]
            a[1]["approachFocus"]=a[0]["approachFocus"]
        self.reject(m)
    def test_two_urls_same_source_not_enough(self):
        self.reject(lambda d:d["scenarios"][0]["alternativeSourceCandidates"][1].update(
            url=d["scenarios"][0]["alternativeSourceCandidates"][0]["url"]))
    def test_cannot_mark_unread_full_claims_verified(self):
        self.reject(lambda d:d["scenarios"][0]["alternativeSourceCandidates"][0].update(
            currentOperationalAuthorityVerified=True))
    def test_cannot_insert_operational_steps(self):
        self.reject(lambda d:d["scenarios"][1]["alternativeSourceCandidates"][0].update(
            permittedProcedureSteps=["synthetic instruction"]))
    def test_cannot_claim_stage_completed(self):
        self.reject(lambda d:d.update(workStatus="COMPLETE"))
    def test_cannot_author_versions_without_claim_review(self):
        self.reject(lambda d:d["scenarios"][0]["versions"].update(short="ACTIVE"))
    def test_cannot_merge_into_other_locomotive_id(self):
        self.reject(lambda d:d["scenarios"][1].update(scenarioId="chme3.diagnostics.chme3-diag-110"))
    def test_cannot_claim_unexamined_difference_as_conflict(self):
        self.reject(lambda d:d["scenarios"][0].update(differingInterpretationsAreVerifiedContradictions=True))
    def test_cannot_attach_source_to_unverified_variant(self):
        self.reject(lambda d:d["scenarios"][0]["alternativeSourceCandidates"][0].update(
            applicabilityToInstalledVariantVerified=True))
if __name__=="__main__":
    unittest.main()
