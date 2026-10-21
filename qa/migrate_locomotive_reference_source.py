#!/usr/bin/env python3
"""Preserve the effective donor locomotive mass table as non-runtime source evidence."""

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content-packs/common/calculations/migration/source-assets/LocomotiveDatabase.kt"
DEST = ROOT / "content-packs/common/calculations/migration/locomotive-reference-source.candidate.json"
BLOB = "cd42e781f0e92e4849b6bb48233ebd27bd6e3c01"
PATH = "patch/app/src/main/java/ru/railbrake/calculator/core/LocomotiveDatabase.kt"
COMMIT = "3176d6ee228f0ed4b78371f45209e10c1c724eff"


def project():
    raw = SOURCE.read_bytes()
    assert hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == BLOB
    source = raw.decode("utf-8")
    defaults = {}
    for field in ("note", "massKind", "sourceNote"):
        match = re.search(r"val " + field + r': String = ("(?:\\.|[^"\\])*")', source)
        assert match, field
        defaults[field] = json.loads(match.group(1))
    body = source.split("val items = listOf(", 1)[1].split("\n    )", 1)[0]
    records = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        match = re.fullmatch(r"LocomotiveSpec\((.*)\),?", stripped)
        assert match, stripped
        fields = [json.loads(m.group()) for m in re.finditer(r'"(?:\\.|[^"\\])*"|\d+(?:\.\d+)?', match.group(1))]
        assert len(fields) in (4, 5, 6, 7), (stripped, fields)
        name, category, mass, axles = fields[:4]
        assert isinstance(name, str) and isinstance(category, str)
        assert isinstance(mass, (int, float)) and isinstance(axles, int)
        records.append({"sourceOrdinal": len(records), "sourceCall": stripped,
                        "name": name, "category": category, "massTons": mass,
                        "axles": axles,
                        "note": fields[4] if len(fields) > 4 else defaults["note"],
                        "massKind": fields[5] if len(fields) > 5 else defaults["massKind"],
                        "sourceNote": fields[6] if len(fields) > 6 else defaults["sourceNote"],
                        "explicitOptionalFields": fields[4:]})
    assert len(records) == 46 and len({r["name"] for r in records}) == 46
    return {"schemaVersion": 1, "donorCommit": COMMIT,
            "sourcePath": PATH, "sourceBlobSha": BLOB,
            "publicationStatus": "CANDIDATE", "runtimeImport": False,
            "actionDisposition": "INFORMATION_ONLY",
            "sourceNote": "Original Kotlin and call text retained. Values are donor reference inputs; variant and current authority are not established.",
            "recordCount": len(records), "records": records}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(project(), ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert DEST.read_text() == encoded
    else:
        DEST.write_text(encoded)
    print("LOCOMOTIVE_REFERENCE_SOURCE_PASS 46")


if __name__ == "__main__":
    main()
