#!/usr/bin/env python3
"""Validate complete source preservation independently of transformed packs."""

import json

from migrate_vl80s_diagnostic_source import (
    DESTINATION, SOURCE_BLOB, SOURCE_JSON_SHA256, SOURCE_PATH, digest,
)

inventory = json.loads(DESTINATION.read_text())
assert inventory["sourcePath"] == SOURCE_PATH
assert inventory["sourceBlobSha"] == SOURCE_BLOB
assert inventory["sourceObjectSha256"] == SOURCE_JSON_SHA256
assert inventory["publicationStatus"] == "CANDIDATE"
assert inventory["runtimeImport"] is False and inventory["actionAuthorityGranted"] is False
source = inventory["sourceObject"]
assert digest(source) == SOURCE_JSON_SHA256
assert len(source["scenarios"]) == 103
assert len({row["id"] for row in source["scenarios"]}) == 103
assert len(source["edges"]) == 1181
assert len(source["acceptanceHintCorrections"]) == 7
assert len(source["integrationExceptions"]) == 2
print("VL80S_DIAGNOSTIC_SOURCE_PASS", 103, 1181, 7, 2)
