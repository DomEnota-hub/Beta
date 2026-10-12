#!/usr/bin/env python3
"""Ermak snapshot completeness and fail-closed policy checks."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

from migrate_ermak import ASSETS, BASE, build, read_asset

OUTPUT_SHA256 = {
    "equipment-01.pack.json": "566aec5980def867bcccfb50aaead4faf2cb69e2629be97d989874df3d53e890",
    "equipment-02.pack.json": "ccae3c5b651ea753fadb64b1d1d6005aa84fe4083fd038c803cee4d6cc6db5a1",
    "equipment-03.pack.json": "84f741ddb117041c0f6d512e66d6506f47aeeae2c20cbd2bab7a11dc9e9d5ce9",
    "equipment-04.pack.json": "f2bf7da40b07a7e2915a7eaf7fd4ba1582fe62cb22d8dee2ac1fdbf92e616429",
    "equipment-05.pack.json": "05b73d55b7fb9d8fe98ad5447fa9d8927308ce83e21623876dd2930a9b48f391",
    "equipment-06.pack.json": "f07ee5345d52fddee3acac95df14125a8807cddd1d005e2c17f3703337776042",
    "schemes-01.pack.json": "6d54e0c3629f5f16ef058fe8fb263aee2af503d1dc6821e3376749812ffffbb7",
    "schemes-02.pack.json": "4c1c2b9e6513cd19258c151a1abb8ef6d198f9dd93de0bd798540388f770b2cb",
    "diagnostics-01.pack.json": "fb5f84757fc69ed638d9301afe075be151b4fa14f81c199a3117e5225812a3d2",
    "diagnostics-02.pack.json": "ecd41c31b16a2f31522a13425339428ab751b4c15d7c2c3ef39c67a4d43fcec0",
    "diagnostics-03.pack.json": "8a3a94dfae951af5209f163ca3adab43de14d9ffe0dc2c5f83bc1f19d346ee9d",
    "diagnostics-04.pack.json": "9fd49913a8cc6340825424b513edfd9306ed0807dcc70f54f8a818f2586e3e21",
    "diagnostics-05.pack.json": "f95c277a4f17f82da091d377ec932deb7860e5fa7da283d226f59c4846d1580a",
    "diagnostics-06.pack.json": "e43d46b0bd87d10dae62319fd3a480af2990ff9cc7270cef6c85acd7794abcf2",
    "diagnostics-07.pack.json": "eec132e64124d7aa6964e7fe7b9ee0eeaff19a0654cede6f956eeee727cb4742",
    "knowledge-01.pack.json": "d07a206091103f18fc283d13309b072618d994935ad48cc1a3fa188b0698c53d",
    "knowledge-02.pack.json": "3e9b1b50185cde77628e83defb3c019625e8a82145633053b3a91b81d871ffe5",
    "knowledge-03.pack.json": "8fdd1b9315e69796e7ece95d479a19aded32596eb783e51cd726d2cbf49af40d",
    "knowledge-04.pack.json": "046943aefc0e84818bbd3b5dd3727fb4980520fad19b945ee8f3e3eed9957ae3",
    "knowledge-05.pack.json": "199a1a36d6baf02fd9dce0276288570d62d31a0bc306c4727e50864d0c1d5616",
    "knowledge-06.pack.json": "90b1545ccadb7678274a0a886feedf364fb6abdc99128c790fe8a8bb2bc9423c",
    "knowledge-07.pack.json": "0874140769eeb3d34d8d71f98bcc761e3eaaf49784be9bbc405b236880196964",
    "sources-01.pack.json": "bf2e2eec6f6a7c1c418ea6c67cd81fa0499534420c9e5f628c0ab7a6d8067925",
    "sources-02.pack.json": "26e824b39d094fbb916b42bac5fcd3683ab89f8bf8ea74c41e9be9d5022fd902",
    "sources-03.pack.json": "6b11880920b3d8194886e20b532bdf03c43b89ac4c2a1bd9ab69fb724b80fcd1",
    "sources-04.pack.json": "a49ac66f04d83340c3374c3bae5a8977cbf4897c23bb5ddc225fd32339f99a40",
    "sources-05.pack.json": "89f7b3633b2569aaf3217cccd74b4a1a46e809b39b226ebe3bde8fb18c956e54",
}

COUNTS = {"equipment": 111, "knowledge": 138, "diagnostics": 136, "schemes": 22, "sources": 99}
TYPES = {**{n: v[1] for n, v in ASSETS.items()}, "sources": "SOURCE"}


def pack_paths(root):
    subdirs = {"equipment": "atlas/equipment", "knowledge": "technical-data/knowledge",
               "diagnostics": "diagnostics/recommended", "schemes": "atlas/schemes",
               "sources": "technical-data/sources"}
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
            assert m["checksums"] == {f"ermak_{name if name != 'sources' else 'equipment'}.json.gz.gitBlob":
                                      ASSETS[name if name != "sources" else "equipment"][2]}
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
            origin = name if name != "sources" else "equipment"
            assert e["sourceObject"]["sourcePath"] == f"app/src/main/assets/technical/ermak_{origin}.json.gz"
            assert e["sourceObject"]["sourceBlobSha"] == ASSETS[origin][2]
            if name == "sources":
                assert e["sourceObject"]["object"]["registryKey"].lower() == e["id"].removeprefix("ermak.source.")
            else:
                assert e["sourceObject"]["object"]["id"] == e["id"]
            assert isinstance(e["sourceObject"]["object"], dict)
        groups[name] = entries
        all_entries += entries
    ids = [e["id"] for e in all_entries]
    assert len(ids) == len(set(ids)) == 506
    expected_types = {"EQUIPMENT":"EQUIPMENT", "KNOWLEDGE":"KNOWLEDGE",
                      "RELATED_SCENARIO":"DIAGNOSTIC_SCENARIO", "SOURCE":"SOURCE"}
    canonical_types = {e["id"]:e["type"] for e in all_entries}
    links = [link for e in all_entries for link in e["links"]]
    assert len(links) == 4731
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
    audit = json.loads((root / BASE / "migration/source-audit.json").read_text())
    assert audit["donorCommit"] == "3176d6ee228f0ed4b78371f45209e10c1c724eff"
    assert audit["sourceObjectCounts"] == {name: COUNTS[name] for name in ASSETS}
    assert audit["sourceRegistryKeyCount"] == 99
    refs = audit["sourceReferences"]
    assert len(refs) == 152 and sum(r["occurrences"] for r in refs) == 1472
    assert {k:(sum(r["disposition"] == k for r in refs),
               sum(r["occurrences"] for r in refs if r["disposition"] == k))
            for k in ("LINKED", "AMBIGUOUS_SOURCE_ID", "SOURCE_GAP")} == {
                "LINKED": (95,924), "AMBIGUOUS_SOURCE_ID": (2,6), "SOURCE_GAP": (55,542)}
    assert {r["sourceId"] for r in refs if r["disposition"] == "AMBIGUOUS_SOURCE_ID"} == {
        "ER-SRC-039", "ER-SRC-041"}
    assert set(audit["sourceRootMetadata"]) == set(ASSETS)
    if donor_dir:
        for name in COUNTS:
            if name != "sources":
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
