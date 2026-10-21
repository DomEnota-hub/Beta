#!/usr/bin/env python3
"""Check model-package link identity and variant compatibility across both pack contracts."""
import json
from collections import Counter
from pathlib import Path

from validate_migrated_data_array import BLOCKS, LINK_TARGET_TYPES


ROOTS = {"vl80s": "content-packs/electric/vl80s"}
ROOTS.update({block: directory for block, (directory, _, _) in BLOCKS.items()})


def check(root):
    records = {}
    counts = Counter()
    for block, directory in ROOTS.items():
        for path in sorted((root / directory).rglob("*.pack.json")):
            pack = json.loads(path.read_text())
            assert pack["manifest"]["entries"] == [e["id"] for e in pack["entries"]], path
            for entry in pack["entries"]:
                key = entry["id"]
                assert key not in records, ("duplicate ID", key, path)
                assert entry["owner"] == ({"kind": "COMMON"} if block == "common" else
                                           {"kind": "MODEL", "modelId": block}), key
                records[key] = (block, entry)
                counts[block] += 1
    links = Counter()
    for key, (block, entry) in records.items():
        source_variants = set(entry.get("applicability", {}).get("variantIds", []))
        for link in entry.get("links", []):
            target_block, target = records[link["targetId"]]
            assert LINK_TARGET_TYPES[link["type"]] == target["type"], (key, link)
            assert target_block == block or (block != "common" and target_block == "common"), (key, link)
            target_variants = set(target.get("applicability", {}).get("variantIds", []))
            edge_variants = set(link.get("applicability", {}).get("variantIds", []))
            if source_variants and target_variants:
                assert source_variants & target_variants, ("disjoint variants", key, link["targetId"])
            if edge_variants:
                assert edge_variants <= source_variants & target_variants, (key, link)
            links[block] += 1
    return counts, links


if __name__ == "__main__":
    counts, links = check(Path("."))
    assert counts == {"vl80s": 394, "common": 87, "ermak": 558,
                      "chme3-family": 796, "tem2-family": 348}, counts
    assert links == {"vl80s": 2805, "common": 77, "ermak": 4731,
                     "chme3-family": 5421, "tem2-family": 1153}, links
    print("STAGE2_MODEL_LINKS_PASS", sum(counts.values()), sum(links.values()))
