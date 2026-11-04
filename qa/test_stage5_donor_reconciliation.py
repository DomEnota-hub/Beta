"""Fail-closed Stage 5 direct-donor reconciliation fixtures."""
import copy,json,unittest
from validate_stage5_donor_reconciliation import ROOT,MANIFEST,check
class DonorReconciliationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=json.loads((ROOT/MANIFEST).read_text(encoding="utf-8"))
    def reject(self,mutate):
        data=copy.deepcopy(self.source)
        mutate(data)
        with self.assertRaises(ValueError):check(data)
    def test_real_pinned_donor_questions_are_not_synthetic(self):
        self.assertEqual(len(check(self.source)),2)
    def test_cannot_claim_executable_runtime_compared(self):
        self.reject(lambda m:m["items"][0].update(fullFiveNodeRuntimeGraphCompared=True))
    def test_cannot_accept_unmapped_question(self):
        self.reject(lambda m:m["items"][0]["questionReconciliation"][1].update(coverage="COMPLETE"))
    def test_unsafe_missing_donor_stop(self):
        self.reject(lambda m:m["items"][0].update(donorStopConditions=[]))
    def test_donor_question_cannot_change_silently(self):
        self.reject(lambda m:m["items"][1]["donorQuestions"][0].update(question="Other"))
    def test_cannot_invent_graph_node(self):
        self.reject(lambda m:m["items"][0]["questionReconciliation"][0].update(draftNodes=["short:invented"]))
    def test_cannot_publish_weakly_verified_kotlin_record(self):
        self.reject(lambda m:m.update(technicalAcceptance="APPROVED"))
    def test_cannot_mark_missing_branch_as_mapped(self):
        self.reject(lambda m:m["items"][1]["questionReconciliation"][1].update(
            draftNodes=["short:danger"]))
if __name__=="__main__":
    unittest.main()
