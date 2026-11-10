#!/usr/bin/env python3
"""Verify 7 summary-only Test- → Beta references against pinned donor blob SHAs.

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
assert len(items) == 7
assert {item["modelId"] for item in items} == {
    "2es5k", "3es5k", "chme3", "chme3t", "chme3e", "tem2", "tem2u",
}
allowed_keys = {
    "id", "modelId", "executionId", "scope", "title", "summary",
    "donorPath", "donorBlobSha", "donorId", "targetPack", "targetId",
}
seen = set()
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
    assert item["title"].strip() and item["summary"].strip()
    assert item["donorBlobSha"] == donor_shas[item["donorPath"]]
    path = root / item["targetPack"]
    assert path.is_file() and path.suffix == ".json"
    pack = json.loads(path.read_text(encoding="utf-8"))
    candidates = [e for e in pack["entries"] if e["id"] == item["targetId"]]
    assert len(candidates) == 1, item["id"]
    source = candidates[0]
    assert source["title"] == item["title"] and source["summary"] == item["summary"]
    assert source["publicationStatus"] == "CANDIDATE"
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
print("STAGE13_DONOR_SUMMARY_PARITY_PASS entries=7 models=7 executable=0")
