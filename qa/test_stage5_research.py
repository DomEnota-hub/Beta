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
                         [(10, 20, 5), (12, 20, 5)])
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
    def test_gv_2018_section_is_historical_only(self):
        d=self.fixture()
        self.assertTrue(d["sourceRecords"]["gv2018"]["usableForScenario"])
        self.assertFalse(d["sourceRecords"]["gv2018"]["authorityForCurrentLocomotive"])
        self.assertFalse(d["sourceRecords"]["gv2018"]["safeToExecuteHistoricalProcedures"])
        self.assertEqual(d["sourceRecords"]["gv2018"]["claimScopeStatus"],
                         "HISTORICAL_GV_SECTION_FOUND_NO_CURRENT_ACTION_AUTHORITY")
        self.reject(lambda d:d["sourceRecords"]["gv2018"].update(
            authorityForCurrentLocomotive=True))
    def test_bataisk_instruction_is_historical(self):
        self.assertEqual(self.fixture("ekg")["sourceRecords"]["ekgdepot"]["claimScopeStatus"],
                         "EXACT_LOCAL_CLAUSE_UNVERIFIED")
    def test_no_false_donor_graph_comparison(self):
        self.reject(lambda d: d["integrationAudit"].update(actualRuntimeGraphCompared=True))
    def test_variant_cannot_be_forged(self):
        self.reject(lambda d: d.update(exactInstalledVariantConfirmed=True))
    def test_synthetic_safe_stop_cannot_be_removed(self):
        self.reject(lambda d: d["short"]["nodes"][0]["responses"].update(UNKNOWN="missing"))
    def test_direct_donor_questions_are_distinct_and_non_operational(self):
        required={
            "vl80s.diag.gv-no-close":{"attempt-indication","trip-during-notch","relay-known"},
            "vl80s.diag.ekg-stuck":{"audible-motor","reset-only","position-specific"}
        }
        for draft in self.items:
            mapped={n["id"] for n in draft["detailed"]["nodes"]}
            self.assertTrue(required[draft["scenarioId"]]<=mapped)
            by={n["id"]:n for n in draft["detailed"]["nodes"]}
            for node_id in required[draft["scenarioId"]]:
                node=by[node_id]
                self.assertFalse(node["operationRequested"])
                self.assertIn("donorKotlin",node["sourceRefs"])
                self.assertEqual(by[node["responses"]["UNKNOWN"]]["type"],"STOP")
            self.assertFalse(draft["runtimeImport"])
            self.assertFalse(draft["actionAuthorityGranted"])

if __name__ == "__main__":
    unittest.main()
