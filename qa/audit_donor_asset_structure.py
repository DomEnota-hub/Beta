#!/usr/bin/env python3
"""Read pinned donor JSON/GZIP assets without trusting transport or filenames.

Outputs discovery-only structural counts. It does not certify semantic migration,
publication status, profile applicability, or safety authority.
"""
import argparse
import gzip
import json
import time
import urllib.request
from pathlib import Path

from validate_donor_asset_crosswalk import blob_sha

BASE = 'https://raw.githubusercontent.com/DomEnota-hub/Test-/'
MAX_DECODED_BYTES = 40 * 1024 * 1024


def scan(row: dict, raw: bytes) -> dict:
    assert len(raw) == row['compressedBytes'], row['sourcePath']
    assert blob_sha(raw) == row['gitBlobSha'], row['sourcePath']
    decoded = gzip.decompress(raw) if row['format'] == 'json.gz' else raw
    assert len(decoded) <= MAX_DECODED_BYTES, row['sourcePath']
    try:
        data = json.loads(decoded.decode('utf-8-sig'))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        # The pinned exam_questions.json is opaque/encoded despite its extension.
        # Do not guess a decoding scheme or silently reinterpret other assets.
        if row['sourcePath'] != 'app/src/main/assets/exam_questions.json':
            raise
        return {
            'sourcePath': row['sourcePath'], 'gitBlobSha': row['gitBlobSha'],
            'family': row['family'], 'encodedBytes': len(raw), 'decodedBytes': len(decoded),
            'formatStatus': 'OPAQUE_UNPARSED', 'parseErrorType': type(exc).__name__,
            'topLevelKeys': [], 'arrays': {}, 'objects': {},
            'totalTopLevelArrayElements': 0, 'disposition': 'STRUCTURE_ONLY_NOT_PUBLISHED',
        }
    fields = data if isinstance(data, dict) else {'$root': data}
    arrays = {}
    objects = {}
    for key, value in fields.items():
        if isinstance(value, list):
            ids = [str(x['id']) for x in value if isinstance(x, dict) and x.get('id') is not None]
            arrays[key] = {
                'count': len(value), 'withId': len(ids),
                'uniqueIds': len(set(ids)), 'duplicateIdOccurrences': len(ids) - len(set(ids)),
                'firstId': ids[0] if ids else None,
            }
        elif isinstance(value, dict):
            objects[key] = {'keys': len(value)}
    return {
        'sourcePath': row['sourcePath'], 'gitBlobSha': row['gitBlobSha'],
        'family': row['family'], 'encodedBytes': len(raw), 'decodedBytes': len(decoded),
        'formatStatus': 'JSON_PARSED', 'topLevelKeys': list(fields), 'arrays': arrays, 'objects': objects,
        'totalTopLevelArrayElements': sum(x['count'] for x in arrays.values()),
        'disposition': 'STRUCTURE_ONLY_NOT_PUBLISHED',
    }


def download(row: dict, commit: str) -> bytes:
    url = BASE + commit + '/' + row['sourcePath']
    last = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'RailBrake-Pinned-Audit/1.0'}), timeout=40) as response:
                return response.read(2 * 1024 * 1024)
        except Exception as exc:
            last = exc
            if attempt < 3:
                time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"failed to fetch pinned donor asset {row['sourcePath']}: {last}")


def audit(manifest: dict, fetch=download) -> dict:
    rows = []
    for asset in manifest['assets']:
        row = scan(asset, fetch(asset, manifest['donor']['commit']))
        rows.append(row)
        print('SOURCE_STRUCTURE', row['sourcePath'], 'arrays=', row['totalTopLevelArrayElements'], 'decoded=', row['decodedBytes'], flush=True)
    return {
        'schemaVersion': 1, 'donor': manifest['donor'],
        'auditStatus': 'STRUCTURAL_DISCOVERY_ONLY', 'assets': rows,
        'summary': {
            'assets': len(rows),
            'decodedBytes': sum(x['decodedBytes'] for x in rows),
            'topLevelArrayElements': sum(x['totalTopLevelArrayElements'] for x in rows),
            'families': {k: sum(x['family'] == k for x in rows) for k in sorted({x['family'] for x in rows})},
        },
    }


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--manifest', type=Path, default=Path('docs/migration/donor-asset-crosswalk.json'))
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
    result = audit(manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('DONOR_STRUCTURE_PASS', result['summary'])
