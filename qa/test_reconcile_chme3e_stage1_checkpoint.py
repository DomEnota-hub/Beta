#!/usr/bin/env python3
"""Regression check for the CHME3E Stage 1 historical checkpoint relation."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Chme3eStage1CheckpointTest(unittest.TestCase):
    def test_guarded_relation_covers_profile_traits_and_edb_exclusions(self) -> None:
        relation_path = ROOT / "docs/data-migration/chme3e-stage1-checkpoint-relations.json"
        relation = json.loads(relation_path.read_text(encoding="utf-8"))

        self.assertEqual("CANDIDATE", relation["publicationStatus"])
        self.assertFalse(relation["runtimeImport"])
        self.assertFalse(relation["actionAuthorityGranted"])
        self.assertEqual(
            [
                "additional_electronic_control",
                "diesel_preheating_device",
                "no_factory_rheostatic_brake",
            ],
            relation["profileTraits"],
        )
        self.assertEqual(
            [
                "CHME3T-EQ-BRAKE-RESISTORS",
                "CHME3T-EQ-BRAKE-RESISTOR-FAN",
                "CHME3T-EQ-EDB-CONTROL",
            ],
            relation["chme3tOnlyEquipmentIds"],
        )

        result = subprocess.run(
            [sys.executable, "qa/reconcile_chme3e_stage1_checkpoint.py", "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("CHME3E_STAGE1_CHECKPOINT_PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
