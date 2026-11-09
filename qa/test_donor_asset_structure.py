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


    def test_pinned_exam_questions_opaque_but_other_invalid_json_rejected(self):
        raw = b'not a JSON document'
        base = {'compressedBytes':len(raw),'gitBlobSha':module.blob_sha(raw),'format':'json','family':'shared'}
        opaque = module.scan(dict(base, sourcePath='app/src/main/assets/exam_questions.json'), raw)
        self.assertEqual(opaque['formatStatus'], 'OPAQUE_UNPARSED')
        with self.assertRaises(json.JSONDecodeError):
            module.scan(dict(base, sourcePath='app/src/main/assets/technical/broken.json'), raw)



if __name__ == '__main__':
    unittest.main()
