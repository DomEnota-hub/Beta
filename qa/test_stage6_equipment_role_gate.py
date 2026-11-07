"""Stage6 adversarial serial-number, equipment and crew/repair role checks."""
import copy
import json
import unittest
from validate_stage6_equipment_role_gate import ROOT, GATE_PATH, LEDGER_PATH, ROUTES, check

class EquipmentAndRoleGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gate = json.loads(GATE_PATH.read_text(encoding="utf-8"))
        cls.ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
        cls.routes = {k: json.loads((ROOT / p).read_text(encoding="utf-8"))
                      for k,p in ROUTES.items()}

    def reject(self, change):
        data = copy.deepcopy(self.gate)
        change(data)
        with self.assertRaises(ValueError):
            check(data, self.ledger, self.routes)

    def test_real_archived_source_can_still_be_read(self):
        self.assertEqual(check(self.gate, self.ledger, self.routes)["historicalClaims"], 4)

    def test_serial_1897_cannot_automatically_set_up1(self):
        self.reject(lambda d: d["cases"][1]["indicatorHistoricalTransition"].update(
            automaticIndicatorModelAssignment=True))

    def test_interchangeability_cannot_be_erased(self):
        self.reject(lambda d: d["cases"][1]["indicatorHistoricalTransition"].update(
            explicitlyInterchangeable=False))

    def test_known_number_not_proof_of_installed_device(self):
        self.reject(lambda d: d["cases"][1]["indicatorHistoricalTransition"].update(
            factoryNumberIsInstalledEquipmentProof=True))

    def test_current_indicator_cannot_be_inferred(self):
        self.reject(lambda d: d["cases"][1].update(installedPositionIndicator="УП-1"))

    def test_equipment_type_from_old_manual_not_installed_gv(self):
        self.reject(lambda d: d["cases"][0].update(installedSwitchType="ВОВ-25А-10/400УХЛ1"))

    def test_relay_204_not_auto_matched(self):
        self.reject(lambda d: d["cases"][1]["relayHistoricalReference"].update(
            bindingToCurrentInstalledScheme="CONFIRMED"))

    def test_crew_rules_not_individual_repair_permit(self):
        self.reject(lambda d: d["sources"]["crewSafety2024"].update(
            crewRepairProcedureAuthorized=True))

    def test_2025_repair_rules_not_crew_authority(self):
        self.reject(lambda d: d["sources"]["maintenanceSafety2025"].update(
            verifiedCrewOperationAuthority=True))

    def test_must_preserve_local_depot_instruction_gap(self):
        self.reject(lambda d: d["sources"]["crewSafety2024"].update(
            localDepotInstructionsChecked=True))

    def test_one_publisher_book_two_title_strings_not_silently_overwritten(self):
        self.reject(lambda d: d["sources"]["scheme2005"]["identity"].update(
            publisherCatalogTitle=d["sources"]["scheme2005"]["identity"]["printedScanTitle"]))

    def test_hist_source_date_does_not_approve_operating_action(self):
        self.reject(lambda d: d["sources"]["manual1990"].update(grantsActionAuthority=True))

    def test_warning_not_authority(self):
        self.reject(lambda d: d["historicalInformationalVisibility"].update(
            actionAuthorityGranted=True))

    def test_no_runtime_promotion(self):
        self.reject(lambda d: d.update(runtimeImport=True))

    def test_source_with_actual_equipment_is_not_yet_verified(self):
        self.reject(lambda d: d["currentAuthorityGate"].update(
            installedEquipmentConfirmed=True))

    def test_stage_six_cannot_be_marked_accepted(self):
        self.reject(lambda d: d.update(stageReviewStatus="ACCEPTED"))

if __name__ == "__main__":
    unittest.main()
