"""Fail closed when generator provenance is promoted into Stage 7 authority."""
import copy
import json
import unittest
from pathlib import Path

from validate_ermak_generator_dispositions import DEST, LEDGER, validate

ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / LEDGER


class ErmakGeneratorDispositionTest(unittest.TestCase):
    def test_no_stage7_promotion(self):
        data = json.loads((ROOT / DEST).read_text(encoding="utf-8"))
        broken = copy.deepcopy(data)
        broken["stage7AutoLink"] = True
        with self.assertRaises(AssertionError):
            validate(ROOT, LEDGER_PATH, broken)

    def test_no_source_code_action_authority(self):
        data = json.loads((ROOT / DEST).read_text(encoding="utf-8"))
        broken = copy.deepcopy(data)
        broken["rows"][0]["authority"] = "APPROVED"
        with self.assertRaises(AssertionError):
            validate(ROOT, LEDGER_PATH, broken)


if __name__ == "__main__":
    unittest.main()
