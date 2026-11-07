"""Adversarial Stage7 compressor candidate gates, not device tests."""
import copy,json,unittest
from validate_stage7_compressor_source_first import ROOT,BASE,MIG,LEDGER,EXPECTED,check,require
class Stage7CompressorQA(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.inventory=json.loads((ROOT/BASE).read_text(encoding="utf-8"))
  cls.migration=json.loads((ROOT/MIG).read_text(encoding="utf-8"))["sourceObject"]
  cls.cases={sid:json.loads((ROOT/f"content-packs/electric/vl80s/diagnostics/authoring/stage7-{sid}.research.json").read_text(encoding="utf-8")) for sid in EXPECTED}
 def assert_rejected(self,mutate,case="compressor-pressure"):
  data=copy.deepcopy(self.cases[case]);mutate(data)
  with self.assertRaises(ValueError):check(data,self.inventory,self.migration)
 def test_all_three(self):
  self.assertEqual({check(d,self.inventory,self.migration) for d in self.cases.values()},set(EXPECTED))
 def test_cross_original_identity(self):
  self.assert_rejected(lambda d:d.update(originalId="compressor-no-start"))
 def test_source_blob_substitution(self):
  self.assert_rejected(lambda d:d.update(donorOriginalBlobSha="bad"))
 def test_runtime_promotion(self):
  self.assert_rejected(lambda d:d.update(runtimeImport=True))
 def test_action_permission(self):
  self.assert_rejected(lambda d:d.update(actionAuthorityGranted=True))
 def test_unknown_must_stop(self):
  self.assert_rejected(lambda d:d["versions"]["SHORT"]["nodes"][1]["responses"].update(UNKNOWN="report-yes"))
 def test_unsafe_branch(self):
  self.assert_rejected(lambda d:d["versions"]["DETAILED"]["nodes"][1]["responses"].update(NO="secondary"))
 def test_hidden_by_default(self):
  self.assert_rejected(lambda d:d["warningGate"].update(default="VISIBLE"))
 def test_ack_does_not_authorize(self):
  self.assert_rejected(lambda d:d["versions"]["DETAILED"]["extendedRoutes"][0]["visibility"].update(warningGrantsActionAuthority=True))
 def test_source_authority_not_current(self):
  self.assert_rejected(lambda d:d["sourceRecords"]["manual1990"].update(currentOperatingAuthority=True))
 def test_teaching_discrepancy_preserved(self):
  self.assert_rejected(lambda d:d["sourceRecords"]["training"].update(unresolvedDiscrepancy=""))
 def test_installed_profile_not_assumed(self):
  self.assert_rejected(lambda d:d["versions"]["SHORT"]["extendedRoutes"][1]["applicability"].update(exactEquipmentProfileConfirmed=True))
 def test_no_fake_device_qa(self):
  self.assert_rejected(lambda d:d.update(deviceQA="PASSED"))
 def test_seed_question_provenance(self):
  self.assert_rejected(lambda d:d.update(donorOriginalQuestions=["invented"]),case="compressor-long-run")
 def test_archival_claim_no_fault_proof(self):
  self.assert_rejected(lambda d:d["historicalEvidenceClaims"][0].update(provesFaultCause=True))
 def test_no_copy_paste_approach(self):
  self.assert_rejected(lambda d:d["versions"]["DETAILED"]["extendedRoutes"][1].update(approachFocus="DONOR_SYMPTOM"))
if __name__=="__main__":unittest.main()
