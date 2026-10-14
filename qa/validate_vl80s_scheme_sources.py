#!/usr/bin/env python3
"""Validate the two complete non-runtime VL80S source catalogs."""

import json

from migrate_vl80s_scheme_sources import DESTINATION, SOURCE_DIR, SOURCES, digest

candidate = json.loads(DESTINATION.read_text())
assert candidate["modelOwner"] == "vl80s"
assert candidate["publicationStatus"] == "CANDIDATE" and candidate["runtimeImport"] is False
assert len(candidate["sources"]) == len(SOURCES) == 2
for row, (name, (blob, original_hash)) in zip(candidate["sources"], SOURCES.items()):
    assert row["sourcePath"] == f"{SOURCE_DIR}/{name}"
    assert row["sourceBlobSha"] == blob
    assert row["sourceObjectSha256"] == digest(row["sourceObject"]) == original_hash
electrical, pneumatic = (row["sourceObject"] for row in candidate["sources"])
assert (len(electrical["baseSchemes"]), len(electrical["modeOverlays"]),
        len(electrical["variantOverlays"]), len(electrical["candidateVariantFragments"])) == (8, 8, 8, 2)
assert (len(pneumatic["views"]), len(pneumatic["states"]),
        len(pneumatic["referenceBenchmarks"])) == (8, 13, 5)
print("VL80S_SCHEME_SOURCES_PASS", 2, 5)
