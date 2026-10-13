#!/usr/bin/env python3
"""Preserve pinned CHME3 diagnostic graph documents without activating them."""
import argparse
import hashlib
import json
from pathlib import Path

DEST = Path("content-packs/diesel/chme3-family/migration/graph-source-index.json")
PINS = {
    "docs/locomotives/chme3/diagnostic_runtime_graphs_v2_batch1.json": "9f7a889eabcbe4ee0a327a55ff8c03c922003a6a",
    "docs/locomotives/chme3/diagnostic_runtime_graphs_v2_batch2.json": "ca06073e8405d1b24d0ec416023c35ef01d445a1",
    "docs/locomotives/chme3/diagnostic_runtime_graphs_v2_batch3.json": "83e4a219751e7f0aec742d6b0a50a5aaf1a14d28",
    "docs/locomotives/chme3/diagnostic_runtime_graphs_v2_batch4.json": "1f17fa806bdeba265b95854a5111094c2a57c6e8",
    "docs/locomotives/chme3/diagnostic_runtime_graphs_v2_batch5.json": "840bf0d7f649dbddd04f3468a9fa388b9f1fd0bf",
    "docs/locomotives/chme3/diagnostic_runtime_graphs_v2_batch6.json": "147463af97a7e5ac32c0e592372d7ef49ef2f8b4",
    "docs/locomotives/chme3/diagnostic_runtime_graphs_v2_batch7.json": "ba5eea98dd30aa5d9953b66f5a652c095951b1f8",
    "docs/locomotives/chme3/diagnostic_runtime_graphs_v2_batch8.json": "a47a53566db5e2ffdfe596e26373e4a0dd762e8d",
    "docs/locomotives/chme3/diagnostic_runtime_graphs_v2_batch9.json": "4a256c1d1b12bdfdf7fc26a714cc3a6cfc795111",
    "docs/locomotives/diesel/chme3-family/chme3e/diagnostic_runtime_graphs_v2.json": "462a3ca769c6ee2e7e183cd78cba4fc5b4d0d59e",
}
PACKS = [f"content-packs/diesel/chme3-family/diagnostics/recommended/diagnostics-{n:02d}.pack.json" for n in range(1, 5)]


def read_pinned(root, path, sha):
    raw = (root / path).read_bytes()
    digest = lambda b: hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()
    if digest(raw) != sha and raw.endswith(b"\n"):
        raw = raw[:-1]
    assert digest(raw) == sha, path
    return json.loads(raw)


def normalized(graph):
    result = json.loads(json.dumps(graph, ensure_ascii=False))
    for node in result["nodes"]:
        if "choices" in node:
            node["choices"] = [c for c in node["choices"] if c.get("responseKind") != "UNKNOWN"]
    return result


def build(donor_root, canonical_root):
    documents = [{"sourcePath": p, "sourceBlobSha": sha,
                  "sourceObject": read_pinned(donor_root, p, sha)} for p, sha in PINS.items()]
    canonical = {}
    for pack in PACKS:
        for entry in json.loads((canonical_root / pack).read_text())["entries"]:
            source_id = entry["sourceObject"]["object"]["id"]
            assert source_id not in canonical, source_id
            canonical[source_id] = (pack, entry)
    links = []
    for di, doc in enumerate(documents):
        for si, scenario in enumerate(doc["sourceObject"]["scenarios"]):
            source_id = scenario["scenarioId"]
            pack, entry = canonical.pop(source_id)
            assert scenario["runtimeGraph"] == normalized(entry["sourceObject"]["object"]["graph"]), source_id
            links.append({"sourcePath": doc["sourcePath"], "sourcePointer": f"/scenarios/{si}",
                          "sourceId": source_id, "canonicalPack": pack, "canonicalId": entry["id"],
                          "relation": "GRAPH_EQUALS_CANONICAL_AFTER_UNKNOWN_BRANCH_REMOVAL"})
    assert not canonical and len(links) == 68
    assert sum(len(s["runtimeGraph"]["nodes"]) for d in documents for s in d["sourceObject"]["scenarios"]) == 898
    return {"schemaVersion": 1, "donorCommit": "3176d6ee228f0ed4b78371f45209e10c1c724eff",
            "publicationStatus": "CANDIDATE", "actionDisposition": "INFORMATION_ONLY", "runtimeImport": False,
            "relationPolicy": "SOURCE_GRAPH_PRESERVED_CANONICAL_GRAPH_TRANSFORM_VERIFIED",
            "links": links, "documents": documents}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--donor-root", type=Path, required=True)
    p.add_argument("--canonical-root", type=Path, default=Path("."))
    p.add_argument("--output-root", type=Path, default=Path("."))
    a = p.parse_args()
    target = a.output_root / DEST
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build(a.donor_root, a.canonical_root), ensure_ascii=False, separators=(",", ":")) + "\n")
    print("CHME3_GRAPH_SOURCES", len(PINS), 68)
