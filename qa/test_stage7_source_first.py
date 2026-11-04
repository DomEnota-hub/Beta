"""Stage7 negative regression fixtures: no publication, source substitution or action."""
import copy, json, unittest
from validate_stage7_source_first import PATHS, ROOT, check

class Stage7SourceFirstTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.inventory=json.loads((ROOT/"docs/data-migration/diagnostic-corpus-analysis.json").read_text(encoding="utf-8"))
  cls.docs=[json.loads((ROOT/p).read_text(encoding="utf-8")) for p in PATHS.values()]
 def reject(self, fn, index=0):
  doc=copy.deepcopy(self.docs[index]);fn(doc)
  with self.assertRaises(ValueError): check(doc,self.inventory)
 def test_both_have_independent_short_and_detailed(self):
  self.assertTrue(all(check(x,self.inventory)=={"SHORT":6,"DETAILED":12} for x in self.docs))
 def test_wrong_canonical_scenario_rejected(self):
  self.reject(lambda x:x.update(scenarioId="vl80s.diag.gv-no-open"))
 def test_mixing_previous_ekg_symptom_rejected(self):
  self.reject(lambda x:x["mustRemainDistinctFrom"].remove("vl80s.diag.ekg-stuck"),1)
 def test_wrong_donor_blob_rejected(self):
  self.reject(lambda x:x.update(donorBlobSha="not-pinned"))
 def test_runtime_import_rejected(self):
  self.reject(lambda x:x.update(runtimeImport=True))
 def test_technical_approval_rejected(self):
  self.reject(lambda x:x.update(technicalClaimsReviewed=True))
 def test_unknown_not_stop_rejected(self):
  self.reject(lambda x:x["versions"]["SHORT"]["nodes"][0]["responses"].update(UNKNOWN="s7-gv-air-loss-short-yes0"))
 def test_unsafe_operation_rejected(self):
  self.reject(lambda x:x["versions"]["DETAILED"]["extendedRoutes"][0].update(operationalSteps=["synthetic action"]))
 def test_missing_warning_read_rejected(self):
  self.reject(lambda x:x["warningGate"].update(warningReadToEnd=False))
 def test_unknown_equipment_declared_confirmed_rejected(self):
  self.reject(lambda x:x["versions"]["SHORT"]["extendedRoutes"][0]["applicability"].update(exactEquipmentProfileConfirmed=True))
 def test_historical_claim_cannot_authorize_action(self):
  self.reject(lambda x:x["historicalClaims"][0].update(authorizesAction=True))
 def test_approach_identity_cannot_be_duplicated(self):
  self.reject(lambda x:x["versions"]["DETAILED"]["extendedRoutes"][1].update(approachId=x["versions"]["SHORT"]["extendedRoutes"][1]["approachId"]))
 def test_archival_claim_cannot_be_relabelled_as_donor(self):
  self.reject(lambda x:x["versions"]["DETAILED"]["extendedRoutes"][1].update(sourceId="donorSeed"))
 def test_source_pointer_cannot_be_invented(self):
  self.reject(lambda x:x["historicalClaims"][0].update(sourcePointer="unknown page"))
 def test_false_confirmed_cause_rejected(self):
  self.reject(lambda x:x["versions"]["DETAILED"]["nodes"][1].update(causeConfirmed=True))
 def test_wrong_ekg_indicator_source_rejected(self):
  self.reject(lambda x:x["sourceRecords"]["manual1990"].update(isbn="invented"),1)
if __name__=="__main__": unittest.main()
