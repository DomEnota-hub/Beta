#!/usr/bin/env python3
"""Check the non-runtime VL80S root context and three zone records."""

import json

from migrate_vl80s_equipment_context import CONTEXT_SHA, SOURCE_PATH, SOURCE_SHA, TARGET, ZONE_IDS, digest

candidate = json.loads(TARGET.read_text())
assert candidate["sourcePath"] == SOURCE_PATH and candidate["sourceBlobSha"] == SOURCE_SHA
assert candidate["modelOwner"] == "vl80s"
assert candidate["publicationStatus"] == "CANDIDATE" and candidate["runtimeImport"] is False
assert candidate["recordCountPreservedInEquipmentPacks"] == 89
context = candidate["sourceRootWithoutRecords"]
assert candidate["sourceRootSha256"] == digest(context) == CONTEXT_SHA
assert tuple(z["id"] for z in context["zones"]) == ZONE_IDS
assert [digest(z) for z in context["zones"]] == [
    "9246ef9a4e11fbd30c0d2a35b94a37f6beb88559fad80f018210eac34d1bb7d5",
    "2e8ca708f79f427c851e7df01a32d1592f602635867fa8cac9fd0ca3d1216b6f",
    "c3b298b62c73b8849f40a17c4a455b6b0daabd2b175b73992ff143d92b8c5961",
]
assert len(context["sources"]) == 10
print("VL80S_EQUIPMENT_CONTEXT_PASS", 89, 3)
