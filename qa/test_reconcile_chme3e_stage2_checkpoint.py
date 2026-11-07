#!/usr/bin/env python3
"""Regression check for the bounded CHME3E Stage 2 historical relation."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Chme3eStage2CheckpointTest(unittest.TestCase):
    def test_relation_keeps_profile_data_non_runtime_and_guards_edb_isolation(self) -> None:
        relation_path = ROOT / "docs/data-migration/chme3e-stage2-checkpoint-relations.json"
        relation = json.loads(relation_path.read_text(encoding="utf-8"))

        self.assertEqual("CANDIDATE", relation["publicationStatus"])
        self.assertFalse(relation["runtimeImport"])
        self.assertFalse(relation["actionAuthorityGranted"])
        self.assertEqual(33, relation["counts"]["profileAtlasIds"])
        self.assertEqual(6, relation["counts"]["profileSchemes"])
        self.assertEqual(29, relation["counts"]["schemeDesignations"])
        self.assertEqual(
            ["CHME3-SYS-EDB", "CHME3T-EQ-BRAKE-RESISTORS", "CHME3T-EQ-EDB-CONTROL"],
            relation["forbiddenChme3tIds"],
        )

        result = subprocess.run(
            [sys.executable, "qa/reconcile_chme3e_stage2_checkpoint.py", "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("CHME3E_STAGE2_CHECKPOINT_PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
