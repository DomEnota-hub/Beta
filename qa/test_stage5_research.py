"""Negative review fixtures: all tests use nonoperational historical information."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_stage5_research import load, validate, visible_alternatives, PATTERNS

class Stage5ResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = [load(path) for path in PATTERNS]
    def fixture(self, scenario="gv"):
        return copy.deepcopy(next(x for x in self.items if scenario in x["scenarioId"]))
    def reject(self, change):
        d = self.fixture()
        change(d)
        with self.assertRaises(ValueError):
            validate(d)
    def test_all_drafts_structurally_valid(self):
        self.assertEqual([validate(d) for d in self.items],
                         [(10, 14, 5), (12, 14, 5)])
    def test_historical_not_shown_without_full_warning(self):
        for d in self.items:
            for v in ("short", "detailed"):
                for flags in ((False,True,True),(True,False,True),(True,True,False)):
                    self.assertEqual(visible_alternatives(d,v,d["authoringProfileId"],*flags),[])
                self.assertEqual(visible_alternatives(
                    d,v,"chme3t-rheostatic",True,True,True),[])
                self.assertGreater(len(visible_alternatives(
                    d,v,d["authoringProfileId"],True,True,True)),0)
    def test_candidate_only(self):
        self.reject(lambda d: d.update(publicationStatus="ACTIVE"))
    def test_cannot_upgrade_action(self):
        self.reject(lambda d: d.update(actionAuthorityGranted=True))
    def test_cannot_import_runtime(self):
        self.reject(lambda d: d.update(runtimeImport=True))
    def test_no_extended_execution(self):
        self.reject(lambda d: d["short"]["extendedRoutes"][0].update(executable=True))
    def test_no_historical_procedure_steps(self):
        self.reject(lambda d: d["detailed"]["extendedRoutes"][0].update(operationalSteps=["mock"]))
    def test_warning_cannot_be_skipped(self):
        self.reject(lambda d: d["historicalVisibility"].update(warningReadToEnd=False))
    def test_source_cannot_be_made_current(self):
        self.reject(lambda d: next(iter(d["sourceRecords"].values())).update(
            authorityForCurrentLocomotive=True))
    def test_duplicate_approach_disallowed(self):
        self.reject(lambda d: d["detailed"]["extendedRoutes"][0].update(
            approachId=d["short"]["extendedRoutes"][0]["approachId"]))
    def test_unknown_must_stop(self):
        self.reject(lambda d: d["short"]["nodes"][0]["responses"].update(
            UNKNOWN=d["short"]["nodes"][0]["responses"]["NO"]))
    def test_provenance_required(self):
        self.reject(lambda d: d["short"]["nodes"][0].update(sourceRefs=["INVENTED"]))
    def test_diverse_methods_not_multiple_links(self):
        self.reject(lambda d: d["short"]["extendedRoutes"][1].update(
            approachFocus=d["short"]["extendedRoutes"][0]["approachFocus"]))
    def test_source_mismatch_disallowed(self):
        self.reject(lambda d: d["short"]["extendedRoutes"][0]["nodes"][0].update(
            sourceRefs=["gvbook2005"]))
    def test_independent_main_graphs(self):
        self.reject(lambda d: d["detailed"].update(nodes=d["short"]["nodes"]))
    def test_wrong_2018_gv_citation_stays_blocked(self):
        self.assertFalse(self.fixture()["sourceRecords"]["gv2018"]["usableForScenario"])
        self.reject(lambda d: d["short"]["extendedRoutes"][1].update(sourceId="gv2018"))
    def test_bataisk_instruction_is_historical(self):
        self.assertEqual(self.fixture("ekg")["sourceRecords"]["ekgdepot"]["claimScopeStatus"],
                         "EXACT_LOCAL_CLAUSE_UNVERIFIED")
    def test_no_false_donor_graph_comparison(self):
        self.reject(lambda d: d["integrationAudit"].update(actualRuntimeGraphCompared=True))
    def test_variant_cannot_be_forged(self):
        self.reject(lambda d: d.update(exactInstalledVariantConfirmed=True))
    def test_synthetic_safe_stop_cannot_be_removed(self):
        self.reject(lambda d: d["short"]["nodes"][0]["responses"].update(UNKNOWN="missing"))
if __name__ == "__main__":
    unittest.main()
