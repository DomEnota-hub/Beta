#!/usr/bin/env python3
"""Check full pinned VL80S acceptance source without runtime promotion."""

import json

from migrate_vl80s_acceptance_source import DESTINATION, OBJECT_SHA256, SOURCE_PATH, SOURCE_SHA, digest

candidate = json.loads(DESTINATION.read_text())
assert candidate["sourcePath"] == SOURCE_PATH and candidate["sourceBlobSha"] == SOURCE_SHA
assert candidate["modelOwner"] == "vl80s"
assert candidate["publicationStatus"] == "CANDIDATE" and candidate["runtimeImport"] is False
obj = candidate["sourceObject"]
assert candidate["sourceObjectSha256"] == digest(obj) == OBJECT_SHA256
assert (len(obj["items"]), len(obj["routes"]), len(obj["zones"])) == (66, 7, 9)
assert (len(obj["designPrinciples"]), len(obj["gates"]), len(obj["sources"])) == (6, 3, 6)
assert len({x["id"] for x in obj["items"]}) == 66
assert len({x["id"] for x in obj["routes"]}) == 7
assert len({x["id"] for x in obj["zones"]}) == 9
print("VL80S_ACCEPTANCE_SOURCE_PASS", 66, 7, 9)
