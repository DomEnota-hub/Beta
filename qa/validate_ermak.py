#!/usr/bin/env python3
"""Ermak snapshot completeness and fail-closed policy checks."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

from migrate_ermak import ASSETS, BASE, build, read_asset

OUTPUT_SHA256 = {
    "equipment-01.pack.json": "f44f5c7ba25c79b32c566fbaa1f4c7f188a8b63f01013fb578b2534c398cadb8",
    "equipment-02.pack.json": "37162aee26d6494ad3d63dbbe9bfd4c3cfe2a6d107accc510fbd86c85a8ff6a9",
    "equipment-03.pack.json": "a53b6cf87ed2e7ba7a80dbb7b963fecab184ef61f6a4217131be3e36dd685a0a",
    "equipment-04.pack.json": "013e9c810613e69e54f7d37a69828d3b78b81e917c1c7c567e1be0c460be86fb",
    "equipment-05.pack.json": "932231e86073a64aa5ebbd6bc891beb357be7c6f531d5a1047e8c15b97603228",
    "equipment-06.pack.json": "12b2c1863593ec5831c8a797f91ac293208fda905e18e3d5aff2b223b4e6880b",
    "schemes-01.pack.json": "6f024f1117e6d6ec6623f7062dd1ad01f4473e99af71df99651da2e71ca5642d",
    "schemes-02.pack.json": "ffe06abc7be76d728cc5f6138a6c434153d926e11654e653d433a03749a6aa24",
    "diagnostics-01.pack.json": "016182b1b035a66fbce038b64a1f1787c4d748a4f31212b0569c503b9df28328",
    "diagnostics-02.pack.json": "f57bfeb2e04aeeed34df8d785421948ae1273c3ff3903f0ef06d4b0466ed2994",
    "diagnostics-03.pack.json": "c64d454bcaf72a41cc0b500fdbe6802101da1ef889cce3e242bc27ec3a10a49b",
    "diagnostics-04.pack.json": "9feb7fca6727c2a99365e03693f54006bfc81a23a458fb793cf7ba22352f6931",
    "diagnostics-05.pack.json": "3fe35d130785cc431b7048315963a56510ac8fb599b77bb3eda7f39aa3ec4d21",
    "diagnostics-06.pack.json": "3d579bdaaedebced51ae16c117807f838a4c9512e963476f3d4786a95c9fcc78",
    "diagnostics-07.pack.json": "8d65eae72e16392b713032fccbea1b51ecb64a0fd9a49570cc9a59f8a424903d",
    "knowledge-01.pack.json": "4801967c4f5432052135dd33cf6a577c5372ed1eb8ec608683bfff37acd3c7af",
    "knowledge-02.pack.json": "e33c71d2b96e11a0bd6d682e6703a0bc51046a03d828ad52ab5fdc7cf15918bc",
    "knowledge-03.pack.json": "227eb3bd4006b1a2e4c206fe070c5e52a5562fecd52d4d387bcaa138d2dfabe2",
    "knowledge-04.pack.json": "abe68c942cbedf3dc69e2215d4345ca1b1b67d61b869c3789b1ee3944216a123",
    "knowledge-05.pack.json": "08dacf467cbee602f2d32734e4c5d860e8a12da5d99c9fc83ebbec19051118ed",
    "knowledge-06.pack.json": "8a3088ed9d8d6e8c4b03b36c852527d18094ef6e81bff7898681b3fe7de56a8a",
    "knowledge-07.pack.json": "047a79cf942d201d062453c36f9e91377249a8bc8cd4c9b4cf7302c650f4f27a",
}

COUNTS = {"equipment": 111, "knowledge": 138, "diagnostics": 136, "schemes": 22}
TYPES = {n: v[1] for n, v in ASSETS.items()}


def pack_paths(root):
    subdirs = {"equipment": "atlas/equipment", "knowledge": "technical-data/knowledge",
               "diagnostics": "diagnostics/recommended", "schemes": "atlas/schemes"}
    return {n: sorted((root / BASE / subdirs[n]).glob(f"{n}-*.pack.json")) for n in COUNTS}


def validate(root, donor_dir=None):
    groups = {}
    all_entries = []
    for name, paths in pack_paths(root).items():
        assert len(paths) == (COUNTS[name] + 19) // 20, (name, paths)
        entries = []
        for path in paths:
            assert hashlib.sha256(path.read_bytes()).hexdigest() == OUTPUT_SHA256[path.name]
            pack = json.loads(path.read_text())
            m = pack["manifest"]
            assert m["packId"] == f"ermak.{name}.{len(entries)//20 + 1:02d}"
            assert m["modelIds"] == ["ermak"] and m["variantIds"] == []
            assert m["checksums"] == {f"ermak_{name}.json.gz.gitBlob": ASSETS[name][2]}
            assert m["entries"] == [e["id"] for e in pack["entries"]]
            assert 0 < len(pack["entries"]) <= 20
            entries += pack["entries"]
        assert len(entries) == COUNTS[name]
        for e in entries:
            assert e["type"] == TYPES[name]
            assert e["owner"] == {"kind": "MODEL", "modelId": "ermak"}
            assert e["applicability"] == {"modelIds": ["ermak"]}
            assert e["publicationStatus"] == "CANDIDATE"
            assert e["provenance"] == e["sourceStatus"] == "UNKNOWN"
            assert e["actionDisposition"] == "INFORMATION_ONLY"
            assert e["sourceObject"]["sourcePath"] == f"app/src/main/assets/technical/ermak_{name}.json.gz"
            assert e["sourceObject"]["sourceBlobSha"] == ASSETS[name][2]
            assert e["sourceObject"]["object"]["id"] == e["id"]
            assert isinstance(e["sourceObject"]["object"], dict)
        groups[name] = entries
        all_entries += entries
    ids = [e["id"] for e in all_entries]
    assert len(ids) == len(set(ids)) == 407
    scenario_ids = {e["id"] for e in groups["diagnostics"]}
    node_total = branch_total = 0
    for e in groups["diagnostics"]:
        graph = e["sourceObject"]["object"].get("graph") or {}
        nodes = graph.get("nodes", [])
        node_ids = [n["id"] for n in nodes]
        assert nodes and len(node_ids) == len(set(node_ids))
        assert graph.get("startNodeId") in node_ids
        node_total += len(nodes)
        for node in nodes:
            for choice in node.get("choices", []):
                assert (choice.get("nextNodeId") in node_ids or
                        choice.get("nextScenarioId") in scenario_ids)
                branch_total += 1
    assert (node_total, branch_total) == (2535, 2248)
    if donor_dir:
        for name in COUNTS:
            originals = read_asset(name, donor_dir)
            assert [e["sourceObject"]["object"] for e in groups[name]] == originals
            expected = build(donor_dir)
            for path, content in expected.items():
                actual = (root / path).read_text()
                assert actual == content, path
    return groups


def negative_cases(root):
    groups = validate(root)
    for mutation in (
        lambda e: e.update(publicationStatus="ACTIVE"),
        lambda e: e["sourceObject"].pop("object"),
        lambda e: e.update(owner={"kind":"MODEL", "modelId":"vl80s"}),
    ):
        sample = copy.deepcopy(groups["equipment"][0])
        mutation(sample)
        try:
            assert sample["publicationStatus"] == "CANDIDATE"
            assert sample["owner"] == {"kind":"MODEL", "modelId":"ermak"}
            assert sample["sourceObject"]["object"]["id"] == sample["id"]
        except (AssertionError, KeyError):
            pass
        else:
            raise AssertionError("unsafe mutation accepted")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--donor-dir", type=Path)
    args = p.parse_args()
    groups = validate(args.root, args.donor_dir)
    negative_cases(args.root)
    print("ERMAK_SOURCE_OBJECTS_PASS", {k:len(v) for k,v in groups.items()})
