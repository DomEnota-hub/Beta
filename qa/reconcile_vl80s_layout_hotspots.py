#!/usr/bin/env python3
"""Check the 15 VL80S Atlas hotspot records against their pinned Kotlin literals."""

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content-packs/electric/vl80s/atlas/interactive/migration/source-assets/KnowledgeRepository.kt"
PACK = ROOT / "content-packs/electric/vl80s/atlas/interactive/layout-hotspots.json"
SOURCE_BLOB = "b37ead2d66c0c976bcc850f9cde4fddc0e198fb3"
STRING = r'"(?:\\.|[^"\\])*"'


def source_hotspots(text):
    section = text.split("val vl80LayoutHotspots = listOf(\n", 1)[1].split("\n    )", 1)[0]
    blocks = re.findall(r"        DiagramHotspot\((.*?)\n        \),?", section, re.S)
    assert len(blocks) == 15
    entries = []
    for block in blocks:
        entry = {}
        for field in ("id", "title", "subtitle", "details"):
            literal = re.search(r"\b" + field + r" = (" + STRING + r")", block)
            assert literal is not None, (field, block[:80])
            entry[field] = json.loads(literal.group(1))
        details = re.search(r"learnMore = listOf\((.*?)\n            \)", block, re.S)
        assert details is not None, entry["id"]
        entry["learnMore"] = [json.loads(value) for value in re.findall(STRING, details.group(1))]
        assert len(entry["learnMore"]) == 5, entry["id"]
        bounds = {}
        for field in ("left", "top", "right", "bottom"):
            literal = re.search(r"\b" + field + r" = (0?\.\d+)f", block)
            assert literal is not None, (entry["id"], field)
            bounds[field] = float(literal.group(1))
        entry["bounds"] = bounds
        entries.append(entry)
    return entries


def main():
    raw = SOURCE.read_bytes()
    assert hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == SOURCE_BLOB
    pack = json.loads(PACK.read_text(encoding="utf-8"))
    assert pack["sourceSnapshot"]["blobSha"] == SOURCE_BLOB
    originals = source_hotspots(raw.decode("utf-8"))
    projected = [{key: value for key, value in item.items() if key != "equipmentId"}
                 for item in pack["hotspots"]]
    assert projected == originals
    print("VL80S_LAYOUT_HOTSPOT_PARITY_PASS", len(originals))


if __name__ == "__main__":
    main()
