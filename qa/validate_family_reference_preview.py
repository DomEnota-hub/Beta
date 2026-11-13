#!/usr/bin/env python3
"""Verify 84 summary-only Test- → Beta references against pinned donor blob SHAs.

This is a *knowledge preview*, not source/normative approval or an action gate.
No procedures, diagnostic branches, linked actions or variant inference are allowed.
"""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
data = json.loads((root / "content-packs/crew-reference/summaries.json").read_text(encoding="utf-8"))
assert data["schemaVersion"] == 1
assert data["donorCommit"] == "3176d6ee228f0ed4b78371f45209e10c1c724eff"
items = data["entries"]
assert len(items) == 84
assert {item["modelId"] for item in items} == {
    "2es5k", "3es5k", "chme3", "chme3t", "chme3e", "tem2", "tem2u",
}
allowed_keys = {
    "id", "modelId", "executionId", "scope", "title", "summary",
    "donorPath", "donorBlobSha", "donorId", "targetPack", "targetId",
}
seen = set()
seen_objects = set()
from collections import Counter
assert Counter(item["modelId"] for item in items) == Counter({
    "2es5k": 12, "3es5k": 12, "chme3": 12, "chme3t": 12,
    "chme3e": 12, "tem2": 12, "tem2u": 12,
})
donor_shas = {
    "app/src/main/assets/technical/ermak_knowledge.json.gz": "08d164fc11c33c241d04ad6ad60c13a3aec996c8",
    "app/src/main/assets/technical/chme3_chme3_catalog.json.gz": "fa63f0ca6bf46e91780d77e6e17131cd00a4df7e",
    "app/src/main/assets/technical/chme3_chme3t_catalog.json.gz": "3682ce0b3a8607f972dec8527cb9af437484af95",
    "app/src/main/assets/technical/chme3_chme3e_catalog.json.gz": "095e3230dd40f8b1dbc93cd5181a69fcabd1975f",
    "app/src/main/assets/technical/tem2_tem2_catalog.json": "c7a94c1cd2687b84de4358b80773e3156c6b93d7",
    "app/src/main/assets/technical/tem2_tem2u_catalog.json": "766ac526fa4b86245704ed0252c2fdf3998a0e78",
}
for item in items:
    assert set(item) == allowed_keys, item["id"]
    assert item["id"] not in seen
    seen.add(item["id"])
    object_key = (item["modelId"], item["donorId"])
    assert object_key not in seen_objects, object_key
    seen_objects.add(object_key)
    assert item["title"].strip() and item["summary"].strip()
    assert len(item["summary"]) <= 240 and "\n" not in item["summary"]
    assert item["donorBlobSha"] == donor_shas[item["donorPath"]]
    path = root / item["targetPack"]
    assert path.is_file() and path.suffix == ".json"
    pack = json.loads(path.read_text(encoding="utf-8"))
    candidates = [e for e in pack["entries"] if e["id"] == item["targetId"]]
    assert len(candidates) == 1, item["id"]
    source = candidates[0]
    assert source["title"] == item["title"] and source["summary"] == item["summary"]
    assert source["publicationStatus"] == "CANDIDATE"
    assert source["layer"] == "STANDARD"
    assert source["actionDisposition"] == "INFORMATION_ONLY"
    assert source["type"] in {"EQUIPMENT", "KNOWLEDGE", "ACCEPTANCE_ITEM"}
    assert source["sourceObject"]["sourcePath"] == item["donorPath"]
    assert source["sourceObject"]["sourceBlobSha"] == item["donorBlobSha"]
    assert source["sourceObject"]["object"]["id"] == item["donorId"]
    variants = source.get("applicability", {}).get("variantIds", [])
    if item["scope"] == "DONOR_VARIANT":
        assert item["executionId"] in variants
        assert item["executionId"] is not None
    else:
        assert item["scope"] == "EXECUTION_UNVERIFIED"
        assert item["executionId"] is None
        assert item["modelId"] in {"2es5k", "3es5k", "chme3t"}
        # Generic Ermak, or CHME3T without verified pre/post-6245 split.
        assert not variants or variants == ["chme3t"]
print("STAGE13_DONOR_SUMMARY_PARITY_PASS entries=84 models=7 executable=0")

# Separately authored equipment references: no raw donor descriptions, parameters or actions.
equipment = json.loads((root / "content-packs/crew-reference/ermak-equipment.json").read_text(encoding="utf-8"))
assert equipment["schemaVersion"] == 1 and equipment["donorCommit"] == data["donorCommit"]
equipment_sources = {}
for number in range(1, 7):
    pack_path = f"content-packs/electric/ermak/atlas/equipment/equipment-{number:02d}.pack.json"
    pack = json.loads((root / pack_path).read_text(encoding="utf-8"))
    for entry in pack["entries"]:
        assert entry["id"] not in equipment_sources
        equipment_sources[entry["id"]] = (pack_path, entry)
assert len(equipment_sources) == 111
by_id = {key: (path, entry) for key, (path, entry) in equipment_sources.items()
         if entry["sourceObject"]["object"]["applicability"]["profiles"] == ["base_early"]}
assert len(by_id) == 99
assert len(equipment["entries"]) == 198
assert {(e["modelId"], e["donorId"]) for e in equipment["entries"]} == {
    (model, donor_id) for model in ("2es5k", "3es5k") for donor_id in by_id
}
for item in equipment["entries"]:
    assert set(item) == allowed_keys and item["id"] not in seen
    seen.add(item["id"])
    assert item["scope"] == "EXECUTION_UNVERIFIED" and item["executionId"] is None
    pack_path, source = by_id[item["donorId"]]
    assert item["targetPack"] == pack_path and item["targetId"] == item["donorId"]
    assert set(source["sourceObject"]["object"]["applicability"]["exclusions"]) <= {"booster_only"}
    assert source["title"] == item["title"] and source["summary"] != item["summary"]
    assert source["publicationStatus"] == "CANDIDATE" and source["actionDisposition"] == "INFORMATION_ONLY"
    assert item["donorPath"] == source["sourceObject"]["sourcePath"] == "app/src/main/assets/technical/ermak_equipment.json.gz"
    assert item["donorBlobSha"] == source["sourceObject"]["sourceBlobSha"] == "47a8d2424d69943fba9747746aa6ad8c8f4e2e98"
    assert source["sourceObject"]["object"]["id"] == item["donorId"]
    assert source["sourceObject"]["object"]["applicability"]["profiles"] == ["base_early"]
    assert set(source["sourceObject"]["object"]["applicability"]["models"]) == {"2ES5K", "3ES5K"}
    assert 0 < len(item["summary"]) <= 240 and "\n" not in item["summary"]
print("ERMAK_EQUIPMENT_REFERENCE_PASS objects=99 model_entries=198 executable=0")
