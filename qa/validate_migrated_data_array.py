#!/usr/bin/env python3
"""One-head cross-block structural gate for newly migrated Common/model packs."""
import argparse
import copy
import json
from pathlib import Path

BLOCKS = {
    "common": ("content-packs/common", 3, 87),
    "ermak": ("content-packs/electric/ermak", 27, 506),
    "chme3-family": ("content-packs/diesel/chme3-family", 38, 738),
    "tem2-family": ("content-packs/diesel/tem2-family", 17, 320),
}
LINK_TARGET_TYPES = {
    "RELATED_SCENARIO": "DIAGNOSTIC_SCENARIO",
    "EQUIPMENT": "EQUIPMENT",
    "ATLAS_SCHEME": "ATLAS_SCHEME",
    "ACCEPTANCE_ITEM": "ACCEPTANCE_ITEM",
    "TECHNICAL_DATA": "TECHNICAL_DATA",
    "KNOWLEDGE": "KNOWLEDGE",
    "SOURCE": "SOURCE",
    "FIRST_AID": "FIRST_AID",
    "SAFETY": "SAFETY",
}


def check(entries):
    ids = {}
    for block, e in entries:
        assert e["id"] not in ids, ("duplicate", e["id"])
        ids[e["id"]] = (block, e)
        assert e["publicationStatus"] == "CANDIDATE", e["id"]
        assert e["actionDisposition"] == "INFORMATION_ONLY", e["id"]
        assert e["provenance"] == e["sourceStatus"] == "UNKNOWN", e["id"]
        expected = {"kind": "COMMON"} if block == "common" else {
            "kind": "MODEL", "modelId": block}
        assert e["owner"] == expected, e["id"]
        if block != "common":
            assert e["applicability"]["modelIds"] == [block], e["id"]
    links = 0
    for block, e in entries:
        source_variants = set(e.get("applicability", {}).get("variantIds", []))
        for link in e.get("links", []):
            links += 1
            target_block, target = ids[link["targetId"]]
            assert link["type"] in LINK_TARGET_TYPES
            assert LINK_TARGET_TYPES[link["type"]] == target["type"]
            if block == "common":
                assert target_block == "common" and link["scope"] == "COMMON_INTERNAL"
            else:
                assert target_block in (block, "common")
                assert link.get("scope", "SAME_MODEL") == (
                    "SAME_MODEL" if target_block == block else "COMMON_TARGET")
                edge_variants = set(link.get("applicability", {}).get("variantIds", []))
                if edge_variants:
                    target_variants = set(target["applicability"]["variantIds"])
                    assert edge_variants <= source_variants & target_variants
    return len(ids), links


def load(root):
    entries = []
    for block, (directory, expected_packs, expected_entries) in BLOCKS.items():
        paths = sorted((root / directory).rglob("*.pack.json"))
        assert len(paths) == expected_packs, (block, len(paths))
        count = 0
        for path in paths:
            pack = json.loads(path.read_text())
            manifest = pack["manifest"]
            assert manifest["entries"] == [e["id"] for e in pack["entries"]]
            if block == "common":
                assert manifest["modelIds"] == [] and manifest["variantIds"] == []
            else:
                assert manifest["modelIds"] == [block]
            entries.extend((block, e) for e in pack["entries"])
            count += len(pack["entries"])
        assert count == expected_entries, (block, count)
    return entries


def negative_cases(entries):
    examples = (
        lambda a: a[0][1].update(owner={"kind":"MODEL","modelId":"ermak"}),
        lambda a: a.append(copy.deepcopy(a[0])),
        lambda a: a[0][1].update(publicationStatus="ACTIVE"),
    )
    for mutation in examples:
        mutated = copy.deepcopy(entries)
        mutation(mutated)
        try:
            check(mutated)
        except (AssertionError, KeyError):
            pass
        else:
            raise AssertionError("invalid cross-block data accepted")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path("."))
    a = p.parse_args()
    entries = load(a.root)
    assert check(entries)[0] == 1651
    negative_cases(entries)
    print("MIGRATED_DATA_ARRAY_PASS", *check(entries))
