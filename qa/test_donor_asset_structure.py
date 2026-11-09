import gzip
import importlib.util
import json
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('structure', Path(__file__).with_name('audit_donor_asset_structure.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class StructureTests(unittest.TestCase):
    def test_plain_and_compressed_records(self):
        raw = json.dumps({'entries': [{'id':'a'}, {'id':'a'}, {'id':'b'}], 'meta': {'v': 1}}).encode()
        for encoded, fmt in [(raw, 'json'), (gzip.compress(raw), 'json.gz')]:
            row = {'sourcePath': 'test.' + fmt, 'compressedBytes': len(encoded), 'gitBlobSha': module.blob_sha(encoded), 'format': fmt, 'family': 'test'}
            result = module.scan(row, encoded)
            self.assertEqual(result['arrays']['entries']['count'], 3)
            self.assertEqual(result['arrays']['entries']['duplicateIdOccurrences'], 1)
            self.assertEqual(result['disposition'], 'STRUCTURE_ONLY_NOT_PUBLISHED')

    def test_modified_source_rejected(self):
        raw = b'{"entries":[]}'
        row = {'sourcePath':'test.json','compressedBytes':len(raw),'gitBlobSha':module.blob_sha(raw),'format':'json','family':'test'}
        with self.assertRaises(AssertionError):
            module.scan(row, raw[:-1] + b' ')


if __name__ == '__main__':
    unittest.main()
