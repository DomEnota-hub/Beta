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
    def test_inherited_extension_rejected(self):
        x=self.fixture();x["versionDrafts"]["SHORT"]["extendedRoutes"]=[{"fiction":"yes"}];self.reject(x)
    def test_empty_source_gap_rejected(self):
        x=self.fixture();x["versionDrafts"]["DETAILED"]["extendedSourceGapReason"]="";self.reject(x)
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

if __name__=="__main__":
    unittest.main()
