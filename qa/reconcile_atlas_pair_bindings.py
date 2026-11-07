#!/usr/bin/env python3
"""Relate preserved stepwise Atlas pairs to exact model equipment without runtime promotion."""
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "content-packs/locomotive-migration/atlas-pair-bindings.candidate.json"
PACKS = {
    "ermak": ("content-packs/electric/ermak/atlas/shared-scheme-pairs.candidate.pack.json",),
    "chme3-family": ("content-packs/diesel/chme3-family/atlas/shared-scheme-pairs.candidate.pack.json",),
    "tem2-family": ("content-packs/diesel/tem2-family/atlas/sequences/sequences-01.pack.json",
                    "content-packs/diesel/tem2-family/atlas/layouts/layouts-01.pack.json"),
}
AUDITS = {
    "chme3-family": "content-packs/diesel/chme3-family/migration/source-audit.json",
    "tem2-family": "content-packs/diesel/tem2-family/migration/source-audit.json",
}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode()).hexdigest()


def project(root=ROOT):
    records = {}
    for model in PACKS:
        folder = {"ermak": "electric/ermak", "chme3-family": "diesel/chme3-family",
                  "tem2-family": "diesel/tem2-family"}[model]
        for path in (root / "content-packs" / folder).rglob("*.pack.json"):
            for entry in json.loads(path.read_text())["entries"]:
                assert entry["id"] not in records, entry["id"]
                records[entry["id"]] = entry

    mappings = {}
    for model, path in AUDITS.items():
        by_key = defaultdict(set)
        for mapping in json.loads((root / path).read_text())["mappings"]:
            if mapping["sourceKind"] == "catalog":
                by_key[(mapping["variant"], mapping["sourceId"])].add(mapping["canonicalId"])
        mappings[model] = by_key

    rows = []
    for model, paths in PACKS.items():
        entries = [entry for path in paths
                   for entry in json.loads((root / path).read_text())["entries"]]
        sequences = {e["sourceObject"]["object"]["id"]: e for e in entries
                     if "steps" in e["sourceObject"]["object"]}
        layouts = {e["sourceObject"]["object"]["sequenceId"]: e for e in entries
                   if "nodes" in e["sourceObject"]["object"]}
        assert len(sequences) == len(layouts) == {"ermak": 26,
            "chme3-family": 29, "tem2-family": 17}[model]
        assert set(sequences) == set(layouts)
        for source_id in sorted(sequences):
            sequence, layout = sequences[source_id], layouts[source_id]
            source, geometry = sequence["sourceObject"]["object"], layout["sourceObject"]["object"]
            assert sequence["publicationStatus"] == layout["publicationStatus"] == "CANDIDATE"
            assert sequence["actionDisposition"] == layout["actionDisposition"] == "INFORMATION_ONLY"
            assert sequence["owner"] == layout["owner"] == {"kind": "MODEL", "modelId": model}
            variants = sequence["applicability"].get("variantIds", [])
            assert variants == layout["applicability"].get("variantIds", [])
            assert len(variants) == (0 if model == "ermak" else 1)
            if "sourceSchemeRef" in geometry:
                assert source["sourceSchemeRef"] == geometry["sourceSchemeRef"]
            assert source["functionalDisclaimer"].strip()
            if "representation" in source:
                assert source["representation"] == "SOURCE_BACKED_FUNCTIONAL"
            if "spatialClaim" in geometry:
                assert geometry["spatialClaim"] == "DISPLAY_COORDINATES_ONLY_NOT_PHYSICAL_EQUIPMENT_LOCATION"
            nodes = geometry["nodes"]
            by_node = {node["nodeKey"]: node for node in nodes}
            assert len(by_node) == len(nodes)
            active = set()
            equipment = set()
            for step in source["steps"]:
                active.update(step.get("activeHotspotIds", []))
                equipment.update(step.get("activeEquipmentIds", []))
                for edge in step.get("edges", []):
                    active.update(edge[key] for key in ("fromAnchor", "toAnchor") if key in edge)
                    equipment.update(edge[key] for key in ("fromEquipmentId", "toEquipmentId") if key in edge)
            assert active <= set(by_node), (model, source_id, active - set(by_node))
            placed_equipment = {n["equipmentId"] for n in nodes if n.get("equipmentId")}
            assert equipment <= placed_equipment, (model, source_id, equipment - placed_equipment)
            equipment.update(n["equipmentId"] for n in nodes if n.get("equipmentId"))
            resolved = {}
            for raw_id in sorted(equipment):
                candidates = ({raw_id} if model == "ermak" else
                              mappings[model][(variants[0], raw_id)])
                assert len(candidates) == 1, (model, variants, raw_id, candidates)
                target = next(iter(candidates))
                card = records[target]
                assert card["type"] == "EQUIPMENT" and card["owner"] == sequence["owner"]
                card_variants = card["applicability"].get("variantIds", [])
                assert not variants or variants[0] in card_variants, (model, source_id, target)
                resolved[raw_id] = target
            for node in nodes:
                position = node["position"]
                assert position["width"] > 0 and position["height"] > 0
                if "coordinateSpace" in geometry:
                    space = geometry["coordinateSpace"]
                    assert 0 <= position["x"] < position["x"] + position["width"] <= space["width"]
                    assert 0 <= position["y"] < position["y"] + position["height"] <= space["height"]
                if node.get("equipmentId"):
                    assert node["equipmentId"] in resolved
            scheme_target = None
            if model == "ermak":
                assert source["sourceSchemeRef"] in records
                scheme_target = source["sourceSchemeRef"]
                assert records[scheme_target]["type"] == "ATLAS_SCHEME"
            elif model == "tem2-family":
                candidates = mappings[model][(variants[0], source["sourceSchemeRef"])]
                assert len(candidates) == 1
                scheme_target = next(iter(candidates))
                assert records[scheme_target]["type"] == "KNOWLEDGE"
            # CHME3 source scheme references exist in documentary source indexes,
            # but no unique canonical scheme entry is established for these pairs.
            rows.append({
                "modelId": model, "variantIds": variants, "sourceSequenceId": source_id,
                "sequenceEntryId": sequence["id"], "layoutEntryId": layout["id"],
                "sourceSchemeRef": source["sourceSchemeRef"],
                "sourceSchemeContextTargetId": scheme_target,
                "sourceSchemeContextTargetType": records[scheme_target]["type"] if scheme_target else None,
                "sourceSequenceSha256": digest(source), "sourceLayoutSha256": digest(geometry),
                "equipmentTargets": resolved,
                "nodeTargets": {node["nodeKey"]: resolved.get(node.get("equipmentId")) for node in nodes},
                "stepCount": len(source["steps"]), "nodeCount": len(nodes),
            })
    assert len(rows) == 72
    return {"schemaVersion": 1, "publicationStatus": "CANDIDATE",
            "actionDisposition": "INFORMATION_ONLY", "runtimeImport": False,
            "spatialClaim": "DISPLAY_COORDINATES_ONLY_NOT_PHYSICAL_EQUIPMENT_LOCATION",
            "rows": rows}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(project(), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        assert OUTPUT.read_text() == rendered
    else:
        OUTPUT.write_text(rendered)
    print("ATLAS_PAIR_BINDINGS_PASS", 72)
