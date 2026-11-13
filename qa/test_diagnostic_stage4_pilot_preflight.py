"""Stage 4 negative cases must fail closed; test data do not describe railway actions."""
import copy
import unittest
from diagnostic_stage4_pilot_preflight import load, PILOTS, check_graph, check_pilot, main

class PilotTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory=load("docs/data-migration/diagnostic-corpus-analysis.json")
        cls.ledger=load("docs/diagnostics/DIAGNOSTIC_AUTHORING_STAGE2_CLAIM_LEDGER.json")
        cls.by={r["scenarioId"]:r for r in cls.inventory["rows"]}
    def fixture(self,key=None):
        key=key or next(iter(PILOTS))
        return copy.deepcopy(load(PILOTS[key]))
    def reject(self,record):
        with self.assertRaises(ValueError):
            check_pilot(record,self.by[record["scenarioId"]],self.ledger)
    def test_structural_pilots_are_review_drafts_only(self):
        out=main()
        self.assertEqual(len(out),2)
        self.assertGreater(out[next(iter(PILOTS))]["DETAILED"],out[next(iter(PILOTS))]["SHORT"])
    def test_executable_rejected(self):
        x=self.fixture();x["executable"]=True;self.reject(x)
    def test_published_rejected(self):
        x=self.fixture();x["publicationStatus"]="ACTIVE";self.reject(x)
    def test_false_source_authority_rejected(self):
        x=self.fixture();x["sourceAuthorityVerified"]=True;self.reject(x)
    def test_donor_blob_substitution_rejected(self):
        x=self.fixture();x["canonicalDonorBlob"]="0"*40;self.reject(x)
    def test_unverified_source_must_not_be_misrepresented_as_unbound(self):
        x=self.fixture();x["versionDrafts"]["SHORT"]["extendedSourceStatus"]="UNBOUND";self.reject(x)
    def test_historical_routes_must_keep_their_source(self):
        x=self.fixture();x["versionDrafts"]["DETAILED"]["extendedRoutes"][0]["sourceId"]="UNLINKED";self.reject(x)
    def test_unknown_cannot_become_no(self):
        x=self.fixture();v=x["versionDrafts"]["SHORT"]
        v["nodes"][0]["responses"]["UNKNOWN"]=v["nodes"][0]["responses"]["NO"]
        self.reject(x)
    def test_external_unreviewed_source_cannot_be_marked_current(self):
        x=self.fixture();x["sources"][1]["currentRevisionVerified"]=True;self.reject(x)
    def test_unanchored_node_rejected(self):
        x=self.fixture();x["versionDrafts"]["SHORT"]["nodes"][0]["donorAnchors"]=["INVENTED"]
        self.reject(x)
    def test_copying_short_into_detailed_rejected(self):
        x=self.fixture();x["versionDrafts"]["DETAILED"]=copy.deepcopy(x["versionDrafts"]["SHORT"])
        self.reject(x)
    def test_forbidden_action_in_node_rejected(self):
        x=self.fixture();x["versionDrafts"]["SHORT"]["nodes"][0]["permittedAction"]=True
        self.reject(x)
    def test_empty_equipment_confirmation_cannot_be_forged(self):
        x=self.fixture();x["installedEquipmentConfirmed"]=True;self.reject(x)
    def test_cross_model_profile_isolated(self):
        ch=self.fixture("chme3.diagnostics.chme3-diag-110")
        ch["canonicalDonorBlob"]=self.fixture()["canonicalDonorBlob"]
        self.reject(ch)
    def test_unreachable_node_rejected(self):
        x=self.fixture();v=x["versionDrafts"]["SHORT"]
        node=copy.deepcopy(v["nodes"][-1]);node["id"]="disconnected";v["nodes"].append(node)
        self.reject(x)

    def test_historical_evidence_is_retained_without_current_normative_approval(self):
        x=self.fixture()
        for version in ("SHORT","DETAILED"):
            self.assertGreater(len(x["versionDrafts"][version]["extendedRoutes"]),0)
            self.assertEqual(x["versionDrafts"][version]["extendedSourceStatus"],
                             "HISTORICAL_INFORMATION_BOUND")
        check_pilot(x,self.by[x["scenarioId"]],self.ledger)
    def test_archival_alternatives_must_differ_in_focus(self):
        x=self.fixture();alts=x["versionDrafts"]["SHORT"]["extendedRoutes"]
        alts[1]["approachFocus"]=alts[0]["approachFocus"];self.reject(x)
    def test_historical_action_never_enabled(self):
        x=self.fixture();x["versionDrafts"]["SHORT"]["extendedRoutes"][0]["executable"]=True;self.reject(x)
    def test_historical_operational_steps_not_importable(self):
        x=self.fixture();x["versionDrafts"]["DETAILED"]["extendedRoutes"][0]["procedureSteps"]=["mock-step"];self.reject(x)
    def test_no_warning_bypass(self):
        x=self.fixture();x["versionDrafts"]["SHORT"]["extendedRoutes"][0]["visibility"]["warningReadToEndRequired"]=False;self.reject(x)
    def test_historical_source_not_current_revision_requirement(self):
        x=self.fixture("chme3.diagnostics.chme3-diag-110")
        self.assertFalse(x["sources"][1]["currentRevisionVerified"])
        self.assertEqual(check_pilot(x,self.by[x["scenarioId"]],self.ledger)["SHORT"],10)
    def test_two_approaches_same_source_are_allowed(self):
        x=self.fixture("chme3.diagnostics.chme3-diag-110")
        refs=[a["sourceId"] for a in x["versionDrafts"]["DETAILED"]["extendedRoutes"]]
        self.assertEqual(refs.count("NOTIK-1996-ONLINE"),2)
        check_pilot(x,self.by[x["scenarioId"]],self.ledger)
    def test_exact_profile_not_forged(self):
        x=self.fixture();x["versionDrafts"]["SHORT"]["extendedRoutes"][0]["applicability"]["profileId"]="other-series";self.reject(x)
    def test_independent_ext_graphs(self):
        x=self.fixture();alts=x["versionDrafts"]["DETAILED"]["extendedRoutes"]
        alts[1]["nodes"]=alts[0]["nodes"]
        # The approach metadata differs, but reusing its graph is still accidental.
        self.assertNotEqual(alts[0]["approachFocus"],alts[1]["approachFocus"])
        # Graph uniqueness guard is tested in the validator.
        self.reject(x)

if __name__=="__main__":
    unittest.main()
