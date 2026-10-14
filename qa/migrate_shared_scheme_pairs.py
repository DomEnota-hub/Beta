#!/usr/bin/env python3
"""Project pinned shared training flows/layouts into non-runtime model packs."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

DONOR_COMMIT = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
SOURCES = {
    "sequences": ("stepwise_scheme_flows.json", "ccda6a1384f3f0d0183ef4403e8593b544e40981"),
    "layouts": ("scheme_layout_metadata.json", "ad34505c73ea6833ddc7a95c242874f794cd7ccd"),
}
FAMILIES = {"ERMAK": ("electric/ermak", "ermak", []),
            "CHME3": ("diesel/chme3-family", "chme3-family", ["chme3"]),
            "CHME3T": ("diesel/chme3-family", "chme3-family", ["chme3t"]),
            "CHME3E": ("diesel/chme3-family", "chme3-family", ["chme3e"])}


def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("donor", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    source_dir = args.donor / "app/src/main/assets/technical"
    source = {}
    for kind, (name, sha) in SOURCES.items():
        path = source_dir / name
        actual = subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()
        assert actual == sha, (path, actual)
        source[kind] = json.loads(path.read_text())
    overlay = json.loads((root / "docs/data-migration/shared-scheme-flow-layout-dispositions.json").read_text())
    sequences = {s["id"]: s for s in source["sequences"]["sequences"]}
    layouts = {l["sequenceId"]: l for l in source["layouts"]["layouts"]}
    assert len(sequences) == len(layouts) == len(overlay["rows"]) == 55
    assert set(sequences) == set(layouts) == {r["sequenceId"] for r in overlay["rows"]}
    out = {"ermak": [], "chme3-family": []}
    for row in overlay["rows"]:
        sid = row["sequenceId"]
        seq, layout = sequences[sid], layouts[sid]
        assert seq["family"] == layout["family"] == row["family"]
        assert seq["sourceSchemeRef"] == layout["sourceSchemeRef"] == row["sourceSchemeRef"]
        assert digest(seq) == row["sequenceSha256"] and digest(layout) == row["layoutSha256"]
        _, model, variants = FAMILIES[seq["family"]]
        identity = sid.lower()
        for kind, obj in (("sequence", seq), ("layout", layout)):
            entry_id = f"{model}.shared-schemes.{kind}.{identity}"
            entry = {
                "id": entry_id, "type": "ATLAS_SCHEME",
                "owner": {"kind": "MODEL", "modelId": model},
                "applicability": {"modelIds": [model], "variantIds": variants},
                "layer": "STANDARD", "publicationStatus": "CANDIDATE",
                "provenance": "UNKNOWN", "sourceStatus": "UNKNOWN",
                "actionDisposition": "INFORMATION_ONLY",
                "title": seq["title"] if kind == "sequence" else f"Экранная раскладка: {seq['title']}",
                "summary": seq["functionalDisclaimer"] if kind == "sequence" else "Координаты экранного отображения, не расположение оборудования.",
                "searchTerms": [], "sourceRefs": [], "links": [],
                "sourceObject": {
                    "sourcePath": f"app/src/main/assets/technical/{SOURCES[kind + 's'][0]}",
                    "sourceBlobSha": SOURCES[kind + "s"][1], "object": obj,
                },
            }
            out[model].append(entry)
    for model, entries in out.items():
        family = "ELECTRIC" if model == "ermak" else "DIESEL"
        folder = "electric/ermak" if model == "ermak" else "diesel/chme3-family"
        path = root / "content-packs" / folder / "atlas/shared-scheme-pairs.candidate.pack.json"
        pack = {
            "manifest": {"schemaVersion": 1, "packId": f"{model}.shared-scheme-pairs.candidate",
                         "packVersion": "0.1.0", "family": family, "modelIds": [model],
                         "variantIds": [] if model == "ermak" else ["chme3", "chme3t", "chme3e"],
                         "locale": "ru-RU", "entries": [e["id"] for e in entries],
                         "requiresRuntime": "1.1.0", "sourceCatalogVersion": f"test-{DONOR_COMMIT[:8]}-shared-schemes",
                         "checksums": {name + ".gitBlob": sha for name, sha in SOURCES.values()}},
            "entries": entries,
        }
        encoded = json.dumps(pack, ensure_ascii=False, separators=(",", ":")) + "\n"
        if args.check:
            assert path.read_text() == encoded, path
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(encoded)
        print(model, len(entries), path.relative_to(root))


if __name__ == "__main__":
    main()
