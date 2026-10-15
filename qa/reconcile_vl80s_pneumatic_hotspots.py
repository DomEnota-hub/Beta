#!/usr/bin/env python3
"""Compare every legacy pneumatic hotspot field with the pinned Kotlin source."""

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content-packs/electric/vl80s/atlas/interactive/migration/source-assets/KnowledgeBaseScreen.kt"
PACK = ROOT / "content-packs/electric/vl80s/atlas/interactive/pneumatic-flows.json"
SOURCE_BLOB = "0f18989087a7f4f2efcbdd46bdf05b1065d8f54c"


def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def source_components(text):
    section = text.split("private val pneumaticComponents = listOf(\n", 1)[1].split("\n)\n", 1)[0]
    lines = [line.strip() for line in section.splitlines() if line.strip()]
    assert len(lines) == 10
    components = []
    for index, line in enumerate(lines, 1):
        assert line.startswith("PneumaticComponent(") and line.endswith(("),", ")")), index
        values = re.findall(r'"(?:\\.|[^"\\])*"|(?:0|1)\.\d+f', line)
        assert len(values) == 9, (index, len(values))
        strings = [json.loads(value) for value in values if value.startswith('"')]
        bounds = [float(value[:-1]) for value in values if value.endswith("f")]
        assert len(strings) == 5 and len(bounds) == 4, index
        components.append({
            "id": f"legacy-pneumatic-{index:02}",
            "title": strings[0], "details": strings[1],
            "bounds": dict(zip(("left", "top", "right", "bottom"), bounds)),
            "principle": strings[2], "faultSigns": strings[3], "checks": strings[4],
        })
    return components


def main():
    raw = SOURCE.read_bytes()
    assert git_blob(raw) == SOURCE_BLOB
    pack = json.loads(PACK.read_text(encoding="utf-8"))
    assert any(snapshot.get("blobSha") == SOURCE_BLOB and snapshot.get("role") == "equipment-hotspots"
               for snapshot in pack["sourceSnapshots"])
    assert pack["components"] == source_components(raw.decode("utf-8"))
    print("VL80S_PNEUMATIC_HOTSPOT_PARITY_PASS", len(pack["components"]))


if __name__ == "__main__":
    main()
