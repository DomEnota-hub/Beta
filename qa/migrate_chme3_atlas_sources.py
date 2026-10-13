#!/usr/bin/env python3
"""Preserve CHME3 Atlas indexes and cards as paired source evidence."""
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

DEST = Path("content-packs/diesel/chme3-family/migration/atlas-source-index.json")
PINS = {
    "docs/locomotives/chme3/atlas_cards_electric_brake.json": "50a11507ad7b28033f2accb345233feae1250fb8",
    "docs/locomotives/chme3/atlas_cards_engine_control_remaining.json": "6ae2a66ba5840a6f21618febb540c43a7687786b",
    "docs/locomotives/chme3/atlas_cards_powerplant.json": "93124b1969588ea17aaee508c97efc2638d29ecd",
    "docs/locomotives/chme3/atlas_cards_running_auxiliary.json": "8ee798422f08f02a08d45b637460b4da0498bfb9",
    "docs/locomotives/chme3/atlas_cards_scheme_equipment.json": "0538ffd060f626f4bbec37b2e36054ebfa1ec11a",
    "docs/locomotives/chme3/atlas_index.json": "6274dbcbbfdfdd775a44c8dfc5b9af1fc6ca134d",
    "docs/locomotives/chme3/atlas_index_extension.json": "b0a0385d7818ac07b38ae040fde6479df8fbbd4f",
    "docs/locomotives/diesel/chme3-family/chme3e/atlas_cards_electronic.json": "a14aaba2d233a9243d8111bb565ab6335cbe23bc",
    "docs/locomotives/diesel/chme3-family/chme3e/atlas_cards_preheat_remote.json": "4222dd9f116d2739b338d369276bc39f7efcaae7",
    "docs/locomotives/diesel/chme3-family/chme3e/atlas_variant.json": "2b30501c8817ecd5801341eac0e7b50699724c91",
}


def read_pinned(root, path, sha):
    raw = (root / path).read_bytes()
    digest = lambda b: hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()
    if digest(raw) != sha and raw.endswith(b"\n"):
        raw = raw[:-1]
    assert digest(raw) == sha, path
    return json.loads(raw)


def build(donor_root):
    documents = []
    identities = defaultdict(list)
    for path, sha in PINS.items():
        obj = read_pinned(donor_root, path, sha)
        documents.append({"sourcePath": path, "sourceBlobSha": sha, "sourceObject": obj})
        for field in ("records", "equipment"):
            for i, record in enumerate(obj.get(field, [])):
                assert isinstance(record.get("id"), str)
                identities[record["id"]].append({"sourcePath": path, "sourcePointer": f"/{field}/{i}",
                                                  "name": record.get("name"),
                                                  "role": "CARD" if "atlas_cards_" in path else "INDEX"})
    pairs = []
    for source_id, occurrences in sorted(identities.items()):
        if len(occurrences) == 1:
            continue
        assert len(occurrences) == 2 and {o["role"] for o in occurrences} == {"CARD", "INDEX"}, source_id
        names = [o["name"] for o in occurrences]
        name_status = ("MISSING_CARD_NAME" if None in names else
                       "MATCHING_NAMES" if names[0] == names[1] else "DIFFERENT_NAMES")
        pairs.append({"sourceId": source_id, "nameComparison": name_status,
                      "occurrences": occurrences})
    assert len(pairs) == 103
    assert sum(p["nameComparison"] == "MISSING_CARD_NAME" for p in pairs) == 33
    assert [p["sourceId"] for p in pairs if p["nameComparison"] == "DIFFERENT_NAMES"] == [
        "CHME3T-EQ-BRAKE-RESISTORS"]
    brake = next(p for p in pairs if p["sourceId"] == "CHME3T-EQ-BRAKE-RESISTORS")
    by_role = {o["role"]: o for o in brake["occurrences"]}
    assert by_role["INDEX"]["name"] == "Блок тормозных резисторов"
    assert by_role["CARD"]["name"] == "Тормозные резисторы"
    source_by_path = {d["sourcePath"]: d["sourceObject"] for d in documents}
    for occurrence in brake["occurrences"]:
        node = source_by_path[occurrence["sourcePath"]]
        for token in occurrence["sourcePointer"].lstrip("/").split("/"):
            node = node[int(token)] if isinstance(node, list) else node[token]
        assert node["applicability"] == ["ЧМЭ3Т"]
    name_resolution = {"sourceId": brake["sourceId"],
                       "canonicalId": "chme3.catalog.chme3t-eq-brake-resistors",
                       "preferredName": by_role["INDEX"]["name"],
                       "alternativeNames": [by_role["CARD"]["name"]],
                       "applicability": ["ЧМЭ3Т"],
                       "nameSources": brake["occurrences"],
                       "cardContentPolicy": "PRESERVE_COMPLETE_SOURCE_CARD"}
    return {"schemaVersion": 1, "donorCommit": "3176d6ee228f0ed4b78371f45209e10c1c724eff",
            "publicationStatus": "CANDIDATE", "actionDisposition": "INFORMATION_ONLY",
            "runtimeImport": False, "pairPolicy": "INDEX_AND_CARD_RETAINED_SEPARATELY",
            "pairedRecords": pairs, "canonicalNameResolutions": [name_resolution],
            "documents": documents}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--donor-root", type=Path, required=True)
    p.add_argument("--output-root", type=Path, default=Path("."))
    a = p.parse_args()
    target = a.output_root / DEST
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build(a.donor_root), ensure_ascii=False, separators=(",", ":")) + "\n")
    print("CHME3_ATLAS_SOURCES", len(PINS), 103)
