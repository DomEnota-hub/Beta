"""Adversarial evidence-authority tests for archived VL80S technical literature."""
import copy,json,unittest
from validate_stage6_claim_ledger import ROOT,LEDGER,PATHS,validate
class ClaimsTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.ledger=json.loads(LEDGER.read_text(encoding="utf-8"))
  cls.records={k:json.loads(p.read_text(encoding="utf-8")) for k,p in PATHS.items()}
 def reject(self,modify):
  d=copy.deepcopy(self.ledger);r=copy.deepcopy(self.records);modify(d,r)
  with self.assertRaises(ValueError):validate(d,r)
 def test_only_text_location_is_verified(self):
  self.assertEqual(validate(self.ledger,self.records),4)
 def test_old_book_is_not_current_safety_authority(self):
  self.reject(lambda d,r:d["corroboratingSources"]["manual1990"].update(currentActionAuthorityVerified=True))
 def test_specific_equipment_must_remain_unconfirmed(self):
  self.reject(lambda d,r:d["claims"][0].update(installedEquipmentApplicability="CONFIRMED"))
 def test_cannot_invent_proven_fault(self):
  self.reject(lambda d,r:d["claims"][3].update(causeAtThisLocomotive="CONFIRMED"))
 def test_no_historical_repair_instructions_authorized(self):
  self.reject(lambda d,r:d["claims"][2].update(repairProcedure="REPAIR"))
 def test_same_book_two_mechanisms_keep_two_claim_ids(self):
  self.reject(lambda d,r:d["claims"][1].update(claimId="S6-GV-1990-01"))
 def test_graph_alt_needs_precise_section(self):
  self.reject(lambda d,r:r["vl80s.diag.gv-no-open"]["versions"]["DETAILED"]["extendedRoutes"][3].update(sourcePointer="Other"))
 def test_no_cross_scenario_source_reassignment(self):
  self.reject(lambda d,r:d["claims"][2].update(scenarioId="vl80s.diag.gv-no-open"))
 def test_claim_cannot_upgrade_stage(self):
  self.reject(lambda d,r:d.update(stageTechnicalAcceptance="ACCEPTED"))
if __name__=="__main__":unittest.main()
