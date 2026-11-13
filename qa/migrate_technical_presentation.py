#!/usr/bin/env python3
"""Preserve pinned Kotlin presentation vocabulary without enabling its behavior."""

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = "app/src/main/java/ru/railbrake/calculator/core/TechnicalPresentation.kt"
SOURCE_SHA = "9bca8e63e62390d65b5ed4e1208b1889999fd300"
DONOR_COMMIT = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
ARCHIVE = ROOT / "content-packs/locomotive-migration/source-assets/TechnicalPresentation.kt"
INVENTORY = ROOT / "content-packs/locomotive-migration/technical-presentation-vocabulary.candidate.json"
LITERAL_PAIR = re.compile(r'"((?:\\.|[^"\\])*)"\s+to\s+"((?:\\.|[^"\\])*)"')


def unquote(value):
    return json.loads('"' + value + '"')


def project(text):
    groups = {}
    for name, end, count in (
        ("technicalLocationLabels", "internal fun technicalLocationLabel", 78),
        ("exactLabels", "private val englishRules", 82),
        ("englishRules", "private val legacyIdentifier", 7),
    ):
        fragment = text[text.index("private val " + name):text.index(end)]
        rows = [{"key": unquote(k), "label": unquote(v)} for k, v in LITERAL_PAIR.findall(fragment)]
        assert len(rows) == count and len({r["key"] for r in rows}) == count, name
        groups[name] = rows
    hidden = text[text.index("private val hiddenMetadata"):text.index("private val technicalLocationLabels")]
    hidden_keys = re.findall(r'"([a-z_]+)"', hidden)
    assert len(hidden_keys) == len(set(hidden_keys)) == 10
    fragment = text[text.index("internal fun technicalStatusPresentation"):]
    arms = re.findall(r'((?:"[A-Z_]+"(?:,\s*)?)+)\s*->\s*"((?:\\.|[^"\\])*)"', fragment)
    status = [{"sourceStatuses": re.findall(r'"([A-Z_]+)"', keys), "label": unquote(label)}
              for keys, label in arms]
    assert len(status) == 16 and sum(len(r["sourceStatuses"]) for r in status) == 19
    return {
        "schemaVersion": 1,
        "recordKind": "HISTORICAL_TECHNICAL_PRESENTATION_VOCABULARY",
        "donorCommit": DONOR_COMMIT,
        "sourcePath": SOURCE_PATH,
        "sourceBlobSha": SOURCE_SHA,
        "publicationStatus": "CANDIDATE",
        "runtimeImport": False,
        "sourceStatusInterpretation": "DONOR_DISPLAY_WORDING_ONLY_NOT_CURRENT_REVIEW",
        "hiddenMetadataKeys": hidden_keys,
        "literalMappings": groups,
        "statusDisplayMappings": status,
        "unprojectedLogic": "Dynamic quantity, profile, filtering and rendering functions remain in the exact archived Kotlin source; no runtime behavior imported.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("donor", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    source = args.donor / SOURCE_PATH
    assert subprocess.check_output(["git", "hash-object", str(source)], text=True).strip() == SOURCE_SHA
    data = source.read_bytes()
    text = data.decode("utf-8")
    encoded = (json.dumps(project(text), ensure_ascii=False, indent=2) + "\n").encode()
    if args.check:
        assert ARCHIVE.read_bytes() == data and INVENTORY.read_bytes() == encoded
    else:
        ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
        ARCHIVE.write_bytes(data)
        INVENTORY.write_bytes(encoded)
    print("TECHNICAL_PRESENTATION_VOCABULARY_PASS", 167, 19)


if __name__ == "__main__":
    main()
