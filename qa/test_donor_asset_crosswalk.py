"""Negative and positive tests for donor raw-blob integrity and runtime gates."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("crosswalk", Path(__file__).with_name("validate_donor_asset_crosswalk.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CrosswalkTests(unittest.TestCase):
    def test_git_blob_hash_uses_git_header(self):
        self.assertEqual(module.blob_sha(b"hello\n"), "ce013625030ba8dba906f756967f9e9ca394464a")

    def test_raw_copy_valid_and_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "content-packs/electric/ermak/migration/source-assets/example.json.gz"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"payload")
            module.validate_raw_copy(root, target.relative_to(root).as_posix(), module.blob_sha(b"payload"), 7)
            with self.assertRaises(AssertionError):
                module.validate_raw_copy(root, target.relative_to(root).as_posix(), module.blob_sha(b"tampered"), 7)
            with self.assertRaises(AssertionError):
                module.validate_raw_copy(root, target.relative_to(root).as_posix(), module.blob_sha(b"payload"), 8)

    def test_runtime_index_blocks_cross_model_and_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "content-packs/electric/vl80s"
            base.mkdir(parents=True)
            pack = base / "diagnostics/recommended/ok.pack.json"
            pack.parent.mkdir(parents=True)
            pack.write_text("{}")
            index = base / "runtime-index.json"
            import json
            index.write_text(json.dumps({"modelId": "vl80s", "packs": ["electric/vl80s/diagnostics/recommended/ok.pack.json"]}))
            self.assertEqual(module.validate_runtime_index(root, "content-packs/electric/vl80s", "vl80s"), 1)
            for bad in ["electric/ermak/diagnostics/recommended/ok.pack.json", "electric/vl80s/diagnostics/research/ok.pack.json", "electric/vl80s/diagnostics/../recommended/ok.pack.json"]:
                index.write_text(json.dumps({"modelId": "vl80s", "packs": [bad]}))
                with self.assertRaises(AssertionError, msg=bad):
                    module.validate_runtime_index(root, "content-packs/electric/vl80s", "vl80s")

    def test_unsafe_paths_rejected(self):
        for path in ["../secret", "/tmp/file", "x/../../y", "foo\\bar"]:
            with self.assertRaises(AssertionError):
                module.safe_relative(path)


    def test_shared_split_object_family_cannot_be_forged(self):
        import copy
        import json
        baseline = json.loads(module.CROSSWALK.read_text(encoding="utf-8"))
        self.assertEqual(module.validate(module.ROOT, baseline)[0], 36)
        forged = copy.deepcopy(baseline)
        split = next(row for row in forged["assets"]
                     if row["recordParity"] == "SOURCE_SPLIT_OBJECT_EQUIVALENT_CANDIDATE")
        split["family"] = "ermak"
        with self.assertRaises(AssertionError):
            module.validate(module.ROOT, forged)

    def test_shared_split_object_requires_ci_evidence(self):
        import copy
        import json
        baseline = json.loads(module.CROSSWALK.read_text(encoding="utf-8"))
        forged = copy.deepcopy(baseline)
        split = next(row for row in forged["assets"]
                     if row["recordParity"] == "SOURCE_SPLIT_OBJECT_EQUIVALENT_CANDIDATE")
        split.pop("evidenceWorkflow", None)
        with self.assertRaises(AssertionError):
            module.validate(module.ROOT, forged)

if __name__ == "__main__":
    unittest.main()
