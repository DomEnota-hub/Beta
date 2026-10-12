#!/usr/bin/env python3
"""Keep pinned Ermak Stage-2/7 source indexes inspectable, without runtime authority."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path("content-packs/electric/ermak/migration/source-indexes")
ASSETS = {
    "ermak_links.json.gz": "432eb86db028b8c6c1413ad054bc110fa83ce633",
    "ermak_system_map.json.gz": "bd17468332261f7fb965de6e1ba3d7f0b28a05b2",
}


def blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def validate(root):
    data = {}
    for name, sha in ASSETS.items():
        raw = (root / ROOT / name).read_bytes()
        assert blob_sha(raw) == sha, name
        data[name] = json.loads(gzip.decompress(raw))
    links, systems = data.values()
    assert {key: len(value) for key, value in links["indexes"].items()} == {
        "byEquipment": 111, "bySystem": 15, "byDiagnostic": 135, "byScheme": 22}
    assert len(systems["systems"]) == 15 and len(systems["criticalLinks"]) == 16
    assert len(systems["openQuestions"]) == 7
    assert set(links["indexes"]["bySystem"]) == {s["id"] for s in systems["systems"]}
    assert links["statistics"]["diagnostics"] == 135
    assert len(links["indexes"]["byDiagnostic"]) == 135
    # Stage-7 is a separate historical index; it must not silently redefine the
    # 136 canonical scenario objects imported from the pinned diagnostics asset.
    scenarios = set()
    for path in (root / "content-packs/electric/ermak/diagnostics").rglob("*.pack.json"):
        scenarios.update(e["id"] for e in json.loads(path.read_text())["entries"])
    assert len(scenarios) == 136
    assert set(links["indexes"]["byDiagnostic"]) <= scenarios
    assert scenarios - set(links["indexes"]["byDiagnostic"]) == {"ER-DIAG-136"}
    note = json.loads((root / ROOT / "source-index-note.json").read_text())
    assert note["classification"] == "CANDIDATE_SOURCE_INDEX_ONLY"
    assert note["runtimeImport"] is False
    assert {x["gitBlob"] for x in note["sourceAssets"]} == set(ASSETS.values())
    return len(scenarios), len(links["indexes"]["byDiagnostic"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    print("ERMAK_SUPPLEMENT_PASS", *validate(args.root))
