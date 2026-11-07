#!/usr/bin/env python3
"""Preserve informational wording embedded in two historical Android asset builders."""

import argparse
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "content-packs/locomotive-migration/migration"
OUTPUT = BASE / "family-projection-literals.candidate.json"
PINS = {
    "tools/build_chme3_android_assets.py": "4392f7285a1f3c4e910710508919f97c6e96cd30",
    "tools/build_tem2_android_assets.py": "f8a8fcbacc9d4acabd921dd86e9f5cb1d1950fe8",
}


def project():
    files = []
    for source, blob in PINS.items():
        path = BASE / "source-assets" / Path(source).name
        raw = path.read_bytes()
        actual = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        assert actual == blob, source
        literals = []
        for node in ast.walk(ast.parse(raw.decode("utf-8"), filename=source)):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and any(
                "А" <= char <= "я" or char in "Ёё" for char in node.value
            ):
                literals.append({"line": node.lineno, "text": node.value,
                                 "sha256": hashlib.sha256(node.value.encode("utf-8")).hexdigest()})
        files.append({"sourcePath": source, "sourceBlobSha": blob,
                      "archivePath": path.relative_to(ROOT).as_posix(),
                      "occurrences": len(literals), "literals": literals})
    assert [file["occurrences"] for file in files] == [27, 46]
    return {"schemaVersion": 1, "donorCommit": "3176d6ee228f0ed4b78371f45209e10c1c724eff",
            "publicationStatus": "CANDIDATE", "runtimeImport": False,
            "interpretation": "Historical generated display literals, including warnings and aliases. Exact script preservation does not certify dynamic projection, source authority or new UI wording.",
            "files": files}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(project(), ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        assert OUTPUT.read_text(encoding="utf-8") == encoded
    else:
        OUTPUT.write_text(encoded, encoding="utf-8")
    print("FAMILY_PROJECTION_LITERAL_PASS 2 73")


if __name__ == "__main__":
    main()
