"""Negative checks for independent Stage6 contrast drafts."""
import copy,json,unittest
from validate_stage6_routes import PATHS,ROOT,check
class Stage6RouteTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.inv=json.loads((ROOT/"docs/data-migration/diagnostic-corpus-analysis.json").read_text(encoding="utf-8"))
  cls.records=[json.loads((ROOT/p).read_text(encoding="utf-8")) for p in PATHS.values()]
 def reject(self,fn,index=0):
  obj=copy.deepcopy(self.records[index]);fn(obj)
  with self.assertRaises(ValueError):check(obj,self.inv)
 def test_both_have_independent_versions(self):
  self.assertTrue(all(check(x,self.inv)["DETAILED"]>check(x,self.inv)["SHORT"] for x in self.records))
 def test_source_can_have_multiple_different_approaches(self):
  self.assertTrue(all({a["sourceId"] for v in r["versions"].values() for a in v["extendedRoutes"]}=={"donorSeed"} for r in self.records))
 def test_unknown_must_stop(self):
  self.reject(lambda x:x["versions"]["SHORT"]["nodes"][0]["responses"].update(UNKNOWN="confirmed"))
 def test_operational_steps_never_accepted(self):
  self.reject(lambda x:x["versions"]["DETAILED"]["extendedRoutes"][0].update(operationalSteps=["fake"]))
 def test_source_approval_cannot_be_forged(self):
  self.reject(lambda x:x.update(sourceAuthorityVerified=True))
 def test_runtime_import_cannot_be_enabled(self):
  self.reject(lambda x:x.update(runtimeImport=True))
 def test_a_warning_acknowledgment_is_not_enough(self):
  self.reject(lambda x:x["warningGate"].update(warningReadToEnd=False))
 def test_different_source_layer_cannot_be_substituted(self):
  self.reject(lambda x:x.update(donorLayer="DiagnosticRepository.kt"),1)
 def test_model_variant_not_forged(self):
  self.reject(lambda x:x["versions"]["SHORT"]["extendedRoutes"][0]["applicability"].update(profileId="vl80s-later"))
 def test_duplicate_methods_not_just_urls(self):
  self.reject(lambda x:x["versions"]["SHORT"]["extendedRoutes"][1].update(approachFocus=x["versions"]["SHORT"]["extendedRoutes"][0]["approachFocus"]))
 def test_observation_cannot_be_declared_as_verified_cause(self):
  self.reject(lambda x:x["versions"]["DETAILED"]["nodes"][4].update(causeConfirmed=True))
 def test_canonical_scenario_cannot_be_conflated(self):
  self.reject(lambda x:x.update(scenarioId="vl80s.diag.gv-no-close"))
if __name__=="__main__":unittest.main()
