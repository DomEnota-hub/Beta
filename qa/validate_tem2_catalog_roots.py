#!/usr/bin/env python3
"""Validate two original TEM2 catalog roots without runtime promotion."""

import json

from migrate_tem2_catalog_roots import SOURCE_DIR, SOURCES, TARGET, digest

candidate = json.loads(TARGET.read_text())
assert candidate["modelOwner"] == "tem2-family"
assert candidate["publicationStatus"] == "CANDIDATE" and candidate["runtimeImport"] is False
assert len(candidate["catalogs"]) == len(SOURCES) == 2
for row, (name, (blob, original_hash, count, profile)) in zip(candidate["catalogs"], SOURCES.items()):
    assert row["sourcePath"] == f"{SOURCE_DIR}/{name}" and row["sourceBlobSha"] == blob
    assert row["entryCountInExistingPacks"] == count
    assert row["sourceRootWithoutEntries"] == {"schemaVersion": 1, "profileId": profile}
    assert row["sourceRootSha256"] == digest(row["sourceRootWithoutEntries"]) == original_hash
print("TEM2_CATALOG_ROOTS_PASS", 2, 253)
