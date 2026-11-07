#!/usr/bin/env python3
"""Check the archived display vocabulary and non-runtime candidate projection."""

import json
import subprocess

from migrate_technical_presentation import ARCHIVE, INVENTORY, SOURCE_SHA, project

assert subprocess.check_output(["git", "hash-object", str(ARCHIVE)], text=True).strip() == SOURCE_SHA
expected = project(ARCHIVE.read_text())
actual = json.loads(INVENTORY.read_text())
assert actual == expected
assert actual["runtimeImport"] is False and actual["publicationStatus"] == "CANDIDATE"
assert len(actual["literalMappings"]["technicalLocationLabels"]) == 78
assert len(actual["literalMappings"]["exactLabels"]) == 82
assert len(actual["literalMappings"]["englishRules"]) == 7
assert len(actual["statusDisplayMappings"]) == 16
assert sum(len(r["sourceStatuses"]) for r in actual["statusDisplayMappings"]) == 19
print("TECHNICAL_PRESENTATION_PASS", 167, 19)
