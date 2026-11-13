#!/usr/bin/env python3
"""Regression check for the bounded CHME3-family interactive Stage 2 relation."""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELATION = ROOT / "docs/data-migration/chme3-interactive-stage2-checkpoint-relations.json"


class Chme3InteractiveStage2CheckpointTest(unittest.TestCase):
    def test_relation_keeps_historical_runtime_claims_non_runtime(self) -> None:
        relation = json.loads(RELATION.read_text(encoding="utf-8"))

        self.assertEqual("CANDIDATE", relation["publicationStatus"])
        self.assertFalse(relation["runtimeImport"])
        self.assertFalse(relation["currentAuthorityVerified"])
        self.assertFalse(relation["actionAuthorityGranted"])
        self.assertEqual(
            ["chme3-base", "chme3t-rheostatic", "chme3e-electronic"],
            relation["profileIds"],
        )
        self.assertEqual(
            {
                "chme3-base": 7,
                "chme3t-rheostatic": 8,
                "chme3e-electronic": 14,
            },
            relation["preservedFunctionalPairCounts"],
        )
        self.assertEqual(
            {
                "historicalEffectiveViews": 38,
                "historicalHotspots": 261,
                "historicalDirectedEdges": 215,
            },
            relation["historicalRuntimeClaims"],
        )
        self.assertEqual(
            "NOT_REIFIED_NO_BOUNDED_INTERACTIVE_RUNTIME_SOURCE",
            relation["historicalRuntimeClaimsDisposition"],
        )

        result = subprocess.run(
            ["python3", "qa/reconcile_chme3_interactive_stage2_checkpoint.py", "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("CHME3_INTERACTIVE_STAGE2_CHECKPOINT_PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
