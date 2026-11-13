"""Regression gates for stage-1 handoff: evidence gaps cannot be marked complete."""
import copy
import unittest
from pathlib import Path
from qa.validate_stage1_structural_handoff import read, validate, HANDOFF

ROOT = Path(__file__).resolve().parents[1]

class HandoffTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.h = read(ROOT, HANDOFF)
        cls.assets = read(ROOT, cls.h["verifiedScope"]["donorAssets"]["ledger"])
        cls.kotlin = read(ROOT, cls.h["verifiedScope"]["donorMainKotlin"]["ledger"])
        cls.triage = read(ROOT, cls.h["verifiedScope"]["sourceLinks"]["ledger"])

    def check(self, h=None, assets=None, kotlin=None, triage=None):
        return validate(h if h is not None else self.h,
                        assets if assets is not None else self.assets,
                        kotlin if kotlin is not None else self.kotlin,
                        triage if triage is not None else self.triage, ROOT)

    def test_real_handoff(self):
        self.assertEqual(self.check()["nextStage"], 2)

    def test_cannot_approve_runtime(self):
        h = copy.deepcopy(self.h)
        h["runtimePublicationApproved"] = True
        with self.assertRaises(AssertionError): self.check(h=h)

    def test_cannot_claim_full_source_authority(self):
        h = copy.deepcopy(self.h)
        h["status"] = "ALL_SOURCES_VERIFIED"
        with self.assertRaises(AssertionError): self.check(h=h)

    def test_cannot_drop_unresolved_chme3(self):
        t = copy.deepcopy(self.triage)
        t["chme3"]["targetGroups"].pop()
        with self.assertRaises(AssertionError): self.check(triage=t)

    def test_cannot_promote_ermak_link(self):
        t = copy.deepcopy(self.triage)
        t["ermak"]["sourceIds"][0]["runtimeImport"] = True
        with self.assertRaises(AssertionError): self.check(triage=t)

    def test_cannot_claim_user_journey_migrated(self):
        k = copy.deepcopy(self.kotlin)
        k["sources"][0]["userJourneyVerified"] = True
        with self.assertRaises(AssertionError): self.check(kotlin=k)

    def test_cannot_remove_backlog(self):
        h = copy.deepcopy(self.h)
        h["openBacklog"].pop()
        with self.assertRaises(AssertionError): self.check(h=h)

    def test_cannot_repin_donor(self):
        h = copy.deepcopy(self.h)
        h["donorCommit"] = "0" * 40
        with self.assertRaises(AssertionError): self.check(h=h)

if __name__ == "__main__":
    unittest.main()
