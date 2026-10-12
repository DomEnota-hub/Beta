#!/usr/bin/env python3
"""Ermak snapshot completeness and fail-closed policy checks."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

from migrate_ermak import ASSETS, BASE, build, read_asset

OUTPUT_SHA256 = {
    "equipment-01.pack.json": "a9f433ac0c25bf0e01fd4b0c29d950f8b0d7d21ad2364d3f0fff42afc52624a4",
    "equipment-02.pack.json": "323a354ba2c6bf4941460dae03459b41f8d4a2fb3e560e7a05483e8d28456681",
    "equipment-03.pack.json": "6eab32817d3dbd52ef7778619bec41e279a8f8163572afd7a7a16ccfcae618a7",
    "equipment-04.pack.json": "1bc4f050d7a576840368c1906498a7c199b270aa5821f29a7196229abafc4003",
    "equipment-05.pack.json": "64b45ac902ec9cbc1b7263a0ac645bc377d9bb56b7bb350687a2929863f7d2e2",
    "equipment-06.pack.json": "167ce0dd342e33d965a81b4ed432f58c1b7a5811b6b929ded6275065e37a7490",
    "schemes-01.pack.json": "4f84728a222a7ce7f670ce5814d1cf8ed646de39480810f50b696b6e5765bf88",
    "schemes-02.pack.json": "4c1c2b9e6513cd19258c151a1abb8ef6d198f9dd93de0bd798540388f770b2cb",
    "diagnostics-01.pack.json": "fb5f84757fc69ed638d9301afe075be151b4fa14f81c199a3117e5225812a3d2",
    "diagnostics-02.pack.json": "ecd41c31b16a2f31522a13425339428ab751b4c15d7c2c3ef39c67a4d43fcec0",
    "diagnostics-03.pack.json": "195060385d2d0df28c6177bcc752c37fbcab89fd0d5f4faf9ebd19397979652c",
    "diagnostics-04.pack.json": "c088cd3d491036ed1e6c27c33b6a04d230882ee20cfdcdf5164dede6ac3db31e",
    "diagnostics-05.pack.json": "9ec0fe543378e2fff3b5031c19f79974716d2375a59e36589a51d1b98947c35b",
    "diagnostics-06.pack.json": "2b70f08ef3962f479d6093b44146f6bca5220508f379fdf21fb2b5f23e940c93",
    "diagnostics-07.pack.json": "2100dc65f64c53a33da97e202551abefa47191c86e8b78ffed3a720eca82e4c4",
    "knowledge-01.pack.json": "ccd618254ba25835212dc12dbd601026805d8153106816719659344206c9815c",
    "knowledge-02.pack.json": "ecb3a6c7c12b73dbc5ecaefc3eda034b8f02bc7f8bb62f7fc1a0b5a2397d207d",
    "knowledge-03.pack.json": "68c801dec97f772eac7d584e018d8422c90c689d056667377357faa6e77015d6",
    "knowledge-04.pack.json": "cab1e18d7e2856c2b22bb1816687a31094bee68dfaa84cb0acaa18c9623318c1",
    "knowledge-05.pack.json": "3083a14cf4cfd3ac375dfadfb37179d2fca57e7c84bd57dcae7e8a5e04d5ef91",
    "knowledge-06.pack.json": "b0ce7befe89f6d53a051be957be0d614391f67c29484f15b67334a76ca108143",
    "knowledge-07.pack.json": "54eb69ee57c60de9ea84fe84d13c5ef261ff6597cc334f94cb4b974b188e989c",
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
    expected_types = {"EQUIPMENT":"EQUIPMENT", "KNOWLEDGE":"KNOWLEDGE",
                      "RELATED_SCENARIO":"DIAGNOSTIC_SCENARIO"}
    canonical_types = {e["id"]:e["type"] for e in all_entries}
    links = [link for e in all_entries for link in e["links"]]
    assert len(links) == 3809
    for link in links:
        assert canonical_types[link["targetId"]] == expected_types[link["type"]]
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
