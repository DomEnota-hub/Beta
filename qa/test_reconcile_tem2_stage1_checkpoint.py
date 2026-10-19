#!/usr/bin/env python3
"""Regression check for the bounded TEM2/TEM2U Stage 1 relation."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Tem2Stage1CheckpointTest(unittest.TestCase):
    def test_relation_keeps_two_profiles_foundation_only_and_fail_closed(self) -> None:
        relation = json.loads(
            (ROOT / "docs/data-migration/tem2-stage1-checkpoint-relations.json").read_text(encoding="utf-8")
        )
        self.assertEqual("CANDIDATE", relation["publicationStatus"])
        self.assertFalse(relation["runtimeImport"])
        self.assertFalse(relation["actionAuthorityGranted"])
        self.assertEqual(["tem2-base", "tem2u-improved"], relation["profileIds"])
        self.assertEqual(9, relation["sourceCount"])
        self.assertEqual(
            ["TEM2-SRC-BRAKES-2026", "TEM2-SRC-POT-RZD-342-2025"],
            relation["currentConfirmedSourceIds"],
        )

        result = subprocess.run(
            [sys.executable, "qa/reconcile_tem2_stage1_checkpoint.py", "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("TEM2_STAGE1_CHECKPOINT_PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
