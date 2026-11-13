"""Negative guards for Stage6 source/identity differentiation."""
import copy,json,unittest
from validate_stage6_separation import ROOT,P,check
class TestStage6(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=json.loads((ROOT/P).read_text(encoding="utf-8"))
        cls.inv=json.loads((ROOT/"docs/data-migration/diagnostic-corpus-analysis.json").read_text(encoding="utf-8"))
        cls.src=json.loads((ROOT/"content-packs/electric/vl80s/diagnostics/migration/diagnostics-source.candidate.json").read_text(encoding="utf-8"))["sourceObject"]
    def reject(self,fn):
        x=copy.deepcopy(self.d);fn(x)
        with self.assertRaises(ValueError):check(x,self.inv,self.src)
    def test_valid_distinct_pairs(self):self.assertEqual(check(self.d,self.inv,self.src),2)
    def test_wrong_provenance_layer(self):
        self.reject(lambda d:d["groups"][0]["contrastingScenario"].update(sourceLayer="DiagnosticRepository.kt"))
    def test_canonical_duplicate(self):
        self.reject(lambda d:d["groups"][0]["contrastingScenario"].update(scenarioId="vl80s.diag.gv-no-close"))
    def test_extended_scenario_not_an_extended_method(self):
        self.reject(lambda d:d["groups"][1].update(contrastIsSeparateCanonicalScenarioNotAnExtension=False))
    def test_no_historical_actions(self):
        self.reject(lambda d:d["groups"][0].update(operationalSteps=["fictional"]))
    def test_no_publishing(self):
        self.reject(lambda d:d["groups"][1].update(publicationStatus="ACTIVE"))
    def test_no_equipment_claim(self):
        self.reject(lambda d:d["groups"][1].update(exactInstalledEquipmentVerified=True))
    def test_keep_different_symptoms(self):
        self.reject(lambda d:d["groups"][1]["symptomCodes"].update(contrast="NO_MOVEMENT_STUCK_OR_COMMAND_LOST"))
if __name__=="__main__":unittest.main()
